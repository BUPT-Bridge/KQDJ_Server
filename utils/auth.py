import jwt
from datetime import datetime, timedelta
from functools import wraps
from rest_framework.response import Response
from django.conf import settings
# 添加用户模型导入
from user.models import Users  # 请确保这是正确的用户模型导入路径

"""
验证token的装饰器
使用示例：
        @auth.token_required
        def protected_view(request):
            user_openid = request.openid
            # 进行后续业务逻辑处理
            return Response(...)

@auth.token_required(required_permission=ADMIN_USER)  # ADMIN_USER 是您定义的权限等级常量
def admin_only_view(request):
    pass

# 多个权限验证 (只需满足其中任意一个)
@auth.token_required(required_permission=[ADMIN_USER, SUPER_USER])
def special_view(request):

"""

class Auth:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化配置
            cls._instance.jwt_secret = getattr(settings, 'SECRET_KEY', 'your-secret-key')
            cls._instance.jwt_expiration = timedelta(days=14)
        return cls._instance

    def get_user_permission(self, openid):
        """获取用户权限等级"""
        try:
            user = Users.objects.get(openid=openid)
            return user.permission_level
        except Users.DoesNotExist:
            return None

    def generate_token(self, openid):
        """
        生成JWT token,包含用户openid和权限信息，返回带Bearer前缀的token
        """
        permission_level = self.get_user_permission(openid)
        if permission_level is None:
            return None
        current_timestamp = datetime.now().timestamp()
        payload = {
            'openid': openid,
            'permission_level': permission_level,
            'exp': int(current_timestamp + self.jwt_expiration.total_seconds()),
        }
        jwt_token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        return f"Bearer {jwt_token}"

    def verify_token(self, token):
        """验证JWT token"""
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            return None

    def get_token_from_header(self, request):
        """从请求头中获取并验证Bearer token
        
        验证规则：
        1. Authorization header必须存在
        2. 必须以'Bearer '开头（注意空格）
        3. Token不能为空
        """
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
            
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header[7:].strip()
        if not token:
            return None
        return token

    def verify_user_exists(self, openid):
        """验证用户是否存在于数据库中"""
        try:
            return Users.objects.filter(openid=openid).exists()
        except Exception:
            return False

    def token_required(self, view_func=None, required_permission=None):
        def decorator(view_func):
            @wraps(view_func)
            def wrapped_view(request, *args, **kwargs):
                token = self.get_token_from_header(request)
                if not token:
                    return Response({'code': 401, 'message': '未提供token'})
                
                payload = self.verify_token(token)
                if not payload:
                    return Response({'code': 401, 'message': 'token无效或已过期'})
                
                openid = payload.get('openid')
                permission_level = payload.get('permission_level')
                
                if not openid or not self.verify_user_exists(openid):
                    return Response({'code': 401, 'message': '用户不存在或已被删除'})
                
                # 权限验证逻辑
                if required_permission is not None:
                    # 转换required_permission为列表形式
                    required_permissions = (
                        required_permission 
                        if isinstance(required_permission, (list, tuple)) 
                        else [required_permission]
                    )
                    
                    # 验证是否满足任一权限要求
                    if not any(permission_level == p for p in required_permissions):
                        return Response({
                            'code': 403, 
                            'message': '权限不符',
                            'required': required_permissions,
                            'current': permission_level
                        })
                
                request.openid = openid
                request.permission_level = permission_level
                request.token_payload = payload
                return view_func(request, *args, **kwargs)
            return wrapped_view
        
        if view_func:
            return decorator(view_func)
        return decorator

    def get_current_user(self, request):
        """获取当前用户的openid"""
        token = self.get_token_from_header(request)
        if not token:
            return None
        payload = self.verify_token(token)
        return payload.get('openid') if payload else None

# 创建全局认证实例
auth = Auth()
