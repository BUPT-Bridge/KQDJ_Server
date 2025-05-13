import requests
import json
from typing import Dict, Optional

# 微信网页应用配置（需要替换为您的实际配置）
WX_WEB_APP_ID = "wxbdc5610cc59c1631"
WX_WEB_APP_SECRET = "ee5a5f2802fbfeeef23ec2d518d847ac" 
WEB_REDIRECT_URI = "http://8.130.167.117:80/"  # 需要进行urlencode编码

def get_qrconnect_url() -> str:
    """
    获取微信扫码登录的URL
    :return: 微信扫码登录URL
    """
    import urllib.parse
    
    redirect_uri = urllib.parse.quote(WEB_REDIRECT_URI)
    
    # 构建微信扫码登录的URL
    qrconnect_url = (
        f"https://open.weixin.qq.com/connect/qrconnect"
        f"?appid={WX_WEB_APP_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=snsapi_login"
        f"&state={generate_state()}"
        f"#wechat_redirect"
    )
    
    return qrconnect_url

def generate_state() -> str:
    """
    生成state参数，用于防止CSRF攻击
    :return: state字符串
    """
    import uuid
    import time
    import hashlib
    
    # 生成一个随机的state
    state = hashlib.md5(f"{uuid.uuid4()}{time.time()}".encode()).hexdigest()
    return state

def get_access_token(code: str) -> Dict:
    """
    通过code获取网页授权access_token
    :param code: 微信扫码登录回调返回的code
    :return: 包含access_token和openid等信息的字典
    """
    try:
        # 请求地址
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        
        # 请求参数
        params = {
            'appid': WX_WEB_APP_ID,
            'secret': WX_WEB_APP_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        
        # 发送请求
        response = requests.get(url, params=params)
        data = response.json()
        
        # 检查是否有错误
        if 'errcode' in data:
            print(f"获取网页授权access_token错误: {data['errmsg']}")
            raise Exception(data['errmsg'])
            
        # 返回access_token等信息
        return {
            'access_token': data.get('access_token'),
            'expires_in': data.get('expires_in'),
            'refresh_token': data.get('refresh_token'),
            'openid': data.get('openid'),
            'scope': data.get('scope'),
            'unionid': data.get('unionid', '')
        }
        
    except Exception as e:
        print(f"获取网页授权access_token异常: {str(e)}")
        raise Exception(f"获取网页授权access_token失败: {str(e)}")

def get_user_info(access_token: str, openid: str) -> Dict:
    """
    通过access_token和openid获取用户信息
    :param access_token: 网页授权接口调用凭证
    :param openid: 用户唯一标识
    :return: 用户信息字典
    """
    try:
        # 请求地址
        url = "https://api.weixin.qq.com/sns/userinfo"
        
        # 请求参数
        params = {
            'access_token': access_token,
            'openid': openid
        }
        
        # 发送请求
        response = requests.get(url, params=params)
        data = response.json()
        
        # 检查是否有错误
        if 'errcode' in data:
            print(f"获取用户信息错误: {data['errmsg']}")
            raise Exception(data['errmsg'])
            
        # 返回用户信息
        return data
        
    except Exception as e:
        print(f"获取用户信息异常: {str(e)}")
        raise Exception(f"获取用户信息失败: {str(e)}")

def check_access_token(access_token: str, openid: str) -> bool:
    """
    检验授权凭证（access_token）是否有效
    :param access_token: 网页授权接口调用凭证
    :param openid: 用户唯一标识
    :return: 是否有效
    """
    try:
        # 请求地址
        url = "https://api.weixin.qq.com/sns/auth"
        
        # 请求参数
        params = {
            'access_token': access_token,
            'openid': openid
        }
        
        # 发送请求
        response = requests.get(url, params=params)
        data = response.json()
        
        # 如果返回的errcode为0，说明access_token有效
        return data.get('errcode', -1) == 0
        
    except Exception as e:
        print(f"检验access_token有效性异常: {str(e)}")
        return False

def refresh_access_token(refresh_token: str) -> Dict:
    """
    刷新或续期access_token使用
    :param refresh_token: 用户刷新access_token
    :return: 刷新后的access_token信息
    """
    try:
        # 请求地址
        url = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
        
        # 请求参数
        params = {
            'appid': WX_WEB_APP_ID,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        # 发送请求
        response = requests.get(url, params=params)
        data = response.json()
        
        # 检查是否有错误
        if 'errcode' in data:
            print(f"刷新access_token错误: {data['errmsg']}")
            raise Exception(data['errmsg'])
            
        # 返回刷新后的access_token信息
        return {
            'access_token': data.get('access_token'),
            'expires_in': data.get('expires_in'),
            'refresh_token': data.get('refresh_token'),
            'openid': data.get('openid'),
            'scope': data.get('scope')
        }
        
    except Exception as e:
        print(f"刷新access_token异常: {str(e)}")
        raise Exception(f"刷新access_token失败: {str(e)}")