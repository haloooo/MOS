# -*-coding:utf-8 -*-
from __future__ import unicode_literals
import json
from MfcOpeSys.models import models_summary_offset
from MfcOpeSys.models.models_logger import Logger
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def initSummaryOffsetData(request):
    Logger.write_log("初始化Summary Offset数据")
    model = request.GET.get('model_name')
    result = []
    result = models_summary_offset.initSummaryOffsetData(model)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)

@csrf_exempt
def update_summary_offset(request):
    Logger.write_log("更新summary_offset数据")
    model = request.GET.get('model_name')
    received_json_data = json.loads(request.body.decode('utf-8'))
    for item in received_json_data:
        assy_text = item['assy_text']
        ng_count = item['ng_count']
        reason = item['reason']
        result = []
        result = models_summary_offset.update_summary_offset(model, assy_text,ng_count,reason)
        if(result['status'] == 'fail'):
            jsonstr = json.dumps(result)
            return HttpResponse(jsonstr)
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)
