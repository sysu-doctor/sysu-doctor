import oss2
from flask import blueprints, request, jsonify
import uuid
from utils import Result, upload_file

bp = blueprints.Blueprint("upload_file", __name__, url_prefix='/upload')

@bp.route('/picture', methods=['POST'])
def upload_picture():
    """上传头像"""
    file = request.files.get('file')
    if not file:
        return jsonify(Result.error("未提供文件").to_dict()), 400

    original_file_name = file.filename
    if not original_file_name:
        return jsonify(Result.error("文件名不能为空").to_dict()), 400
    if not original_file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify(Result.error("仅支持PNG、JPG、JPEG和GIF格式的图片").to_dict()), 400
    suffix = original_file_name.split('.')[-1]
    file_name = f"{uuid.uuid4().hex}.{suffix}"

    try:
        file_url = upload_file(file, file_name)
        return jsonify(Result.success({"file_url": file_url}).to_dict()), 200
    except oss2.exceptions.OssError as e:
        return jsonify(Result.error(f"文件上传失败: {str(e)}").to_dict()), 500
    except Exception as e:
        return jsonify(Result.error(f"服务器错误: {str(e)}").to_dict()), 500