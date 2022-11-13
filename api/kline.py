'''
Desc:
File: /kline.py
File Created: Friday, 7th October 2022 1:13:52 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import requests

class ApiKline:
    def __init__(self):
        self.url = "http://localhost:5000/kline"

    def get_kline(self):
        response = requests.get(self.url)
        print("response", response)
        print("response", response.text)
        # return response.json()

if __name__ == '__main__':
    api_kline = ApiKline()
    api_kline.get_kline()
