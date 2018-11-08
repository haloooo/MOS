# -*-coding:utf-8 -*-
'''传感器 views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json
import datetime
from django.http import HttpResponse

from MfcOpeSys.models import models_chart
from MfcOpeSys.models.models_logger import Logger

def go_chart(request):
    Logger.write_log("进入chart页面")
    model = request.GET.get('model')
    return render(request, 'chart.html', {"model":model})

#def search_AdverseRate(request):
    #   Logger.write_log("查找Adverse Rate数据")
    #    model_name = request.GET.get("model_name")
    #    startTime = request.GET.get("from")
    #    endTime = request.GET.get("to")
    #    result = models_chart.search_AdverseRate(model_name, startTime, endTime)
    #   jsonstr = json.dumps(result)
#   return HttpResponse(jsonstr)

#def search_Ng(request):
    #    Logger.write_log("查找NG数据")
    #    model_name = request.GET.get("model_name")
    #    startTime = request.GET.get("from")
    #    endTime = request.GET.get("to")
    #   result = models_chart.search_Ng(model_name, startTime, endTime)
    #    jsonstr = json.dumps(result)
#   return HttpResponse(jsonstr)

#def search_Ok(request):
    #   Logger.write_log("查找OK数据")
    #   model_name = request.GET.get("model_name")
    #   startTime = request.GET.get("from")
    #   endTime = request.GET.get("to")
    #   result = models_chart.search_Ok(model_name, startTime, endTime)
    #   jsonstr = json.dumps(result)
#    return HttpResponse(jsonstr)

# 获取chart下拉数据(ASSY,PROCESS)
def get_select_content(request):
    Logger.write_log("获取chart下拉数据")
    model_name = request.GET.get("model_name")
    object = request.GET.get('object')
    result = models_chart.get_select_content(model_name,object)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr.encode("utf-8"))

# 查询chart数据
def search_chart(request):
    Logger.write_log("查询chart数据")
    result = []
    model_name = request.GET.get("model_name")
    start = request.GET.get('from')
    end = request.GET.get('to')
    object = request.GET.get('object')
    content = request.GET.get('content')
    type = request.GET.get('type')
    lineNum = request.GET.get('lineNum')
    if not lineNum:
        lineNum = "2nd"
    result = models_chart.search_chart(model_name,start,end,object,content,type,lineNum)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr.encode("utf-8"))