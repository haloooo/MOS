# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import json
import os
import operator

def initConfigureData(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        # cur.execute("SELECT DISTINCT line_cd FROM m_work ORDER BY line_cd")
        # rows = cur.fetchall()
        # i = 1
        # for row in rows:
        #     line_cd = row[0]
        #     cur.execute("SELECT assy_text,time_tbl_cd from m_work where line_cd = %s", (line_cd,))
        #     rows_1 = cur.fetchall()
        #     for row_1 in rows_1:
        #         assy.append({'assy_text':row_1[0],'time_tbl_cd':row_1[1]})
        #     result.append({'num':i,'line_cd':row[0],'assy_text_list':assy})
        #     i = i + 1
        #     assy = []
        #     assy_text = ""
        i = -1
        cur.execute("SELECT\
                    a.assy_text = b.assy_text checked,\
                    b.line_cd,\
                    b.assy_text,\
                    a.time_tbl_cd\
                FROM\
                    (\
                SELECT\
                    a.assy_text,\
                    line_cd,\
                    time_tbl_cd\
                FROM\
                    ( SELECT DISTINCT assy_text FROM m_assy ) A\
                    RIGHT JOIN ( SELECT line_cd, assy_text, time_tbl_cd FROM m_work ) B ON A.assy_text = B.assy_text\
                ORDER BY\
                    line_cd,\
                    assy_text\
                    ) a\
                    RIGHT JOIN (\
                SELECT\
                    line_cd,\
                    assy_text\
                FROM\
                    ( SELECT DISTINCT assy_text FROM m_assy ORDER BY assy_text ) a,\
                    ( SELECT DISTINCT line_cd FROM m_work ORDER BY line_cd ) b\
                ORDER BY\
                    line_cd,\
                    assy_text\
                    ) b ON a.line_cd = b.line_cd\
                    AND a.assy_text = b.assy_text\
                ORDER BY\
                    b.line_cd,\
                    b.assy_text")
        rows = cur.fetchall()
        line = ""
        for row in rows:
            checked = (row[0] == True)
            if line == row[1]:
                result[i]["assy_text_list"].append({'checked': checked, 'assy_text': row[2], 'time_tbl_cd': row[3]})
            else:
                i = i + 1
                line = row[1]
                result.append({'num': i + 1, 'line_cd': row[1], 'assy_text_list': [{'checked': checked, 'assy_text': row[2], 'time_tbl_cd': row[3]}]})

    except BaseException as exp:
        print(exp)
    connections[model_name].close()
    return result

def get_time_tbl_cd(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT DISTINCT time_tbl_cd from m_time_table where trim(time_tbl_cd) <> ''")
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
    connections[model_name].close()
    return result

def get_assy_text(model_name,line_cd):
    result = []
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT assy_text from m_work where line_cd = %s",(line_cd,))
        rows = cur.fetchall()
        for row in rows:
            result.append({'assy_text': row[0]})
    except BaseException as exp:
        print(exp)
    connections[model_name].close()
    return result

# def update_worktime(model_name, Assy_Text,work_time,Line_name):
#     result = []
#     try:
#         cur = connections[model_name].cursor()
#         sql = 'UPDATE m_work SET time_tbl_cd = %s WHERE line_cd = %s AND assy_text = %s'
#         cur.execute(sql, (work_time,Line_name,Assy_Text,))
#         connections[model_name].commit
#         result = {'status': "success"}
#     except BaseException as exp:
#         print exp
#         result = {'status': "fail"}
#     connections[model_name].close()
#     return result

def update_worktime(model_name, data):
    result = []
    try:
        cur = connections[model_name].cursor()
        for row in data:
            for subitem in row["assy_text_list"]:
                if subitem["checked"] == False:
                    sql = 'DELETE FROM m_work WHERE line_cd = %s AND assy_text = %s'
                    cur.execute(sql, (row["line_cd"], subitem["assy_text"],))
                else:
                    sql = "select line_cd from m_work WHERE line_cd = %s AND assy_text = %s"
                    cur.execute(sql, (row["line_cd"], subitem["assy_text"],))
                    rows = cur.fetchall()
                    if len(rows) > 0:
                        sql = "UPDATE m_work SET time_tbl_cd = %s WHERE line_cd = %s AND assy_text = %s"
                        cur.execute(sql, (subitem["time_tbl_cd"], row["line_cd"], subitem["assy_text"],))
                    else:
                        sql = "select max(work_seq) + 1 from m_work"
                        cur.execute(sql)
                        items = cur.fetchall()
                        sql = "INSERT into m_work VALUES (%s,%s,%s,%s)"
                        cur.execute(sql, (items[0][0], row["line_cd"], subitem["assy_text"], subitem["time_tbl_cd"],))
        connections[model_name].commit
        result = {'status': "success"}
    except BaseException as exp:
        print(exp)
        result = {'status': "fail"}
    connections[model_name].close()
    return result