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
from threading import Thread, Lock

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


def get_request_header_key(entry_url, host, request_header_key, mime_type="json"):
    capabilities = DesiredCapabilities.CHROME
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    driver = webdriver.Chrome(options=chrome_options,
                              desired_capabilities=capabilities,)
    driver.get(entry_url)
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
    # with open('./logs.json', 'w', encoding='utf-8') as f:
    #     json.dump(logs, f, ensure_ascii=False, indent=2)
    #     f.close()
    for log in logs:
        flag = log["method"] == "Network.requestWillBeSentExtraInfo" and host
        headers = log["params"].get('headers')
        request_header_key_value = headers.get(
            request_header_key) if headers else None
        host_url = headers.get('Host') if headers else None
        if flag and request_header_key_value and host_url in host:
            driver.quit()
            line = f'此次爬取{request_header_key}: {request_header_key_value} '
            logging.info(line)
            return request_header_key_value
    driver.quit()


def bootstrap_thread(target_fn, total, thread_count=2):
    threaders = []
    start_time = time.time()
    # 如果少于10个，只开一个线程
    if total < 10:
        thread_count = 1
    step_num = total / thread_count
    for i in range(thread_count):
        # start = steps[i]['start']
        # end = steps[i]['end']
        start = i * step_num
        end = (i + 1) * step_num
        t = Thread(target=target_fn, args=(int(start), int(end)))
        t.setDaemon(True)
        threaders.append(t)
        t.start()
    for threader in threaders:
        threader.join()
    end_time = time.time()
    print(total, 'run time is %s' % (end_time - start_time))


def lock_process(func):
    lock = Lock()

    def wrapper(self, *args):
        lock.acquire()
        result = func(self, *args)
        lock.release()
        return result
    return wrapper
