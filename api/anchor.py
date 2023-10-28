'''
Desc:
File: /anchor.py
File Created: Sunday, 15th January 2023 9:03:35 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
import os
sys.path.append(os.getcwd() + '/')
from base.base_api import BaseApi
import requests

class AnchorApi(BaseApi):
    def __init__(self):
        super().__init__()
        self.base_url = 'http://127.0.0.1:5000/api'
    def get_stock_profile(self, stock_code):
        payload = {
            'code': stock_code,
        }
        url = self.base_url + "/stock_profile?code={code}".format(
            **payload)
        res = requests.get(url)
        print("res", res)
        print(res.json())
if __name__ == '__main__':
    anchorApi = AnchorApi()
    code = '000005'
    anchorApi.get_stock_profile(code)
