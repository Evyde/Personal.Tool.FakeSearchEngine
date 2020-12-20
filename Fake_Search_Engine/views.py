from django.shortcuts import render
import models

def index(request):
    return render(request, 'Google.html')

def search(request):
    randomName = "以下是您搜索的答案，请享用！" + request.GET['q']
    rtnDict = models.searchFromInputBox(request.GET['q'])
    nie = [{
        "link": "asdoasdhiajksd",
        "linkEnd": "aqqq21",
        "title": rtnDict['answerDicts'][0]['question'],
        "mixup": "混淆专用",
        "answer": rtnDict['answerDicts'][0]['answer'],
        "randomName": randomName

    },
        {
            "link": "asdoasdhiajksd",
            "linkEnd": "aqqq21",
            "title": "fuck2",
            "mixup": "混淆专用2",
            "answer": "第2题选A",
            "randomName": randomName

        }
    ]
    return render(request, 's.html', {"nice": nie, "randomName": randomName, "items": rtnDict['questionNum'], "randomSec": "50"})