from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render
from .models import Users
from utils.wx_web_login import get_qrconnect_url, get_access_token, get_user_info
from utils.response import CustomResponse
from utils.auth import auth
from utils.constance import *

class WxWebLoginURL(APIView):
    """
    获取微信网页扫码登录的URL
    """
    def get(self, request):
        # 获取微信扫码登录URL
        qrconnect_url = get_qrconnect_url()
        return JsonResponse({
            'message': '获取成功',
            'login_url': qrconnect_url
        })

class WxWebLoginCallback(APIView):
    """
    处理微信扫码登录的回调
    """
    def get(self, request):
        try:
            # 获取微信回调的code
            code = request.GET.get('code')
            state = request.GET.get('state')
            
            # 如果没有获取到code，返回错误信息
            if not code:
                return JsonResponse({
                    'message': '授权失败，未获取到code',
                    'success': False
                })
                
            # 通过code获取access_token和openid
            wx_info = get_access_token(code)
            access_token = wx_info['access_token']
            openid = wx_info['openid']
            
            # 获取用户信息
            user_info = get_user_info(access_token, openid)
            
            # 检查用户是否已存在
            if Users.objects.filter(openid=openid).exists():
                # 用户已存在，更新用户信息
                user = Users.objects.get(openid=openid)
                # 这里可以根据需要更新用户信息，例如昵称、头像等
                # user.nickname = user_info.get('nickname')
                # user.avatar = user_info.get('headimgurl')
                # user.save()
                
                # 生成token并登录
                token = auth.generate_token(openid)
                return self._success_redirect(token)
            else:
                # 用户不存在，创建新用户
                user = Users.objects.create(
                    openid=openid,
                    # 这里可以根据需要设置其他用户信息，例如昵称、头像等
                    # nickname=user_info.get('nickname'),
                    # avatar=user_info.get('headimgurl'),
                )
                
                # 生成token并注册
                token = auth.generate_token(openid)
                return self._success_redirect(token)
                
        except Exception as e:
            # 处理异常
            return JsonResponse({
                'message': f'授权失败: {str(e)}',
                'success': False
            })
    
    def _success_redirect(self, token):
        """
        成功后重定向到前端页面，并携带token
        """
        # 假设前端页面的URL
        frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else "/"
        
        # 重定向到前端页面，并携带token
        redirect_url = f"{frontend_url}?token={token}"
        
        return HttpResponseRedirect(redirect_url)

class WxWebLoginTest(APIView):
    """
    展示微信扫码登录页面（测试用）
    """
    def get(self, request):
        # 获取微信扫码登录URL
        qrconnect_url = get_qrconnect_url()
        
        # 渲染模板
        return render(request, 'wx_web_login.html', {'qrconnect_url': qrconnect_url})
