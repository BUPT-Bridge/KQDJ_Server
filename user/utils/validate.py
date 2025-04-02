import time
import hashlib
import base64
import json
from django.conf import settings

class VerificationCode:
    def __init__(self, secret_key: str = getattr(settings, 'SECRET_KEY', 'your-secret-key'), expire_seconds: int = 300):
        """
        初始化验证码生成器
        :param secret_key: 密钥
        :param expire_seconds: 过期时间(秒)，默认5分钟
        """
        self.secret_key = secret_key
        self.expire_seconds = expire_seconds

    def generate_code(self) -> str:
        """
        生成验证码
        :param data: 需要编码的数据
        :return: 验证码字符串
        """
        # 添加时间戳
        timestamp = int(time.time())
        payload = {
            'timestamp': timestamp,
        }
        
        # 将数据转为base64编码
        content = base64.b64encode(
            json.dumps(payload).encode('utf-8')
        ).decode('utf-8')
        
        # 生成签名
        signature = self._generate_signature(content)
        
        # 拼接验证码
        return {'code': f"{content}:{signature}"}
    
    def verify_code(self, code: str) -> dict:
        """
        验证校验码
        :param code: 校验码字符串
        :return: 原始数据
        """
        try:
            content, signature = code.split(':')
            
            # 验证签名
            if signature != self._generate_signature(content):
                raise ValueError("无效的校验码")
            
            # 解码数据
            payload = json.loads(
                base64.b64decode(content).decode('utf-8')
            )
            
            # 检查是否过期
            if time.time() - payload['timestamp'] > self.expire_seconds:
                raise ValueError("校验码已过期")
            
            payload['message'] = '更改权限成功'
            return payload
            
        except Exception as e:
            raise ValueError(f"校验码验证失败: {str(e)}")

    def _generate_signature(self, content: str) -> str:
        """
        生成签名
        :param content: 待签名内容
        :return: 签名字符串
        """
        sign_text = f"{content}{self.secret_key}"
        return hashlib.md5(sign_text.encode('utf-8')).hexdigest()[:6]