from datetime import datetime

def generate_custom_uuid(serial_number=None, type: str = 'suggest') -> str:
        if not serial_number:
            # 将导入移到函数内部
            from ..models import MainForm as MainFormModel
            
            # 获取类型前缀
            type_prefix = 'J' if type == 'suggest' else 'T'
            
            # 获取当前日期字符串
            current_date = datetime.now().strftime('%Y%m%d')
            
            # 获取当天同类型的表单数量
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_timestamp = int(today_start.timestamp())
            count = MainFormModel.objects.filter(
                upload_time__gte=today_timestamp,
                type=type  # 只统计同类型的表单
            ).count()
            print(count)
            # 生成序号（从1开始）
            sequence_number = count + 1
            
            # 组合UUID
            return f"{type_prefix}-{current_date}-{sequence_number}"
        else:
            return serial_number