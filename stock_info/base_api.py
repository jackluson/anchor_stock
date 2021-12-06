'''
Desc: 用接口获取股票信息
File: /base_api.py
Project: stock_info
File Created: Friday, 11th June 2021 1:58:37 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import json
from dotenv import load_dotenv


class BaseApier:
    def __init__(self):
        load_dotenv()

    def get_client_headers(self, *,  cookie_env_key="xue_qiu_cookie", referer="https://xueqiu.com"):
        cookie = self.__dict__.get(cookie_env_key)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
            'Origin': referer,
            'Referer': referer,
            'Cookie': cookie
        }
        return headers

    def get_data_from_json(self, path):
        with open(path) as json_file:
            return json.load(json_file)
