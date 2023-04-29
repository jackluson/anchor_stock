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
from base.base_api_config import BaseApiConfig

default_try_count = 3
class ApiCninfo(BaseApiConfig):
    mcode = None  # 巨潮资讯接口mcode
    try_count = default_try_count # try count when happen error
    request_count = 0 # 记录请求记录
    headers = dict() # 请求头
    def __init__(self):
        super().__init__()
        self.mcode = os.getenv('mcode')
        if not self.mcode:
            self.set_mcode()
        self.set_headers()

    def set_mcode(self):
        target_url = 'http://webapi.cninfo.com.cn/api/stock/p_public0001'
        header_key = 'mcode'
        entry_url = 'http://webapi.cninfo.com.cn/#/dataBrowse'
        self.mcode = get_request_header_key(
            entry_url, target_url, header_key)
        return self.mcode
    
    def set_headers(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Origin': 'http://webapi.cninfo.com.cn',
            'Referer': 'http://webapi.cninfo.com.cn/',
            'mcode': self.mcode
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
                if res_json.get('resultcode') == 401:
                    print('res_json', res_json) # 可能出现图片验证,这时候上网页上验证完即可
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
