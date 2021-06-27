'''
Desc: 入口文件
File: /main.py
Project: anchor_stock
File Created: Sunday, 27th June 2021 11:57:44 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from controller.store_industry import store_industry
from controller.store_stock_industry import store_stock_industry
from controller.store_stock_daily import store_stock_daily

def main():
    print('main')
    #store_industry() # 执行申万行业信息入库

    #store_stock_industry() # 执行行业股票信息入库

    store_stock_daily() # 执行股票每天变动信息入库
if __name__ == '__main__':
    main()
