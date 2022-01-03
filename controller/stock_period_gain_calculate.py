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


def printTop(df, market, count=5):
    print('{}的涨幅前五名,跌幅前五名分别为'.format(market))
    print(df.head(count))
    print(df.tail(count))
    print('------------{}------------\n'.format(market))


def getPercentHeadText(params):
    freq = params.get('freq')
    date = params.get('date')
    percent_str = ''
    if freq == 'M':
        percent_str = params.get('date')[0:7] + '月份'
    elif (freq == 'Y'):
        percent_str = params.get('date')[0:4] + '年份'
    elif (freq == 'Q'):
        percent_str = date + '(该季度)'
    elif (freq == 'W'):
        percent_str = date + '(该周)'
    return percent_str


def process_params(params):
    date = params.get('date')
    if date:
        ts = pd.Timestamp(date)
        freq = params.get('freq')
        res = ts.to_period(freq=freq)
        begin_date = res.start_time.strftime('%Y-%m-%d')
        end_date = res.end_time.strftime('%Y-%m-%d')
        params = {
            'begin_date': begin_date,
            'end_date': end_date,
            **params,
        }
    params = {
        'period': 'day',
        **params,
    }
    return params


each_api = ApiXueqiu()


def calculate_period_percent(symbol, begin_date, end_date, name, period):
    # each_api = ApiXueqiu()
    df_stock_kline_info = each_api.get_kline_info(
        symbol, begin_date, end_date, period)
    if df_stock_kline_info.empty:
        # print(symbol, etf_item['基金简称'])
        line = f'该ETF{name}--{symbol}没有查到数据'
        logging.info(line)
        return
    df_stock_kline_info['date'] = df_stock_kline_info.index.date
    df_stock_kline_info = df_stock_kline_info.set_index('date')
    try:
        # percent = df_stock_kline_info.loc[pd.Timestamp.date(
        #     datetime.fromisoformat(tail_date))]['percent']
        first_net = df_stock_kline_info.loc[df_stock_kline_info.index[0]]['close']
        first_chg = df_stock_kline_info.loc[df_stock_kline_info.index[0]]['chg']
        first_net = first_net - first_chg
        last_net = df_stock_kline_info.loc[df_stock_kline_info.index[-1]]['close']
        percent = round((last_net - first_net)/first_net*100, 2)
        return percent
    except:
        print(symbol)
        print(df_stock_kline_info)
        pass


def calculate_period_percent_params(symbol, name, params: Dict):
    params = process_params(params)
    begin_date = params.get('begin_date')
    end_date = params.get('end_date')
    period = params.get('period')
    percent = calculate_period_percent(
        symbol, begin_date, end_date, name, period)
    if percent:
        percent = str(percent) + '%'
    return percent


def stock_period_gain_calculate(params: Dict):

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
        name = stock.get('name')
        stock['percent'] = calculate_period_percent_params(
            symbol, name, params)
    select_columns = ['name', 'code', 'percent']
    freq = params.get('freq')
    percent_str = getPercentHeadText(params) if freq else 'percent'

    columns = {
        "code": "证券代码",
        "name": "证券名称",
        'percent': percent_str,
    }

    if freq and freq != 'Y':
        params['freq'] = 'Y'
        year_str = params.get('date')[0:4]
        select_columns.append('year_percent')
        columns['year_percent'] = year_str + '年以来涨幅',
        for stock in stock_list:
            symbol = stock.get('market') + stock.get('code')
            name = stock.get('name')
            stock['year_percent'] = calculate_period_percent_params(
                symbol, name, params)

    df_stock_list = pd.DataFrame(stock_list)

    df_stock_list = df_stock_list[select_columns]
    print("df_stock_list", df_stock_list)

    df_stock_list.rename(columns=columns, inplace=True)
    print("columns", columns)
    df_stock_list.set_index("证券名称", inplace=True)

    print(df_stock_list.to_markdown())
    # print(df_stock_list)


def etf_sh_gain_calulate(params: Dict):
    print("params", params, params.get('dir'))
    dir = params.get('dir') if params.get('dir') else './data/sh'
    begin_date = params.get('begin_date')
    end_date = params.get('end_date')
    period = params.get('period')
    files = os.listdir(dir)
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
                symbol = 'SH' + etf_item['fundCode']
                name = etf_item["fundAbbr"]
                df.at[index, 'fundCode'] = symbol
                df.at[index, 'percent'] = calculate_period_percent(
                    symbol, begin_date, end_date, name, period)
                # if index > 5:
                #     continue
                # # print(df.loc[index])

            df.dropna(subset=['percent'], inplace=True)
            df.sort_values(by='percent', inplace=True,
                           ascending=False, ignore_index=True)
            printTop(df, file[0:-5])
            df_all = df_all.append(df, ignore_index=True)

    df_all.sort_values(by='percent', inplace=True,
                       ascending=False, ignore_index=True)
    df_all.rename(columns={
        "fundCode": "证券代码",
        "fundAbbr": "基金简称",
    }, inplace=True)
    printTop(df_all, '上证全ETF')
    return df_all


def etf_sz_gain_calulate(params: Dict):
    df = download_szse_etf()
    begin_date = params.get('begin_date')
    end_date = params.get('end_date')
    period = params.get('period')
    for index, etf_item in df.iterrows():
        symbol = 'SZ' + index
        name = etf_item.get('基金简称')
        df.at[index, 'percent'] = calculate_period_percent(
            symbol, begin_date, end_date, name, period)
    df.dropna(subset=['percent'], inplace=True)
    df.sort_values(by='percent', inplace=True, ascending=False)
    df.reset_index(inplace=True)
    df = df[['证券代码', '基金简称', 'percent']]
    df['证券代码'] = "SZ" + df['证券代码']
    printTop(df, '深证全ETF')
    return df


def etf_gain_calulate(params: Dict, count=5):
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='log/stock_etf_info.log',  filemode='a', level=logging.INFO)
    df_etf = etf_sh_gain_calulate(process_params(params))
    sz_etf = etf_sz_gain_calulate(process_params(params))
    df_etf = df_etf.append(sz_etf, ignore_index=True)
    df_etf.sort_values(by='percent', inplace=True,
                       ascending=False, ignore_index=True)

    top_df = df_etf.head(count)
    last_df = df_etf.tail(count)

    def rank_year(df, params):
        freq = params.get('freq')
        year_str = params.get('date')[0:4]
        percent_str = getPercentHeadText(params)

        df = df.copy()
        columns = {
            'percent': percent_str,
        }
        if freq != 'Y':
            params['freq'] = 'Y'
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('证券代码')
                name = etf_item.get('基金简称')
                df.at[index, 'year_percent'] = calculate_period_percent_params(
                    symbol, name, params)
            columns['year_percent'] = year_str + '年以来涨幅'

        df['percent'] = df['percent'].astype(str) + '%'
        df.rename(
            columns=columns, inplace=True
        )
        df.set_index("基金简称", inplace=True)
        print(df.to_markdown())
    print('\n---涨幅排行榜---')

    rank_year(top_df, params)

    print('\n---跌幅排行榜---')
    rank_year(last_df, params)

    # printTop(df_etf, 'A股全ETF', 10)


if __name__ == '__main__':
    # stock_period_gain_calculate()
    etf_gain_calulate({
        dir: 'test'
    })
