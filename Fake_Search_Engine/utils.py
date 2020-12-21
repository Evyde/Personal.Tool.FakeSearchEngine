import json
from urllib import parse

import requests

from . import Exceptions


class getter:
    __list = ["API4"]
    __result = []

    def get(self, arg):
        self.__result = []
        j = 0
        t = []
        noAnswerError = 0
        for i in self.__list:
            try:
                self.__result.append(eval("self." + i)(arg))
            except:
                noAnswerError += 1
                continue
            if self.__result[j]['status'] is False:
                noAnswerError += 1
            j += 1
        if noAnswerError == j:
            raise Exceptions.NoAnswerFound
        return self.__result

    def __oneToSharp(self, str):
        return str.replace("\1", "#", 999)

    def API4(self, a):
        url = "https://api.gochati.cn/jsapi.php?"
        tmp = json.loads(requests.get(url + "q=" + parse.quote(a['q']) + "&token=" + a['token']).text)
        r = {'answer': "", 'status': False, "tm": ""}
        if tmp['tm'] != "未查到该题，已收录到后台，过几天再来试试吧~":
            r['status'] = True
            r['answer'] = self.__oneToSharp(tmp['da'])
            r['tm'] = self.__oneToSharp(tmp['tm'])
        return r
