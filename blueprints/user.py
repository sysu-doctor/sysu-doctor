from flask import Blueprint, jsonify
from flask import request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from utils import Result
from exts import db
from models import UserModel
from vo import LoginVO

bp = Blueprint("user", __name__, url_prefix='/user')


@bp.route('/login', methods=['POST'])
def login():
    # 读取请求数据
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')

    # 查询数据库
    user = UserModel.query.filter_by(phone=phone).one_or_none()

    # 数据处理
    if not user:
        return jsonify(Result.error("该手机号未注册！").to_dict())
    if password != user.password:
        return jsonify(Result.error("密码错误！").to_dict())

    # 登录成功，生成JWT令牌
    token = create_access_token(identity=user.id, additional_claims={"role":"user"})

    #返回结果
    login_vo = LoginVO(id=user.id, name=user.name, token=token, role="user")
    result = Result.success(login_vo.to_dict())
    return jsonify(result.to_dict())

@bp.route('/register', methods=['POST'])
def register():
    # 读取请求数据
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    name = data.get('name')

    # 数据库操作
    try:
        user = UserModel(phone=phone, password=password, name=name)
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify(Result.error("该手机号已被注册！").to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify(Result.error("未知错误").to_dict())

    # 返回结果
    result = Result.success()
    return jsonify(result.to_dict())

@bp.route('/logout', methods=['POST'])
def logout():
    result = Result.success()
    return jsonify(result.to_dict())