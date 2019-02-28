import os
import demjson
from . import service
from loggings import logger
from flask import request
from app.models.models import Service, Version, Project, Configuration, Dependency, Server
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


@service.route('/upload', methods=['POST'])
@jwt_required
def upload_files():
    upload_file = request.files['file']
    try:
        if upload_file and allowed_file(upload_file.filename):
            filename = secure_filename(upload_file.filename)  # 带后缀的文件名
            name = filename[: -4]  # 不带后缀的文件名
            time_dir_name = localtime()  # 文件夹以当前时间命名
            base_time_dir_name = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], time_dir_name)  # 时间文件夹绝对路径
            os.system("mkdir {}".format(base_time_dir_name))
            file_path = os.path.join(base_time_dir_name, filename)
            upload_file.save(file_path)  # app.root_path获取当前项目绝对路径
            # upload_file.seek(0)
            # file_size = len(upload_file.read()) // app.config["M_SIZE"]  # 该文件的大小 M为单位
            # 先解压
            # 读项目配置文件， 获取项目名，服务名 配置信息等
            # 获取信息之后写入表中，在写表之前先判断该项目是否已经存在，
            # 存在， 更新相关数据。
            # 不存在 就添加数据

            os.system("unzip {} -d {}".format(file_path, base_time_dir_name))  # 解压操作
            base_proj_dir = os.path.join(base_time_dir_name, name)  # 项目文件夹绝对路径
            proj_dir = os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, name)  # 项目文件夹相对路径
            json_path = os.path.join(base_proj_dir, app.config["PROJ_CONFIG"])  # 项目配置文件所在路径
            with open(json_path, 'r') as f_read:
                json_data = demjson.decode(f_read.read())
                project_name = json_data["project_name"]
                project_instruction = json_data["project_instruction"]
                search_param = {
                    "is_delete": False,
                    "project_name": project_name
                }
                proj_first = Project.query.filter_by(**search_param).first()
                if proj_first:  # 该项目已经上传
                    logger.error("proj_name: {}".format(proj_first))
                    services = json_data["services"]
                    for service_info in services:
                        service_name = service_info.get("service_name")
                        service_instruction = service_info.get("service_instruction")
                        version_number = service_info.get("version_number")
                        version_instruction = service_info.get("version_instruction")
                        version_path = service_info.get("version_path")
                        remote_path = service_info.get("remote_path")
                        config_path = service_info.get("config_path")
                        service_obj_list = [service_obj for service_obj in proj_first.services if service_obj.service_name == service_name]
                        # logger.error([service_obj.service_name for service_obj in proj_first.services])
                        if not service_obj_list:
                            # 项目中添加新服务
                            # logger.error("执行")
                            service_param_info = {
                                "service_name": service_name,
                                "service_instruction": service_instruction,
                                "remote_path": remote_path,
                                "project": proj_first
                            }
                            service_obj = Service(**service_param_info)
                            db.session.add(service_obj)  # 新服务入库

                            version_param_info = {
                                "version_number": version_number,
                                "version_instruction": version_instruction,
                                "config_path": os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, config_path),
                                "version_path": os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, version_path),
                                "service": service_obj
                            }
                            version_obj = Version(**version_param_info)
                            db.session.add(version_obj)  # 服务版本入库
                            configurations = service_info.get("configurations")
                            for configuration_info in configurations:
                                config_name = configuration_info.get("config_name")
                                config_param_info = {
                                    "item": config_name,
                                    "version": version_obj
                                }
                                config_obj = Configuration(**config_param_info)
                                db.session.add(config_obj)
                            relys = service_info.get("relys")
                            for rely_info in relys:
                                service_name = rely_info.get("service_name")
                                version_number = rely_info.get("version_number")
                                rely_param_info = {
                                    "dependency_name": service_name,
                                    "version_number": version_number,
                                    "service": service_obj
                                }
                                dependency_obj = Dependency(**rely_param_info)
                                db.session.add(dependency_obj)
                            continue
                        # else:  # 服务存在更新服务信息
                        #     service_obj = service_obj_list[0]

                        search_param = {
                            "is_delete": False,
                            "service_name": service_name
                        }
                        service_obj = Service.query.filter_by(**search_param).first()
                        # logger.error("hh: {}".format(service_obj))
                        # logger.error([version.version_number for version in service_obj.versions])

                        if version_number not in [version_obj.version_number for version_obj in service_obj.versions]:

                            # 服务添加新版本
                            version_param_info = {
                                "version_number": version_number,
                                "version_instruction": version_instruction,
                                "config_path": os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, config_path),
                                "version_path": os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, version_path),
                                "service": service_obj
                            }
                            version_obj = Version(**version_param_info)
                            db.session.add(version_obj)
                            # 还要增加依赖表字段
                            configurations = service_info.get("configurations")
                            for configuration_info in configurations:
                                config_name = configuration_info.get("config_name")
                                config_param_info = {
                                    "item": config_name,
                                    "version": version_obj
                                }
                                config_obj = Configuration(**config_param_info)
                                db.session.add(config_obj)
                            relys = service_info.get("relys")
                            for rely_info in relys:
                                service_name = rely_info.get("service_name")
                                version_number = rely_info.get("version_number")
                                rely_param_info = {
                                    "dependency_name": service_name,
                                    "version_number": version_number,
                                    "service": service_obj
                                }
                                dependency_obj = Dependency(**rely_param_info)
                                db.session.add(dependency_obj)
                        # else:

                else:
                    project_param_info = {
                        "project_name": project_name,
                        "project_instruction": project_instruction,
                        "project_path": proj_dir
                    }
                    proj_obj = Project(**project_param_info)
                    db.session.add(proj_obj)
                    services = json_data["services"]
                    for service_info in services:
                        service_name = service_info.get("service_name")
                        service_instruction = service_info.get("service_instruction")
                        version_number = service_info.get("version_number")
                        version_instruction = service_info.get("version_instruction")
                        version_path = service_info.get("version_path")
                        remote_path = service_info.get("remote_path")
                        config_path = service_info.get("config_path")
                        service_param_info = {
                            "service_name": service_name,
                            "service_instruction": service_instruction,
                            "remote_path": remote_path,
                            "project": proj_obj
                        }
                        service_obj = Service(**service_param_info)
                        db.session.add(service_obj)
                        version_param_info = {
                            "version_number": version_number,
                            "version_instruction": version_instruction,
                            "config_path": os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, config_path),
                            "version_path": os.path.join(app.config['UPLOAD_FOLDER'], time_dir_name, version_path),
                            "service": service_obj
                        }
                        version_obj = Version(**version_param_info)
                        db.session.add(version_obj)
                        configurations = service_info.get("configurations")
                        for configuration_info in configurations:
                            config_name = configuration_info.get("config_name")
                            config_param_info = {
                                "item": config_name,
                                "version": version_obj
                            }
                            config_obj = Configuration(**config_param_info)
                            db.session.add(config_obj)
                        relys = service_info.get("relys")
                        for rely_info in relys:
                            service_name = rely_info.get("service_name")
                            version_number = rely_info.get("version_number")
                            rely_param_info = {
                                "dependency_name": service_name,
                                "version_number": version_number,
                                "service": service_obj
                            }
                            dependency_obj = Dependency(**rely_param_info)
                            db.session.add(dependency_obj)
            db.session.commit()

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


