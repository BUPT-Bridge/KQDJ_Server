from utils.auth import auth
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from utils.response import CustomResponse, CustomResponseSync
from .models import MainForm
import asyncio
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser


# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回
class UserFormFunctions(APIView):
    parser_classes = (MultiPartParser,)
    
    @method_decorator(auth.token_required)
    def post(self, request, *args, **kwargs):
        # 使用同步方式调用异步方法
        async def _async_post():
            permission_level = request.permission_level
            user_openid = request.openid
            form_data = request.data
            form_images = request.FILES.getlist('form_images')
            source = 'user' if permission_level == 0 else 'admin'
            
            form = await self._create_form(form_data, form_images, source, user_openid=user_openid)
            return CustomResponseSync(data=form, message="表单创建成功")
        
        # 使用 sync_to_async 运行异步代码
        return asyncio.run(_async_post())

    async def _create_form(self, form_data, images=None, source="user", user_openid=None):
        # 创建表单
        form = await MainForm.query_manager.create_form(form_data, images, source, user_openid=user_openid)
        return form

    # 获取自己的表单(这两个接口我没有想好，这里是带参数进行选择查询未处理，已处理等等还是分开，这里可以考虑一下)
    @method_decorator(auth.token_required)
    def get(self,request):
        pass

    def get_multi_pages(self,request):
        pass
    
    # 评价自己的表单
    def evaluate_my_page(self,request):
        pass
    
class AdminFormFunctions(APIView):
    # 拉起表单(单表单和多表单)
    def admin_get_single_form(self,request):
        pass
    def admin_get_multi_forms(self,request):
        pass
    
    # 处理一个表单 // 接口复用 // 每次修改以下部分字段
    def handle_a_form(self,request):
        pass
    
    # 删除表单
    def delete_a_form(self,request):  # 只能开给最高管理
        pass
