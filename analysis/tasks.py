"""
异步任务模块，用于处理不需要立即完成的后台任务
"""
import threading
import time
from datetime import datetime
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_category_counts_async(specific_category=None):
    """
    异步更新类别计数
    """
    from .models import StatusTypeNum
    try:
        if specific_category:
            StatusTypeNum.update_category_counts(specific_category=specific_category)
        else:
            StatusTypeNum.update_category_counts()
        return True
    except Exception as e:
        logger.error(f"异步更新类别计数失败: {str(e)}")
        return False

@shared_task
def create_form_user_relation_async(form_pk):
    """
    异步创建表单用户关系
    在MainForm表单字段生成后执行
    只处理未处理状态的表单
    """
    from proceed.models import MainForm
    from .models import FormUserRelation
    from proceed.utils.choice import UNHANDLED
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 重新获取表单实例，确保获取最新状态
        main_form = MainForm.objects.filter(pk=form_pk).first()
        
        if not main_form:
            logger.error(f"找不到ID为{form_pk}的MainForm实例")
            return False
        
        # 只处理未处理状态的表单
        if main_form.handle != UNHANDLED:
            logger.info(f"表单 {main_form.pk} 不是未处理状态，不创建关系")
            # 删除可能存在的关系
            FormUserRelation.objects.filter(main_form=main_form).delete()
            return False
            
        # 检查必要字段是否已经生成
        if not main_form.category or not main_form.title:
            # 如果字段仍未生成，可能是AI分析任务还未完成或失败
            # 这种情况下，就不创建关系，依赖后续的signal触发
            logger.warning(f"表单 {main_form.pk} 的必要字段尚未生成，不创建关系")
            return False
            
        # 创建或更新关系
        relation = FormUserRelation.create_or_update_from_form(main_form)
        return bool(relation)
        
    except Exception as e:
        logger.error(f"创建表单用户关系失败: {str(e)}")
        return False

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

@shared_task
def analyze_form_content_async(form_id):
    """
    异步分析表单内容并更新表单信息
    """
    from proceed.models import MainForm
    from proceed.utils.analyze_content import analyze_content
    from proceed.manager import MainFormManager
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 获取表单
        main_form = MainForm.objects.filter(pk=form_id).first()
        
        if not main_form:
            logger.error(f"找不到ID为{form_id}的MainForm实例")
            return False
        
        # 分析内容
        logger.info(f"开始分析表单 {form_id} 的内容")
        form_type, title, category = analyze_content(main_form.content)
        
        # 更新表单信息
        logger.info(f"更新表单 {form_id} 的类型和标题: {form_type}, {title}, {category}")
        MainForm.query_manager.update_form_type_and_title(
            form_id, form_type, title, category
        )
        
        # 表单更新后，信号会自动触发create_form_user_relation_async任务
        # 不需要在这里明确调用
        
        return True
    except Exception as e:
        logger.error(f"异步分析表单内容失败: {str(e)}")
        return False

@shared_task
def generate_solution_suggestion_async(relation_id):
    """
    异步生成解决方案建议
    """
    from .models import FormUserRelation
    import logging
    import time
    
    logger = logging.getLogger(__name__)
    
    try:
        # 获取关系对象
        relation = FormUserRelation.objects.get(id=relation_id)
        
        # 添加延迟，避免与其他大模型调用冲突
        time.sleep(3)
        
        # 生成解决方案建议
        logger.info(f"开始为表单 {relation.main_form_id} 生成解决方案建议")
        
        # 调用原方法生成建议
        relation.generate_solution_suggestion()
        
        logger.info(f"表单 {relation.main_form_id} 的解决方案建议生成完成")
        return True
    except Exception as e:
        logger.error(f"生成解决方案建议失败: {str(e)}")
        return False
