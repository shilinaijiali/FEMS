import django
import os
from django.test import TestCase

# 设置Django配置
os.environ['DJANGO_SETTINGS_MODULE'] = 'CMS.settings'

# 配置Django环境
django.setup()
import pytest
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from CMSapp.views.views_consumable import get_C_Scrap_list
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_get_C_Scrap_list_post():
    # 创建带有用户信息的请求对象
    request_factory = RequestFactory()
    request = request_factory.post('/get_C_Scrap_list/', {
        'ConsumableType': 'Screen',
    })
    request.user = User.objects.create_user(username='username4', password='password')
    request.user.save()

    # 定义一个 get_response 函数
    def get_response(request):
        return None  # 这里可以根据需要返回响应对象

    # 启用会话中间件
    session_middleware = SessionMiddleware(get_response=get_response)
    session_middleware.process_request(request)
    request.session.save()

    # 创建视图实例
    view = get_C_Scrap_list()

    # 调用视图的post方法进行测试
    response = view.post(request)

    # 断言期望的响应结果
    assert response.status_code == 200
    # response_data = response.json()
    # assert response_data['status'] == 'info'
    # assert 'sn_list' in response_data['data']

