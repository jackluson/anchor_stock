'''
Desc: ETF下载
File: /download_etf.py
Project: controller
File Created: Monday, 6th December 2021 9:32:04 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
from random import random
from time import time
import pandas as pd
from sql_model.insert import StockInsert
from stock_info.sse_api import ApiSSE
from stock_info.szse_api import ApiSZSE


def store_sse_etf():
    each_api = ApiSSE()
    each_insert = StockInsert()
    subClass_list = [
        {
            'name': '单市场ETF',
            'code': '01'
        },
        {
            'name': '跨市场ETF',
            'code': '03,08'
        },
        {
            'name': '跨境ETF',
            'code': '04'
        },
        {
            'name': '债券',
            'code': '02'
        },
        {
            'name': '黄金ETF',
            'code': '06'
        },
        {
            'name': '单市场科创板ETF',
            'code': '09'
        },
        {
            'name': '跨市场科创板ETF',
            'code': '31'
        }
    ]
    for subClass in subClass_list:
        code = subClass.get('code')
        fund_list = each_api.get_etf_fund_list(subClass=code)
        columns = [
            'id',
            'fundCode',
            'fundAbbr',
            'secNameFull',
            'INDEX_NAME',
            'INDEX_CODE',
            'subClass',
            'companyName',
        ]
        df_fund_list = pd.DataFrame(fund_list.get('result'), columns=columns)
        df_fund_list['market'] = 'sh'
        for index in range(len(df_fund_list)):
            id = int(time() * int((index + random()) * 10000)) + \
                int(random() * 10000) + index
            df_fund_list.at[index, 'id'] = id
        each_insert.batch_insert_etf_fund(df_fund_list.values.tolist())
        # etf_name = '{name}.json'.format(
        #     name=subClass.get('name'))
        # with open('./data/sh/' + etf_name, 'w', encoding='utf-8') as f:
        #     json.dump(fund_list.get('result'), f, ensure_ascii=False, indent=2)


def store_szse_etf():
    each_api = ApiSZSE()
    fund_list = each_api.get_etf_fund_list()
    etf_items = fund_list[0].get('data')
    # etf_cols = fund_list[0].get('metadata').get('cols')
    nets_items = fund_list[1].get('data')
    columns = [
        'id',
        'sys_key',
        'fundAbbr',
        'secNameFull',
        'nhzs',
        'INDEX_CODE',
        'subClass',
        # 'companyName',
        # 'dqgm',
        'glrmc',
    ]
    df_etf = pd.DataFrame(etf_items, columns=columns)
    df_etf.fillna('', inplace=True)
    df_nets = pd.DataFrame(nets_items)
    df_nets = df_nets.set_index('jjdm')
    # df_etf = df_etf[[*, 'sys_key', 'dqgm', 'glrmc', 'nhzs']]
    df_etf['sys_key'] = df_etf['sys_key'].str.slice(-14, -8)
    for index, etf_item in df_etf.iterrows():
        id = int(time() * int((index + random()) * 10000)) + \
            int(random() * 10000) + index
        df_etf.at[index, 'id'] = id
        code = etf_item['sys_key']
        index_info = etf_item['nhzs']
        jjjc = df_nets.loc[code]['jjjc']
        # jjjz = df_nets.loc[code]['jjjz']
        df_etf.at[index, 'fundAbbr'] = jjjc
        # df_etf.at[index, '基金净值'] = jjjz
        index_code = ''
        index_name = ''
        if index_info:
            index_code = index_info.split(' ')[0]
            index_name = index_info.split(' ')[1]
        df_etf.at[index, 'nhzs'] = index_name
        df_etf.at[index, 'INDEX_CODE'] = index_code
    rename_map = {
        'sys_key': 'fundCode',
        'glrmc': 'companyName',
        'nhzs': 'INDEX_NAME'
    }
    df_etf.rename(columns=rename_map, inplace=True)
    df_etf['market'] = 'sz'
    each_insert = StockInsert()
    each_insert.batch_insert_etf_fund(df_etf.values.tolist())


def store_etf():
    store_sse_etf()
    store_szse_etf()


if __name__ == '__main__':
    store_etf()
