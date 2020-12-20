import requests
from urllib import parse
import json
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
        r = {'answer': "", 'status': False}
        if tmp['msg'] != "可能过几天就有这道题了":
            r['status'] = True
            r['answer'] = self.__oneToSharp(tmp['da'])
        return r
