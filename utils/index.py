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
import time
import json
import logging

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils.file_op import write_fund_json_data


def get_symbol_by_code(stock_code):
    """
    根据code规则输出是上证还是深证
    """
    if bool(re.search("^(6|9)\d{5}$", stock_code)):
        symbol = 'SH' + stock_code
    else:
        symbol = 'SZ' + stock_code
    return symbol


def get_request_header_key(entry_url, target_url, request_header_key, mime_type="json"):
    capabilities = DesiredCapabilities.CHROME
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    driver = webdriver.Chrome(options=chrome_options,
                              desired_capabilities=capabilities,)
    driver.get(entry_url)
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
    for log in logs:
        flag = log["method"] == "Network.responseReceived" and mime_type in log["params"][
            "response"]["mimeType"] and target_url == log["params"]["response"]["url"]
        if flag and log["params"]["response"]['requestHeaders']:
            request_header_key_value = log["params"]["response"]['requestHeaders'].get(
                request_header_key)
            driver.quit()
            line = f'此次爬取{request_header_key}: {request_header_key_value} '
            logging.info(line)
            return request_header_key_value
    driver.quit()
