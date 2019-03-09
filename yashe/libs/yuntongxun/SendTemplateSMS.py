#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#���ʺ�
accountSid= '8a216da86904c06001694d061eda1f93'

#���ʺ�Token
accountToken= '159037d9e16f4b4980a67fb5b5cd27d0'

#Ӧ��Id
appId='8a216da86904c06001694d061f2b1f99'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

class CCP(object):
    '''��װ���Ͷ��ŵĸ�����'''
    _instance =None
    def __new__(cls, *args, **kwargs):
        #�ж�CCP����û���Ѿ���un�ؼ��õĶ������ÿҳ������һ�����󣬲��ұ���
        if cls._instance is None:
            obj=super(CCP,cls).__new__(cls,*args, **kwargs)
            # ��ʼ��REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls._instance =obj
        return cls._instance


    # sendTemplateSMS(�ֻ�����,��������,ģ��Id)
    def sendTemplateSMS(self,to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        #result��һ���ֵ䣬�����������ֶ�
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
