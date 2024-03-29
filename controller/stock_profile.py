'''
Desc:
File: /stock_base.py
Project: controller
File Created: Saturday, 2nd July 2022 10:01:56 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import logging
import time 
from sql_model.query import StockQuery
from sql_model.insert import StockInsert
from utils.index import bootstrap_thread
from infra.api.snowball import ApiSnowBall

def store_stock_proile():
    each_api = ApiSnowBall()
    each_insert = StockInsert()
    each_query = StockQuery()
    all_stock = each_query.query_all_stock()
    print('the number of all stock', len(all_stock))
    def crawlData(start, end):
        line = f'开始爬取: 从{start}到{end}'
        logging.info(line)
        for index in range(start, end):
            if not index % 100:
                print('index', index)
            stock = all_stock[index]
            code = stock.get('stock_code')
            info = each_api.get_stock_profile_info(code)
            if not info or not info['org_short_name_cn']:
                continue
            time_local =  time.localtime(info['established_date']/1000) if info['established_date'] else None
            established_date =  time.strftime("%Y-%m-%d",time_local) if time_local else None # js是毫秒制
            time_local = time.localtime(info['listed_date']/1000) if info['listed_date'] else None
            listed_date = time.strftime("%Y-%m-%d",time_local) if time_local else None # js是毫秒制
            profile_dict = {
                'stock_code': code,
                'stock_name': info['org_short_name_cn'],
                'org_name': info['org_name_cn'],
                'actual_controller': info['actual_controller'],
                'chairman': info['chairman'],
                'general_manager': info['general_manager'],
                'legal_representative': info['legal_representative'],
                'classi_name': info['classi_name'],
                'provincial_name': info['provincial_name'],
                'main_operation_business': info['main_operation_business'],
                'org_cn_introduction': info['org_cn_introduction'],
                'established_date': established_date,
                'listed_date': listed_date
            }
            each_insert.insert_stock_profile(profile_dict)
        line = f'结束:从{start}到{end}'
        logging.info(line)
    bootstrap_thread(crawlData, len(all_stock), 10)
    exit()

if __name__ == '__main__':
    store_stock_proile()
