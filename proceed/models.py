from django.db import models
import time
from datetime import datetime
from .utils.path_processor import *
from .utils.choice import *
from .utils.uuid import *
from utils import *

# Create your models here.
class MainForm(models.Model):
    upload_time = models.BigIntegerField(verbose_name='时间')
    uuid = models.UUIDField(verbose_name='Form-UUID')
    type = models.CharField(max_length=10, choices=FORM_TYPE_CHOICES, verbose_name='表单类型')

    # User 相关字段
    phone = models.CharField(max_length=20, verbose_name='电话号码')
    name = models.CharField(max_length=50, verbose_name='姓名')
    address = models.TextField(verbose_name='地址')
    content = models.TextField(verbose_name='内容')
    feedback_need = models.BooleanField(default=False, verbose_name='是否需要回访')
    audio = models.FileField(upload_to='audios/', null=True, blank=True, verbose_name='音频文件')
    
    # Admin 相关字段
    admin_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='管理员电话')
    admin_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='管理员姓名')
    admin_way = models.CharField(max_length=50, null=True, blank=True, verbose_name='处理方式')
    admin_content = models.TextField(null=True, blank=True, verbose_name='管理员处理内容')
    feedback_summary = models.TextField(null=True, blank=True, verbose_name='回访总结')
    
    # 处理状态以及相关判断
    handle = models.IntegerField(choices=HANDLE_STATUS_CHOICES, default=UNHANDLED, verbose_name='处理状态')
    feedback_or_not = models.BooleanField(default=False, verbose_name='是否已回访')
    evaluation = models.IntegerField(null=True, blank=True, verbose_name='评价分数')

    # 保存同时需要同步更改的数据
    def save(self, *args, **kwargs):
        generate_custom_uuid(self)
        set_timestamp(self)
        super().save(*args, **kwargs)
    
    # 添加辅助方法，将 Unix 时间戳转换回 datetime 对象
    def get_datetime(self):
        return datetime.fromtimestamp(self.upload_time)
    
    def __str__(self):
        return f"表单 {self.uuid} - {self.name} - {self.get_handle_display()}"
    
    class Meta:
        verbose_name = '表单'
        verbose_name_plural = '表单'


class ImageModel(models.Model):
    # 可以通过 related_name 参数指定反向查询的名称，可以通过main_form_instance.images.all() 来获取所有与该 MainForm 实例关联的 ImageModel 实例。
    main_form = models.ForeignKey(MainForm, on_delete=models.CASCADE, related_name='images', verbose_name='关联表单')
    image = models.ImageField(upload_to=get_image_path, verbose_name='图片')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='user', verbose_name='来源')
    upload_time = models.BigIntegerField(verbose_name='上传时间')

    def save(self, *args, **kwargs):
        set_timestamp(self)
        super().save(*args, **kwargs)
    
    def get_datetime(self):
        return datetime.fromtimestamp(self.upload_time)

    def __str__(self):
        return f"从该表单：{self.main_form.uuid} 获取图片, 图片：{self.image}"
    
    class Meta:
        verbose_name = '表单图片'
        verbose_name_plural = '表单图片'