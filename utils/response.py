from rest_framework.response import Response
def api_response(data: any, code: int = 200, message: str = "success!") -> dict:
    return Response({'code': code, 'message': message, 'data': data})

def error_response(data: any, code: int = 400, message: str = "error...") -> dict:
    return Response({'code': code, 'message': message, 'data': data})
