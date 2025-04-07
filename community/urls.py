"""
这个是community模块的路由配置文件,由根目录的urls.py文件引入
在views.py文件中定义了视图函数,在这里将视图函数和url进行绑定
e.g.  path("", views.index, name="index")
该路由主要配置与社区管理处理相关的各个函数和页面

"""
from django.urls import path
from . import views

urlpatterns = [
    path('warm_notice', views.WarmNoticeFunctions.as_view(), name='warm_notice'),
    path('visit_count', views.VisitCountFunctions.as_view(), name='visit_count'),
    path('phone_number', views.CommunityTele.as_view(), name='phone_number'),
    path('car_limit', views.CarLimitFunctions.as_view(), name='car_limit'),
    path('banners', views.BanerFunctions.as_view(), name='banner'),
    path('cover', views.CoverFunctions.as_view(), name='cover')
]