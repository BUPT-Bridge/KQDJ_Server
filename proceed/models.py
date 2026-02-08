from django.db import models
from datetime import datetime
from imagekit.models import ProcessedImageField
from .manager import MainFormManager
import time
from .utils.path_processor import get_image_path
from .utils.choice import *
from .utils.sync_feedback_status import sync_feedback_status
from .utils import *
import uuid
from utils.time_utils import set_timestamp  # 改为使用绝对导入
from openpyxl import Workbook
from io import BytesIO
from django.http import HttpResponse
from .utils.handle_timestamp import timestamp_to_beijing_str


# Create your models here.
class MainForm(models.Model):
    # 通过自定义管理器，可以在查询时使用自定义的查询方法
    objects = models.Manager()
    query_manager = MainFormManager()

    # 定义字段
    upload_time = models.BigIntegerField(verbose_name="时间")
    uuidx = models.UUIDField(verbose_name="表单UUID",default=uuid.uuid4,editable=False)
    type = models.CharField(
        max_length=10, choices=FORM_TYPE_CHOICES, null=True, blank=True, verbose_name="表单类型"
    )
    serial_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True, verbose_name="表单序号"
    )
    category = models.CharField(
        max_length=10, choices=CATEGORY_CHOICES, verbose_name="表单分类",null=True, blank=True
    )

    # User 相关字段
    phone = models.CharField(max_length=20, verbose_name="电话号码")
    name = models.CharField(max_length=50, verbose_name="姓名")
    address = models.TextField(verbose_name="地址")
    Latitude_Longitude = models.CharField(max_length=20, null=True, blank=True, verbose_name="经纬度", default="116.397128,39.916527")
    title = models.CharField(max_length=100, null=True, blank=True, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    feedback_need = models.BooleanField(default=False, verbose_name="是否需要回访")
    audio = models.FileField(
        upload_to="audios/", null=True, blank=True, verbose_name="音频文件"
    )
    user_openid = models.CharField(max_length=100, verbose_name="用户OpenID")

    # Admin 相关字段
    admin_phone = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="管理员电话"
    )
    admin_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="管理员姓名"
    )
    admin_way = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="处理方式"
    )
    admin_content = models.TextField(
        null=True, blank=True, verbose_name="管理员处理内容"
    )
    admin_openid = models.CharField(max_length=100, verbose_name="管理员OpenID")
    handle_time = models.BigIntegerField(null=True, blank=True, verbose_name="处理时间")
    feedback_summary = models.TextField(null=True, blank=True, verbose_name="回访总结")

    # 处理状态以及相关判断  提供了 get_handle_display() 方法来获取人类可读的值
    handle = models.IntegerField(
        choices=HANDLE_STATUS_CHOICES, default=UNHANDLED, verbose_name="处理状态"
    )
    feedback_status = models.IntegerField(
        choices=IS_NEED_FEEDBACK_CHOICES, default=NEED_FEEDBACK, verbose_name="回访状态"
    )
    evaluation = models.IntegerField(null=True, blank=True, verbose_name="评价分数")
    evaluation_or_not = models.BooleanField(default=False, verbose_name="是否已评价")

    # 保存同时需要同步更改的数据
    def save(self, *args, **kwargs):
        if self.pk is None:  # 只在首次创建时执行
            set_timestamp(self)
            sync_feedback_status(self)
        elif self.serial_number:
            self.handle_time = int(time.time())
        super().save(*args, **kwargs)

    # 添加辅助方法，将 Unix 时间戳转换回 datetime 对象
    def get_datetime(self):
        return datetime.fromtimestamp(self.upload_time)

    def update_form(self, handle_images=None, **kwargs):
        """
        :param kwargs: 可包含以下字段（每次调用只能包含其中一个）：
            - handle_info: dict 管理员处理信息
            - feedback_info: dict 回访信息
            - evaluation_info: dict 评价信息
        :return: bool 更新是否成功
        :raises ValueError: 当没有提供任何更新信息或提供了多个更新信息时
        """
        # 检查传入的更新类型数量
        update_types = [
            bool(kwargs.get("handle_info")),
            bool(kwargs.get("feedback_info")),
            bool(kwargs.get("evaluation_info")),
        ]
        if sum(update_types) == 0:
            raise ValueError("必须提供一个更新信息")
        if sum(update_types) > 1:
            raise ValueError("每次只能提供一种类型的更新信息")

        # 记录更新前的状态
        old_handle_status = self.handle
        trigger_count_update = False

        # 更新管理员信息
        handle_info = kwargs.get("handle_info", {})
        if handle_info:
            self.admin_phone = handle_info.get("phone", self.admin_phone)
            self.admin_name = handle_info.get("name", self.admin_name)
            self.admin_way = handle_info.get("way", self.admin_way)
            self.admin_content = handle_info.get("content", self.admin_content)
            self.admin_openid = kwargs.get("openid", self.admin_openid)
            if self.feedback_status == NOT_NEED_FEEDBACK:
                self.handle = HANDLED
                # 检查状态是否变为已完成
                if old_handle_status != HANDLED:
                    trigger_count_update = True
            else:
                self.handle = PROCESSING

            if handle_images:
                for image in handle_images:
                    HandleImageModel.objects.create(
                        main_form=self,
                        image=image
                    )

        # 更新回访信息
        feedback_info = kwargs.get("feedback_info", {})
        if feedback_info:
            self.feedback_status = NEED_FEEDBACK_DONE
            self.handle = HANDLED
            # 检查状态是否变为已完成
            if old_handle_status != HANDLED:
                trigger_count_update = True
            self.feedback_summary = feedback_info.get(
                "feedback_summary", self.feedback_summary
            )

        # 更新评价信息
        evaluation_info = kwargs.get("evaluation_info", {})
        if evaluation_info:
            self.evaluation = evaluation_info["evaluation_info"]
            print(self.evaluation)
            self.evaluation_or_not = True

        self.save()
        
        # 如果表单状态变为已完成，且有管理员 openid，则触发异步任务
        if trigger_count_update and self.admin_openid:
            from analysis.tasks import update_admin_finished_count_async
            update_admin_finished_count_async.delay(self.admin_openid)
        
        return True

    def export_to_excel(start_timestamp, end_timestamp):
        """
        导出符合条件的 MainForm 数据到 Excel 文件。

        Args:
            start_timestamp (int): 起始时间戳
            end_timestamp (int): 结束时间戳

        Returns:
            HttpResponse: 包含 Excel 文件的 HTTP 响应
        """
        # 筛选符合条件的记录
        queryset = MainForm.objects.filter(
            upload_time__gte=start_timestamp, upload_time__lte=end_timestamp
        )

        # 创建 Excel 工作簿
        wb = Workbook()
        ws = wb.active
        ws.title = "MainForm Data"

        # 写入表头
        headers = [
            "表单序号", "表单类型", "上传时间", "表单分类","表单标题", "姓名", "电话号码", "地址", 
             "内容", "是否需要回访", "管理员电话", "管理员姓名", 
            "处理方式", "管理员处理内容", "处理时间", "回访总结", 
            "处理状态", "回访状态", "评价分数", "是否已评价"
        ]
        ws.append(headers)

        # 写入数据
        for form in queryset:
            row = [
                form.serial_number,
                dict(FORM_TYPE_CHOICES).get(form.type,"建议"),
                timestamp_to_beijing_str(form.upload_time),  # 转换上传时间
                form.category,
                form.title,
                form.name,
                form.phone,
                form.address,
                form.content,
                "是" if form.feedback_need else "否",
                form.admin_phone,
                form.admin_name,
                form.admin_way,
                form.admin_content,
                "未处理" if form.handle == 0 else timestamp_to_beijing_str(form.handle_time),  # 处理时间
                form.feedback_summary,
                dict(HANDLE_STATUS_CHOICES).get(form.handle, "无"),
                dict(IS_NEED_FEEDBACK_CHOICES).get(form.feedback_status, "无"),
                form.evaluation,
                "是" if form.evaluation_or_not else "否",
            ]
            ws.append(row)

        # 将工作簿保存到内存中
        output = BytesIO()
        wb.save(output)
        output.seek(0)

        # 创建 HTTP 响应
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="MainForm_Data.xlsx"'
        return response

    def __str__(self):
        return f"表单 {self.uuidx} - {self.name} - {self.get_handle_display()}"

    class Meta:
        verbose_name = "表单"
        verbose_name_plural = "表单"


