import time
import os
import random
import string

def generate_random_string(length=8):
    """生成指定长度的随机字符串"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def cover_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    # 使用随机字符串和时间戳生成新文件名
    new_filename = f'{generate_random_string()}_{int(time.time())}.{ext}'
    # 返回完整的上传路径
    return os.path.join('picture/cover', new_filename)

def banner_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    # 使用随机字符串和时间戳生成新文件名
    new_filename = f'{generate_random_string()}_{int(time.time())}.{ext}'
    # 返回完整的上传路径
    return os.path.join('picture/banner', new_filename)
