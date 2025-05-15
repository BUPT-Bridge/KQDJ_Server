"""
此模块定义信号处理器，用于在MainForm模型变化时自动更新相关模型
优化了信号处理逻辑，合并了相关操作以提高性能
"""
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from proceed.models import MainForm
from proceed.utils.choice import UNHANDLED
from .models import StatusTypeNum, FormUserRelation
from .tasks import update_category_counts_async, create_form_user_relation_async

# 配置日志
logger = logging.getLogger(__name__)

# 保存instance的旧category值，用于对比是否发生变化
old_category = {}

@receiver(pre_save, sender=MainForm)
def store_old_category(sender, instance=None, **kwargs):
    """
    在MainForm保存前，记录旧的category值
    """
    if instance.pk:  # 只有已存在的实例才需要记录
        try:
            old_instance = MainForm.objects.get(pk=instance.pk)
            old_category[instance.pk] = old_instance.category
        except MainForm.DoesNotExist:
            pass

@receiver([post_save, post_delete], sender=MainForm)
def handle_mainform_change(sender, instance=None, created=False, **kwargs):
    """
    当MainForm模型实例变化时，集中处理所有相关更新操作
    """
    # 1. 处理状态和类别计数更新
    # 确定是否是删除操作
    is_delete = kwargs.get('signal') == post_delete
    
    # 确定需要更新哪些内容
    update_fields = kwargs.get('update_fields')
    needs_status_update = created or (update_fields is None) or (update_fields and ('handle' in update_fields or 'feedback_status' in update_fields))
    needs_category_update = created or (update_fields is None) or (update_fields and 'category' in update_fields)
    
    # 确定需要更新的类别
    categories_to_update = set()
    
    # 处理类别变更
    if not created and not is_delete and instance and instance.pk in old_category:
        old_cat = old_category.get(instance.pk)
        new_cat = instance.category
        
        # 如果类别发生变化，记录需要更新的类别
        if old_cat != new_cat:
            needs_category_update = True
            if old_cat:
                categories_to_update.add(old_cat)
            if new_cat:
                categories_to_update.add(new_cat)
    
    # 处理删除操作
    if is_delete and instance and instance.category:
        needs_category_update = True
        categories_to_update.add(instance.category)
    
    # 清理保存的旧值，避免内存泄漏
    if instance and instance.pk in old_category:
        del old_category[instance.pk]
    
    # 执行更新操作
    if needs_status_update:
        StatusTypeNum.update_counts(update_category=False)  # 不在这里更新类别计数
    
    # 异步更新类别计数
    if needs_category_update:
        if categories_to_update:
            for category in categories_to_update:
                update_category_counts_async(category)
        else:
            update_category_counts_async()
    
    # 2. 处理表单用户关系更新 - 改为使用延迟处理
    if not is_delete and instance and instance.handle == UNHANDLED:  # 只处理未处理状态的表单
        try:
            # 检查是否为更新category和title字段的操作
            update_fields = kwargs.get('update_fields')
            fields_updated = created or (update_fields is None) or (
                update_fields and ('category' in update_fields or 'title' in update_fields)
            )
            
            # 只有在更新了这些字段后，才触发创建关系
            if fields_updated and instance.category and instance.title:
                # 设置延迟，避免与AI分析任务冲突
                create_form_user_relation_async.apply_async(
                    args=[instance.pk], 
                    countdown=3  # 延迟3秒，避免冲突
                )
        except Exception as e:
            logger.error(f"更新FormUserRelation时出错: {str(e)}")
    elif instance and instance.handle != UNHANDLED:
        # 如果表单状态不是未处理，尝试删除对应的关系记录
        try:
            FormUserRelation.objects.filter(main_form=instance).delete()
            logger.info(f"已删除非未处理状态表单的关系记录: {instance.pk}")
        except Exception as e:
            logger.error(f"清理非未处理表单关系时出错: {str(e)}")
