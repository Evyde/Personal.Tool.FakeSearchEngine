from django.shortcuts import render

def index(request):
    return render(request, 'Google.html')

def search(request):
    randomName = "asdasdasd" + request.GET['q']
    nie = [{
        "link": "asdoasdhiajksd",
        "linkEnd": "aqqq21",
        "title": "fuck",
        "mixup": "混淆专用",
        "answer": "第一题选A",
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
    return render(request, 's.html', {"nice": nie, "randomName": randomName, "items": "6000", "randomSec": "50"})