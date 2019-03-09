#coding:utf-8
import random

from flask import request

from yashe.libs.yuntongxun.SendTemplateSMS import CCP
from yashe.tasks.sms.tasks import send_sms
from . import api

from yashe.utils.captcha.captcha import captcha
from yashe import redis_store,constant,db
from flask import current_app,jsonify,make_response
from yashe.utils.response_code import RET
from yashe.models import User

#get ip/api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    '''
    获取图片验证码
    :param image_code_id:图片验证码
    :return: 验证码图片/异常：json
    '''
    #获取参数
    #校验参数
    #处理业务逻辑
    #1.生成验证码图片
    #名字 ，真实文本，图片数据
    name,text,image_data =captcha.generate_captcha()
    #2.将验证码真实值与编号保存到redis中,设置有效期
    #redis：str  list hash set zset
    #单条维护记录，选用字符串

    #参数： 1. key  2. 有效期  3.value
    try:
        # redis_store.set('image_code_%s'%image_code_id,text)
        # redis_store.expire('image_code_%s'%image_code_id,constant.IMAGE_CODE_REDIS_EXPIRES)
        redis_store.setex('image_code_%s'%image_code_id,constant.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        #记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='save image code failed')
    #返回响应
    resp =make_response(image_data)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


# GET  /api/v1.0/sms_codes/<mobile>?image_code=xxxx%image_code_id=xxx
# @api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
# def get_sms_code(mobile):
#     '''获取短信验证码'''
#     #获取参数
#     image_code =request.args.get('image_code')
#     image_code_id =request.args.get('image_code_id')
#     #校验
#     if not all([image_code_id,image_code]):
#         #表示参数不完整
#         return jsonify(errno=RET.PARAMERR,errmsg ='参数不完整')
#     #业务逻辑处理
#     #从redis中取出真实图片验证码，进行对比
#     try:
#         print ('code:','image_code_%s'%image_code_id)
#         real_image_code=redis_store.get('image_code_%s'%image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR,errmsg='redis数据库异常')
#      #判断图片验证码是否过期
#     if real_image_code is None:
#         return jsonify(errno=RET.NODATA,errmsg='图片验证码失效')
#
#     #删除图片验证码，防止用户使用同一个图片验证码验证多次防止撞库等行为的攻击,
#     try:
#         redis_store.delete('image_code_%s'%image_code_id)
#     except Exception as e:
#         current_app.logger.error(e)
#     #与用户填写的信息进行对比
#     if real_image_code.lower() !=image_code.lower():
#         return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误')
#
#     #判断这个手机号是否在60s内发送给短信
#     try:
#         send_flag =redis_store.get('send_sms_code_%s'%mobile)
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if send_flag is not None:
#             return jsonify(errno=RET.REQERR,errmsg='请求过于频繁，请60s后再试')
#
#     #判断手机号是否存在
#     try:
#         user = User.query.filter_by(mobile=mobile).first()
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if user is not None:
#             return jsonify(errno=RET.DATAEXIST,errmsg='手机号已存在')
#
#     #生成短信验证码
#     sms_code ='%06d'% random.randint(0,999999)
#     #保存真实的短信验证码
#     try:
#         redis_store.setex('sms_code_%s'%mobile,constant.SMS_CODE_REDIS_EXPIRES,sms_code)
#         #保存发送给这个手机号的记录，防止用户在60s内再次发出短信的操作
#         redis_store.setex('send_sms_code_%s'%mobile,constant.SEND_SMS_CODE_INTERVAL,1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.DBERR,errmsg='保存短信验证码异常')
#
#     #发送短信
#     try:
#         ccp=CCP()
#         result =ccp.sendTemplateSMS(mobile,[sms_code,int(constant.SMS_CODE_REDIS_EXPIRES/60)],1)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(errno=RET.THIRDERR, errmsg='发送异常')
#     if result == 0:
#         #发送成功
#         return jsonify(errno=RET.OK,errmsg ='发送成功')
#     else:
#         return jsonify(errno=RET.THIRDERR,errmsg='发送失败')
#     #返回值



# GET  /api/v1.0/sms_codes/<mobile>?image_code=xxxx%image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def get_sms_code(mobile):
    '''获取短信验证码'''
    #获取参数
    image_code =request.args.get('image_code')
    image_code_id =request.args.get('image_code_id')
    #校验
    if not all([image_code_id,image_code]):
        #表示参数不完整
        return jsonify(errno=RET.PARAMERR,errmsg ='参数不完整')
    #业务逻辑处理
    #从redis中取出真实图片验证码，进行对比
    try:
        print ('code:','image_code_%s'%image_code_id)
        real_image_code=redis_store.get('image_code_%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='redis数据库异常')
     #判断图片验证码是否过期
    if real_image_code is None:
        return jsonify(errno=RET.NODATA,errmsg='图片验证码失效')

    #删除图片验证码，防止用户使用同一个图片验证码验证多次防止撞库等行为的攻击,
    try:
        redis_store.delete('image_code_%s'%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    #与用户填写的信息进行对比
    if real_image_code.lower() !=image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误')

    #判断这个手机号是否在60s内发送给短信
    try:
        send_flag =redis_store.get('send_sms_code_%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            return jsonify(errno=RET.REQERR,errmsg='请求过于频繁，请60s后再试')

    #判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST,errmsg='手机号已存在')

    #生成短信验证码
    sms_code ='%06d'% random.randint(0,999999)
    #保存真实的短信验证码
    try:
        redis_store.setex('sms_code_%s'%mobile,constant.SMS_CODE_REDIS_EXPIRES,sms_code)
        #保存发送给这个手机号的记录，防止用户在60s内再次发出短信的操作
        redis_store.setex('send_sms_code_%s'%mobile,constant.SEND_SMS_CODE_INTERVAL,1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存短信验证码异常')

    #发送短信
    #使用celery异步发送短信,delay函数调用后立即返回
    result=send_sms.delay(mobile,[sms_code,int(constant.SMS_CODE_REDIS_EXPIRES/60)],1)
    #返回异步执行结果对象
    # print (result.id)
    #通过get方法能获取异步执行的结果
    #get方法默认是阻塞的行为，会等到有执行结果之后才返回
    #get方法页接受参数timeout，超时时间，超过超时时间还拿不到结果则返回
    # ret =result.get()
    # print (ret)
    #发送成功
    return jsonify(errno=RET.OK,errmsg ='发送成功')



