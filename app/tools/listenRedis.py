import redis
from loggings import logger


def publish_redis(host, channel, message, password=None):
    """
    push content to redis-server
    :param host: redis-server address
    :param channel: redis-server channel
    :param password: redis-server password
    :param message: what content you want to push, int or string/json
    :return: true is push successful,false is fail
    """
    returns = [True, False]
    try:
        if password:
            r = redis.Redis(host=host, password=password)
        else:
            r = redis.Redis(host=host)
        r.publish(channel, message=message)
        code = 0
    except Exception as e:
        logger.error(e)
        code = 1

    return returns[code]
