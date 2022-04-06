import math
import random
import logging
import pandas as pd
from datetime import datetime
from base.kline import Kline
from strategy.base_strategy import BaseStrategy
from calculate.correlated import Correlator
from controller.asset_calculator import AssetCalculator


class MomentumStrategy(BaseStrategy):
    init_money = 50000 # 初始资金
    hold_market_value = init_money # 目前持有市值
    current_flow_money = init_money # 可用现金流
    hold_etf = []
    sell_list = [] # 卖出列表
    max_hold_etf_count = 5 #最大可同时买入的ETF数量
    cost = 5 # 每次交易的费用
    max_one_hold_asset = init_money / cost # 
    begin_date = None
    end_date = None

    def __init__(self, begin_date, end_date):
        super().__init__()
        benchmark = Kline('SH000300', '沪深300')
        self.begin_date = begin_date
        self.end_date = end_date
        benchmark.format_params({
            'period': 'day',
            'begin_date': begin_date,
            'end_date': end_date,
        })
        benchmark.get_kline_data()
        benchmark.percent = benchmark.calculate_period_percent()
        self.benchmark = benchmark

    def traverse(self):
        dates = self.benchmark.df_kline.index
        for index in range(1, len(dates)):
            self.pre_date = dates[index - 1]
            self.cur_date = dates[index]
            self.sell_list = []
            logging.info("=================traverse_date: %s=====================", self.cur_date)
            candidate_etf = self.compute()
            self.sell()
            self.buy(candidate_etf)
            self.per_day_summary()
        self.serialize()
        return self

    def compute(self, is_predict=False):
        compute_date = self.cur_date if is_predict else self.pre_date
        compute_date_str = compute_date.strftime("%Y-%m-%d")
        ts = pd.Timestamp(compute_date_str).timestamp()
        # 测量过去半年的相似度
        filter_found_date = datetime.fromtimestamp(
            ts - 720 * 24 * 3600).strftime("%Y-%m-%d")
        etf_gain = AssetCalculator({
            'is_year': 1,
            'count': 10,
            'day_10_before': 1,
            'day_20_before': 1,
            'day_30_before': 1,
            'day_60_before': 1,
            'type': 'etf',  # index or etf
            'markdown': 0,
            'filter_found_date': filter_found_date
        })

        etf_gain.set_date({
            'date': compute_date_str,
            # 'freq': 'W',  # Y,Q,M,W,D
            'before_day':  5,
        }).calculate()
        # print('len', len(etf_gain.df_data))
        # 过滤成交量少于10w手的etf
        filter_volumn = etf_gain.df_data.loc[etf_gain.df_data['percent'] > 3].reset_index(
        )
        # print('len', len(filter_volumn))
        filter_volumn = filter_volumn.loc[filter_volumn['avg_volume'] > 1.0e6]
        # print('len', len(filter_volumn))

        if len(filter_volumn) == 0:
            return []
        if len(filter_volumn) == 1:
            return [filter_volumn.iloc[0]]
        compares = filter_volumn.head(100)
        # etf_gain.append_before_data(compares)
        correlator = Correlator()
        correlator.set_compare(compares, self.hold_etf).correlate()
        candidate_etf = correlator.filter_near_similarity()
        # print("candidate_etf:\n")
        # print(candidate_etf)
        return candidate_etf

    def buy(self, candidate_etf):
        if isinstance(candidate_etf, pd.DataFrame):
            for candidate in candidate_etf.index:
                name = candidate[0: -10]
                symbol = candidate[-9:-1]
                self.buyone(symbol, name)
        elif len(candidate_etf) == 1:
            symbol = candidate_etf[0]['market'].upper(
            ) + candidate_etf[0]['code']
            self.buyone(symbol, candidate_etf[0]['name'])

    def buyone(self, symbol, name):
        if len(self.hold_etf) >= self.max_hold_etf_count:
            return
        for etf in self.hold_etf:
            if etf['symbol'] == symbol:
                return
        for etf in self.sell_list:
            if etf['symbol'] == symbol:
                return
        # 计算买入的价格 ～ 最低价和最高价之间的随机价格
        prices = self.get_cur_price(symbol, name)
        if prices == None:
            print('symbol', symbol, 'name', name, '当天没有交易价格')
            return
        buy_price = prices[0]
        close_price = prices[1]
        max_buy_available_asset = min(self.max_one_hold_asset, self.current_flow_money)
        hand_count = math.floor(max_buy_available_asset / buy_price / 100)  # 多少手
        buy_info = {
            'symbol': symbol,
            'name': name,
            'buy_price': buy_price,
            'buy_date': self.cur_date,
            'hand_num': hand_count * 100,
            'buy_close_price': close_price,
        }
        self.hold_etf.append(buy_info)
        logging.info('buy_info: symbol: %s, name: %s, 买入价格: %f, close_price: %f, 手数: %f '% (symbol, name, buy_price, close_price, hand_count))
        self.current_flow_money = self.current_flow_money - \
            self.cost - buy_price * hand_count * 100

    def sell(self):
        sell_list = []
        for etf in self.hold_etf:
            symbol = etf.get('symbol')
            name = etf.get('name')
            hand_num = etf.get('hand_num')
            buy_price = etf.get('buy_price')
            each_kline = self.init_kline(symbol, name)
            close = each_kline.df_kline.loc[self.pre_date]['close']
            last_percent = ((close - buy_price) / buy_price * 100).round(2)
            # 求是否低于5日均线
            ma_5 = each_kline.get_past_mean('close', 5, 2)
            if ma_5 > close and (last_percent > 3 or (0 > last_percent and -3 > last_percent)):
                prices = self.get_cur_price(symbol, name)
                if prices == None:
                    print('symbol', symbol, 'name', name, '当天没有交易价格')
                    return
                sell_price = prices[0]
                self.hold_etf.remove(etf)
                sell_list.append(etf)
                self.current_flow_money = self.current_flow_money - \
                    self.cost + sell_price * hand_num
                percent = ((sell_price - etf['buy_price']) / etf['buy_price'] * 100 ).round(2)
                logging.info("[sell] name:%s, symbol:%s, sell_price:%s, buy_price:%s, percent:%s" % (etf['name'], etf['symbol'],sell_price, etf['buy_price'], str(percent)))
        self.sell_list = sell_list
    def get_cur_price(self, symbol, name):
        # 取近半年前数据进行统计
        kline = self.init_kline(symbol, name, -1)
        if kline.df_kline.empty:
            return None
        row = kline.df_kline.iloc[0]
        buy_price = random.uniform(row['low'], row['high']).round(2)
        return [buy_price, row['close']]

    def per_day_summary(self):

        market_value = self.current_flow_money
        logging.info("====%s当前持仓===="%(self.cur_date))
        for etf in self.hold_etf:
            cur_close_price = etf.get('buy_close_price')
            hand_num = etf.get('hand_num')
            buy_price = etf.get('buy_price')
            symbol = etf.get('symbol')
            name = etf.get('name')
            if etf.get('buy_date') != self.cur_date:
                cur_prices = self.get_cur_price(symbol, name)
                if cur_prices == None:
                    logging.error("[error] name:%s, symbol:%s, 没有当天交易价格"%(name, symbol))
                    return
                cur_close_price = cur_prices[1]
            market_value = market_value + cur_close_price * hand_num
            percent = ((cur_close_price - buy_price
                        ) / buy_price * 100).round(2)
            logging.info("[info] name:%s, code:%s, price:%f, 当前价格: %f" % (name, symbol, buy_price , cur_close_price))
            # print("symbol", etf['symbol'], "percent",  percent)
        pre_hold_market_value = self.hold_market_value
        self.hold_market_value = market_value
        percent = ((market_value - pre_hold_market_value) / pre_hold_market_value * 100).round(2)
        logging.info("策略当日涨幅:%f, 最新持有市值:%f, 可用资金:%f"%(percent, self.hold_market_value, self.current_flow_money))
        logging.info("沪深300当日涨幅:%f"%(self.benchmark.df_kline.loc[self.cur_date]['percent']))


    def init_kline(self, symbol, name,  before_day=180):
        """
        初始化kline,
        Args:
            symbol (_type_): etf代码
            name (_type_): etf名称
            before_day (int, optional): _description_. Defaults to 180

        Returns:
            _type_: _description_
        """
        each_kline = Kline(symbol, name)
        end_date = self.pre_date.strftime("%Y-%m-%d")
        end_date_ts = pd.Timestamp(end_date).timestamp()
        if before_day == -1:
            begin_date_ts = pd.Timestamp(
                self.cur_date.strftime("%Y-%m-%d")).timestamp()
        else:
            # 默认取近半年前数据进行统计
            begin_date_ts = end_date_ts - before_day * 24 * 3600
        begin_date = datetime.fromtimestamp(begin_date_ts).strftime("%Y-%m-%d")
        if begin_date_ts > end_date_ts:
            end_date = begin_date

        each_kline.format_params({
            'period': 'day',
            'begin_date': begin_date,
            'end_date': end_date,
        })
        each_kline.get_kline_data()
        return each_kline

    def serialize(self):
        logging.info("=====================serialize=====================")
        logging.info("[keep] 当前持仓股票:")
        cur_hold_etf = pd.DataFrame(self.hold_etf)
        print(cur_hold_etf)
        for index, row in cur_hold_etf.iterrows():
            logging.info("[keep] name:%s, code:%s, price:%s" % (row['name'], row['symbol'], row['buy_price']))

        logging.warning("沪深300期间基准涨幅:%s" % self.benchmark.percent)
        earn_money = self.hold_market_value - self.init_money
        earn_percent = (earn_money / self.init_money * 100).round(2)
        logging.warning("策略涨幅:%f" % earn_percent)
        return self

    def predict(self):
        self.compute(True)
        pass
