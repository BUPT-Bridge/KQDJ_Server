from utils.auth import auth
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from utils.response import CustomResponse, CustomResponseSync
from .models import MainForm
import asyncio
from utils.constance import *


# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回
class UserFormFunctions(APIView):

    @method_decorator(auth.token_required)
    def post(self, request):
        # 使用同步方式调用异步方法
        async def _async_post():
            permission_level = request.permission_level
            user_openid = request.openid
            form_data = request.data
            form_images = request.FILES.getlist("form_images")
            source = "user" if permission_level == 0 else "admin"

            form = await self._create_form(
                form_data, form_images, source, user_openid=user_openid
            )
            return CustomResponseSync(data=form, message="表单创建成功")

        # 使用 sync_to_async 运行异步代码
        return asyncio.run(_async_post())

    async def _create_form(
        self, form_data, images=None, source="user", user_openid=None
    ):
        # 创建表单
        form = await MainForm.query_manager.create_form(
            form_data, images, source, user_openid=user_openid
        )
        return form

    @method_decorator(auth.token_required)
    def get(self, request):
        is_single = request.GET.get("uuid", None)
        finished = request.GET.get("finish", 0)
        if not is_single:
            # 获取所有表单
            return CustomResponse(
                self._get_multi_pages, request, openid=request.openid, finished=finished
            )
        else:
            # 获取单个表单
            return CustomResponse(self._get_single_page, is_single)

    def _get_multi_pages(self, request, openid, finished):
        mainform_queryset = MainForm.query_manager.filter_by_openid(openid).filter(
            handle=finished
        )
        if not mainform_queryset.exists():
            raise Exception("对应表单不存在")
        return mainform_queryset.order_by("-upload_time").paginate(request, simple=True)

    def _get_single_page(self, is_pk):
        return MainForm.query_manager.get_queryset().filter(uuidx=is_pk).serialize()

    @method_decorator(auth.token_required)
    def put(self, request):
        is_pk = request.GET.get("uuid", None)
        if not is_pk:
            raise Exception("uuid不能为空")
        return CustomResponse(self._update_form, request, is_pk)

    def _update_form(self, request, is_pk):
        evaluate_info = request.data
        form_evaulation = MainForm.objects.filter(uuidx=is_pk).first()
        form_evaulation.update_form(evaluation_info=evaluate_info)
        from .serializers import MainFormSerializer

        return {"message": "评价成功", "data": MainFormSerializer(form_evaulation).data}


class AdminFormFunctions(APIView):
    # 拉起表单(单表单和多表单)
    @method_decorator(
        auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER])
    )
    def get(self, request):
        is_pk = request.GET.get("uuid", None)
        finished = request.GET.get("finish", 0)
        if not is_pk:
            # 获取所有表单
            return CustomResponse(
                self._admin_get_multi_forms, request, finished=finished
            )
        else:
            # 获取单个表单详情
            return CustomResponse(self._admin_get_single_form, is_pk)

    def _admin_get_single_form(self, is_pk):
        form = MainForm.query_manager.get_queryset().filter(uuidx=is_pk)
        if not form:
            raise Exception("表单不存在")
        return form.serialize()

    def _admin_get_multi_forms(self, request, finished):
        form = MainForm.query_manager.get_queryset().filter(handle=finished)
        if not form:
            raise Exception("表单不存在")
        return form.order_by("-upload_time").paginate(request, simple=True)

    # 处理一个表单
    @method_decorator(
        auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER])
    )
    def put(self, request):
        is_pk = request.GET.get("uuid", None)
        if not is_pk:
            raise Exception("表单UUID不能为空")

        return CustomResponse(self._handle_a_form, request, is_pk)

    def _handle_a_form(self, request, is_pk):
        update_info = request.data
        openid = request.openid
        form = MainForm.objects.filter(uuidx=is_pk).first()

        if not form:
            raise Exception("表单不存在")
        # update_info["admin_openid"] = openid
        # 更新表单状态和管理员处理信息
        form.update_form(handle_info=update_info, openid=openid)

        from .serializers import MainFormSerializer

        return {"message": "表单处理成功", "data": MainFormSerializer(form).data}

    # 删除表单
    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def delete(self, request):
        return CustomResponse(self._delete_a_form, request)

    def _delete_a_form(self, request):
        # 从请求体中获取要删除的表单ID列表
        form_ids = request.data.get("form_uuids", [])

        if not form_ids:
            raise Exception("未指定要删除的表单UUID")

        # 记录删除结果
        deletion_results = {"successful": [], "failed": []}

        # 删除表单
        for form_id in form_ids:
            try:
                form = MainForm.objects.get(uuidx=form_id)
                form_info = {
                    "uuid": form_id,
                    "title": getattr(form, "title", f"表单-{form_id}"),
                }
                form.delete()
                deletion_results["successful"].append(form_info)
            except MainForm.DoesNotExist:
                deletion_results["failed"].append(
                    {"id": form_id, "reason": "表单不存在"}
                )
            except Exception as e:
                deletion_results["failed"].append({"id": form_id, "reason": str(e)})

        return {
            "message": f"成功删除{len(deletion_results['successful'])}个表单，失败{len(deletion_results['failed'])}个",
            "data": deletion_results,
        }


class AdminFormHandleFunctions(APIView):
    # 获取待回访表单
    @method_decorator(
        auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER])
    )
    def get(self, request):
            return CustomResponse(self._admin_get_multi_forms, request)

    def _admin_get_multi_forms(self, request):
        form = MainForm.query_manager.feedback_needed()
        if not form:
            raise Exception("表单不存在")
        return (
            form
            .order_by("-upload_time")
            .paginate(request, simple=True)
        )
    
    # 处理一个表单
    @method_decorator(
        auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER])
    )
    def put(self, request):
        is_pk = request.GET.get("uuid", None)
        if not is_pk:
            raise Exception("表单UUID不能为空")

        return CustomResponse(self._handle_a_form, request, is_pk)

    def _handle_a_form(self, request, is_pk):
        update_info = request.data
        form = MainForm.objects.filter(uuidx=is_pk).first()

        if not form:
            raise Exception("表单不存在")

        # 更新表单状态和管理员处理信息
        form.update_form(feedback_info=update_info)

        from .serializers import MainFormSerializer

        return {"message": "表单处理成功", "data": MainFormSerializer(form).data}
    
class List2Excel(APIView):    
    @method_decorator(
        auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER])
    )
    def post(self, request):
        data = request.data
        start_date = data.get("start_time", "")
        end_date = data.get("end_time", "")
        try:
            from .utils.handle_timestamp import process_date_range
            start_timestamp, end_timestamp = process_date_range(start_date, end_date)
            return MainForm.export_to_excel(start_timestamp, end_timestamp)

        except Exception as e:
            raise Exception(str(e))
