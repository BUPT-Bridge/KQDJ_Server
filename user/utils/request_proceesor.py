def request_proceesor(request):
    data = {
                'username': request.data.get('username'),
                'phone': request.data.get('phone'),
                'password': request.data.get('password'),
                'avatar': request.FILES.get('avatar')  # 从request.FILES获取上传的文件
            }
            # 过滤掉None值
    data = {k: v for k, v in data.items() if v is not None}
    return data