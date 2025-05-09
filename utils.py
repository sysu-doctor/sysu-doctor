from flask import request, g, make_response
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

WHITE_LIST = [
    "/patient/login",
    "/patient/register",
    "/doctor/login",
    "/doctor/register",
    "/patient/patient_manage",
    "/doctor/doctor_manage"
    ]


# jwt拦截器
def jwt_interceptor():
    # 检查当前请求路径是否在白名单中
    path = request.path
    if any(path.startswith(p) for p in WHITE_LIST):
        return None

    try:
        # 手动校验JWT令牌
        verify_jwt_in_request()
        # 将用户身份信息存入g对象供后续使用
        g.user = get_jwt_identity()
        g.role = get_jwt()['role']

    except Exception as e:
        # 返回具体的错误信息
        return make_response('', 401)


# 返回格式
class Result:
    def __init__(self, code, msg, data):
        self.code = code
        self.msg = msg
        self.data = data

    @staticmethod
    def success(data=None):
        return Result(1, "", data)

    @staticmethod
    def error(msg):
        return Result(0, msg, None)

    def to_dict(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }