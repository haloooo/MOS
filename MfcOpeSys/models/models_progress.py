# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import operator
import datetime
from datetime import timedelta
import time
from MfcOpeSys.models import models_common

def get_progressDetail(model_name, search_date,lineNum):
    result = []
    header_data = []
    lineArr = []
    # 页面跳转用
    lines_hid = []
    lineArr_temp = []
    dateArr = []
    dayNightArr = []
    timepartArr = []
    time_part = ''
    try:
        database_list = models_common.get_config("database")
        assyDic = {}
        assyDic_int = {}
        formulaDic = {}
        timepartDic = {}
        fpy_sub_formula_dic = {}
        # timeparts：例：{0："D01"}
        timeparts = {}
        timepartName = "--"
        timepartValue = "--"
        for row in database_list:
            if operator.eq(row['MODEL'], model_name):
                # 从配置文件里取得ASSY
                assyDic = row['ASSY']
                # 从配置文件里取得FORMULA
                formulaDic = row['FORMULA_SUMMARY']
                # 从配置文件里取得time_part
                timepartDic = row['TIME_PART']
                break

        # 系统日期的取得
        now = datetime.datetime.now()
        process_at = now.strftime("%Y-%m-%d")
        times = now.strftime("%H:%M")
        sysdatatime = process_at + ' ' + times
        yesterday = now + datetime.timedelta(days=-1)
        yesterday = yesterday.strftime('%Y-%m-%d')

        # 从config文件取得time_part
        j = 1
        sorted(timepartDic.keys())
        timepartList = sorted(timepartDic.items(), key=lambda d: d[0], reverse=False)
        for key in timepartDic:
            timeparts[int(key)] = timepartDic[key].split(',')[0]
        for key in timepartList:
            timepartStart = process_at + ' ' + key[1].split(',')[1].split('-')[0]
            timepartEnd = process_at + ' ' + key[1].split(',')[1].split('-')[1]
            if compare_time(sysdatatime, timepartStart, timepartEnd):
                j = int(key[0])
                break

        sql_timepart = "time_part = '" + time_part + "' "
        if j != 1:
            time_part = timeparts[j - 1]
            timepartName = time_part
            timepartValue = timepartDic[str(j - 1)].split(',')[1]

            if time_part[0] == "N":
                sql_timepart = "(time_part = '" + time_part + "' or time_part = 'Day') "
            else:
                sql_timepart = "time_part = '" + time_part + "' "

        # 根据time_part，设定日期(00:00-夜班下班点：日期为前一天)
        # 夜班下班时间取得
        closeTime = timepartDic[str(len(timeparts))].split(',')[1].split('-')[1]
        if times < closeTime and times >= "00:00":
            process_at = yesterday

        # 各个line的first processid的取得
        lineOfFirstPro = models_common.get_lineFirstProcess(model_name, process_at,lineNum)   #lineNum切换
        if lineOfFirstPro == 101 or lineOfFirstPro == 102:
            return lineOfFirstPro
        # input
        result_inputQuantity = get_inputQuantity_line(model_name, process_at, sql_timepart,lineNum) #lineNum切换
        if result_inputQuantity == 101 or result_inputQuantity == 102:
            return result_inputQuantity
        # output
        result_outputQuantity = get_outputQuantity_line(model_name, process_at, sql_timepart, lineNum) #lineNum切换
        if result_outputQuantity == 101 or result_outputQuantity == 102:
            return result_outputQuantity
        # ng
        result_ngQuantity = get_ngQuantity_line(model_name, process_at, sql_timepart, lineNum) #lineNum切换
        if result_ngQuantity == 101 or result_ngQuantity == 102:
            return result_ngQuantity
        # get assy
        assyArr = models_common.get_allAssy(model_name)
        if assyArr == 101 or assyArr == 102:
            return assyArr

        # 给key为整数的字典assyDic_int赋值
        for key in assyDic:
            assyDic_int[int(key)] = assyDic[key]
        # 字典排序
        sorted(assyDic_int.keys())

        fpy_sub_formula = formulaDic["Assembly Yield(sub+main)"]
        assembly_yield_sub_formula = formulaDic["Assy Yield(main)"]
        fpy_formula = formulaDic["FPY(sub+main)"]
        assembly_yield_formula = formulaDic["FPY(main)"]
        # 将Assembly Yield(sub+main)的计算公式存放到字典
        for i in range(len(fpy_sub_formula)):
            fpy_sub_formula_dic[i] = fpy_sub_formula[i].split(',')

        for row in lineOfFirstPro:
            flag = True
            for inputrow in result_inputQuantity:
                if row['line_cd'] == inputrow['line_cd'] and row['assy_text'] == inputrow['assy_text'] \
                        and row['dayornight'][0] == inputrow['dayornight'][0]:
                    flag = False
            if flag:
                result_inputQuantity.append({"line_cd":row['line_cd'],"assy_text":row['assy_text'], "process_id":row['process_id'],"first_ok_quantity":0,"first_ng_quantity":0,"dayornight":row['dayornight'],"input_quantity":0,})

        # outputQuantity,ngQuantity合并到inputQuantity
        for inputrow in result_inputQuantity :
            output_quantity = 0
            for outputrow in result_outputQuantity :
                if operator.eq(outputrow['line_cd'], inputrow['line_cd']) and operator.eq(outputrow['assy_text'], inputrow['assy_text']) \
                        and operator.eq(outputrow['dayornight'], inputrow['dayornight']):
                    output_quantity = outputrow['output_quantity']
                    break
            inputrow["output_quantity"] = output_quantity
            ng_quantity = 0
            for ngrow in result_ngQuantity :
                if operator.eq(ngrow['line_cd'], inputrow['line_cd']) and operator.eq(ngrow['assy_text'], inputrow['assy_text']) \
                        and operator.eq(ngrow['dayornight'], inputrow['dayornight']):
                    ng_quantity = ngrow['ng_quantity']
                    break
            inputrow["ng_quantity"] = ng_quantity

            if inputrow["input_quantity"] > 0:
                inputrow["y1"] = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
            else:
                inputrow["y1"] = 0
            if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                inputrow["y2"] = inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
            else:
                inputrow["y2"] = 0

        cur = connections[model_name].cursor()
        cur.execute("SELECT DISTINCT\
                        line_cd,\
                        m_assy.assy_text \
                    FROM\
                      m_assy\
                        INNER JOIN m_work ON m_work.assy_text = m_assy.assy_text \
                    ORDER BY line_cd,m_assy.assy_text")
        rows = cur.fetchall()
        last_line = ''
        lineArr.append("Config Test SW")
        dateArr.append("Production Date")
        dayNightArr.append("Shift")
        temp = process_at.split('-')
        date = temp[1] + "/" + temp[2]
        for row in rows:
            if operator.eq(row[0], last_line) == False:
                lineArr.append(row[0])
                lineArr_temp.append(row[0])
                dateArr.append(date)
                dateArr.append(date)
                dayNightArr.append("Day")
                dayNightArr.append("Night")
                if time_part == "":
                    timepartArr.append(time_part)
                    timepartArr.append(time_part)
                elif time_part[0] == 'D':
                    timepartArr.append(time_part)
                    timepartArr.append("Night")
                else:
                    timepartArr.append("Day")
                    timepartArr.append(time_part)
                last_line = row[0]
                lines_hid.append(row[0])
                lines_hid.append(row[0])

        lineArr.append("All Line")
        dateArr.append(date)
        dayNightArr.append("")
        header_data.append(lineArr)
        header_data.append(dateArr)
        header_data.append(dayNightArr)
        lines_hid.append("all")

        # FPY(sub+main)等的计算
        y1_fpy_sub_data = ["Assembly Yield1(sub+main)"]
        y2_fpy_sub_data = ["Assembly Yield2(sub+main)"]
        y1_assembly_yield_sub_data = ["Assy Yield(main)"]
        y1_fpy_data = ["FPY(sub+main)"]
        y1_assembly_yield_data = ["FPY(main)"]

        assy_len = len(assyDic)
        for line in lineArr_temp:
            y1_day = {}
            y2_day = {}
            y1_night = {}
            y2_night = {}
            y1_day_temp = {}
            y2_day_temp = {}
            y1_night_temp = {}
            y2_night_temp = {}
            for inputrow in result_inputQuantity:
                if operator.eq(inputrow['line_cd'], line) == False:
                    continue

                for key in assyDic:
                    if operator.eq(inputrow['assy_text'], assyDic[key]):
                        if operator.eq(inputrow['dayornight'][0], 'D'):
                            if inputrow['y1'] == float(0):
                                y1_day[int(key)] = float(1)
                                y1_day_temp[int(key)] = 'NP'
                            else:
                                y1_day[int(key)] = inputrow['y1']
                                y1_day_temp[int(key)] = inputrow['y1']
                            if inputrow['y2'] == float(0):
                                y2_day[int(key)] = float(1)
                                y2_day_temp[int(key)] = 'NP'
                            else:
                                y2_day[int(key)] = inputrow['y2']
                                y2_day_temp[int(key)] = inputrow['y2']
                        if operator.eq(inputrow['dayornight'][0], 'N'):
                            if inputrow['y1'] == float(0):
                                y1_night[int(key)] = float(1)
                                y1_night_temp[int(key)] = 'NP'
                            else:
                                y1_night[int(key)] = inputrow['y1']
                                y1_night_temp[int(key)] = inputrow['y1']
                            if inputrow['y2'] == float(0):
                                y2_night[int(key)] = float(1)
                                y2_night_temp[int(key)] = 'NP'
                            else:
                                y2_night[int(key)] = inputrow['y2']
                                y2_night_temp[int(key)] = inputrow['y2']
                        break
            # 字典排序
            sorted(y1_day.keys())
            sorted(y1_night.keys())
            sorted(y2_day.keys())
            sorted(y2_night.keys())
            sorted(y1_day_temp.keys())
            sorted(y1_night_temp.keys())
            sorted(y2_day_temp.keys())
            sorted(y2_night_temp.keys())
            index = 0
            # y1,y2不存在的情况，默认设为0.00
            while index < assy_len:
                if index not in y1_day.keys():
                    y1_day[index] = float(1)
                    y1_day_temp[index] = 'NP'
                if index not in y1_night.keys():
                    y1_night[index] = float(1)
                    y1_night_temp[index] = 'NP'
                if index not in y2_day.keys():
                    y2_day[index] = float(1)
                    y2_day_temp[index] = 'NP'
                if index not in y2_night.keys():
                    y2_night[index] = float(1)
                    y2_night_temp[index] = 'NP'

                index = index + 1

            y1_day_list = []
            y1_night_list = []
            y2_day_list = []
            y2_night_list = []
            y1_day_list_temp = []
            y1_night_list_temp = []
            y2_day_list_temp = []
            y2_night_list_temp = []
            # y1,y2的值分别保存在数组中
            for key in y1_day:
                y1_day_list.append(y1_day[key])
                y2_day_list.append(y2_day[key])
                y1_day_list_temp.append(y1_day_temp[key])
                y2_day_list_temp.append(y2_day_temp[key])
            for key in y1_night:
                y1_night_list.append(y1_night[key])
                y2_night_list.append(y2_night[key])
                y1_night_list_temp.append(y1_night_temp[key])
                y2_night_list_temp.append(y2_night_temp[key])

            # 计算Assembly Yield(sub+main)
            y1_fpy_sub_day_value = models_common.get_formula_value(y1_day_list, y1_day_list_temp, fpy_sub_formula)
            y1_fpy_sub_night_value = models_common.get_formula_value(y1_night_list, y1_night_list_temp, fpy_sub_formula)
            y2_fpy_sub_day_value = models_common.get_formula_value(y2_day_list, y2_day_list_temp, fpy_sub_formula)
            y2_fpy_sub_night_value = models_common.get_formula_value(y2_night_list, y2_night_list_temp, fpy_sub_formula)
            # 计算Assy Yield(main)
            y1_assembly_yield_sub_day_value = models_common.get_formula_value(y1_day_list, y1_day_list_temp, assembly_yield_sub_formula)
            y1_assembly_yield_sub_night_value = models_common.get_formula_value(y1_night_list, y1_night_list_temp, assembly_yield_sub_formula)
            # 计算FPY(sub+main)
            y1_fpy_day_value = models_common.get_formula_value(y1_day_list, y1_day_list_temp, fpy_formula)
            y1_fpy_night_value = models_common.get_formula_value(y1_night_list, y1_night_list_temp, fpy_formula)
            # 计算FPY(main)
            y1_assembly_yield_day_value = models_common.get_formula_value(y1_day_list, y1_day_list_temp, assembly_yield_formula)
            y1_assembly_yield_night_value = models_common.get_formula_value(y1_night_list, y1_night_list_temp, assembly_yield_formula)
            # y1_fpy_sub的计算
            y1_fpy_sub_data.append("%.2f%%" % (y1_fpy_sub_day_value * 100))
            y1_fpy_sub_data.append("%.2f%%" % (y1_fpy_sub_night_value * 100))
            # y2_fpy_sub的计算
            y2_fpy_sub_data.append("%.2f%%" % (y2_fpy_sub_day_value * 100))
            y2_fpy_sub_data.append("%.2f%%" % (y2_fpy_sub_night_value * 100))
            # y1_assembly_yield_sub的计算
            y1_assembly_yield_sub_data.append("%.2f%%" % (y1_assembly_yield_sub_day_value * 100))
            y1_assembly_yield_sub_data.append("%.2f%%" % (y1_assembly_yield_sub_night_value * 100))
            # y1_fpy的计算
            y1_fpy_data.append("%.2f%%" % (y1_fpy_day_value * 100))
            y1_fpy_data.append("%.2f%%" % (y1_fpy_night_value * 100))
            # y1_assembly_yield的计算
            y1_assembly_yield_data.append("%.2f%%" % (y1_assembly_yield_day_value * 100))
            y1_assembly_yield_data.append("%.2f%%" % (y1_assembly_yield_night_value * 100))

        img_path = models_common.get_config("img_path")
        result_allLine = []
        result_assy = []
        # 各assy的内容的取得和追加
        for assy in assyArr:
            assy_data = []
            input_data = ["Input"]
            input_data_int = []
            output_data = ["Output"]
            output_data_int = []
            ng_data = ["NG"]
            ng_data_int = []
            yield_data = ["Yield2"]
            for line in lineArr_temp:
                input_day = 0
                input_night = 0
                output_day = 0
                output_night = 0
                ng_day = 0
                ng_night = 0
                yield_day = "NP"
                yield_night = "NP"
                for inputrow in result_inputQuantity:
                    if operator.eq(inputrow['line_cd'], line) and operator.eq(inputrow['assy_text'], assy) \
                            and operator.eq(inputrow['dayornight'][0], 'D'):
                        input_day = int(inputrow['input_quantity'])
                        output_day = int(inputrow['output_quantity'])
                        ng_day = int(inputrow['ng_quantity'])
                        if inputrow['y2'] != 0:
                            yield_day = "%.2f%%" % (inputrow['y2'] * 100)
                    elif operator.eq(inputrow['line_cd'], line) and operator.eq(inputrow['assy_text'], assy) \
                            and operator.eq(inputrow['dayornight'][0], 'N'):
                        input_night = int(inputrow['input_quantity'])
                        output_night = int(inputrow['output_quantity'])
                        ng_night = int(inputrow['ng_quantity'])
                        if inputrow['y2'] != 0:
                            yield_night = "%.2f%%" % (inputrow['y2'] * 100)
                input_data.append(input_day)
                input_data.append(input_night)
                input_data_int.append(input_day)
                input_data_int.append(input_night)
                output_data.append(output_day)
                output_data.append(output_night)
                output_data_int.append(output_day)
                output_data_int.append(output_night)
                ng_data.append(ng_day)
                ng_data.append(ng_night)
                ng_data_int.append(ng_day)
                ng_data_int.append(ng_night)
                yield_data.append(yield_day)
                yield_data.append(yield_night)

            sums = sum(input_data_int)
            input_data.append(sums)
            sums = sum(output_data_int)
            output_data.append(sums)
            sums = sum(ng_data_int)
            ng_data.append(sums)
            if (sum(output_data_int) + sum(ng_data_int)) > 0:
                sums = "%.2f%%" % (sum(output_data_int)/((sum(output_data_int) + sum(ng_data_int))*1.0) * 100)
            else:
                sums = "NP"
            yield_data.append(sums)

            assy_data.append(input_data)
            assy_data.append(output_data)
            assy_data.append(ng_data)
            assy_data.append(yield_data)
            img_full_name = img_path + models_common.getPicture(assy)

            # 获取Target
            target = models_common.get_target(assy,model_name)
            result_assy.append({"name": assy,"target":target,"img": img_full_name,"data": assy_data, })
            result_allLine.append({"assy_text": assy,"input_quantity": sum(input_data_int),"output_quantity": sum(output_data_int),\
                                   "ng_quantity": sum(ng_data_int), })

        y1_list = []
        y1_list_temp = []
        y2_list = []
        y2_list_temp = []
        # All Line的FPY(sub+main)等的计算
        for key in assyDic_int:
            flg = False
            for row in result_allLine:
                if operator.eq(row['assy_text'], assyDic_int[key]):
                    flg = True
                    if row["input_quantity"] > 0:
                        y1_list.append(row["output_quantity"] / (row["input_quantity"] * 1.0))
                        y1_list_temp.append(row["output_quantity"] / (row["input_quantity"] * 1.0))
                    else:
                        y1_list.append(float(1))
                        y1_list_temp.append('NP')
                    if row["output_quantity"] + row["ng_quantity"] > 0:
                        y2_list.append(row["output_quantity"] / ((row["output_quantity"] + row["ng_quantity"]) * 1.0))
                        y2_list_temp.append(row["output_quantity"] / ((row["output_quantity"] + row["ng_quantity"]) * 1.0))
                    else:
                        y2_list.append(float(1))
                        y2_list_temp.append('NP')
                    break
            # 当前Assy在result_allLine里不存在的场合
            if flg == False:
                y1_list.append(float(1))
                y1_list_temp.append('NP')
                y2_list.append(float(1))
                y2_list_temp.append('NP')

        # Assembly Yield(sub+main)
        y1_fpy_sub_value = models_common.get_formula_value(y1_list, y1_list_temp, fpy_sub_formula)
        y2_fpy_sub_value = models_common.get_formula_value(y2_list, y2_list_temp, fpy_sub_formula)

        # 计算Assy Yield(main)
        y1_assembly_yield_sub_value = models_common.get_formula_value(y1_list, y1_list_temp, assembly_yield_sub_formula)
        # 计算FPY(sub+main)
        y1_fpy_value = models_common.get_formula_value(y1_list, y1_list_temp, fpy_formula)
        # 计算FPY(main)
        y1_assembly_yield_value = models_common.get_formula_value(y1_list, y1_list_temp, assembly_yield_formula)
        # y1_fpy_sub的计算
        y1_fpy_sub_data.append("%.2f%%" % (y1_fpy_sub_value * 100))
        # y2_fpy_sub的计算
        y2_fpy_sub_data.append("%.2f%%" % (y2_fpy_sub_value * 100))
        # y1_assembly_yield_sub的计算
        y1_assembly_yield_sub_data.append("%.2f%%" % (y1_assembly_yield_sub_value * 100))
        # y1_fpy的计算
        y1_fpy_data.append("%.2f%%" % (y1_fpy_value * 100))
        # y1_assembly_yield的计算
        y1_assembly_yield_data.append("%.2f%%" % (y1_assembly_yield_value * 100))

        header_data.append(y1_fpy_sub_data)
        header_data.append(y2_fpy_sub_data)
        header_data.append(y1_assembly_yield_sub_data)
        header_data.append(y1_fpy_data)
        header_data.append(y1_assembly_yield_data)

        result.append({"name": "VS", "img": "", "data": header_data, "lines": lines_hid, \
                       "timepart":timepartArr, "timepartName":timepartName, "timepartValue":timepartValue, \
                       "process_at":process_at,})
        result.extend(result_assy)
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result


