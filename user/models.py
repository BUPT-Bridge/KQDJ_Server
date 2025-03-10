from django.db import models

# Create your models here.
class User(models.Model):
    # Django 会自动创建 id 字段作为主键，所以不需要显式定义
    openid = models.CharField(max_length=100, unique=True, verbose_name='微信OpenID')
    username = models.CharField(max_length=50, verbose_name='用户名')
    password = models.CharField(max_length=50, verbose_name='密码')
    phone = models.CharField(max_length=20, verbose_name='手机号')
    # 权限等级，使用整数表示不同的权限级别
    PERMISSION_CHOICES = [
        (0, '普通用户'),
        (1, '管理员'),
        (2, '超级管理员'),
    ]
    permission_level = models.IntegerField(
        choices=PERMISSION_CHOICES, 
        default=0, 
        verbose_name='权限等级'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f"{self.username} (权限: {self.get_permission_level_display()})"