#coding:utf-8
import re

from flask import current_app
from flask import g
from flask import request, jsonify
from flask import session

from yashe import constant
from yashe import redis_store,db
from yashe.models import User
from yashe.utils.comments import login_required
from yashe.utils.response_code import RET
from . import api
from sqlalchemy.exc import IntegrityError
@api.route('/users',methods=['POST'])
def register():
    '''
    注册逻辑,请求参数，手机号，短信验证码,密码
    参数格式:json
    :return:
    '''
    #获取请求的json数据，返回字典
    req_dict=request.get_json()
    mobile =req_dict.get('mobile')
    sms_code =req_dict.get('sms_code')
    password =req_dict.get('password')
    password2 = req_dict.get('password2')
    #校验参数
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')

    #判断手机号格式
    if not re.match(r'1[34578]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')

    #从redis中取出短信验证码，判断短信验证码是否过期,对比验证码正确性
    try:
        real_sms_code =redis_store.get('sms_code_%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(RET.DBERR,errmsg='去读redis短信验证码异常')
    #删除redis中的短信验证码，防止重复使用校验
    try:
        redis_store.delete('sms_code_%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)


    if real_sms_code is None:
        return jsonify(errno=RET.NODATA,errmsg='短信验证码失效')
    #判断手机号是否注册过
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg ='数据库异常')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')
    #保存数据
    user =User(name =mobile,mobile=mobile)
    user.password_hash=password #设置密码
    try:
        db.session.add(user)
        db.session.commit()
    #保存登录状态
    except IntegrityError as e:
        #表示手机号出现重复值,即手机号已注册过
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已存在')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')
    #保存登录状态到session中
    session['name']=mobile
    session['mobile']=mobile
    session['user_id']=user.id
    return jsonify(errno=RET.OK, errmsg='注册成功')

@api.route('/sessions',methods=['POST'])
def login():
    '''
    用户登录
    手机号，密码
    :return:
    '''
    #手机号格式，错误次数限制
    req_dict=request.get_json()
    mobile =req_dict.get('mobile')
    password =req_dict.get('password')
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    if not re.match(r'1[34578]\d{9}',mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')

    #错误次数限制ip，redis记录 ’access_nums_请求id地址‘：次数
    ip =request.remote_addr
    try:
        access_nums = redis_store.get('access_nums_%s'%ip)

    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >=constant.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg='错误次数过多，请稍后重试')

    #从数据库中根据手机号查询用户的数据对象
    try:
        user =User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')

    if user is None or  not user.check_password(password):
        #验证失败，记录错误次数
        try:
            redis_store.incr('access_nums_%s'%ip)
            redis_store.expire('access_nums_%s'%ip,constant.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')

    #验证成功，保存登录状态
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/session',methods=['GET'])
def check_login():
    name =session.get('name')
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='True',data={'name':name})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg='false')


#登出
@api.route('/session',methods=['DELETE'])
def lougout():
    csrf_token=session.get('csrf_token')
    session.clear()
    session['csrf_token']=csrf_token
    return jsonify(errno=RET.OK, errmsg='OK')

@api.route('/user/info',methods=['GET'])
@login_required
def get_userinfo():
    username =session.get('name')
    mobile =session.get('mobile')
    return jsonify(errno=RET.OK, errmsg='OK',data={'username':username,'mobile':mobile})


#获取用户的真实姓名
@api.route('/user/auth',methods=['GET'])
@login_required
def get_userauth():

    user_id =g.user_id
    try:
        real_name =User.query.filter_by(id=user_id).first().real_name
        id_card =User.query.filter_by(id=user_id).first().id_card
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询信息异常')
    return jsonify(errno=RET.OK, errmsg='OK',data={'real_name':real_name,'id_card':id_card})


# 设置用户的真实姓名
@api.route('/user/auth', methods=['POST'])
@login_required
def set_userauth():
    user_id = g.user_id
    #获取参数
    resp_dict=request.get_json()
    print ('resp_dict',resp_dict)
    real_name=resp_dict.get('real_name')
    id_card=resp_dict.get('id_card')
    #校验参数
    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')
    try:
        User.query.filter_by(id=user_id).update({'real_name':real_name,'id_card':id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='修改信息异常')
    return jsonify(errno=RET.OK, errmsg='OK', data={'real_name': real_name, 'id_card': id_card})