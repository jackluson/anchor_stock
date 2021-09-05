'''
Desc: 雪球API数据
File: /xue_api.py
Project: stock_info
File Created: Friday, 3rd September 2021 10:41:00 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''
import os
import time
import requests

from .base_api import BaseApier
from utils.file_op import write_fund_json_data
from utils.index import get_symbol_by_code, get_request_header_key


class ApiXueqiu(BaseApier):
    def __init__(self):
        super().__init__()
        self.xue_qiu_cookie = os.getenv('xue_qiu_cookie')
        if not self.xue_qiu_cookie:
            entry_url = 'https://xueqiu.com/'
            target_url = 'https://xueqiu.com/interview/list/latest.json?count=5'
            header_key = 'Cookie'
            self.xue_qiu_cookie = get_request_header_key(
                entry_url, target_url, header_key)

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
            headers = self.get_client_headers()
            res = requests.get(url, headers=headers)
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
        headers = self.get_client_headers()
        res = requests.get(url, headers=headers)
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
