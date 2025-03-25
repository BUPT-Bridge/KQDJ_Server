# 矿桥东街社区后端服务系统
## 文件结构
```
KQDJ_Server/
├── KQTX_backend/            # 项目配置目录
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # 项目设置
│   ├── urls.py             # 主路由配置
│   └── wsgi.py
│
├── analysis/               # 数据分析模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py          # 数据模型
│   ├── tests.py
│   ├── urls.py           # 路由配置
│   └── views.py          # 视图函数
│
├── community/             # 社区管理模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py         # 社区相关模型
│   ├── tests.py
│   ├── urls.py          # 路由配置
│   └── views.py         # 视图函数
│
├── proceed/              # 表单处理模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py        # 表单相关模型
│   ├── serializers.py   # 序列化器
│   ├── tests.py
│   ├── urls.py         # 路由配置
│   └── views.py        # 视图函数
│   └── utils/          # 模块工具函数
│
├── user/               # 用户管理模块
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py      # 用户模型
│   ├── tests.py
│   ├── urls.py       # 路由配置
│   └── views.py      # 视图函数
│
├── utils/            # 全局工具模块
│   ├── __init__.py
│   ├── auth.py      # JWT认证
│   ├── page_divide.py # 分页工具
│   ├── response.py  # 响应格式化
│   ├── time_utils.py # 时间工具
│   └── wx_login.py  # 微信登录
│
├── manage.py         # Django管理脚本
├── requirements.txt  # 项目依赖
└── README.md        # 项目说明文档
```