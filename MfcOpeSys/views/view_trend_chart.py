# -*-coding:utf-8 -*-
'''传感器 views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json
import os
from django.http import HttpResponse
from MfcOpeSys.models.models_logger import Logger
# @auth_required
from MfcOpeSys.models import models_common, models_trend_chart

def get_config(key):
    # 加载配置文件
    file_path = os.getcwd() + '/config/config.json'
    fp = open(file_path)
    json_data = json.load(fp)
    return json_data[key]

def go_trend_chart(request):
    Logger.write_log("初始化trend chart数据")
    model = request.GET.get('model')
    return render(request, 'trend_chart.html', {"model": model})

def get_inspect(request):
    Logger.write_log("获取Inspect数据")
    model_name = request.GET.get('model_name')
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')
    process_cd = request.GET.get('process')
    result = models_trend_chart.get_inspect(model_name, start_date, end_date, process_cd)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr.encode("utf-8"))

def search_trend(request):
    Logger.write_log("查询trend数据")
    model_name = request.POST.get('model')
    start_date = request.POST.get('from')
    end_date = request.POST.get('to')
    process_cd = request.POST.get('process')
    inspect_cd = request.POST.get('inspect')
    type = request.POST.get('datatype')
    time_part = request.POST.getlist('timepart')
    result = models_trend_chart.get_trend(model_name, start_date, end_date, process_cd, inspect_cd, time_part, type)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)




