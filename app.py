import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import config
from exts import db, migrate, socketio
from models import PatientModel, DoctorModel
from blueprints.patient import bp as patient_auth_bp
from blueprints.doctor import bp as doctor_auth_bp
from blueprints.patient_manage import bp as patient_info_bp
from blueprints.doctor_manage import bp as doctor_info_bp
from blueprints.chat import bp as chat_bp
from blueprints.registration import bp as registration_bp
# from utils import jwt_interceptor
from dotenv import load_dotenv
import consultant

load_dotenv()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, async_mode='eventlet')

    # jwt验证
    jwt = JWTManager(app)
    # app.before_request(jwt_interceptor)

    # 允许跨域
    CORS(app, supports_credentials=True, origins=["http://localhost:7070"],
         allow_headers=["Content-Type", "Authorization"])

    # 注册蓝本
    # 登录注册蓝图
    app.register_blueprint(patient_auth_bp)
    app.register_blueprint(doctor_auth_bp)
    # 个人信息管理蓝图
    app.register_blueprint(patient_info_bp)
    app.register_blueprint(doctor_info_bp)
    app.register_blueprint(registration_bp)
    # 问诊接口蓝图
    app.register_blueprint(chat_bp)

    return app

app = create_app('development')

if __name__ == '__main__':
    socketio.run(app, debug=False)
