from urllib import parse
import requests
import re
from . import Exceptions
from . import utils
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
    g = utils.getter()
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
    a = __findAnswer(qDicts, 0, qDicts)
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
    # for i in range(0, threadNum):
    #     maxRange = int(tasks * (i + 1) / threadNum + 1)
    #     minRange = int(tasks * i / threadNum + 1)
    #     print(f"{minRange}-{maxRange}")
    #     t.append(threading.Thread(target=__threadSearch, args=(questionDicts[minRange: maxRange])))
    #     t[i].start()
    # for i in t:
    #     i.join()
    for i in questionDicts:
        __threadSearch(i)
    __answerDicts.sort(key=cmp_to_key(__sortByEleID))


def __detectQuestionNum(questions):
    # 最后一题题号 - 第一题题号
    tmpQList = re.split(r'(\d+\.)', questions)
    for i in tmpQList:
        if i == "":
            tmpQList.remove(i)
    print(int(tmpQList[-2].replace('.', "")) - int(tmpQList[0].replace('.', "")))
    return int(tmpQList[-2].replace('.', "")) - int(tmpQList[0].replace('.', "")) + 1


def __getQuestionDict(q):
    i = 0
    tmpList = re.split(r'(\d+\.)', q)
    for i in tmpList:
        if i == "":
            tmpList.remove(i)
    i = 0
    questionDicts = []
    for qs in tmpList:
        if i % 2 == 0:
            questionDicts.append({"id": qs, "question": ""})
        else:
            questionDicts[int((i - 1) / 2)]['question'] = qs
        i += 1
    return questionDicts


def searchFromInputBox(questions):
    initFlag = True
    nowNum = 0
    threadNum = 2
    numOfQuestions = 0
    while initFlag:
        try:
            numOfQuestions = __detectQuestionNum(questions)
        except:
            print("TWF???")
            return {"questionNum": numOfQuestions, "answerDicts": [{"question": "Error!", "answer": "提取题号错误！"}]}
        else:
            initFlag = False

    q = __textProcess(questions, 1)
    nowNum += 1
    __startSearch(numOfQuestions, threadNum, __getQuestionDict(q))
    print(__answerDicts)
    return {"questionNum": numOfQuestions, "answerDicts": __answerDicts}
