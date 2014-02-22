import redis

from chapstream import config

redis_conn = redis.Redis(host=config.REDIS_HOST,
                         port=config.REDIS_PORT)