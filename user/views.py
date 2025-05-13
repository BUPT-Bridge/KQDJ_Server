from rest_framework.views import APIView
from .models import Users
from django.utils.decorators import method_decorator
from utils.wx_login import wx_login
from utils.response import CustomResponse
from utils.auth import auth
from utils.constance import *
from .utils.request_proceesor import request_proceesor
from .utils.validate import VerificationCode
from utils.wx_web_login import get_access_token

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回

class LoginOrRegisterWechat(APIView):
    # 从微信小程序注册/登录账号
    def post(self, request):
        # data=self._login_or_register(request)
        return CustomResponse(self._login_or_register,request)
    
    def _login_or_register(self, request) -> dict:
        # 获取请求数据
        data = request.data
        code = data['code'] # 获取code 如果没有code会报错
        wx_info = wx_login(code) # 获取微信openid
        openid = wx_info['openid'] # 检查用户是否已存在
        if Users.objects.filter(openid=openid).exists():
            return self._login_from_wechat(openid)
        else:
            Users.objects.create(openid=openid)
        return {
                'message': '注册成功',
                'token': auth.generate_token(openid)
            }
    def _login_from_wechat(self,openid):
        Users.objects.filter(openid=openid)
        return {
            'message': '登录成功',
            'token': auth.generate_token(openid)
            }

class LoginTest(APIView):
    def post(self, request):
        return CustomResponse(self._login_or_register,request)
    
    def _login_or_register(self, request) -> dict:
        # 获取请求数据
        data = request.data
        openid = data['openid'] # 获取code 如果没有code会报错

        if Users.objects.filter(openid=openid).exists():
            return self._login_from_wechat(openid)
        else:
            Users.objects.create(openid=openid)
        return {
                'message': '注册成功',
                'token': auth.generate_token(openid)
            }
    def _login_from_wechat(self,openid):
        Users.objects.get(openid=openid)
        return {
            'message': '登录成功',
            'token': auth.generate_token(openid)
            }


class UserInfo(APIView):
    @method_decorator(auth.token_required)
    def get(self, request):
        openid = request.openid
        return CustomResponse(self._get_user_info, openid)
    
    def _get_user_info(self, openid):
        # 获取用户信息
        user_queryset = Users.query_manager.self_fliter(openid)
        if not user_queryset.exists():
            raise Exception('用户不存在')
        user_data = Users.query_manager.self_fliter(openid).serialize()
        return user_data
    
class AdminList(APIView):
    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def get(self, request):
        return CustomResponse(self._get_admin_list, request)
    
    @method_decorator(auth.token_required)
    def put(self, request):
        openid = request.openid
        return CustomResponse(self._adjust_admin_list, request, openid)
    
    def _get_admin_list(self, request):
        # 获取管理员列表
        admin_queryset = Users.query_manager.permission_fliter(ADMIN_USER)
        if not admin_queryset.exists():
            raise Exception('没有管理员')
        admin_data = admin_queryset.order_by('-created_at').paginate(request)
        return admin_data

    def _adjust_admin_list(self, request, openid):
        # 获取表单数据和文件
        data = request_proceesor(request)
        reply = Users.objects.get(openid=openid).update_user(data=data)
        return reply
    
class ChangePermission(APIView):
    
    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def get(self, _):
        return CustomResponse(self._generate_code)
    
    @method_decorator(auth.token_required(required_permission=[COMMON_USER]))
    def post(self, request):
        code = request.data['code']
        openid = request.openid
        return CustomResponse(self._verify_code, code, openid)
        
    def _generate_code(self):
        verification = VerificationCode()
        return verification.generate_code()
    
    def _verify_code(self, code, openid):
        if not code:
            raise Exception('用户不存在')
        else:
            verification = VerificationCode()
            reply = verification.verify_code(code)
        Users.query_manager.self_fliter(openid).update(permission_level=ADMIN_USER)
        return reply

    
class WxWebLoginWeb(APIView):
    """
    处理微信网页直接POST code登录的接口
    """
    def post(self, request):
        return CustomResponse(self._web_login_or_register, request)
    
    def _web_login_or_register(self, request) -> dict:
        # 获取请求数据
        data = request.data
        code = data.get('code')
        
        if not code:
            raise Exception('缺少必要参数code')
            
        # 使用code获取access_token和openid
        wx_info = get_access_token(code)
        openid = wx_info.get('openid')
            
        if not openid:
            raise Exception('获取openid失败')
                
            # 调用LoginTest中的登录或注册逻辑
        login_test = LoginTest()
        mock_request = request
        mock_request.data = {'openid': openid}
        result = login_test._login_or_register(mock_request)
            
        return result