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
    
    def permission_fliter(self,permission_level):
        """获取不同权限的管理员"""
        return self.get_queryset().filter(permission_level=permission_level)
    
    def get_password(self, openid):
        """获取某个用户的密码的表单"""
        return self.filter(openid=openid).get('password')
    
    def get_enrollment(self):
        """获取今天注册的用户数量"""
        from datetime import datetime, time
        today = datetime.now().date()
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        
        return self.get_queryset().filter(created_at__range=(today_start, today_end)).count()

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