import time
import os

def avatar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    # 使用用户openid和时间戳生成新文件名
    new_filename = f'{instance.openid}_{int(time.time())}.{ext}'
    # 返回完整的上传路径
    return os.path.join('picture/avatars', new_filename)
