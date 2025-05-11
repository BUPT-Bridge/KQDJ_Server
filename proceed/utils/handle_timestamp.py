import datetime
import pytz

def timestamp_to_beijing_str(timestamp, format="%Y-%m-%d %H:%M:%S"):
    """
    将时间戳转换为北京时间字符串
    
    Args:
        timestamp (int): 时间戳（秒）
        format (str): 输出格式，默认为"YY-MM-DD"
        
    Returns:
        str: 格式化的北京时间字符串
    """
    beijing_tz = pytz.timezone('Asia/Shanghai')
    dt = datetime.datetime.fromtimestamp(timestamp, beijing_tz)
    return dt.strftime(format)

def process_date_range(start_date_str, end_date_str):
    """
    将YYYY-MM-DD格式的日期字符串转换为北京时间的时间戳
    开始日期转为当天0时0分0秒，结束日期转为当天23时59分59秒
    
    Args:
        start_date_str (str): 开始日期，格式为YYYY-MM-DD
        end_date_str (str): 结束日期，格式为YYYY-MM-DD
        
    Returns:
        tuple: (开始时间戳(秒), 结束时间戳(秒))
        
    Raises:
        Exception: 如果日期格式错误或选择了未来日期
    """
    # 检查日期是否为空
    if not start_date_str or not end_date_str:
        raise Exception("开始日期和结束日期不能为空")
    
    # 获取当前北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now = datetime.datetime.now(beijing_tz)
    today = now.date()
    
    try:
        # 解析日期字符串
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise Exception("日期格式错误，请使用YYYY-MM-DD格式")
    
    # 检查是否选择了未来日期
    if start_date > today or end_date > today:
        raise Exception("不能选择当前日期之后的时间")
    
    # 检查开始日期是否大于结束日期
    if start_date > end_date:
        raise Exception("开始日期不能大于结束日期")
    
    # 设置开始时间为当天00:00:00，结束时间为当天23:59:59
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
    
    # 添加北京时区信息
    start_datetime = beijing_tz.localize(start_datetime)
    end_datetime = beijing_tz.localize(end_datetime)
    
    # 转换为时间戳（秒）
    start_timestamp = int(start_datetime.timestamp())
    end_timestamp = int(end_datetime.timestamp())
    
    return start_timestamp, end_timestamp
