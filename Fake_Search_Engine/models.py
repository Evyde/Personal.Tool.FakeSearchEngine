from urllib import parse
import requests
import re
import Exceptions
import getter
import time
import configparser
import threading
from functools import cmp_to_key
import os

__header = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Authorization': ""
}

__oriInput = "搜索框输入的字符串"
__questionList = []
__answerList = []
__token = "test123"

# searched = 1
# tasks = 0


#早上干脆重写了一遍，思路极其简单，我这儿反正能跑





def textProcessing(input):
    input.replace(' ', '')
    questionList = re.split(
        '1.|2.|3.|4.|5.|6.|7.|8.|9.|10.|11.|12.|13.|14.|15.|16.|17.|18.|19.|20.|21.|22.|23.|24.|25.|26.|27.|28.|29.|30.|31.|32.|33.|34.|35.|36.|37.|38.|39.|40.|41.|42.|43.|44.|45.|46.|47.|48.|49.|50.',
        input)
    return questionList
# 处理题干字符串，生成一个不含题号、空格，只有一堆题干的列表

def findingAndCombining(questionList):
    urList = []
    i = 0
    for i in range(0,20):
        currentQuestion = questionList[i]
        currentAnswer = requests.get(
            "https://api.gochati.cn/jsapi.php?token=test123&q=" + parse.quote(currentQuestion).text)
        urList.append(currentAnswer)
        i = i + 1
    return urList
# 得到形如   [{题目字典},{题目字典},......,{题目字典}]   的列表

def getUrAnswer(__oriInput):
    answerList = findingAndCombining(textProcessing(__oriInput))
    return answerList
# 直接用这个就行


def save(dicto):
    __questionList.append(dicto)


def detectQuestionID(question):
    listOrig = re.findall("(\d+).", question)  # 挑出数字
    numMidd = listOrig[0]
    # 合并list，以防ocr空格分开数字
    num = int(numMidd)
    return num


# 提取题号


def preProcessQuestion(question):
    m1 = question.split('A', 2)  # 以A为分割
    question = m1[0]  # 取前一半
    splitChar = "分)"
    if "分）" in question:
        splitChar = "分）"
    n1 = list(question.split(splitChar, 2))
    n1.pop(0)
    return n1[0]


# 预提取题干（带题号）

def removeQuestionNum(question):
    if re.findall("(\d+).", question):
        question = question.replace(".", "", 1)
        question = question.replace(str(re.findall("(\d+)", question)[0]), "", 1)
    else:
        question = question.replace(str(re.findall("(\d+)", question)[0]), "", 1)
    return question


# 删除题干的题号


def detectQuestion(question):
    n1 = preProcessQuestion(question)
    question = ""
    for i in n1:
        question += i
    question = removeQuestionNum(question)
    return question


def getFromBaidu(question):
    return str(f"没有，前往<a href=\"https://zhidao.baidu.com/search?word={question}\">百度知道</a>或者<a href=\"https://www.baidu.com/s?q={question}\">百度</a>")


def findAnswer(a, times, source=None):
    if source is None:
        source = a.copy()
    if times > 4:
        raise Exceptions.NoAnswerFoundAtAll
    g = getter.getter()
    str = ""
    j = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'] # 此处由API总数决定
    h = 0
    try:
        tmp = g.get({'q': a['question'], 'token': __token})
    except Exceptions.NoAnswerFound:
        if times == 0:
            return findAnswer(a, times + 1, source)
        try:
            tmpA = a.copy()
            tmpA['question'] = textProcess(tmpA['question'], times + 1)
            r = findAnswer(tmpA, times + 1, source)
        except Exceptions.NoAnswerFoundAtAll:
            return {'id': a['id'], 'question': a['question'], 'answer': getFromBaidu(source['question'])}
        else:
            r['question'] = a['question']
            return r
    else:
        for i in tmp:
            if i['answer'] == "":
                continue
            str += j[h] + ". : " + i['answer']
            str += "\1"
            h += 1
        return {'section': a['section'], 'id': a['id'], 'question': a['question'], 'answer': str,
                'relativeID': a['relativeID']}


def threadSearch(cf, st, en):
    loop = 1
    global searched, tasks
    for i in cf.sections():
        if loop < st:
            loop += 1
            continue
        if loop >= en:
            break
        #print("查找中...第%s(%d/%d)题 : " % (i, searched, tasks) + cf.get(i, "question"))
        searched += 1
        dic = {'section': i, 'id': cf.get(i, "id"), 'question': cf.get(i, "question"), "type": cf.get(i, "type"),
               'relativeID': cf.get(i, "relativeID")}
        a = findAnswer(dic, 0, dic)
        if a['answer'] != "":
            cf.remove_section(i)
            save(a)
        loop += 1


def textProcess(text, times):
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


def sortByEleID(a, b):
    a1, a2 = a['section'].split("-", 2)
    b1, b2 = b['section'].split("-", 2)
    a1 = int(a1)
    b1 = int(b1)
    a2 = int(a2)
    b2 = int(b2)
    if a1 > b1:
        return 1
    elif a1 < b1:
        return -1
    if a2 > b2:
        return 1
    else:
        return -1


