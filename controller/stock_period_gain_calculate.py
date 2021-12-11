'''
Desc: 股票某个阶段涨幅计算
File: /stock_period_gain_calculate.py
Project: controller
File Created: Sunday, 5th December 2021 8:41:54 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import os
import pandas as pd
import json
from datetime import datetime
from stock_info.xue_api import ApiXueqiu


def stock_period_gain_calculate():
    each_api = ApiXueqiu()
    stock_list = [
        {
            'name': '沪深300',
            'market': 'SH',
            'code': '000300'
        },
        {
            'name': '中证500',
            'market': 'SH',
            'code': '000905'
        },
        {
            'name': '中证1000',
            'market': 'SH',
            'code': '000852'
        },
        {
            'name': '中证全指',
            'market': 'SH',
            'code': '000985'
        },
        {
            'name': '上证指数',
            'market': 'SH',
            'code': '000001'
        },
        {
            'name': '深证成指',
            'market': 'SZ',
            'code': '399001'
        },
        {
            'name': '创业板指',
            'market': 'SZ',
            'code': '399006'
        },
        {
            'name': '科创50',
            'market': 'SH',
            'code': '000688'
        }
    ]
    for stock in stock_list:
        symbol = stock.get('market') + stock.get('code')
        period = 'year'
        begin_date = '2021-01-01'
        end_date = '2021-12-31'

        df_stock_kline_info = each_api.get_kline_info(
            symbol, begin_date, end_date, period)
        print(stock.get('name'), '数据如下:')
        print(df_stock_kline_info)


def etf_gain_calulate():
    dir = './data/sh'
    files = os.listdir(dir)
    each_api = ApiXueqiu()
    begin_date = '2021-12-09'
    end_date = '2021-12-09'
    period = 'day'
    for file in files:
        file_path = dir + '/' + file
        with open(file_path) as json_file:
            cur_market_etfs = json.load(json_file)
            df = pd.DataFrame(
                cur_market_etfs)
            df['percent'] = None
            df = df[['fundCode', 'fundAbbr', 'percent',
                     'secNameFull', 'companyName', 'INDEX_NAME']]
            for index, etf_item in df.iterrows():
                # if index > 5:
                #     continue
                # # print(df.loc[index])
                symbol = 'SH' + etf_item['fundCode']
                df_stock_kline_info = each_api.get_kline_info(
                    symbol, begin_date, end_date, period)
                if df_stock_kline_info.empty:
                    continue
                df_stock_kline_info['date'] = df_stock_kline_info.index.date
                df_stock_kline_info = df_stock_kline_info.set_index('date')
                percent = df_stock_kline_info.loc[pd.Timestamp.date(
                    datetime.fromisoformat(end_date))]['percent']
                df.at[index, 'percent'] = percent
            df.sort_values(by='percent', inplace=True, ascending=False)
            print(df)


if __name__ == '__main__':
    # stock_period_gain_calculate()
    etf_gain_calulate()
