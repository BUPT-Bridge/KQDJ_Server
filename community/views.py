from django.shortcuts import render

from rest_framework.views import APIView

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回
class WarmNoticeFunctions(APIView):
    def get_warm_notice(self,request):
        pass
    
    def update_warm_notice(self,request):
        pass

class CoverFunctions(APIView):
    def get_cover(self,request):
        pass
    
    def update_cover(self,request):
        pass

class BanerFunctions(APIView):
    def get_all_banners(self,request):
        pass
    
    def add_a_banner(self,request):
        pass
    
    def delete_a_banner(self,request):
        pass
    