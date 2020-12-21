import time

from django.shortcuts import render

from . import models


def index(request):
    return render(request, 'Google.html')


def search(request):
    startT = time.time()
    randomName = request.GET['q']
    rtnDict = models.searchFromInputBox(request.GET['q'])
    endT = time.time()
    return render(request, 's.html',
                  {"nice": rtnDict['answerDicts'], "randomName": randomName, "items": rtnDict['questionNum'],
                   "randomSec": round(endT - startT, 4)})
