# -*-coding:utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
import json
from datetime import datetime,timedelta
import time

from MfcOpeSys.models import models_common, models_assy
from django.http import HttpResponse
from MfcOpeSys.models import models_ngreport
from MfcOpeSys.models.models_logger import Logger
from django.views.decorators.csrf import csrf_exempt
import xlrd
from django.http import HttpResponse

def initAssyData(request):
    Logger.write_log("初始化Assy数据")
    model = request.GET.get('model_name')
    result = []
    result = models_assy.initAssyData(model)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def update_assy(request):
    Logger.write_log("更新Assy数据")
    model = request.GET.get('model_name')
    process_id = request.GET.get('process_id')
    assy_text = request.GET.get('assy_text')
    result = []
    result = models_assy.update_assy(model,process_id,assy_text)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)
