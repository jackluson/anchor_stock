'''
Desc:
File: /stock.py
File Created: Sunday, 25th December 2022 9:02:50 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2022 Camel Lu
'''
import sys
sys.path.append('.')

from sqlalchemy import Table
from models.var import ORM_Base, engine, Model
from infra.lib.mysnowflake import IdWorker

stock_profile_tablename = 'stock_profile'

stock_profile_table = Table(stock_profile_tablename, ORM_Base.metadata, autoload=True, autoload_with=engine)

idWorker = IdWorker()

class StockProfile(ORM_Base, Model):
    __table__ = stock_profile_table
    def __init__(self, **kwargs):
            self.id = idWorker.get_id()
            column_keys = self.__table__.columns.keys()
            udpate_data = dict()
            for key in kwargs.keys():
                if key not in column_keys:
                    continue
                else:
                    udpate_data[key] = kwargs[key]
            ORM_Base.__init__(self, **udpate_data)
            Model.__init__(self, **kwargs, id = self.id)

    def __repr__(self):
        return f"Stock Profile(id={self.id!r}, code={self.stock_code!r}, name={self.stock_name!r})"
