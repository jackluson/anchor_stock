'''
Desc: 股票每日更新信息
File: /stock_daily.py
Project: anchor_stock
File Created: Monday, 21st June 2021 11:21:39 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from utils.index import bootstrap_thread
from api.xue_api import ApiXueqiu
from sql_model.query import StockQuery
from sql_model.insert import StockInsert
from infra.logger.logger import logger
from infra.config.parser import conf_parser


def store_stock_daily(target_date=None):
    # if target_date and type(target_date) is not datetime:
    #     raise TypeError(
    #         'target_date must be a datetime.datetime, not a %s' % type(target_date))
    if target_date == None:
        target_date = conf_parser.latest_data_day
    print("target_date", target_date)
    each_query = StockQuery()
    each_insert = StockInsert()
    each_api = ApiXueqiu()
    all_stock = each_query.query_all_stock(target_date)
    count = len(all_stock)
    print("total:", count)
    def crawlData(start, end):
        line = f'开始爬取：爬取时间: {target_date} 个数数量: {end-start}(从{start}到{end})'
        logger.info(line)
        for index in range(start, end):
            if not index % 100:
                print('index', index)
            stock = all_stock[index]
            stock_code = stock.get('stock_code')
            #print("stock_code", index, stock_code)
            stock_daily_info_dict = each_api.get_stock_quote(
                stock_code)
            # status = 0 未上市状态
            if not stock_daily_info_dict or stock_daily_info_dict.get('status') == 0:
                logger.info(stock_daily_info_dict)
                logger.info({'stock_code': stock_code})

                continue
            if stock_daily_info_dict.get('timestamp') != target_date:
                logger.info(stock_daily_info_dict.get('timestamp'))
                logger.info({'stock_code': stock_code})

                continue
            each_insert.insert_stock_daily_data(stock_daily_info_dict)
        line = f'结束：爬取时间: {target_date} 个数数量: {end-start}(从{start}到{end})'
        logger.info(line)
    bootstrap_thread(crawlData, count, 8)


if __name__ == '__main__':
    store_stock_daily()