@service.route("/project", methods=["POST"])
def project():
    """
    查询所有项目信息
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
        pagination = Project.query.filter_by(**search_param).paginate(page, page_size, 0)
        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page
        all_proj = pagination.items
        for proj in all_proj:
            proj_info = {
                "id": proj.id,
                "project_name": proj.project_name,
                "update_time": proj.update_time
            }
            all_info.append(proj_info)
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


@service.route("/delete_project", methods=["POST"])
def delete_project():
    """
    根据项目id删除某个项目,如果该项目已经部署到远程,则删除失败
    :return:
    """
    json_data = return_json(request)
    project_id = json_data.get("project_id", None)
    if not project_id:
        code = -1
        msg = "project_id is required"
        return response_tem(code=code, msg=msg)
    all_info = []
    flag = False
    try:
        search_param = {
            "is_delete": False,
            "id": project_id
        }
        proj_obj = Project.query.filter_by(**search_param).first()
        if not proj_obj:
            code = -1
            msg = "删除失败,该项目不存在"
            return response_tem(code=code, msg=msg)
        all_service_obj = proj_obj.services
        all_service_obj = [service for service in all_service_obj if service.is_delete == False]
        for service_obj in all_service_obj:
            service_name = service_obj.service_name
            all_version_obj = service_obj.versions
            all_version_obj = [version for version in all_version_obj if version.is_delete == False]

            for version in all_version_obj:
                server_infos = []
                version_number = version.version_number
                all_server_obj = version.servers
                all_server_obj = [server for server in all_server_obj if server.status == 1]

                if all_server_obj:
                    for server_obj in all_server_obj:
                        server_info = {
                            "ip": server_obj.server.ip,
                            "name": server_obj.server.name
                        }
                        server_infos.append(server_info)
                        flag = True
                    service_info = {
                        "service_name": service_name,
                        "version_number": version_number,
                        "server_infos": server_infos
                    }

                    all_info.append(service_info)
        if flag:
            code = -1
            msg = "该项目已有服务部署成功,请卸载服务后再删除"
            return response_tem(code=code, msg=msg, data=all_info)
        else:
            proj_obj.is_delete = True
            db.session.add(proj_obj)
            db.session.commit()
            code = 0
            msg = "删除项目成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "删除项目出错"
    return response_tem(code=code, msg=msg)


@service.route("/project_detail", methods=["POST"])
def project_detail():
    """
    根据项目id查看项目详情,项目说明以及项目包含的服务等
    :return:
    """
    json_data = return_json(request)
    project_id = json_data.get("project_id", None)
    if not project_id:
        code = -1
        msg = "project_id is required"
        return response_tem(code=code, msg=msg)
    all_info = []
    try:
        search_param = {
            "is_delete": False,
            "id": project_id
        }
        proj_obj = Project.query.filter_by(**search_param).first()
        if not proj_obj:
            code = -1
            msg = "查询失败, 该项目不存在或已被删除"
            return response_tem(code=code, msg=msg)
        project_name = proj_obj.project_name
        all_service_obj = proj_obj.services
        all_service_obj = [service for service in all_service_obj if service.is_delete == False]
        service_info_list = []
        for service_obj in all_service_obj:
            service_info = {
                "service_id": service_obj.id,
                "service_name": service_obj.service_name,
                "service_instruction": service_obj.service_instruction
            }
            service_info_list.append(service_info)
        proj_info = {
            "project_name": project_name,
            "service_info": service_info_list
        }
        all_info.append(proj_info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(code=code, msg=msg, data=all_info)


@service.route("/service_detail", methods=["POST"])
def service_detail():
    """
    根据服务id查询服务详细信息, 服务的运行情况和依赖服务信息等
    :return:
    """
    json_data = return_json(request)
    service_id = json_data.get("service_id", None)
    if not service_id:
        code = -1
        msg = "service_id is required"
        return response_tem(code=code, msg=msg)
    all_info = []
    try:
        search_param = {
            "is_delete": False,
            "id": service_id
        }
        service_obj = Service.query.filter_by(**search_param).first()
        if not service_obj:
            code = -1
            msg = "查询失败, 该服务不存在或已被删除"
            return response_tem(code=code, msg=msg)
        service_instruction = service_obj.service_instruction
        service_name = service_obj.service_name
        all_version_obj = service_obj.versions
        all_version_obj = [version for version in all_version_obj if version.is_delete == False]
        service_info_list = []
        rely_info_list = []
        for version_obj in all_version_obj:
            all_rel_obj = version_obj.servers
            all_rel_obj = [rel for rel in all_rel_obj if rel.status == 1]
            if all_rel_obj:
                version_number = version_obj.version_number
                for rel in all_rel_obj:
                    rel_info = {
                        "service_name": service_name,
                        "server_ip": rel.server.ip,
                        "server_name": rel.server.name,
                        "status": rel.status,
                        "version_number": version_number
                    }
                    service_info_list.append(rel_info)
        all_rely_obj = service_obj.dependencys
        all_rely_obj = [rely for rely in all_rely_obj if rely.is_delete == False]
        for rely_obj in all_rely_obj:
            dependency_name = rely_obj.dependency_name
            version_number = rely_obj.version_number
            search_param = {
                "is_delete": False,
                "service_name": dependency_name
            }
            dep_service = Service.query.filter_by(**search_param).first()  # 依赖服务对象
            if not dep_service:
                rely_info = {
                    "service_name": dependency_name,
                    "status": 0,
                    "version_number": version_number
                }
                rely_info_list.append(rely_info)
                continue
            all_dep_version = dep_service.versions
            dep_version_list = [version for version in all_dep_version if version.version_number == version_number]
            if dep_version_list:  # 依赖的版本存在
                dep_version = dep_version_list[0]
                all_dep_rel = dep_version.servers
                all_dep_rel = [rel for rel in all_dep_rel if rel.status == 1]
                if all_dep_rel:  #存在正在执行的版本
                    for rel in all_dep_rel:
                        rely_info = {
                        "service_name": dependency_name,
                        "server_ip": rel.server.ip,
                        "server_name": rel.server.name,
                        "status": rel.status,
                        "version_number": version_number
                    }
                        rely_info_list.append(rely_info)
                else:  # 该本版未执行
                    rely_info = {
                        "service_name": dependency_name,
                        "status": 0,
                        "version_number": version_number
                    }
                    rely_info_list.append(rely_info)

            else:  # 依赖版本不存在
                rely_info = {
                    "service_name": dependency_name,
                    "status": 0,
                    "version_number": version_number
                }
                rely_info_list.append(rely_info)
        info = {
            "service_instruction": service_instruction,
            "service_info": service_info_list,
            "rely_info": rely_info_list
        }
        all_info.append(info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(code=code, msg=msg, data=all_info)


@service.route("/version", methods=["POST"])
def version():
    """
    根据服务id获取该服务所有有效版本号
    :return:
    """
    json_data = return_json(request)
    service_id = json_data.get("service_id", None)
    if not service_id:
        code = -1
        msg = "service_id is required"
        return response_tem(code=code, msg=msg)
    all_info = []
    try:
        search_param = {
            "is_delete": False,
            "id": service_id
        }
        service_obj = Service.query.filter_by(**search_param).first()
        if not service_obj:
            code = -1
            msg = "查询失败, 该服务不存在或已被删除"
            return response_tem(code=code, msg=msg)
        all_version_obj = service_obj.versions
        all_version_obj = [version for version in all_version_obj if version.is_delete == False]
        for version_obj in all_version_obj:
            version_info = {
                "version_id": version_obj.id,
                "version_number": version_obj.version_number,
                "version_instruction": version_obj.version_instruction
            }
            all_info.append(version_info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(code=code, msg=msg, data=all_info)