class ImageModel(models.Model):
    # 可以通过 related_name 参数指定反向查询的名称，可以通过main_form_instance.images.all() 来获取所有与该 MainForm 实例关联的 ImageModel 实例。
    main_form = models.ForeignKey(
        MainForm,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="关联表单",
    )
    image = models.CharField(max_length=255, verbose_name="图片路径")
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default="user", verbose_name="来源"
    )
    upload_time = models.BigIntegerField(verbose_name="上传时间")

    def save(self, *args, **kwargs):
        set_timestamp(self)
        super().save(*args, **kwargs)

    def get_datetime(self):
        return datetime.fromtimestamp(self.upload_time)

    def __str__(self):
        return f"从该表单：{self.main_form.uuidx} 获取图片, 图片：{self.image}"

    class Meta:
        verbose_name = "表单图片"
        verbose_name_plural = "表单图片"


class HandleImageModel(models.Model):
    # 可以通过 related_name 参数指定反向查询的名称，可以通过main_form_instance.images.all() 来获取所有与该 MainForm 实例关联的 ImageModel 实例。
    main_form = models.ForeignKey(
        MainForm,
        on_delete=models.CASCADE,
        related_name="handle_images",
        verbose_name="关联表单",
    )
    image = models.CharField(max_length=255, verbose_name="处理图片路径")
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default="admin", verbose_name="来源"
    )
    upload_time = models.BigIntegerField(verbose_name="上传时间")

    def save(self, *args, **kwargs):
        set_timestamp(self)
        super().save(*args, **kwargs)

    def get_datetime(self):
        return datetime.fromtimestamp(self.upload_time)

    def __str__(self):
        return f"从该表单：{self.main_form.uuidx} 获取处理反馈图片, 图片：{self.image}"

    class Meta:
        verbose_name = "表单处理反馈图片"
        verbose_name_plural = "表单处理反馈图片"


