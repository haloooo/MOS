# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import operator
from django.db import connections
import datetime



def exits_mplan(model_name):
    try:
        exits = False
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=-1)
        yestoday = now + delta
        #print yestoday.strftime('%Y-%m-%d')
        cur = connections[model_name].cursor()
        cur.execute("SELECT to_regclass('m_plan') is not null as EXISTS")
        rows = cur.fetchall()
        for row in rows:
            exits = row[0]
        cur.execute("select plan_date from m_plan where plan_date=%s", (yestoday.strftime('%Y-%m-%d'),))
        rows = cur.fetchall()
        exits = exits and (len(rows) > 0)
    except BaseException as exp:
        print(exp)
    connections[model_name].close()
    return exits


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

def is_int(x):
    try:
        x=int(x)
        return isinstance(x,int)
    except ValueError:
        return False

def check_planTable(model_name):
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT to_regclass('m_plan') is not null as EXISTS")
        rows = cur.fetchall()
        for row in rows:
            exits = row[0]
        if not exits:
            SQL = 'CREATE TABLE "public"."m_plan" ( \
            "id" SERIAL PRIMARY KEY NOT NULL, \
            "mode_name" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT NULL::character varying, \
            "assy_text" text COLLATE "pg_catalog"."default" NOT NULL DEFAULT NULL::character varying, \
            "plan_date" date NOT NULL, \
            "in_quantity" int4 NOT NULL, \
            "out_quantity" int4 NOT NULL, \
            "before_quantity" int4 NOT NULL, \
            "after_quantity" int4 NOT NULL, \
            "revision" int4 NOT NULL)'
            cur.execute(SQL)
        return True
    except BaseException as exp:
        print(exp)
        return False
    connections[model_name].close()

def getSummaryTimeType(model_name):
    try:
        from MfcOpeSys.models import models_common
        result = []
        cur = connections[model_name].cursor()
        SQL = 'select time_tbl_cd from m_time_table order by time_tbl_cd  limit 1'
        cur.execute(SQL)
        row = cur.fetchone()
        SQL = 'SELECT time_part from m_time_table WHERE time_tbl_cd = %s order by time_part;'
        cur.execute(SQL,(row[0],))
        rows = cur.fetchall()
        result_temp1 = []
        result_temp2 = []
        for row in rows:
            if row[0] == 'All' or row[0] == 'Night' or row[0] == 'Day':
                result_temp1.append(row[0])
            else:
                result_temp2.append(row[0])

        result = result_temp1
        result.extend(result_temp2)
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def getStartEndTime(model_name,timeType):
    try:
        result = []
        cur = connections[model_name].cursor()
        SQL = 'SELECT DISTINCT time_val_s,time_val_e FROM m_time_table WHERE time_part = %s;'
        cur.execute(SQL,(timeType,))
        row = cur.fetchone()
        result.append(row[0])
        result.append(row[1])
    except BaseException as exp:
        print(exp)
    connections[model_name].close()
    return result

def getAchievementRate(model_name):
    from MfcOpeSys.models import models_common
    database_list = models_common.get_config("database")
    result = []
    in_out = []
    yield2 = []
    for row in database_list:
        if operator.eq(row['MODEL'], model_name):
            # 从配置文件里取得ASSY
            in_out = row['RGB']['In/Out_Boundary_Value']
            # 从配置文件里取得FORMULA
            yield2 = row['RGB']['Yield2_Boundary_Value']
            break
    result = [{"in_out":in_out,"yield2":yield2}]
    return result


