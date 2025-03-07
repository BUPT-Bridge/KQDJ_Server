"""
URL configuration for KQTX_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include


# 根路由分发配置

from django.contrib import admin
from django.urls import path, include
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.views import SpectacularRedocView, SpectacularAPIView

urlpatterns = [
    # YOUR PATTERNS
    path("admin/", admin.site.urls),
    
    path('api-auth/', include('rest_framework.urls')),
    path('user/', include('user.urls'), name='user'),
    path('analysis/', include('analysis.urls'), name='analysis'),
    path('community/', include('community.urls'), name='community'),
    path('proceed/', include('proceed.urls'), name='proceed'),
    
    path('doc/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'), # redoc的路由
]

# path('doc/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
# swagger-ui的路由