# 1和2
def get_inputQuantity_line(model_name, process_at, sql_timepart,lineNum):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT\
                    first_process.line_cd,\
                    first_process.assy_text,\
                    auto_ok.process_id,\
                    auto_ok.ok_quantity AS first_ok_quantity,\
                    COALESCE(auto_ng.ng_quantity,0) AS first_ng_quantity,\
                    auto_ok.dayornight,\
                    ( ok_quantity + COALESCE(ng_quantity,0) ) AS input_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    dayornight,\
                    SUM( quantity ) AS ok_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    time_part AS dayornight,\
                    quantity \
                FROM\
                    t_1_auto_io_" + lineNum + " \
                WHERE\
                    process_at = '(process_at)' \
                  AND judge_text = 'ok' \
                 AND " + sql_timepart + " \
                    ) AS auto \
                GROUP BY\
                    line_cd,\
                    process_id,\
                    dayornight \
                    ) AS auto_ok\
                    INNER JOIN (\
                SELECT\
                    line_cd,\
                    assy_text,\
                    dayornight,\
                    MIN( process_id ) AS process_id \
                FROM\
                    (\
                SELECT\
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    time_part AS dayornight,\
                    SUM( auto2.quantity ) \
                FROM\
                    m_assy\
                    INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id \
                    AND auto2.quantity > 0 \
                    AND auto2.judge_text = 'ok' \
                    AND process_at = '(process_at)' \
                    AND " + sql_timepart + " \
                GROUP BY\
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id, \
                    dayornight\
                ORDER BY\
                    assy_text,\
                    process_id \
                    ) AS a \
                GROUP BY\
                    line_cd,\
                    assy_text, \
                    dayornight\
                    ) AS first_process ON auto_ok.process_id = first_process.process_id \
                    AND auto_ok.line_cd = first_process.line_cd\
                    AND auto_ok.dayornight = first_process.dayornight\
                    LEFT JOIN (\
                SELECT\
                    line_cd,\
                    process_id,\
                    dayornight,\
                    SUM( quantity ) AS ng_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    time_part AS dayornight,\
                    quantity \
                FROM\
                    t_1_auto_io_" + lineNum + " \
                WHERE\
                    process_at = '(process_at)' \
                    AND judge_text = 'ng' \
                    AND " + sql_timepart + " \
                    ) AS auto \
                GROUP BY\
                    line_cd,\
                    process_id,\
                    dayornight \
                    ) AS auto_ng ON auto_ng.process_id = first_process.process_id \
                    AND auto_ng.line_cd = first_process.line_cd \
                    AND auto_ng.dayornight = first_process.dayornight\
                ORDER BY first_process.line_cd,auto_ok.process_id,dayornight"
        sql = sql.replace("(process_at)", process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"line_cd":row[0],"assy_text":row[1], "process_id":row[2],"first_ok_quantity":int(row[3]),"first_ng_quantity":int(row[4]),"dayornight":row[5],"input_quantity":int(row[6]),})
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

