from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """启动定时任务"""
        self.scheduler.start()
    
    def add_job(self, func, trigger, **kwargs):
        """添加定时任务"""
        self.scheduler.add_job(func, trigger, **kwargs)
    
    def shutdown(self):
        """关闭定时任务"""
        self.scheduler.shutdown()

# 全局调度器实例
scheduler = Scheduler()
