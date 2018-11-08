# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections

def add_worktime(model_name, worktime):
    result = {"status": "success", "message": "added successfully."}
    try:
        details = []
        cur = connections[model_name].cursor()
        cur.execute("SELECT time_tbl_cd FROM  m_time_table WHERE time_tbl_cd = %s", (worktime["worktime_name"],))
        rows = cur.fetchall()
        if len(rows) == 0:
            # worktime不存在
            for item in worktime["detail"]:
                if item["time_part"] == 'All':
                    time_type = 'ONE DAY'
                elif item["time_part"] == 'Day':
                    time_type = 'DAY SHIFT'
                elif item["time_part"] == 'Night':
                    time_type = 'NIGHT SHIFT'
                else:
                    time_type = 'ONE HOUR'
                details.append([worktime["worktime_name"], item["time_part"],time_type, 0 , item["time_val_s"],0, item["time_val_e"]])
            cur.executemany("INSERT INTO m_time_table VALUES \
                        ( %s, %s, %s, %s, %s,%s, %s )", details)
            connections[model_name].commit
        else:
            # worktime存在
            result = {"status": "fail", "message": "worktime has already existed."}
    except BaseException as exp:
        print(exp)
        result = {"status": "fail", "message": exp}
    connections[model_name].close()
    return result

def edit_worktime_detail(model_name, field, value, worktime_name, time_part):
    result = {"status": "success", "message": "updated successfully."}
    try:
        cur = connections[model_name].cursor()
        sql = "UPDATE m_time_table SET "+ field +" = %s WHERE time_tbl_cd = %s and time_part = %s"
        cur.execute(sql,
                    (value, worktime_name, time_part,))
        connections[model_name].commit
    except BaseException as exp:
        print(exp)
        result = {"status": "fail", "message": exp}
    connections[model_name].close()
    return result

def del_worktime(model_name, worktime_name):
    result = {"status": "success", "message": "delete successful."}
    try:
        cur = connections[model_name].cursor()
        cur.execute("DELETE FROM m_time_table WHERE time_tbl_cd = %s",
                    (worktime_name,))
        connections[model_name].commit
    except BaseException as exp:
        print(exp)
        result = {"status": "fail", "message": exp}
    connections[model_name].close()
    return result

def del_worktime_detail(model_name, worktime_name, time_part):
    result = {"status": "success", "message": "delete successful."}
    try:
        cur = connections[model_name].cursor()
        cur.execute("DELETE FROM m_time_table WHERE time_tbl_cd = %s and time_part = %s",
                    (worktime_name, time_part,))
        connections[model_name].commit
    except BaseException as exp:
        print(exp)
        result = {"status": "fail", "message": exp}
    connections[model_name].close()
    return result

def get_worktime(model_name):
    result = {"status": "success", "message": "query successfully.", "data": []}
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT * FROM m_time_table ORDER BY time_tbl_cd, time_part")
        rows = cur.fetchall()
        worktime_name = ""
        index1 = -1
        for row in rows:
            if worktime_name == row[0]:
                detail = {"time_part": row[1], "delta_day": row[2], "time_val_s": row[4], "time_val_e": row[6]}
                result["data"][index1]["detail"].append(detail)
            else:
                worktime_name = row[0]
                index1 = index1 + 1
                detail = [{"time_part": row[1], "delta_day": row[2], "time_val_s": row[4], "time_val_e": row[6]}]
                result["data"].append({"worktime_name": row[0], "detail": detail})
    except BaseException as exp:
        print(exp)
        result = {"status": "fail", "message": exp}
    connections[model_name].close()
    return result

def update_sttype(model_name,work_name,time_part,time_type,Start_Time,End_Time):
    try:
        result = {"status": "success", "message": "update successful."}
        cur = connections[model_name].cursor()
        SQL = 'INSERT INTO m_time_table (time_tbl_cd,time_part,time_type,delta_day_s,time_val_s,delta_day_e,time_val_e) VALUES(%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(SQL, (work_name,time_part,time_type,0,Start_Time,0,End_Time,))
        connections[model_name].commit
    except BaseException as exp:
        result = {"status": "fail", "message": exp}
        print(exp)
    connections[model_name].close()
    return result

def del_workname(model_name,work_name):
    try:
        cur = connections[model_name].cursor()
        SQL = 'DELETE FROM m_time_table WHERE time_tbl_cd = %s'
        cur.execute(SQL,(work_name,))
        connections[model_name].commit
    except BaseException as exp:
        print(exp)
    connections[model_name].close()



