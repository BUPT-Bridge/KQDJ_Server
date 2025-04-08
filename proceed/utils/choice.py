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

IS_NEED_FEEDBACK_CHOICES = [
    (0, '不需要回访'),
    (1, '需要回访'),
    (2, '已回访'),
]

NOT_NEED_FEEDBACK = 0
NEED_FEEDBACK = 1
NEED_FEEDBACK_DONE = 2

CATEGORY_CHOICES = [
    ('物业纠纷类', '物业纠纷类'),
    ('公共设施维护类', '公共设施维护类'),
    ('环境卫生与秩序类', '环境卫生与秩序类'),
    ('邻里矛盾类', '邻里矛盾类'),
]