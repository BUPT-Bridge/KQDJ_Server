from django.core.paginator import Paginator
from proceed.models import MainForm
from proceed.serializers import MainFormSerializer

def paginate_mainforms(request, queryset=None):
    """
    分页处理MainForm查询结果
    :param request: HTTP请求对象
    :param queryset: 可选的预过滤查询集
    :return: dict 包含分页数据和元数据
    """
    # 获取页码和每页数量参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # 如果没有提供查询集，则使用所有MainForm
    if queryset is None:
        queryset = MainForm.objects.all().order_by('-upload_time')
    
    # 创建分页器
    paginator = Paginator(queryset, page_size)
    
    # 获取当前页的数据
    current_page = paginator.get_page(page)
    
    # 序列化数据
    serializer = MainFormSerializer(current_page.object_list, many=True)
    
    # 返回分页数据
    return {
        'total': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': serializer.data
    }
