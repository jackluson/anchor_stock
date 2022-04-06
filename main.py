'''
Desc: 入口文件
File: /main.py
Project: anchor_stock
File Created: Sunday, 27th June 2021 11:57:44 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from controller.store_industry import store_industry
from controller.store_stock_industry import store_stock_industry
from controller.store_stock_daily import store_stock_daily
from controller.store_stock_main_financial_indicator import store_stock_main_financial_indicator
from controller.stock_valuation_calculate import stock_valuation_calculate
from controller.asset_calculator import AssetCalculator
from controller.store_etf import store_etf
from controller.store_etf import store_etf
from controller.reversal_maxdrawdown import DrawdownCalculator, BatchDrawdownList, IndicatorCalculator
from calculate.correlated import Correlator
from strategy.momentum import MomentumStrategy


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
    input_value = input("请输入下列序号执行操作:\n \
        1.“行业” \n \
        2.“行业个股”\n \
        3.“股票日更”\n \
        4.“个股+日更”\n \
        5.“财务指标”\n \
        6.“A股估值”\n \
        7.入库ETF\n \
        8.市场指数/ETF近期收益计算\n \
    输入：")
    if input_value == '1' or input_value == '行业':
        store_industry()  # 执行申万行业信息入库
    elif input_value == '2' or input_value == '行业个股':
        store_stock_industry()  # 执行行业股票信息入库
    elif input_value == '3' or input_value == '股票日更':
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_daily_info.log',  filemode='a', level=logging.INFO)

        store_stock_daily()  # 执行股票每天变动信息入库
    elif input_value == '4' or input_value == '个股+日更':
        # store_stock_industry_and_daily() #联合执行
        bootstrap_stock_daily_scheduler()
    elif input_value == '5' or input_value == '财务指标':
        store_stock_main_financial_indicator()  # 入库股票财报关键指标信息
    elif input_value == '6' or input_value == 'A股低估值':
        stock_valuation_calculate()  # 入库股票财报关键指标信息
    elif input_value == '7' or input_value == '入库ETF':
        store_etf()  # 入库ETF
    elif input_value == '8' or input_value == '市场指数/ETF近期收益计算':
        etf_gain = AssetCalculator({
            'is_year': 1,
            'count': 10,
            'day_10_before': 1,
            'day_20_before': 1,
            'day_30_before': 1,
            'day_60_before': 1,
            'type': 'etf',  # index or etf
            'markdown': 1
        })
        etf_gain.set_date({
            # 'date': '2022-03-29',
            'freq': 'D',  # Y,Q,M,W,D
        })
        etf_gain.calculate().output()  # ETF收益计算


if __name__ == '__main__':
    is_main = 0
    if is_main:
        main()
    else:
        # max_drawdown_calculator = DrawdownCalculator('SH000001')
        # BatchDrawdownList()
        # IndicatorCalculator('SZ159981', '能源化工ETF')
        # correlator = Correlator([
        #     {
        #         'symbol': 'SH000300',

        #         'name': 'SH000300'
        #     },
        #     {
        #         'symbol': 'SZ159769',
        #         'name': 'SZ159769'
        #     },
        #     {
        #         'symbol': 'SH512880',
        #         'name': 'SH512880'
        #     },
        #     {
        #         'symbol': 'SH515700',
        #         'name': 'SH515700'
        #     }
        # ])
        # similarity = correlator.correlate()
        # print("similarity", similarity)
        # filter_near_similarity()
        strategy = MomentumStrategy('2021-01-01', '2021-12-31').traverse().predict()
