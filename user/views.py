from rest_framework.views import APIView
from .models import Users
from utils.wx_login import wx_login
from utils.response import api_response, error_response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from .serializers import UserSerializer
from utils.auth import auth  # 添加这行导入

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回
class UserRegisterWechat(APIView):
    # 从微信小程序注册账号

    @extend_schema(
        summary="微信小程序用户注册",
        description="通过微信小程序 code 进行用户注册",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'string', 'description': '微信小程序登录code'},
                },
                'required': ['code']
            }
        }
    )
    def post(self, request):
        try:
                # 获取请求数据
            data = request.data
            code = data.get('code')
                
                # 验证必要字段
            if not all([code]):
                return error_response(data={
                    'message': '注册失败',
                    'error': '缺少必要的注册信息'})
                
                # 获取微信openid
            wx_info = wx_login(code)
            if not wx_info:
                return error_response(data={
                    'message': wx_info['errmsg'],
                    'error': '微信登录验证失败'})
            if not wx_info.get('openid'):
                return error_response(data={
                    'message': wx_info['errmsg'],
                    'error': 'openid获取失败'})
            # 获取openid
            openid = wx_info['openid']
                # 检查用户是否已存在
            if Users.objects.filter(openid=code).exists():
                return self.login_from_wechat(request)
                # 创建新用户
            user = Users.objects.create(
                    openid=openid)
            return api_response(data={
                'message': '注册成功',
                'user_id': user.id,
                'token': auth.generate_token(code)
            })
                
        except Exception as e:
            return error_response(data={
                'message': '注册失败',
                'error': str(e)
            })
    
class UserLoginWechat(APIView):
    # 从微信小程序登录
    def post(self, request):
        try:
                # 获取请求数据
            data = request.data
            code = data.get('code')
                
                # 验证必要字段
            if not all([code]):
                return error_response(data={
                    'message': '注册失败',
                    'error': '缺少必要的登录信息'})
                
                # 获取微信openid
            wx_info = wx_login(code)
            if not wx_info:
                return error_response(data={
                    'message': wx_info['errmsg'],
                    'error': '微信登录验证失败'})
            if not wx_info.get('openid'):
                return error_response(data={
                    'message': wx_info['errmsg'],
                    'error': 'openid获取失败'})
            # 获取openid
            openid = wx_info['openid']
            return api_response(data={
                'message': '注册成功',
                'token': auth.generate_token(openid)
            })
                
        except Exception as e:
            return error_response(data={
                'message': '注册失败',
                'error': str(e)
            })
        
class UserInfo(APIView):
    # get 为获取用户信息
    def post(self, request):
        try:
            data = request.data
            code = data.get('code')

            # 使用manager的self_filter方法获取用户信息
            user_queryset = Users.query_manager.self_fliter(code)
            if not user_queryset.exists():
                return error_response(data={
                    'message': '获取用户信息失败',
                    'error': '用户不存在'
                })
            user_data = Users.query_manager.self_fliter(code).serialize()
            return api_response(data=user_data)

        except Exception as e:
            return error_response(data={
                'message': '获取用户信息失败',
                'error': str(e)
            })

    # # 使用账号密码登录
    # def login_from_website(self, request):
    #     pass

    # def login_from_QRcode(self, request):
    #     pass

    # # 从请求中获取用户信息
    # def get_user_info(self, request):
    #     pass

    # # 修改用户信息
    # def modify_user_info(self, request):
    #     pass

    # # # 删除用户 (这个暂时可以不用实现/仅在测试时使用)
    # # def delete_user(self, request):
    # #     pass
    # def get_admin_list(self, request):
    #     pass

    # # 从网站注册账号
    # def register_from_website(self, request):
    #     pass

