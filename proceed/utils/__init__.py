"""
工具模块结构说明：
---------------

path_processor.py:
    - get_image_path: 根据实例source属性处理图片存储路径
                     用于区分用户上传和表单处理的图片存储位置
                     
uuid.py:
    - generate_custom_uuid: 生成自定义UUID
                          格式：{类型前缀}-{日期}-{序号}
                          类型前缀：J(建议)/T(投诉)
                          用于表单的唯一标识生成
                          
choice.py:
    常量定义模块：
    - HANDLE_STATUS_CHOICES: 处理状态选项 [(0,'未处理'),(1,'处理中'),(2,'已处理')]
    - SOURCE_CHOICES: 来源选项 [('user','用户'),('admin','管理员')]
    - FORM_TYPE_CHOICES: 表单类型 [('complaint','投诉'),('suggest','建议')]
    
    状态常量：
    - UNHANDLED(0): 未处理状态
    - PROCESSING(1): 处理中状态
    - HANDLED(2): 已处理状态
"""

from .uuid import *
from path_processor import *
from .choice import *

__all__ = [
    'get_image_path',
    'generate_custom_uuid',
    # 下面都是常量的引入
    'SOURCE_CHOICES',
    'FORM_TYPE_CHOICES',
    'HANDLE_STATUS_CHOICES',
    'UNHANDLED',
    'PROCESSING',
    'HANDLED', 
]
