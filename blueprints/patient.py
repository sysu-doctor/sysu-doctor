from flask import Blueprint, jsonify
from flask import request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from utils import Result, validate_phone_number
from exts import db
from models import PatientModel, PatientInfoModel, DoctorInfoModel
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
        return jsonify(Result.error("该手机号未注册！").to_dict()),400
    if password != patient.password:
        return jsonify(Result.error("密码错误！").to_dict()),400

    patient = PatientInfoModel.query.filter_by(phone=phone).one_or_none()

    # 登录成功，生成JWT令牌
    token = create_access_token(identity=str(patient.id), additional_claims={"role":"patient"})

    #返回结果
    login_vo = LoginVO(id=patient.id, name=patient.name, token=token, role="patient", avatar_url=patient.avatar_url)
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
        patient = PatientModel(phone=phone, password=password, name=name)
        db.session.add(patient)
        db.session.flush()

        patient_info = PatientInfoModel(
            id=patient.id,  # 显式关联主键
            phone=phone,  # 同步手机号
            name=name,  # 同步姓名
            gender=None,
            address=None,            avatar_url='https://tse3-mm.cn.bing.net/th/id/OIP-C.uCSRqHDxGs8iC0VK7d_2dgAAAA?r=0&rs=1&pid=ImgDetMain',
            birth_date=None,
            medical_history=''
        )
        db.session.add(patient_info)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        return jsonify(Result.error("该手机号已被注册！").to_dict()), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("未知错误").to_dict()), 500

    # 返回结果
    result = Result.success()
    return jsonify(result.to_dict())

@bp.route('/logout', methods=['POST'])
def logout():
    result = Result.success()
    return jsonify(result.to_dict())

@bp.route('/doctorlist', methods=['GET'])
def doctor_list():
    # 查询所有医生
    doctors = DoctorInfoModel.query.all()

    # 转换为字典列表
    doctor_list = [
        {
            **doctor.to_dict(),
            "hospital": doctor.hospital.name if doctor.hospital else None,
            "department": doctor.department.name if doctor.department else None
        }
        for doctor in doctors
    ]

    # 返回结果
    result = Result.success(doctor_list)
    return jsonify(result.to_dict())