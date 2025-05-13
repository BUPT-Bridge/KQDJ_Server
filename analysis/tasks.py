"""
异步任务模块，用于处理不需要立即完成的后台任务
"""
import threading
import time
from datetime import datetime

def update_category_counts_async(specific_category=None):
    """
    在后台线程中异步更新类别计数
    
    Args:
        specific_category: 要更新的特定类别，如果为None则更新所有类别
    """
    def task():
        # 导入放在函数内部以避免循环导入
        from .models import StatusTypeNum
        
        try:
            # 使用优化的方法更新类别计数
            StatusTypeNum.update_category_counts(optimize=True, specific_category=specific_category)
        except Exception as e:
            print(f"更新类别计数失败: {str(e)}")

    # 创建并启动一个单独的线程
    thread = threading.Thread(target=task)
    thread.daemon = True  # 设置为守护线程，这样它不会阻止程序退出
    thread.start()

def update_view_counts_async():
    """
    在后台线程中异步更新访问量和注册量统计
    """
    def task():
        # 导入放在函数内部以避免循环导入
        from .models import ViewNum
        
        try:
            # 更新今天的访问量和注册量
            ViewNum.update_today_counts()
            print(f"[{datetime.now()}] 访问量和注册量统计更新成功")
        except Exception as e:
            print(f"[{datetime.now()}] 更新访问量和注册量统计失败: {str(e)}")

    # 创建并启动一个单独的线程
    thread = threading.Thread(target=task)
    thread.daemon = True  # 设置为守护线程，这样它不会阻止程序退出
    thread.start()

def start_periodic_tasks():
    """
    启动定期执行的任务
    """
    def run_periodic_tasks():
        # 定时更新访问量和注册量统计
        while True:
            try:
                update_view_counts_async()
            except Exception as e:
                print(f"定时任务执行失败: {str(e)}")
            
            # 等待10分钟
            time.sleep(600)  # 10分钟 = 600秒
    
    # 创建并启动定时任务线程
    thread = threading.Thread(target=run_periodic_tasks)
    thread.daemon = True  # 设置为守护线程，这样它不会阻止程序退出
    thread.start()
    print("定时统计任务已启动，每10分钟更新一次访问量和注册量")
