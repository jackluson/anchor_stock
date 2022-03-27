import pandas as pd
from stock_info.xue_api import ApiXueqiu
import logging


class Kline:
    def __init__(self, symbol, name):
        self.date = None
        self.freq = 'D'
        self.each_api = ApiXueqiu()
        self.symbol = symbol
        self.name = name
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_kline_info.log',  filemode='a', level=logging.INFO)

    def format_params(self, params, is_self=True):
        date = params.get('date') if params.get('date') else self.date
        freq = self.freq
        if date:
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
            self.freq = freq
            self.params = params
            return self
        return params

    def get_kline_data(self):
        begin_date = self.params.get('begin_date')
        end_date = self.params.get('end_date')
        period = self.params.get('period')
        df_stock_kline_info = self.each_api.get_kline_info(
            self.symbol, begin_date, end_date, period)
        if df_stock_kline_info.empty:
            line = f'该ETF{self.name}--{self.symbol}没有查到数据'
            logging.info(line)
            self.df_kline = df_stock_kline_info
            return
        df_stock_kline_info['date'] = df_stock_kline_info.index.date
        df_stock_kline_info = df_stock_kline_info.set_index('date')
        self.df_kline = df_stock_kline_info

    def calculate_period_percent(self, is_format_str=False):
        try:
            # percent = df_stock_kline_info.loc[pd.Timestamp.date(
            #     datetime.fromisoformat(tail_date))]['percent']
            first_net = self.df_kline.loc[self.df_kline.index[0]]['close']
            first_chg = self.df_kline.loc[self.df_kline.index[0]]['chg']
            first_net = first_net - first_chg
            last_net = self.df_kline.loc[self.df_kline.index[-1]]['close']
            percent = round((last_net - first_net)/first_net*100, 2)
            if percent and is_format_str:
                percent = str(percent) + '%'
            return percent
        except:
            print(self.df_kline)
