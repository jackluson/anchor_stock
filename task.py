from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from controller.store_stock_daily import store_stock_daily
from controller.save_value_level import SaveValueLevel

def store_stock_industry_and_daily():
    # store_stock_industry()  # 执行行业股票信息入库
    store_stock_daily()  # 执行股票每天变动信息入库
    SaveValueLevel().save()

def bootstrap_stock_daily_scheduler():
    print(f"本轮定时任务开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    # 添加任务,时间间隔2S
    scheduler.add_job(
        store_stock_industry_and_daily,
        trigger='cron',
        day_of_week='mon-fri',
        hour=15,
        minute=30,
    )
    scheduler.start()
    
if __name__ == '__main__':
    bootstrap_stock_daily_scheduler()
