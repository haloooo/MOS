# -*-coding:utf-8 -*-
'''传感器 views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json,os
from MfcOpeSys.models import models_common
import datetime
from django.http import HttpResponse
from MfcOpeSys.models.models_logger import Logger
from MfcOpeSys.models import models_sntracert
from MfcOpeSys.models import models_trend_chart

def get_config(key):
    # 加载配置文件
    file_path = os.getcwd() + '/config/config.json'
    fp = open(file_path)
    json_data = json.load(fp)
    return json_data[key]

def test(request):
    Logger.write_log("获取LINES列表")

    result = models_common.test()
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def go_assy(request):
    '''ASSY'''
    Logger.write_log("ASSY")
    model = request.GET.get('model')
    return render(request, 'assy.html', {"model":model})
def go_sttype(request):
    '''ST Type'''
    Logger.write_log("ST Type")
    model = request.GET.get('model')
    return render(request, 'worktime.html', {"model":model})
def go_config(request):
    '''Configure'''
    Logger.write_log("Configure")
    model = request.GET.get('model')
    return render(request, 'configure.html', {"model":model})

def go_summary_offset(request):
    '''Configure'''
    Logger.write_log("Summary_Offset")
    model = request.GET.get('model')
    return render(request, 'summary_offset.html', {"model":model})

def get_lines(request):
    Logger.write_log("获取LINES列表")
    model_name = request.GET.get('model_name')
    result = models_common.get_lines(model_name)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_assys(request):
    line = request.GET.get('line')
    model_name = request.GET.get('model_name')
    if(line == 'All Line'):
        result = models_common.get_allAssy(model_name)
    else:
        result = models_common.get_assys(model_name, line)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_datatypeIds(request):
    line = request.GET.get('line')
    model_name = request.GET.get('model_name')
    result = models_common.get_datatypeIds(model_name, line)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_tps(request):
    model_name = request.GET.get('model_name')
    line = request.GET.get('line')
    assy = request.GET.get('assy')
    result = models_common.get_tps(model_name, line, assy)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_1_processdetail(request):
    Logger.write_log("根据assy,date,time_part,获取First工位信息一览")
    model_name = request.GET.get('model_name')
    line = request.GET.get('line')
    assy = request.GET.get('assy')
    process_at = request.GET.get('process_at')
    time_part = request.GET.get('time_part')
    selectedModel = request.GET.get('selectedModel')
    result = models_common.get_processdetail(model_name,line,assy,process_at,time_part,'First',selectedModel)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_2_processdetail(request):
    Logger.write_log("根据assy,date,time_part,获取Second工位信息一览")
    model_name = request.GET.get('model_name')
    line = request.GET.get('line')
    assy = request.GET.get('assy')
    process_at = request.GET.get('process_at')
    time_part = request.GET.get('time_part')
    selectedModel = request.GET.get('selectedModel')
    result = models_common.get_processdetail(model_name,line,assy,process_at,time_part,'Second',selectedModel)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_1_defectdetail(request):
    Logger.write_log("获取First具体不良信息")
    model_name = request.GET.get('model_name')
    data_seq = request.GET.get('data_seq')
    inspect_cd = request.GET.get('inspect_cd')
    result = models_common.get_defectdetail(model_name, data_seq, inspect_cd, 'First')
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_2_defectdetail(request):
    Logger.write_log("获取Second具体不良信息")
    model_name = request.GET.get('model_name')
    data_seq = request.GET.get('data_seq')
    inspect_cd = request.GET.get('inspect_cd')
    result = models_common.get_defectdetail(model_name, data_seq, inspect_cd, 'Second')
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_summaryDetail(request):
    Logger.write_log("获取所选Model的Summary一览")
    Search_date = request.GET.get('searchDate')
    model_name = request.GET.get('model_name')
    time_type = request.GET.get('time_type')
    lineNum = request.GET.get('lineNum')
    if not lineNum:
        lineNum="2nd"
    result = models_common.get_summaryDetail(model_name,Search_date,time_type,lineNum)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_lineSummaryDetail(request):
    Logger.write_log("统计所选Model的line/Assy信息")
    Search_date = request.GET.get('searchDate')
    model_name = request.GET.get('model_name')
    time_type = request.GET.get('time_type')
    lineNum= request.GET.get('lineNum')
    if not lineNum:
        lineNum="2nd"
    result = models_common.get_lineSummaryDetail(model_name,Search_date,time_type,lineNum)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def getServerDate(request):
    process_at = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%m/%d')
    return HttpResponse(process_at)

def getFullServerDate(request):
    process_at = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    return HttpResponse(process_at)

def getTodayServerDate(request):
    # n = random.randint(1, 20)
    # process_at = (datetime.date.today() - datetime.timedelta(days=n)).strftime('%Y-%m-%d')
    process_at = (datetime.date.today()).strftime('%Y-%m-%d')
    return HttpResponse(process_at)

def getLine(request):
    Logger.write_log("根据assy获取line")
    model_name = request.GET.get('model_name')
    assy = request.GET.get('assy')
    result = models_common.getLine(model_name, assy)
    return HttpResponse(result)

def go_upload(request):
    Logger.write_log("进入upload页面")
    model = request.GET.get('model')
    return render(request, 'upload.html', {"model": model})

def go_history(request):
    Logger.write_log("进入trend页面")
    objects = get_config('object')
    model = request.GET.get('model')
    return render(request, 'history.html', {"model": model,"objects":objects})

def go_defect(request):
    Logger.write_log("进入defect页面")
    model = request.GET.get('model')
    return render(request, 'defect.html', {"model": model})

def search_defect(request):
    Logger.write_log("进入defect pareto页面")
    model_name = request.GET.get('model_name')
    startTime = request.GET.get('from')
    endTime = request.GET.get('to')
    line = request.GET.get('line')
    assy = request.GET.get('assy')
    time_part = request.GET.get('time_part')
    top_rank = request.GET.get('top_rank')
    target = request.GET.get('target')
    mode = request.GET.get('mode')
    result = models_common.search_defect(model_name, startTime, endTime, line, assy, time_part, top_rank, target, mode)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr.encode("utf-8"))

def checkConnection(request):
    model = request.GET.get('model')
    result = models_common.checkConnection(model)
    return HttpResponse(result)

def get_sntracert(request):
    Logger.write_log("显示工位信息以及各工位下的各部品状况信息")
    model_name = request.GET.get('model_name')
    from_process_at = request.GET.get('from')
    to_process_at = request.GET.get('to')
    config = request.GET.get('config')
    line = request.GET.get('line')
    datatype_id = request.GET.get('datatype_id')
    mode = request.GET.get('mode')
    pernum=request.GET.get('pernum')
    c_pernum=int(pernum)
    result = models_sntracert.get_sntracert(model_name, from_process_at, to_process_at, config, line, datatype_id, mode, c_pernum)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_configs(request):
    Logger.write_log("取得所有config信息")
    model_name = request.GET.get('model_name')
    from_process_at = request.GET.get('from')
    to_process_at = request.GET.get('to')
    result = models_common.get_configs(model_name, from_process_at, to_process_at)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def go_sntracert(request):
    Logger.write_log("进入sn tracert页面")
    model = request.GET.get('model')
    return render(request, 'sntracert.html', {"model": model})

def get_trendOfDefect(request):
    Logger.write_log("显示所有产线在各个时间段里的不良项目")
    model_name = request.GET.get('model_name')
    start_date = request.GET.get('from')
    end_date = request.GET.get('to')
    process_cd = request.GET.get('process_cd')
    inspect_cd = request.GET.get('inspect_cd')
    time_part = request.GET.get('time_part')
    dataType = request.GET.get('dataType')

    result = models_trend_chart.get_trend(model_name, start_date, end_date, process_cd, inspect_cd, time_part, dataType)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)