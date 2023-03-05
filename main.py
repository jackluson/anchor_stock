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

import matplotlib.pyplot as plt
from multiprocessing import Process, Lock
from apscheduler.schedulers.blocking import BlockingScheduler
from controller.store_industry import store_industry
from controller.store_stock_industry import store_stock_industry
from controller.store_stock_daily import store_stock_daily
from controller.store_stock_main_financial_indicator import store_stock_main_financial_indicator
from controller.stock_valuation_calculate import stock_valuation_calculate
from controller.asset_calculator import AssetCalculator
from controller.asset_calculator_st import AssetCalculatorSt
from controller.return_test_st_stock import return_test_st_stock

from controller.store_etf import store_etf
from controller.store_etf import store_etf
from controller.reversal_maxdrawdown import DrawdownCalculator, BatchDrawdownList, IndicatorCalculator
from calculate.correlated import Correlator
from strategy.momentum import MomentumStrategy
from controller.stock_profile import store_stock_proile


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
    input_value = int(input("请输入下列序号执行操作:\n \
        1.“行业” \n \
        2.“个股信息”\n \
        3.“定时日更个股”\n \
        4.“财务指标”\n \
        5.“A股估值”\n \
        6.入库ETF\n \
        7.市场指数/ETF近期收益计算\n \
        8.ST股票近期收益计算\n \
    输入："))
    if input_value == 1:
        os.system('sh scripts/industry.sh')
        time.sleep(3)
        store_industry()  # 执行申万行业信息入库
    elif input_value == 2:
        select = int(input("请再输入下列序号执行操作:\n \
            1.“行业个股”\n \
            2.“个股简介”\n \
            3.“股票日更”\n \
        输入："))
        if select == 1:
            store_stock_industry()  # 执行行业股票信息入库
        elif select == 2:
            store_stock_proile()  # 执行股票简介信息入库
        elif select == 3:
            logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_daily_info.log',  filemode='a', level=logging.INFO)

            store_stock_daily()  # 执行股票每天变动信息入库
        else:
            print('输入有误')
    elif input_value == 3:
        # store_stock_industry_and_daily() #联合执行
        bootstrap_stock_daily_scheduler()
    elif input_value == 4:
        store_stock_main_financial_indicator()  # 入库股票财报关键指标信息
    elif input_value == 5:
        stock_valuation_calculate()  # 入库股票财报关键指标信息
    elif input_value == 6:
        store_etf()  # 入库ETF
    elif input_value == 7:
        etf_gain = AssetCalculator({
            # 'is_year': 1,
            'count': 10,
            # 'day_10_before': 1,
            # 'day_20_before': 1,
            # 'day_30_before': 1,
            # 'day_60_before': 1,
            'type': 'index',  # index, etf
            'markdown': 0
        })
        etf_gain.set_date({
            'begin_date': '2021-02-01',
            'end_date': '2023-01-31',
            # 'freq': 'W',  # Y,Q,M,W,D
        })
        etf_gain.calculate().output()  # ETF收益计算
    elif input_value == 8:
        etf_gain = AssetCalculatorSt({
            'is_year': 1,
            'count': 20,
            'day_10_before': 1,
            'day_20_before': 1,
            'day_30_before': 1,
            'day_60_before': 1,
            'type': 'st',  # index, etf, st
            'markdown': 0
        })
        etf_gain.set_date({
            # 'date': '2023-02-03',
            'freq': 'W',  # Y,Q,M,W,D
        })
        etf_gain.calculate().ouputRank() # ETF收益计算

if __name__ == '__main__':
    is_main = 0
    if is_main == 0:
        main()
    elif is_main == 1:
        return_test_st_stock()
    else :
        # max_drawdown_calculator = DrawdownCalculator('SH000001')
        # BatchDrawdownList()
        # IndicatorCalculator('SZ159981', '能源化工ETF')
        # correlator = Correlator()
        # correlator.set_compare([
        #     # {
        #     #     'symbol': 'SH000300',
        #     #     'name': 'SH000300'
        #     # },
        #     {
        #         'symbol': 'SH513100',
        #         'name': '纳指ETF'
        #     },
        #     {
        #         'symbol': 'SZ159941',
        #         'name': '纳指ETF'
        #     },
        #     {
        #         'symbol': 'SH510880',
        #         'name': '红利ETF'
        #     }
        # ])
        # correlator.correlate()
        
        # print(correlator.res_compare)
        # print(correlator.filter_near_similarity())
        # print("similarity", similarity)
        # exit()
        recall_date_list = [
            {
                'start_date': '2017-12-31',
                'end_date': '2018-06-30',
            },
             {
                'start_date': '2018-06-30',
                'end_date': '2018-12-31',
            }
            ,
            {
                'start_date': '2018-12-31',
                'end_date': '2019-06-30',
            },
            {
                'start_date': '2019-06-30',
                'end_date': '2019-12-31',
            },
            {
                'start_date': '2019-12-31',
                'end_date': '2020-06-30',
            },
            {
                'start_date': '2020-06-30',
                'end_date': '2020-12-31',
            },
            {
                'start_date': '2020-12-31',
                'end_date': '2021-06-30',
            },
            {
                'start_date': '2021-06-30',
                'end_date': '2021-12-31',
            }
        ]
        process_list = []
        start_time = time.time()
        lock = Lock()
        def run(start_date, end_date):
            strategy = MomentumStrategy(start_date, end_date, lock)
            strategy.traverse()
        process_count = 0
        len = len(recall_date_list)
        for i in range(process_count):
            p = Process(target=run, args=(recall_date_list[i]['start_date'], recall_date_list[i]['end_date']))
            p.start()
            process_list.append(p)
        for p in process_list:
            p.join()
        end_time = time.time()
        input_value = input("请输入回撤序号:\n")
        index = int(input_value)
        run(recall_date_list[index]['start_date'], recall_date_list[index]['end_date'])
        print('run time is %s' % (end_time - start_time))
        plt.show()
