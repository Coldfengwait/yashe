#coding:utf-8
from celery import Celery
from yashe.libs.yuntongxun.SendTemplateSMS import CCP
#定义celery对象
celery_app=Celery('yashe',broker='redis://192.168.9.128:6379/1')


@celery_app.task
def send_sms(to,datas,temp_id):
    '''发送短信的异步任务'''
    ccp=CCP()
    ccp.sendTemplateSMS(to,datas,temp_id)

