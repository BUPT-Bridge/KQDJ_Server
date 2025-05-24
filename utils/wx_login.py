import requests
from typing import Dict
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)
# 微信小程序配置
WX_APP_ID = os.getenv("APP_ID")
WX_APP_SECRET = os.getenv("APP_SECRET")
WX_LOGIN_URL = "https://api.weixin.qq.com/sns/jscode2session"

if not WX_APP_ID or not WX_APP_SECRET:
    raise ValueError("环境变量 APP_ID 或 APP_SECRET 未设置")  # 替换为你的实际APP ID和Secret


def wx_login(code: str) -> Dict:
    """
    微信小程序登录
    :param code: 小程序登录时获取的 code
    :return: 返回登录信息字典，登录失败返回 None
    """
    try:
        # 准备请求参数
        params = {
            'appid': WX_APP_ID,
            'secret': WX_APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        # 发送请求到微信服务器
        response = requests.get(WX_LOGIN_URL, params=params)
        data = response.json()
        
        if 'errcode' in data:
            print(f"微信登录错误: {data['errmsg']}")
            raise Exception(data['errmsg'])
            # return data
        return {
            'session_key': data.get('session_key'),
            'openid': data.get('openid')
        }
        
    except Exception as e:
        print(f"微信登录发生异常: {str(e)}")
        raise Exception(f"微信登录失败: {str(e)}")