from rest_framework.views import APIView
from .models import Users, AllImageModel
from django.utils.decorators import method_decorator
from utils.wx_login import wx_login
from utils.response import CustomResponse
from utils.auth import auth
from utils.constance import *
from .utils.request_proceesor import request_proceesor
from .utils.validate import VerificationCode
from .utils.salt_manager import SaltManager
from .utils.web_login import get_wxacode
from django.http import HttpResponse
import hashlib  # 添加 hashlib 导入

# 在创建Response时，要求必须包含一个message字段，用于返回操作结果
# 例如：return Response({'message': '操作成功'})
# 其他字段可以根据需要自行添加
# 建议所有接口数据通过Body返回


class LoginOrRegisterWechat(APIView):
    # 从微信小程序注册/登录账号
    def post(self, request):
        # data=self._login_or_register(request)
        return CustomResponse(self._login_or_register, request)

    def _login_or_register(self, request) -> dict:
        # 获取请求数据
        data = request.data
        code = data["code"]  # 获取code 如果没有code会报错
        wx_info = wx_login(code)  # 获取微信openid
        openid = wx_info["openid"]  # 检查用户是否已存在
        if Users.objects.filter(openid=openid).exists():
            return self._login_from_wechat(openid)
        else:
            Users.objects.create(openid=openid)
        return {"message": "注册成功", "token": auth.generate_token(openid)}

    def _login_from_wechat(self, openid):
        Users.objects.filter(openid=openid)
        return {"message": "登录成功", "token": auth.generate_token(openid)}


class LoginTest(APIView):
    def post(self, request):
        return CustomResponse(self._login_or_register, request)

    def _login_or_register(self, request) -> dict:
        # 获取请求数据
        data = request.data
        openid = data["openid"]  # 获取code 如果没有code会报错

        if Users.objects.filter(openid=openid).exists():
            return self._login_from_wechat(openid)
        else:
            Users.objects.create(openid=openid)
        return {"message": "注册成功", "token": auth.generate_token(openid)}

    def _login_from_wechat(self, openid):
        Users.objects.get(openid=openid)
        return {"message": "登录成功", "token": auth.generate_token(openid)}


class UserInfo(APIView):
    @method_decorator(auth.token_required)
    def get(self, request):
        openid = request.openid
        return CustomResponse(self._get_user_info, openid)

    def _get_user_info(self, openid):
        # 获取用户信息
        user_queryset = Users.query_manager.self_fliter(openid)
        if not user_queryset.exists():
            raise Exception("用户不存在")
        user_data = Users.query_manager.self_fliter(openid).serialize()
        return user_data

    @method_decorator(auth.token_required)
    def put(self, request):
        openid = request.openid
        return CustomResponse(self._update_user_info, request, openid)

    def _update_user_info(self, request, openid):
        # 获取表单数据和文件
        data = request_proceesor(request)
        reply = Users.objects.get(openid=openid).update_user(data=data)
        return reply

    def post(self, request):
        return CustomResponse(self.login_code, request)

    def login_code(self, request):
        # 获取请求数据
        data = request.data
        phone = data["phone"]
        password = data["password"]
        # 将密码进行MD5加密
        md5 = hashlib.md5()
        md5.update(password.encode("utf-8"))
        encrypted_password = md5.hexdigest()
        print("加密后的密码:", encrypted_password)
        user = Users.query_manager.phone_fliter(phone)
        if not user.exists():
            raise Exception("用户不存在")
        if Users.query_manager.get_certain_password(phone) == encrypted_password:
            return {
                "message": "登录成功",
                "token": auth.generate_token(
                    Users.query_manager.phone_certain_fliter(phone)
                ),
                "permission": Users.query_manager.get_permission_level_phone(phone),
            }
        else:
            raise Exception("密码错误")


