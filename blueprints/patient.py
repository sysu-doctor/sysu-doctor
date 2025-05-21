from flask import Blueprint, jsonify
from flask import request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from utils import Result, validate_phone_number
from exts import db
from models import PatientModel,PatientInfoModel
from vo import LoginVO

# 改成patient可能更好
bp = Blueprint("patient", __name__, url_prefix='/patient')


@bp.route('/login', methods=['POST'])
def login():
    # 读取请求数据
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    # 查询数据库
    patient = PatientModel.query.filter_by(phone=phone).one_or_none()

    # 数据处理
    if not patient:
        return jsonify(Result.error("该手机号未注册！").to_dict())
    if password != patient.password:
        return jsonify(Result.error("密码错误！").to_dict())

    # 登录成功，生成JWT令牌
    token = create_access_token(identity=str(patient.id), additional_claims={"role":"patient", "name":patient.name}, )

    #返回结果
    login_vo = LoginVO(id=patient.id, name=patient.name, token=token, role="patient")
    result = Result.success(login_vo.to_dict())
    return jsonify(result.to_dict())

@bp.route('/register', methods=['POST'])
def register():
    # 读取请求数据
    data = request.get_json()
    phone = data.get('phone')
    # 校验手机号
    if not validate_phone_number(phone):
        return jsonify(Result.error("请求中缺少 phone 或 name 字段").to_dict()), 400
    password = data.get('password')
    name = data.get('name')

    # 数据库操作
    try:
        patient = PatientModel(phone=phone, password=password, name=name)
        db.session.add(patient)
        db.session.flush()

        patient_info = PatientInfoModel(
            id=patient.id,  # 显式关联主键
            phone=phone,  # 同步手机号
            name=name,  # 同步姓名
            gender=None,
            address=None,
            avatar_url=None,
            birth_date=None,
            medical_history=''
        )
        db.session.add(patient_info)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "phone" in str(e):
            return jsonify(Result.error("该手机号已被注册").to_dict()), 400
        return jsonify(Result.error("数据完整性错误").to_dict()), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("注册失败，请稍后再试").to_dict()), 500

    # 返回结果
    result = Result.success()
    return jsonify(result.to_dict())

@bp.route('/logout', methods=['POST'])
def logout():
    result = Result.success()
    return jsonify(result.to_dict())