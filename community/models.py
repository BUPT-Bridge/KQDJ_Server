from django.db import models

# Create your models here.

class Banners(models.Model):
    """轮播图模型"""
    image = models.ImageField(upload_to='media/banners/', verbose_name='轮播图片')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'

    def __str__(self):
        return self.title


class Notice(models.Model):
    """温馨提示模型"""
    content = models.TextField(verbose_name='内容', blank=True, null=True)

    class Meta:
        verbose_name = '温馨提示'
        verbose_name_plural = '温馨提示'

    def __str__(self):
        return self.content[:20]

class Cover(models.Model):
    """封面图模型"""
    image = models.ImageField(upload_to='media/covers/', verbose_name='封面图片')

    class Meta:
        verbose_name = '封面图'
        verbose_name_plural = '封面图'

    def __str__(self):
        return self.title
    

class PageView(models.Model):
    view_count = models.IntegerField(default=0, verbose_name='访问量')

    class Meta:
        verbose_name = '页面访问量'
        verbose_name_plural = '页面访问量'

    def __str__(self):
        return self.page
    
class PhoneNumber(models.Model):
    """手机号模型"""
    phone_name = models.CharField(max_length=20, unique=True, verbose_name='姓名')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='手机号')

    class Meta:
        verbose_name = '手机号'
        verbose_name_plural = '手机号'

    def __str__(self):
        return self.phone_number