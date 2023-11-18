import logging
from urllib.parse import unquote

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import translation, timezone
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login as log_in, logout as log_out

from CMS import settings

mylog = logging.getLogger('CMS')
default_lang = settings.DEFAULT_LANG


# @login_required()
@csrf_exempt
def home(request):
    try:
        lang = request.session.get(settings.LANGUAGE_SESSION_KEY)
        if not lang:
            lang = default_lang
        request.session[settings.LANGUAGE_SESSION_KEY] = lang
        activate(lang)

        # 没有登录拒绝访问
        if not request.session.get('is_login', None):
            return redirect('/login/')

        return render(request, 'home.html')
    except Exception as e:
        mylog.error(str(e))
        return render(request, 'return_info.html', {'info': str(e), 'TIMESTAMP': timezone.now()})


@csrf_exempt
def login(request):
    try:
        # if request.session.get('is_login', None):
        #     return render(request, 'home.html')
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)  # 使用authenticate对用户进行认证
            if user:
                if user.is_active:
                    log_in(request, user)  # 使用login()进行登录，并保存session
                    lang = request.session.get(settings.LANGUAGE_SESSION_KEY)
                    if not lang:
                        lang = default_lang
                    request.session['username'] = user.username
                    request.session['password'] = user.password
                    request.session[settings.LANGUAGE_SESSION_KEY] = lang
                    request.session['is_login'] = True
                    activate(lang)
                    return redirect('/')
            return render(request, 'login.html')
        return render(request, 'login.html')
    except Exception as e:
        mylog.error(str(e))
        return render(request, 'return_info.html', {'info': str(e), 'TIMESTAMP': timezone.now()})


def logout(request):
    try:
        log_out(request)
        return redirect('/login/')
    except Exception as e:
        mylog.error(str(e))
        return render(request, 'return_info.html', {'info': str(e), 'TIMESTAMP': timezone.now()})


def set_lang_TZ(request):
    try:
        return _set_lang(request, 'zh-hant')
    except Exception as e:
        mylog.error(str(e))
        return render(request, 'return_info.html', {'info': str(e), 'TIMESTAMP': timezone.now()})


def set_lang_CN(request):
    try:
        return _set_lang(request, 'zh-hans')
    except Exception as e:
        mylog.error(str(e))
        return render(request, 'return_info.html', {'info': str(e), 'TIMESTAMP': timezone.now()})


def set_lang_EN(request):
    try:
        return _set_lang(request, 'en')
    except Exception as e:
        mylog.error(str(e))
        return render(request, 'return_info.html', {'info': str(e), 'TIMESTAMP': timezone.now()})


def _set_lang(request, lang):
    request.session[settings.LANGUAGE_SESSION_KEY] = lang
    activate(lang)
    next = request.META.get('HTTP_REFERER')
    next = next and unquote(next)  # HTTP_REFERER may be encoded.
    return HttpResponseRedirect(next)
