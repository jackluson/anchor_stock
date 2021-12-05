'''
Desc: 股票某个阶段涨幅计算
File: /stock_period_gain_calculate.py
Project: controller
File Created: Sunday, 5th December 2021 8:41:54 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from stock_info.xue_api import ApiXueqiu


def stock_period_gain_calculate():
    each_api = ApiXueqiu()
    symbol = 'SH000300'
    period = 'month'
    begin_date = '2021-01-01'
    end_date = '2021-11-30'

    df_stock_kline_info = each_api.get_kline_info(
        symbol, begin_date, end_date, period)
    print(df_stock_kline_info)


if __name__ == '__main__':
    stock_period_gain_calculate()
