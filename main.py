'''
Desc: 入口文件
File: /main.py
Project: anchor_stock
File Created: Sunday, 27th June 2021 11:57:44 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import os
import logging
import time
from datetime import datetime
from multiprocessing import Process, Lock
from apscheduler.schedulers.blocking import BlockingScheduler
from controller.store_industry import store_industry
from controller.store_stock_industry import store_stock_industry
from controller.store_stock_daily import store_stock_daily
from controller.store_stock_main_financial_indicator import store_stock_main_financial_indicator
from controller.asset_calculator import AssetCalculator
from controller.asset_calculator_st import AssetCalculatorSt
from controller.backtest_st_stock import backtest_st_stock
from controller.save_value_level import SaveValueLevel
from controller.reversal_maxdrawdown import DrawdownCalculator, BatchDrawdownList, IndicatorCalculator
from controller.stock_profile import store_stock_proile


def store_stock_industry_and_daily():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/stock_daily_info.log',  filemode='a', level=logging.INFO)
    store_stock_industry()  # 执行行业股票信息入库
    store_stock_daily()  # 执行股票每天变动信息入库
    SaveValueLevel().save()


def bootstrap_stock_daily_scheduler():
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler()
    # 添加任务,时间间隔2S
    scheduler.add_job(
        store_stock_industry_and_daily,
        trigger='cron',
        day_of_week='mon-fri',
        hour=14,
        minute=00,
    )
    scheduler.start()

def main():
    input_value = int(input("请输入下列序号执行操作:\n \
        1.“定时日更”\n \
        2.“股票日更-行情&PE、PB”\n \
        3.“行业个股及简介更新”\n \
        4.“行业” \n \
        5.“财务指标”\n \
        6.市场指数/ETF近期收益计算\n \
        7.回撤ST股票摘帽收益计算\n \
    输入："))
    if input_value == 1:
        bootstrap_stock_daily_scheduler()
    elif input_value == 2:
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/stock_daily_info.log',  filemode='a', level=logging.INFO)

        # target_date = '2023-10-27'
        store_stock_daily()  # 执行股票每天变动信息入库
        SaveValueLevel().save()
    elif input_value == 3:
        store_stock_industry() #执行行业股票信息入库
        store_stock_proile()  # 执行股票简介信息入库
    elif input_value == 4:
        os.system('sh scripts/industry.sh')
        time.sleep(3)
    elif input_value == 5:
        store_stock_main_financial_indicator()  # 入库股票财报关键指标信息
    elif input_value == 6:
        etf_gain = AssetCalculator({
            'is_year': 1,
            'count': 20,
            'day_10_before': 1,
            'day_20_before': 1,
            'day_30_before': 1,
            'day_60_before': 1,
            'type': 'etf',  # index, etf
            'markdown': 0,
            'is_all': True
        })
        etf_gain.set_date({
            # 'begin_date': '2021-02-01',
            # 'end_date': '2023-01-31',
            'freq': 'W',  # Y,Q,M,W,D
        })
        etf_gain.calculate().output()  # ETF收益计算
    elif input_value == 7:
        backtest_st_stock()
if __name__ == '__main__':
    main()
