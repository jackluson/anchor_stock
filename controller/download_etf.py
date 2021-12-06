'''
Desc: ETF下载
File: /download_etf.py
Project: controller
File Created: Monday, 6th December 2021 9:32:04 pm
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

from stock_info.sse_api import ApiSSE
import json


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


if __name__ == '__main__':
    download_sse_etf
