#coding:utf-8
from yashe.libs.yuntongxun.SendTemplateSMS import CCP
from yashe.tasks.main import celery_app

@celery_app.task
def send_sms(to,datas,temp_id):
    '''发送短信的异步任务'''
    ccp=CCP()
    ret=ccp.sendTemplateSMS(to,datas,temp_id)
    return ret