class AdminList(APIView):
    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def get(self, request):
        return CustomResponse(self._get_admin_list, request)

    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def put(self, request):
        openid = request.GET.get('openid',None)
        return CustomResponse(self._adjust_admin_list, request, openid)

    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def delete(self, request):
        openid = request.GET.get('openid',None)
        return CustomResponse(self._delete_admin, openid)

    def _get_admin_list(self, request):
        # 获取管理员、网格员和物业人员列表
        admin_grid_queryset = Users.query_manager.get_admin_and_grid_list()
        if not admin_grid_queryset.exists():
            raise Exception("没有管理员、网格员或物业人员")
        admin_data = admin_grid_queryset.paginate(request)
        return admin_data

    def _adjust_admin_list(self, request, openid):
        # 获取表单数据和文件
        data = request_proceesor(request)
        reply = Users.objects.get(openid=openid).update_user(data=data)
        return reply

    def _delete_admin(self, openid):
        # 删除管理员
        user = Users.query_manager.self_fliter(openid)
        if not user.exists():
            raise Exception("用户不存在")
        user.delete()
        return {"data": "删除成功"}


class ChangePermission(APIView):

    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER,ADMIN_USER]))
    def get(self, request):
        permission_type = request.GET.get('type', 'admin')
        return CustomResponse(self._generate_code, permission_type)

    @method_decorator(auth.token_required(required_permission=[COMMON_USER]))
    def post(self, request):
        code = request.data["code"]
        openid = request.openid
        return CustomResponse(self._verify_code, code, openid)

    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER, ADMIN_USER]))
    def put(self, request):
        phone = request.data.get("phone")
        permission_type = request.GET.get('type', 'grid')
        return CustomResponse(self._change_permission_by_phone, phone, permission_type)

    def _generate_code(self, permission_type):
        # 验证 permission_type 参数
        if permission_type not in ['admin', 'grid', 'property']:
            raise Exception("权限类型参数错误，仅支持 admin、grid 或 property")
        verification = VerificationCode()
        return verification.generate_code(permission_type)

    def _verify_code(self, code, openid):
        if not code:
            raise Exception("校验码不能为空")
        
        verification = VerificationCode()
        reply = verification.verify_code(code)
        
        # 从校验码中获取权限类型
        permission_type = reply.get('type', 'admin')
        
        # 根据不同的权限类型设置对应的权限等级
        if permission_type == 'admin':
            permission_level = ADMIN_USER
        elif permission_type == 'grid':
            permission_level = GRID_WORKER
        elif permission_type == 'property':
            permission_level = PROPERTY_STAFF
        else:
            raise Exception("无效的权限类型")
        
        Users.query_manager.self_fliter(openid).update(permission_level=permission_level)
        reply['permission_type'] = permission_type
        return reply

    def _change_permission_by_phone(self, phone, permission_type):
        if not phone:
            raise Exception("手机号不能为空")
        
        # 验证 permission_type 参数
        if permission_type not in ['grid', 'property']:
            raise Exception("权限类型参数错误，仅支持 grid 或 property")
        
        # 使用 phone_fliter 查询用户
        user_queryset = Users.query_manager.phone_fliter(phone)
        
        if not user_queryset.exists():
            raise Exception("该手机号对应的用户不存在")
        
        # 根据不同的权限类型设置对应的权限等级
        if permission_type == 'grid':
            permission_level = GRID_WORKER
            permission_name = "网格员"
        elif permission_type == 'property':
            permission_level = PROPERTY_STAFF
            permission_name = "物业人员"
        
        # 更新权限
        user_queryset.update(permission_level=permission_level)
        
        return {
            "message": "权限修改成功",
            "phone": phone,
            "new_permission": permission_name
        }


class LoginOrRegisterWeb(APIView):
    # 从微信小程序注册/登录账号
    def post(self, request):
        return CustomResponse(self._login_or_register, request)

    def _login_or_register(self, request) -> dict:
        # 获取请求数据
        salt = request.GET.get("salt")
        print("salt:", salt)
        if not salt:
            raise Exception("salt不能为空")
        data = request.data
        code = data["code"]  # 获取code 如果没有code会报错
        wx_info = wx_login(code)  # 获取微信openid
        openid = wx_info["openid"]  # 检查用户是否已存在
        if Users.objects.filter(openid=openid).exists():
            salt_manager = SaltManager()
            salt_manager.add_salt_openid(salt, openid)
            return self._login_from_wechat(openid)
        else:
            Users.objects.create(openid=openid)
            salt_manager = SaltManager()
            salt_manager.add_salt_openid(salt, openid)
        return {"message": "注册成功", "token": auth.generate_token(openid)}

    def _login_from_wechat(self, openid):
        Users.objects.filter(openid=openid)
        return {"message": "登录成功", "token": auth.generate_token(openid)}

    def get(self, request):
        # data=self._login_or_register(request)
        return CustomResponse(self._polling, request)

    def _polling(self, request) -> dict:
        # 获取请求数据
        salt = request.GET.get("salt")
        if not salt:
            raise Exception("salt不能为空")

        # 从JSON文件中获取openid
        salt_manager = SaltManager()
        openid = salt_manager.get_openid_by_salt(salt)

        if openid == "not_found":
            return {"message": "未找到对应的登录请求", "code": "not_found"}
        elif openid == "expired":
            return {"message": "登录请求已过期，请重新扫码", "code": "expired"}
        else:
            user_permission = Users.query_manager.get_permission_level(openid)
            # 找到有效的openid
            return {
                "message": "登录成功",
                "token": auth.generate_token(openid),
                "permission": user_permission,
            }


