from Language.zh_hant import msg as zh_hant
from Language.zh_hans import msg as zh_hans
from Language.en import msg as en

import logging

mylog = logging.getLogger('CMS')


class Message:
    def __init__(self, state, info):
        self.state = state
        self.info = info

    def msg(self):
        return self.state

    def state(self):
        return self.info


class Language:
    def __init__(self, lang):
        self.lang = lang
        self.Pack = en

    def main(self):
        if self.lang == 'zh-hant':
            self.Pack = zh_hant
        elif self.lang == 'zh-hans':
            self.Pack = zh_hans
        return self.Pack
