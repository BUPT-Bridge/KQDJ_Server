import os
from typing import Any

def get_image_path(instance: Any, filename: str) -> str:
    """
    根据实例的来源确定图片保存路径。

    Args:
        instance: 包含source属性的实例对象
        filename: 文件名

    Returns:
        str: 生成的文件保存路径
    """
    source_folder = 'admin' if instance.source == 'admin' else 'user'
    return os.path.join('images', source_folder)