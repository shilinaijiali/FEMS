"""CMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import to include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

from CMSapp.views import views_home

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/', admin.site.urls),
    path('', views_home.home, name='home'),
    path('home/', views_home.home, name='home'),
    path('login/', views_home.login, name='login'),
    path('logout/', views_home.logout, name='logout'),
    path('lang/zh-hans/', views_home.set_lang_CN, name='set_lang_CN'),
    path('lang/en/', views_home.set_lang_EN, name='set_lang_EN'),
    path('lang/zh-hant/', views_home.set_lang_TZ, name='set_lang_TZ'),
    path('CMS/', include('CMSapp.urls')),
]
