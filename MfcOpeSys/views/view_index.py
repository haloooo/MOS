# -*-coding:utf-8 -*-
'''传感器 views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json
import datetime
from django.http import HttpResponse

from MfcOpeSys.models.models_logger import Logger
from MfcOpeSys.models import models_common

# @auth_required
def go_index(request):
    '''HOME PAGE'''
    Logger.write_log("进入HOME Page")
    return render(request, 'index.html', {})

def get_models(request):
    Logger.write_log("获取MODELS列表")
    result = models_common.get_models()
    jsonstr = json.dumps(result)
    return HttpResponse(jsonstr)
