# -*-coding:utf-8 -*-
'''传感器 views '''
from __future__ import unicode_literals
from django.shortcuts import render
import json
import datetime
from MfcOpeSys.models.models_auth import auth_required
from MfcOpeSys.models.models_logger import Logger

@auth_required
def go_manufacture(request):
    '''生产实绩'''
    Logger.write_log("生产实绩")
    model = request.GET.get('model')
    return render(request, 'manufacture.html', {"model":model})