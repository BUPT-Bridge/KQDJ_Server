from rest_framework.views import APIView
from utils.response import CustomResponse
from .models import StatusTypeNum, ViewNum
from django.utils.decorators import method_decorator
from utils.auth import auth
from utils.constance import ADMIN_USER, SUPER_ADMIN_USER


class ViewNumStatsView(APIView):
    """
    访问量和注册量统计的API视图
    """
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER]))
    def get(self, request):
        """
        获取近七天的访问量和注册量统计数据
        """
        return CustomResponse(self._get_view_stats)
    
    def _get_view_stats(self):
        """获取并返回最近7天的访问量和注册量统计"""
        # 触发一次更新，确保数据是最新的
        ViewNum.update_today_counts()
        
        # 获取所有记录，按日期降序排序
        records = ViewNum.objects.all().order_by('-date')[:7]
        
        stats = []
        for record in records:
            stats.append({
                'date': record.date.strftime('%m-%d'),
                'view_count': record.view_count,
                'enrollment_count': record.enrollment_count,
                'is_today': record.is_today
            })
            
        return {
            'message': '获取成功',
            'data': stats
        }


class StatusCountView(APIView):
    """
    获取当前表单状态数量的API视图
    """
    def get(self, request):
        """
        获取当前各状态的表单数量
        """
        return CustomResponse(self._get_status_counts, request)
    
    def _get_status_counts(self, request):
        """
        获取并返回最新的状态计数
        
        可接受的查询参数:
        - status_only: 只返回状态计数
        - category_only: 只返回类别计数
        """
        # 检查请求参数
        status_only = request.query_params.get('status_only', '').lower() == 'true'
        category_only = request.query_params.get('category_only', '').lower() == 'true'
        
        # 如果都没指定，返回全部
        if not status_only and not category_only:
            status_only = category_only = False
        
        # 获取状态计数实例
        # 注意: 这里不执行更新，而是获取现有的状态计数
        # 更新已经通过信号机制在后台完成
        status_num = StatusTypeNum.objects.first()
        
        # 如果没有实例，创建一个并更新
        if not status_num:
            status_num = StatusTypeNum.update_counts(optimize=True)
            
        result = {'message': '获取成功'}
        
        # 根据参数返回相应数据
        if not category_only:
            result.update({
                'status': {
                    'unhandled': status_num.Unhandle,
                    'handling': status_num.Handling, 
                    'handled': status_num.Handled,
                    'waiting_callback': status_num.WaitCallback,
                }
            })
            
        if not status_only:
            result.update({
                'categories': {
                    '物业纠纷类': status_num.PropertyDispute,
                    '公共设施维护类': status_num.PublicFacility,
                    '环境卫生与秩序类': status_num.Environment,
                    '邻里矛盾类': status_num.NeighborConflict,
                }
            })
            
        return result
    
    

