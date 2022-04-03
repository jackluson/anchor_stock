'''
Date: 2022-04-03 17:03:07
LastEditTime: 2022-04-03 17:04:25
Description: Update sql 语句封装
'''
from .base import BaseSqlModel

class UpdateSql(BaseSqlModel):
    def __init__(self):
        super().__init__()

    def udpate_etf_date(self, code, market, found_date, delist_date):
        # 更新etf成立日期
        sql_update = "UPDATE etf_fund SET found_date='{found_date}', delist_date='{delist_date}' WHERE market='{market}' AND code='{symbol}';".format(
            found_date=found_date,
            delist_date=delist_date,
            market=market,
            symbol=code
        )
        sql = sql_update.replace('\'None\'', 'NULL')
        self.cursor.execute(sql)
        self.connect.commit()
