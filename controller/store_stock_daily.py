'''
Desc: 股票每日更新信息
File: /stock_daily.py
Project: anchor_stock
File Created: Monday, 21st June 2021 11:21:39 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import time
from datetime import datetime
import logging

from stock_info.xue_api import ApiXueqiu
from sql_model.query import StockQuery
from sql_model.insert import StockInsert


def store_stock_daily(target_date=None):
    if target_date and type(target_date) is not datetime:
        raise TypeError(
            'target_date must be a datetime.datetime, not a %s' % type(target_date))
    elif target_date:
        target_date = datetime.strftime(target_date, '%Y-%m-%d')
    if target_date == None:
        target_date = time.strftime('%Y-%m-%d', time.localtime())
    each_query = StockQuery()
    each_insert = StockInsert()
    each_api = ApiXueqiu()
    all_stock = each_query.query_all_stock(target_date)
    count = len(all_stock)
    line = f'开始爬取：爬取时间: {target_date} 个数数量: {count}'
    logging.info(line)
    for index in range(0, count):
        if not index % 100:
            print('index', index)
        stock = all_stock[index]
        stock_code = stock.get('stock_code')
        #print("stock_code", index, stock_code)
        stock_daily_info_dict = each_api.get_special_stock_quote(
            stock_code, target_date)
        # status = 0 未上市状态
        if stock_daily_info_dict.get('status') == 0:
            print("stock_daily_info_dict", stock_daily_info_dict)
            continue
        each_insert.insert_stock_daily_data(stock_daily_info_dict)
    line = f'开始结束：爬取时间: {target_date} 个数数量: {count}'
    logging.info(line)


if __name__ == '__main__':
    store_stock_daily()
