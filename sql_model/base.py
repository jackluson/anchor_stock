'''
Desc:
File: /base.py
Project: sql_model
File Created: Sunday, 3rd April 2022 5:31:31 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
from db.connect import connect

class BaseSqlModel(object):
    def __init__(self):
        connect_instance = connect()
        self.connect = connect_instance.get('connect')
        self.cursor = connect_instance.get('cursor')
        self.dict_cursor = connect_instance.get('dict_cursor')
