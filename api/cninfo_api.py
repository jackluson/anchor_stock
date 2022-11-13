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


class ApiCninfo(BaseApiConfig):
    mcode = None  # 巨潮资讯接口mcode

    def __init__(self):
        super().__init__()
        self.mcode = os.getenv('mcode')
        if not self.mcode:
            entry_url = 'http://webapi.cninfo.com.cn/#/dataBrowse'
            target_url = 'http://webapi.cninfo.com.cn/api/stock/p_public0001'
            header_key = 'mcode'
            self.mcode = get_request_header_key(
                entry_url, target_url, header_key)

    def get_stocks_by_industry(self, industry_code):
        url = "http://webapi.cninfo.com.cn/api/stock/p_public0004?platetype=137004&platecode={0}&@orderby=SECCODE:asc&@column=SECCODE,SECNAME".format(
            industry_code)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Origin': 'http://webapi.cninfo.com.cn',
            'Referer': 'http://webapi.cninfo.com.cn/',
            'mcode': self.mcode
        }
        payload = {
            # 'fundcode': self.fund_code,
        }
        res = requests.post(url, headers=headers, data=payload)
        try:
            if res.status_code == 200:
                res_json = res.json()
                if res_json.get('resultcode') == 401:
                    print('res_json', res_json)
                    return None
                return res_json.get('records')
        except:
            raise('中断')
