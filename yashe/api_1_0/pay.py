#coding:utf-8
from flask import current_app, jsonify
from flask import g
from flask import request

from yashe import constant, db
from yashe.models import Order
from yashe.utils.comments import login_required
from yashe.utils.response_code import RET
from  . import api
from alipay import  AliPay
import os
#发起支付宝支付
@api.route('/orders/<int:order_id>/payment',methods=['POST'])
@login_required
def order_pay(order_id):
    user_id =g.user_id
    #查询订单,判断订单状态
    try:
        order=Order.query.filter(Order.id==order_id,Order.status=='WAIT_PAYMENT',Order.user_id==user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库异常')
    if order is None:
        return jsonify(errno=RET.NODATA,errmsg='订单数据有误')

    #创建支付宝sdk的工具对象
    alipay=AliPay(
        appid="2016092800615894",
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(__file__),'keys/app_private_key.pem'), #私钥
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=os.path.join(os.path.dirname(__file__),'keys/alpay_public_key.pem'),
        sign_type="RSA2", # RSA 或者 RSA2
        debug = True  # 默认False
    )
    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order.id, #订单编号
        total_amount=str(order.amount/100.0),
        subject=u'哑舍租房%s'%order_id, #订单标题
        return_url="http://192.168.9.128:5000/payComplate.html", #返回连接地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    #构建让用户跳转的支付宝链接地址
    pay_url=constant.ALIPAY_URL_PREFIX+order_string

    return jsonify(errno=RET.OK,errmsg='OK',data ={'pay_url':pay_url})

#保存订单支付结果
@api.route('/orders/payment',methods=['PUT'])
def save_order_payment_result():

    alipay_dict=request.form.to_dict()
    #对支付宝的数据进行分离，提取出支付宝的签名参数,sign和剩下的其他数据
    alipay_sign=alipay_dict.pop('sign')
    # 创建支付宝sdk的工具对象
    alipay = AliPay(
        appid="2016092800615894",
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(__file__), 'keys/app_private_key.pem'),  # 私钥
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=os.path.join(os.path.dirname(__file__), 'keys/alpay_public_key.pem'),
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )
    #借助工具验证参数的合法性.update
    #验证是否是支付宝的参数
    result=alipay.verify(alipay_dict,alipay_sign)

    if result:
        #修改数据库的订单状态信息
        order_id = alipay_dict.get('out_trade_no')
        trade_no =alipay_dict.get('trade_no')  #支付宝的交易流水号
        try:
            Order.query.filter_by(id=order_id).update({'status':'WAIT_COMMENT','trade_no':trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    return jsonify(errno=RET.OK,errmsg='OK')

