import demjson
from loggings import logger
from xml.etree.ElementTree import Element, SubElement, ElementTree


def spzlapi_config(path, database_ip, database_password, application_ip, stream_ip):
    """
    修改视频智联api服务的配置文件
    :param path: 配置文件绝对路径
    :param database_ip: 数据库ip
    :param database_password: 数据库密码
    :param application_ip: 应用服务器ip
    :param stream_ip: 流媒体服务器ip
    :return:
    """
    try:
        with open(path, 'r') as f_read:
            json_data = demjson.decode(f_read.read())

            DefaultConn = json_data["ConnectionStrings"]["DefaultConnection"]
            if DefaultConn:
                DefaultConn = "Server="+ database_ip + ";Database=VideoManagement;UID=sa;PWD=" + database_password
                json_data["ConnectionStrings"]["DefaultConnection"] = DefaultConn  # 修改后的DefaultConnection
            else:
                return False

            UmsConn = json_data["UmsConnection"]
            if UmsConn:
                UmsConn = "Server=" + database_ip + ";Database=UmsCore-SPZL;UID=sa;PWD=" + database_password
                json_data["UmsConnection"] = UmsConn  # 修改后的UmsConnection
            else:
                return False

            RunPath = json_data["RunPath"]
            if RunPath:
                RunPath = "http://" + application_ip + ":8088"
                json_data["RunPath"] = RunPath
            else:
                return False
            StreamUrl = json_data["StreamUrl"]
            if StreamUrl:
                StreamUrl = "http://" + stream_ip + ":8080"
                json_data["StreamUrl"] = StreamUrl
            else:
                return False
            PVGAddress = json_data["PVGAddress"]
            if PVGAddress:
                PVGAddress = "http://" + database_ip +":503"
                json_data["PVGAddress"] = PVGAddress
            else:
                return False
            redislinkAddress = json_data["redislinkAddress"]
            if redislinkAddress:
                redislinkAddress = application_ip + ":6379"
                json_data["redislinkAddress"] = redislinkAddress
            with open(path, "w") as f_write:
                f_write.write(demjson.encode(json_data))
        return True
    except Exception as e:
        logger.error(e)
        return False



def spzlweb_config(path, application_ip, stream_ip):
    """

    :param path: 配置文件路径
    :param application_ip: 应用服务器IP，字符串格式
    :param stream_ip: 流媒体服务器IP，字符串格式
    :return: 成功返回True
             失败返回False
    """
    try:
        with open(path, "rb+") as f:
            json_info = demjson.decode(f.read(), encoding="utf-8")

            server_url = "http://" + application_ip + ":8088"
            json_info["serviceUrl"] = server_url

            ums_url = "http://" + application_ip + ":5556"
            json_info["umsUrl"] = ums_url

            stream_url = "http://" + stream_ip + ":8080"
            json_info["streamUrl"] = stream_url

            web_site_address = "http://" + application_ip + ":8087"
            json_info["webSiteAddress"] = web_site_address

            json_str = demjson.encode(json_info)  # .replace(",", ",\n").replace("{", "\n{\n").replace("}", "\n}\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)
        return True
    except BaseException as e:
        logger.error(e)
        return False


def ums_config(path, database_ip, database_password, application_ip):
    """

    :param path: 配置文件路径
    :param database_ip: 数据库ip，字符串格式
    :param database_passwd: 数据库密码，字符串格式
    :param application_ip: 应用服务器IP，字符串格式
    :return: 成功返回True
             失败返回False
    """
    try:
        with open(path, "rb+") as f:
            # 解析json
            json_info = demjson.decode(f.read(), encoding="utf-8")

            # 替换需要替换的部分
            server = "Server=" + database_ip + ";Database=UMSCore-SPZL;UID=sa;PWD=" + database_password
            json_info["ConnectionStrings"]["DefaultConnection"] = server
            deploy_url = "http://" + application_ip + ":5556"
            json_info["appSettings"]["DeployUrl"] = deploy_url

            # 转为json字符串形式
            json_str = demjson.encode(json_info)  # .replace(",", ",\n").replace("{", "\n{\n").replace("}", "\n}\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json_str)
        return True
    except BaseException as e:
        logger.error(e)
        return False


def mssprism_config(path, stream_ip, rtmp_ip, application_ip):
    """
    修改mssprism服务的配置文件
    :param path: 配置文件路径
    :param stream_ip: 流媒体服务器ip
    :param rtmp_ip: rtmp服务器ip
    :param application_ip: 应用服务器ip
    :return: 修改成功 True  修改失败False
    """
    try:
        et = ElementTree()
        root = et.parse(path)
        for config in root.iter('config'):
            for sink in config.iter('sink'):
                for sip in sink.iter("sip"):
                    for serverIp in sip.iter("serverIp"):
                        serverIp.text = stream_ip
                for rtmp in sink.iter("rtmp"):
                    for serverIp in rtmp.iter("serverIp"):
                        serverIp.text = rtmp_ip
                for m3u8 in sink.iter("m3u8"):
                    for serverIp in m3u8.iter("serverIp"):
                        serverIp.text = stream_ip
            for server in config.iter("server"):
                for rtsp in server.iter("rtsp"):
                    for listenerIp in rtsp.iter("listenerIp"):
                        listenerIp.text = stream_ip
                for GB28181 in server.iter("GB28181"):
                    for listenerIp in GB28181.iter("listenerIp"):
                        listenerIp.text = stream_ip
                for webserver in server.iter("webserver"):
                    for ip in webserver.iter("ip"):
                        ip.text = application_ip
                for redis in server.iter("redis"):
                    for ip in redis.iter("ip"):
                        ip.text = application_ip
        et.write(path)
        return True
    except Exception as e:
        logger.error(e)
        return False


if __name__ == "__main__":
    # path = "/home/ingin/Desktop/Soyuan.SysDeployService/app/server_folder/appsettings.json"
    # path = "/home/ingin/Desktop/Soyuan.SysDeployService/app/server_folder/config.xml"
    path = "/home/ingin/Desktop/Soyuan.SysDeployService/app/server_folder/appsettings.json"
    path_ums = "/home/ingin/Desktop/Soyuan.SysDeployService/app/server_folder/appsettings.json"
    database_ip = application_ip = stream_ip = rtmp_ip = "172.16.1.201"
    database_password = "hello"
    # result = spzlapi_config(path,database_ip,database_password,application_ip,stream_ip)
    # result = mssprism_config(path, stream_ip, rtmp_ip, application_ip)
    result = ums_config(path_ums, database_ip, database_password, application_ip)
    print(result)
