import json
import os
import time
from datetime import datetime, timedelta

class SaltManager:
    def __init__(self, file_path='user/utils/data/salt_openid.json'):
        self.file_path = file_path
        self.ensure_file_exists()
        
    def ensure_file_exists(self):
        """确保JSON文件存在，不存在则创建"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
    
    def load_data(self):
        """加载JSON数据"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_data(self, data):
        """保存数据到JSON文件"""
        with open(self.file_path, 'w') as f:
            json.dump(data, f)
    
    def add_salt_openid(self, salt, openid):
        """添加salt-openid对"""
        data = self.load_data()
        # 设置过期时间为5分钟后
        expire_time = (datetime.now() + timedelta(minutes=5)).timestamp()
        
        data[salt] = {
            "openid": openid,
            "expire_at": expire_time
        }
        
        self.save_data(data)
        return True
    
    def get_openid_by_salt(self, salt):
        data = self.load_data()
        if salt in data:
            if data[salt]["expire_at"] > datetime.now().timestamp():
                return data[salt]["openid"]
            else:
            # 过期了，删除该记录
                del data[salt]
                self.save_data(data)
                return "expired"
        return "not_found"
    
    def clean_expired(self):
        """清理过期的salt-openid对"""
        data = self.load_data()
        now = datetime.now().timestamp()
        
        # 过滤掉已过期的记录
        updated_data = {salt: value for salt, value in data.items() 
                       if value["expire_at"] > now}
        
        if len(updated_data) != len(data):
            self.save_data(updated_data)
        
        return len(data) - len(updated_data)  # 返回删除的记录数