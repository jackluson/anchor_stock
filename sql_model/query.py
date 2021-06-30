'''
Desc: query 相关语句
File: /query.py
Project: sql_model
File Created: Friday, 11th June 2021 12:59:09 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import pymysql
from db.connect import connect

class StockQuery:
    def __init__(self):
        connect_instance = connect()
        self.connect = connect_instance.get('connect')
        self.cursor = connect_instance.get('cursor')
        self.dict_cursor = connect_instance.get('dict_cursor')

    def query_industry_data(self):
        query_industry_sql = "SELECT a1.industry_name AS '三级行业', a1.industry_code as '三级行业代码', a2.industry_name AS '二级行业',a2.industry_code as '二级行业代码', a3.industry_name AS '一级行业', a3.industry_code as '一级行业代码' FROM shen_wan_industry as a1 \
        LEFT JOIN shen_wan_industry as a2 ON a2.industry_code = a1.p_industry_code \
            LEFT JOIN shen_wan_industry as a3 ON a3.industry_code = a2.p_industry_code \
            WHERE a1.industry_type=2 AND a2.industry_type=1 AND a3.industry_type = 0"
        self.cursor.execute(query_industry_sql)
        results = self.cursor.fetchall()
        return results

    def query_all_stock(self, date=None):
        print("date", date)
        if date == None:
            query_stock_sql = "SELECT stock_code FROM stock_industry"
            self.dict_cursor.execute(query_stock_sql)
        else:
            query_stock_sql = "SELECT stock_code FROM stock_industry as a WHERE a.stock_code NOT IN ( SELECT b.`code` FROM stock_daily_info AS b WHERE b.`timestamp` = %s )"
            self.dict_cursor.execute(query_stock_sql, [date])

        results = self.dict_cursor.fetchall()
        return results
