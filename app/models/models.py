from app import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import uuid


def gen_id():
    return uuid.uuid4().hex


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间
    is_delete = db.Column(db.Boolean, default=False, nullable=False)  # 删除标识


class User(BaseModel, db.Model):
    __tablename__ = "tbuser"

    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 用户uuid
    name = db.Column(db.String(32), nullable=False, unique=True)  # 用户名
    password_hash = db.Column(db.String(128), nullable=False)  # 用户密码
    number = db.Column(db.String(32))  # 用户手机号

    @property
    def password(self):
        raise AttributeError("you can not read it")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User %r>" % self.id


class ServerVersionRelationship(db.Model):
    __tablename__ = "tbserverversionrel"
    server_id = db.Column(db.String(32), db.ForeignKey("tbserver.id"), primary_key=True)
    version_id = db.Column(db.String(32), db.ForeignKey("tbversion.id"), primary_key=True)
    status = db.Column(db.Integer)  # 运行状态 0 未运行  1 正在运行
    timestamp = db.Column(db.DateTime, default=datetime.now)


"""
项目表：

uuid
项目名称 
项目服务对应关系（项目服务 一对多）
项目说明
项目路径 （相对）
"""


class Project(BaseModel, db.Model):
    __tablename__ = "tbproject"
    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 项目uuid
    project_name = db.Column(db.String(32), nullable=False)  # 项目名称
    project_instruction = db.Column(db.String(512))  # 项目说明
    project_path = db.Column(db.String(128))  # 项目存放相对路径
    services = db.relationship("Service", backref="project", lazy="dynamic")  # 该项目下的所有服务


"""
服务表

uuid
服务名
服务-版本对应关系（服务版本一对多）
项目外键 （属于哪个服务）

"""


class Service(BaseModel, db.Model):  # 服务表 项目文件
    __tablename__ = "tbservice"

    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 服务uuid
    service_name = db.Column(db.String(64), nullable=False)  # 服务文件名
    service_instruction = db.Column(db.String(512))  # 服务说明
    remote_path = db.Column(db.String(128))  # 项目远程部署的路径
    project_id = db.Column(db.String(32), db.ForeignKey("tbproject.id"))  # 该服务所属项目id
    versions = db.relationship("Version", backref="service", lazy="dynamic")  # 该服务下的所有版本
    dependencys = db.relationship("Dependency", backref="service", lazy="dynamic")  # 该服务下的所有依赖项

    # type = db.Column(db.String(32), nullable=False)  # 服务类型
    # size = db.Column(db.String(32), nullable=False)  # 服务文件大小 M为单位
    # path = db.Column(db.String(128), nullable=False)  # 文件存储的路径
    # servers = db.relationship("ServerFileRelationship", foreign_keys=[ServerFileRelationship.file_id],
    #                         backref=db.backref("file", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")
    def __repr__(self):
        return "<Service %r>" % self.id


"""
服务版本表：

uuid
版本号
服务外建
版本说明
配置文件的路径
存放路径（该服务版本的相对路径）
配置表外建
"""


class Version(BaseModel, db.Model):  # 版本表
    __tablename__ = "tbversion"
    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 版本uuid
    version_number = db.Column(db.String(32))  # 版本号
    version_instruction = db.Column(db.String(512))  # 版本说明
    config_path = db.Column(db.String(128))  # 配置文件的路径
    version_path = db.Column(db.String(128))  # 该版本存放服务器相对路径
    service_id = db.Column(db.String(32), db.ForeignKey("tbservice.id"))  # 该版本所属服务id
    configurations = db.relationship("Configuration", backref="version", lazy="dynamic")  # 该版本下的所有配置项
    servers = db.relationship("ServerVersionRelationship", foreign_keys=[ServerVersionRelationship.version_id],
                              backref=db.backref("version", lazy="joined"), lazy="dynamic",
                              cascade="all, delete-orphan")


"""
配置表：

uuid
版本表外建
配置项
"""


class Configuration(BaseModel, db.Model):  # 配置表
    __tablename__ = "tbconfiguration"
    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 配置uuid
    item = db.Column(db.String(64), nullable=False)  # 配置项名称
    version_id = db.Column(db.String(32), db.ForeignKey("tbversion.id"))  # 该配置项所属版本id


"""
依赖表
uuid
服务表外键
依赖服务的名称
依赖服务的版本

"""


class Dependency(BaseModel, db.Model):  # 依赖表
    __tablename__ = "tbdependency"
    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 依赖uuid
    dependency_name = db.Column(db.String(64))  # 依赖服务的名称
    version_number = db.Column(db.String(32))  # 依赖服务的版本号
    service_id = db.Column(db.String(32), db.ForeignKey("tbservice.id"))  # 该依赖项所属服务id


class Server(BaseModel, db.Model):
    __tablename__ = "tbserver"

    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)  # 服务文件uuid
    name = db.Column(db.String(64), nullable=False)  # 服务器名称
    ip = db.Column(db.String(32), nullable=False)  # 服务器ip地址
    port = db.Column(db.String(16), nullable=False)  # 服务器端口
    user_name = db.Column(db.String(32), nullable=False)  # 服务器用户名
    user_password = db.Column(db.String(32), nullable=False)  # 服务器用户密码
    secret_key = db.Column(db.String(256))  # 服务器秘钥
    # files = db.relationship("File", backref="server", lazy="dynamic")  # 部署到该服务器上的项目
    versions = db.relationship("ServerVersionRelationship", foreign_keys=[ServerVersionRelationship.server_id],
                               backref=db.backref("server", lazy="joined"), lazy="dynamic",
                               cascade="all, delete-orphan")

    # version_id = db.Column(db.String(32), db.ForeignKey("tbversion.id"))  # 该依赖项所属服务id

    def __repr__(self):
        return "<Server %r>" % self.id
