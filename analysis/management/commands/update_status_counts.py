"""
update_status_counts命令模块
用于手动更新StatusTypeNum模型中的状态计数
"""
from django.core.management.base import BaseCommand
from analysis.models import StatusTypeNum
# python manage.py update_status_counts

class Command(BaseCommand):
    help = '根据MainForm模型的当前状态更新StatusTypeNum模型'
    
    def add_arguments(self, parser):
        """添加命令行参数"""
        parser.add_argument(
            '--no-optimize',
            action='store_true',
            dest='no_optimize',
            help='禁用优化模式(使用多次查询)',
        )
        parser.add_argument(
            '--status-only',
            action='store_true',
            dest='status_only',
            help='只更新状态计数，不更新类别计数',
        )
        parser.add_argument(
            '--category-only',
            action='store_true',
            dest='category_only',
            help='只更新类别计数，不更新状态计数',
        )
        parser.add_argument(
            '--category',
            type=str,
            dest='category',
            help='只更新指定的类别计数',
        )

    def handle(self, *args, **kwargs):
        """
        命令处理函数
        """
        try:
            # 获取参数
            optimize = not kwargs.get('no_optimize', False)
            status_only = kwargs.get('status_only', False)
            category_only = kwargs.get('category_only', False)
            specific_category = kwargs.get('category')
            
            result_message = f'状态计数已成功更新 ({"优化模式" if optimize else "标准模式"}):\n'
            
            # 根据参数决定执行的操作
            if category_only:
                # 只更新类别计数
                status_num = StatusTypeNum.update_category_counts(
                    optimize=optimize,
                    specific_category=specific_category
                )
                result_message = f'类别计数已成功更新 ({"优化模式" if optimize else "标准模式"}):\n'
            elif specific_category:
                # 更新特定类别计数
                status_num = StatusTypeNum.update_category_counts(
                    optimize=optimize,
                    specific_category=specific_category
                )
                result_message = f'"{specific_category}"类别计数已成功更新 ({"优化模式" if optimize else "标准模式"}):\n'
            else:
                # 更新所有计数
                status_num = StatusTypeNum.update_counts(
                    optimize=optimize,
                    update_category=not status_only
                )
            
            # 构建输出消息
            status_info = (
                f'未处理: {status_num.Unhandle}\n'
                f'处理中: {status_num.Handling}\n'
                f'已处理: {status_num.Handled}\n'
                f'待回访: {status_num.WaitCallback}'
            )
            
            category_info = (
                f'\n类别计数:\n'
                f'物业纠纷类: {status_num.PropertyDispute}\n'
                f'公共设施维护类: {status_num.PublicFacility}\n'
                f'环境卫生与秩序类: {status_num.Environment}\n'
                f'邻里矛盾类: {status_num.NeighborConflict}'
            )
            
            # 输出结果
            if not category_only:
                result_message += status_info
            if not status_only:
                result_message += category_info
                
            self.stdout.write(self.style.SUCCESS(result_message))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'更新状态计数失败: {str(e)}'))
