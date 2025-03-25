# 工具模块结构说明

## 认证相关 (auth.py)
- `Auth` 类: JWT认证实现
  - `generate_token`: 生成JWT令牌
  - `verify_token`: 验证JWT令牌
  - `get_token_from_header`: 从请求头获取token
  - `verify_user_exists`: 验证用户是否存在
  - `token_required`: 装饰器，用于保护需要认证的API
  - `get_current_user`: 获取当前认证用户

## 分页处理 (page_divide.py)
- `paginate_mainforms`: 处理MainForm查询结果的分页
  - 支持自定义页码和每页数量
  - 返回包含分页元数据的字典

## 响应格式化 (response.py)
- `api_response`: 统一成功响应格式 
  - 包含code、message和data字段
- `error_response`: 统一错误响应格式
  - 包含code、message和data字段

## 时间工具 (time_utils.py)
- `set_timestamp`: 设置模型实例的时间戳
  - 用于自动设置上传时间
- `format_datetime`: 时间格式化工具

## 微信登录 (wx_login.py)
- `wx_login`: 处理微信小程序登录
  - 处理code换取session_key和openid
  - 错误处理和异常捕获

## 文件结构
```
utils/
│
├── __init__.py        # 导出所有工具函数
├── auth.py            # JWT认证相关
├── page_divide.py     # 分页处理工具
├── response.py        # 响应格式化
├── time_utils.py      # 时间处理工具
└── wx_login.py        # 微信登录处理
```

## 使用注意
1. 所有工具函数通过 `__init__.py` 统一导出
2. 修改或添加新工具时需要更新 `__init__.py` 中的 `__all__` 变量
3. 时间戳统一使用Unix时间戳（秒级）
4. 响应格式需要保持一致性，使用统一的响应工具函数
