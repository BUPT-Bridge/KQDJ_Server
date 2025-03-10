from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
class UserFunctions(APIView):
    # 从微信小程序注册账号
    def register_from_wechat(self, request):
        pass
    
    # 从网站注册账号
    def register_from_website(self, request):
        pass
    
    # 从微信小程序登录
    def login_from_wechat(self, request):
        pass
    
    # 使用账号密码登录
    def login_from_website(self, request):
        pass

    # 从请求中获取用户信息
    def get_user_info(self, request):
        pass

    # 修改用户信息
    def modify_user_info(self, request):
        pass

    # # 删除用户 (这个暂时可以不用实现/仅在测试时使用)
    # def delete_user(self, request):
    #     pass
    def get_admin_list(self, request):
        pass
    

