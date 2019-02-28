class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = "cn.com.soyuan.www"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@127.0.0.1:3306/deploy"  # 公司正式数据库
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@127.0.0.1:3306/Deploy"  # 公司测试数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪对象的修改并发送信号
    SQLALCHEMY_ECHO = True  # 记录所有发送给stderr的语句，有利于调试
    MAX_CONTENT_LENGTH = 1000 * 1024 * 1024  # 文件上传最大为1000M
    M_SIZE = 1024 * 1024  # 1M 的字节数
    ALLOWED_EXTENSIONS = set(["zip"])  # 上传文件允许的后缀名
    UPLOAD_FOLDER = 'server_folder'  # 文件上传的目录
    PROJ_CONFIG = "app.json"
    REMOTE_DIR = "/opt/test"  # 远程服务器上传文件夹
    # REDIS_HOST = "172.16.120.224"  # redis发布地址
    REDIS_HOST = "127.0.0.1"  # redis发布地址
    REDIS_CHANNEL = "test"  # redis发布通道
    PROJ = {
        "spzlapi": "/SPZLApi/appsettings.json",
        "spzlweb": "/SPZLWeb/assets/config/appsetting.json",
        "umscore": "/UMSCore/appsettings.json",
        "mssprism": " /MSSPrism/config.xml",
        "deploy": "",
        "dotnet": "",
        "nginx": "",
        "redis": ""
    }


config = {
    "baseConfig": BaseConfig,
}
