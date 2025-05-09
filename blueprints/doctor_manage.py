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
        return jsonify(Result.fail("请输入有效的11位国内手机号").to_dict()), 400

    # 出生日期验证
    if 'birth_date' in data:
        try:
            birth_date = datetime.strptime(data['birth_date'], "%Y-%m-%d").date()
            if birth_date > date.today():
                return jsonify(Result.fail("出生日期不能晚于当前日期").to_dict()), 400
            data['birth_date'] = birth_date  # 替换为date对象
        except ValueError:
            return jsonify(Result.fail("日期格式应为YYYY-MM-DD").to_dict()), 400

    # 获取当前医生
    doctor_id = get_jwt_identity()

    # 更新主表 DoctorInfoModel
    doctor_info = DoctorInfoModel.query.filter_by(doctor_id=doctor_id).first()
    if not doctor_info:
        return jsonify(Result.fail("医生信息不存在").to_dict()), 404

    # 更新医生信息
    for field, value in data.items():
        setattr(doctor_info, field, value)

    # 同步手机号和姓名到 DoctorModel（登录表）
    doctor = DoctorModel.query.get(doctor_id)
    doctor.phone = data['phone']
    doctor.name = data['name']

    # 检查医院或科室是否变更
    old_hospital_id = doctor_info.hospital_id
    old_department_id = doctor_info.department_id
    try:
        # 处理医院变更
        if 'hospital_id' in data and data['hospital_id'] != old_hospital_id:
            # 从旧医院移除
            old_hospital = HospitalModel.query.get(old_hospital_id)
            if old_hospital and doctor_info in old_hospital.doctors:
                old_hospital.doctors.remove(doctor_info)

            # 添加到新医院
            new_hospital = HospitalModel.query.get(data['hospital_id'])
            if new_hospital:
                new_hospital.doctors.append(doctor_info)

        # 处理科室变更
        if 'department_id' in data and data['department_id'] != old_department_id:
            # 从旧科室移除
            if old_department_id:
                old_department = DepartmentModel.query.get(old_department_id)
                if old_department and doctor_info in old_department.doctors:
                    old_department.doctors.remove(doctor_info)

            # 添加到新科室
            if data['department_id']:
                new_department = DepartmentModel.query.get(data['department_id'])
                if new_department:
                    new_department.doctors.append(doctor_info)

        db.session.commit()
        return jsonify(Result.success().to_dict())

    except IntegrityError as e:
        db.session.rollback()
        if 'uix_hospital_employee' in str(e):
            return jsonify(Result.fail("该医院工号已存在").to_dict()), 400
        return jsonify(Result.fail("数据更新失败").to_dict()), 400