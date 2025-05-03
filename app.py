import os

from flask import Flask
from flask_jwt_extended import JWTManager

from config import config
from exts import db, migrate
from models import UserModel, DoctorModel
from blueprints.user import bp as user_bp
from blueprints.doctor import bp as doctor_bp
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
    app.register_blueprint(user_bp)
    app.register_blueprint(doctor_bp)

    return app

