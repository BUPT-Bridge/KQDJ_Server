from rest_framework.response import Response
from typing import Any,Callable,Dict

def CustomResponse(function: Callable[..., Dict[str, Any]], *args, **kwargs):
    """
    自定义响应函数
    :param data: 响应数据
    :param function: 函数名，该函数必须返回一个字典
    :return: 响应对象
    """
    try: 
        data = function(*args, **kwargs)
        return Response({'data':data,'code':200,'message':'success'})
    except Exception as e:
        return Response({'code': 400, 'message': f"出现错误：{e}"})