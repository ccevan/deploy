import json
import time
import os


def return_json(request):
    json_str = str(request.get_data(), encoding="utf-8")
    json_data = json.loads(json_str)
    return json_data


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


def localtime():
    """
    生成当前时间戳 年月日时分秒
    :return: 精确到秒的字符串
    """
    str_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    return str_time


def get_file_name(path):
    """
    获取文件的名称
    :param path: 文件的绝对路径
    :return: 上层文件夹目录路径, 不带后缀文件名, 文件后缀名
    """
    if os.path.abspath(path):
        dirname = os.path.dirname(path)  # 上层文件夹名称
        name = os.path.basename(path).split('.')[0]  # 不带后缀的文件名称
        suffix = os.path.basename(path).split('.')[-1]  # 文件名后缀
    else:
        dirname = 0
        name = 0
        suffix = 0
    return dirname, name, suffix
