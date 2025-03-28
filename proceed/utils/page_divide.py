"""
可能没用处了
"""

from django.core.paginator import Paginator

def paginate_queryset(request, queryset, simple=False):
    """
    通用分页处理函数
    :param request: HTTP请求对象
    :param queryset: 查询集
    :param simple: 是否使用简单序列化
    :return: dict 包含分页数据和元数据
    """
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))

    paginator = Paginator(queryset, page_size)
    current_page = paginator.get_page(page)
    
    if not hasattr(current_page.object_list, 'serialize'):
        raise ValueError("查询集必须实现serialize方法")

    return {
        'total': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': current_page.object_list.serialize(simple=simple)
    }
