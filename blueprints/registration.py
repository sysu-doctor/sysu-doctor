from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from exts import db
from models import RegistrationModel
from utils import Result

bp = Blueprint("registration", __name__, url_prefix='/patient')

@bp.route("/registration", methods=["POST"])
@jwt_required()
def add_registration():
    data = request.get_json()
    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    date = data.get("date")
    time_slot = data.get("timeSlot")
    if not patient_id or not doctor_id or not date or not time_slot:
        return jsonify(Result.error("请填入完整的信息！").to_dict()), 400
    if RegistrationModel.query.filter_by(patient_id=patient_id, doctor_id=doctor_id, date=date,
                                      time_slot=time_slot).first():
        return jsonify(Result.error("您已预约过该时段！").to_dict()), 400
    try:
        registration = RegistrationModel(
            patient_id=patient_id,
            doctor_id=doctor_id,
            date=date,
            time_slot=time_slot
        )
        db.session.add(registration)
        db.session.commit()
        return jsonify(Result.success().to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("服务器异常").to_dict()), 500

@bp.route("/registration", methods=["GET"])
@jwt_required()
def get_registration():
    claims = get_jwt()
    role = claims["role"]
    id = int(get_jwt_identity())

    if role == "patient":
        registrations = RegistrationModel.query.filter_by(patient_id=id).all()
        registration_list = [reg.to_dict() for reg in registrations]
    else:
        registrations = RegistrationModel.query.filter_by(doctor_id=id).all()
        registration_list = [reg.to_dict() for reg in registrations]

    return jsonify(Result.success(registration_list).to_dict()), 200

@bp.route("/registration/<int:registration_id>", methods=["DELETE"])
@jwt_required()
def delete_registration(registration_id):
    registration = RegistrationModel.query.get(registration_id)
    if not registration:
        return jsonify(Result.error("预约记录不存在").to_dict()), 404

    try:
        db.session.delete(registration)
        db.session.commit()
        return jsonify(Result.success().to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("服务器异常").to_dict()), 500