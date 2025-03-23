# KQDJ_Server 项目开发注意事项

## utils文件
- utils分为全局和局部的，只有全部用到的会分在全局里面(根目录下的)
- 修改后请注意在`__init__.py`中进行添加

## 全局开发注意事项
- 所有的上传时间统一命名为upload_time
- 获取表单数据可以选择：`form.get_type_display()`
