from rest_framework.views import APIView
from utils.response import CustomResponse
from django.utils.decorators import method_decorator
from utils.auth import auth
from utils.constance import *
from .models import Banners,Notice, Cover, PageView,PhoneNumber
from .utils.limit import xianxing
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
            'notice': notice.content if notice else '暂无温馨提示'
        }
    
    def _update_warm_notice(self,request) -> dict:
        data = request.data
        notice = data['notice']
        Notice.objects.all().delete()
        Notice.objects.create(content=notice)
        return {
            'notice': notice
        }

# 管理端封面 这个封面只有获取和修改
class CoverFunctions(APIView):
    def get(self,request):
        return CustomResponse(self._get_cover)
    
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def post(self,request):
        return CustomResponse(self._update_cover, request)
    
    def _get_cover(self):
        return Cover.query_manager.get_cover()

    def _update_cover(self, request) -> dict:
        cover_image = request.FILES.get('cover')
        if not cover_image:
            raise ValueError("没有提供封面图片")
        return Cover.update_cover(cover_image)

# 管理端轮播图
class BanerFunctions(APIView):
    def get(self,request):
        return CustomResponse(self._get_banner)
    
    def _get_banner(self):
        return Banners.query_manager.get_banners()

    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def post(self, request):
        return CustomResponse(self._add_banner, request)

    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def delete(self,request):
        return CustomResponse(self._delete_banner, request)
    
    def _delete_banner(self, request) -> dict:
        pk = request.GET.get('pk')
        return Banners.query_manager.delete_banner(pk)

    def _add_banner(self, request) -> dict:
        return Banners.query_manager.create_banner(request)

# 获取限行信息
class CarLimitFunctions(APIView):
    # 获取请求数据
    def get(self,request):
        # 获取请求数据
        return CustomResponse(self._get_limit)
    def _get_limit(self):
        today,tomorrow = xianxing()
        return {
            'today_limit': today,
            'tomorrow_limit': tomorrow
        }

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
    # 获取请求数据
    def get(self,request,):
        return CustomResponse(self._get_tele)
    def _get_tele(self):
        return PhoneNumber.query_manager.get_phone_number()
    
    # 添加社区电话
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def post(self,request):
        return CustomResponse(self._add_tele,request)
    def _add_tele(self,request):
        return PhoneNumber.query_manager.update_phone_number(
        phone_name=request.data['phone_name'],
        phone_number=request.data['phone_number']
    )
    
    # 删除社区电话
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER,SUPER_ADMIN_USER]))
    def delete(self,request):
        return CustomResponse(self._delete_tele,request)
    def _delete_tele(self,request):
        pk = request.GET.get('pk')
        return PhoneNumber.query_manager.delete_phone_number(pk)
    
    def put(self,request):
        # 更新社区电话
        return CustomResponse(self._update_tele,request)
    def _update_tele(self,request):
        pk = request.GET.get('pk')
        return PhoneNumber.query_manager.update_phone_number(
        phone_name=request.data['phone_name'],
        phone_number=request.data['phone_number'],
        pk=pk
    )
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
                'view_count': page_view.view_count
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
