from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import or_, and_, func

from exts import db
from models import MessageModel, RoomModel, DoctorModel, PatientModel, DoctorInfoModel, PatientInfoModel
from utils import Result

bp = Blueprint("chat", __name__, url_prefix='/chat')


@bp.route("/<doctor_id>", methods=["POST"])
@jwt_required()
def new_chat(doctor_id):
    try:
        room = RoomModel(doctor_id=doctor_id, patient_id=int(get_jwt_identity()))
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
    role = claims.get("role")
    id = get_jwt_identity()
    for message in messages:
        if message.to_user == role + "_" + id:
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
        to_user = "doctor_" + str(id)
        # 查询发给当前用户的消息中未读的数目，并根据发送人分组
        messages = (
            db.session.query(MessageModel.from_user, func.count(MessageModel.id).label('count'))
            .filter(and_(MessageModel.to_user == to_user, MessageModel.read == 0))
            .group_by(MessageModel.from_user)
            .all()
        )
        message_dicts = [{'from_user': from_user, 'count': count} for from_user, count in messages]

        id_list = db.session.query(RoomModel.patient_id).filter(RoomModel.doctor_id == id).all()
        id_list = [item[0] for item in id_list]
        list = PatientInfoModel.query.filter(PatientInfoModel.id.in_(id_list)).all()
        patients_list = []
        for p in list:
            from_user = "patient_" + str(p.id)

            patients_list.append({"id": p.id,
                                  "name": p.name,
                                  "gender": p.gender,
                                  "birth_date": p.birth_date.strftime("%Y-%m-%d") if p.birth_date else None,
                                  "address": p.address,
                                  "avatar_url": p.avatar_url,
                                  "unreadCount": next((item['count'] for item in message_dicts if item['from_user'] == from_user), 0)})
        return jsonify(Result.success(patients_list).to_dict())
    else:
        to_user = "patient_" + str(id)
        # 查询发给当前用户的消息中未读的数目，并根据发送人分组
        messages = (
            db.session.query(MessageModel.from_user, func.count(MessageModel.id).label('count'))
            .filter(and_(MessageModel.to_user == to_user, MessageModel.read == 0))
            .group_by(MessageModel.from_user)
            .all()
        )
        message_dicts = [{'from_user': from_user, 'count': count} for from_user, count in messages]
        id_list = db.session.query(RoomModel.doctor_id).filter(RoomModel.patient_id == id).all()
        print(id_list)
        id_list = [item[0] for item in id_list]
        list = DoctorInfoModel.query.filter(DoctorInfoModel.id.in_(id_list)).all()
        print(list)
        doctors_list = []
        for d in list:
            from_user = "doctor_" + str(d.id)
            doctors_list.append({"id": d.id,
                                 "name": d.name,
                                 "avatar_url": d.avatar_url,
                                 "department": d.department.name if d.department else None,
                                 "position_rank": d.position_rank,
                                 "specialty": d.specialty,
                                 "hospital": d.hospital.name if d.hospital else None,
                                 "unreadCount": next((item['count'] for item in message_dicts if item['from_user'] == from_user), 0)})
        print(doctors_list)
        return jsonify(Result.success(doctors_list).to_dict())


# @bp.route("/unread", methods=["GET"])
# @jwt_required()
# def get_unread():
#     to_user = request.args.get("to_user")
#
#     #查询发给当前用户的消息中未读的数目，并根据发送人分组
#     messages = (
#         db.session.query(MessageModel.from_user, func.count(MessageModel.id).label('count'))
#         .filter(and_(MessageModel.to_user == to_user, MessageModel.read == 0))
#         .group_by(MessageModel.from_user)
#         .all()
#     )
#
#     message_dicts = [{'from_user': from_user, 'count': count} for from_user, count in messages]
#     return jsonify(Result.success(message_dicts).to_dict())

@bp.route("/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(doctor_id):
    try:
        patient_id = int(get_jwt_identity())
        room = RoomModel.query.filter_by(doctor_id=doctor_id, patient_id=patient_id).first()
        if not room:
            return jsonify(Result.error("没有找到对应的聊天记录").to_dict()), 404
        db.session.delete(room)
        from_user = "doctor_" + str(doctor_id)
        to_user = "patient_" + str(patient_id)
        # 删除对应的消息记录
        MessageModel.query.filter(
            or_(and_(MessageModel.from_user == from_user, MessageModel.to_user == to_user),
                and_(MessageModel.from_user == to_user, MessageModel.to_user == from_user))
        ).delete(synchronize_session=False)
        db.session.commit()
        return jsonify(Result.success().to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("服务器异常！").to_dict())