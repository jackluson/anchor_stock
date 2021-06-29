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
import time
import json
import os
from dotenv import load_dotenv
from utils.file_op import write_fund_json_data

class StockApier:
  def __init__(self):
      load_dotenv()

  def get_stocks_by_industry(self, industry_code):
      url = "http://webapi.cninfo.com.cn/api/stock/p_public0004?platetype=137004&platecode={0}&@orderby=SECCODE:asc&@column=SECCODE,SECNAME".format(industry_code)
      mcode = os.getenv('mcode')
      headers = {
          'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
          'Origin': 'http://webapi.cninfo.com.cn',
          'Referer': 'http://webapi.cninfo.com.cn/',
          'mcode': mcode
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
  
  def get_special_stock(self, symbol, date=None):
      if not date:
        date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
      dir = './archive_data/json/xueqiu/'+ symbol + '/'
      file_name_path = dir + date + '.json'
      if os.path.exists(file_name_path):
        res_json = self.get_data_from_json(file_name_path)
      else:
        url = "https://stock.xueqiu.com/v5/stock/quote.json?symbol={0}&extend=detail".format(symbol)
        cookie = os.getenv('xue_qiu_cookie')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
            'Origin': 'https://xueqiu.com',
            'Referer': 'https://xueqiu.com',
            'Cookie': cookie
        }
        res = requests.get(url, headers=headers)
        try:
            if res.status_code == 200:
              res_json = res.json()
        except:
            raise('中断')
      data = res_json['data'].get('quote')
      data_others = res_json['data'].get('others')
      time_format = time.strftime("%Y-%m-%d", time.localtime(data['timestamp']/1000))
      # 数据存档
      dir = './archive_data/json/xueqiu/'+ symbol + '/'
      file_name = time_format + '.json'
      write_fund_json_data(res_json, file_name,  dir)
      #print("time_format", time_format)
      stock_daily_dict = {
        'code': data['code'],
        'status': data['status'],
        'name': data['name'],
        'exchange': data['exchange'],
        'timestamp': time.strftime("%Y-%m-%d", time.localtime(data['timestamp']/1000)),
        'price': data['current'],
        'open_price': data['open'],
        'limit_up_price': data['limit_up'],
        'limit_low_price': data['limit_down'],
        'avg_price': data['avg_price'],
        'last_close_price': data['last_close'],
        'amplitude': data['amplitude'],
        'turnover_rate': data['turnover_rate'],
        'low52w': data['low52w'],
        'high52w': data['high52w'],
        'pb': data['pb'],
        'pe_ttm': data['pe_ttm'],
        'pe_lyr': data['pe_lyr'],
        'pe_forecast': data['pe_forecast'],
        'amount': data['amount'],
        'volume': data['volume'],
        'volume_ratio': data['volume_ratio'],
        'pankou_ratio': data_others['pankou_ratio'],
        'float_shares': data['float_shares'],
        'total_shares': data['total_shares'],
        'float_market_capital': data['float_market_capital'],
        'market_capital': data['market_capital'],
        'eps': data['eps'],
        'navps': data['navps'],
        'dividend': data['dividend'],
        'dividend_yield': data['dividend_yield'],
        'percent': data['percent'],
        'current_year_percent': data['current_year_percent'],
      }
      return stock_daily_dict

  def get_main_financial_indicator(self, count):
      print("count", count)
  def get_data_from_json(self, path):
      with open(path) as json_file:
        return json.load(json_file)
