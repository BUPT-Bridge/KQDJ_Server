from django.contrib import admin

from .models import StatusTypeNum, ViewNum
# Register your models here.
admin.site.register([StatusTypeNum, ViewNum])