def startSearch(threadNum=1, file="questions.ini", write=True):
    # 初始化题目文件
    global __questionList, tasks
    cfg = configparser.ConfigParser()
    cfg.read(file, encoding="gbk")
    tasks = int(cfg.sections().__len__())

    t = []
    for i in range(0, threadNum):
        maxRange = tasks * (i + 1) / threadNum + 1
        minRange = tasks * i / threadNum + 1
        t.append(threading.Thread(target=threadSearch, args=(cfg, minRange, maxRange)))
        t[i].start()

    for i in t:
        i.join()

    if write:
        with open(file, "w+") as f:
            cfg.write(f)
            f.close()
    del cfg
    __questionList.sort(key=cmp_to_key(sortByEleID))
    cfg = configparser.ConfigParser()
    for i in __questionList:
        cfg.add_section(i['section'])
        cfg.set(i['section'], "ID", i['id'])
        cfg.set(i['section'], "relativeID", i['relativeID'])
        cfg.set(i['section'], "question", i['question'])
        cfg.set(i['section'], "answer", i['answer'])
    foundAnswers = int(cfg.sections().__len__())
    with open("answers.ini", "w", encoding="utf-8") as f:
        cfg.write(f)
        f.close()
    del cfg
    return foundAnswers


def oneToN(str):
    return str.replace("\1", "\n", 999)


def nToOne(str):
    return str.replace("\n", "\1", 999)


def yourMode(modeChoice):
    manualMode = False
    if modeChoice == "y":
        manualMode = True
    if modeChoice == "n":
        manualMode = False
    return manualMode


lastString = ""

# 初始化AipOcr

tmp = ""
baiduAPI = False

cfg = configparser.ConfigParser()

initFlag = True
numOfQuestions = 0
nowNum = 0
tp = 0
lastType = -1
threadNum = 1
uniCopy = False

manualMode = False
searchingMode = str(input("搜题模式？y/N"))

if yourMode(searchingMode):
    startSearch(threadNum, "questions1.ini", False)
    quit()

modeChoice = str(input("是否选择紧急模式？y/N"))
startTime = time.time()
if yourMode(modeChoice):
    while 51 >= nowNum:
        if baiduAPI:
            try:
                tmp = getDataOCR(0)
            except Exceptions.ClipNotIMG:
                tmp = getDataPaste("")
            except:
                continue
        else:
            tmp = getDataPaste(tmp)
            if tmp == "":
                continue
        if lastString == textProcess(tmp, 1):
            endTime = time.time()
            if endTime - startTime >= 3000:
                quit()
            continue
        else:
            startTime = time.time()
            lastString = textProcess(tmp, 1)
            nowNum += 1
            # print(findAnswer(
            #      {'section': "0-0", 'relativeID': 0, 'id': 0, 'question': textProcess(tmp, 1),
            #      'type': 0}, 0)['answer'])

#print("开始初始化...")
# initFlag = False
# numOfQuestions = 2
while initFlag:
    try:
        numOfQuestions = detectQuestionNum(getDataOCR(0))
    except:
        continue
    else:
        initFlag = False
#print("初始化完成！")
#print("开始获取题目内容...")
while (nowNum - numOfQuestions) != 0:
    if uniCopy:
        time.sleep(1)
    try:
        tmp = getDataOCR(0)
        uniCopy = False
    except Exceptions.ClipNotIMG:
        tmp = getDataPaste("")
        if tmp == "":
            continue
        uniCopy = True
    except:
        continue
    if not uniCopy:
        if lastString == detectQuestion(textProcess(tmp, 1)):
            continue
    else:
        if lastString == textProcess(tmp, 1):
            continue
        if int(detectQuestionType(textProcess(tmp, 1))) != 3:
            if lastType != int(detectQuestionType(textProcess(tmp, 1))):
                lastType = int(detectQuestionType(textProcess(tmp, 1)))
                tmp = preProcessQuestion(textProcess(tmp, 1))
                pyperclip.copy(tmp)
                continue
    q = textProcess(tmp, 1)
    nowNum += 1
    try:
        if not uniCopy:
            lastString = detectQuestion(q)
            lastType = int(detectQuestionType(q))
            rID = detectQuestionID(preProcessQuestion(q))
            q = detectQuestion(q)
            #print("第%s(%d/%d)题 : " % (str(lastType + 1) + "-" + str(rID), nowNum, numOfQuestions) + q)
        else:
            lastString = q
            rID = detectQuestionID(q)
            q = removeQuestionNum(q)
            #print("第%s(%d/%d)题 : " % (str(lastType + 1) + "-" + str(rID), nowNum, numOfQuestions) + q)
        section = str(lastType + 1) + "-" + str(rID)
        cfg.add_section(section)
        cfg.set(section, "ID", str(nowNum))
        cfg.set(section, "relativeID", str(rID))
        cfg.set(section, "question", q)
        cfg.set(section, "type", str(lastType))
    except:
        nowNum -= 1
        continue

with open("questions.ini", "w", encoding="utf-8") as f:
    cfg.write(f)
    f.close()
    del cfg
os.popen("cp /y questions.ini questions1.ini")  # Linux把copy改成cp
#print("开始查找(%d线程)..." % threadNum)
fdA = startSearch(threadNum)
#print("正在推送...")
j = 1
for i in __questionList:
    #print("第%s题(%d/%d/%d) : %s" % (i['section'], j, fdA, numOfQuestions, i['answer']))
    j = j + 1
    #push(i)
