'''
Desc: 入口文件
File: /main.py
Project: anchor_stock
File Created: Sunday, 27th June 2021 11:57:44 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import time

from controller.store_industry import store_industry
from controller.store_stock_industry import store_stock_industry
from controller.store_stock_daily import store_stock_daily
from controller.store_stock_main_financial_indicator import store_stock_main_financial_indicator

def store_stock_industry_and_daily():
    target_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    store_stock_industry() # 执行行业股票信息入库
    store_stock_daily(target_date) # 执行股票每天变动信息入库

def main():
    print('main')
    #store_industry() # 执行申万行业信息入库

    #store_stock_industry() # 执行行业股票信息入库

    #store_stock_daily() # 执行股票每天变动信息入库

    #store_stock_industry_and_daily() #联合执行

    store_stock_main_financial_indicator() # 入库股票财报关键指标信息
if __name__ == '__main__':
    main()
