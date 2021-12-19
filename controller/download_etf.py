'''
Desc: ETF下载
File: /download_etf.py
Project: controller
File Created: Monday, 6th December 2021 9:32:04 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import json
import pandas as pd
from stock_info.sse_api import ApiSSE
from stock_info.szse_api import ApiSZSE


def download_sse_etf():
    each_api = ApiSSE()
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

        etf_name = '{name}.json'.format(
            name=subClass.get('name'))
        with open('./data/sh/' + etf_name, 'w', encoding='utf-8') as f:
            json.dump(fund_list.get('result'), f, ensure_ascii=False, indent=2)


def download_szse_etf():
    each_api = ApiSZSE()
    fund_list = each_api.get_etf_fund_list()
    # print("fund_list", fund_list)
    etf_items = fund_list[0].get('data')
    etf_cols = fund_list[0].get('metadata').get('cols')
    nets_items = fund_list[1].get('data')
    df_etf = pd.DataFrame(etf_items)
    df_nets = pd.DataFrame(nets_items)
    df_nets = df_nets.set_index('jjdm')
    # print("df_nets", df_nets)
    df_etf = df_etf[['sys_key', 'dqgm', 'glrmc', 'nhzs']]
    df_etf['sys_key'] = df_etf['sys_key'].str.slice(-14, -8)
    # print(df_etf)
    for index, etf_item in df_etf.iterrows():
        code = etf_item['sys_key']
        jjjc = df_nets.loc[code]['jjjc']
        jjjz = df_nets.loc[code]['jjjz']
        df_etf.at[index, '基金简称'] = jjjc
        df_etf.at[index, '基金净值'] = jjjz
    etf_cols['dqgm'] = '规模'
    df_etf.rename(columns=etf_cols, inplace=True)
    df_etf.set_index('证券代码', inplace=True)
    return df_etf


if __name__ == '__main__':
    download_sse_etf()
