# KQDJ_Server 项目开发注意事项

## 分文件注意事项

### proceed.py
- 在拉表时要进行分页处理，直接调用工具函数即可

## utils文件
- utils分为全局和局部的，只有全部用到的会分在全局里面(根目录下的)
- 修改后请注意在`__init__.py`中进行添加

## 全局开发注意事项
- 所有的上传时间统一命名为upload_time
- 获取表单数据可以选择：`form.get_type_display()`
- 采用APIView进行开发
- 使用restframe框架自带的接口文档进行测试接口

## setting相关配置 
- `数据库`暂时采用`sqlite`
- 文件保存位置先默认按照现行的来
