'''
Desc: 入库股票主要财务指标
File: /store_stock_main_financial_indicator.py
Project: controller
File Created: Tuesday, 29th June 2021 10:51:03 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from stock_info.api import StockApier

def store_stock_main_financial_indicator(count=None):
    print("count", count)
    each_api = StockApier()
    code = '000039'
    stock_main_indicator = each_api.get_main_financial_indicator(code, count)
    print("stock_main_indicator", stock_main_indicator)


if __name__ == '__main__':
    store_stock_main_financial_indicator()