#1和2
def get_outputQuantity_line(model_name, process_at, sql_timepart, lineNum):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT\
                    last_process.line_cd,\
                    last_process.assy_text,\
                    auto_ok.process_id,\
                    auto_ok.dayornight,\
                    auto_ok.ok_quantity AS output_quantity\
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    dayornight,\
                    SUM( quantity ) AS ok_quantity\
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    time_part AS dayornight,\
                    quantity\
                FROM\
                    t_1_auto_io_" + lineNum + "\
                WHERE\
                    process_at = '(process_at)' \
                    AND judge_text = 'ok' \
                    AND " + sql_timepart + " \
                    ) AS auto\
                GROUP BY\
                    line_cd,\
                    process_id,\
                    dayornight\
                    ) AS auto_ok\
                    INNER JOIN (\
                SELECT\
                    line_cd,\
                    assy_text,\
                  dayornight,\
                 MAX( process_id ) AS process_id\
                FROM\
                    (\
                SELECT\
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    time_part AS dayornight,\
                    SUM( auto2.quantity )\
                FROM\
                    m_assy\
                    INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id\
                    AND auto2.judge_text = 'ok' \
                    AND auto2.quantity > 0 \
                    AND process_at = '(process_at)' \
                    AND " + sql_timepart + " \
                GROUP BY\
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    dayornight\
                    ) AS a\
                GROUP BY\
                    line_cd,\
                    assy_text,\
                 dayornight\
                    ) AS last_process ON auto_ok.process_id = last_process.process_id\
                    AND auto_ok.line_cd = last_process.line_cd\
                  AND auto_ok.dayornight = last_process.dayornight\
                ORDER BY last_process.line_cd,auto_ok.process_id,dayornight"
        sql = sql.replace("(process_at)", process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"line_cd":row[0],"assy_text":row[1], "process_id":row[2],"dayornight":row[3],"output_quantity":int(row[4]),})
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

