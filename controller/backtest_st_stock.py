'''
Desc:
File: /backtest_st_stock.py
File Created: Sunday, 5th February 2023 3:54:58 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import pandas as pd
import numpy as np
import datetime as dt
from base.kline import Kline
from utils.file_op import update_xlsx_file
from utils.index import get_symbol_by_code

def backtest_st_stock():
    path = '/Users/admin/Desktop/2022摘帽ST涨跌统计_data.xlsx'
    all_stocks_map = pd.read_excel(
        io=path, engine="openpyxl",  dtype={
            "代码": np.str, 
            # '摘帽日期': np.str,
            # '摘帽公告日期': np.str,
            # '申请摘帽日期': np.str,
            # '年报披露日期': np.str
            }, sheet_name=None)
    print("all_stocks", all_stocks_map['2022'])
    sheet_name = '2022'
    all_stocks = all_stocks_map[sheet_name]
    # print('代码', all_stocks['代码'])
    # print('年报公布前10个交易日涨跌幅', all_stocks['摘帽后5个交易日涨幅'])
    for index, stock_item in all_stocks.iterrows():
        # if(index == 0):
        #     continue
        # if(index > 5):
        #     break
        code = stock_item['代码'].strip().rjust(6,'0') 
        if(len(code) == 6):
            symbol = get_symbol_by_code(code)
        else:
            symbol = stock_item['代码'][-2:] + stock_item['代码'][:6]
        name = stock_item['公司']
        skip = None
        date_field = '摘帽公告日期'
        lost_hat_date = None
        if(stock_item[date_field] is not pd.np.nan):
            if isinstance(stock_item[date_field],str) or isinstance(stock_item[date_field],int):
                hat_date = str(stock_item[date_field]) if isinstance(stock_item[date_field],int) else stock_item[date_field]
                date_str = hat_date[0:4] + '-' + hat_date[4:6] + '-' + hat_date[6:]
                date_str = date_str.strip()
            else:
                date_str = stock_item[date_field].strftime('%Y-%m-%d')
            lost_hat_date = date_str
            if skip == None:
                params = {
                    'period': 'day',
                    'begin_date': date_str,
                    'type': 'before',
                    'count': 6,
                    # 'end_date': date_str
                }
                kline = Kline(symbol, name)
                kline.format_params(params)
                kline.get_kline_data()
                all_stocks.at[index, '摘帽当天涨幅'] = kline.df_kline.iloc[0]['percent']
                last_close = kline.df_kline.iloc[0]['close'] / (kline.df_kline.iloc[0]['percent'] * 0.01 + 1)
                open_percent = round(100 * ((kline.df_kline.iloc[0]['open'] - last_close) / last_close), 2)
                high_percent = round(100 * ((kline.df_kline.iloc[0]['high'] - last_close) / last_close), 2)
                all_stocks.at[index, '摘帽当天开盘涨幅'] = open_percent
                all_stocks.at[index, '摘帽当天最高涨幅'] = high_percent
                for i in range(1,6):
                    percent = kline.df_kline.iloc[i]['percent']
                    all_stocks.at[index, '摘帽后第'+str(i)+'天涨幅涨幅'] = percent
                total_six_percent = round(100 * ((kline.df_kline.iloc[5]['close'] - last_close) / last_close), 2)
                all_stocks.at[index, '摘帽后近6个交易日涨幅'] = total_six_percent
        if(stock_item['申请摘帽日期'] is not pd.np.nan):
            target_date_column = '申请摘帽日期'
            target_date_row = stock_item[target_date_column]
            if isinstance(target_date_row,str):
                target_date_row = target_date_row.strip()
                if '/' in target_date_row:
                    target_date = dt.datetime.strptime(target_date_row, '%Y/%m/%d')
                    target_date = target_date.strftime('%Y-%m-%d')
                elif '-' in target_date_row:
                    target_date = dt.datetime.strptime(target_date_row, '%Y-%m-%d')
                    target_date = target_date.strftime('%Y-%m-%d')
                elif isinstance(target_date_row,str) or isinstance(target_date_row,int):
                    target_date_row = str(target_date_row) if isinstance(target_date_row,int) else target_date_row
                    target_date = target_date_row[0:4] + '-' + target_date_row[4:6] + '-' + target_date_row[6:]
                else:
                    print('日期格式有误')
            elif target_date_row and target_date_row is not pd.NaT:
                target_date = target_date_row.strftime('%Y-%m-%d')
            else:
                continue
            if lost_hat_date and target_date:
                params = {
                'period': 'day',
                'begin_date': target_date,
                # 'type': 'before',
                'end_date': lost_hat_date
                }
                day_diff = (dt.datetime.strptime(lost_hat_date,"%Y-%m-%d") - dt.datetime.strptime(target_date,"%Y-%m-%d")).days
                all_stocks.at[index, '申请摘帽至摘帽天数'] = day_diff
                kline = Kline(symbol, name)
                kline.format_params(params)
                kline.get_kline_data()
                if day_diff != 0 and len(kline.df_kline) > 0:
                    start_point = round(kline.df_kline.iloc[0]['close'] / (1 + kline.df_kline.iloc[0]['percent'] * 0.01), 2) 
                    end_point = kline.df_kline.iloc[-1]['close']
                    all_stocks.at[index, '申请摘帽至摘帽天数'] = day_diff
                    all_stocks.at[index, '申请摘帽至摘帽前涨幅'] = round((end_point - start_point)/end_point * 100, 2)
                else:
                    all_stocks.at[index, '申请摘帽至摘帽前涨幅'] = 0
                # continue
            # print("时间有误")
            params = {
                'period': 'day',
                'begin_date': target_date,
                'type': 'before',
                'count': 6,
                # 'end_date': date_str
            }
            kline = Kline(symbol, name)
            kline.format_params(params)
            kline.get_kline_data()
            all_stocks.at[index, '申请摘帽当天涨幅'] = kline.df_kline.iloc[0]['percent']
            all_stocks.at[index, '申请摘帽当天收盘价'] = kline.df_kline.iloc[0]['close']
            # all_stocks.at[index, '申请摘帽当天市值'] = kline.df_kline.iloc[0]['market_capital']
        if(stock_item['年报披露日期'] is not pd.np.nan):
            target_date_column = '年报披露日期'
            target_date_row = stock_item[target_date_column]
            if isinstance(target_date_row,str):
                target_date_row = target_date_row.strip()
                if '/' in target_date_row:
                    target_date = dt.datetime.strptime(target_date_row, '%Y/%m/%d')
                    target_date = target_date.strftime('%Y-%m-%d')
                elif '-' in target_date_row:
                    target_date = dt.datetime.strptime(target_date_row, '%Y-%m-%d')
                    target_date = target_date.strftime('%Y-%m-%d')
                elif isinstance(target_date_row,str) or isinstance(target_date_row,int):
                    target_date_row = str(target_date_row) if isinstance(target_date_row,int) else target_date_row
                    target_date = target_date_row[0:4] + '-' + target_date_row[4:6] + '-' + target_date_row[6:]
                else:
                    print('日期格式有误')
            elif target_date_row and target_date_row is not pd.NaT:
                target_date = target_date_row.strftime('%Y-%m-%d')
            else:
                continue
            params = {
                'period': 'day',
                'begin_date': target_date,
                'type': 'before',
                'count': -11,
                # 'end_date': date_str
            }
            kline = Kline(symbol, name)
            kline.format_params(params)
            kline.get_kline_data()
            # print(kline.df_kline)
            start_point = round(kline.df_kline.iloc[0]['close'] / (1 + kline.df_kline.iloc[0]['percent'] * 0.01), 2) 
            end_point = kline.df_kline.iloc[-2]['close']
            # print("start_point", start_point, 'end_point', end_point)
            all_stocks.at[index, '年报公布前10个交易日涨跌幅'] = round((end_point - start_point)/end_point * 100, 2)
            all_stocks.at[index, '年报公布前10个交易日涨跌幅_start'] = start_point
            all_stocks.at[index, '年报公布前10个交易日涨跌幅_end'] = end_point
    print(all_stocks)
    update_xlsx_file(path, all_stocks, sheet_name)
    print('end')
