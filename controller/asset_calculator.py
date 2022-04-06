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

from sql_model.query import StockQuery
from base.kline import Kline
import pandas as pd
from utils.constant import const 
import logging

class AssetCalculator:

    def __init__(self, config={}):
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_etf_info.log',  filemode='a', level=logging.INFO)
        for ago in const.before_list:
            ago_key = 'day_' + str(ago) + '_before'
            # self[ago_key] = config.get(ago_key)
            setattr(self, ago_key, config.get(ago_key))
        self.is_year = config.get('is_year')
        self.markdown = config.get('markdown')
        self.count = config.get('count') if config.get('count') else 5
        self.__type = config.get('type')
        self.__freq = 'D'
        self.__date = datetime.now().strftime("%Y-%m-%d")
        self.__before_day = None
        self.filter_found_date = config.get('filter_found_date')
        self.__init_data()

    def __init_data(self):
        if self.__type == 'etf':
            each_query = StockQuery()
            etf_funds = each_query.query_etf(self.filter_found_date)
            self.df_data = pd.DataFrame(etf_funds)
        elif self.__type == 'index':
            self.df_data = pd.DataFrame(const.index_stock_list)

    def set_date(self, params):
        date = params.get('date') if params.get('date') else self.__date
        freq = params.get('freq') if params.get('freq') else self.__freq
        before_day = params.get('before_day')
        begin_date = None
        if before_day:
            ts = pd.Timestamp(date).timestamp()
            begin_date = datetime.fromtimestamp(
                ts - (before_day + 30) * 24 * 3600).strftime("%Y-%m-%d")
            end_date = date
            self.__before_day = before_day
        elif freq:
            res = pd.Timestamp(date).to_period(freq=freq)
            begin_date = res.start_time.strftime('%Y-%m-%d')
            end_date = res.end_time.strftime('%Y-%m-%d')
        params = {
            **params,
            'date': date,
            'begin_date': begin_date,
            'end_date': end_date,
        }
        self.__date = date
        self.__freq = freq
        self.params = params
        return self

    def get_column_label(self, date, freq):
        label = date
        params = self.params
        begin_date = params.get('begin_date')
        end_date = params.get('end_date')
        if freq == 'M':
            label = date[0:7] + '月份'
        elif (freq == 'Y'):
            label = date[0:4] + '年份以来'
        elif (freq == 'Q'):
            label = date + '(该季度)'
        elif (freq == 'W'):
            label = "本周" + "("+begin_date + '一' + end_date + ')'
        return label

    def calculate(self):
        for index, etf_item in self.df_data.iterrows():
            symbol = etf_item.get('market').upper() + etf_item.get('code')
            name = etf_item.get('name')
            kline_res = self.calculate_kline(
                symbol, name, None, False, False)
            self.df_data.at[index, 'percent'] = kline_res[0]
            self.df_data.at[index, 'avg_volume'] = kline_res[1]
            self.df_data.at[index, 'avg_amount'] = kline_res[2]
        self.df_data.dropna(subset=['percent'], inplace=True)
        self.df_data.sort_values(
            by='percent', inplace=True, ascending=False, ignore_index=True)
        return self

    def calculate_kline(self, symbol, name, default_params=None, is_format_str=False, is_only_percent=False):
        params = default_params if default_params else self.params
        kline = Kline(symbol, name)
        kline.format_params(params)
        kline.get_kline_data()
        percent = kline.calculate_period_percent(self.__before_day, is_format_str)
        if(is_only_percent):
            return [percent]
        mean_volume = kline.get_past_mean('volume', 5)
        mean_amount = kline.get_past_mean('amount', 5)
        return [percent, mean_volume, mean_amount]

    def affix_date_percent_date(self, ago, etf_item):
        symbol = etf_item.get('market').upper() + etf_item.get('code')
        name = etf_item.get('name')
        ts = pd.Timestamp(self.__date).timestamp()
        begin_date = datetime.fromtimestamp(
            ts - ago * 24 * 3600).strftime("%Y-%m-%d")
        ago_params = {
            'period': 'day',
            'begin_date': begin_date,
            'end_date': self.__date,
        }
        return self.calculate_kline(symbol, name, ago_params, True, True)[0]

    def append_before_data(self, init_df=None):
        df = self.df_data
        if isinstance(init_df, pd.DataFrame) and not init_df.empty:
            df = init_df.copy()
        columns = {
            "code": "证券代码",
            "name": "证券名称",
            'percent': self.get_column_label(self.__date, self.__freq),
            'year_percent': self.get_column_label(self.__date, 'Y'),
        }
        for ago in before_list:
            if getattr(self, "day_" + str(ago) + "_before"):
                ago_key = 'day_' + str(ago) + '_before_percent'
                columns[ago_key] = '近' + str(ago) + '天'
                for index, etf_item in df.iterrows():
                    df.at[index, ago_key] = self.affix_date_percent_date(
                        ago, etf_item)
        if self.is_year:
            for index, etf_item in df.iterrows():
                symbol = etf_item.get('market').upper() + etf_item.get('code')
                name = etf_item.get('name')
                ts = pd.Timestamp(self.__date)
                res = ts.to_period(freq='Y')
                begin_date = res.start_time.strftime('%Y-%m-%d')
                end_date = res.end_time.strftime('%Y-%m-%d')
                year_params = {
                    'period': 'day',
                    'begin_date': begin_date,
                    'end_date': end_date,
                }
                df.at[index, 'year_percent'] = self.calculate_kline(
                    symbol, name, year_params, True, True)[0]
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
        self.append_before_data(top_df)
        print('跌幅前{}名为:'.format(count))
        self.append_before_data(last_df)

    def output(self):
        if self.__type == 'etf':
            self.ouputRank()
        elif self.__type == 'index':
            self.append_before_data()


if __name__ == '__main__':
    # asset_calculator()
    etf_gain = AssetCalculator({
        'is_year': 1,
        'type': 'etf',  # index or etf
        'markdown': 1
    })
    etf_gain.set_date({
        'date': '2022-01-18',
        'freq': 'D',
    }).calculate().output()
