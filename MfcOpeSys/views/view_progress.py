# -*-coding:utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import json
from datetime import datetime,timedelta
import time,os

from MfcOpeSys.models import models_common, models_assy,models_progress
from django.http import HttpResponse
from MfcOpeSys.models import models_ngreport
from MfcOpeSys.models.models_logger import Logger
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def get_config(key):
    # 加载配置文件
    file_path = os.getcwd() + '/config/config.json'
    fp = open(file_path)
    json_data = json.load(fp)
    return json_data[key]

def go_progress(request):
    Logger.write_log("进入Progress页面")
    model = request.GET.get('model')
    return render(request, 'progress.html', {"model":model})

def getAutoUpdatings(request):
    Logger.write_log("获取自动更新数据")
    result = get_config('auto_updating')
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def getProcessDetail(request):
    Logger.write_log("获取Process数据")
    model_name = request.GET.get('model_name')
    search_date = request.GET.get('searchDate')
    lineNum = request.GET.get('lineNum')
    if not lineNum:
        lineNum="2nd"
    result = models_progress.get_progressDetail(model_name,search_date,lineNum)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)