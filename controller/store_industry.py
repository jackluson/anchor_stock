'''
Desc: 申万行业入库
File: /industry_entrant.py
Project: anchor_stock
File Created: Thursday, 10th June 2021 10:58:06 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import json
from pprint import pprint
from sql_model.insert import StockInsert

def store_industry():
    industry_json_path = "./input/p_sysapi1016.json"
    each_insert = StockInsert()
    def traverse_industry(list, *, level=0):
        for industry_item in list:
            industry_dict = {
                'industry_code': industry_item['SORTCODE'],
                'industry_name': industry_item['SORTNAME'],
                'industry_type': level,
                'p_industry_id': industry_item['PARENTCODE']
            }
            each_insert.insert_industry_data(industry_dict)
            item_childrem = industry_item.get('children')
            if item_childrem:
                traverse_industry(item_childrem, level=level+1)

    with open(industry_json_path) as json_file:
        industry_data = json.load(json_file)
        shen_wan_industry_data = industry_data['records'][0]['children']
        level = 0
        traverse_industry(shen_wan_industry_data, level=level)
if __name__ == '__main__':
    store_industry()
