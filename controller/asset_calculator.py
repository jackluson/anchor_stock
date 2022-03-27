'''
Desc: 股票某个阶段涨幅计算
File: /asset_calculator.py
Project: controller
File Created: Sunday, 5th December 2021 8:41:54 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from datetime import datetime

from stock_info.xue_api import ApiXueqiu
from sql_model.query import StockQuery
from base.kline import Kline
from calculate.correlated import Correlator
import pandas as pd
import logging


ago_list = [10, 20, 30, 60]
index_stock_list = [
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


class AssetCalculator:
    def __init__(self, config={}):
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_etf_info.log',  filemode='a', level=logging.INFO)
        self.is_year = config.get('is_year')
        for ago in ago_list:
            ago_key = 'day_' + str(ago) + '_ago'
            # self[ago_key] = config.get(ago_key)
            setattr(self, ago_key, config.get(ago_key))
        self.markdown = config.get('markdown')
        self.type = config.get('type')
        self.count = config.get('count') if config.get('count') else 5
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.each_api = ApiXueqiu()
        if self.type == 'etf':
            self.set_etf_data()
        elif self.type == 'index':
            self.set_index_data()

    def set_etf_data(self):
        each_query = StockQuery()
        etf_funds = each_query.query_etf()
        self.df_data = pd.DataFrame(etf_funds)

    def set_index_data(self):
        self.df_data = pd.DataFrame(index_stock_list)

    def format_params(self, params, is_self=True):
        date = params.get('date') if params.get('date') else self.date
        ts = pd.Timestamp(date)
        freq = params.get('freq')
        res = ts.to_period(freq=freq)
        begin_date = res.start_time.strftime('%Y-%m-%d')
        end_date = res.end_time.strftime('%Y-%m-%d')
        params = {
            'period': 'day',
            **params,
            'begin_date': begin_date,
            'end_date': end_date,
        }
        if is_self:
            # 覆盖默认值
            if date:
                self.date = date
            self.freq = freq if freq else "D"
            self.params = params
            return self
        return params

    def format_freq_params(self, freq="Y"):
        return self.format_params({
            **self.params,
            'freq': freq
        }, False)

    def get_percent_column_name(self, date, freq):
        percent_str = date
        params = self.params
        begin_date = params.get('begin_date')
        end_date = params.get('end_date')
        if freq == 'M':
            percent_str = date[0:7] + '月份'
        elif (freq == 'Y'):
            percent_str = date[0:4] + '年份以来'
        elif (freq == 'Q'):
            percent_str = date + '(该季度)'
        elif (freq == 'W'):
            percent_str = "本周" + "("+begin_date + '一' + end_date + ')'
        return percent_str

    def calculate(self):
        for index, etf_item in self.df_data.iterrows():
            symbol = etf_item.get('market').upper() + etf_item.get('code')
            name = etf_item.get('name')
            self.df_data.at[index, 'percent'] = self.calculate_period_percent(
                symbol, name)
        self.df_data.dropna(subset=['percent'], inplace=True)
        self.df_data.sort_values(
            by='percent', inplace=True, ascending=False, ignore_index=True)
        return self

    def calculate_period_percent(self, symbol, name, default_params=None, is_format_str=False):
        params = default_params if default_params else self.params
        kline = Kline(symbol, name)
        kline.format_params(params)
        kline.get_kline_data()
        return kline.calculate_period_percent(is_format_str)

    def affix_date_percent_date(self, ago, etf_item):
        symbol = etf_item.get('market').upper() + etf_item.get('code')
        name = etf_item.get('name')
        ts = pd.Timestamp(self.date).timestamp()
        self.day_10_ago_date = datetime.fromtimestamp(
            ts - ago * 24 * 3600).strftime("%Y-%m-%d")
        ago_params = {
            'period': 'day',
            'begin_date': self.day_10_ago_date,
            'end_date': self.date,
        }
        return self.calculate_period_percent(symbol, name, ago_params, True)

    def format_dataframe(self, init_df=None):
        df = self.df_data
        if isinstance(init_df, pd.DataFrame) and not init_df.empty:
            df = init_df.copy()
        columns = {
            "code": "证券代码",
            "name": "证券名称",
            'percent': self.get_percent_column_name(self.date, self.freq),
            'year_percent': self.get_percent_column_name(self.date, 'Y'),
        }
        for ago in ago_list:
            if getattr(self, "day_" + str(ago) + "_ago"):
                ago_key = 'day_' + str(ago) + '_ago_percent'
                columns[ago_key] = '近' + str(ago) + '天'
                for index, etf_item in df.iterrows():
                    df.at[index, ago_key] = self.affix_date_percent_date(
                        ago, etf_item)
        if self.is_year:
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('market').upper() + etf_item.get('code')
                name = etf_item.get('name')
                year_params = self.format_freq_params()
                df.at[index, 'year_percent'] = self.calculate_period_percent(
                    symbol, name, year_params, True)
        df['percent'] = df['percent'].astype(str) + '%'
        # print("df", df)
        # Correlator(df).correlate()
        df.drop('market', axis=1, inplace=True)
        df.rename(columns=columns, inplace=True)
        df.set_index("证券名称", inplace=True)
        if self.markdown:
            print(df.to_markdown())
        else:
            print(df)

    def ouputRank(self):
        count = self.count
        top_df = self.df_data.head(count)
        last_df = self.df_data.tail(count).iloc[::-1]
        print('涨幅前{}名为:'.format(count))
        self.format_dataframe(top_df)
        print('跌幅前{}名为:'.format(count))
        self.format_dataframe(last_df)

    def output(self):
        if self.type == 'etf':
            self.ouputRank()
        elif self.type == 'index':
            self.format_dataframe()


if __name__ == '__main__':
    # asset_calculator()
    etf_gain = AssetCalculator({
        'is_year': 1,
        'type': 'etf',  # index or etf
        'markdown': 1
    })
    etf_gain.format_params({
        'date': '2022-01-18',
        'freq': 'D',
    }).calculate().output()
