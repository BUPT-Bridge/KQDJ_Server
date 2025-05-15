from rest_framework.views import APIView
from utils.response import CustomResponse
from .models import StatusTypeNum, ViewNum, FormUserRelation
from django.utils.decorators import method_decorator
from utils.auth import auth
from utils.constance import ADMIN_USER, SUPER_ADMIN_USER
from proceed.models import MainForm
from proceed.utils.choice import UNHANDLED
from proceed.serializers import MainFormSerializer


class ViewNumStatsView(APIView):
    """
    访问量和注册量统计的API视图
    """
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


class TopUnhandledFormView(APIView):
    """
    获取前N个未处理表单的API视图
    默认返回前6条未处理的表单及其解决方案建议
    """
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER]))
    def get(self, request):
        """
        获取前N个未处理表单及其解决方案建议
        """
        return CustomResponse(self._get_top_unhandled_forms, request)
    
    def _get_top_unhandled_forms(self, request):
        """获取并返回前N个未处理表单"""
        # 从查询参数获取要返回的表单数量，默认为6
        limit = int(request.query_params.get('limit', 6))
        if limit > 20:  # 限制最大数量，避免返回过多数据
            limit = 20
            
        # 获取未处理的表单
        unhandled_forms = MainForm.query_manager.unhandled().order_by('-upload_time')[:limit]
        
        result = []
        for form in unhandled_forms:
            # 获取表单序列化数据
            form_data = MainFormSerializer(form).data
            # 获取关联的解决方案建议
            relation = FormUserRelation.objects.filter(main_form=form).first()
            from .serializers import EventsSerializer
            ser_data = EventsSerializer(relation).data
            result.append(ser_data)
            
        return {
            'message': '获取成功',
            'count': len(result),
            'forms': result
        }



