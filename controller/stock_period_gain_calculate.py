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
from .download_etf import download_szse_etf
import pandas as pd
import os
import json
from typing import Dict
import logging


def printTop(df, market):
    print('{}的涨幅前五名,跌幅前五名分别为'.format(market))
    print(df.head(5))
    print(df.tail(5))
    print('------------{}------------\n'.format(market))


def stock_period_gain_calculate():
    each_api = ApiXueqiu()
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


def etf_sh_gain_calulate(params: Dict):
    print("params", params, params.get('dir'))
    dir = params.get('dir') if params.get('dir') else './data/sh'
    begin_date = params.get('begin_date')
    end_date = params.get('end_date')
    period = params.get('period')
    files = os.listdir(dir)
    each_api = ApiXueqiu()
    df_all = pd.DataFrame([])
    for file in files:
        file_path = dir + '/' + file
        with open(file_path) as json_file:
            cur_market_etfs = json.load(json_file)
            df = pd.DataFrame(
                cur_market_etfs)
            df['percent'] = None
            df = df[['fundCode', 'fundAbbr', 'percent']]
            # df = df[['fundCode', 'fundAbbr', 'percent',
            #          'secNameFull', 'companyName', 'INDEX_NAME']]
            for index, etf_item in df.iterrows():
                # if index > 5:
                #     continue
                # # print(df.loc[index])
                symbol = 'SH' + etf_item['fundCode']
                df_stock_kline_info = each_api.get_kline_info(
                    symbol, begin_date, end_date, period)
                if df_stock_kline_info.empty:
                    line = f'该ETF{etf_item["fundAbbr"]}--{symbol}没有查到数据'
                    logging.info(line)
                    # print(symbol, etf_item['fundAbbr'], '没有查到数据')
                    continue
                df_stock_kline_info['date'] = df_stock_kline_info.index.date
                df_stock_kline_info = df_stock_kline_info.set_index('date')
                try:
                    # percent = df_stock_kline_info.loc[pd.Timestamp.date(
                    #     datetime.fromisoformat(end_date))]['percent']
                    first_net = df_stock_kline_info.loc[df_stock_kline_info.index[0]]['close']
                    first_chg = df_stock_kline_info.loc[df_stock_kline_info.index[0]]['chg']
                    first_net = first_net - first_chg
                    last_net = df_stock_kline_info.loc[df_stock_kline_info.index[-1]]['close']
                    df.at[index, 'percent'] = round(
                        (last_net - first_net)/first_net*100, 4)
                except:
                    line = f'该ETF{etf_item["fundAbbr"]}--{symbol}数据处理有错'
                    logging.error(line)
                    # print(symbol)
                    # print(df_stock_kline_info)
                    pass
            df.dropna(subset=['percent'], inplace=True)
            df.sort_values(by='percent', inplace=True,
                           ascending=False, ignore_index=True)
            # print(df)
            printTop(df, file[0:-5])
            df_all = df_all.append(df, ignore_index=True)
    df_all.sort_values(by='percent', inplace=True,
                       ascending=False, ignore_index=True)
    df_all.rename(columns={"fundCode": "证券代码",
                           "fundAbbr": "基金简称"}, inplace=True)
    printTop(df_all, '上证全ETF')
    return df_all


def etf_sz_gain_calulate(params: Dict):
    df = download_szse_etf()
    each_api = ApiXueqiu()
    begin_date = params.get('begin_date')
    end_date = params.get('end_date')
    period = params.get('period')
    for index, etf_item in df.iterrows():
        symbol = 'SZ' + index
        df_stock_kline_info = each_api.get_kline_info(
            symbol, begin_date, end_date, period)
        if df_stock_kline_info.empty:
            print(symbol, etf_item['基金简称'])
            continue
        df_stock_kline_info['date'] = df_stock_kline_info.index.date
        df_stock_kline_info = df_stock_kline_info.set_index('date')
        try:
            # percent = df_stock_kline_info.loc[pd.Timestamp.date(
            #     datetime.fromisoformat(tail_date))]['percent']
            first_net = df_stock_kline_info.loc[df_stock_kline_info.index[0]]['close']
            first_chg = df_stock_kline_info.loc[df_stock_kline_info.index[0]]['chg']
            first_net = first_net - first_chg
            last_net = df_stock_kline_info.loc[df_stock_kline_info.index[-1]]['close']
            # percent = df_stock_kline_info.loc[df_stock_kline_info.index[-1]]['percent']

            df.at[index, 'percent'] = round(
                (last_net - first_net)/first_net*100, 4)
        except:
            print(symbol)
            print(df_stock_kline_info)
            pass
    df.dropna(subset=['percent'], inplace=True)
    df.sort_values(by='percent', inplace=True, ascending=False)
    df.reset_index(inplace=True)
    df = df[['证券代码', '基金简称', 'percent']]
    printTop(df, '深证全ETF')

    return df


def etf_gain_calulate(params: Dict):
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/stock_etf_info.log',  filemode='a', level=logging.INFO)
    df_etf = etf_sh_gain_calulate(params)
    sz_etf = etf_sz_gain_calulate(params)
    df_etf = df_etf.append(sz_etf, ignore_index=True)
    df_etf.sort_values(by='percent', inplace=True, ascending=False)
    printTop(df_etf, 'A股全ETF')
    print("df_etf", df_etf)


if __name__ == '__main__':
    # stock_period_gain_calculate()
    etf_gain_calulate({
        dir: 'test'
    })
