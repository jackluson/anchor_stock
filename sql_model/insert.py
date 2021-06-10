'''
Desc: insert 相关语句
File: /insert.py
Project: sql_model
File Created: Thursday, 10th June 2021 11:20:43 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from db.connect import connect
from lib.mysnowflake import IdWorker

class StockInsert:
  def __init__(self):
        connect_instance = connect()
        self.connect_instance = connect_instance
        self.cursor = connect_instance.cursor()
        self.IdWorker = IdWorker()

  def generate_insert_sql(self, target_dict, table_name, ignore_list):
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
      snowflaw_id = self.IdWorker.get_id()
      industry_sql_insert = self.generate_insert_sql(
            industry_dict, 'shen_wan_industry', ['id'])
      self.cursor.execute(industry_sql_insert,
                            tuple([snowflaw_id, *industry_dict.values()]))
      self.connect_instance.commit()
