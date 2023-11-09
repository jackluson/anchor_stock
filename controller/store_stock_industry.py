'''
Desc: 获取行业股票数据
File: /acquire_stock_industry.py
Project: anchor_stock
File Created: Friday, 11th June 2021 1:53:51 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import re
import time
from sql_model.query import StockQuery
from sql_model.insert import StockInsert
from api.cninfo_api import ApiCninfo


def store_stock_industry():
    each_insert = StockInsert()
    each_query = StockQuery()
    each_api = ApiCninfo()

    industry_data = each_query.query_industry_data()
    exist_all_stock = each_query.query_all_stock()
    print("exist_all_stock", len(exist_all_stock))
    cur_all_stock = []
    print('行业数量:', len(industry_data))
    start_index = 0
    for index in range(start_index, len(industry_data)):
        item_industry = industry_data[index]
        stock_list = each_api.get_stocks_by_industry(item_industry[1])
        if index % 50 == 0:
            print('index', index)
        if stock_list == None:
            print('item_industry', item_industry)
            exit()
        if len(stock_list) > 0:
            stock_dict = {
                'industry_code_third': item_industry[1],
                'industry_name_third': item_industry[0],
                'industry_code_second': item_industry[3],
                'industry_name_second': item_industry[2],
                'industry_code_first': item_industry[5],
                'industry_name_first': item_industry[4],
            }
            for item_stock in stock_list:
                code = item_stock.get('SECCODE')
                name = item_stock.get('SECNAME')
                stock_dict['stock_code'] = code
                cur_all_stock.append(code)
                stock_dict['stock_name'] = name
                stock_dict['delist_status'] = 0
                each_insert.insert_stock_industry_data(stock_dict) #update or add new stock
    print('len', len(cur_all_stock))
    #退市股票信息更新 -- 如果在最新的列表数据中没有之前存的股票,说明该股退市,更新delist_status 字段
    if start_index == 0:
        for item_stock in exist_all_stock:
            stock_code = item_stock.get('stock_code')
            if bool(re.search("^(6|9|0|2)\d{5}$", stock_code)) and stock_code not in cur_all_stock:
                item_stock['delist_status'] = 1
                print(item_stock)
                each_insert.insert_stock_industry_data(item_stock)
if __name__ == '__main__':
    store_stock_industry()
