from django.shortcuts import render

from rest_framework.views import APIView

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回

# 社区温馨提示
class WarmNoticeFunctions(APIView):
    def get_warm_notice(self,request):
        pass
    
    def update_warm_notice(self,request):
        pass

# 管理端封面
class CoverFunctions(APIView):
    def get_cover(self,request):
        pass
    
    def update_cover(self,request):
        pass

# 管理端轮播图
class BanerFunctions(APIView):
    def get_all_banners(self,request):
        pass
    
    def add_a_banner(self,request):
        pass
    
    def delete_a_banner(self,request):
        pass

# 获取限行信息
class LimitFunctions(APIView):
    def get_limit(self,request):
        pass

# 发布社区风采
class TweetShowFunctions(APIView):
    def get_tweet(self,request):
        pass
    
    def add_tweet(self,request):
        pass
    
    def delete_tweet(self,request):
        pass

# 社区电话
class CommunityTele(APIView):
    def get_tele(self,request):
        pass

    def update_tele(self,request):
        pass

# 访问量获取
class VisitCountFunctions(APIView):
    def get_visit_count(self,request):
        pass

    def update_visit_count(self,request):
        pass    