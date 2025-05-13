"""
此模块定义信号处理器，用于在MainForm模型变化时自动更新StatusTypeNum模型
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from proceed.models import MainForm
from .models import StatusTypeNum
from .tasks import update_category_counts_async

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
def update_status_counts(sender, instance=None, created=False, **kwargs):
    """
    当MainForm模型实例保存或删除时，自动更新StatusTypeNum模型
    
    Args:
        sender: 发送信号的模型类
        instance: MainForm的实例
        created: 是否为新创建的实例
        **kwargs: 其他参数
    """
    # 判断是否需要更新状态计数
    update_status_needed = created  # 新记录肯定需要更新
    update_category_needed = created  # 新记录需要更新类别计数
    
    # 记录需要更新的类别
    categories_to_update = set()
    
    if not created and instance:
        # 检查是否是删除操作
        is_delete = kwargs.get('signal') == post_delete
        
        # 对于非创建的操作，检查更新的字段
        if kwargs.get('update_fields') is not None:
            update_fields = kwargs.get('update_fields')
            update_status_needed = 'handle' in update_fields or 'feedback_status' in update_fields
            update_category_needed = 'category' in update_fields
        else:
            # 如果没有指定更新字段，需要检查category是否变化
            if not is_delete and instance.pk in old_category:
                old_cat = old_category.get(instance.pk)
                new_cat = instance.category
                
                # 如果类别发生变化，记录需要更新的类别
                if old_cat != new_cat:
                    update_category_needed = True
                    if old_cat:  # 旧类别存在则需要更新
                        categories_to_update.add(old_cat)
                    if new_cat:  # 新类别存在则需要更新
                        categories_to_update.add(new_cat)
        
        # 删除操作，如果实例有类别，需要更新该类别计数
        if is_delete and instance.category:
            update_category_needed = True
            categories_to_update.add(instance.category)
        
    # 清理保存的旧值，避免内存泄漏
    if instance and instance.pk in old_category:
        del old_category[instance.pk]
    
    # 更新状态计数
    if update_status_needed or kwargs.get('update_fields') is None:
        StatusTypeNum.update_counts(update_category=False)  # 不在这里更新类别计数
    
    # 异步更新类别计数
    if update_category_needed:
        if categories_to_update:
            # 如果有特定类别需要更新，逐个更新
            for category in categories_to_update:
                update_category_counts_async(category)
        else:
            # 如果没有特定类别或无法确定，更新所有类别
            update_category_counts_async()
