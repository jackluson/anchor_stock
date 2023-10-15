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
from utils.index import get_symbol_by_code
from infra.api.wglh import ApiWglh
from sql_model.query import StockQuery
import pandas as pd


class SaveValueLevel():
    api = None
    query: StockQuery = None
    stocks_info = []
    ignore_codes = ['001267', '601956', '301192', '301321']
    def __init__(self) -> None:
        self.api = ApiWglh()
        self.query = StockQuery()
        self.get_stock_list()
        self.cur_date = time.strftime(
        "%Y-%m-%d", time.localtime(time.time()))
    def save(self):
        self.get_stock_list()
        self.travel()
        self.output()
    def get_stock_list(self):
        self.all_stock = self.query.query_all_stock()
    def travel(self):
        stocks_info = []
        all_stock = self.all_stock
        start_index = 0
        for index in range(start_index, len(all_stock)):
            stock = all_stock[index]
            if index % 100 == 0:
                print('index', index)
            info = {
                **stock
            }
            print("info", info)
            stock_code = stock.get('stock_code')
            if bool(re.search("^(2|4|8|9)\d{5}$", stock_code)) or stock_code in self.ignore_codes:
                continue
            symbol = get_symbol_by_code(stock_code)
            value_levels = self.api.get_pe_pb_levels_from_history(symbol=symbol)
            pb = value_levels.get('pb')
            pe = value_levels.get('pe')
            pe_koufei = value_levels.get('pe_koufei')
            info['pb'] = pb.get('median_10year') #默认十年
            info['pb_5'] = pb.get('median_5year')
            info['pb_all'] = pb.get('median_all')
            info['pb_temperature'] = pb.get('percent_10year')
            info['pb_temperature_5'] = pb.get('percent_5year')
            info['pb_temperature_all'] = pb.get('percent_all')

            info['pe'] = pe.get('median_10year')
            info['pe_5'] = pe.get('median_5year')
            info['pe_all'] = pe.get('median_all')
            info['pe_temperature'] = pe.get('percent_10year')
            info['pe_temperature_5'] = pe.get('percent_5year')
            info['pe_temperature_all'] = pe.get('percent_all')
            
            info['pe_koufei'] = pe_koufei.get('median_10year')
            info['pe_koufei_5'] = pe_koufei.get('median_5year')
            info['pe_koufei_all'] = pe_koufei.get('median_all')
            info['pe_koufei_temperature'] = pe_koufei.get('percent_10year')
            info['pe_koufei_temperature_5'] = pe_koufei.get('percent_5year')
            info['pe_koufei_temperature_all'] = pe_koufei.get('percent_all')
            stocks_info.append(info)
        self.stocks_info = stocks_info
    
    def parse_html_script(self, *, symbol ):
        html = self.api.get_history_html(symbol = symbol)
        print("html", html)
        soup = BeautifulSoup(html, "lxml")
        data = soup.find_all('script', type='text/javascript')
        print("data", data)
        script_content = data[-1].string
        json_string = script_content.split('var positions = ')[1]
        json_string = json_string.split('; ')[0]
        json_string = json_string.replace('\'', '\"')
        positions = json.loads(json_string)
        return {
            'positions': positions
        }
        # context = js2py.EvalJs()
        # execute_code = """
        #         var $ = function (selector) {
        #             return {
        #                 children: function () {
        #                     return {
        #                         click(){

        #                         }
        #                     }
        #                 }
        #             }
        #         };
        # """ + script_content
        # context.execute(execute_code)
        # positions = context.positions
        pb = positions.pb
        pe = positions.pe
        pe_koufei = positions.pe_koufei
        print(pb)
        print("pe", pe)
        print("pe_koufei", pe_koufei)

    def output(self):
        output_dir = f'{os.getcwd()}/outcome/pe_pb/'
        all_file_path = f'{output_dir}/{self.cur_date}_pe_pb_10.xlsx'
        df_all_stocks = pd.DataFrame(self.stocks_info).reset_index(drop=True)
        update_xlsx_file(all_file_path, df_all_stocks, '所有')

# wglh = Wglh()

if __name__ == '__main__':
    SaveValueLevel().save()