class WXACode(APIView):
    """
    获取微信小程序码
    GET: 生成并返回带有指定salt的微信小程序码
    """

    def get(self, request):
        # 获取请求参数中的salt
        salt = request.GET.get("salt")
        if not salt:
            raise Exception("salt不能为空")
        try:
            # 调用get_wxacode获取小程序码二进制数据
            qr_binary = get_wxacode(salt)
            # 返回二进制图片数据，设置正确的content-type
            return HttpResponse(qr_binary, content_type="image/png")
        except Exception as e:
            # 发生错误时返回错误信息
            return HttpResponse(str(e), status=500)


class ImageUploadAPI(APIView):
    """
    图片上传接口
    POST: 上传图片并返回保存路径
    """
    @method_decorator(auth.token_required)
    def post(self, request):
        return CustomResponse(self._upload_image, request)
        
    def _upload_image(self, request):
        openid = request.openid
        # 检查是否有文件上传
        if not request.FILES or 'file' not in request.FILES:
            raise Exception("没有找到上传的图片")
            
        image_file = request.FILES['file']
        # 创建并保存图片
        image_model = AllImageModel(image=image_file, openid=openid)
        image_model.save()
        
        # 获取保存的路径
        image_path = image_model.image.url if hasattr(image_model.image, 'url') else str(image_model.image)
        
        return {
            "path": image_path,
            "message": "图片上传成功"
        }


class ImportantUserManagement(APIView):
    """
    重要用户管理接口
    GET: 获取所有重要用户列表
    POST: 将用户标记为重要用户
    DELETE: 取消用户的重要标记
    """
    
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER]))
    def get(self, request):
        """获取所有重要用户列表"""
        return CustomResponse(self._get_important_users, request)
    
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER]))
    def post(self, request):
        """将用户标记为重要用户"""
        return CustomResponse(self._mark_as_important, request)
    
    @method_decorator(auth.token_required(required_permission=[ADMIN_USER, SUPER_ADMIN_USER]))
    def delete(self, request):
        """取消用户的重要标记"""
        return CustomResponse(self._unmark_as_important, request)
    
    def _get_important_users(self, request):
        """获取所有is_important为true的用户"""
        important_users = Users.query_manager.get_important_users()
        if not important_users.exists():
            return {"data": [], "message": "暂无重要用户"}
        
        # 支持分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        return important_users.paginate_data(page, page_size)
    
    def _mark_as_important(self, request):
        """将用户标记为重要用户"""
        phone = request.data.get('phone')
        if not phone:
            raise Exception("手机号不能为空")
        
        user_queryset = Users.query_manager.phone_fliter(phone)
        if not user_queryset.exists():
            raise Exception("该手机号对应的用户不存在")
        
        user_queryset.update(is_important=True)
        
        return {
            "message": "已将用户标记为重要",
            "phone": phone
        }
    
    def _unmark_as_important(self, request):
        """取消用户的重要标记"""
        phone = request.GET.get('phone') or request.data.get('phone')
        if not phone:
            raise Exception("手机号不能为空")
        
        user_queryset = Users.query_manager.phone_fliter(phone)
        if not user_queryset.exists():
            raise Exception("该手机号对应的用户不存在")
        
        user_queryset.update(is_important=False)
        
        return {
            "message": "已取消用户的重要标记",
            "phone": phone
        }