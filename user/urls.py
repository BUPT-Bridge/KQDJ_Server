"""
这个是user模块的路由配置文件,由根目录的urls.py文件引入
在views.py文件中定义了视图函数,在这里将视图函数和url进行绑定
e.g.  path("", views.index, name="index")
该路由主要配置与用户相关的各个函数和页面

"""
from django.urls import path
from .views import UserFunctions

urlpatterns = [
    path('register', UserFunctions.as_view(), name='register'),
    # path("register_from_website", UserFunctions.as_view(), name="register_from_website"),
    # path("login_from_wechat", UserFunctions.as_view(), name="login_from_wechat"),
    # path("login_from_website", UserFunctions.as_view(), name="login_from_website"),
    # path("get_user_info", UserFunctions.as_view(), name="get_user_info"),
    # path("modify_user_info", UserFunctions.as_view(), name="modify_user_info"),
    # path("get_admin_list", UserFunctions.as_view(), name="get_admin_list"),
    # path("delete_user", UserFunctions.as_view(), name="delete_user"),
]