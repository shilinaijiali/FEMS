# -*- coding: utf-8 -*-
import datetime
import json
import logging
from typing import Any
from django.utils.translation import gettext
from CMSapp.common.tools import tool

mylog = logging.getLogger('CMS')


class DateTimeEncoder(json.JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def AddMsg(msg, type):
    if type == 'success':
        msg = gettext('Success') + ':' + msg
    elif type == 'danger':  # 前端bootstrap5中alter-danger为红色，alter-warning为橙色，所以danger更能体现出是操作错误
        msg = gettext('Warning') + ':' + msg
    else:
        msg = gettext('Error') + ':' + msg
    return msg


class ResMsg:
    type: str   # 传递给alter的类型，以决定是显示何种类型的alter
    msg: str    # 传递给alter的消息
    data: Any   # 传递给前端显示的json数据

    def info(self, msg: str, data: Any = None):
        self.type = 'success'
        self.msg = AddMsg(msg, self.type)
        self.data = data

        mylog.info(json.dumps(self.__dict__, ensure_ascii=False, cls=DateTimeEncoder))

        return self.__dict__

    def warn(self, msg: str, data: Any = None):
        self.type = 'danger'
        self.msg = AddMsg(msg, self.type)
        self.data = data

        mylog.warn(json.dumps(self.__dict__, ensure_ascii=False, cls=DateTimeEncoder))

        return self.__dict__

    def error(self, msg: Exception, data: Any = None):
        self.type = 'warning'
        self.msg = AddMsg(str(msg), self.type)
        self.data = data

        mylog.error(json.dumps(self.__dict__, ensure_ascii=False, cls=DateTimeEncoder))

        return self.__dict__


class ViewRes:
    method: str
    username: str
    lang: str
    path: str
    data: Any

    def RequestInfo(self, request):
        self.method = request.method
        self.username = request.user.username
        self.lang = tool.get_session_lang(request)
        self.path = request.path
        if request.method == 'GET':
            self.data = request.GET
        else:
            self.data = request.POST

        mylog.info(json.dumps(self.__dict__, ensure_ascii=False, cls=DateTimeEncoder))

        return self.__dict__
