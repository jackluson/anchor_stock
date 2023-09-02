'''
Desc: 巨潮资讯API
File: /cninfo_api.py
File Created: Friday, 3rd September 2021 10:53:17 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''
import os
import requests

from utils.index import get_request_header_key
from base.base_api import BaseApi

default_try_count = 3
class ApiCninfo(BaseApi):
    encKey = None  # 巨潮资讯接口encKey
    try_count = default_try_count # try count when happen error
    request_count = 0 # 记录请求记录
    headers = dict() # 请求头
    def __init__(self):
        super().__init__()
        self.encKey = os.getenv('encKey')
        if not self.encKey:
            self.set_encKey()
        self.set_headers()

    def set_encKey(self):
        target_url = 'http://webapi.cninfo.com.cn/api/stock/p_public0001'
        header_key = 'Accept-EncKey'
        entry_url = 'http://webapi.cninfo.com.cn/#/dataBrowse'
        self.encKey = get_request_header_key(
            entry_url, target_url, header_key)
        print(self.encKey, 'encKey')
        return self.encKey
    
    def set_headers(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Origin': 'https://webapi.cninfo.com.cn',
            'Referer': 'http://webapi.cninfo.com.cn/',
            'Accept-EncKey': self.encKey
        }
    
    def get_stocks_by_industry(self, industry_code):
        url = "http://webapi.cninfo.com.cn/api/stock/p_public0004?platetype=137004&platecode={0}&@orderby=SECCODE:asc&@column=SECCODE,SECNAME".format(
            industry_code)
        payload = {
            # 'fundcode': self.fund_code,
        }
        self.request_count = self.request_count +1
        res = requests.post(url, headers=self.headers, data=payload)
        try:
            if res.status_code == 200:
                res_json = res.json()
                print("res_json", res_json)
                if res_json.get('resultcode') == 401:
                    print('res_json', res_json) # 可能出现图片验证,这时候上网页上验证完即可
                    if '请进行图片验证' in res_json.get('resultmsg'):
                        val = input("请进行图片验证,验证完后再回来:\n \
                              1.“继续”\n \
                              2.“退出”\n \
                              ")
                        if val == '1':
                            return self.get_stocks_by_industry(industry_code)
                        else:
                            quit()
                    for i in range(0, self.try_count):
                        self.set_mcode()
                        self.set_headers()
                        self.try_count = self.try_count - 1
                        data = self.get_stocks_by_industry(industry_code)
                        if data:
                            self.try_count = default_try_count
                            return data
                    return None
                return res_json.get('records')
        except:
            raise('中断')
