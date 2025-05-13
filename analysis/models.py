from django.db import models
from proceed.models import MainForm
from proceed.utils.choice import UNHANDLED, PROCESSING, HANDLED, NEED_FEEDBACK

class StatusTypeNum(models.Model):
    """状态数量模型"""
    Unhandle = models.IntegerField(default=0, verbose_name='未处理数量')
    Handling = models.IntegerField(default=0, verbose_name='处理中数量')
    Handled = models.IntegerField(default=0, verbose_name='已处理数量')
    WaitCallback = models.IntegerField(default=0, verbose_name='待回访数量')
    
    PropertyDispute = models.IntegerField(default=0, verbose_name='物业纠纷类数量')
    PublicFacility = models.IntegerField(default=0, verbose_name='公共设施维护类数量')
    Environment = models.IntegerField(default=0, verbose_name='环境卫生与秩序类数量')
    NeighborConflict = models.IntegerField(default=0, verbose_name='邻里矛盾类数量')

    class Meta:
        verbose_name = '状态数量'
        verbose_name_plural = '状态数量'

    def __str__(self):
        return f"未处理数量: {self.Unhandle}, 处理中数量: {self.Handling}, 已处理数量: {self.Handled}, 待回访数量: {self.WaitCallback}"
    
    # 类别与字段映射，定义为类变量方便重用
    CATEGORY_FIELD_MAP = {
        '物业纠纷类': 'PropertyDispute',
        '公共设施维护类': 'PublicFacility',
        '环境卫生与秩序类': 'Environment',
        '邻里矛盾类': 'NeighborConflict',
    }
    
    @classmethod
    def update_category_counts(cls, optimize=True, specific_category=None, save_to_db=True, instance=None):
        """
        只更新类别计数，不更新状态计数
        
        Args:
            optimize: 是否使用优化方式（单次查询）
            specific_category: 指定要更新的特定类别，如果为None则更新所有类别
            save_to_db: 是否立即保存到数据库
            instance: 如果提供，则使用此实例而不是创建新的
        
        Returns:
            更新后的StatusTypeNum实例
        """
        # 获取或创建StatusTypeNum实例
        if instance is None:
            status_num, created = cls.objects.get_or_create(id=1)
        else:
            status_num = instance
            
        if optimize:
            from django.db.models import Count, Q
            
            # 如果指定了特定类别，只更新那一个类别计数
            if specific_category:
                if specific_category in cls.CATEGORY_FIELD_MAP:
                    field_name = cls.CATEGORY_FIELD_MAP[specific_category]
                    count = MainForm.objects.filter(category=specific_category).count()
                    setattr(status_num, field_name, count)
            else:
                # 更新所有类别计数，使用单个查询
                category_counts = MainForm.objects.aggregate(
                    property_dispute_count=Count('id', filter=Q(category='物业纠纷类')),
                    public_facility_count=Count('id', filter=Q(category='公共设施维护类')),
                    environment_count=Count('id', filter=Q(category='环境卫生与秩序类')),
                    neighbor_conflict_count=Count('id', filter=Q(category='邻里矛盾类'))
                )
                
                status_num.PropertyDispute = category_counts['property_dispute_count']
                status_num.PublicFacility = category_counts['public_facility_count']
                status_num.Environment = category_counts['environment_count']
                status_num.NeighborConflict = category_counts['neighbor_conflict_count']
        else:
            # 使用query_manager单独更新
            if specific_category:
                if specific_category in cls.CATEGORY_FIELD_MAP:
                    field_name = cls.CATEGORY_FIELD_MAP[specific_category]
                    count = MainForm.query_manager.filter_category(specific_category).count()
                    setattr(status_num, field_name, count)
            else:
                status_num.PropertyDispute = MainForm.query_manager.filter_category('物业纠纷类').count()
                status_num.PublicFacility = MainForm.query_manager.filter_category('公共设施维护类').count()
                status_num.Environment = MainForm.query_manager.filter_category('环境卫生与秩序类').count()
                status_num.NeighborConflict = MainForm.query_manager.filter_category('邻里矛盾类').count()
        
        # 保存更新（如果需要）
        if save_to_db:
            status_num.save()
            
        return status_num
    
    @classmethod
    def update_counts(cls, optimize=True, update_category=True):
        """
        根据MainForm模型的数据更新状态数量和类别数量
        
        Args:
            optimize: 是否使用优化方式（单次查询）更新状态
            update_category: 是否更新类别计数，如果只需更新状态计数可设为False
        """
        # 获取或创建StatusTypeNum实例
        status_num, created = cls.objects.get_or_create(id=1)
        
        if optimize:
            # 使用单次查询获取所有状态计数
            from django.db.models import Count, Q
            from proceed.utils.choice import UNHANDLED, PROCESSING, HANDLED, NEED_FEEDBACK
            
            # 执行单次查询，使用条件表达式统计各个状态的数量
            counts = MainForm.objects.aggregate(
                unhandle_count=Count('id', filter=Q(handle=UNHANDLED)),
                handling_count=Count('id', filter=Q(handle=PROCESSING)),
                handled_count=Count('id', filter=Q(handle=HANDLED)),
                feedback_needed_count=Count('id', filter=Q(handle=PROCESSING, feedback_status=NEED_FEEDBACK))
            )
            
            # 更新状态数量
            status_num.Unhandle = counts['unhandle_count']
            status_num.Handling = counts['handling_count']
            status_num.Handled = counts['handled_count']
            status_num.WaitCallback = counts['feedback_needed_count']
            
            # 如果需要更新类别计数，调用专用方法
            if update_category:
                # 我们直接调用更新类别的方法，避免代码重复
                # 但不保存，因为后面会统一保存
                status_num = cls.update_category_counts(optimize=True, 
                                                       save_to_db=False, 
                                                       instance=status_num)
        else:
            # 原始方法，使用多次查询
            unhandle_count = MainForm.query_manager.unhandled().count()
            handled_count = MainForm.query_manager.handled().count()
            feedback_needed_count = MainForm.query_manager.feedback_needed().count()
            handling_count = MainForm.query_manager.handling().count()
            
            # 更新状态数量
            status_num.Unhandle = unhandle_count
            status_num.Handling = handling_count
            status_num.Handled = handled_count
            status_num.WaitCallback = feedback_needed_count
            
            # 如果需要更新类别计数，调用专用方法
            if update_category:
                status_num = cls.update_category_counts(optimize=False, 
                                                       save_to_db=False, 
                                                       instance=status_num)
        
        # 保存更新
        status_num.save()
        
        return status_num