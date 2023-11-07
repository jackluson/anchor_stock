'''
Desc:
File: /wglh.py
File Created: Thursday, 25th May 2023 12:29:07 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import os
import re
import time
import json
from bs4 import BeautifulSoup
from utils.file_op import update_xlsx_file
from utils.index import bootstrap_thread, get_symbol_by_code
from infra.api.wglh import ApiWglh
from infra.models.stock_pe_pb import Stock_PE_PB as Stock_PE_PB_Model
from sql_model.query import StockQuery
import pandas as pd
from infra.logger.logger import logger


class SaveValueLevel():
    api = None
    query: StockQuery = None
    stocks_info = []
    ignore_codes = ['001267', '601956', '301192', '301321']
    def __init__(self, *, date = None) -> None:
        self.api = ApiWglh()
        self.query = StockQuery()
        if date == None:
            self.cur_date =  time.strftime(
            "%Y-%m-%d", time.localtime(time.time()))
        else:
            self.cur_date = date
        self.get_stock_list()
    def save(self):
        self.get_stock_list()
        # self.travel()
        # self.output()
        self.crawl()
    def handle_item(self, index):
        stock = self.all_stock[index]
        stock_code = stock.get('stock_code')
        info = {
            'code': stock_code,
            'name': stock.get('stock_name'),
            'date': self.cur_date,
        }
        # wglh没有这些股票数据
        if bool(re.search("^(2|4|8|9)\d{5}$", stock_code)) or stock_code in self.ignore_codes:
            return None
        symbol = get_symbol_by_code(stock_code)
        value_levels = self.api.get_pe_pb_levels_from_history(symbol=symbol)
        if value_levels == None:
            return None
        pb_info = value_levels.get('pb')
        pe_info = value_levels.get('pe')
        pe_koufei_info = value_levels.get('pe_koufei')
        
        info['pb'] = self.format(pb_info.get('value'))
        info['pb_mid'] = pb_info.get('median_10year')
        info['pb_mid_1'] = pb_info.get('median_1year')
        info['pb_mid_3'] = pb_info.get('median_3year')
        info['pb_mid_5'] = pb_info.get('median_5year')
        info['pb_mid_all'] = pb_info.get('median_all')

        info['pb_percent'] = pb_info.get('percent_10year')
        info['pb_percent_1'] = pb_info.get('percent_1year')
        info['pb_percent_3'] = pb_info.get('percent_3year')
        info['pb_percent_5'] = pb_info.get('percent_5year')
        info['pb_percent_all'] = pb_info.get('percent_all')

        info['pe'] = self.format(pe_info.get('value'))
        info['pe_mid'] = pe_info.get('median_10year')
        info['pe_mid_1'] = pe_info.get('median_1year')
        info['pe_mid_3'] = pe_info.get('median_3year')
        info['pe_mid_5'] = pe_info.get('median_5year')
        info['pe_mid_all'] = pe_info.get('median_all')

        info['pe_percent'] = pe_info.get('percent_10year')
        info['pe_percent_1'] = pe_info.get('percent_1year')
        info['pe_percent_3'] = pe_info.get('percent_3year')
        info['pe_percent_5'] = pe_info.get('percent_5year')
        info['pe_percent_all'] = pe_info.get('percent_all')
        
        info['pe_koufei'] = self.format(pe_koufei_info.get('value'))
        info['pe_koufei_mid'] = pe_koufei_info.get('median_10year')
        info['pe_koufei_mid_1'] = pe_koufei_info.get('median_1year')
        info['pe_koufei_mid_3'] = pe_koufei_info.get('median_3year')
        info['pe_koufei_mid_5'] = pe_koufei_info.get('median_5year')
        info['pe_koufei_mid_all'] = pe_koufei_info.get('median_all')
        info['pe_koufei_percent'] = pe_koufei_info.get('percent_10year')
        info['pe_koufei_percent_1'] = pe_koufei_info.get('percent_1year')
        info['pe_koufei_percent_3'] = pe_koufei_info.get('percent_3year')
        info['pe_koufei_percent_5'] = pe_koufei_info.get('percent_5year')
        info['pe_koufei_percent_all'] = pe_koufei_info.get('percent_all')
        return info
    def crawl(self):
        all_stock = self.all_stock
        def crawlData(start, end):
            line = f'开始爬取：爬取时间: {self.cur_date} 个数数量: {end-start}(从{start}到{end})'
            logger.info(line)
            save_info_list = []
            for index in range(start, end):
                if not index % 100 and len(save_info_list) > 0:
                    print('index', index)
                    Stock_PE_PB_Model.bulk_save(save_info_list)
                    save_info_list = []
                info = self.handle_item(index)
                if info:
                    save_info_list.append(info)
            Stock_PE_PB_Model.bulk_save(save_info_list)
            line = f'结束：爬取时间: {self.cur_date} 个数数量: {end-start}(从{start}到{end})'
            logger.info(line)
        count = len(all_stock)
        print("count", count)
        bootstrap_thread(crawlData, count, 12)
        pass
    def get_stock_list(self):
        self.all_stock = self.query.query_all_stock(date=self.cur_date, exclude_table='stock_pe_pb', date_key='date')
    
    def format(self, value):
        val = value.strip()
        if val == '亏损':
            return -1
        if val:
            return float(value)
        return None
    def travel(self):
        stocks_info = []
        all_stock = self.all_stock
        start_index = 0
        for index in range(start_index, len(all_stock)):
            if index % 100 == 0:
                print('index', index)
            info = self.handle_item(index)
            if info:
                stocks_info.append(info)
        self.stocks_info = stocks_info

    def output(self):
        output_dir = f'{os.getcwd()}/outcome/pe_pb/'
        all_file_path = f'{output_dir}/{self.cur_date}_pe_pb_10.xlsx'
        df_all_stocks = pd.DataFrame(self.stocks_info).reset_index(drop=True)
        update_xlsx_file(all_file_path, df_all_stocks, '所有')

# wglh = Wglh()

if __name__ == '__main__':
    SaveValueLevel().save()
