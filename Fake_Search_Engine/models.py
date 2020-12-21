import random
import re
import string
import threading
from functools import cmp_to_key
from . import Exceptions
from . import utils

__header = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Authorization': ""
}
__answerDicts = []
__token = "test123"


def __getMixup(length):
    mix = ""
    mix = mix.join(random.sample("新华网北京12月17日电 中共中央政治局12月11日下午就切实做好国家安全工作举行第二十六次集体学习。习近平总书记主持学习并发表重要讲话。近日,"
                                 "国家安全部党委书记、部长陈文清主持召开部党委会议，专题传达学习习近平总书记重要讲话精神，研究贯彻落实工作。 "
                                 "国家安全部党委学习认为，在“两个一百年”的历史交汇点，在党的十九届五中全会首次把统筹发展和安全纳入我国经济社会发展的指导"
                                 "思想并专章作出战略部署之后不久党中央对国家安全工作进行专题研究部署凸显了国家安全在党和国家工作大局中的重要地位"
                                 "意义重大而深远。习近平总书记的重要讲话，着眼中华民族伟大复兴的历史进程，对总体国家安全观作出全面系统论述，对中国特色国"
                                 "家安全道路作出集中深刻阐释，是指导新时代国家安全工作的纲领性文献。 国家安全部党委学习认为，总体国家安全观是我们党历"
                                 "史上第一个被确立为国家安全工作指导思想的重大战略思想，是习近平新时代中国特色社会主义思想的“国家安全篇”，具有重大"
                                 "理论意义、实践意义、时代意义。习近平总书记将总体国家安全观的内涵要求，系统概括为“十个坚持”，是这次集体学习的最显"
                                 "著特点。“十个坚持”既是重大战略思想，又是重大战略部署，为做好新时代国家安全工作提供了行动指南和根本遵循。 国家安全"
                                 "部党委指出，国家安全机关要把学习贯彻习近平总书记重要讲话精神作为首要政治任务，把“十个坚持”贯彻落实到工作全过程、各"
                                 "方面。特别是必须坚持党对国家安全工作的绝对领导，坚持党中央对国家安全工作的集中统一领导；必须把防范化解重大风险摆"
                                 "在突出位置，为实现中华民族伟大复兴提供坚强安全保障；必须统筹发展和安全、统筹维护和塑造国家安全、统筹传统安全和非传"
                                 "统安全，全面提高国家安全工作的能力和水平；必须坚持系统思维，构建大安全格局，以人民安全为宗旨，以政治安全为根本，"
                                 "以经济安全为基础，统筹推进各领域安全；必须坚持以改革创新为动力，推进国家安全体系和能力现代化；必须加强干部队伍建"
                                 "设，打造坚不可摧的国家安全干部队伍。 国家安全部党委强调，以习近平同志为核心的党中央的坚强领导，是做好新时代国家安"
                                 "全工作的根本依靠。展望建设社会主义现代化国家新征程，有以习近平同志为核心的党中央的掌舵领航，有习近平新时代中国特色"
                                 "社会主义思想的科学指导，我们就有了信心，就有了底气，就有了主心骨。国家安全机关要坚决把思想和行动统一到习近平总书记"
                                 "重要讲话精神上来，以总体国家安全观为指导，更加有力地履行护航中华民族伟大复兴的历史使命。", length))
    return mix


def __getRandomLink():
    rLinkPre = "".join(random.sample('abcdefghijklmnopqrstuvwxyz', random.randint(1, 6)))
    link = random.choice(["www.", "s.", "tm.", "na.", "search.", rLinkPre + "."])
    linkMid = "".join(random.sample('abcdefghijklmnopqrstuvwxyz', random.randint(5, 10)))
    link = link + linkMid + random.choice([".com", ".cn", ".net", ".top", ".me", ".org", ".edu.cn", ".xyz", ".life"])
    return link


def __getRandomLinkEnd():
    linkEnd = ""
    return linkEnd.join(random.sample(string.ascii_letters + string.digits, 8))


def __save(dicto):
    # list是线程安全的，不必设计锁
    __answerDicts.append(dicto)


def __getBaiduLink(q):
    return f"https://www.baidu.com/s?q={q}"


def __getBaiduZhidaoLink(q):
    return f"https://zhidao.baidu.com/search?word={q}"


def __getFromBaidu(question):
    return str(f"没有，点击前往百度知道")


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
            a['question'] = a['question'] + "_Zhidao_百度知道"
            return {'id': a['id'], 'title': a['question'], 'answer': __getFromBaidu(source['question']),
                    'link': __getBaiduZhidaoLink(source['question']), 'linkname': "zhidao.baidu.com",
                    'linkEnd': __getRandomLinkEnd()}
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
        return {'id': a['id'], 'title': a['question'], 'answer': tmpStr,
                'link': __getBaiduZhidaoLink(source['question']), 'linkname': __getRandomLink(),
                'linkEnd': __getRandomLinkEnd()}


def __threadSearch(qDicts):
    print(qDicts)
    for i in qDicts:
        print(i)
        a = __findAnswer(i, 0, i)
        a['mixup'] = __getMixup(random.randint(50, 70))
        a['randomName'] = __getMixup(random.randint(10, 20))
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
    a1 = int(str(a['id']).split('.')[0])
    b1 = int(str(b['id']).split('.')[0])
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
        maxRange = int(tasks * (i + 1) / threadNum + 1)
        minRange = int(tasks * i / threadNum + 1)
        tmpList = []
        tmpList.append(questionDicts[minRange - 1: maxRange - 1])
        t.append(threading.Thread(target=__threadSearch, args=(tmpList)))
        t[i].start()
    for i in t:
        i.join()
    __answerDicts.sort(key=cmp_to_key(__sortByEleID))


def __detectQuestionNum(questions):
    # 最后一题题号 - 第一题题号
    tmpQList = re.split(r'(\d+\.)', questions)
    for i in tmpQList:
        if i == "":
            tmpQList.remove(i)
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
    global __answerDicts
    initFlag = True
    threadNum = 2
    numOfQuestions = 0
    __answerDicts = []
    while initFlag:
        try:
            numOfQuestions = __detectQuestionNum(questions)
        except:
            qlist = {'id': 1, 'question': __textProcess(questions, 1)}
            print(__findAnswer(qlist, 0, qlist))
            return {"questionNum": numOfQuestions + 1, "answerDicts": [__findAnswer(qlist, 0, qlist)]}
        else:
            initFlag = False

    q = __textProcess(questions, 1)
    __startSearch(numOfQuestions, threadNum, __getQuestionDict(q))
    return {"questionNum": numOfQuestions, "answerDicts": __answerDicts}
