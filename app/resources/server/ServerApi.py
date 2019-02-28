import os
# import json
from . import server
from flask import request
from app.tools.return_tools import response_tem, return_json
from app.models.models import Server
# from fabric import Connection
from loggings import logger
from flask_jwt_extended import (
    jwt_required)
from app import create_app
from app.tools.listenRedis import publish_redis
# from app.tools.unzip_tools import un_zip
# from app.tools.modify_config import (
#     spzlapi_config,
#     spzlweb_config,
#     mssprism_config,
#     ums_config)

app, db = create_app("baseConfig")


def upload_file(c, folder_name, bash_name=None, remote_dir="/opt/"):
    """
    本地文件夹打包上传到服务器并解压, 也可远程执行bash脚本
    :param c: conn远程连接
    :param folder_name: 本地文件夹名称
    :param bash_name: 需要远程执行的bash脚本 需放在项目文件夹第一层目录
    :param remote_dir: 远程文件夹 默认/opt/ 必须以/结尾
    :return:
    """
    if not c or not folder_name:
        return False
    try:
        zip_name = folder_name + ".zip"
        upload_folder = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"])
        c.local("cd {} && zip -r {} {}".format(upload_folder, zip_name, folder_name))
        code = 0
        data = "40"
        msg = "项目压缩完成"
        res = response_tem(code=code, data=data, msg=msg)
        redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
        if not redis_result:
            logger.error("{} 推送出错".format(res))

        zip_path = upload_folder + "/{}".format(zip_name)
        if remote_dir[-1] != "/":
            remote_dir = remote_dir + "/"
        c.run("cd {} && rm -rf {}*".format(remote_dir, folder_name))
        c.put(zip_path, remote_dir)  # 上传文件
        code = 0
        data = "60"
        msg = "项目上传完成"
        res = response_tem(code=code, data=data, msg=msg)

        redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
        if not redis_result:
            logger.error("{} 推送出错".format(res))

        c.run("cd {} && unzip {}".format(remote_dir, zip_name))
        code = 0
        data = "80"
        msg = "项目远程解包完成"
        res = response_tem(code=code, data=data, msg=msg)
        redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
        if not redis_result:
            logger.error("{} 推送出错".format(res))

        proj_folder = remote_dir + folder_name  # 远程项目目录
        if bash_name:
            c.run("cd {} && sh {}".format(proj_folder, bash_name))
            code = 0
            data = "90"
            msg = "项目脚本执行完成"
            res = response_tem(code=code, data=data, msg=msg)

            redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
            if not redis_result:
                logger.error("{} 推送出错".format(res))
        return True
    except Exception as e:
        logger.error(e)
        return False


@server.route("/add_server", methods=["POST"])
@jwt_required
def add_server():
    """
    add server
    :return:
    """
    json_data = return_json(request)
    name = json_data.get("name", None)
    ip = json_data.get("ip", None)
    port = json_data.get("port", None)
    user_name = json_data.get("user_name", None)
    user_password = json_data.get("user_password", None)

    param_list = [name, ip, port, user_name, user_password]
    for param in param_list:
        if param is None:
            code = -1
            msg = "all param is required"
            return response_tem(code=code, msg=msg)
    try:
        param = {
            "is_delete": False,
            "name": name
        }
        server_list = Server.query.filter_by(**param).all()
        if len(server_list):
            code = -1
            msg = "该名称已存在"
            return response_tem(code=code, msg=msg)

        param = {
            "is_delete": False,
            "ip": ip
        }
        server_list = Server.query.filter_by(**param).all()
        if len(server_list):
            code = -1
            msg = "该ip已存在"
            return response_tem(code=code, msg=msg)

        server_param = {
            "name": name,
            "ip": ip,
            "port": str(port),
            "user_name": user_name,
            "user_password": user_password
        }
        new_server = Server(**server_param)
        db.session.add(new_server)
        db.session.commit()
        code = 0
        msg = "添加成功"

    except Exception as e:
        logger.error(e)
        code = -1
        msg = "添加失败"
    return response_tem(code=code, msg=msg)


