'''
Date: 2022-04-03 16:30:29
LastEditTime: 2022-04-03 16:49:23
Description: 更新成立,退市时间
'''
import sys
import os
sys.path.append(os.getcwd() + '/')
from sql_model.query import StockQuery
from sql_model.update import UpdateSql
from api.xue_api import ApiXueqiu


def update_found_date():
    each_query = StockQuery()
    each_update = UpdateSql()
    etf_funds = each_query.query_etf()
    print("the count of all etf:", len(etf_funds))
    api_xue_qiu = ApiXueqiu()
    for etf_item in etf_funds:
        market = etf_item['market']
        code = etf_item['code']
        symbol = market.upper() + code
        etf_base_info = api_xue_qiu.get_stock_page_info(symbol)
        each_update.udpate_etf_date(code, market, etf_base_info.get('found_date'), etf_base_info.get('delist_date'))

if __name__ == "__main__":
    update_found_date()
