'''
Desc:
File: /baostock_api.py
File Created: Sunday, 5th December 2021 8:15:35 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import baostock as bs
import pandas as pd


def main():

    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。“分钟线”不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    stock_list = [{
        'market': 'sh',
        'name': '沪深300',
        'code': '000300'
    }]
    symbol = stock_list[0].get('market') + '.' + stock_list[0].get('code')
    print("symbol", symbol)
    rs = bs.query_history_k_data_plus(symbol,
                                      "date,code,open,high,low,close,volume,amount,adjustflag,pctChg",
                                      start_date='2021-07-01', end_date='2021-07-31',
                                      frequency="m", adjustflag="3")
    print('query_history_k_data_plus respond error_code:'+rs.error_code)
    print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 结果集输出到csv文件 ####
    # result.to_csv("D:\\history_A_stock_k_data.csv", index=False)
    print(result)

    #### 登出系统 ####
    bs.logout()


if __name__ == '__main__':
    main()
