# 矿桥东街社区服务器开发指南(v1.0.0)\[重制版\]

## 工作之前，你需要知道. . .

### 基础条件
1. Linux环境
2. 安装好了Python并且建好了环境 (`python`和`pip`能够正常使用)
3. 安装了make工具方便快速调试 (`sudo apt-get install make`)
4. 安装`Reqable`作为调试工具 (可选) ([官网链接](https://reqable.com/))
5. 阅读了`.env.example`，创建了属于自己的`.env`文件并设置好了环境变量(不要写任何注释)

### `make`命令详解
1. 安装相应依赖并设置环境变量
```bash
make setup
```

2. 初始化用户
```bash
USER="USERNAME" PASSWORD="PWD" make init
```

3. 运行服务
```bash
make run
```

4. 数据库迁移
```bash
make # make migrate 也可以
```

5. 删除缓存
```bash
make clean # 如果你想删库，使用 make cleanall
```

6. 设置环境变量
```bash
make env
```
> `Attention!` 要在根目录下即../KQDJ_Server下运行以上命令


### 调试方法

### 创建环境变量
- 如图，首先创建一个名为`Django`(或者你喜欢的其他名字)的集合

- 然后创建名为`BASE_URL`的环境变量，并将`localhost:8000`放入
    ![](./tutor_picture/屏幕截图%202025-04-02%20004340.png)

#### 自动获取token脚本

- 首先在如图位置设置python脚本
    ![](./tutor_picture/image.png)

- `注意`前期测试采用test接口，test接口脚本如下

    ```python 
    from reqable import *

    def onRequest(context, request):
      return request

    def onResponse(context, response):
      response.body.jsonify()
      # print(response.body['data']['token'])
      context.env['TOKEN'] = response.body['data']['token']
      return response

    ```
- 另外在所有需要token校验的位置设置如下脚本

    ```python
    from reqable import *

    def onRequest(context, request):
      request.headers.add('Authorization', context.env['TOKEN'])
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

- 接口`Url`示例: 
    
    `http://localhost:8000/api/user/Adminlist?page=3&page_size=20`
    
    主要是后面的查询参数

- 以下代码为`user/view`的调用示例：
    
    即在查询集后面加上`.paginate(request)`
    ```python
    admin_data = admin_queryset.order_by('-created_at').paginate(request)
    ```
- 如果是**单个用户**进行查询请使用查询集后加`.serialize()`
    
    如以下示例
    ```python 
    user_data = Users.query_manager.self_fliter(openid).serialize()
    ```
### 每个表单update函数开发和调用规范

#### 开发规范

<mark>请注意！</mark>我们都将update函数卸载模型类之下的函数

- 如果修改集合为空，请采用`raise`抛出错误，这样才能在`CustomResponse`中正常返回

- 返回最好是`Dict`类型，而且在一切正常情况下不必加上`message`字段，这样可以让代码更**简洁**

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

- 在`DELETE`轮播图时候规范如下：

    `http://<<BASE_URL>>/api/community/banners?pk=9`

- 在**Phone**部分的`DELETE`和`PUT`请求下都需要加入`Url`传参部分，示例如下：

    `http://<<BASE_URL>>/api/community/phone_number?pk=2` 

### 更新信息规范

有以下<mark>三次</mark>更新过程,**源代码**如下

```python
update_types = [
            bool(kwargs.get("handle_info")),
            bool(kwargs.get("feedback_info")),
            bool(kwargs.get("evaluation_info")),
        ]
```
1. handle_info

    这个为管理员第一次处理的信息

2. feedback_info

    这个是管理员第二次回访的信息(如果用户勾选需要回访)

3. evaluation_info

    用户评价信息通过此来更新

#### `evaluation_info` 评价更新

<mark>IMPORTANT!</mark>

评价更新接口发送规范：
```json
{
  "evaluation_info": "需要评价的数字"
}
```
- "evaluation": "需要评价的数字",为`int`类型

### 获取个人表单规范

执行`GET`获取表单时，我们通过`url`传入参数不同设置不同的获取函数

#### 获取个人对应的所有表单

- 使用`GET`方法

- 请求`http://<<BASE_URL>>/api/proceed/user_form?page=3&page_size=20`

#### 获取某一表单
- 使用`GET`方法

- 请求`http://<<BASE_URL>>/api/proceed/user_form?pk=1`*

- `pk`值是该表单的主键值，会在获取总表时候全部返回，相应请求即可

### 获取excel表

#### 请求接口
- 使用`POST`接口，请求接口类似如下：*http://<<BASE_URL>>/api/proceed/excel_get*
- 请求数据如下：
```json
{
  "start_time": "2025-3-12",
  "end_time": "2025-5-11"
}
```
- 必须严格按照如上`YYYY-MM-DD`格式，并且要求请求日期符合规范，不可为当天之后的日期

#### 前端解析

- 代码中逻辑如下：
```python

output = BytesIO()
        # 创建 HTTP 响应
        response = HttpResponse(
            output,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="MainForm_Data.xlsx"'

```
请根据response中相应修改的`type`进行解析

### 微信扫码登录
#### 接口调用原理
参考[微信开放平台](https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html)的文档进行开发
流程图如下：
![](./tutor_picture/D0wkkHSbtC6VUSHX4WsjP5ssg5mdnEmXO8NGVGF34dxS9N1WCcq6wvquR4K_Hcut.png)
1. 调用以及重定向接口均在前端完成
2. 前端只需要返回申请成功的`code`即可
3. 获得code后，按照正常wx登录逻辑即可
4. 最后返回前端一个token用于校验

#### 接口调用规范
- 使用`POST`方法，请求api:**http://0.0.0.0:8000/api/user/web_login**
- 请求体格式如下
```json
{
    "code": "······"
}
```

### 获取表单状态统计

#### 接口说明
此接口用于获取系统中各种表单的状态数量和类别统计。数据通过后台信号机制自动更新，确保统计数据实时准确。

#### 数据统计内容
- 表单状态统计：未处理、处理中、已处理、待回访的表单数量
- 表单类别统计：物业纠纷类、公共设施维护类、环境卫生与秩序类、邻里矛盾类的表单数量
- 可选择只获取状态统计或只获取类别统计

#### 接口调用规范
- 使用`GET`方法，请求api:**http://<<BASE_URL>>/api/analysis/status**
- 可选查询参数:
  - `status_only=true` 仅返回状态统计
  - `category_only=true` 仅返回类别统计
  - 不传参数则返回全部统计信息

#### 返回数据格式
```json
{
    "message": "获取成功",
    "status": {
        "unhandled": 10,
        "handling": 5,
        "handled": 20,
        "waiting_callback": 3
    },
    "categories": {
        "物业纠纷类": 12,
        "公共设施维护类": 8,
        "环境卫生与秩序类": 15,
        "邻里矛盾类": 3
    }
}
```

### 获取访问量和注册量统计

#### 接口说明
此接口用于获取系统近七天的访问量和用户注册量统计数据。数据每10分钟自动更新一次，确保数据实时性。

#### 数据存储特性
- 存储近七天的访问量和注册量数据，循环覆写
- 前七天数据固定存储，当天数据动态更新
- 当天访问量基于PageView模型字段更新
- 当天注册量使用user/manager下的get_enrollment()函数获取

#### 接口调用规范
- 使用`GET`方法，请求api:**http://<<BASE_URL>>/api/analysis/view-stats**
- 需要管理员权限，必须在header中包含有效的token
- 无需传入任何参数

#### 返回数据格式
```json
{
    "message": "获取成功",
    "data": [
        {
            "date": "05-14",
            "view_count": 100,
            "enrollment_count": 10,
            "is_today": true
        },
        {
            "date": "05-13",
            "view_count": 80,
            "enrollment_count": 5,
            "is_today": false
        },
        // ... 更多数据
    ]
}
```
