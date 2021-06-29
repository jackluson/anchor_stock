'''
Desc: 股票每日更新信息
File: /stock_daily.py
Project: anchor_stock
File Created: Monday, 21st June 2021 11:21:39 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from stock_info.api import StockApier
from sql_model.query import StockQuery
from sql_model.insert import StockInsert

def store_stock_daily(target_date=None):
    print("target_date", target_date)
    each_query = StockQuery()
    each_insert = StockInsert()
    each_api = StockApier()
    all_stock = each_query.query_all_stock(target_date)
    print('len(all_stock)', len(all_stock))
    for index in range(0,len(all_stock)):
        stock = all_stock[index]
        stock_code = stock.get('stock_code')
        print("stock_code", index, stock_code)
        stock_daily_info_dict = each_api.get_special_stock(stock_code,target_date)
        # status = 0 未上市状态
        if stock_daily_info_dict.get('status') == 0:
            print("stock_daily_info_dict", stock_daily_info_dict)
            continue
        each_insert.insert_stock_daily_data(stock_daily_info_dict)

if __name__ == '__main__':
  store_stock_daily()