@server.route("/server", methods=["POST"])
@jwt_required
def server_list():
    """
    查询所有server列表
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
        pagination = Server.query.filter_by(**search_param).paginate(page, page_size, 0)
        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page
        all_server = pagination.items
        for info in all_server:
            rel_list = info.files
            f_list = []  # 存储该服务器中 部署的所有项目
            for rel in rel_list:
                f_list.append(rel.file.name)

            server_info = {
                "server_id": info.id,
                "name": info.name,
                "ip": info.ip,
                "port": info.port,
                "user_name": info.user_name,
                "user_password": info.user_password,
                "status": f_list
            }
            all_info.append(server_info)
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
        msg=msg,
        data=all_info,
        all_data=all_data,
        all_page=all_page,
        page=now_page
    )


@server.route("/search_server", methods=["POST"])
@jwt_required
def search_server():
    """
    根据服务id查询相关信息,用于修改server信息回显
    :return:
    """
    json_data = return_json(request)
    server_id = json_data.get("server_id", None)
    if not server_id:
        code = -1
        msg = "server_id is required"
        return response_tem(
            code=code,
            msg=msg
        )
    try:
        search_param = {
            "is_delete": False,
            "id": server_id
        }
        data = Server.query.filter_by(**search_param).first()
        if not data:
            code = -1
            msg = "没有找到该server"
            return response_tem(code=code, msg=msg)
        info = {
            "name": data.name,
            "ip": data.ip,
            "port": data.port,
            "user_name": data.user_name,
            "user_password": data.user_password
        }
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        info = None
    return response_tem(code, data=info, msg=msg)


@server.route("/modify_server", methods=["POST"])
@jwt_required
def modify_server():
    """
    根据server_id修改server信息
    :return:
    """
    json_data = return_json(request)
    server_id = json_data.get("server_id", None)
    name = json_data.get("name", None)
    ip = json_data.get("ip", None)
    port = json_data.get("port", None)
    user_name = json_data.get("user_name", None)
    user_password = json_data.get("user_password", None)
    if not server_id:
        code = -1
        msg = "server_id is required"
        return response_tem(code=code, msg=msg)
    param_list = [name, ip, port, user_name, user_password]
    for param in param_list:
        if not param:
            code = -1
            msg = "all param is required"
            return response_tem(code=code, msg=msg)
    search_param = {
        "is_delete": False,
        "id": server_id
    }
    try:

        server_info = Server.query.filter_by(**search_param).first()
        if server_info.name != name:
            param = {
                "is_delete": False,
                "name": name
            }
            server_list = Server.query.filter_by(**param).all()
            if len(server_list):
                code = -1
                msg = "该名称已存在"
                return response_tem(code=code, msg=msg)
        if server_info.ip != ip:
            param = {
                "is_delete": False,
                "ip": ip
            }
            server_list = Server.query.filter_by(**param).all()
            if len(server_list):
                code = -1
                msg = "该ip已存在"
                return response_tem(code=code, msg=msg)

        server_info.name = name
        server_info.ip = ip
        server_info.port = port
        server_info.user_name = user_name
        server_info.user_password = user_password
        db.session.add(server_info)
        db.session.commit()
        code = 0
        msg = "修改成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "修改失败"
    return response_tem(code=code, msg=msg)


@server.route("/delete_server", methods=["post"])
@jwt_required
def delete_server():
    """
    根据id删除某个server
    :return:
    """
    json_data = return_json(request)
    server_id = json_data.get("server_id", None)
    if not server_id:
        code = -1
        msg = "server_id is required"
        return response_tem(code=code, msg=msg)
    try:
        search_param = {
            "is_delete": False,
            "id": server_id
        }
        server_info = Server.query.filter_by(**search_param).first()
        if not server_info:
            code = -1
            msg = "没找到该server, 可能已经删除"
            return response_tem(code=code, msg=msg)
        server_info.is_delete = True
        db.session.add(server_info)
        db.session.commit()
        code = 0
        msg = "删除成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "删除失败"
    return response_tem(code=code, msg=msg)

# @server.route("/deploy", methods=["POST"])
# @jwt_required
# def deploy_server():
#     json_data = return_json(request)
#     server_id = json_data.get("server_id", None)
#     file_id = json_data.get("file_id", None)
#     stream_ip = json_data.get("stream_ip", None)
#     rtmp_ip = json_data.get("rtmp_ip", None)
#     application_ip = json_data.get("application_ip", None)
#     database_ip = json_data.get("database_ip", None)
#     database_password = json_data.get("database_password", None)
#
#     if server_id is None or file_id is None:
#         code = -1
#         msg = "server_id and file_id is required"
#         return response_tem(code=code, msg=msg)
#     server_search_param = {
#         "is_delete": False,
#         "id": server_id
#     }
#     file_search_param = {
#         "is_delete": False,
#         "id": file_id
#     }
#     try:
#         server_obj = Server.query.filter_by(**server_search_param).first()
#
#         file_obj = File.query.filter_by(**file_search_param).first()
#         if (not server_obj) or (not file_obj):
#             code = -1
#             msg = "该服务器配置或服务文件不存在"
#             return response_tem(code=code, msg=msg)
#
#         # 服务器信息
#         server_ip = server_obj.ip
#         server_port = int(server_obj.port)
#         server_user_name = server_obj.user_name
#         server_user_password = server_obj.user_password
#
#         c = Connection(host=server_ip, user=server_user_name, port=server_port,
#                        connect_kwargs={'password': server_user_password})
#         try:
#             c.run("whoami")
#         except Exception as e:
#             logger.error(e)
#             code = -1
#             msg = "ssh连接出错"
#             return response_tem(code=code, msg=msg)
#
#         # 项目文件信息
#         file_name = file_obj.name
#         check_name = file_name.split("_")[0]  # 去掉版本号
#
#         check_name = check_name.lower()  # 文件名转小写
#         bash_name = None
#         # bash_name = "install_{}.sh".format(check_name)  # 运行的脚本名称
#         if not check_name in app.config["PROJ"].keys():
#             code = -1
#             msg = "该项目无法部署"
#             return response_tem(code=code, msg=msg)
#
#         file_path = os.path.join(app.root_path, app.config["UPLOAD_FOLDER"], file_name)  # 项目文件路径
#         config_path = app.config["PROJ"][check_name]
#
#         code = 0
#         data = "0"
#         msg = "项目开始部署..."
#         res = response_tem(code=code, data=data, msg=msg)
#         redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#         if not redis_result:
#             code = -1
#             msg = "redis推送失败"
#             return response_tem(code=code, msg=msg)
#
#         if config_path:
#             full_path = file_path + config_path  # 配置文件完整路径
#             if not os.path.exists(full_path):
#                 code = -1
#                 msg = "服务器中该项目可能已被删除"
#                 logger.error("{}找不到配置文件".format(full_path))
#                 return response_tem(code=code, msg=msg)
#
#         if check_name == "spzlapi":
#
#             param_list = [database_ip, database_password, application_ip, stream_ip]
#             for param in param_list:
#                 if param is None:
#                     code = -1
#                     msg = "参数不能为空"
#                     return response_tem(code=code, msg=msg)
#             result = spzlapi_config(full_path, *param_list)
#             if not result:
#                 code = -1
#                 msg = "配置文件写入错误"
#                 logger.error("{}配置文件写入错误".format(full_path))
#                 return response_tem(code=code, msg=msg)
#
#             code = 0
#             data = "20"
#             msg = "修改配置文件完成"
#             res = response_tem(code=code, data=data, msg=msg)
#             redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#             if not redis_result:
#                 logger.error("{} 推送出错".format(res))
#
#             result = upload_file(c, file_name, bash_name, remote_dir=app.config["REMOTE_DIR"])
#             if not result:
#                 code = -1
#                 msg = "项目打包上传出错"
#                 res = response_tem(code=code, msg=msg)
#                 redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#                 if not redis_result:
#                     logger.error("{} 推送出错".format(res))
#                 return res
#
#         elif check_name == "spzlweb":
#
#             param_list = [application_ip, stream_ip]
#             for param in param_list:
#                 if param is None:
#                     code = -1
#                     msg = "参数不能为空"
#                     return response_tem(code=code, msg=msg)
#             result = spzlweb_config(full_path, *param_list)
#             if not result:
#                 code = -1
#                 msg = "配置文件写入错误"
#                 logger.error("{}配置文件写入错误".format(full_path))
#                 return response_tem(code=code, msg=msg)
#
#             code = 0
#             data = "20"
#             msg = "修改配置文件完成"
#             res = response_tem(code=code, data=data, msg=msg)
#             redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#             if not redis_result:
#                 logger.error("{} 推送出错".format(res))
#
#             result = upload_file(c, file_name, bash_name, remote_dir=app.config["REMOTE_DIR"])
#             if not result:
#                 code = -1
#                 msg = "项目打包上传出错"
#                 res = response_tem(code=code, msg=msg)
#                 redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#                 if not redis_result:
#                     logger.error("{} 推送出错".format(res))
#                 return res
#
#         elif check_name == "umscore":
#             param_list = [database_ip, database_password, application_ip]
#             for param in param_list:
#                 if param is None:
#                     code = -1
#                     msg = "参数不能为空"
#                     return response_tem(code=code, msg=msg)
#             result = ums_config(full_path, *param_list)
#             if not result:
#                 code = -1
#                 msg = "配置文件写入错误"
#                 logger.error("{}配置文件写入错误".format(full_path))
#                 return response_tem(code=code, msg=msg)
#             code = 0
#             data = "20"
#             msg = "修改配置文件完成"
#             res = response_tem(code=code, data=data, msg=msg)
#             redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#             if not redis_result:
#                 logger.error("{} 推送出错".format(res))
#             result = upload_file(c, file_name, bash_name, remote_dir=app.config["REMOTE_DIR"])
#             if not result:
#                 code = -1
#                 msg = "项目打包上传出错"
#                 res = response_tem(code=code, msg=msg)
#                 redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#                 if not redis_result:
#                     logger.error("{} 推送出错".format(res))
#                 return res
#
#         elif check_name == "mssprism":
#             param_list = [stream_ip, rtmp_ip, application_ip]
#             for param in param_list:
#                 if param is None:
#                     code = -1
#                     msg = "参数不能为空"
#                     return response_tem(code=code, msg=msg)
#             result = mssprism_config(full_path, *param_list)
#             if not result:
#                 code = -1
#                 msg = "配置文件写入错误"
#                 logger.error("{}配置文件写入错误".format(full_path))
#                 return response_tem(code=code, msg=msg)
#
#             code = 0
#             data = "20"
#             msg = "修改配置文件完成"
#             res = response_tem(code=code, data=data, msg=msg)
#             redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#             if not redis_result:
#                 logger.error("{} 推送出错".format(res))
#
#             result = upload_file(c, file_name, bash_name, remote_dir=app.config["REMOTE_DIR"])
#             if not result:
#                 code = -1
#                 msg = "项目打包上传出错"
#                 res = response_tem(code=code, msg=msg)
#                 redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#                 if not redis_result:
#                     logger.error("{} 推送出错".format(res))
#                 return res
#
#         else:
#             result = upload_file(c, file_name, bash_name, remote_dir=app.config["REMOTE_DIR"])
#             if not result:
#                 code = -1
#                 msg = "项目打包上传出错"
#                 res = response_tem(code=code, msg=msg)
#                 redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#                 if not redis_result:
#                     logger.error("{} 推送出错".format(res))
#                 return res
#         file_obj.server = server_obj
#         server_obj.files = [ServerFileRelationship(server_id=server_obj.id, file_id=file_obj.id)]
#         db.session.add(file_obj)
#         db.session.commit()
#         code = 0
#         data = "100"
#         msg = "部署成功"
#         res = response_tem(code=code, data=data, msg=msg)
#         redis_result = publish_redis(app.config["REDIS_HOST"], app.config["REDIS_CHANNEL"], res)
#         if not redis_result:
#             logger.error("{} 推送出错".format(res))
#         code = 0
#         msg = "部署成功"
#
#     except Exception as e:
#         logger.error(e)
#         code = -1
#         msg = "部署失败{}".format(e)
#     return response_tem(code=code, msg=msg)
