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
from datetime import datetime
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from controller.store_industry import store_industry
from controller.store_stock_industry import store_stock_industry
from controller.store_stock_daily import store_stock_daily
from controller.store_stock_main_financial_indicator import store_stock_main_financial_indicator
# from controller.stock_value_calculate import stock_value_calculate


def store_stock_industry_and_daily():
    store_stock_industry()  # 执行行业股票信息入库
    #target_date = datetime.strptime('2021-07-08','%Y-%m-%d')
    store_stock_daily()  # 执行股票每天变动信息入库


def bootstrap_stock_daily_scheduler():
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔2S
    scheduler.add_job(
        store_stock_industry_and_daily,
        trigger='cron',
        day_of_week='mon-fri',
        hour=17,
        minute=00,
    )
    scheduler.start()


def main():
    print('main')
    input_value = input("请输入下列序号执行操作:\n \
        1.“行业” \n \
        2.“行业个股”\n \
        3.“股票日更”\n \
        4.“个股+日更”\n \
        5.“财务指标”\n \
        6.“A股估值”\n \
    输入：")
    if input_value == '1' or input_value == '行业':
        store_industry()  # 执行申万行业信息入库
    elif input_value == '2' or input_value == '行业个股':
        store_stock_industry()  # 执行行业股票信息入库
    elif input_value == '3' or input_value == '股票日更':
        store_stock_daily()  # 执行股票每天变动信息入库
    elif input_value == '4' or input_value == '个股+日更':
        # store_stock_industry_and_daily() #联合执行
        bootstrap_stock_daily_scheduler()
    elif input_value == '5' or input_value == '财务指标':
        store_stock_main_financial_indicator()  # 入库股票财报关键指标信息

    # elif input_value == '6' or input_value == 'A股估值':
    #     stock_value_calculate() # 入库股票财报关键指标信息
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/stock_daily_info.log',  filemode='a', level=logging.INFO)
    main()
