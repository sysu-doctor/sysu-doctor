from flask import Blueprint, jsonify
from flask import request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from utils import Result, validate_phone_number
from exts import db
from models import DoctorModel,DoctorInfoModel
from vo import LoginVO

bp = Blueprint("doctor", __name__, url_prefix='/doctor')


@bp.route('/login', methods=['POST'])
def login():
    # 读取请求数据
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    # 查询数据库
    doctor = DoctorModel.query.filter_by(phone=phone).one_or_none()

    # 数据处理
    if not doctor:
        return jsonify(Result.error("该手机号未注册！").to_dict()),400
    if password != doctor.password:
        return jsonify(Result.error("密码错误！").to_dict()),400

    doctor = DoctorInfoModel.query.filter_by(phone=phone).one_or_none()

    # 登录成功，生成JWT令牌
    token = create_access_token(identity=str(doctor.id), additional_claims={"role":"doctor"})

    #返回结果
    login_vo = LoginVO(id=doctor.id, name=doctor.name, token=token, avatar_url=doctor.avatar_url, role="doctor")
    result = Result.success(login_vo.to_dict())
    return jsonify(result.to_dict())

@bp.route('/register', methods=['POST'])
def register():
    # 读取请求数据
    data = request.get_json()

    if not data.get('phone') or not data.get('password') or not data.get('name'):
        return jsonify(Result.error("请填入完整的信息！").to_dict()),400

    phone = data.get('phone')
    password = data.get('password')
    name = data.get('name')

    # 校验手机号
    if not validate_phone_number(phone):
        return jsonify(Result.error("请输入正确的手机号!").to_dict()), 400
    # 数据库操作
    try:
        doctor = DoctorModel(phone=phone, password=password, name=name)
        db.session.add(doctor)
        db.session.flush()  # 获取自动生成的id

        # 创建医生基本信息
        doctor_info = DoctorInfoModel(
            id=doctor.id,
            phone=phone,
            name=name,
            gender=None,
            hospital_id=None,
            department_id=None,
            internal_id=None,
            position_rank=None,
            specialty='',
            birth_date=None,
            avatar_url='https://pic.616pic.com/ys_bnew_img/00/30/13/VgZR6eQ01M.jpg',
            schedule=None
        )
        db.session.add(doctor_info)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        return jsonify(Result.error("该手机号已被注册！").to_dict()),400
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("未知错误").to_dict()),500

    # 返回结果
    result = Result.success()
    return jsonify(result.to_dict())

@bp.route('/logout', methods=['POST'])
def logout():
    result = Result.success()
    return jsonify(result.to_dict())