import os
from . import file
from loggings import logger
from flask import request
from app.models.models import File
from app import create_app
from werkzeug.utils import secure_filename
from app.tools.return_tools import response_tem, return_json, localtime, get_file_name
from app.tools.unzip_tools import un_zip
from flask_jwt_extended import (
    jwt_required)

app, db = create_app("baseConfig")


def allowed_file(filename):
    """
    判断filename是否有后缀以及后缀是否在app.config['ALLOWED_EXTENSIONS']中
    :param filename:
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@file.route('/upload', methods=['POST'])
@jwt_required
def upload_files():
    type = request.args.get("type", None)  # 上传的文件类型
    if type is None:
        code = -1
        msg = "type is required"
        return response_tem(code=code, msg=msg)
    upload_file = request.files['file']
    try:
        if upload_file and allowed_file(upload_file.filename):
            filename = secure_filename(upload_file.filename)  # 带后缀的文件名
            name = filename[: -4]  # 不带后缀的文件名
            file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            upload_file.save(file_path)  # app.root_path获取当前项目绝对路径
            upload_file.seek(0)
            file_size = len(upload_file.read()) // app.config["M_SIZE"]  # 该文件的大小 M为单位
            search_param = {
                "is_delete": False,
                "name": name
            }
            file_obj = File.query.filter_by(**search_param).first()
            if file_obj:  # 已有数据更新数据
                file_obj.type = type
                file_obj.size = file_size,
                file_obj.path = file_path
            else:
                file_obj = File(name=name, type=type, size=file_size, path=file_path)
            db.session.add(file_obj)
            db.session.commit()
            un_zip(file_path)
            code = 0
            msg = "文件上传成功"
        else:
            code = -1
            msg = "文件格式不正确或文件出错"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "文件上传失败"
    return response_tem(code=code, msg=msg)


@file.route("/files", methods=["POST"])
@jwt_required
def files():
    """
    查询已上传文件的信息, 包括文件名 文件大小, 文件类型 , 最后更新时间
    :return:
    """
    json_data = return_json(request)
    page = json_data.get("page", None)
    page_size = json_data.get("page_size", 10)
    if not (page and page_size):
        code = -1
        msg = "page和page_size参数必填"
        return response_tem(code=code, msg=msg)

    if type(page) is str:
        if not page.isdigit():
            code = -1
            msg = "page应该是数字类型"
            return response_tem(code=code, msg=msg)

    if type(page_size) is str:
        if not page_size.isdigit():
            code = -1
            msg = "page_size应该是数字类型"
            return response_tem(code=code, msg=msg)
    page = int(page)
    page_size = int(page_size)

    all_info = []
    try:
        search_param = {
            "is_delete": False
        }
        pagination = File.query.filter_by(**search_param).paginate(page, page_size, 0)
        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page
        all_file = pagination.items
        for info in all_file:
            file_info = {
                "file_id": info.id,
                "name": info.name,
                "type": info.type,
                "size": info.size,
                "update_time": info.update_time
            }
            all_info.append(file_info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None
        all_page = None
        now_page = None
    return response_tem(
        code=code,
        data=all_info,
        msg=msg,
        all_data=all_data,
        all_page=all_page,
        page=now_page
    )


@file.route("/delete_file", methods=["POST"])
@jwt_required
def delete_file():
    """
    删除指定上传的文件
    :return:
    """
    json_data = return_json(request)
    file_id = json_data.get("file_id", None)
    if not file_id or len(file_id) != 32:
        code = -1
        msg = "File_id is required, and its length should be 32"
        return response_tem(code=code, msg=msg)
    try:
        search_param = {
            "is_delete": False,
            "id": file_id
        }
        file_obj = File.query.filter_by(**search_param).first()
        if not file_obj:
            code = -1
            msg = "没有找到该文件, 可能已被删除"
            return response_tem(code=code, msg=msg)
        file_path = file_obj.path
        dirname, name, suffix = get_file_name(file_path)
        str_time = localtime()
        file_obj.name = name + str_time
        file_obj.is_delete = True
        db.session.add(file_obj)
        if os.path.exists(file_path):
            new_name = name + str_time + "." + suffix  # 带时间的文件名
            new_file_path = os.path.join(dirname, new_name)
            os.rename(file_path, new_file_path)
            file_obj.path = new_file_path
            db.session.add(file_obj)
        dir_path = os.path.join(dirname, name)  # 解压文件目录
        db.session.commit()
        if os.path.isdir(dir_path):
            new_dir_path = os.path.join(dirname, name + str_time)
            os.rename(dir_path, new_dir_path)

        code = 0
        msg = "文件删除成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "文件删除失败"
    return response_tem(code=code, msg=msg)