#1和2
def get_ngQuantity_line(model_name, process_at, sql_timepart, lineNum):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT\
                    line_cd,\
                    assy_text,\
                    dayornight,\
                    SUM( ng_quantity ) AS ng_quantity \
                FROM\
                    (\
                SELECT DISTINCT\
                    auto_ng.line_cd,\
                    m_assy.assy_text,\
                    auto_ng.process_id,\
                    auto_ng.dayornight,\
                    auto_ng.ng_quantity AS ng_quantity \
                FROM\
                    m_assy\
                    INNER JOIN (\
                SELECT\
                    line_cd,\
                    process_id,\
                    dayornight,\
                    SUM( quantity ) AS ng_quantity\
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    time_part AS dayornight,\
                    quantity \
                FROM\
                    t_1_auto_io_" + lineNum + " \
                WHERE\
                    process_at = '(process_at)' \
                    AND judge_text = 'ng' \
                    AND " + sql_timepart + " \
                    ) AS auto \
                GROUP BY\
                    line_cd,\
                    process_id,\
                    dayornight \
                    ) AS auto_ng ON m_assy.process_id = auto_ng.process_id\
                    ) AS main \
                GROUP BY\
                    line_cd,\
                    assy_text,\
                    dayornight \
                ORDER BY line_cd,assy_text,dayornight"
        sql = sql.replace("(process_at)", process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"line_cd":row[0],"assy_text":row[1],"dayornight":row[2], "ng_quantity":int(row[3]),})
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

# 比较时间大小
def compare_time(l_time, start_t, end_t):
    date = start_t.split(' ')[0]
    if start_t == date + ' 00:00':
        start_t = date + ' 24:00'
    if end_t == date + ' 00:00':
        end_t = date + ' 24:00'
    if start_t < end_t:
        if l_time >= start_t and l_time <= end_t:
            return True
    else:
        if l_time <= end_t and l_time <= start_t:
            return True
    return False