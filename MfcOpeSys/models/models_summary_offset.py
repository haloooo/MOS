# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import json
import os
import operator
import datetime

from MfcOpeSys.models import models_common


def initSummaryOffsetData(model_name):
    result = []
    try:
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        cur = connections[model_name].cursor()
        cur.execute("SELECT DISTINCT assy_text,min(process_id) as a FROM m_assy GROUP BY assy_text ORDER BY a;")
        rows = cur.fetchall()
        create_summary_offset_table(model_name,cur)
        for row in rows:
            assy_text = row[0]
            cur.execute("SELECT ng_count,reason,date FROM m_summary_offset WHERE assy_text = %s;",(assy_text,))
            row_m = cur.fetchone()
            if(row_m != None):
                if(row_m[2] == yesterday):
                    result.append({'assy_text': row[0], 'ng_count': row_m[0], 'reason': row_m[1]})
                else:
                    result.append({'assy_text': row[0], 'ng_count': 0, 'reason': ''})
            else:
                result.append({'assy_text': row[0], 'ng_count': 0, 'reason': ''})
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def update_summary_offset(model_name, assy_text,ng_count,reason):
    result = []
    try:
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        cur = connections[model_name].cursor()
        cur.execute("SELECT assy_text FROM m_summary_offset WHERE assy_text = %s;", (assy_text,))
        row = cur.fetchone()
        if (row != None):
            sql = 'UPDATE m_summary_offset SET ng_count = %s,reason = %s,date = %s WHERE assy_text = %s'
            cur.execute(sql, (ng_count, reason,yesterday, assy_text,))
        else:
            sql = 'INSERT INTO m_summary_offset(assy_text,ng_count,reason,date) VALUES (%s,%s,%s,%s) '
            cur.execute(sql,(assy_text,ng_count,reason,yesterday,))
        connections[model_name].commit
        result = {'status': "success"}
    except BaseException as exp:
        print(exp)
        result = {'status': "fail"}
    connections[model_name].close()
    return result

def create_summary_offset_table(model_name,cur):
    try:
        cur.execute("SELECT to_regclass('m_summary_offset') is not null as EXISTS")
        rows = cur.fetchall()
        for row in rows:
            exits = row[0]
        if not exits:
            SQL = 'CREATE TABLE "public"."m_summary_offset" ( \
                    "id" SERIAL PRIMARY KEY NOT NULL, \
                    "assy_text" text COLLATE "default" NOT NULL,\
                    "ng_count" int4 NOT NULL,\
                    "reason" text COLLATE "default" NOT NULL,\
                    "date" date NOT NULL\
                )'
            cur.execute(SQL)
    except BaseException as exp:
        print(exp)
