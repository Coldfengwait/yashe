#coding:utf-8
from celery import Celery
from yashe.tasks import config
#定义celery对象
celery_app=Celery('yashe')

#引入配置信息
celery_app.config_from_object(config)
#自动搜寻任务
celery_app.autodiscover_tasks(['yashe.tasks.sms'])


