import datetime
from . import user
from app.tools.return_tools import return_json, response_tem
from flask import request
from app.models.models import User

from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity)


@user.route("/login", methods=["POST"])
def login():
    """
    登录接口
    :param username
    :param password
    :return:
    """
    json_data = return_json(request)
    name = json_data.get("name", None)
    password = json_data.get("password", None)
    if name is None or password is None:
        code = -1
        msg = "name and password is required"
        return response_tem(code=code, msg=msg)
    search_param = {
        "is_delete": False,
        "name": name,
    }
    data = User.query.filter_by(**search_param).first()
    if not data:
        code = -1
        msg = "用户不存在"
    elif data.check_password_hash(password):
        code = 0
        msg = "登录成功"
        name = name
        expires = datetime.timedelta(days=30)
        access_token = create_access_token(name, expires_delta=expires)
        # access_token = create_access_token(identity=name)
        return response_tem(code=code, msg=msg, name=name, access_token=access_token)
    else:
        code = -1
        msg = "密码错误"
    return response_tem(code=code, msg=msg)

# @user.route('/protected', methods=['GET'])
# @jwt_required
# def protected():
#     # Access the identity of the current user with get_jwt_identity
#     current_user = Lget_jwt_identity()
#     return response_tem(code=1, current_user=current_user)
