from django.shortcuts import render

from rest_framework.views import APIView

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回
class UserFormFunctions(APIView):
    # 用户提交表单
    def handle_form(self,request):
        pass
    
    # 获取自己的表单(这两个接口我没有想好，这里是带参数进行选择查询未处理，已处理等等还是分开，这里可以考虑一下)
    def get_single_page(self,request):
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
    def delete_a_form(self,request):
        pass
