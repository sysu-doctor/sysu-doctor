from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required,get_jwt_identity
from sqlalchemy.exc import IntegrityError
import re
from datetime import datetime,date
from utils import Result
from exts import db
from models import DoctorInfoModel,DoctorModel,DepartmentModel,HospitalModel

bp = Blueprint("doctor_info", __name__, url_prefix='/doctor')



def validate_phone_number(phone):
    """简化版手机号验证（仅限国内）"""
    pattern = r'^1[3-9]\d{9}$'  # 严格的11位国内手机号
    return re.match(pattern, phone) is not None


@bp.route('/doctor_manage', methods=['PATCH'])
@jwt_required()
def patient_management():
    """部分更新医生信息（自动同步手机号和姓名）"""

    data = request.get_json()

    # 手机号格式验证
    if 'phone' in data and not validate_phone_number(data['phone']):
        return jsonify(Result.error("请输入有效的11位国内手机号").to_dict()), 400

    # 出生日期验证
    if 'birth_date' in data:
        try:
            birth_date = datetime.strptime(data['birth_date'], "%Y-%m-%d").date()
            if birth_date > date.today():
                return jsonify(Result.error("出生日期不能晚于当前日期").to_dict()), 400
            data['birth_date'] = birth_date  # 替换为date对象
        except ValueError:
            return jsonify(Result.error("日期格式应为YYYY-MM-DD").to_dict()), 400

    # 获取当前医生
    doctor_id = str(get_jwt_identity())

    # 更新主表 DoctorInfoModel
    doctor_info = DoctorInfoModel.query.filter_by(id=doctor_id).first()
    if not doctor_info:
        return jsonify(Result.error("医生信息不存在").to_dict()), 404


    # 同步手机号和姓名到 DoctorModel（登录表）
    doctor = DoctorModel.query.get(doctor_id)
    if not doctor:
        return jsonify(Result.error("医生账户不存在").to_dict()), 404
    doctor.phone = data['phone']
    doctor.name = data['name']
    try:
        # 特殊处理关联字段
        if 'hospital_id' in data:
            hospital = HospitalModel.query.get(data['hospital_id'])
            if not hospital:
                return jsonify(Result.error("医院不存在").to_dict()), 400
            doctor_info.hospital = hospital  # 赋模型对象而非ID

        if 'department_id' in data:
            department = DepartmentModel.query.get(data['department_id'])
            if not department:
                return jsonify(Result.error("科室不存在").to_dict()), 400
            doctor_info.department = department  # 赋模型对象而非ID

        # 更新医生信息
        for field, value in data.items():
            if hasattr(doctor_info, field):
                setattr(doctor_info, field, value)

        db.session.commit()
        return jsonify(Result.success().to_dict())

    except IntegrityError as e:
        db.session.rollback()
        return jsonify(Result.error("数据库操作失败，请检查数据完整性").to_dict()), 400

    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error(f"服务器错误: {str(e)}").to_dict()), 500