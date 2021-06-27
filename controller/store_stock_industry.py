'''
Desc: 获取行业股票数据
File: /acquire_stock_industry.py
Project: anchor_stock
File Created: Friday, 11th June 2021 1:53:51 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from sql_model.query import StockQuery
from sql_model.insert import StockInsert
from stock_info.api import StockApier


def store_stock_industry():
  each_insert = StockInsert()
  each_query = StockQuery()
  each_api = StockApier()

  industry_data = each_query.query_industry_data()
  for item_industry in industry_data:
      stock_list = each_api.get_stocks_by_industry(item_industry[1])
      stock_dict = {
          'industry_code_third': item_industry[1],
          'industry_name_third': item_industry[0],
          'industry_code_second': item_industry[3],
          'industry_name_second': item_industry[2],
          'industry_code_first': item_industry[5],
          'industry_name_first': item_industry[4],
      }
      if stock_list == None:
        print('item_industry', item_industry)
        exit()
      for item_stock in stock_list:
        code = item_stock.get('SECCODE')
        name = item_stock.get('SECNAME')
        stock_dict['stock_code'] = code
        stock_dict['stock_name'] = name
        each_insert.insert_stock_industry_data(stock_dict)

if __name__ == '__main__':
    store_stock_industry()
