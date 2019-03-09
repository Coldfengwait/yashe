# coding:utf-8
import datetime
from flask import current_app
from flask import g
from flask import json
from flask import request, jsonify
from flask import session

from yashe import constant
from yashe import redis_store,db
from yashe.api_1_0 import api
from yashe.models import User, Area,House, Facility, HouseImage, Order
from yashe.utils.comments import login_required
from yashe.utils.image_storage import storage
from yashe.utils.response_code import RET
from yashe import redis_store


@api.route('/areas')
def get_area_info():
    '''获取城区信息'''
    #查询数据库，读取城区信息
    #尝试从redis中读取数据
    try:
        resp_json =redis_store.get('area_info')
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            #有缓存数据

            return resp_json, 200, {'Content-Type': 'application/json'}
    try:
        area_li=Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库异常')
    area_dict_li=[]
    #将对象的属性转换成字典值，存储在列表中
    for area in area_li:
        area_dict_li.append(area.to_dict())

    #将数据转换为json字符串
    resp_dict =dict(errno=RET.OK,errmsg='OK',data=area_dict_li)
    resp_json=json.dumps(resp_dict)
    #将数据保存到redis中

    try:
        redis_store.setex('area_info',constant.AREA_INFO_REDIS_CACHE_EXPIRES,resp_json)
    except Exception as e:
        current_app.logger.error(e)
    return '{"errno":0, "errmsg":"OK", "data":%s}' % resp_json, 200, {"Content-Type": "application/json"}

