# 各个自定义接口的实现和示例

## Before Working

### 数据迁移与启动命令
1. 安装相应依赖
```cmd
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
```

2. 执行以下命令
```cmd
python manage.py makemigrations user proceed community analysis

python manage.py migrate
```

3. 直接运行服务

```cmd
python manage.py runserver 

```
`Attention!` 要在根目录下即/home/zhao/KQDJ_Server运行该命令

如果在局域网运行，想要别人连接到改服务运行：
```cmd
python manage.py runserver 0.0.0.0:8000 

```

### 调试方法 
- 建议采用`Reqable` [官网链接](https://reqable.com/)
#### 创建集合和请求
 该步骤比较简单自己做
#### 创建环境变量
![](./tutor_picture/屏幕截图%202025-04-02%20004340.png)
- 如图所示，创建名为`token`的环境变量
- 另外，我们强烈建议再创建一个名为`BASE_URL`的环境变量，将*localhost:8000/api*放入
#### 设置自动获取token脚本
如图
![](./tutor_picture/image.png)
如上位置设置python脚本
- `注意`前期测试采用test接口，test接口脚本如下
```python 
from reqable import *

def onRequest(context, request):
  return request

def onResponse(context, response):
  response.body.jsonify()
  print(response.body['data']['token'])
  context.env['token'] = response.body['data']['token']
  return response

```
- 另外在所有需要token校验的位置设置如下脚本

```python
from reqable import *

def onRequest(context, request):
  request.headers.add('Authorization', context.env['token'])
  return request

def onResponse(context, response):
  return response
```
即可丝滑启动

## When You Woring——开发接口调用规范

### Response接口调用规范
以如下代码为例
```python 
class LoginTest(APIView):
    def post(self, request):
        return CustomResponse(self._login_or_register,request)
```
- `class`后为类名，继承APIView
- `def` 定义api方法，正常逻辑函数写为私有函数，如<i>_login_or_register</i> ,前面加一个`_`

- `CustomResponse`为自定义错误处理和返回相应函数，接受的私有函数要求返回为<mark>dict(字典)</mark>格式，`CustomResponse`第二个参数为私有函数所需要的参数
- 如果有异常情况让报错终止函数，不需要在主函数中额外返回

### 修饰器调用规范(即token校验函数)
```python
    @method_decorator(auth.token_required)
    def get(self, request):
        openid = request.openid
        return CustomResponse(self._get_user_info, openid)
```
- 首先在需要被校验的函数上添加`@method_decorator`
- 在主函数中使用`request.openid`读取到解码之后的openid
- 使用`@method_decorator(auth.token_required(required_permission=[ADMIN_USER, SUPER_USER]))`进行权限控制

### 分页器调用规范
<mark>注意：</mark>所有列表只要是`多个`请进行分页操作！

- request的url示例: *http://localhost:8000/api/user/Adminlist?page=3&page_size=20*  主要是后面的查询参数
- 以下代码为`user/view`的调用示例，即在查询集后面加上`.paginate(request)`
```python
admin_data = admin_queryset.order_by('-created_at').paginate(request)
```
- 如果是**单个用户**进行查询请使用查询集后加`.serialize()` 如以下示例
```python 
user_data = Users.query_manager.self_fliter(openid).serialize()
```
### 每个表单update函数开发和调用规范

#### 开发规范
<mark>请注意！</mark>我们都将update函数卸载模型类之下的函数

- 如果修改集合为空，请采用`raise`抛出错误，这样才能在`CustomResponse`中正常返回
- 返回最好是`Dict`类型，而且建议加上`message`字段，这样可以直接显示出信息，让代码更**简洁**
```python 
self.save()
        updated_fields['message'] = '更新成功'
        return updated_fields
```
- **注意** 图片类型最好单独处理
- 每个模型的`utils.request_proceesor`要单独开发，每个模型不太一样

#### 调用规范
- 传入的data 需要经过`utils.request_proceesor`处理进行，将data进行规范化
- 直接传入处理后的data，调用示例如下
```python 
def _adjust_admin_list(self, request, openid):
  # 获取表单数据和文件
  data = request_proceesor(request)
  reply = Users.objects.get(openid=openid).update_user(data=data)
  return reply  
```

### 传入pk值调用规范
**有一些需要修改和删除需要附上图片的pk主键值**
- 在`DELETE`轮播图时候规范如下：*http://<<BASE_URL>>/api/community/banners?pk=9*
- 在**Phone**部分的`DELETE`和`PUT`请求下都需要加入url传参部分，示例如下：
*http://<<BASE_URL>>/api/community/phone_number?pk=2* 