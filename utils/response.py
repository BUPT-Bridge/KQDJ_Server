from rest_framework.response import Response
from typing import Any,Callable,Dict
from django.http import HttpResponse

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

def CustomFileResponse(function: Callable[..., Any], *args, **kwargs):
    try:
        output = function(*args, **kwargs)
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="MainForm_Data.xlsx"'
        return response
    except Exception as e:
        return Response({'code': 400, 'message': f"出现错误：{e}"})
    
from typing import Any, Callable, Dict

class CustomResponseSync(Response):
    def __init__(self, data=None, message="success", status=200, **kwargs):
        response_data = {
            "message": message,
            "data": data
        }
        response_data.update(kwargs)
        super().__init__(data=response_data, status=status)