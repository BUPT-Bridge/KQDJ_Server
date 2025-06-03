import requests
import time
import os
import json
from typing import Dict
from io import BytesIO
from utils.env_loader import env_vars

# 存储 access_token 的文件路径
TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'access_token.json')
PATH = "pages/weblogin/index"
SAVE_PATH = "./"
APPID = env_vars.APP_ID
APP_SECRET = env_vars.APP_SECRET

def update_access_token_if_needed(force: bool = False) -> str:
    """
    检查 access_token 是否需要更新，如需要则更新
        
    Returns:
        当前有效的 access_token
    """
    cached_token = _get_cached_token()
    # 如果没有缓存的 token 或者 token 已经过期
    if not cached_token or cached_token.get('expires_at', 0) <= time.time():
        return _get_access_token(force=force)
    return cached_token['access_token']

def _get_access_token(force: bool = False) -> str:
    """
    获取微信 access_token
    
    Args:
        force: 是否强制刷新 token

    Returns:
        获取到的 access_token
    """
    # 检查是否已有缓存的 token 且未过期
    cached_token = _get_cached_token()
    if not force and cached_token and cached_token.get('expires_at', 0) > time.time():
        return cached_token['access_token']
    
    # 请求新的 access_token
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": APPID,
        "secret": APP_SECRET
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        result = response.json()
        
        if 'errcode' in result and result['errcode'] != 0:
            raise Exception(f"获取 access_token 失败: {result.get('errmsg', '未知错误')}")
        
        # 保存 token 和过期时间
        access_token = result['access_token']
        expires_in = result['expires_in']
        # 提前 5 分钟过期，确保有足够时间更新
        expires_at = time.time() + expires_in - 300
        
        _save_token_to_cache(access_token, expires_at)
        return access_token
        
    except Exception as e:
        # 如果请求失败但有缓存的 token，则返回缓存的 token
        if cached_token:
            return cached_token['access_token']
        raise e


def _get_cached_token() -> Dict:
    """获取缓存的 token 信息"""
    if not os.path.exists(TOKEN_FILE):
        # 确保目录存在
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        return {}
    
    try:
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def _save_token_to_cache(access_token: str, expires_at: float) -> None:
    """保存 token 到缓存文件"""
    # 确保目录存在
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    
    token_data = {
        'access_token': access_token,
        'expires_at': expires_at,
        'updated_at': time.time()
    }
    
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)


def get_wxacode(salt: str, env_version: str = "trial") -> BytesIO:
    """
    获取微信小程序码
    
    Args:
        salt: 唯一标识符，用于登录验证
        env_version: 环境版本，可选值：release、trial、develop，默认为 release
    
    Returns:
        包含小程序码图片的二进制数据的 BytesIO 对象
    
    Raises:
        Exception: 获取小程序码失败时抛出异常
    """
    # 获取 access_token
    access_token = update_access_token_if_needed()
    
    # 构建请求 URL
    url = f"https://api.weixin.qq.com/wxa/getwxacode?access_token={access_token}"
    print(f"{PATH}?salt={salt}")
    # 构建请求体
    data = {
        "path": f"{PATH}?salt={salt}",
        "env_version": env_version
    }
    
    try:
        # 发送请求并接收二进制响应
        response = requests.post(url, json=data)
        
        # 检查响应内容
        if response.headers.get('Content-Type') == 'application/json':
            # 如果响应是 JSON，可能表示有错误
            error_info = response.json()
            raise Exception(f"获取小程序码失败: {error_info.get('errmsg', '未知错误')}")
        
        # 如果是二进制数据，表示成功获取图片
        print("获取小程序码成功")
        
        # 直接返回二进制内容
        return response.content
    
    except Exception as e:
        if isinstance(e, requests.RequestException):
            raise Exception(f"网络请求失败: {str(e)}")
        raise e