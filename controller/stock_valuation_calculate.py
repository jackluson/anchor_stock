'''
Desc: 股票估值计算
File: /stock_valuation_calculate.py
Project: controller
File Created: Friday, 3rd September 2021 12:27:00 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import pandas as pd
import numpy as np

from sql_model.query import StockQuery


def stock_valuation_calculate():
    each_query = StockQuery()
    all_stock = each_query.query_all_stock()
    # all_stock_financial_list = each_query.query_all_stock_main_financial()
    # print('len(all_stock)', len(all_stock_financial_list))
    # for item in all_stock_financial_list:
    gross_selling_rate_benchmark = 30
    total_revenue_yoy_benchmark = 0.3
    pe_benchmark = 30
    df_stock_list = pd.DataFrame()
    for index in range(0, len(all_stock)):
        stock = all_stock[index]
        stock_code = stock.get('stock_code')
        timestamp = '2021-09-03'
        stock_financial_info_list = each_query.query_special_stock_main_financial(
            stock_code, timestamp)
        if len(stock_financial_info_list) == 0:
            print("stock_code", stock_code)
            continue
        df_stock_financial_info = pd.DataFrame(
            stock_financial_info_list, dtype="float")
        target_column = [
            'code', 'name', 'price',
            'report_date',
            'total_revenue',
            'total_revenue_yoy', 'net_profit_atsopc',
            'net_profit_atsopc_yoy', 'gross_selling_rate',
            'gross_selling_rate_yoy', 'net_selling_rate',
            'net_selling_rate_yoy',
            'roe', 'roe_yoy',
            'pe_ttm', 'pe_lyr', 'pe_forecast'
        ]
        df_main = df_stock_financial_info[target_column].set_index(
            'report_date').sort_index(ascending=False)

        df_main['code'] = np.str(stock_code)
        df_main['pe_cal'] = pe_benchmark * (1 + (df_main['gross_selling_rate'] - gross_selling_rate_benchmark) / gross_selling_rate_benchmark) * (
            1 + df_main['gross_selling_rate'] * 0.01 * (df_main['total_revenue_yoy']-total_revenue_yoy_benchmark) / total_revenue_yoy_benchmark)

        pe_sum = 0.0
        for i in range(0, 4):
            pe_sum += df_main['pe_cal'].shift(-i)
        df_main['pe_ttm_cal'] = pe_sum / 4  # 当前总市值
        df_main['is_under'] = df_main['pe_ttm_cal'] > df_main['pe_ttm']
        # print("df_main", df_main)
        last_three_year_per_roe = (
            df_main.at['2020-12-31', 'roe'] + df_main.at['2019-12-31', 'roe'] + df_main.at['2018-12-31', 'roe']) / 3
        if df_main.at['2021-06-30', 'is_under'] and last_three_year_per_roe > 10:
            df_stock_list = df_stock_list.append(df_main.head(1))
            # print("stock_list", stock_list)
        # exit()
    print(df_stock_list)
    # print("stock_financial_info_list", stock_financial_info_list)


if __name__ == '__main__':
    stock_valuation_calculate()
