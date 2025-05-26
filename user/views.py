from rest_framework.views import APIView
from .models import Users
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
import time
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

    @method_decorator(auth.token_required)
    def put(self, request):
        openid = request.openid
        return CustomResponse(self._adjust_admin_list, request, openid)

    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def delete(self, request):
        openid = request.openid
        return CustomResponse(self._delete_admin, openid)

    def _get_admin_list(self, request):
        # 获取管理员列表
        admin_queryset = Users.query_manager.permission_fliter(ADMIN_USER)
        if not admin_queryset.exists():
            raise Exception("没有管理员")
        admin_data = admin_queryset.order_by("-created_at").paginate(request)
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

    @method_decorator(auth.token_required(required_permission=[SUPER_ADMIN_USER]))
    def get(self, _):
        return CustomResponse(self._generate_code)

    @method_decorator(auth.token_required(required_permission=[COMMON_USER]))
    def post(self, request):
        code = request.data["code"]
        openid = request.openid
        return CustomResponse(self._verify_code, code, openid)

    def _generate_code(self):
        verification = VerificationCode()
        return verification.generate_code()

    def _verify_code(self, code, openid):
        if not code:
            raise Exception("用户不存在")
        else:
            verification = VerificationCode()
            reply = verification.verify_code(code)
        Users.query_manager.self_fliter(openid).update(permission_level=ADMIN_USER)
        return reply


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
