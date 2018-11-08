# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import operator
import datetime
from MfcOpeSys.models import models_common

def get_inspect(model_name, start_date, end_date, process_cd):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT \
                    defect.inspect_cd \
                FROM \
                    t_1_defect_2nd defect \
                    INNER JOIN t_1_auto_io_2nd auto ON defect.data_seq = auto.data_seq \
                    AND auto.process_at >= %s \
                    AND auto.process_at <= %s \
                    INNER JOIN m_assy assy ON auto.process_id = auto.process_id \
                    AND assy.process_cd = %s \
                ORDER BY inspect_cd"
        cur.execute(sql, (start_date, end_date, process_cd))
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def get_trend(model_name, start_date, end_date, process_cd, inspect_cd, time_part, type):
    process_at_list = models_common.get_periodDate(start_date, end_date)
    timePartStr = ""
    for value in time_part:
        timePartStr = timePartStr + "'" + value + "',"
    timePartStr = timePartStr[:-1]
    inspect_cd = inspect_cd.upper()

    # typeName设定
    if type == "NG":
        typeName = "failed_quantity"
    else:
        typeName = "yield2"

    data_zero = []
    data_NP = []
    try:
        i = 0
        while i < len(process_at_list):
            data_zero.append(0)
            data_NP.append("NP")
            i = i + 1

        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT \
                    auto_ng.line_cd,\
                    auto_ng.time_part,\
                    auto_ng.line_cd || ' ' || auto_ng.time_part AS lineAndTimepart, \
                    auto_ng.process_at, \
                    COALESCE ( auto_ok.ok_quantity, 0 ) AS ok_quantity,\
                    COALESCE ( auto_ng.ng_quantity, 0 ) AS ng_quantity,\
                    COALESCE ( defect.inspect_count, 0 ) AS failed_quantity,\
                    ( COALESCE ( auto_ok.ok_quantity, 0 ) + COALESCE ( auto_ng.ng_quantity, 0 ) ) AS input_quantity,\
                COALESCE ( defect.inspect_count, 0 ) / ( COALESCE ( auto_ok.ok_quantity, 0 ) + COALESCE ( auto_ng.ng_quantity, 0 ) ) AS detractor \
                FROM \
                    ( \
                SELECT \
                    line_cd,\
                    time_part,\
                    process_at,\
                    SUM( quantity ) AS ok_quantity \
                FROM \
                    m_assy A \
                    INNER JOIN t_1_auto_io_2nd auto ON A.process_id = auto.process_id \
                WHERE \
                    process_at >= '(start_date)' \
                    AND process_at <= '(end_date)' \
                    AND time_part IN( '(time_part)' ) \
                    AND judge_text = 'ok' \
                    AND process_cd = '(process_cd)' \
                GROUP BY \
                    line_cd,\
                    time_part,\
                    process_at \
                    ) AS auto_ok \
                  INNER JOIN (\
                SELECT \
                    line_cd,\
                    time_part,\
                    process_at,\
                    SUM( quantity ) AS ng_quantity \
                FROM \
                    m_assy A \
                    INNER JOIN t_1_auto_io_2nd auto ON A.process_id = auto.process_id \
                WHERE \
                    process_at >= '(start_date)' \
                    AND process_at <= '(end_date)' AND time_part IN('(time_part)') AND judge_text = 'ng' AND quantity > 0 \
                    AND process_cd = '(process_cd)' \
                GROUP BY \
                    line_cd,\
                    time_part,\
                    process_at \
                    ) AS auto_ng ON auto_ok.line_cd = auto_ng.line_cd \
                    AND auto_ok.time_part = auto_ng.time_part \
                    AND auto_ok.process_at = auto_ng.process_at \
                    INNER JOIN (\
                SELECT \
                    line_cd,\
                    time_part,\
                    process_at,\
                    COUNT( serial_cd ) AS inspect_count \
                FROM \
                    (\
                SELECT DISTINCT \
                    line_cd,\
                    time_part,\
                    process_at,\
                    defect.data_seq,\
                    defect.serial_cd \
                FROM \
                    m_assy A \
                    INNER JOIN t_1_auto_io_2nd auto ON A.process_id = auto.process_id \
                    INNER JOIN t_1_defect_2nd defect ON auto.data_seq = defect.data_seq \
                WHERE \
                    process_at >= '(start_date)' \
                    AND process_at <= '(end_date)' AND time_part IN('(time_part)') AND judge_text = 'ng' AND quantity > 0 \
                    AND process_cd = '(process_cd)' \
                    AND UPPER(inspect_cd) LIKE '%(inspect_cd_str)%' \
                    ) AS defect1 \
                GROUP BY \
                    line_cd,\
                    time_part,\
                    process_at \
                    ) AS defect ON auto_ng.line_cd = defect.line_cd \
                    AND auto_ng.time_part = defect.time_part \
                    AND auto_ng.process_at = defect.process_at \
                ORDER BY \
                    line_cd,\
                    time_part,\
                    process_at"
        sql = sql.replace("(start_date)", start_date).replace("(end_date)", end_date).replace("(process_cd)", process_cd) \
            .replace("(inspect_cd_str)", inspect_cd).replace("'(time_part)'", timePartStr)
        cur.execute(sql)
        rows = cur.fetchall()
        result_quantity = []
        for row in rows:
            # result_quantity.append({"line_cd":row[0], "lineAndTimepart":row[2], "process_at": str(row[3]),\
            #                         "failed_quantity": int(row[6]), "yield2":float(1-float(row[8])),})
            result_quantity.append({"line_cd": row[0], "lineAndTimepart": row[2], "process_at": str(row[3]), \
                                    "failed_quantity": int(row[6]), "yield2": float(float(row[8])), })
        if type == 'NG':
            # 获取All Line(sum)数据
            subSql_sum1 = "SELECT process_at,SUM( failed_quantity ) AS sum_failed_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
            sql = subSql_sum1 + sql + subSql_sum2
            cur.execute(sql)
            rows = cur.fetchall()
            result_quantity_all = []
            for row in rows:
                result_quantity_all.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })

        # get all lines
        lineArr = models_common.get_allLines(model_name)
        if lineArr == 101 or lineArr == 102:
            return lineArr

        # 设定目标json数据
        result = setDataList(process_at_list, result_quantity, typeName, lineArr, time_part)

        # sort
        result = sorted(result, key=lambda x: (x['name']))

        # All Line追加
        if type == 'NG':
            if len(result_quantity) == 0:
                result_all = {"name": "All Line", "data_tb": data_zero, 'data':data_zero}
            else:
                result_all = models_common.supplementZero("All Line", result_quantity_all, process_at_list, 'trend_chart')
        else:
            # get allLine
            if len(result_quantity) == 0:
                result_all = {'name': 'All Line', 'data_tb': data_zero, 'data':data_zero}
            else:
                # 求取平均值
                data = models_common.getAvg_allLine(result, process_at_list)
                result_all = {'name': 'All Line', 'data_tb': data, 'data':data}
        result.append(result_all)

        # 数据format
        if type == 'Y2':
            for row in result:
                row_data = []
                row_data_tb = []
                i = 0
                for value in row['data_tb']:
                    if value != 'NP':
                        row_data_tb.append("%.2f%%" % (value * 100))
                        row_data.append(float("%.2f" % (value * 100)))
                    else:
                        row_data_tb.append("NP")
                        row_data.append(float("%.2f" % 0))
                    i = i + 1

                row['data'] = row_data
                row['data_tb'] = row_data_tb
        else:
            for row in result:
                row_data = []
                i = 0
                for value in row['data']:
                    if value == 'NP':
                        row_data.append(0)
                    else:
                        row_data.append(value)
                    i = i + 1

                row['data'] = row_data

    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def setDataList(process_at_list, result_quantity, typeName, lineArr, time_part):
    result = []
    last_text = ""
    last_process_at = ""
    data = []
    data_zero = []
    index = 0
    end_date = datetime.datetime.strptime(process_at_list[-1], "%Y-%m-%d")

    i = 0
    while i < len(process_at_list):
        data_zero.append("NP")
        i = i + 1

    for row in result_quantity:
        begin_date = datetime.datetime.strptime(process_at_list[0], "%Y-%m-%d")
        current_date = datetime.datetime.strptime(row['process_at'], "%Y-%m-%d")
        if operator.eq(row['lineAndTimepart'], last_text) == False:
            # 不是第一条数据的场合
            if index != 0:
                # data数组最后的补位处理
                while last_process_at < end_date:
                    data.append("NP")
                    last_process_at += datetime.timedelta(days=1)

                result.append({'name': last_text, 'data_tb': data, 'data':data})
                data = []
                # data数组最前端的补位处理
                while begin_date < current_date:
                    data.append("NP")
                    begin_date += datetime.timedelta(days=1)

                data.append(row[typeName])

            else:
                # data数组最前端的补位处理
                while begin_date < current_date:
                    data.append("NP")
                    begin_date += datetime.timedelta(days=1)

                data.append(row[typeName])

            last_text = row['lineAndTimepart']
        else:
            # data数组中间的补位处理
            last_process_at += datetime.timedelta(days=1)
            while last_process_at < current_date:
                data.append("NP")
                last_process_at += datetime.timedelta(days=1)

            data.append(row[typeName])

        index = index + 1
        last_process_at = current_date

    if len(result_quantity) > 0:
        # 最后一条的处理（追加到result）
        while last_process_at < end_date:
            data.append("NP")
            last_process_at += datetime.timedelta(days=1)

        result.append({'name': last_text, 'data_tb': data, 'data':data})

    # 结果集里追加无数据的产线
    for line_cd in lineArr:
        flg = False
        for row in result_quantity:
            if operator.eq(row['line_cd'], line_cd):
                flg = True
                break

        if flg == False:
            for value in time_part:
                result.append({'name':line_cd + ' ' + value, 'data_tb':data_zero, 'data':data_zero})

    result_temp = []

    # 结果集里各产线追加无数据的time_part
    for line_cd in lineArr:
        for value in time_part:
            result_temp.append(line_cd + ' ' + value)

    for value in result_temp:
        flg = True
        for row in result:
            if row['name'] == value:
                flg = False
                break
        # 该timepart无数据的场合
        if flg:
            result.append({'name': value, 'data_tb': data_zero, 'data': data_zero})

    return result

