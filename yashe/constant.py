# coding:utf-8

#图片验证码的redis有效期，单位秒
IMAGE_CODE_REDIS_EXPIRES= 180

#短信验证码的redis有效期
SMS_CODE_REDIS_EXPIRES=180

#发送短信验证码的间隔，单位：秒

SEND_SMS_CODE_INTERVAL=60

#登录错误尝试次数
LOGIN_ERROR_MAX_TIMES=5
#登录错误限制的时间，单位秒
LOGIN_ERROR_FORBID_TIME = 600

#七牛的域名
QINIU_URL_DOMAIN='http://pnz4ki84o.bkt.clouddn.com/'

#城区信息的缓存时间,单位 秒
AREA_INFO_REDIS_CACHE_EXPIRES=7200

#主页最多展示商品数量
HOME_INDEX_PAGE =5

#主页轮播图缓存时间 单位 秒
HOME_PAGE_DATA_REDIS_EXPIRES =7200

#房屋详情允许显示的最大评论数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS=30

#房屋详情的redis过期时间，单位秒
HOUSE_DETAIL_REDIS_EXPIRE_SECOND=7200

#房屋列表页面每一页数据容量
HOUSE_LSIT_PAGE_CAPACITY=2
#房屋列表页面缓存时间，单位秒
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES=7200

#支付宝网关地址
ALIPAY_URL_PREFIX='https://openapi.alipaydev.com/gateway.do?'