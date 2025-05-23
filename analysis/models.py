from django.db import models
from proceed.models import MainForm
from proceed.utils.choice import UNHANDLED, PROCESSING, HANDLED, NEED_FEEDBACK
from user.models import Users
from proceed.utils.analyze_content import analyze_content
from .utils.form_user_relation import find_user_by_openid, generate_solution_suggestion
import logging

# 配置日志
logger = logging.getLogger(__name__)

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
    
class ViewNum(models.Model):
    """视图数量模型 - 存储近七天的访问量和注册量数据"""
    date = models.DateField(verbose_name='日期')
    view_count = models.IntegerField(default=0, verbose_name='访问量')
    enrollment_count = models.IntegerField(default=0, verbose_name='注册量')
    is_today = models.BooleanField(default=False, verbose_name='是否为当天')
    
    class Meta:
        verbose_name = '使用情况'
        verbose_name_plural = '使用情况'
        ordering = ['-date']  # 按日期倒序排列

    def __str__(self):
        return f"{self.date} - 访问量: {self.view_count}, 注册量: {self.enrollment_count}"
    
    @classmethod
    def update_today_counts(cls):
        """
        更新当天的访问量和注册量
        从PageView和Users模型获取数据
        """
        from datetime import date
        from community.models import PageView
        from user.models import Users
        
        today = date.today()
        
        # 先处理所有的is_today记录
        # 将所有记录标记为非今天
        cls.objects.filter(is_today=True).update(is_today=False)
        
        # 获取或创建今天的记录
        # 删除可能的重复记录
        today_records = cls.objects.filter(date=today)
        if today_records.count() > 1:
            # 保留第一条，删除其余的
            keep_id = today_records.first().id
            cls.objects.filter(date=today).exclude(id=keep_id).delete()
            
        # 获取或创建今天的记录
        today_record, created = cls.objects.get_or_create(
            date=today,
            defaults={'is_today': True, 'view_count': 0, 'enrollment_count': 0}
        )
        
        # 标记为今天的记录
        today_record.is_today = True
        
        # 从PageView获取当天访问量
        page_view = PageView.objects.first()
        if page_view:
            today_record.view_count = page_view.view_count
        
        # 从Users获取当天注册量
        today_record.enrollment_count = Users.query_manager.get_enrollment()
        
        # 保存更新
        today_record.save()
        
        # 维护7天的记录限制
        cls._maintain_records_limit()
        
        return today_record
    
    @classmethod
    def _maintain_records_limit(cls, days_limit=7):
        """
        维护记录数量，保持最近7天的数据
        删除超过7天的旧记录
        """
        # 获取所有记录，按日期降序排序
        records = cls.objects.all().order_by('-date')
        
        # 如果记录超过7条，删除多余的
        if records.count() > days_limit:
            # 获取需要保留的7条记录的ID
            keep_ids = records[:days_limit].values_list('id', flat=True)
            # 删除其他记录
            cls.objects.exclude(id__in=keep_ids).delete()
            
class FormUserRelation(models.Model):
    """
    表单与用户关系模型 - 关联MainForm和Users，提取关键信息并生成问题解决建议
    """
    # 关联字段
    main_form = models.OneToOneField(MainForm, on_delete=models.CASCADE, related_name='analysis_relation', verbose_name='关联表单')
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name='form_relations', verbose_name='关联用户')
    
    # 提取的关键信息
    serial_number = models.CharField(max_length=20, verbose_name='表单序号', null=True, blank=True)
    username = models.CharField(max_length=50, verbose_name='用户名称', null=True, blank=True)
    category = models.CharField(max_length=50, verbose_name='表单分类', null=True, blank=True)
    Latitude_Longitude = models.CharField(max_length=20, null=True, blank=True, verbose_name='经纬度')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='地址')
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name='用户头像')
    content = models.TextField(verbose_name='表单内容', null=True, blank=True)

    # AI生成的建议
    solution_suggestion = models.TextField(verbose_name='解决方案建议', null=True, blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '表单用户关系'
        verbose_name_plural = '表单用户关系'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.serial_number} - {self.username} - {self.category}"
    
    def generate_solution_suggestion(self, save=True):
        """
        使用大模型API生成解决方案建议
        """
        suggestion = generate_solution_suggestion(self.category, self.content)
        
        if suggestion and save:
            self.solution_suggestion = suggestion
            self.save(update_fields=['solution_suggestion'])
            
        return suggestion
    
    @classmethod
    def create_or_update_from_form(cls, main_form):
        """
        从MainForm创建或更新FormUserRelation实例
        不再直接触发解决方案生成
        """
        from proceed.utils.choice import UNHANDLED
        
        if not main_form:
            return None
        
        # 只处理未处理状态的表单
        if main_form.handle != UNHANDLED:
            logger.info(f"表单 {main_form.pk} 不是未处理状态，不创建关系")
            # 如果表单状态不是未处理，删除可能存在的关系
            cls.objects.filter(main_form=main_form).delete()
            return None
            
        try:
            # 检查表单的必要字段是否已经由大模型生成完成
            if not main_form.category or not main_form.title:
                logger.warning(f"表单 {main_form.pk} 的必要字段尚未生成完成")
                return None
                
            # 准备基本字段数据，用于创建和更新
            base_fields = {
                'serial_number': main_form.serial_number,
                'category': main_form.category,
                'Latitude_Longitude': main_form.Latitude_Longitude,
                'address': main_form.address,
                'content': main_form.content,
            }
            
            # 查找关联的用户
            user = find_user_by_openid(Users, main_form.user_openid)
            if user:
                base_fields['user'] = user
                base_fields['username'] = user.username
                base_fields['avatar'] = user.avatar.url if user.avatar else None
                
            
            # 根据表单查找或创建关系记录，使用准备好的字段
            relation, created = cls.objects.update_or_create(
                main_form=main_form,
                defaults=base_fields
            )
            
            # 提交生成解决方案建议的任务，而不是立即执行
            if created or 'content' in base_fields:
                from .tasks import generate_solution_suggestion_async
                logger.info(f"为表单 {main_form.pk} 安排生成解决建议任务")
                generate_solution_suggestion_async.delay(relation.id)
        
            return relation
        except Exception as e:
            logger.error(f"创建或更新FormUserRelation失败: {str(e)}")
            return None


