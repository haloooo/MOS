# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db import connection


# 权限控制装饰器
def auth_required(view):
    def decorator(request, *args, **kwargs):
        return view(request, *args, **kwargs)
    return decorator


