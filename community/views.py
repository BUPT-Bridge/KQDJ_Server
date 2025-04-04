from rest_framework.views import APIView
from utils.response import CustomResponse
from django.utils.decorators import method_decorator
from utils.auth import auth
from utils.constance import *
from .models import Banner,Notice, Cover, PageView
# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回

# 社区温馨提示
class WarmNoticeFunctions(APIView):
    def get(self,request):
        # 获取请求数据
        return CustomResponse(self._get_warm_notice)
        
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def put(self,request):
        return CustomResponse(self._update_warm_notice,request)

    def _get_warm_notice(self) -> dict:
        # 处理请求数据
        notice = Notice.objects.first()
        return {
            'message': '获取温馨提示成功',
            'data': notice.content if notice else '暂无温馨提示'
        }
    
    def _update_warm_notice(self,request) -> dict:
        data = request.data
        notice = data['notice']
        Notice.objects.all().delete()
        Notice.objects.create(content=notice)
        return {
            'message': '更新温馨提示成功',
            'data': notice
        }

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
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def get(self,request):
        # 获取请求数据
        return CustomResponse(self._get_visit_count)

    @method_decorator(auth.token_required(required_permission=[COMMON_USER,ADMIN_USER,SUPER_ADMIN_USER]))
    def put(self,request):
        # 获取请求数据
        return CustomResponse(self._update_visit_count)
    
    def _get_visit_count(self) -> dict:
        page_view = PageView.objects.first()
        if page_view:
            return {
                'message': '获取访问量成功',
                'data': page_view.view_count
            }

    def _update_visit_count(self)-> dict:
        # 处理请求数据
        page_view = PageView.objects.first()
        if page_view:
            page_view.view_count += 1
            page_view.save()
        else:
            PageView.objects.create(view_count=1)
        return {
            'message': '访问量更新成功'
        }
        