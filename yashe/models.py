#coding:utf-8
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from yashe import constant
from . import db
class BaseModel(object):
    '''模型基类，为每个模型补充创建时间于更新时间'''
    create_time =db.Column(db.DateTime,default=datetime.now)
    update_time =db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)

class User(BaseModel,db.Model):
    '''用户'''
    __tablename__='ys_user_profile'
    id =db.Column(db.Integer,primary_key=True) #用户id
    name=db.Column(db.String(32),unique=True,nullable=False) #用户昵称
    password =db.Column(db.String(128),nullable=False) #密码
    mobile =db.Column(db.String(11),unique=True,nullable=False) #手机号
    real_name =db.Column(db.String(32)) #真实姓名
    id_card=db.Column(db.String(20)) #身份证号码
    avatar_url = db.Column(db.String(128)) #用户头像
    houses =db.relationship('House',backref='user') #用户发布的房屋
    orders =db.relationship('Order',backref ='user') #用户下的订单

    #加上property装饰器后，会把函数变为属性，属性名即为函数名
    @property
    def password_hash(self):
        '''读取属性的函数行为'''
        # return 'xxxx'
        raise AttributeError('这个属性只可能设置')
    #使用这个装饰器，对应设置属性操作
    @password_hash.setter
    def password_hash(self,value):
        '''
        设置属性
        :param value: 加密前密码
        :return:
        '''
        self.password = generate_password_hash(value)

    # def generate_password_hash(self,origin_password):
    #     '''对密码进行加密'''
    #     self.password=generate_password_hash(origin_password)

    def check_password(self,passwd):
        '''
        检验密码的正确性
        :param passwd:用户登录时填写的原始密码
        :return: T/F
        '''
        return check_password_hash(self.password,passwd)

class Area(BaseModel,db.Model):
    '''城区'''
    __tablename__='ys_area_info'
    id = db.Column(db.Integer, primary_key=True) #区域编号
    name =db.Column(db.String(32),nullable=False) #区域名字
    houses=db.relationship('House',backref='area')

    def to_dict(self):
        '''对象转换为字典'''
        d = {
            'aid': self.id,
            'aname': self.name
        }
        return d

#建立房屋和设施的多对多关系
house_facility=db.Table('ys_house_facility',
                        db.Column('house_id',db.Integer,db.ForeignKey('ys_hosue_info.id'),primary_key=True), #房屋编号
                        db.Column('facility_id',db.Integer,db.ForeignKey('ys_facility_info.id'),primary_key=True)) #设施编号


class House(BaseModel,db.Model):
    '''房屋信息'''
    __tablename__ ='ys_hosue_info'
    id = db.Column(db.Integer, primary_key=True) #房屋编号
    user_id =db.Column(db.Integer,db.ForeignKey('ys_user_profile.id'),nullable=False) #房屋主人的用户编号
    area_id=db.Column(db.Integer,db.ForeignKey('ys_area_info.id'),nullable=False) #归属地区编号
    title =db.Column(db.String(64),nullable=False) #标题
    price =db.Column(db.Integer,default=0) #单价，
    address =db.Column(db.String(512),default='') #地址
    room_count = db.Column(db.Integer,default=1) #房间数目
    acreage =db.Column(db.Integer,default=0)  #房屋面积
    unit =db.Column(db.String(32),default='') #房屋单元，几室几厅
    capacity =db.Column(db.Integer,default=1) #房屋容纳人数
    beds =db.Column(db.String(64),default='') #房屋床铺配置
    deposit =db.Column(db.Integer,default=0) #房屋押金
    min_days =db.Column(db.Integer,default=1) #最少入住天数
    max_days =db.Column(db.Integer,default=1) #最多入住天数
    order_count =db.Column(db.Integer,default=0) #预定完成该房屋的订单数
    index_image_url =db.Column(db.String(256),default='') #房屋主图片的路径
    facilities =db.relationship('Facility',secondary=house_facility) #房屋的设施
    images =db.relationship('HouseImage') #房屋的图片
    orders =db.relationship('Order',backref='house') #房屋的订单

    def to_myhouse_info(self):
        data = {
            'house_id': self.id,
            'title': self.title,
            'area_name': self.area.name,
            "room_count": self.room_count,
            "order_count": self.order_count,
            "address": self.address,
            "user_avatar": constant.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            'price': self.price,
            'img_url': constant.QINIU_URL_DOMAIN + self.index_image_url if self.index_image_url else '',
            'ctime':self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return  data

    def to_house_detail(self):
        data={
            "hid": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": constant.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "acreage": self.acreage,
            "unit": self.unit,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days,
        }
        img_urls =[]
        for img in self.images:
            img_urls.append(constant.QINIU_URL_DOMAIN + img.url)
        data['img_urls']=img_urls
        facilities=[]
        for facility in self.facilities:
            facilities.append(facility.id)
        data['facilities']=facilities
        comments =[]
        orders =Order.query.filter(Order.house_id==self.id,Order.status =="COMPLETE",Order.comment != None)\
            .order_by(Order.update_time.desc()).limit(constant.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        for order in orders:
            comment={
                'comment':order.comment, #评论内容
                'user_name':order.user.name if order.user.name !=order.user.mobile else u'匿名用户',
                'ctime':order.update_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            comments.append(comment)
        data['comments']=comments
        return data



class Facility(BaseModel,db.Model):
    '''设施信息'''
    __tablename__='ys_facility_info'
    id = db.Column(db.Integer, primary_key=True)  # 设施编号
    name = db.Column(db.String(32), nullable=False)  # 设施名字

class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "ys_hosue_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("ys_hosue_info.id"), nullable=False)  # 房屋编号
    url = db.Column(db.String(256), nullable=False)  # 图片的路径

class Order(BaseModel,db.Model):
    '''订单'''
    __tablename__='ys_order_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer,db.ForeignKey('ys_user_profile.id'),nullable=False) #下单用户id
    house_id =db.Column(db.Integer,db.ForeignKey('ys_hosue_info.id'),nullable=False) #预定的房间编号
    begin_date =db.Column(db.DateTime,nullable=False) #预定的起始时间
    end_date=db.Column(db.DateTime,nullable=False) #预定的结束时间
    days =db.Column(db.Integer,nullable=False) #预定的总天数
    house_price =db.Column(db.Integer,nullable=False) #房屋的单价
    amount =db.Column(db.Integer,nullable=False) #订单的总金额
    status =db.Column(db.Enum('WAIT_ACCEPT', #带接单
                              'WAIT_PAYMENT', #待支付
                              'PAID',#已支付
                              'WAIT_COMMENT', #待评价
                              'COMPLETE', #已完成
                              'CANCELED',#已取消
                              'REJECTED'#已拒单
                              ),default='WAIT_ACCEPT',index=True)
    comment =db.Column(db.Text)
    trade_no=db.Column(db.String(80))  #交易流水号

    def to_dict(self):
        """将订单信息转换为字典数据"""
        order_dict = {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": constant.QINIU_URL_DOMAIN + self.house.index_image_url if self.house.index_image_url else "",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }
        return order_dict
