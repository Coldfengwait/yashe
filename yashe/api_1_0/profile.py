# coding:utf-8
from flask import session

from yashe import constant, redis_store
from yashe import db
from yashe.models import User
from yashe.utils.image_storage import storage
from . import api
from yashe.utils.comments import login_required
from flask import g,current_app,request,jsonify
from yashe.utils.response_code import RET


@api.route('/user/avatar',methods=['POST'])
@login_required
def set_user_avatar():
    '''
    设置用户的头像，参数：图片（多媒体表单），用户id(g.user_id)
    :return:
    '''
    #在login_required装饰器中已经把user_id保存到g对象中
    user_id=g.user_id
    #获取图片
    image_file =request.files.get('avatar')
    if image_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg='未上传图片')

    image_data =image_file.read()
    try:
        file_name =storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='上传图片失败')

    #保存文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({'avatar_url':file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片失败')
    #保存返回
    avatar_url=constant.QINIU_URL_DOMAIN+file_name
    return jsonify(errno=RET.OK,errmsg='保存成功',data={'avatar_url':avatar_url})

#获取用户头像
@api.route('/user/avatar',methods=['GET'])
@login_required
def get_user_avatar():
    user_id = g.user_id
    # 获取图片
    try:
        image_file = User.query.filter_by(id=user_id).first().avatar_url
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户头像失败')

    image_url = constant.QINIU_URL_DOMAIN+image_file
    print ('image_url',image_url)
    return jsonify(errno=RET.OK,errmsg='查询成功',data={'image_url':image_url})
#获取用户姓名
@api.route('/user/name',methods=['GET'])
@login_required
def get_name():

    username=session.get('name')
    return jsonify(errno=RET.OK, errmsg='True',data={'username':username})

#修改用户名
@api.route('/user/name',methods=['POST'])
@login_required
def set_name():
    #获取前端传来的参数
    req_dict = request.get_json()
    username = req_dict.get('user_name')
    print ('username',username)
    if not username:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 在login_required装饰器中已经把user_id保存到g对象中
    user_id =g.user_id
    try:
        User.query.filter_by(id=user_id).update({'name':username})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='修改用户名失败')
    session['name']=username
    return jsonify(errno=RET.OK, errmsg='True',data={'username':username})