@api.route('/houses/info',methods=['POST'])
@login_required
def set_house_info():
    '''保存房屋的基本信息qi前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    '''
    #获取数据
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数

    #检验参数
    if not all([title, price, area_id, address, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    try:
        price = int(float(price)*100)
        deposit=int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg ='参数错误')

    #判断地区id是否存在
    try:
        area=Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库异常')
    if area == None:
        return jsonify(errno=RET.NODATA, errmsg='城区信息有误')

    #保存房屋信息
    house =House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    #处理房屋的设施信息
    facilitiy_ids =house_data.get('facility')
    if facilitiy_ids:
        try:
            facilities=Facility.query.filter(Facility.id.in_(facilitiy_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg='数据库异常')

        if facilities:
            #表示有合法的设施数据,进行保存
            house.facilities=facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')

    return jsonify(errno=RET.OK,errmsg='OK',data={'house_id':house.id})



@api.route('/houses/image',methods=['POST'])
@login_required
def save_house_image():
    '''
    保存图片房屋的图片
    参数：图片，房屋id
    :return:
    '''
    image_file =request.files.get('house_image')
    house_id =request.form.get('house_id')

    if not all([image_file,house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    #判断house_Id的正确性
    try:
        house=House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")
    #保存图片到七牛中
    image_data =image_file.read()
    try:
        file_name=storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存图片异常")
    #保存图片信息到数据库
    house_image=HouseImage(house_id=house_id,url=file_name)
    db.session.add(house_image)
    #处理房屋的主图片
    if not house.index_image_url:
        house.index_image_url=file_name
        db.session.add(house)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存图片数据异常')

    image_url=constant.QINIU_URL_DOMAIN+file_name
    return jsonify(errno=RET.OK, errmsg='OK', data={'image_url': image_url})

#验证实名认证
@api.route('/house/auth',methods=['GET'])
def get_house_auth():
    #获取session中的用户id
    user_id=session.get('user_id')
    #查询数据库
    try:
        user =User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')

    if  not user:
        return jsonify(errno=RET.PARAMERR,errmsg='没有该用户')

    if user.real_name and user.id_card:
        return jsonify(errno=RET.OK,errmsg='ok')
    else:
        return jsonify(errno=RET.PARAMERR, errmsg='没有实名认证')

#查询用户的房源
@api.route('/house/info',methods=['GET'])
@login_required
def get_house_info():
    user_id =g.user_id
    try:
        user=User.query.get(user_id)
        houses=user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')

    #将查询到的房屋信息转换为字典存放到列表中
    houses_list=[]
    if houses:
        for house in houses:
            houses_list.append(house.to_myhouse_info())
    return jsonify(errno=RET.OK, errmsg='OK', data={'houses':houses_list})

#查询用户的轮播图信息
@api.route('/houses/index',methods=['GET'])
def get_house_index():
    try:
        ret=redis_store.get('home_page_data')
    except Exception as e:
        current_app.logger.error(e)
        ret=None
    if ret:
        return '{"errno":0, "errmsg":"OK", "data":%s}' % ret, 200, {"Content-Type": "application/json"}

    try:
        houses=House.query.order_by(House.order_count.desc()).limit(constant.HOME_INDEX_PAGE)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')
    if not houses:
        return jsonify(errno=RET.NODATA,errmsg='查询无数据')
    #若房屋没有主图，则不展示该图片
    houses_list=[]
    for house in houses:
        if not house.index_image_url:
            continue
        houses_list.append(house.to_myhouse_info())
    json_houses =json.dumps(houses_list)
    try:
        redis_store.setex('home_page_data',constant.HOME_PAGE_DATA_REDIS_EXPIRES,json_houses)
    except Exception as e:
        current_app.logger.error(e)
    return '{"errno":0, "errmsg":"OK", "data":%s}' % json_houses, 200, {"Content-Type": "application/json"}

@api.route('/houses/<int:house_id>',methods=['GET'])
def get_house_detail(house_id):
    '''获取房屋详情'''
    user_id =session.get('user_id')

    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
    # 尝试从redis中读取数据
    try:
        ret =redis_store.get('house_inf_%s'%house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret =None
    if ret:
        return '{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}'%(user_id,ret),200,{'Content-Type':'application/json'}

    try:
        house=House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')
    if not house:
        return jsonify(errno=RET.NODATA,errmsg='房屋不存在')
    try:
        house_data =house.to_house_detail()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据出错')
    #存入到redis中
    json_house=json.dumps(house_data)
    try:
        redis_store.setex('house_info_%s'%house_id,constant.HOUSE_DETAIL_REDIS_EXPIRE_SECOND,json_house)
    except Exception as e:
        current_app.logger.error(e)

    resp ='{"errno":"0", "errmsg":"OK", "data":{"user_id":%s, "house":%s}}'%(user_id,json_house),200,{'Content-Type':'application/json'}

    return resp

# GET /api/v1.0/houses?sd=2018-01-12&ed=2018-01-15&aid=10&sk=new&p=1
@api.route('/houses')
def get_house_list():
    '''获取房屋的搜索页面'''
    start_date=request.args.get('sd','') #入住起始时间
    end_date=request.args.get('ed','') #入住结束时间
    area_id =request.args.get('aid','') #区域编号
    sort_key=request.args.get('sk','new') #排序关键字
    page =request.args.get('p') #页数

    #处理时间
    try:
        if start_date:
            start_date=datetime.datetime.strptime(start_date,'%Y-%m-%d')
        if end_date:
            end_date =datetime.datetime.strptime(start_date,'%Y-%m-%d')
        if start_date and end_date:
            assert start_date<=end_date
    except Exception as e:
         current_app.logger.error(e)
         return jsonify(errno=RET.PARAMERR,errmsg='日期参数有误')
    #判断区域id
    if area_id:
        try:
            area =Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR,errmsg='区域参数有误')
    #处理页数
    try:
        page=int(page)
    except Exception as e:
        current_app.logger.error(e)
        page =1
    #尝试从缓存中获取
    redis_key='house_%s_%s_%s_%s' % (start_date, end_date, area_id, sort_key)
    try:
        resp_json=redis_store.hget(redis_key,page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json,200,{'Content-Type':'application/json'}
    # 构建过滤条件的参数列表容器
    filter_params = []
    #填充过滤参数
    conflict_corders=None
    #查看时间条件
    try:
        if start_date and end_date:
            #查询冲突的订单
            conflict_corders =Order.query.filter(Order.begin_date<=end_date,Order.end_date>=start_date).all()
        elif start_date:
            # 查询冲突的订单
            conflict_corders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_corders =Order.query.filter(Order.begin_date<=end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='数据库异常')
    if conflict_corders:
        # 从订单中获取冲突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_corders]
        #如果冲突的房屋id不为空，向查询参数中添加条件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))
    # 查看区域条件
    if area_id:
        filter_params.append(House.area_id ==area_id)

    #查询数据库
    #补充排序条件

    if sort_key == 'booking':
        house_query=House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        house_query=House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == 'price-desc':
        house_query=House.query.filter(*filter_params).order_by(House.price.desc())
    else: #默认按新旧
        house_query=House.query.filter(*filter_params).order_by(House.create_time.desc())
    try:
        #处理分页,参数为：当前页数， 每页数据数， 自动错误输出
        page_obj=house_query.paginate(page=page,per_page=constant.HOUSE_LSIT_PAGE_CAPACITY,error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    #获取页面数据
    house_li = page_obj.items
    houses=[]
    for house in house_li:
        houses.append(house.to_myhouse_info())
    #获取总页面数
    total_page =page_obj.pages

    resp_dict= dict(errno=RET.OK,errmsg='OK',data={'total_page':total_page,'houses':houses,'current_page':page})
    resp_json=json.dumps(resp_dict)
    #当前页数小于总页数时进行缓存
    if page <= total_page:
        #设置缓存数据
        redis_key='house_%s_%s_%s_%s'%(start_date,end_date,area_id,sort_key)
        #哈希类型
        try:
            # redis_store.hset(redis_key,page,resp_json)
            # redis_store.expire(redis_key,constant.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
            #创建redis管道对象，可以一次执行多个语句
            pipeline=redis_store.pipeline()
            #开启多个语句的记录
            pipeline.multi()
            pipeline.hset(redis_key,page,resp_json)
            pipeline.expire(redis_key,constant.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
            #执行语句
            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)

    return resp_json,200,{'Content-Type':'application/json'}


