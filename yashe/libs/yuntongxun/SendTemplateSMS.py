#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da86904c06001694d061eda1f93'

#主帐号Token
accountToken= '159037d9e16f4b4980a67fb5b5cd27d0'

#应用Id
appId='8a216da86904c06001694d061f2b1f99'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

class CCP(object):
    '''封装发送短信的辅助类'''
    _instance =None
    def __new__(cls, *args, **kwargs):
        #判断CCP类有没有已经差un关键好的对象，如果每页，创建一个对象，并且保存
        if cls._instance is None:
            obj=super(CCP,cls).__new__(cls,*args, **kwargs)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls._instance =obj
        return cls._instance


    # sendTemplateSMS(手机号码,内容数据,模板Id)
    def sendTemplateSMS(self,to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        #result是一个字典，有以下三个字段
        #smsMessageSid:760b115d46034c70a98cc1ddb317817e
        #dateCreated:20190305171522
        #statusCode:000000
        status_code =result.get('statusCode')
        if status_code == '000000':
            return 0
        else:
            return -1

if __name__ == '__main__':
    ccp =CCP()
    ret =ccp.sendTemplateSMS('13554762170',['1234','5'],1)
    print (ret)
