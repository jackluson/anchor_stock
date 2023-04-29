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

from base.base_api_config import BaseApiConfig
from utils.file_op import write_fund_json_data
from utils.index import get_symbol_by_code, get_request_header_key

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

class ApiXueqiu(BaseApiConfig):
    def __init__(self):
        super().__init__()
        self.xue_qiu_cookie = os.getenv('xue_qiu_cookie')
        if not self.xue_qiu_cookie:
            entry_url = 'https://xueqiu.com/'
            host = 'xueqiu.com'
            header_key = 'Cookie'
            xue_qiu_cookie = get_request_header_key(
                entry_url, host, header_key)
            self.xue_qiu_cookie = xue_qiu_cookie
        self.set_client_headers()

    def get_special_stock_quote(self, code, date=None):
        symbol = get_symbol_by_code(code)
        if not date:
            date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        dir = './archive_data/json/xueqiu/' + symbol + '/'
        file_name_path = dir + date + '.json'
        if os.path.exists(file_name_path):
            res_json = self.get_data_from_json(file_name_path)
        else:
            url = "https://stock.xueqiu.com/v5/stock/quote.json?symbol={0}&extend=detail".format(
                symbol)
            # headers = self.get_client_headers()
            res = session.get(url, headers=self.headers)
            try:
                if res.status_code == 200:
                    res_json = res.json()
                else:
                    print('res异常', res)
            except:
                raise('中断')
        data = res_json['data'].get('quote')
        data_others = res_json['data'].get('others')
        time_format = time.strftime(
            "%Y-%m-%d", time.localtime(data['timestamp']/1000))
        # 数据存档
        dir = './archive_data/json/xueqiu/' + symbol + '/'
        file_name = time_format + '.json'
        write_fund_json_data(res_json, file_name,  dir)
        #print("time_format", time_format)
        stock_daily_dict = {
            'code': data['code'],
            'status': data['status'],
            'name': data['name'],
            'exchange': data['exchange'],
            'timestamp': time.strftime("%Y-%m-%d", time.localtime(data['timestamp']/1000)),
            'price': data['current'],
            'open_price': data['open'],
            'limit_up_price': data['limit_up'],
            'limit_low_price': data['limit_down'],
            'avg_price': data['avg_price'],
            'last_close_price': data['last_close'],
            'amplitude': data['amplitude'],
            'turnover_rate': data['turnover_rate'],
            'low52w': data['low52w'],
            'high52w': data['high52w'],
            'pb': data['pb'],
            'pe_ttm': data['pe_ttm'],
            'pe_lyr': data['pe_lyr'],
            'pe_forecast': data['pe_forecast'],
            'amount': data['amount'],
            'volume': data['volume'],
            'volume_ratio': data['volume_ratio'],
            'pankou_ratio': data_others['pankou_ratio'],
            'goodwill_in_net_assets': data['goodwill_in_net_assets'],
            'float_shares': data['float_shares'],
            'total_shares': data['total_shares'],
            'float_market_capital': data['float_market_capital'],
            'market_capital': data['market_capital'],
            'eps': data['eps'],
            'navps': data['navps'],
            'dividend': data['dividend'],
            'dividend_yield': data['dividend_yield'],
            'percent': data['percent'],
            'current_year_percent': data['current_year_percent'],
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
                    #print("report_item", report_item)
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
        for td in soup.body.select('table.quote-info')[0].select('td'):
            if '成立日：' in td.text:
                etf_info['found_date'] = td.span.text
            elif '到期日：' in td.text and '--' not in td.span.text:
                print(symbol, td.getText(), td.span.text)
                etf_info['delist_date'] = td.span.text
            #没有到期日去最新净值日期
            elif etf_info.get('delist_date') and '净值日期' in td.text:
                print(symbol, td.getText(), td.span.text)
                etf_info['delist_date'] = td.span.text
        return etf_info
    
    def get_stock_profile_info(self, code):
        """ 获取公司简介信息
        """
        symbol = get_symbol_by_code(code)
        payload = {
            'symbol': symbol.upper(),
        }
        url = "https://stock.xueqiu.com/v5/stock/f10/cn/company.json?symbol={symbol}".format(
            **payload)
        # headers = self.get_client_headers()
        # print("headers", headers)
        res = session.get(url, headers=self.headers)
        try:
            if res.status_code == 200:
                res_json = res.json()
                info = res_json.get('data').get('company')
                if not info or not info['org_short_name_cn']:
                    line = f'该{symbol}--没有简介信息'
                    logging.warning(line)
                return info
            else:
                print('请求异常', res, symbol)
                line = f'该股票{symbol}{res}--api数据有误'
                logging.error(line)
                
        except:
            line = f'该股票{symbol}--api数据有误'
            logging.error(line)
