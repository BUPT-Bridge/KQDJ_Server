"""
这个是proceed模块的路由配置文件,由根目录的urls.py文件引入
在views.py文件中定义了视图函数,在这里将视图函数和url进行绑定
e.g.  path("", views.index, name="index")
该路由主要配置与表单处理相关的各个函数和页面

"""
from django.urls import path
from . import views

# 接口仍在开发中，暂时不写注册
urlpatterns = [
    
]