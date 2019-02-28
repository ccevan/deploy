import zipfile
import os
from app.tools.return_tools import localtime


def un_zip(file_name):
    """
    :param file_name: zip文件绝对路径
    :return:
    """
    zip_file = zipfile.ZipFile(file_name)
    dirname = os.path.dirname(file_name)  # zip文件上层目录
    name = os.path.basename(file_name)[:-4]  # zip文件不带后缀的文件名

    if os.path.isdir(os.path.join(dirname, name)):
        str_time = localtime()
        os.rename(os.path.join(dirname, name), os.path.join(dirname, name + str_time))

    for names in zip_file.namelist():
        zip_file.extract(names, dirname)
    zip_file.close()
