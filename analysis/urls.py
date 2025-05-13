"""
这个是analysis模块的路由配置文件,由根目录的urls.py文件引入
在views.py文件中定义了视图函数,在这里将视图函数和url进行绑定
e.g.  path("", views.index, name="index")
该路由主要配置与管理数据处理相关的各个函数和页面

"""
from django.urls import path
from .views import StatusCountView, ViewNumStatsView, TopUnhandledFormView

urlpatterns = [
    path('status', StatusCountView.as_view(), name='status_counts'),
    path('view-stats', ViewNumStatsView.as_view(), name='view_stats'),
    path('event', TopUnhandledFormView.as_view(), name='event'),
]