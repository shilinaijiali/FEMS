from django.shortcuts import redirect
from django.urls import reverse


# 获取用户名，显示在base模板中
def get_username(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
    return {'username': username}


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查当前请求是否是登录页面
        if request.path == reverse('login'):
            return self.get_response(request)
        # 检查用户是否已经登录，如果没有则重定向到登录页面
        if not request.user.is_authenticated:
            return redirect('login')
        # 如果用户已经登录，则正常处理请求
        response = self.get_response(request)
        return response
