'''
Desc: 雪球API数据
File: /xue_api.py
File Created: Friday, 3rd September 2021 10:41:00 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''
import os
import pandas as pd
import time
import logging
import dateutil
import requests
from bs4 import BeautifulSoup

from base.base_api import BaseApi
from utils.file_op import write_fund_json_data
from utils.index import get_symbol_by_code, get_request_header_key

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from infra.api.snowball import ApiSnowBall
from infra.logger.logger import logger
from infra.config.parser import conf_parser

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

indictor_key_map = {
    '市价': 'price',
    '成交量': 'volume',
    '成交额': 'amount',
    '振幅': 'amplitude',
    '单位净值': 'net_value',
    '累计净值': 'accum_net_value',
    '溢价率': 'premium_rate',
    '基金份额': 'share',
    '资产净值': 'asset',
    # '成立日': 'found_date'
}

class ApiXueqiu(BaseApi):
    infraSnowBallApi: ApiSnowBall = None
    def __init__(self):
        super().__init__()
        self.infraSnowBallApi = ApiSnowBall()
        self.snowball_cookie = conf_parser.snowball_cookie
        if not self.snowball_cookie:
            self.snowball_cookie = self.infraSnowBallApi.xue_qiu_cookie
        self.set_client_headers()

    def get_stock_quote(self, code):
        data = self.infraSnowBallApi.get_stock_quote(code)
        data_quote = data.get('quote')
        # 有些股票在新三板停牌后，再其他板块还没上市 比如并行科技(NQ:839493)，这个时候股票代码是NQ开头
        if not data_quote:
            logger.info(f'code:{code}')
            return None
        data_others = data.get('others')
        stock_daily_dict = {
            'code': data_quote['code'],
            'status': data_quote['status'],
            'name': data_quote['name'],
            'exchange': data_quote['exchange'],
            'timestamp': time.strftime("%Y-%m-%d", time.localtime(data_quote['timestamp']/1000)),
            'price': data_quote['current'],
            'open_price': data_quote['open'],
            'limit_up_price': data_quote['limit_up'],
            'limit_low_price': data_quote['limit_down'],
            'avg_price': data_quote['avg_price'],
            'last_close_price': data_quote['last_close'],
            'amplitude': data_quote['amplitude'],
            'turnover_rate': data_quote['turnover_rate'],
            'low52w': data_quote['low52w'],
            'high52w': data_quote['high52w'],
            'pb': data_quote['pb'],
            'pe_ttm': data_quote['pe_ttm'],
            'pe_lyr': data_quote['pe_lyr'],
            'pe_forecast': data_quote['pe_forecast'],
            'amount': data_quote['amount'],
            'volume': data_quote['volume'],
            'volume_ratio': data_quote.get('volume_ratio'),
            'pankou_ratio': data_others['pankou_ratio'],
            'goodwill_in_net_assets': data_quote.get('goodwill_in_net_assets'),
            'float_shares': data_quote['float_shares'],
            'total_shares': data_quote['total_shares'],
            'float_market_capital': data_quote['float_market_capital'],
            'market_capital': data_quote['market_capital'],
            'eps': data_quote['eps'],
            'navps': data_quote['navps'],
            'dividend': data_quote['dividend'],
            'dividend_yield': data_quote['dividend_yield'],
            'percent': data_quote['percent'],
            'current_year_percent': data_quote['current_year_percent'],
        }
        return stock_daily_dict

    def get_main_financial_indicator(self, code, count, **args):
        symbol = get_symbol_by_code(code)
        type = args.get('type') if args.get('type') else 'all'
        timestamp = args.get('timestamp') if args.get('timestamp') else ''
        payload = {
            'symbol': symbol,
            'type':  type,
            'count': count,
            'timestamp': timestamp,
        }
        url = "https://stock.xueqiu.com/v5/stock/finance/cn/indicator.json?symbol={symbol}&type={type}&is_detail=true&count={count}&timestamp={timestamp}".format(
            **payload)
        # headers = self.get_client_headers()
        res = session.get(url, headers=self.headers)
        try:
            if res.status_code == 200:
                res_json = res.json().get('data')
                stock_name = res_json.get('quote_name')
                stock_quarter_financial_indicator_list = []
                report_list = res_json.get('list')
                for report_item in report_list:
                    report_date = time.strftime(
                        "%Y-%m-%d", time.localtime(report_item.get('report_date')/1000))
                    report_publish_date = time.strftime(
                        "%Y-%m-%d", time.localtime(report_item.get('ctime')/1000))
                    stock_quarter_financial_indicator_dict = {
                        'code': code,
                        'name': stock_name,
                        'report_date': report_date,
                        'report_name': report_item.get('report_name'),
                        'report_publish_date': report_publish_date,
                        'report_publish_date': report_publish_date,
                        # 关键指标
                        'total_revenue': report_item.get('total_revenue')[0],
                        'total_revenue_yoy': report_item.get('total_revenue')[1],
                        'total_revenue_yoy_yoy': report_item.get('operating_income_yoy')[1],
                        'net_profit_atsopc': report_item.get('net_profit_atsopc')[0],
                        'net_profit_atsopc_yoy': report_item.get('net_profit_atsopc')[1],
                        'net_profit_atsopc_yoy_yoy': report_item.get('net_profit_atsopc_yoy')[1],
                        'net_profit_after_nrgal_atsolc': report_item.get('net_profit_after_nrgal_atsolc')[0],
                        'net_profit_after_nrgal_atsolc_yoy': report_item.get('net_profit_after_nrgal_atsolc')[1],
                        'net_profit_after_nrgal_atsolc_yoy_yoy': report_item.get('np_atsopc_nrgal_yoy')[1],
                        'net_selling_rate': report_item.get('net_selling_rate')[0],
                        'net_selling_rate_yoy': report_item.get('net_selling_rate')[1],
                        'gross_selling_rate': report_item.get('gross_selling_rate')[0],
                        'gross_selling_rate_yoy': report_item.get('gross_selling_rate')[1],
                        'roe': report_item.get('avg_roe')[0],
                        'roe_yoy': report_item.get('avg_roe')[1],
                        # 每股指标
                        'np_per_share': report_item.get('np_per_share')[0],
                        'np_per_share_yoy': report_item.get('np_per_share')[1],
                        'operate_cash_flow_ps': report_item.get('operate_cash_flow_ps')[0],
                        'operate_cash_flow_ps_yoy': report_item.get('operate_cash_flow_ps')[1],
                        'basic_eps': report_item.get('basic_eps')[0],
                        'basic_eps_yoy': report_item.get('basic_eps')[1],
                        'capital_reserve': report_item.get('capital_reserve')[0],
                        'capital_reserve_yoy': report_item.get('capital_reserve')[1],
                        'undistri_profit_ps': report_item.get('undistri_profit_ps')[0],
                        'undistri_profit_ps_yoy': report_item.get('undistri_profit_ps')[1],
                        # 盈利能力
                        'ore_dlt': report_item.get('ore_dlt')[0],
                        'ore_dlt_yoy': report_item.get('ore_dlt')[1],
                        'net_interest_of_total_assets': report_item.get('net_interest_of_total_assets')[0],
                        'net_interest_of_total_assets_yoy': report_item.get('net_interest_of_total_assets')[1],
                        'rop': report_item.get('rop')[0],
                        'rop_yoy': report_item.get('rop')[1],
                        # 偿债能力，财务风险
                        'asset_liab_ratio': report_item.get('asset_liab_ratio')[0],
                        'asset_liab_ratio_yoy': report_item.get('asset_liab_ratio')[1],
                        'equity_multiplier': report_item.get('equity_multiplier')[0],
                        'equity_multiplier_yoy': report_item.get('equity_multiplier')[1],
                        'current_ratio': report_item.get('current_ratio')[0],
                        'current_ratio_yoy': report_item.get('current_ratio')[1],
                        'quick_ratio': report_item.get('quick_ratio')[0],
                        'quick_ratio_yoy': report_item.get('quick_ratio')[1],
                        'equity_ratio': report_item.get('equity_ratio')[0],
                        'equity_ratio_yoy': report_item.get('equity_ratio')[1],
                        'holder_equity': report_item.get('holder_equity')[0],
                        'holder_equity_yoy': report_item.get('holder_equity')[1],
                        'ncf_from_oa_to_total_liab': report_item.get('ncf_from_oa_to_total_liab')[0],
                        'ncf_from_oa_to_total_liab_yoy': report_item.get('ncf_from_oa_to_total_liab')[1],
                        # 运营能力
                        'inventory_turnover_days': report_item.get('inventory_turnover_days')[0],
                        'inventory_turnover_days_yoy': report_item.get('inventory_turnover_days')[1],
                        'receivable_turnover_days': report_item.get('receivable_turnover_days')[0],
                        'receivable_turnover_days_yoy': report_item.get('receivable_turnover_days')[1],
                        'accounts_payable_turnover_days': report_item.get('accounts_payable_turnover_days')[0],
                        'accounts_payable_turnover_days_yoy': report_item.get('accounts_payable_turnover_days')[1],
                        'cash_cycle': report_item.get('cash_cycle')[0],
                        'cash_cycle_yoy': report_item.get('cash_cycle')[1],
                        'operating_cycle': report_item.get('operating_cycle')[0],
                        'operating_cycle_yoy': report_item.get('operating_cycle')[1],
                        'total_capital_turnover': report_item.get('total_capital_turnover')[0],
                        'total_capital_turnover_yoy': report_item.get('total_capital_turnover')[1],
                        'inventory_turnover': report_item.get('inventory_turnover')[0],
                        'inventory_turnover_yoy': report_item.get('inventory_turnover')[1],
                        'account_receivable_turnover': report_item.get('account_receivable_turnover')[0],
                        'account_receivable_turnover_yoy': report_item.get('account_receivable_turnover')[1],
                        'accounts_payable_turnover': report_item.get('accounts_payable_turnover')[0],
                        'accounts_payable_turnover_yoy': report_item.get('accounts_payable_turnover')[1],
                        'current_asset_turnover_rate': report_item.get('current_asset_turnover_rate')[0],
                        'current_asset_turnover_rate_yoy': report_item.get('current_asset_turnover_rate')[1],
                        'fixed_asset_turnover_ratio': report_item.get('fixed_asset_turnover_ratio')[0],
                        'fixed_asset_turnover_ratio_yoy': report_item.get('fixed_asset_turnover_ratio')[1],
                    }
                    stock_quarter_financial_indicator_list.append(
                        stock_quarter_financial_indicator_dict)
                # pprint.pprint(stock_quarter_financial_indicator_list)
                return stock_quarter_financial_indicator_list
        except:
            raise('中断')

    def get_kline_info(self, symbol, begin, period, *, type = 'before', rest = dict()):
        begin_timestamp = dateutil.parser.parse(begin).timestamp()
        if rest.get('end'):
            end = rest.get('end')
            end_timestamp = dateutil.parser.parse(end).timestamp()
            rest['end'] = int(end_timestamp * 1000)
        payload = {
            'symbol': symbol.upper(),
            'period': period,
            'type': 'before' if type == None else type, #默认前复权数据
            # JavaScript时间戳 = python时间戳 * 1000
            'begin': int(begin_timestamp * 1000),
            'indicator': 'kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance',
            # 'end': int(end_timestamp * 1000),
            **rest
            # 'count': 181,
            # 'timestamp': timestamp,
        }
        params_template = ''
        for filed in payload.keys():
            if params_template:
                params_template += '&'
            params_template = params_template + filed + '={' + filed + '}'
        url = ("https://stock.xueqiu.com/v5/stock/chart/kline.json?" + params_template).format(
            **payload)
        # headers = self.get_client_headers()
        # print("headers", headers)
        res = session.get(url, headers=self.headers)
        res_json = {}
        try:
            if res.status_code == 200:
                res_json = res.json()
            else:
                print('请求异常', res, symbol)
                line = f'该ETF{symbol}{res}--api数据有误'
                logging.error(line)
                return pd.DataFrame([], columns=[])
        except:
            line = f'该ETF{symbol}--api数据有误'
            logging.error(line)
            return pd.DataFrame([], columns=[])
            # raise ('中断')

        columns = res_json["data"]["column"]
        items = res_json["data"]["item"]
        pd.Series(items)
        df = pd.DataFrame(
            items, columns=columns)

        if df.empty:
            # print(symbol)
            return df
        try:
            df = df[['timestamp', 'open', 'close', 'low', 'high', 'chg',
                     'percent', 'volume', 'amount', 'market_capital']]
            df['timestamp'] = df['timestamp'] / 1000
            df['timestamp'] = pd.to_datetime(
                df['timestamp'], unit='s', utc=True)
            # df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            df = df.set_index('timestamp').tz_convert('Asia/Shanghai')
            # df = df.set_index('timestamp').tz_convert('Asia/Shanghai')
        except:
            print(res_json)
            print(symbol)
            line = f'该ETF{symbol}{res_json}数据处理有错'
            logging.error(line)
            return pd.DataFrame({'A': []})
        return df

    def get_stock_page_info(self, symbol):
        """ 获取ETF到期时间等基本信息
        """
        url = "https://xueqiu.com/S/{}".format(symbol)
        # headers = self.get_client_headers()
        res = session.get(url, headers=self.headers)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, 'lxml')
        # print(soup.body.select('table.quote-info')[0].select('td'))
        etf_info = {}
        delist_flag = False
        for div in soup.body.select('.stock-flag'):
            if '退市' in div.text:
                delist_flag = True
                break
        if delist_flag:
            etf_info['delist_date'] = 1
        indictor_data = dict()
        for td in soup.body.select('table.quote-info')[0].select('td'):
            key = td.next[0:-1]
            if key in indictor_key_map.keys():
                value = td.span.text
                if key == '成交量':
                    if '万手' in value:
                        value = float(value.replace('万手', '')) * 10000
                    elif '亿手' in value :
                        value = float(value.replace('亿手', '')) * 100000000
                    elif '手' in value:
                        value = float(value.replace('手', ''))
                if isinstance(value, str):
                    if '万' in value:
                        value = float(value.replace('万', '')) * 10000
                    elif '亿' in value:
                        value = float(value.replace('亿', '')) * 100000000
                    elif '%' in value:
                        value = float(value.replace('%', ''))
                if isinstance(value, float):
                    value = round(value, 3)
                if value == '--':
                    value = None
                indictor_data[indictor_key_map[key]] = value
            elif '成立日' in td.text:
                etf_info['found_date'] = td.span.text
            elif '到期日：' in td.text and '--' not in td.span.text:
                print(symbol, td.getText(), td.span.text)
                etf_info['delist_date'] = td.span.text
            #没有到期日去最新净值日期
            elif etf_info.get('delist_date') and '净值日期' in td.text:
                print(symbol, td.getText(), td.span.text)
                etf_info['delist_date'] = td.span.text
        etf_info['indictor'] = indictor_data
        return etf_info
