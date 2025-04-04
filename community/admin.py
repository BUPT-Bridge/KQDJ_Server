from django.contrib import admin
from .models import Banners,Notice,Cover,PageView,PhoneNumber
# Register your models here.
admin.site.register([Banners,Notice,Cover,PageView,PhoneNumber])