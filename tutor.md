# 各个自定义接口的实现和示例

## 调试方法 
使用drf自带的接口文档进行调试
- 开起服务之后，输入http://127.0.0.1:8000/doc/swagger
- 可以在下面进行测试


## /utils/response.py

### api_response
一般只需要调用 `api_response(data=data)` 返回状态码默认200，message也是默认的，可以改`api_response(data=data,message=message, code=201)`
### error_response
用法同上，data是默认400
### 提醒
我们此时http协议的状态码都是200，这个code是我们打包在response中的一个key值
