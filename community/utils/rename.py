import time
import os
from utils.random_string import generate_random_string


def cover_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    # 使用随机字符串和时间戳生成新文件名
    new_filename = f'{generate_random_string()}_{int(time.time())}.{ext}'
    # 返回完整的上传路径
    os.makedirs('picture/cover', exist_ok=True)  # 确保目录存在
    return os.path.join('picture/cover', new_filename)

def banner_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    # 使用随机字符串和时间戳生成新文件名
    new_filename = f'{generate_random_string()}_{int(time.time())}.{ext}'
    # 返回完整的上传路径
    os.makedirs('picture/banner', exist_ok=True)  # 确保目录存在
    return os.path.join('picture/banner', new_filename)
