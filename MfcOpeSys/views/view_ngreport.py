# -*-coding:utf-8 -*-
'''summary views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json
import datetime
from MfcOpeSys.models import models_common
from MfcOpeSys.models import models_ngreport
from MfcOpeSys.models.models_logger import Logger
from django.views.decorators.csrf import csrf_exempt
import xlrd
from django.http import HttpResponse

def go_ngreport(request):
    '''不良发生状况'''
    Logger.write_log("不良发生状况")
    model = request.GET.get('model')
    return render(request, 'ngreport.html', {"model":model})

@csrf_exempt
def upload(request):
    Logger.write_log("获取上传文件")
    model_name = request.POST.get('model_name')
    try:
        wb = xlrd.open_workbook(
            filename = None,file_contents= request.FILES.get('file').read())
    except BaseException as exp:
        print(exp)
        return HttpResponse('Please ensure the excel file is correct')
    count = len(wb.sheets())  # sheet数量
    result = []
    result1 = []
    for sheet in wb.sheets():
        sheet_name = sheet.name
        table = sheet
        row = table.nrows

        if(row < 2):
            return HttpResponse('Please ensure the excel file data is not empty')
        revision = table.row_values(0)[1]
        mode_name = table.row_values(1)[1]
        type_1 = table.row_values(2)[1]
        type_2 = table.row_values(2)[2]
        if(mode_name.lower()!=model_name.lower()):
            return HttpResponse('Please ensure the model name is correct')
        for i in range(3, row):
            col = table.row_values(i)
            # mode_name, assy_text, plan_date, in_quantity, out_quantity, before_quantity, after_quantity
            if(models_ngreport.is_number(col[1]) != True):
                return HttpResponse('Please ensure the content format is correct')
            if (models_ngreport.is_number(col[2]) != True):
                return HttpResponse('Please ensure the content format is correct')
            # if (models_ngreport.is_number(col[3]) != True):
            #     return HttpResponse('Please ensure the content format is correct')
            # if (models_ngreport.is_number(col[4]) != True):
            #     return HttpResponse('Please ensure the content format is correct')
            if (models_ngreport.is_int(col[1]) != True):
                return HttpResponse('Please ensure the content format is correct')
            if (models_ngreport.is_int(col[2]) != True):
                return HttpResponse('Please ensure the content format is correct')
            # if (models_ngreport.is_int(col[3]) != True):
            #     return HttpResponse('Please ensure the content format is correct')
            # if (models_ngreport.is_int(col[4]) != True):
            #     return HttpResponse('Please ensure the content format is correct')
            assy_text = col[0]
            val_1 = col[1]
            val_2 = col[2]
            data = {"ID": i - 2, "Mode_Name": mode_name, "Assy_Name": assy_text, "Date": sheet_name,
                    type_1: val_1, type_2: val_2}
            # if(type.lower() == 'in_quantity' or type.lower() == 'out_quantity'):
            #     assy_text = col[0]
            #     in_quantity = col[1]
            #     out_quantity = col[2]
            #     data = {"ID": i - 1, "Mode_Name": mode_name, "Assy_Name": assy_text, "Date": sheet_name,
            #             "In": in_quantity, "Out": out_quantity}
            # elif(type.lower() == 'before_quantity' or type.lower() == 'after_quantity'):
            #     assy_text = col[0]
            #     before_quantity = col[1]
            #     after_quantity = col[2]
            #     data = {"ID": i - 1, "Mode_Name": mode_name, "Assy_Name": assy_text, "Date": sheet_name,
            #             "Before": before_quantity, "After": after_quantity}
            result.append(data)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

@csrf_exempt
def insertDatabase_back(request):
    from datetime import datetime
    Logger.write_log("获取上传文件")
    model_name = request.POST.get('model_name')
    wb = xlrd.open_workbook(
        filename=None, file_contents=request.FILES.get('file').read())
    count = len(wb.sheets())  # sheet数量
    param = []
    for sheet in wb.sheets():
        table = sheet
        revision = table.row_values(0)[1]
        sheet_name = sheet.name
        plan_date = datetime.strptime(sheet_name, "%Y-%m-%d")
        models_common.deletePlanData(model_name,plan_date)
        row = table.nrows
        mode_name = table.row_values(1)[1]
        type = table.row_values(2)[1]
        for i in range(3, row):
            col = table.row_values(i)
            # mode_name, assy_text, plan_date, in_quantity, out_quantity, before_quantity, after_quantity
            if(type.lower() == 'in_quantity' or type.lower() == 'out_quantity'):
                assy_text = col[0]
                in_quantity = col[1]
                out_quantity = col[2]
                before_quantity = 0
                after_quantity = 0
            elif(type.lower() == 'before_quantity' or type.lower() == 'after_quantity'):
                assy_text = col[0]
                in_quantity = 0
                out_quantity = 0
                before_quantity = col[1]
                after_quantity = col[2]
            if(models_ngreport.check_planTable(model_name)==False):
                result = {'status': "fail"}
                jsonstr = json.dumps(result)
                return HttpResponse(jsonstr)
            param.append([mode_name,assy_text,plan_date,in_quantity,out_quantity,before_quantity,after_quantity,revision])
    ret = models_common.get_exceldata(model_name,param)
    jsonstr = json.dumps(ret)
    return HttpResponse(jsonstr)

@csrf_exempt
def insertDatabase(request):
    from datetime import datetime
    Logger.write_log("获取上传文件")
    model_name = request.POST.get('model_name')
    wb = xlrd.open_workbook(
        filename=None, file_contents=request.FILES.get('file').read())
    count = len(wb.sheets())  # sheet数量
    params = []
    param = []
    flag = 0
    for sheet in wb.sheets():
        table = sheet
        revision = table.row_values(0)[1]
        sheet_name = sheet.name
        plan_date = datetime.strptime(sheet_name, "%Y-%m-%d")
        row = table.nrows
        mode_name = table.row_values(1)[1]
        if (models_ngreport.check_planTable(model_name) == False):
            result = {'status': "fail"}
            jsonstr = json.dumps(result)
            return HttpResponse(jsonstr)
        params = models_common.getPlanData(model_name,plan_date,revision)
        type = table.row_values(2)[1]
        if(len(params) == 0):
            for i in range(3, row):
                col = table.row_values(i)
                if (type.lower() == 'in_quantity' or type.lower() == 'out_quantity'):
                    assy_text = col[0]
                    in_quantity = col[1]
                    out_quantity = col[2]
                    before_quantity = 0
                    after_quantity = 0
                elif (type.lower() == 'before_quantity' or type.lower() == 'after_quantity'):
                    assy_text = col[0]
                    in_quantity = 0
                    out_quantity = 0
                    before_quantity = col[1]
                    after_quantity = col[2]
                param.append([mode_name, assy_text, plan_date, in_quantity, out_quantity, before_quantity, after_quantity,revision])
            ret = models_common.get_exceldata(model_name, param)
            param = []
        else:
            for i in range(3, row):
                col = table.row_values(i)
                if (type.lower() == 'in_quantity' or type.lower() == 'out_quantity'):
                    assy_text = col[0]
                    in_quantity = col[1]
                    out_quantity = col[2]
                    before_quantity = 0
                    after_quantity = 0
                    param.append(
                        [mode_name, assy_text, plan_date, in_quantity, out_quantity, before_quantity, after_quantity,
                         revision])
                    flag = 1
                elif (type.lower() == 'before_quantity' or type.lower() == 'after_quantity'):
                    assy_text = col[0]
                    in_quantity = 0
                    out_quantity = 0
                    before_quantity = col[1]
                    after_quantity = col[2]
                    param.append(
                        [mode_name, assy_text, plan_date, in_quantity, out_quantity, before_quantity, after_quantity,
                         revision])
                    flag = 2
            for key in param:
                for keys in params:
                    if(keys['assy_text'] == key[1]):
                        if flag == 1:
                            key[5] = keys['before']
                            key[6] = keys['after']
                        elif flag == 2:
                            key[3] = keys['in']
                            key[4] = keys['out']
                print (key[0], key[1], key[2], key[3], key[4], key[5], key[6], key[7])
            ret = models_common.get_exceldata(model_name, param)
            params = []
            param = []
    jsonstr = json.dumps(ret)
    return HttpResponse(jsonstr)

def exits_mplan(request):
    '''m_plan当天数据是否存在'''
    Logger.write_log("m_plan当天数据是否存在")
    model = request.GET.get('model_name')
    result = models_ngreport.exits_mplan(model)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def getSummaryTimeType(request):
    Logger.write_log("获取time_table数据")
    model_name = request.GET.get('model_name')
    result = models_ngreport.getSummaryTimeType(model_name)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def getStartEndTime(request):
    Logger.write_log("获取Start End时间数据")
    model_name = request.GET.get('model_name')
    timeType = request.GET.get('timeType')
    result = models_ngreport.getStartEndTime(model_name,timeType)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

def get_Achievement_Rate(request):
    Logger.write_log("获取Achievement Rate时间数据")
    model_name = request.GET.get('model_name')
    result = models_ngreport.getAchievementRate(model_name)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)