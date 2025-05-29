import os
from typing import Any
import time
from utils.random_string import generate_random_string

def get_image_path(instance: Any, filename: str) -> str:
    """
    根据实例的来源确定图片保存路径。

    Args:
        instance: 包含source属性的实例对象
        filename: 文件名

    Returns:
        str: 生成的文件保存路径
    """
    ext = filename.split('.')[-1]
    # 使用用户openid和时间戳生成新文件名
    new_filename = f'{generate_random_string()}_{int(time.time())}.{ext}'
    source_folder = 'admin' if instance.source == 'admin' else 'user'
    # 返回完整的上传路径
    return os.path.join(f'picture/proceed/{source_folder}', new_filename)
