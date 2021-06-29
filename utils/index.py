'''
Desc: 工具函数
File: /index.py
Project: utils
File Created: Tuesday, 29th June 2021 11:27:46 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''
import re

"""
根据code规则输出是上证还是深证
"""
def get_symbol_by_code(stock_code):
    if bool(re.search("^(6|9)\d{5}$", stock_code)):
        symbol = 'SH' + stock_code
    else:
        symbol = 'SZ' + stock_code
    return symbol
