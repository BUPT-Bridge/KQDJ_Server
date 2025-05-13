"""
异步任务模块，用于处理不需要立即完成的后台任务
"""
import threading
from django.db import transaction

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
