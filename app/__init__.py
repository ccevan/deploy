import os
import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string
from config import config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()


def response_tem(code, data=None, msg=None, userdata=None, **kwargs):
    """
    :param code: 返回码
    :param data: 数据列表
    :param msg: 返回说明
    :param userdata: 用户数据
    :param kwargs:
    :return:
    """

    re_json = {
        "code": code,
        "data": data,
        "msg": msg,
        "userdata": userdata
    }
    if kwargs:
        for key in kwargs:
            re_json[key] = kwargs[key]

    return json.dumps(re_json, indent=4, default=str, sort_keys=True)


def create_app(config_name):
    app = Flask(__name__)
    config_mode = config[config_name]
    app.config.from_object(config_mode)
    db.init_app(app)
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def my_expired_token_callback():
        # token_type = expired_token['type']
        code = -2
        msg = "token 已经过期, 请重新登录"
        return response_tem(code=code, msg=msg)

    @jwt.invalid_token_loader
    def my_invalid_token_callback(e):
        # token_type = expired_token['type']
        code = -3
        msg = "token无效"
        return response_tem(code=code, msg=msg, e=e)

    filenames = os.listdir("app/resources")
    for filename in filenames:
        if os.path.isdir("app/resources/" + filename) and os.path.exists('app/resources/' + filename + '/__init__.py'):
            bp = import_string('app.resources.' + filename + ':' + filename)
            app.register_blueprint(bp)

    return app, db
