from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import re
from datetime import datetime, date
from utils import Result, validate_phone_number
from exts import db
from models import PatientInfoModel, PatientModel
from vo import PatientInfoVO

bp = Blueprint("patient_info", __name__, url_prefix='/patient')


@bp.route('/patient_manage', methods=['PUT'])
@jwt_required()
def patient_management():
    try:
        data = request.get_json()
        if not data:
            return jsonify(Result.error("请求体不能为空").to_dict()), 400

        # 验证必填字段
        if 'phone' not in data or 'name' not in data:
            return jsonify(Result.error("请求中缺少 phone 或 name 字段").to_dict()), 400

        # 手机号验证
        if not validate_phone_number(data['phone']):
            return jsonify(Result.error("请输入有效的11位国内手机号").to_dict()), 400

        # 出生日期验证（可选字段）
        if 'birth_date' in data:
            try:
                birth_date = datetime.strptime(data['birth_date'], "%Y-%m-%d").date()
                if birth_date > date.today():
                    return jsonify(Result.error("出生日期不能晚于当前日期").to_dict()), 400
                data['birth_date'] = birth_date
            except ValueError:
                return jsonify(Result.error("日期格式应为YYYY-MM-DD").to_dict()), 400

        # 获取患者ID并验证
        patient_id = str(get_jwt_identity())
        patient_info = PatientInfoModel.query.filter_by(id=patient_id).first()
        if not patient_info:
            return jsonify(Result.error("患者信息不存在").to_dict()), 404

        # 更新 PatientInfoModel
        for field, value in data.items():
            if hasattr(patient_info, field):
                setattr(patient_info, field, value)

        # 同步到 PatientModel
        patient = PatientModel.query.get(patient_id)
        if not patient:
            return jsonify(Result.error("用户不存在").to_dict()), 404
        patient.phone = data['phone']
        patient.name = data['name']

        db.session.commit()
        return jsonify(Result.success().to_dict())

    except IntegrityError as e:
        db.session.rollback()
        return jsonify(Result.error("数据库操作失败，请检查数据完整性").to_dict()), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error(f"服务器错误: {str(e)}").to_dict()), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_patient_info():
    patient_id = str(get_jwt_identity())
    patient_info = PatientInfoModel.query.filter_by(id=patient_id).first()
    if not patient_info:
        return jsonify(Result.error("用户不存在").to_dict()), 404
    patient_info_vo = PatientInfoVO(patient_info.phone,
                                    patient_info.name,
                                    patient_info.gender,
                                    patient_info.address,
                                    patient_info.birth_date.strftime("%Y-%m-%d") if patient_info.birth_date else None,
                                    patient_info.avatar_url,
                                    patient_info.medical_history)
    return jsonify(Result.success(patient_info_vo.to_dict()).to_dict())