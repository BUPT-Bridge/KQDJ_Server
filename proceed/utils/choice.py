# Desc: 选项常量定义，使主文件更简洁

# 处理状态选项
HANDLE_STATUS_CHOICES = [
    (0, '未处理'),
    (1, '处理中'),
    (2, '已处理'),
]

# 状态常量
UNHANDLED = 0
PROCESSING = 1
HANDLED = 2

# 来源选项
SOURCE_CHOICES = [
    ('user', '用户'),
    ('admin', '管理员'),
]

FORM_TYPE_CHOICES = [
    ('complaint', '投诉'),    # 第一个值是存储在数据库中的值，第二个是显示用的人类可读的值
    ('suggest', '建议'),
]