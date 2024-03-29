'''
Desc: insert 相关语句
File: /insert.py
Project: sql_model
File Created: Thursday, 10th June 2021 11:20:43 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from utils.index import lock_process
from .base import BaseSqlModel
from infra.lib.mysnowflake import IdWorker

class StockInsert(BaseSqlModel):
    def __init__(self):
        super().__init__()
        self.IdWorker = IdWorker()

    def generate_insert_sql(self, target_dict, table_name, ignore_list):
        # 拼接sql
        keys = 'id,' + ','.join(target_dict.keys())
        values = ','.join(['%s'] * (len(target_dict) + 1))
        update_values = ''
        for key in target_dict.keys():
            if key in ignore_list:
                continue
            update_values = update_values + '{0}=VALUES({0}),'.format(key)
        sql_insert = "INSERT INTO {table} ({keys}) VALUES ({values})  ON DUPLICATE KEY UPDATE {update_values}; ".format(
            table=table_name,
            keys=keys,
            values=values,
            update_values=update_values[0:-1]
        )
        return sql_insert

    def insert_industry_data(self, industry_dict):
        # 入库申万行业数据
        snowflaw_id = self.IdWorker.get_id()
        industry_sql_insert = self.generate_insert_sql(
            industry_dict, 'shen_wan_industry', ['id'])
        self.cursor.execute(industry_sql_insert,
                            tuple([snowflaw_id, *industry_dict.values()]))
        self.connect.commit()

    # 入库股票行业信息
    def insert_stock_industry_data(self, stock_dict):
        snowflaw_id = self.IdWorker.get_id()
        stock_sql_insert = self.generate_insert_sql(
            stock_dict, 'stock_industry', ['id', 'code'])
        # print('sql', stock_sql_insert)
        # print('value', stock_dict.values())
        self.cursor.execute(stock_sql_insert,
                            tuple([snowflaw_id, *stock_dict.values()]))
        self.connect.commit()
    
    @lock_process
    def insert_stock_profile(self, profile_dict):
        # 入库股票简介数据
        snowflaw_id = self.IdWorker.get_id()
        stock_sql_insert = self.generate_insert_sql(
            profile_dict, 'stock_profile', ['id'])
        self.cursor.execute(stock_sql_insert,
                            tuple([snowflaw_id, *profile_dict.values()]))
        self.connect.commit()

    @lock_process
    def insert_stock_daily_data(self, stock_dict):
        # 入库股票日常股价等信息
        snowflaw_id = self.IdWorker.get_id()
        stock_sql_insert = self.generate_insert_sql(
            stock_dict, 'stock_daily_info', ['id'])
        self.cursor.execute(stock_sql_insert,
                            tuple([snowflaw_id, *stock_dict.values()]))
        self.connect.commit()

    def insert_stock_financial_indicator(self, financial_indicator_dict):
        # 入库财务指标等数据
        snowflaw_id = self.IdWorker.get_id()
        stock_sql_insert = self.generate_insert_sql(
            financial_indicator_dict, 'stock_main_financial_indicator', ['id'])
        self.cursor.execute(stock_sql_insert,
                            tuple([snowflaw_id, *financial_indicator_dict.values()]))
        self.connect.commit()

    def batch_insert_etf_fund(self, fund_list):
        etf_dict = {
            'code': '',
            'name': '',
            'full_name': '',
            'index_name': '',
            'index_code': '',
            'type': '',
            'company': '',
            # 'found_date': '',
            # 'delist_date': '',
            'market': ''
        }# 保持与sq表l设计顺序一致
        etf_sql_insert = self.generate_insert_sql(
            etf_dict, 'etf_fund', ['id', 'code'])
        self.cursor.executemany(etf_sql_insert, fund_list)
        self.connect.commit()
