import requests
from typing import Dict, Optional

# 微信小程序配置
WX_APP_ID = "你的小程序APPID"
WX_APP_SECRET = "你的小程序SECRET"
WX_LOGIN_URL = "https://api.weixin.qq.com/sns/jscode2session"

def wx_login(code: str) -> Optional[Dict]:
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
            return data
            
        # 成功返回数据示例：{'session_key': 'xxx', 'openid': 'xxx'}
        return {
            'session_key': data.get('session_key'),
            'openid': data.get('openid')
        }
        
    except Exception as e:
        print(f"微信登录发生异常: {str(e)}")
        return None

# 使用示例
if __name__ == "__main__":
    test_code = "测试code"
    result = wx_login(test_code)
    if result:
        print("登录成功:", result)
    else:
        print("登录失败")
