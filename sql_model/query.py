'''
Desc: query 相关语句
File: /query.py
Project: sql_model
File Created: Friday, 11th June 2021 12:59:09 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from datetime import datetime
from infra.sql.stocks.query import StockQuery as InfraStockQuery
from .base import BaseSqlModel


class StockQuery(BaseSqlModel):
    infra_stock_query:InfraStockQuery = None
    def __init__(self):
        super().__init__()
        self.infra_stock_query = InfraStockQuery()

    def query_industry_data(self):
        query_industry_sql = "SELECT a1.industry_name AS '三级行业', a1.industry_code as '三级行业代码', a2.industry_name AS '二级行业',a2.industry_code as '二级行业代码', a3.industry_name AS '一级行业', a3.industry_code as '一级行业代码' FROM shen_wan_industry as a1 \
        LEFT JOIN shen_wan_industry as a2 ON a2.industry_code = a1.p_industry_code \
            LEFT JOIN shen_wan_industry as a3 ON a3.industry_code = a2.p_industry_code \
            WHERE a1.industry_type=2 AND a2.industry_type=1 AND a3.industry_type = 0"
        self.cursor.execute(query_industry_sql)
        results = self.cursor.fetchall()
        return results

    def query_all_stock(self, date=None):
        return self.infra_stock_query.query_all_stock(date=date)

    def query_stock_with_st(self, date=None):
        query_stock_sql = "SELECT t.stock_code, t.stock_name, t.industry_name_third, t1.org_name, t1.actual_controller, t1.classi_name, t1.main_operation_business FROM stock_industry as t \
LEFT JOIN stock_profile as t1 ON t.stock_code = t1.stock_code WHERE t.delist_status NOT IN (1) AND t.stock_name LIKE '%ST%' AND t.stock_name NOT LIKE '%B%' AND t.delist IS NULL"
        self.dict_cursor.execute(query_stock_sql)
        results = self.dict_cursor.fetchall()
        return results

    def query_special_stock_main_financial(self, code, timestamp):
        """ 查看股票主要财务数据
        """
        query_stock_sql = "SELECT b.price, b.pe_ttm, b.pe_lyr, b.pe_forecast, a.*, c.industry_name_third, c.industry_name_second, c.industry_name_first, b.goodwill_in_net_assets, b.market_capital FROM stock_main_financial_indicator as a LEFT JOIN stock_daily_info as b ON a.code = b.code LEFT JOIN stock_industry as c ON a.code = c.stock_code WHERE a.code = %s AND b.timestamp = %s"
        self.dict_cursor.execute(query_stock_sql, [code, timestamp])

        results = self.dict_cursor.fetchall()
        return results

    def query_etf(self, found_date=None):
        """
        查询ETF
        Args:
            market ([str]): ['sh', 'sz']
        """
        found_date = found_date if found_date else datetime.now().strftime("%Y-%m-%d")
        query_stock_sql = "SELECT a.code, a.name, a.market FROM etf_fund as a WHERE a.delist_date IS NULL AND a.found_date <= %s"
        self.dict_cursor.execute(query_stock_sql, [found_date])

        results = self.dict_cursor.fetchall()
        return results
