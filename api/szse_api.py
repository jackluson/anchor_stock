'''
Desc: 深证交易所api
File: /sse_api.py
File Created: Monday, 6th December 2021 9:20:01 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import random
import os
import requests

from utils.index import get_request_header_key

from base.base_api_config import BaseApiConfig


class ApiSZSE(BaseApiConfig):
    def __init__(self):
        super().__init__()
        self.szse_cookie = os.getenv('szse_cookie')
        if not self.szse_cookie:
            entry_url = 'http://www.szse.cn/'
            host = 'www.szse.cn'
            header_key = 'Cookie'
            szse_cookie = get_request_header_key(
                entry_url, host, header_key)
            self.szse_cookie = szse_cookie

    def get_etf_fund_list(self, tab1PAGENO,tab2PAGENO):
        url = "https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1945&tab1PAGENO={tab1PAGENO}&tab2PAGENO={tab2PAGENO}&random={random}&tab1PAGESIZE={tab1PAGESIZE}&tab2PAGESIZE={tab2PAGESIZE}".format(
            random=random.random(),
            tab1PAGENO=tab1PAGENO,
            tab2PAGENO=tab2PAGENO,
            tab2PAGESIZE=10,# 目前设置无效
            tab1PAGESIZE=10,# 目前设置无效
        )
        headers = self.get_client_headers(
            cookie_env_key="szse_cookie",
            referer='http://www.szse.cn/'
        )
        res = requests.get(url, headers=headers)
        try:
            if res.status_code == 200:
                res_json = res.json()
                return res_json
            else:
                print('请求异常', res)
        except:
            raise('中断')
