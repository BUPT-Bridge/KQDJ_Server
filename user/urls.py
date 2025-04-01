"""
这个是user模块的路由配置文件,由根目录的urls.py文件引入
在views.py文件中定义了视图函数,在这里将视图函数和url进行绑定
e.g.  path("", views.index, name="index")
该路由主要配置与用户相关的各个函数和页面

"""
from django.urls import path
from .views import LoginOrRegisterWechat

urlpatterns = [
    # path('register', UserRegisterWechat.as_view(), name='register'),
    # path('LoginWechat', UserLoginWechat.as_view(), name='login_from_wechat'),
    # path('UserInfo', UserInfo.as_view(), name='info'),
    path("login",LoginOrRegisterWechat.as_view(),name="login")
]