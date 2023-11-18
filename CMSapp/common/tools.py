# -*- coding: utf-8 -*-
from django.utils import translation

from CMS import settings
from CMSapp.views.views_home import default_lang
from CMSapp.common import msg as Msg


class tool:
    @staticmethod
    def get_session_lang(request):
        if request.session.get(settings.LANGUAGE_SESSION_KEY):
            return request.session[settings.LANGUAGE_SESSION_KEY]
        else:
            return default_lang


class Verify:
    def __init__(self, user, lang):
        self.user = user
        self.lang = lang
        self.info = ''

    def is_digits(self, x):
        if not x.isdigit():
            self.info = Msg.Language(self.lang).main().Verify.V01.format(x, self.user)
            return True
        return False
