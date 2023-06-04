'''
Desc:
File: /etf_quotos.py
File Created: Saturday, 3rd June 2023 10:41:35 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2023 Camel Lu
'''
import sys
sys.path.append('.')
from sqlalchemy.orm import registry, relationship
from sqlalchemy import (UniqueConstraint, ForeignKey, Table, String, Float, Column, text, DateTime, BigInteger, func)
from sqlalchemy.dialects.mysql import insert
from db.engine import get_engine
from models.var import ORM_Base, Model
from lib.mysnowflake import IdWorker
from db.engine import get_engine, get_session
from utils.index import timeit

engine = get_engine()
etf_fund_table_name = 'etf_fund'
etf_fund_table = Table(etf_fund_table_name, ORM_Base.metadata, autoload=True, autoload_with=engine)
idWorker = IdWorker()

class EtfFund(ORM_Base, Model):
    __table__ = etf_fund_table

    def __init__(self, **kwargs):
        self.id = idWorker.get_id()
        column_keys = self.__table__.columns.keys()
        print("column_keys", column_keys)
        udpate_data = dict()
        for key in kwargs.keys():
            if key not in column_keys:
                continue
            else:
                udpate_data[key] = kwargs[key]
        ORM_Base.__init__(self, **udpate_data)
        Model.__init__(self, **kwargs, id = self.id)

    def __repr__(self):
        return f"EtfFund(id={self.id!r}, name={self.name!r}, code={self.code!r})"


class EtfIndicator(ORM_Base, Model):
    __tablename__ = 'etf_indicator'
    __table_args__ = {'extend_existing': True}
    id = Column(BigInteger, primary_key=True)
    code_key = f"{etf_fund_table_name}.code"
    code =  Column(String(10), ForeignKey(code_key), nullable=False, comment='代码')
    name = Column(String(24), nullable=False, comment='名称')
    price = Column(Float(4, True), comment='最新价')
    volume = Column(Float(4, True), comment='成交量')
    amount = Column(Float(4, True), comment='成交额')
    net_value = Column(Float(4, True), comment='净值')
    accum_net_value = Column(Float(4, True), comment='累计净值')
    amplitude = Column(Float(4, True), comment='振幅')
    premium_rate = Column(Float(4, True), comment='溢价率')
    share = Column(Float(4, True), comment='份额')
    asset = Column(Float(4, True), comment='资产净值')
    update_time = Column(DateTime,  server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), onupdate=func.now(), comment='更新时间') 
    create_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

    UniqueConstraint(code, name='uix_1')
    etf_fund = relationship('EtfFund', backref='etf_indicator')

    def __init__(self, **kwargs):
        self.id = idWorker.get_id()
        ORM_Base.__init__(self, **kwargs)
        Model.__init__(self, **kwargs, id = self.id)

    def __repr__(self):
        return f"EtfIndicator(id={self.id!r}, code={self.code!r}, name={self.name!r})"


    @timeit
    @staticmethod
    def bulk_save(data_list: list):
        """批量保存(新增或者更新, id只能是新增)

        Args:
            data_list (list): _description_
        """
        ups_stmt = insert(EtfIndicator).values(
            data_list
        )
        update_dict = {x.name: x for x in ups_stmt.inserted}
        # del update_dict['id']
        del update_dict['code']
        ups_stmt = ups_stmt.on_duplicate_key_update(update_dict)
        with engine.connect() as conn:
            conn.execute(ups_stmt)
            conn.commit()

def create():
    EtfIndicator.__table__.drop(engine)
    ORM_Base.metadata.create_all(engine)
    # mapper_registry.metadata.create_all(engine)

def drop():
    EtfIndicator.__table__.drop(engine)

if __name__ == '__main__':
    create()
