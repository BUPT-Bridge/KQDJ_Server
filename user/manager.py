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
    def serialize(self):
        """
        序列化当前查询集
        :param simple: 是否使用简单序列化器
        :return: 序列化后的数据
        """
        from user.serializers import UserSerializer
        return UserSerializer(self, many=True).data


class UsersManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    def self_fliter(self, openid):
        """获取未处理的表单"""
        return self.get_queryset().filter(openid=openid)
    
    def permission_fliter(self,permission_level):
        """获取已处理的表单"""
        return self.get_queryset().filter(permission_level=permission_level)
    
    def get_password(self, openid):
        """获取需要回访的表单"""
        return self.filter(openid=openid).get('password')

    def paginate(self, request, queryset=None):
        """
        分页方法
        :param request: HTTP请求对象
        :param queryset: 可选的查询集，默认使用全部
        :return: dict 包含分页数据和元数据
        """
        if queryset is None:
            queryset = self.get_queryset()
            
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        simple = bool(request.GET.get('simple', False))

        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)

        return {
            'total': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'results': current_page.object_list.serialize()
        }