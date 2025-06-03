from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from utils.constance import *
from .utils.rename import avatar_upload_path
from .manager import UsersManager
import hashlib  # 添加 hashlib 导入

_AVATAR_WIDTH = 120
_AVATAR_HEIGHT = 120

# Create your models here.
class Users(models.Model):
    objects = models.Manager()
    query_manager = UsersManager()

    openid = models.CharField(max_length=100, unique=True, verbose_name='微信OpenID')
    username = models.CharField(max_length=50, verbose_name='用户名', blank=True, null=True)
    password = models.CharField(max_length=50, verbose_name='密码', blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name='手机号', blank=True, null=True)
    avatar = models.CharField(max_length=255, verbose_name='头像', blank=True, null=True)
    permission_level = models.IntegerField(
        choices=PERMISSION_CHOICES, default=COMMON_USER, 
        verbose_name='权限等级')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def update_user(self, **kwargs):
        """
        处理表单提交的用户信息更新
        :param kwargs: 包含以下字段：
            - data: dict 表单数据，可能包含：
                - username: str 用户名
                - phone: str 手机号
                - password: str 密码
                - avatar: InMemoryUploadedFile 头像文件
        :return: dict 更新结果
        """
        data = kwargs.get('data', {})
        updated_fields = {}
        
        if data:
            update_fields = {'username', 'phone', 'password', 'avatar'}
            valid_fields = {field: value for field, value in data.items() 
                          if field in update_fields and value}
            if not valid_fields:
                raise ValueError("至少提供一个需要更新的字段")
            
            for field, value in valid_fields.items():
                # 如果是密码字段，使用 MD5 加密
                if field == 'password':
                    md5 = hashlib.md5()
                    md5.update(value.encode('utf-8'))
                    value = md5.hexdigest()
                    
                setattr(self, field, value)
                # 对于文件字段，返回文件名而不是文件对象
                if field == 'avatar':
                    updated_fields[field] = value
                else:
                    updated_fields[field] = value
        elif not data:
            raise ValueError("没有提供任何需要更新的字段")            
        self.save()
        updated_fields['message'] = '更新成功'
        return updated_fields

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} - {self.openid} - {self.phone} - {self.permission_level}"
    
class AllImageModel(models.Model):
    """
    用于存储所有上传的图片
    """
    openid = models.CharField(max_length=100, verbose_name='微信OpenID', blank=True, null=True)
    image = ProcessedImageField(
        upload_to=avatar_upload_path,
        processors=[ResizeToFill(_AVATAR_WIDTH, _AVATAR_HEIGHT)],
        format='WEBP',
        options={'quality': 60},
        verbose_name='图片'
    )
    
    class Meta:
        verbose_name = '上传图片'
        verbose_name_plural = '上传图片'
    
    def __str__(self):
        return f"Image {self.id}"
    
    class Meta:
        verbose_name = '上传图片'
        verbose_name_plural = '上传图片'
    
    def __str__(self):
        return f"Image {self.id}"