class AllImageModel(models.Model):
    """
    用于存储所有图片的模型
    """
    image = ProcessedImageField(
        upload_to=get_image_path, format="WEBP", options={"quality": 40}
    )
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default="admin", verbose_name="来源"
    )
    upload_time = models.BigIntegerField(verbose_name="上传时间")

    def save(self, *args, **kwargs):
        set_timestamp(self)
        super().save(*args, **kwargs)

    def get_datetime(self):
        return datetime.fromtimestamp(self.upload_time)

    def __str__(self):
        return f"图片：{self.image}"

    class Meta:
        verbose_name = "所有图片"
        verbose_name_plural = "所有图片"


class Order(models.Model):
    """
    派单记录模型
    """
    from .manager import OrderManager
    
    objects = models.Manager()
    query_manager = OrderManager()
    
    main_form = models.ForeignKey(
        MainForm,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="关联表单"
    )
    serial_number = models.CharField(max_length=20, verbose_name="表单序号")
    title = models.CharField(max_length=100, verbose_name="表单标题")
    dispatch_time = models.BigIntegerField(verbose_name="派单时间")
    dispatch_openid = models.CharField(max_length=100, verbose_name="派单员OpenID")
    
    def save(self, *args, **kwargs):
        if self.pk is None:  # 只在首次创建时执行
            set_timestamp(self, field_name='dispatch_time')
        super().save(*args, **kwargs)
    
    def get_datetime(self):
        return datetime.fromtimestamp(self.dispatch_time)
    
    def __str__(self):
        return f"派单 {self.serial_number} - {self.dispatch_openid}"
    
    class Meta:
        verbose_name = "派单记录"
        verbose_name_plural = "派单记录"
        ordering = ['-dispatch_time']