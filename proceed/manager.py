"""
本文件是用于创建模型文件的管理器，在管理器中，可以：
1.定义自定义查询方法
2.修改默认的查询集
3.添加表级操作方法
4.添加统计方法
"""
from django.db import models
from django.core.paginator import Paginator
from .utils.analyze_content import analyze_content
from .utils.generate_uuid import generate_custom_uuid
from asgiref.sync import sync_to_async
from django.db import transaction


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

    def paginate(self, request,simple=False) -> dict:
        """QuerySet的分页方法"""
        return MainFormManager().paginate(request, self,simple=simple)


class MainFormManager(models.Manager):
    def get_queryset(self):
        return MainFormQuerySet(self.model, using=self._db)

    def unhandled(self):
        """获取未处理的表单"""
        return self.get_queryset().filter(handle=0)

    def handled(self):
        """获取已完结的表单"""
        return self.get_queryset().filter(handle=2)

    def feedback_needed(self):
        """获取需要回访的表单"""
        return self.get_queryset().filter(handle=1, feedback_status=1)
    
    def handling(self):
        """获取正在处理的表单"""
        return self.get_queryset().filter(handle=1)

    def filter_category(self, category):
        """按分类筛选"""
        return self.get_queryset().filter(category=category)

    def filter_by_openid(self, user_openid):
        """按用户openid筛选"""
        return self.get_queryset().filter(user_openid=user_openid)
    
    def filter_by_admin_openid(self, admin_openid):
        """按用户openid筛选"""
        return self.get_queryset().filter(admin_openid=admin_openid)
    
    def filter_by_pk(self, pk):
        """按表单主键值筛选"""
        return self.get_queryset().filter(pk=pk)

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

    def paginate(self, request, queryset=None, simple=False):
        """
        分页方法
        :param request: HTTP请求对象
        :param queryset: 可选的查询集，默认使用self
        :return: dict 包含分页数据和元数据
        """
        queryset = queryset or self

        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)

        from .serializers import MainFormSerializer, MainFormSerializerSimple
        # print(simple)
        return {
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "page_size": page_size,
            "results": (
                MainFormSerializerSimple(current_page.object_list, many=True).data
                if simple
                else MainFormSerializer(current_page.object_list, many=True).data
            ),
        }

    async def create_form(self, form_data, images=None, source="user", user_openid=None):
        """异步创建表单方法"""
        content = form_data.get("content", "")
        
        # 使用 sync_to_async 包装同步数据库操作
        @sync_to_async
        def create_form_sync():
            with transaction.atomic():
                status=form_data.get("feedback_need", False)
                print("status",status)
                form = self.create(
                    phone=form_data.get("phone"),
                    name=form_data.get("name"),
                    address=form_data.get("address"),
                    content=content,
                    feedback_need=form_data.get("feedback_need", False),
                    audio=form_data.get("audio", None),
                    Latitude_Longitude = form_data.get("Latitude_Longitude", None),
                    user_openid=user_openid,
                    feedback_status= 0 if status==False else 1
                )

                if images:
                    from .models import ImageModel
                    for image in images:
                        ImageModel.objects.create(
                            main_form=form,
                            image=image,
                            source=source
                        )
                return form

        # 创建表单
        form = await create_form_sync()
        
        # 触发后台任务处理AI分析，不等待结果
        from analysis.tasks import analyze_form_content_async
        analyze_form_content_async.delay(form.id)
        
        # 返回序列化数据
        from .serializers import MainFormSerializerSimple
        serializer_function = sync_to_async(lambda: MainFormSerializerSimple(form).data)
        return await serializer_function()

    def update_form_type_and_title(self, form_id, form_type, title, category):
        """更新表单类型和标题的方法"""
        from .models import MainForm
        form = MainForm.objects.get(pk=form_id)
        serial_number = generate_custom_uuid(form.serial_number,form_type)
        form.type = form_type
        form.title = title
        form.category = category  
        form.serial_number = serial_number
        form.save()
        return form
