from urllib import parse
import requests
import re
from . import Exceptions
from . import utils.getter
import configparser
import threading
from functools import cmp_to_key
import os

__header = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Authorization': ""
}
__answerDicts = []
__token = "test123"


def __save(dicto):
    # list是线程安全的，不必设计锁
    __answerDicts.append(dicto)


def __getFromBaidu(question):
    return str(f"没有，前往<a href=\"https://zhidao.baidu.com/search?word={question}\">百度知道</a>或者<a href=\"https://www.baidu.com/s?q={question}\">百度</a>")


def __findAnswer(a, times, source=None):
    if source is None:
        source = a.copy()
    if times > 4:
        raise Exceptions.NoAnswerFoundAtAll
    g = getter()
    tmpStr = ""
    # 此处由API总数决定
    romans = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    h = 0
    try:
        tmpDict = g.get({'q': a['question'], 'token': __token})
    except Exceptions.NoAnswerFound:
        if times == 0:
            return __findAnswer(a, times + 1, source)
        try:
            tmpA = a.copy()
            tmpA['question'] = __textProcess(tmpA['question'], times + 1)
            r = __findAnswer(tmpA, times + 1, source)
        except Exceptions.NoAnswerFoundAtAll:
            a['question'] = a['question'] + "Zhidao_百度知道"
            return {'id': a['id'], 'question': a['question'], 'answer': __getFromBaidu(source['question'])}
        else:
            r['question'] = a['question']
            return r
    else:
        for i in tmpDict:
            if i['answer'] == "":
                continue
            tmpStr += romans[h] + ". : " + i['answer']
            tmpStr += "\1"
            h += 1
        return {'id': a['id'], 'question': a['question'], 'answer': tmpStr}


def __threadSearch(qDicts):
    global searched, tasks
    for i in qDicts:
        a = __findAnswer(i, 0, i)
        if a['answer'] != "":
            __save(a)


def __textProcess(text, times):
    targetText = text
    if times == 1:
        targetText = targetText.strip()
        targetText = targetText.replace(" ", '')
        targetText = targetText.replace("\n", '')
        targetText = targetText.replace("\t", '')
        targetText = targetText.replace("\r", '')
        targetText = targetText.replace("\xa0", '')
        targetText = targetText.replace("\x20", '')
        targetText = targetText.replace("\u3000", '')
        targetText = targetText.lstrip()
        targetText = targetText.rstrip()
    elif times == 2:
        targetText = targetText[0:int(int(targetText.__len__()) / 2)]
    elif times == 3:
        targetText = targetText.replace("（", ")")
        targetText = targetText.replace("）", ")")
        targetText = targetText.replace("，", ",")
        targetText = targetText.replace("。", " ")
        targetText = targetText.replace("(", "（")
        targetText = targetText.replace(")", "）")
        targetText = targetText.replace(",", "，")
    elif times == 4:
        pattern = r'，|,|。|;|：|:|;'
        str1 = re.split(pattern, targetText)
        targetText = str1[0]
    else:
        targetText = targetText[0:int(int(targetText.__len__()) / 2)]
    return targetText


def __sortByEleID(a, b):
    a1 = int(a['id'])
    b1 = int(b['id'])
    if a1 > b1:
        return 1
    elif a1 < b1:
        return -1
    else:
        return 0


def __startSearch(tasks, threadNum=1, questionDicts=None):
    if questionDicts is None:
        questionDicts = []
    global __answerDicts
    t = []
    for i in range(0, threadNum):
        maxRange = tasks * (i + 1) / threadNum + 1
        minRange = tasks * i / threadNum + 1
        t.append(threading.Thread(target=__threadSearch, args=(questionDicts[minRange: maxRange])))
        t[i].start()
    for i in t:
        i.join()
    __answerDicts.sort(key=cmp_to_key(__sortByEleID))


def __detectQuestionNum(questions):
    # 最后一题题号 - 第一题题号
    return int(str(questions).split('.')[-1]) - int(str(questions).split('.')[0])


def __getQuestionDict(q):
    i = 0
    tmpList = re.split(r"(\d+)\.", q)
    questionDicts = []
    for qs in tmpList:
        if i / 2 == 0:
            questionDicts.append({"id": qs, "question": ""})
        else:
            questionDicts[int((i - 1) / 2)]['question'] = qs
        i += 1
    return questionDicts


def searchFromInputBox(questions):
    initFlag = True
    nowNum = 0
    threadNum = 1
    while initFlag:
        try:
            numOfQuestions = __detectQuestionNum(questions)
        except:
            return [{"question": "Error!", "answer": "提取题号错误！"}]
        else:
            initFlag = False

    q = __textProcess(questions, 1)
    nowNum += 1
    __startSearch(numOfQuestions, threadNum, __getQuestionDict(q))
    return {"questionNum": numOfQuestions, "answerDicts": __answerDicts}
