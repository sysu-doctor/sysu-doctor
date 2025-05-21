from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_, and_, func

from exts import db
from models import MessageModel, RoomModel, DoctorModel, PatientModel
from utils import Result

bp = Blueprint("chat", __name__, url_prefix='/chat')


@bp.route("/<doctor_id>", methods=["POST"])
@jwt_required()
def new_chat(doctor_id):
    try:
        doctor = DoctorModel.query.get(doctor_id)
        patient = PatientModel.query.get(int(get_jwt_identity()))
        room = RoomModel(doctor_id=doctor.id, doctor_name=doctor.name, patient_id=patient.id, patient_name=patient.name)
        db.session.add(room)
        db.session.commit()
        return jsonify(Result.success().to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("服务器异常！").to_dict())


@bp.route("/message", methods=["GET"])
@jwt_required()
def get_message():
    # 获取请求参数
    from_user = request.args.get("from_user")
    to_user = request.args.get("to_user")

    # 查询来自两者的消息
    messages = (MessageModel
                .query
                .filter(or_(and_(MessageModel.from_user == from_user,
                                       MessageModel.to_user == to_user),
                                  and_(MessageModel.from_user == to_user,
                                       MessageModel.to_user == from_user)))
                .order_by(MessageModel.time)
                .all())

    # 转为字典列表
    messages_list = []
    # 同时设为已读
    claims = get_jwt()
    id = get_jwt_identity()
    name = claims.get("name")
    role = claims.get("role")
    for message in messages:
        if message.to_user == name + id + role:
            message.read = 1
        messages_list.append(message.to_dict())

    db.session.commit()

    return jsonify(Result.success(messages_list).to_dict())


@bp.route("/user_list", methods=["GET"])
@jwt_required()
def get_user_list():
    claims = get_jwt()
    role = claims["role"]
    id = int(get_jwt_identity())
    if role == "doctor":
        patients = RoomModel.query.filter(RoomModel.doctor_id == id).all()
        patients_list = []
        for patient in patients:
            patients_list.append({"patient_id": patient.patient_id, "patient_name": patient.patient_name})
        return jsonify(Result.success(patients_list).to_dict())
    else:
        doctors = RoomModel.query.filter(RoomModel.patient_id == id).all()
        doctors_list = []
        for doctor in doctors:
            doctors_list.append({"doctor_id": doctor.doctor_id, "doctor_name": doctor.doctor_name})
        return jsonify(Result.success(doctors_list).to_dict())


@bp.route("/unread", methods=["GET"])
@jwt_required()
def get_unread():
    to_user = request.args.get("to_user")

    #查询发给当前用户的消息中未读的数目，并根据发送人分组
    messages = (
        db.session.query(MessageModel.from_user, func.count(MessageModel.id).label('count'))
        .filter(and_(MessageModel.to_user == to_user, MessageModel.read == 0))
        .group_by(MessageModel.from_user)
        .all()
    )

    message_dicts = [{'from_user': from_user, 'count': count} for from_user, count in messages]
    return jsonify(Result.success(message_dicts).to_dict())