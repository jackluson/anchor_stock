'''
Desc: 入库股票主要财务指标
File: /store_stock_main_financial_indicator.py
Project: controller
File Created: Tuesday, 29th June 2021 10:51:03 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from sql_model.query import StockQuery
from stock_info.api import StockApier
from sql_model.insert import StockInsert

def store_stock_main_financial_indicator():
    count = 41
    each_insert = StockInsert()
    each_query = StockQuery()
    all_stock = each_query.query_all_stock()
    print('len(all_stock)', len(all_stock))
    each_api = StockApier()
    for index in range(76,len(all_stock)):
        stock = all_stock[index]
        stock_code = stock.get('stock_code')
        print("index", index, stock_code)
        stock_main_indicator_list = each_api.get_main_financial_indicator(stock_code, count)
        for stock_main_indicator in stock_main_indicator_list:
            each_insert.insert_stock_financial_indicator(stock_main_indicator)
            


if __name__ == '__main__':
    store_stock_main_financial_indicator()
