from dotenv import load_dotenv
import re
import oss2
import os

from flask import jsonify

load_dotenv()

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

def validate_phone_number(phone):
    """简化版手机号验证（仅限国内）"""
    pattern = r'^1[3-9]\d{9}$'  # 严格的11位国内手机号
    return re.match(pattern, phone) is not None

# 文件上传功能
def upload_file(file_object, file_name):
    access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
    access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
    endpoint = os.getenv('OSS_ENDPOINT')
    bucket_name = os.getenv('OSS_BUCKET_NAME')

    # 初始化 Bucket
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    try:
        bucket.put_object(file_name, file_object.stream)
    except oss2.exceptions.OssError as e:
        raise e
    except Exception as e:
        raise e

    file_url = f"https://{bucket_name}.{endpoint}/{file_name}"
    return file_url
