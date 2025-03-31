"""
本文件是用于创建模型文件的管理器，在管理器中，可以：
1.定义自定义查询方法
2.修改默认的查询集
3.添加表级操作方法
4.添加统计方法
"""
from django.db import models
from django.core.paginator import Paginator

class MainFormQuerySet(models.QuerySet):
    def serialize(self, simple=False):
        """
        序列化当前查询集
        :param simple: 是否使用简单序列化器
        :return: 序列化后的数据
        """
        from proceed.serializers import MainFormSerializer, MainFormSerializerSimple
        serializer_class = MainFormSerializerSimple if simple else MainFormSerializer
        return serializer_class(self, many=True).data


class MainFormManager(models.Manager):
    def get_queryset(self):
        return MainFormQuerySet(self.model, using=self._db)
    
    def unhandled(self):
        """获取未处理的表单"""
        return self.get_queryset().filter(handle=0)
    
    def handled(self):
        """获取已处理的表单"""
        return self.get_queryset().filter(handle=2)
    
    def feedback_needed(self):
        """获取需要回访的表单"""
        return self.get_queryset().filter(handle=1, feedback_status=1)
    
    def filter_by_admin(self, admin_openid):
        """按管理员openid筛选"""
        return self.get_queryset().filter(admin_openid=admin_openid)
    
    def filter_by_user(self, user_openid):
        """按用户openid筛选"""
        return self.get_queryset().filter(user_openid=user_openid)
    
    def filter_by_handle_time(self, start_time=None, end_time=None):
        """
        按处理时间范围筛选，必须同时提供起始和结束时间
        :param start_time: 起始时间戳
        :param end_time: 结束时间戳
        :return: QuerySet 或空查询集
        """
        if start_time and end_time:
            return self.get_queryset().filter(handle_time__range=(start_time, end_time))
        return self.get_queryset().none()  # 返回空查询集

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
            'results': current_page.object_list.serialize(simple=simple)
        }