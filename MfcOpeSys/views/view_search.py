# -*-coding:utf-8 -*-
'''传感器 views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json
import os
import datetime
from django.http import HttpResponse
from MfcOpeSys.models.models_logger import Logger

# @auth_required
from MfcOpeSys.models import models_common
from MfcOpeSys.models import models_trend

def get_config(key):
    # 加载配置文件
    file_path = os.getcwd() + '/config/config.json'
    fp = open(file_path)
    json_data = json.load(fp)
    return json_data[key]

def search_history(request):
    Logger.write_log("初始化history数据")
    model = request.GET.get('model_name')
    object = request.GET.get('object')
    content = request.GET.get('content')
    dataType = request.GET.get('dataType')
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')
    result = models_trend.get_trend(model,start_date,end_date,object,content,dataType)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_history_targrt(request):
    Logger.write_log("获取history target数据")
    result = get_config('database')
    model = request.GET.get('model_name')
    # print(result)
    for item in result:
        if(item['MODEL'] == model):
            target = item['TARGET']
            break
    jsonstr = json.dumps(target)
    return HttpResponse(jsonstr)

def get_history_assy(request):
    Logger.write_log("获取history assy数据")
    result = get_config('database')
    model = request.GET.get('model_name')
    # print(result)
    for item in result:
        if(item['MODEL'] == model):
            target = item['ASSY']
            break
    jsonstr = json.dumps(target)
    return HttpResponse(jsonstr)

def get_toprank(request):
    Logger.write_log("获取top rank数据")
    result = get_config('top_rank')
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def search_defect(request):
    Logger.write_log("获取defect数据")
    model_name = request.GET.get('model_name')
    startTime = request.GET.get('from')
    endTime = request.GET.get('to')
    line = request.GET.get('line')
    assy = request.GET.get('assy')
    time_part = request.GET.get('time_part')
    top_rank = request.GET.get('top_rank')
    result = models_common.search_defect(model_name,startTime,endTime,line,assy,time_part,top_rank)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_Trend_Data(request):
    Logger.write_log("获取defect数据")
    result = get_config('database')
    model = request.GET.get('model_name')
    # print(result)
    for item in result:
        if (item['MODEL'] == model):
            target = item['RGB']['Trend_Boundary_Value']
            break
    jsonstr = json.dumps(target)
    return HttpResponse(jsonstr)

def getObjs(request):
    Logger.write_log("获取objects数据")
    result = get_config('object')
    model = request.GET.get('model_name')
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def getDataType(request):
    Logger.write_log("获取data type数据")
    result = get_config('data_type')
    model = request.GET.get('model_name')
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)
