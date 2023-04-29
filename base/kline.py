import pandas as pd
from api.xue_api import ApiXueqiu
import logging
from  .__init__ import *

save_begin_date = '2011-12-30'
save_end_date = '2022-04-01'

xueqiu_api = ApiXueqiu()
class Kline:
    def __init__(self, symbol, name):
        self.date = None
        self.freq = 'D'
        self.each_api = xueqiu_api
        self.symbol = symbol
        self.name = name
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                            filename='log/stock_kline_info.log',  filemode='a', level=logging.INFO)

    def format_params(self, params, is_self=True):
        date = params.get('date') if params.get('date') else self.date
        freq = params.get('freq')
        params = {
            'period': 'day',
            **params,
        }
        if date and freq:
            self.date = date
            ts = pd.Timestamp(date)
            res = ts.to_period(freq=freq)
            begin_date = res.start_time.strftime('%Y-%m-%d')
            end_date = res.end_time.strftime('%Y-%m-%d')
            params = {
                **params,
                'begin_date': begin_date,
                'end_date': end_date,
            }

        if is_self:
            self.params = params
            return self
        return params

    def get_kline_data(self):
        begin_date = self.params.get('begin_date')
        end_date = self.params.get('end_date')
        type = self.params.get('type')
        count = self.params.get('count')
        period = self.params.get('period')
        is_in_date = False
        payload = dict()
        if end_date:
            filename = "./archive_data/csv/" + self.symbol + '_'  + begin_date + '_' + end_date + '_' + period + '.csv'
            is_in_date = pd.Timestamp(end_date).timestamp() <= pd.Timestamp(end_date).timestamp() and pd.Timestamp(begin_date).timestamp() >= pd.Timestamp(begin_date).timestamp()
            payload['end'] = end_date
        elif type and count:
            filename = "./archive_data/csv/" + self.symbol + '_'  + begin_date + '_' + type + '_' + str(count) + '_' + period + '.csv'
            payload['count'] = count
        if os.path.exists(filename):
            df_stock_kline_info = pd.read_csv(filename, index_col=['date'], parse_dates=['date'])
            # print("df_stock_kline_info", df_stock_kline_info)
            try:
                if end_date:
                    final_timestamp = df_stock_kline_info.index[-1]
                    end_timestamp = pd.Timestamp(end_date)
                    if final_timestamp >= end_timestamp:
                        self.df_kline = df_stock_kline_info.loc[begin_date:end_date]
                    else:
                        self.df_kline = self.each_api.get_kline_info(self.symbol, begin_date, period, type = type, rest = payload)

                else:
                    self.df_kline = df_stock_kline_info
                return
            except:
                print('date', begin_date, end_date,'匹配不到数据')
                df_stock_kline_info = self.each_api.get_kline_info(
                self.symbol, begin_date, period, type = type, rest = payload)
        else:
            line = f'该ETF请求{self.name}--{self.symbol}kline数据:--{begin_date}--{end_date}'
            logging.info(line)
            df_stock_kline_info = self.each_api.get_kline_info(
                self.symbol, begin_date, period, type = type, rest = payload)
        if df_stock_kline_info.empty:
            line = f'该ETF{self.name}--{self.symbol}没有查到数据--{begin_date}--{end_date}'
            logging.info(line)
            self.df_kline = df_stock_kline_info
            return
        df_stock_kline_info['date'] = df_stock_kline_info.index.date
        df_stock_kline_info = df_stock_kline_info.set_index('date')
        df_stock_kline_info.to_csv(filename)
        self.df_kline = df_stock_kline_info

    def calculate_period_percent(self, before_day_count=None, is_format_str=False):
        if(self.df_kline.empty):
            print(self.symbol, 'K线数据为空:', self.df_kline)
            return None
        # percent = df_stock_kline_info.loc[pd.Timestamp.date(
        #     datetime.fromisoformat(tail_date))]['percent']
        start_net = self.df_kline.loc[self.df_kline.index[0]]['close']
        start_chg = self.df_kline.loc[self.df_kline.index[0]]['chg']
        if before_day_count and len(self.df_kline) > before_day_count:
            start_net = self.df_kline.iloc[-(before_day_count)]['close']
            start_chg = self.df_kline.iloc[-(before_day_count)]['chg']
        start_net = start_net - start_chg
        last_net = self.df_kline.loc[self.df_kline.index[-1]]['close']
        percent = round((last_net - start_net)/start_net*100, 2)
        if percent and is_format_str:
            percent = str(percent) + '%'
        return percent

    def get_past_mean(self, dimension, before_days=5, round_num=3):
        if self.df_kline.empty:
            return None
        return self.df_kline[dimension].tail(before_days).mean().round(round_num)
