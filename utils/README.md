# 工具模块结构说明

## 认证相关 (auth.py)

### Auth 类
JWT认证的实现类，提供完整的用户认证和权限验证功能。

**主要方法:**
- `generate_token(openid)`: 生成包含用户openid和权限信息的JWT令牌
- `verify_token(token)`: 验证JWT令牌的有效性
- `get_token_from_header(request)`: 从请求头获取Bearer token
- `verify_user_exists(openid)`: 验证用户是否存在
- `token_required([required_permission])`: 装饰器,用于API接口的认证保护
- `get_current_user(request)`: 获取当前认证用户的openid

**使用示例:**
```python
# 保护需要登录的接口
@auth.token_required
def protected_view(request):
    user_openid = request.openid
    return Response(...)

# 权限验证
@auth.token_required(required_permission=ADMIN_USER)
def admin_view(request):
    pass
```

## 响应格式化 (response.py)

### CustomResponse
统一的响应格式处理函数。

**参数:**
- `function`: 需要包装的业务函数，必须返回字典类型
- `args`, `kwargs`: 传递给业务函数的参数

**响应格式:**
```python
{
    'code': 200/400,  # 状态码
    'message': 'success/error',  # 响应消息
    'data': {}  # 响应数据
}
```

## 时间工具 (time_utils.py)

### set_timestamp
设置模型实例的时间戳字段。

**参数:**
- `instance`: 模型实例

### format_datetime
格式化时间字符串。

**参数:**
- `dt`: 待格式化的时间字符串
- `format`: 格式化模板，默认"%Y-%m-%d %H:%M:%S"

## 微信登录 (wx_login.py)

### wx_login
处理微信小程序登录逻辑。

**参数:**
- `code`: 小程序登录时获取的code

**返回:**
```python
{
    'session_key': '会话密钥',
    'openid': '用户唯一标识'
}
```

## 使用注意事项

1. 认证相关
   - token过期时间默认为14天
   - 请求需要在Header中携带`Authorization: Bearer <token>`

2. 响应格式
   - 所有API响应都应使用CustomResponse包装
   - 确保业务函数返回字典类型数据

3. 时间处理
   - 时间戳统一使用Unix时间戳(秒级)
   - 注意时区设置

4. 微信登录
   - 需要在配置中设置正确的WX_APP_ID和WX_APP_SECRET
   - 注意异常处理