"""
这个是user模块的路由配置文件,由根目录的urls.py文件引入
在views.py文件中定义了视图函数,在这里将视图函数和url进行绑定
e.g.  path("", views.index, name="index")
该路由主要配置与用户相关的各个函数和页面

"""
from django.urls import path
from .views import LoginOrRegisterWechat,LoginTest,UserInfo, AdminList, ChangePermission, wechat_verify
from .views_web_login import WxWebLoginURL, WxWebLoginCallback, WxWebLoginTest

urlpatterns = [
    # path('register', UserRegisterWechat.as_view(), name='register'),
    # path('LoginWechat', UserLoginWechat.as_view(), name='login_from_wechat'),
    # path('UserInfo', UserInfo.as_view(), name='info'),
    path("login",LoginOrRegisterWechat.as_view(),name="login"),
    path('test', LoginTest.as_view(),name="login_test"),
    path('UserInfo', UserInfo.as_view(), name='info'),
    path('Adminlist', AdminList.as_view(), name='admin_list'),
    path('Changepermission', ChangePermission.as_view(), name='change_permission'),
    
    # 微信网页扫码登录相关路由
    path('web/login/url', WxWebLoginURL.as_view(), name='wx_web_login_url'),
    path('web/login/callback', WxWebLoginCallback.as_view(), name='wx_web_login_callback'),
    path('web/login/test', WxWebLoginTest.as_view(), name='wx_web_login_test'),

    path('test1', wechat_verify),
]