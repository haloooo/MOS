# -*-coding:utf-8 -*-
'''Worktime views '''
from __future__ import unicode_literals
import json
from django.http import HttpResponse
from MfcOpeSys.models.models_logger import Logger
from MfcOpeSys.models import models_worktime
from django.views.decorators.csrf import csrf_exempt

def add_worktime(request):
    Logger.write_log("add worktime")
    model = request.GET.get('model')
    str_json = str(request.GET.get('worktime'))
    worktime = json.loads(str_json)
    result = models_worktime.add_worktime(model, worktime)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def del_worktime(request):
    Logger.write_log("del worktime")
    model = request.GET.get('model')
    worktime_name = request.GET.get('worktime_name')
    result = models_worktime.del_worktime(model, worktime_name)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def del_worktime_detail(request):
    Logger.write_log("del_worktime_detail")
    model = request.GET.get('model')
    worktime_name = request.GET.get('worktime_name')
    time_part = request.GET.get('time_part')
    result = models_worktime.del_worktime(model, worktime_name, time_part)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def edit_worktime_detail(request):
    Logger.write_log("del worktime")
    model = request.GET.get('model')
    worktime_name = request.GET.get('worktime_name')
    time_part = request.GET.get('time_part')
    field = request.GET.get('field')
    value = request.GET.get('value')
    result = models_worktime.edit_worktime_detail(model, field, value, worktime_name, time_part)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_worktime(request):
    Logger.write_log("get worktime")
    model = request.GET.get('model')
    result = models_worktime.get_worktime(model)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

@csrf_exempt
def update_sttype(request):
    Logger.write_log("get sttype")
    model_name = request.GET.get('model_name')
    content = request.body.decode("utf-8")
    received_json_data = json.loads(content)
    work_name_list = []
    result = []
    for item in received_json_data:
        work_name = item['work_name']
        if work_name not in work_name_list:
            work_name_list.append(work_name)
    for item in work_name_list:
        models_worktime.del_workname(model_name,item)
    for item in received_json_data:
        work_name = item['work_name']
        time_part = item['time_part']
        Day_Night = item['Day_Night']
        Start_Time = item['Start_Time']
        End_Time = item['End_Time']
        if Day_Night=='Day':
            Day_Night = 0
        else:
            Day_Night = 1
        if time_part == 'All':
            time_type = 'ONE DAY'
        elif time_part == 'Day':
            time_type = 'DAY SHIFT'
        elif time_part == 'Night':
            time_type = 'NIGHT SHIFT'
        else:
            time_type = 'ONE HOUR'
        result = models_worktime.update_sttype(model_name,work_name,time_part,time_type,Start_Time,End_Time)
        if(result['status'] == 'fail'):
            jsonstr = json.dumps(result)
            return HttpResponse(jsonstr)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)