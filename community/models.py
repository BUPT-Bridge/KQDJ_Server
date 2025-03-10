from django.db import models

# Create your models here.

class Banner(models.Model):
    """轮播图模型"""
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='banners/', verbose_name='轮播图片')
    index = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = '轮播图'
        ordering = ['index']

    def __str__(self):
        return self.title


class Notice(models.Model):
    """温馨提示模型"""
    title = models.CharField(max_length=500, verbose_name='标题')
    content = models.TextField(verbose_name='内容')

    class Meta:
        verbose_name = '温馨提示'
        verbose_name_plural = '温馨提示'

    def __str__(self):
        return self.title


class Cover(models.Model):
    """封面图模型"""
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='covers/', verbose_name='封面图片')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = '封面图'
        verbose_name_plural = '封面图'

    def __str__(self):
        return self.title