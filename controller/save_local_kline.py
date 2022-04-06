'''
Desc:
File: /save_local_kline.py
Project: controller
File Created: Tuesday, 5th April 2022 4:27:20 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
import os
sys.path.append(os.getcwd() + '/')
from sql_model.query import StockQuery
from base.kline import Kline
from utils.constant import const

begin_date = '2011-12-30'
end_date = '2022-04-01'
def save_local_kline():
    each_query = StockQuery()
    etf_funds = each_query.query_etf()
    etf_funds.extend(const.index_stock_list)
    for index in range(0, len(etf_funds)):
        etf_item = etf_funds[index]
        symbol = etf_item.get('market').upper() + etf_item.get('code')
        name = etf_item.get('name')
        kline = Kline(symbol, name)
        kline.format_params(
            {
                'begin_date': begin_date,
                'end_date': end_date,
            }
        )
        kline.get_kline_data()


if __name__ == '__main__':
    save_local_kline()
