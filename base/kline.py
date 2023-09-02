import pandas as pd
from api.xue_api import ApiXueqiu
import logging
from utils.index import timeit
from  .__init__ import *
from datetime import datetime

save_begin_date = '2017-06-29'
save_end_date = '2023-04-28'
xueqiu_api = None

archive_dir = "./archive_data/csv/"

class Kline:
    def __init__(self, symbol, name):
        self.date = None
        self.freq = 'D'
        global xueqiu_api
        if xueqiu_api == None:
            xueqiu_api = ApiXueqiu()
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

    def get_kline_data(self, *, is_slice = False):
        begin_date = self.params.get('begin_date')
        end_date = self.params.get('end_date')
        type = self.params.get('type')
        count = self.params.get('count')
        period = self.params.get('period')
        is_in_date = False
        payload = dict()
        in_date_file = archive_dir + self.symbol + '_'  + save_begin_date + '_' + save_end_date + '_' + period + '.csv'
        if end_date:
            filename = archive_dir + self.symbol + '_'  + begin_date + '_' + end_date + '_' + period + '.csv'
            is_in_date = pd.Timestamp(end_date).timestamp() <= pd.Timestamp(save_end_date).timestamp() and pd.Timestamp(begin_date).timestamp() >= pd.Timestamp(save_begin_date).timestamp()
            payload['end'] = end_date
        elif type and count:
            filename = archive_dir + self.symbol + '_'  + begin_date + '_' + type + '_' + str(count) + '_' + period + '.csv'
            payload['count'] = count
        is_exist_file = os.path.exists(filename)
        if is_exist_file or (is_in_date and os.path.exists(in_date_file)):
            cur_file_name =  filename if is_exist_file else in_date_file
            df_stock_kline_info = pd.read_csv(cur_file_name, index_col=['date'], parse_dates=['date'])
            # print("df_stock_kline_info", df_stock_kline_info)
            try:
                if end_date:
                    pd_start_timestamp = df_stock_kline_info.index[0]
                    pd_begin_timestamp = pd.Timestamp(begin_date)
                    pd_save_begin_timestamp = pd.Timestamp(save_begin_date)
                    pd_final_timestamp = df_stock_kline_info.index[-1]
                    pd_end_timestamp = pd.Timestamp(end_date)
                    td = (pd_final_timestamp - pd_end_timestamp).total_seconds()
                    #已存在的数据的开始时间小于开始时间,特殊处理周末
                    start_td = (pd_start_timestamp - pd_begin_timestamp).total_seconds()
                    start_weekend = pd_begin_timestamp.weekday()
                    max_td = 0
                    is_begin_valid = False
                    is_large_save_begin = pd_begin_timestamp  > pd_save_begin_timestamp
                    # 周六
                    if start_weekend == 5:
                        max_td = 2 * 24 * 60 * 60
                    # 周日
                    elif start_weekend == 6:
                        max_td = 1 * 24 * 60 * 60
                    if max_td >= start_td:
                        is_begin_valid = True
                    weekend = pd_end_timestamp.weekday()
                    max_td = 0
                    # 周六
                    if weekend == 5:
                        max_td = -1 * 24 * 60 * 60
                    # 周日
                    elif weekend == 6:
                        max_td = -2 * 24 * 60 * 60
                    is_end_valid = td >= max_td
                    if is_end_valid and (is_begin_valid or is_large_save_begin):
                        new_end_date_sec = pd_end_timestamp.timestamp() + max_td
                        new_end_date  = datetime.fromtimestamp(new_end_date_sec).strftime("%Y-%m-%d")
                        if is_slice :
                            self.df_kline = df_stock_kline_info.loc[begin_date:new_end_date]
                        else:
                            self.df_kline = df_stock_kline_info # 为了获取过去均线,暂时不做截取
                    else:
                        self.df_kline = self.each_api.get_kline_info(self.symbol, begin_date, period, type = type, rest = payload)

                else:
                    self.df_kline = df_stock_kline_info
                return
            except:
                print('date', begin_date, end_date,'匹配不到数据')
                payload['end'] = end_date
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
        init_data = df_stock_kline_info
        df_stock_kline_info['date'] = df_stock_kline_info.index.date
        df_stock_kline_info = df_stock_kline_info.set_index('date')
        df_stock_kline_info.to_csv(filename)
        self.df_kline = init_data
    
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

    def calculate_ma(self):
        self.df_kline['ma5'] = self.df_kline['close'].rolling(
            5).mean().round(2)
        self.df_kline['ma10'] = self.df_kline['close'].rolling(
            10).mean().round(2)
        self.df_kline['ma20'] = self.df_kline['close'].rolling(
            20).mean().round(2)
        self.df_kline['ma30'] = self.df_kline['close'].rolling(
            30).mean().round(2)
        self.df_kline['ma60'] = self.df_kline['close'].rolling(
            60).mean().round(2)
        self.df_kline['ma120'] = self.df_kline['close'].rolling(
            120).mean().round(2)

    def calculate_mv(self):
        self.df_kline['mv4'] = self.df_kline['volume'].rolling(
            4).mean().round(2)
        self.df_kline['mv8'] = self.df_kline['volume'].rolling(
            8).mean().round(2)
        self.df_kline['mv20'] = self.df_kline['volume'].rolling(
            20).mean().round(2)
        self.df_kline['mv30'] = self.df_kline['volume'].rolling(
            30).mean().round(2)
        
        self.df_kline['max_mv4'] = self.df_kline['volume'].rolling(4, min_periods=1).max()
        self.df_kline['max_percent4'] = self.df_kline['percent'].rolling(4, min_periods=1).max()
        

    def calculate_drawdown(self, size = 100):
        day_cnt = size
        max_close_key = 'max_close_'+str(day_cnt)
        min_close_key = 'min_close_'+str(day_cnt)
        dd_key = 'dd_'+str(day_cnt)
        max_dd_key = 'max_dd_'+str(day_cnt)
        # 计算每一天的最近最大回撤幅度, min_periods一定要设置为1, 否则会出现max_dd_key出现问题
        self.df_kline[min_close_key] = self.df_kline['close'].rolling(day_cnt, min_periods=1).min()
        # self.df_kline[max_close_key] = self.df_kline['close'].expanding(min_periods=day_cnt).max()
        self.df_kline[max_close_key] = self.df_kline['close'].rolling(day_cnt, min_periods=1).max()
        self.df_kline[dd_key] = ((self.df_kline['close'] - self.df_kline[max_close_key]) / self.df_kline[max_close_key]).round(4)
        self.df_kline[max_dd_key] = self.df_kline[dd_key].rolling(
            day_cnt, min_periods=1).min().round(4)
        # for debugger
        # if self.symbol == 'SZ159855':
        #     print(self.df_kline[[max_close_key, min_close_key, dd_key, max_dd_key, 'diff']])
        #     self.df_kline.to_csv("data/stock_kline-SZ159855.csv", header=True, index=True)

        # self.df_kline['max_close'] = self.df_kline['close'].rolling(
        #     len(self.df_kline), min_periods=1).max()
        # self.df_kline['min_close'] = self.df_kline['close'].rolling(
        #     len(self.df_kline), min_periods=1).min()
        # self.df_kline['dd'] = ((
        #     self.df_kline['close'] - self.df_kline['max_close']) / self.df_kline['max_close']).round(4)
        # self.df_kline['max_dd'] = self.df_kline['dd'].rolling(
        #     len(self.df_kline), min_periods=1).min().round(4)
    def calculate_increase(self):
        # 过去20天的最低价
        self.df_kline['min_price_20'] = self.df_kline['close'].rolling(20, min_periods=1).min().round(4)

        # 计算每一天的涨幅相对低点的涨幅
        self.df_kline['increase_20'] = (
            (self.df_kline['close'] - self.df_kline['min_price_20']) / self.df_kline['min_price_20']).round(4)
        self.df_kline['min_price_10'] = self.df_kline['close'].rolling(10, min_periods=1).min().round(4)

        # 计算每一天的涨幅相对低点的涨幅
        self.df_kline['increase_10'] = (
            (self.df_kline['close'] - self.df_kline['min_price_10']) / self.df_kline['min_price_10']).round(4)
