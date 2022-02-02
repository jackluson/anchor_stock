'''
Desc: 股票某个阶段涨幅计算
File: /stock_period_gain_calculate.py
Project: controller
File Created: Sunday, 5th December 2021 8:41:54 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from datetime import datetime

from pandas.core.resample import f
from stock_info.xue_api import ApiXueqiu
from sql_model.query import StockQuery
import pandas as pd
import logging


class AssetCalculator:
    def __init__(self, config={}):
        """
        :param df:index为时间，column为"net_value"的dataframe,基金的净值数据
        """
        # self.df = df
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_etf_info.log',  filemode='a', level=logging.INFO)
        self.is_year = config.get('is_year')
        self.day_10_ago = config.get('day_10_ago')
        self.day_20_ago = config.get('day_20_ago')
        self.day_60_ago = config.get('day_60_ago')
        self.markdown = config.get('markdown')
        self.type = config.get('type')
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.each_api = ApiXueqiu()
        if self.type == 'etf':
            self.set_etf_data()
        elif self.type == 'index':
            self.set_index_data()
        # print(df_data)

    def set_etf_data(self):
        each_query = StockQuery()
        etf_funds = each_query.query_etf()
        self.df_data = pd.DataFrame(etf_funds)

    def set_index_data(self):
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
        self.df_data = pd.DataFrame(stock_list)

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
        if freq == 'M':
            percent_str = date[0:7] + '月份'
        elif (freq == 'Y'):
            percent_str = date[0:4] + '年份'
        elif (freq == 'Q'):
            percent_str = date + '(该季度)'
        elif (freq == 'W'):
            percent_str = date + '(该周)'
        return percent_str

    def calculate(self):
        for index, etf_item in self.df_data.iterrows():
            symbol = etf_item.get('market').upper() + etf_item.get('code')
            name = etf_item.get('name')
            percent = self.calculate_period_percent(
                symbol, name)
            self.df_data.at[index, 'percent'] = percent
        self.df_data.dropna(subset=['percent'], inplace=True)
        self.df_data.sort_values(
            by='percent', inplace=True, ascending=False, ignore_index=True)
        return self

    def calculate_period_percent(self, symbol, name, default_params=None, is_format_str=False):
        params = default_params if default_params else self.params
        begin_date = params.get('begin_date')
        end_date = params.get('end_date')
        period = params.get('period')
        df_stock_kline_info = self.each_api.get_kline_info(
            symbol, begin_date, end_date, period)
        if df_stock_kline_info.empty:
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
            if percent and is_format_str:
                percent = str(percent) + '%'
            return percent
        except:
            print(symbol, df_stock_kline_info)
            pass

    def format_dataframe(self, init_df=None):
        df = self.df_data
        if isinstance(init_df, pd.DataFrame) and not init_df.empty:
            df = init_df.copy()
        if self.day_10_ago:
            ts = pd.Timestamp(self.date).timestamp()
            self.day_10_ago_date = datetime.fromtimestamp(
                ts - 10 * 24 * 3600).strftime("%Y-%m-%d")
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('market').upper() + etf_item.get('code')
                name = etf_item.get('name')
                day_20_ago_params = {
                    'period': 'day',
                    'begin_date': self.day_10_ago_date,
                    'end_date': self.date,
                }
                df.at[index, 'day_10_ago_percent'] = self.calculate_period_percent(
                    symbol, name, day_20_ago_params, True)
        if self.day_20_ago:
            ts = pd.Timestamp(self.date).timestamp()
            self.day_20_ago_date = datetime.fromtimestamp(
                ts - 20 * 24 * 3600).strftime("%Y-%m-%d")
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('market').upper() + etf_item.get('code')
                name = etf_item.get('name')
                day_20_ago_params = {
                    'period': 'day',
                    'begin_date': self.day_20_ago_date,
                    'end_date': self.date,
                }
                df.at[index, 'day_20_ago_percent'] = self.calculate_period_percent(
                    symbol, name, day_20_ago_params, True)
        if self.day_60_ago:
            ts = pd.Timestamp(self.date).timestamp()
            self.day_60_ago_date = datetime.fromtimestamp(
                ts - 60 * 24 * 3600).strftime("%Y-%m-%d")
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('market').upper() + etf_item.get('code')
                name = etf_item.get('name')
                day_60_ago_params = {
                    'period': 'day',
                    'begin_date': self.day_60_ago_date,
                    'end_date': self.date,
                }
                df.at[index, 'day_60_ago_percent'] = self.calculate_period_percent(
                    symbol, name, day_60_ago_params, True)
        if self.is_year:
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('market').upper() + etf_item.get('code')
                name = etf_item.get('name')
                year_params = self.format_freq_params()
                df.at[index, 'year_percent'] = self.calculate_period_percent(
                    symbol, name, year_params, True)
        df['percent'] = df['percent'].astype(str) + '%'
        df.drop('market', axis=1, inplace=True)
        columns = {
            "code": "证券代码",
            "name": "证券名称",
            'percent': self.get_percent_column_name(self.date, self.freq),
            'day_10_ago_percent': '近10天',
            'day_20_ago_percent': '近20天',
            'day_60_ago_percent': '近60天',
            'year_percent': self.get_percent_column_name(self.date, 'Y'),
        }
        df.rename(columns=columns, inplace=True)
        df.set_index("证券名称", inplace=True)
        if self.markdown:
            print(df.to_markdown())
        else:
            print(df)

    def ouputRank(self, count=5):
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
    # stock_period_gain_calculate()
    etf_gain = AssetCalculator({
        'is_year': 1,
        'type': 'etf',  # index or etf
        'markdown': 1
    })
    etf_gain.format_params({
        'date': '2022-01-18',
        'freq': 'D',
    }).calculate().output()
