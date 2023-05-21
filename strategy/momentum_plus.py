'''
Desc:
File: /momentum copy.py
File Created: Sunday, 30th April 2023 5:47:53 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import math
import random

import logging
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from base.kline import Kline
from strategy.base_strategy import BaseStrategy
from calculate.correlated import Correlator
from controller.asset_calculator import AssetCalculator
import mplcursors

# %matplotlib inline

def get_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file, 'a')
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

class MomentumStrategyPlus(BaseStrategy):
    holdlist = []
    sell_list = []  # 卖出列表
    max_hold_count = 4  # 最大可同时买入的ETF数量
    per = 1 / max_hold_count  # 每只ETF买入的仓位
    sell_win_count = 0
    sell_loss_count = 0
    record_percents = []
    daily_percent = 0
    begin_date = None
    end_date = None
    is_predict = False
    similarity_threshold = 0.8
    open_drawdown_filter = True
    follow_trend = False
    drawdown_percent = -0.2
    drawdown_size = 240
    rise_percent = 0.2
    open_filter_similarity = True
    min_avg_volume = 1.0e7  # 最小交易量10000000
    type = 'etf'
    def __init__(self, *, rise_percent=0.2, open_filter_similarity=True, open_drawdown_filter=True, follow_trend=False, drawdown_percent=-0.2, drawdown_size=240, min_avg_volume = 1.0e7, lock=None, type="etf"):
        # self.lock = lock
        # --------params--------
        self.rise_percent = rise_percent  # 突破涨幅, 单位%
        self.open_filter_similarity = open_filter_similarity
        self.min_drawdown = -0.05  # 回撤涨幅
        self.type = type
        # self.ma_day = 4  # 低于x天均线
        # self.sell_second_ma_day = 9  # 低于多少日均线卖出
        self.threshold_day = 10 # 亏损可卖出天数门槛值

        self.before_found_day = 180  # 至少成立多少天etf
        self.min_avg_volume = min_avg_volume  # 最小交易量10000000
        self.open_drawdown_filter = open_drawdown_filter
        self.follow_trend = follow_trend
        self.drawdown_size = drawdown_size
        self.drawdown_percent = drawdown_percent
    def back_test(self, *, begin_date, end_date):
        log_file_name = 'log/' + begin_date + '至' + end_date + '_momentum_plus.log'
        # super().__init__(is_save_log, log_file_name)
        self.logger = get_logger(log_file_name, log_file_name)
        benchmark = Kline('SH000300', '沪深300')
        benchmark_500 = Kline('SH000905', '中证500')
        benchmark_1000 = Kline('SH000852', '中证1000')
        self.begin_date = begin_date
        self.end_date = end_date
        benchmark.format_params({
            'period': 'day',
            'begin_date': begin_date,
            'end_date': end_date,
        })
        benchmark.get_kline_data(is_slice=True)
        benchmark.percent = benchmark.calculate_period_percent()
        self.benchmark = benchmark
        benchmark_500.format_params({
            'period': 'day',
            'begin_date': begin_date,
            'end_date': end_date,
        })
        benchmark_500.get_kline_data(is_slice=True)
        benchmark_500.percent = benchmark_500.calculate_period_percent()
        self.benchmark_500 = benchmark_500
        benchmark_1000.format_params({
            'period': 'day',
            'begin_date': begin_date,
            'end_date': end_date,
        })
        benchmark_1000.get_kline_data(is_slice=True)
        benchmark_1000.percent = benchmark_1000.calculate_period_percent()
        self.benchmark_1000 = benchmark_1000
        self.earn_percent_history = []  # 第一天的默认收益率
        self.collect_data()
        self.traverse()
    def collect_data(self):
        if self.is_predict == False:
            date_params = {
                'begin_date': self.begin_date,
                'end_date': self.end_date,
            }
            ts = pd.Timestamp(self.begin_date).timestamp()
        else:
            date_params = {
                'end_date': self.cur_date,
                'before_day': 360, # 去过去360天的数据,为了算均线,回撤等
            }
            ts = pd.Timestamp(self.cur_date).timestamp()
        filter_found_date = datetime.fromtimestamp(
            ts - self.before_found_day * 24 * 3600).strftime("%Y-%m-%d")
        asset_calculator = AssetCalculator({
            'type': self.type,  # index or etf, bond
            # 'filter_found_date': filter_found_date,
            # 'mean_day': self.ma_day,
            # 'second_mean_day': self.sell_second_ma_day,
        })
        asset_calculator.set_date(date_params)
        asset_calculator.calculate_v2(drawdown_size=self.drawdown_size)
        self.asset_calculator = asset_calculator
    def traverse(self):
        dates = self.benchmark.df_kline.index
        self.dates = dates
        for index in range(1, len(dates)):
            self.cur_date = self.dates[index]
            self.prev_date = self.dates[index - 1]
            # self.logger.info("\n=================traverse_date: %s=====================", self.cur_date)
            self.prepare()
            self.filter()
            self.trade()
            self.compute()
            self.per_day_summary()
        self.serialize()
        return self
    def prepare(self):
        ready_prev_df = []
        ready_df = []
        for index, etf_item in self.asset_calculator.df_data.iterrows():
            code = etf_item.get('code')
            df_kline = self.asset_calculator.kline_list_map.get(code)
            if len(df_kline) == 0:
                continue
            # print(df_kline)
            if self.is_predict == False and self.prev_date in df_kline.index:
                cur_kline = df_kline.loc[self.prev_date] #前一天数据计算
                ready_prev_df.append(cur_kline)
            if self.cur_date in df_kline.index:
                cur_kline = df_kline.loc[self.cur_date] #当天数据计算
                ready_df.append(cur_kline)
        ready_prev_df = pd.DataFrame(ready_prev_df)
        if len(ready_prev_df) > 0:
            ready_prev_df.set_index('code', inplace=True)
        ready_df = pd.DataFrame(ready_df)
        if len(ready_df) > 0:
            ready_df.set_index('code', inplace=True)
        self.ready_prev_df = ready_prev_df
        self.ready_df = ready_df
    def filter(self):
        all_candidate = self.ready_df if self.is_predict else self.ready_prev_df
        candidate = all_candidate.loc[all_candidate['percent'] > self.rise_percent]
        candidate = candidate.loc[candidate['volume'] > self.min_avg_volume]
        candidate = candidate.loc[candidate['volume'] > candidate['mv4']] #还是加上这个胜率高,收益也好
        candidate = candidate.loc[candidate['mv4'] > candidate['mv8']] #这个也要加上,这个胜率高,收益也好
        candidate = candidate.loc[candidate['close'] > candidate['ma5']] # 这个影响因素不大
        candidate = candidate.loc[candidate['close'] > candidate['ma10']] # 这个影响很大,如果改成ma5> ma10
        # candidate = candidate.loc[candidate['ma5'] > candidate['ma10']]
        # candidate = candidate.loc[candidate['close'] > candidate['open']] # 筛选这个好一些
        # candidate = candidate.loc[candidate['ma10'] > candidate['ma20']] # 波动有大一些,但最终收益率差不多
        if self.open_drawdown_filter:
            #右侧交易
            drawdown_size = self.drawdown_size
            max_dd_key = 'max_dd_'+str(drawdown_size)
            dd_key = 'dd_'+str(drawdown_size)
            candidate = candidate.loc[candidate[max_dd_key] < self.drawdown_percent] # 过去x天回撤大于20%, 加了这个指标之后,类似右侧交易,抄底, 涨幅和胜率有显著提高, 改了-0.3之后,收益率提高一些,但胜率下降一些,可见-0.3和-0.2差别不大了,
            if self.follow_trend == False:
                candidate = candidate.loc[candidate[dd_key] < 0] # 这个值为-0.1效果也不好, 作用不大
        candidate = candidate.sort_values(by="amount", ascending=False, ignore_index=True)
        # candidate = candidate.loc[candidate['increase_20'] < 0.2] # 加了这个没有明显影响
        # candidate = candidate.loc[candidate['increase_10'] < 0.1] # 加了这个之后策略涨幅出现明显下降
        # def due_filter(row):
        #     volume_percent = (row.volume - row.mv4) / row.mv4
        #     return volume_percent > 0.2
        # candidate = candidate[candidate.apply(due_filter, axis=1)]
        # candidate.to_csv("data/stock_kline.csv", header=True, index=True)
        if self.is_predict == True:
            print('=====================', self.cur_date, '=====================')
            print(candidate)
            print('=====================', self.cur_date, '=====================')
        if len(candidate) > 0 and self.open_filter_similarity:
            prev_len = len(candidate)
            # print(candidate['name'])
            correlator = Correlator(self.cur_date if self.is_predict else self.prev_date.strftime("%Y-%m-%d"))
            compares = candidate
            holdlist = self.holdlist
            correlator.prepare_compare(compares, holdlist).correlate()
            if self.is_predict:
                print(correlator.res_compare)
            threshold = self.similarity_threshold # 相似度大于0.8过滤
            df_similarity = correlator.filter_near_similarity(threshold)
            new_candidate = []
            for index, item in df_similarity.iterrows():
                code = index[-7: -1]
                is_continue = False
                for item in self.holdlist:
                    if item['code'] == code:
                        is_continue = True
                        break
                if is_continue:
                    continue
                new_candidate.append({
                    **all_candidate.loc[code].to_dict(),
                    'code': code
                })
            candidate = pd.DataFrame(new_candidate)
            if len(candidate) > 0:
                # print(candidate['name'])
                candidate.set_index('code', inplace=True)
            new_len = len(candidate)
            print(f'=====================过滤前数量:{ prev_len }, 过滤后数量:{new_len}, 持仓数量: {len(self.holdlist)}')
        if self.is_predict == True and self.open_filter_similarity == True:
            print(candidate)
        self.candidate = candidate
    def trade(self):
        self.sell_or_keep()
        self.buy()
    def compute(self):
        self.daily_percent = 0
        for item in self.holdlist:
            if item['code'] in self.ready_df.index:
                self.compute_one(item)
        self.record_percents.append({
            'date': self.cur_date,
            'percent': self.daily_percent,
        })
        percent_300 = self.benchmark.df_kline.loc[self.cur_date]['percent']
        percent_500 = self.benchmark_500.df_kline.loc[self.cur_date]['percent']
        percent_1000 = self.benchmark_1000.df_kline.loc[self.cur_date]['percent']
        self.logger.warn(
            f"[汇总] -- 时间:{self.cur_date}, percent:{round(self.daily_percent * 100, 2)}%, 300_percent:{percent_300}%,percent_500:{percent_500}%,percent_1000:{percent_1000}%, 当前持仓数量:{len(self.holdlist)}")
    def compute_one(self, item):
        latest_item = self.ready_df.loc[item['code']]
        cur_price = latest_item['close']
        last_price = round(item['last_price'], 3)
        percent = (cur_price - last_price) / last_price

        self.daily_percent = round(
            self.daily_percent + percent * item['ratio'], 4)
        for i in range(len(self.holdlist)):
            if self.holdlist[i]['code'] == item['code']:
                self.holdlist[i] = {
                    **self.holdlist[i],
                    'last_price': cur_price,
                }
    def buy(self):
        candidate = self.candidate
        for index, item in candidate.head(self.max_hold_count).iterrows():
            code = index
            is_continue = False
            if is_continue:
                continue
            if len(self.holdlist) == self.max_hold_count:
                break
            if code in self.ready_df.index: # 可交易
                self.buyone(code)
    def buyone(self, code):
        lastest_buy_item = self.ready_df.loc[code]
        pre_buy_item = self.ready_prev_df.loc[code]
        #右侧交易
        day_cnt = self.drawdown_size
        max_dd_key = 'max_dd_'+str(day_cnt)
        dd_key = 'dd_'+str(day_cnt)
        buy_price = round(lastest_buy_item['open'], 3) # 开盘价买入
        hold_item = {
            'name': lastest_buy_item['name'],
            'code': code,
            'symbol': lastest_buy_item['symbol'],
            'buy_price': buy_price,
            'buy_date': self.cur_date,
            'last_price': buy_price,
            'ratio': self.per,
            dd_key: pre_buy_item[dd_key],
            max_dd_key: pre_buy_item[max_dd_key],
        }
        self.holdlist.append(hold_item)
        raise_volume_percent = round((pre_buy_item['volume'] - pre_buy_item['mv4']) / pre_buy_item['mv4'] * 100, 2)
        self.logger.info(f"[buy] -- 买入时间:{hold_item['buy_date']}, name:{hold_item['name']}, code:{hold_item['code']}, 买入价格:{hold_item['buy_price']},前天涨幅:{pre_buy_item['percent']}%, 前天交易量:{pre_buy_item['volume']},当天涨幅:{lastest_buy_item['percent']}%, 前天交易量:{lastest_buy_item['volume']}, 相对于五日平均交易量涨幅: {raise_volume_percent}%")
        self.logger.info(f"[buy] -- {max_dd_key}:{pre_buy_item[max_dd_key]}, {dd_key}:{pre_buy_item[dd_key]}")
    def check_should_sell(self, item):
        code = item.get('code')
        kline_data = self.ready_df if self.is_predict else self.ready_prev_df
        if code not in kline_data.index:
            return False
        target_data = kline_data.loc[code]
        should_sell_price = target_data['close'] < target_data['ma5'] and (self.candidate_count > 0 or target_data['ma5'] < target_data['ma10']) # 如果有候选股，放松卖出价格条件, 此外如果改成close < ma10,影响也很大
        # if should_sell_price and self.candidate_count > 0:
        #     return True
        cur_date = self.cur_date
        buy_date = item['buy_date']
        if type(buy_date) == str:
            buy_date = pd.Timestamp(buy_date)
        if type(cur_date) == str:
            cur_date = pd.Timestamp(cur_date)
        hold_days = (cur_date - buy_date).days
        drawdown = round((target_data['close'] - item['buy_price']) / item['buy_price'], 3)
        volume_percent = (target_data['volume'] - target_data['mv4']) / target_data['mv4']
        is_scale_volume = volume_percent > 0.5 and target_data['percent'] <= -2 # 是否放量大跌
        if is_scale_volume:
            self.logger.info(f"[放量大跌] {item['name']},{code}, {target_data['percent']}, {should_sell_price}")
        is_meet_drawdown = drawdown > 0 or drawdown < self.min_drawdown
        is_meet_hold_day = hold_days > self.threshold_day
        # should_sell_price_5 = target_data['close'] < target_data['ma5']
        # if should_sell_price_5 and is_scale_volume: #低于五日均线并且放量大跌
        #     return True
        # should_sell_volume = target_data['volume'] < target_data['mv4'] and target_data['volume'] < target_data['mv10'] and target_data['mv4'] < target_data['mv10']
        return should_sell_price and (is_scale_volume or is_meet_hold_day or is_meet_drawdown)
    def sell_or_keep(self):
        sell_list = []
        keep_list = []
        self.candidate_count = len(self.candidate)
        for hold_item in self.holdlist:
            should_sell = self.check_should_sell(hold_item)
            if should_sell:
                self.candidate_count = self.candidate_count - 1
                sell_list.append(hold_item)
            else:
                keep_list.append(hold_item)
        if self.is_predict:
            if len(sell_list) > 0:
                print(f"====================={self.cur_date}卖出列表:{len(sell_list)}=====================")
                print(sell_list)
            if len(keep_list) > 0:
                print(f"====================={self.cur_date}保留列表:{len(keep_list)}=====================")
                print(keep_list)
            return
        self.sell_list = sell_list
        self.keep_list = keep_list
        for item in sell_list:
                self.sellone(item)
    def sellone(self, item):
        ready_sell_item = self.ready_df.loc[item['code']]
        sell_item = {
            **item,
            'sell_price': round(ready_sell_item['open'], 3), #以开盘价
            # 'sell_price': round(ready_sell_item['close'], 3), #前一天的收盘价,后面可以去当天随机价
            'sell_date': self.cur_date,
        }
        for i in range(len(self.holdlist)):
            if self.holdlist[i]['code'] == sell_item['code']:
                del self.holdlist[i]
                break
        percent = round(
            (sell_item['sell_price'] - sell_item['buy_price']) / sell_item['buy_price'] * 100, 2)
        if percent > 0:
            self.sell_win_count = self.sell_win_count + 1
        else:
            self.sell_loss_count = self.sell_loss_count + 1

        date_format = '%Y-%m-%d'  # 日期格式
        sell_date = sell_item['sell_date']
        buy_date = sell_item['buy_date']
        hold_days = (sell_date - buy_date).days
        self.logger.info(
            f"[sell] -- 卖出时间:{sell_item['sell_date'].strftime(date_format)}, name:{sell_item['name']}, code:{sell_item['code']}, 买出价格:{sell_item['sell_price']}, 买入价格:{sell_item['buy_price']}, 盈亏比例:{percent}%, 买入时间:{sell_item['buy_date'].strftime(date_format)}, 持有天数:{hold_days}")
    def per_day_summary(self):
        self.logger.info(f"====================={self.cur_date}当前持仓数量:{len(self.holdlist)}=====================")
        for row in self.holdlist:
            cur_percent = round(
            (row['last_price'] - row['buy_price']) / row['buy_price'] * 100, 2)
            self.logger.info(f"[keep] name:{row['name']}, code:{row['code']}, buy_price:{row['buy_price']}, latest price:{row['last_price']}, percent:{cur_percent}, buy date:{row['buy_date']}")

    def serialize(self):
        self.logger.info("=====================serialize=====================")
        self.plot()
        self.summary()
        return self

    def plot(self):
        # self.lock.acquire()
        plt_data = self.benchmark.df_kline[['percent']]
        plt_data['percent'] = plt_data['percent']/100 + 1
        rename_map = {
            'percent': '300_percent',
        }
        plt_data.rename(columns=rename_map, inplace=True)
        plt_data['500_percent'] = self.benchmark_500.df_kline[['percent']]/100 + 1
        plt_data['1000_percent'] = self.benchmark_1000.df_kline[['percent']]/100 + 1
        plt_data = plt_data.iloc[1:]
        df_percents = pd.DataFrame(self.record_percents).set_index('date')
        df_percents['percent'] = df_percents[['percent']] + 1
        plt_data['strategy_percent'] = df_percents['percent']
        print(plt_data)
        df_cumprod = plt_data.cumprod().round(4)
        df_cumprod.plot(grid=True, figsize=(15, 7))
        mplcursors.cursor(hover=True)
        self.df_cumprod = df_cumprod
        plt.show()
        # self.lock.release()

    def summary(self):
        self.logger.info('策略回撤期间: %s - %s' % (self.begin_date, self.end_date))
        self.logger.info('策略参数:')
        self.logger.info(f"突破涨幅:{self.rise_percent}%; 是否开启右侧交易:{self.open_drawdown_filter}")
        self.logger.info(f"回撤窗口大小:{self.drawdown_size}; 回撤幅度:{self.drawdown_percent * 100}%; 新高追:{self.follow_trend}")
        self.logger.info(f"最小交易量(min_avg_volume):{self.min_avg_volume}; 相似度门槛值:{self.similarity_threshold}")
        self.logger.info(f'亏损可卖出天数阙值(threshold_day):{self.threshold_day}; 最小回撤:{self.min_drawdown * 100}%')
        # self.logger.info('第一天均线天数(ma_day): %d; 第二天均线天数(sell_second_ma_day): %d' % (
        #     self.ma_day, self.sell_second_ma_day))
        trade_count = self.sell_win_count + self.sell_loss_count
        self.logger.warn(
            f"[汇总] -- 卖出胜数:{self.sell_win_count}, 卖出输次:{self.sell_loss_count}, 卖出总次数:{trade_count}, 胜率:{round(self.sell_win_count / trade_count * 100, 2)}%")
        
        df_cumprod = self.df_cumprod
        df_cumprod['max_percent_300'] = df_cumprod['300_percent'].rolling(
            len(df_cumprod), min_periods=1).max()
        df_cumprod['dd_300'] = ((df_cumprod['300_percent'] - df_cumprod['max_percent_300'])/df_cumprod['max_percent_300']).round(4)
        df_cumprod['max_dd_300'] = df_cumprod['dd_300'].rolling(len(df_cumprod), min_periods=1).min().round(4)

        df_cumprod['max_percent_500'] = df_cumprod['500_percent'].rolling(
            len(df_cumprod), min_periods=1).max()
        df_cumprod['dd_500'] = ((df_cumprod['500_percent'] - df_cumprod['max_percent_500'])/df_cumprod['max_percent_500']).round(4)
        df_cumprod['max_dd_500'] = df_cumprod['dd_500'].rolling(len(df_cumprod), min_periods=1).min().round(4)

        df_cumprod['max_percent_1000'] = df_cumprod['1000_percent'].rolling(
            len(df_cumprod), min_periods=1).max()
        df_cumprod['dd_1000'] = ((df_cumprod['1000_percent'] - df_cumprod['max_percent_1000'])/df_cumprod['max_percent_1000']).round(4)
        df_cumprod['max_dd_1000'] = df_cumprod['dd_1000'].rolling(len(df_cumprod), min_periods=1).min().round(4)


        df_cumprod['max_percent'] = df_cumprod['strategy_percent'].rolling(
            len(df_cumprod), min_periods=1).max()
        df_cumprod['dd'] = ((df_cumprod['strategy_percent'] - df_cumprod['max_percent'])/df_cumprod['max_percent']).round(4)
        df_cumprod['max_dd'] = df_cumprod['dd'].rolling(len(df_cumprod), min_periods=1).min().round(4)
        print(df_cumprod)
        max_percent = round((df_cumprod.iloc[-1]['max_percent'] - 1) * 100, 2)  # 最大盈亏比例
        max_dd = round(df_cumprod.iloc[-1]['max_dd'] * 100, 2)  # 最大回撤
        total_percent = round((self.df_cumprod['strategy_percent'].iloc[-1] - 1) * 100, 2)  # 总盈亏比例

        max_percent_300 = round((df_cumprod.iloc[-1]['max_percent_300'] - 1) * 100, 2)  # 最大盈亏比例
        max_dd_300 = round(df_cumprod.iloc[-1]['max_dd_300'] * 100, 2)  # 最大回撤
        total_percent_300 = round((self.df_cumprod['300_percent'].iloc[-1] - 1) * 100, 2)  # 总盈亏比例

        max_percent_500 = round((df_cumprod.iloc[-1]['max_percent_500'] - 1) * 100, 2)  # 最大盈亏比例
        max_dd_500 = round(df_cumprod.iloc[-1]['max_dd_500'] * 100, 2)  # 最大回撤
        total_percent_500 = round((self.df_cumprod['500_percent'].iloc[-1] - 1) * 100, 2)  # 总盈亏比例

        max_percent_1000 = round((df_cumprod.iloc[-1]['max_percent_1000'] - 1) * 100, 2)  # 最大盈亏比例
        max_dd_1000 = round(df_cumprod.iloc[-1]['max_dd_1000'] * 100, 2)  # 最大回撤
        total_percent_1000 = round((self.df_cumprod['1000_percent'].iloc[-1] - 1) * 100, 2)  # 总盈亏比例

        self.logger.warning(f"沪深300期间基准涨幅:{total_percent_300}%, 策略最大涨幅: {max_percent_300}%, 最大回撤: {max_dd_300}%" )
        self.logger.warning(f"中证500期间基准涨幅:{total_percent_500}%, 策略最大涨幅: {max_percent_500}%, 最大回撤: {max_dd_500}%" )
        self.logger.warning(f"中证1000期间基准涨幅:{total_percent_1000}%, 策略最大涨幅: {max_percent_1000}%, 最大回撤: {max_dd_1000}%" )
        self.logger.warning(f"[汇总] - - 策略涨幅: {total_percent} %, 策略最大涨幅: {max_percent}%, 最大回撤: {max_dd}%")

    def predict(self, *, target_date = None):
        self.is_predict = True
        # self.cur_date = self.dates[index]
        cur_date = datetime.now().strftime("%Y-%m-%d")
        self.cur_date = target_date if target_date else "2023-05-19"
        self.holdlist = [
            # {
            #     'name': "芯片ETF",
            #     'code': "159995",
            #     'symbol': "SZ159995",
            #     'buy_price': 1.1,
            #     'buy_date': '2023-04-21',
            # },
            # {
            #     'name': "新能源",
            #     'code': "516160",
            #     'symbol': "SH516160",
            #     'buy_price': 0.914,
            #     'buy_date': '2023-04-21',
            # },
            # {
            #     'name': "医药50",
            #     'code': "512120",
            #     'symbol': "SH512120",
            #     'buy_price': 0.505,
            #     'buy_date': '2023-04-26',
            # }
        ]
        self.collect_data()
        # self.logger.info("\n=================traverse_date: %s=====================", self.cur_date)
        self.prepare()
        self.filter()
        self.sell_or_keep()


if __name__ == '__main__':
    # asset_calculator()
    strategy = MomentumStrategyPlus('2017-12-31', '2018-06-30')
    