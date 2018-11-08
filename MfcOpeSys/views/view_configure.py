# -*-coding:utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import json
from datetime import datetime,timedelta
import time

from MfcOpeSys.models import models_common, models_assy, models_configure
from django.http import HttpResponse
from MfcOpeSys.models import models_ngreport
from MfcOpeSys.models.models_logger import Logger
from django.views.decorators.csrf import csrf_exempt
import xlrd
from django.http import HttpResponse

def initConfigureData(request):
    Logger.write_log("初始化Configure数据")
    model = request.GET.get('model_name')
    result = []
    result = models_configure.initConfigureData(model)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_workTime(request):
    Logger.write_log("初始化WorkTime数据")
    model = request.GET.get('model_name')
    result = []
    result = models_configure.get_time_tbl_cd(model)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_assytext(request):
    Logger.write_log("初始化AssyText数据")
    model = request.GET.get('model_name')
    line_cd = request.GET.get('line_cd')
    result = []
    result = models_configure.get_assy_text(model,line_cd)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

@csrf_exempt
def update_worktime(request):
    Logger.write_log("更新work_time数据")
    model = request.GET.get('model_name')
    content = request.body.decode("utf-8")
    received_json_data = json.loads(content)
    result = models_configure.update_worktime(model, received_json_data)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)