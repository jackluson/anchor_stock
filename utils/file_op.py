'''
Desc:
File: /file_op.py
Project: utils
File Created: Sunday, 27th June 2021 12:29:28 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2021 Camel Lu
'''

import time
import datetime
import os


# 写json文件
def write_fund_json_data(data, filename, file_dir=None):
    import json
    if not file_dir:
        cur_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        file_dir = os.getcwd() + '/archive_data/json/' + cur_date + '/'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
        print("目录新建成功：%s" % file_dir)
    with open(file_dir + filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.close()
