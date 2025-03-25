import jwt
from datetime import datetime, timedelta
from functools import wraps
from rest_framework.response import Response
from django.conf import settings
# 添加用户模型导入
from user.models import User  # 请确保这是正确的用户模型导入路径

"""
验证token的装饰器
使用示例：
    @auth.token_required
        def protected_view(request):
            user_openid = request.openid
            # 进行后续业务逻辑处理
            return Response(...)
"""

class Auth:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化配置
            cls._instance.jwt_secret = getattr(settings, 'JWT_SECRET', 'your-secret-key')
            cls._instance.jwt_expiration = timedelta(days=7)
        return cls._instance

    def generate_token(self, openid):
        """
        生成JWT token,支持添加额外的claims
        """
        payload = {
            'openid': openid,
            'exp': datetime.now() + self.jwt_expiration,
            'iat': datetime.now(),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')

    def verify_token(self, token):
        """验证JWT token"""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def get_token_from_header(self, request):
        """从请求头中获取token"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        try:
            token_type, token = auth_header.split()
            return token if token_type.lower() == 'bearer' else None
        except ValueError:
            return None

    def verify_user_exists(self, openid):
        """验证用户是否存在于数据库中"""
        try:
            return User.objects.filter(openid=openid).exists()
        except Exception:
            return False

    def token_required(self, view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            token = self.get_token_from_header(request)
            if not token:
                return Response({'code': 401, 'message': '未提供token'})
            
            payload = self.verify_token(token)
            if not payload:
                return Response({'code': 401, 'message': 'token无效或已过期'})
            
            openid = payload.get('openid')
            if not openid or not self.verify_user_exists(openid):
                return Response({'code': 401, 'message': '用户不存在或已被删除'})
            
            request.openid = openid
            request.token_payload = payload
            return view_func(request, *args, **kwargs)
        return wrapped_view

    def get_current_user(self, request):
        """获取当前用户的openid"""
        token = self.get_token_from_header(request)
        if not token:
            return None
        payload = self.verify_token(token)
        return payload.get('openid') if payload else None

# 创建全局认证实例
auth = Auth()
