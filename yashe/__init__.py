#coding:utf-8
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_session import Session
from flask_wtf import CSRFProtect
import logging
from logging.handlers import RotatingFileHandler
from yashe.utils.comments import ReConverter
#创建数据库对象
db =SQLAlchemy()
redis_store=None
csrf =CSRFProtect()

#设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)
#创建日志记录器，指明日志保存的路径，每个日志文件的最大大小，保存日志文件个数上限
file_log_hander =RotatingFileHandler('logs/log',maxBytes=1024*1024*100,backupCount=10)
#创建日志记录的格式               日志等级   输入日志信息的文件名  行数  日志信息
formatter =logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
#为刚创建的日志记录器设置日志记录格式
file_log_hander.setFormatter(formatter)
#为全局的日志工具对象(flask,app使用的添加日志记录器
logging.getLogger().addHandler((file_log_hander))


# 工厂模式
def create_app(config_name):
    '''
    创建flask应用对象
    :param config_name: str 配置模式名字('develop','product')
    :return: app对象
    '''
    app = Flask(__name__)

    config_class =config_map.get(config_name)
    app.config.from_object(config_class)

    #使用app初始化db
    db.init_app(app)

    # 创建redis对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,db=10)
    # 利用flask-session，将session数据保存到redis中
    Session(app)
    # 为flask补充csrf防护
    CSRFProtect(app)
    #为flask添加自定义的转化器
    app.url_map.converters['re']=ReConverter

    #注册蓝图
    from yashe import api_1_0
    app.register_blueprint(api_1_0.api,url_prefix='/api/v1.0')
    #注册提供静态文件的蓝图
    from yashe import web_html
    app.register_blueprint(web_html.html)

    return app


