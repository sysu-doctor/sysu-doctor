import os

from flask import Flask
from flask_jwt_extended import JWTManager

from config import config
from exts import db, migrate
from models import PatientModel, DoctorModel
from blueprints.patient import bp as patient_auth_bp
from blueprints.doctor import bp as doctor_auth_bp
from blueprints.patient_manage import bp as patient_info_bp
from blueprints.doctor_manage import bp as doctor_info_bp
from utils import jwt_interceptor


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    # jwt验证
    jwt = JWTManager(app)
    app.before_request(jwt_interceptor)

    # 注册蓝本
    # 登录注册蓝图
    app.register_blueprint(patient_auth_bp)
    app.register_blueprint(doctor_auth_bp)
    # 个人信息管理蓝图
    app.register_blueprint(patient_info_bp)
    app.register_blueprint(doctor_info_bp)

    return app

