'''
Desc: 用接口获取股票信息
File: /api.py
Project: stock_info
File Created: Friday, 11th June 2021 1:58:37 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import requests

class StockApier:
  def __init__(self):
    print('init')
  
  def get_stocks_by_industry(self, industry_code):
    url = "http://webapi.cninfo.com.cn/api/stock/p_public0004?platetype=137004&platecode={0}&@orderby=SECCODE:asc&@column=SECCODE,SECNAME".format(industry_code)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
        'Origin': 'http://webapi.cninfo.com.cn',
        'Referer': 'http://webapi.cninfo.com.cn/',
        'mcode': 'MTYyMzM5NDAxNA=='
    }
    payload = {
        #'fundcode': self.fund_code,
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
