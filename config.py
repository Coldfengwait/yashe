#coding:utf-8
import redis


class Config(object):
    SECRET_KEY='328HIHKJN&SDFNJN@'
    SQLALCHEMY_DATABASE_URI= 'mysql://root:mysql@192.168.9.128:3306/yashe'
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    REDIS_HOST='192.168.9.128'
    REDIS_PORT=6379
    SESSION_TYPE='redis'
    SESSION_REDIS=redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER=True  #对session的id进行加密
    PERMANENT_SESSION_LIFETIME= 86400 #session有效期

class DevelopmentConfig(Config):
    DEBUG =True

class ProductConfig(Config):
    pass

config_map={
    'develop':DevelopmentConfig,
    'product':ProductConfig
}