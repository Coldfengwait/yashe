# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_data, etag
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = '1c8TTNpPTZgDXKLPuWtX-uNI9afiYazOC0UoopZH'
secret_key = 'r0rwR62m771zxaLXkPVhSIQRyeARhlRa-T2Ymh20'


def storage(file_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'yashe'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    #要上传文件的本地路径

    ret, info = put_data(token, None, file_data)
    if info.status_code ==200:
        return ret.get('key')
    else:
        raise Exception('上传七牛失败')
