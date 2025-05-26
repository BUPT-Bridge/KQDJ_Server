"""
本文件是用于创建模型文件的管理器，在管理器中，可以：
1.定义自定义查询方法
2.修改默认的查询集
3.添加表级操作方法
4.添加统计方法
"""
from django.db import models
from django.core.paginator import Paginator

class UserQuerySet(models.QuerySet):
    def serialize(self)-> dict:
        """
        序列化当前查询集
        :param simple: 是否使用简单序列化器
        :return: 序列化后的数据
        """
        from user.serializers import UserSerializer
        return UserSerializer(self, many=True).data

    def paginate(self, request) -> dict:
        """QuerySet的分页方法"""
        return UsersManager().paginate(request, self)


class UsersManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    def self_fliter(self, openid):
        """获取某个的用户"""
        return self.get_queryset().filter(openid=openid)
    
    def get_permission_level(self, openid):
        return self.get_queryset().filter(openid=openid).values_list('permission_level', flat=True).first()
    
    def get_permission_level_phone(self,phone):
        return self.get_queryset().filter(phone=phone).values_list('permission_level', flat=True).first()

    def phone_fliter(self, phone):
        """获取某个的用户"""
        return self.get_queryset().filter(phone=phone)
    
    def phone_certain_fliter(self, phone):
        result = self.get_queryset().filter(phone=phone).values_list('openid', flat=True).first()
        return result 

    def permission_fliter(self,permission_level):
        """获取不同权限的管理员"""
        return self.get_queryset().filter(permission_level=permission_level)
    
    def get_certain_password(self, phone):
        """获取某个用户的密码的表单"""
        result = self.get_queryset().filter(phone=phone).values_list('password', flat=True).first()
        return result 

    def get_enrollment(self):
        """获取今天注册的用户数量"""
        from django.utils import timezone
        import datetime
        # 使用timezone.now()获取当前时间（带时区）
        today = timezone.now().date()
        # 将日期转换为带时区的datetime
        start_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
        end_of_day = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
        # 使用带时区的datetime进行查询
        return self.get_queryset().filter(created_at__range=(start_of_day, end_of_day)).count()

    def paginate(self, request, queryset=None):
        """
        分页方法
        :param request: HTTP请求对象
        :param queryset: 可选的查询集，默认使用self
        :return: dict 包含分页数据和元数据
        """
        queryset = queryset or self
        
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)

        from user.serializers import UserSerializer
        return {
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'results': UserSerializer(current_page.object_list, many=True).data
        }