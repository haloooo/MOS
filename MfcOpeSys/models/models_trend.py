# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import operator
import datetime
from MfcOpeSys.models import models_common

def get_trend(model_name, start_date, end_date, object, content, type):
    process_at_list = models_common.get_periodDate(start_date, end_date)
    # typeName设定
    if type == "Y1":
        typeName = "Y1"
    elif type == "Y2":
        typeName = "Y2"
    elif type == "Input":
        typeName = "input_quantity"
    elif type == "Output":
        typeName = "output_quantity"
    else:
        typeName = "ng_quantity"
    data_zero = []
    data_NP = []
    i = 0
    while i < len(process_at_list):
        data_zero.append(0)
        data_NP.append("NP")
        i = i + 1
    try:
        if operator.eq('Line', object):
            if operator.eq('Input', type):
                # input
                lineNum="2nd"
                result_quantity = models_common.get_inputQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity

            if operator.eq('Output', type):
                # output
                result_quantity = models_common.get_outputQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity

            if operator.eq('NG', type):
                # input
                lineNum="2nd"
                result_quantity = models_common.get_inputQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity
                # ng
                result_ngQuantity = models_common.get_ngQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_ngQuantity == 101 or result_ngQuantity == 102:
                    return result_ngQuantity
                # ngQuantity合并到inputQuantity
                for inputrow in result_quantity:
                    ng_quantity = 0
                    for ngrow in result_ngQuantity:
                        if operator.eq(ngrow['assy_text'], inputrow['assy_text']) and operator.eq(\
                                ngrow['process_at'], inputrow['process_at']):
                            ng_quantity = ngrow['ng_quantity']
                            break
                    inputrow["ng_quantity"] = ng_quantity

            if operator.eq('Y1', type) or operator.eq('Y2', type):
                # input
                lineNum = "2nd"
                result_quantity = models_common.get_inputQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity
                # output
                result_outputQuantity = models_common.get_outputQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_outputQuantity == 101 or result_outputQuantity == 102:
                    return result_outputQuantity
                # ng
                result_ngQuantity = models_common.get_ngQuantity(model_name, start_date, end_date, 'All', False, content,lineNum)
                if result_ngQuantity == 101 or result_ngQuantity == 102:
                    return result_ngQuantity

                # 计算y2，合并到inputQuantity
                for inputrow in result_quantity:
                    output_quantity = 0
                    for outputrow in result_outputQuantity:
                        if operator.eq(outputrow['assy_text'], inputrow['assy_text']) and operator.eq(\
                                outputrow['process_at'], inputrow['process_at']):
                            output_quantity = outputrow['output_quantity']
                            break
                    ng_quantity = 0
                    for ngrow in result_ngQuantity:
                        if operator.eq(ngrow['assy_text'], inputrow['assy_text']) and operator.eq(\
                                ngrow['process_at'], inputrow['process_at']):
                            ng_quantity = ngrow['ng_quantity']
                            break
                    if output_quantity + ng_quantity > 0:
                        inputrow["Y2"] = output_quantity / ((output_quantity + ng_quantity) * 1.0)
                    else:
                        inputrow["Y2"] = "NP"

                    if inputrow["input_quantity"] > 0:
                        inputrow["Y1"] = output_quantity / (inputrow["input_quantity"] * 1.0)
                    else:
                        inputrow["Y1"] = "NP"

            # get assy
            objectArr = models_common.get_allAssyAndProcessId(model_name)
            if objectArr == 101 or objectArr == 102:
                return objectArr

            # sort
            result_quantity = sorted(result_quantity, key=lambda x: (x['assy_text'], x['process_at']))
        else:
            if operator.eq('Input', type):
                # input
                result_quantity = models_common.get_inputQuantity_sumOfLine(model_name, start_date, end_date, content, False)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity

                # get allLine
                result_quantity_all = models_common.get_inputQuantity_sumOfLine(model_name, start_date, end_date, content, True)
                if result_quantity_all == 101 or result_quantity_all == 102:
                    return result_quantity_all

            if operator.eq('Output', type):
                # output
                result_quantity = models_common.get_outputQuantity_sumOfLine(model_name, start_date, end_date, content, False)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity

                # get allLine
                result_quantity_all = models_common.get_outputQuantity_sumOfLine(model_name, start_date, end_date, content, True)
                if result_quantity_all == 101 or result_quantity_all == 102:
                    return result_quantity_all

            if operator.eq('NG', type):
                # ng
                result_quantity = models_common.get_ngQuantity_sumOfLine(model_name, start_date, end_date, content, False)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity

                # get allLine
                result_quantity_all = models_common.get_ngQuantity_sumOfLine(model_name, start_date, end_date, content, True)
                if result_quantity_all == 101 or result_quantity_all == 102:
                    return result_quantity_all

            if operator.eq('Y1', type) or operator.eq('Y2', type):
                # input
                result_quantity = models_common.get_inputQuantity_sumOfLine(model_name, start_date, end_date, content, False)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity
                # output
                result_outputQuantity = models_common.get_outputQuantity_sumOfLine(model_name, start_date, end_date, content, False)
                if result_outputQuantity == 101 or result_outputQuantity == 102:
                    return result_outputQuantity
                # ng
                result_ngQuantity = models_common.get_ngQuantity_sumOfLine(model_name, start_date, end_date, content, False)
                if result_ngQuantity == 101 or result_ngQuantity == 102:
                    return result_ngQuantity

                # 计算y2，合并到inputQuantity
                for inputrow in result_quantity:
                    output_quantity = 0
                    for outputrow in result_outputQuantity:
                        if operator.eq(outputrow['line_cd'], inputrow['line_cd']) and operator.eq(\
                                outputrow['process_at'], inputrow['process_at']):
                            output_quantity = outputrow['output_quantity']
                            break
                    ng_quantity = 0
                    for ngrow in result_ngQuantity:
                        if operator.eq(ngrow['line_cd'], inputrow['line_cd']) and operator.eq(\
                                ngrow['process_at'], inputrow['process_at']):
                            ng_quantity = ngrow['ng_quantity']
                            break
                    if output_quantity + ng_quantity > 0:
                        inputrow["Y2"] = output_quantity / ((output_quantity + ng_quantity) * 1.0)
                    else:
                        inputrow["Y2"] = "NP"

                    if inputrow["input_quantity"] > 0:
                        inputrow["Y1"] = output_quantity / (inputrow["input_quantity"] * 1.0)
                    else:
                        inputrow["Y1"] = "NP"

            # get line
            objectArr = models_common.get_allLines(model_name)
            if objectArr == 101 or objectArr == 102:
                return objectArr

        # 设定目标json数据
        result = models_common.setDataList(process_at_list, result_quantity, objectArr, model_name, object, content, typeName)

        # sort
        if operator.eq('Line', object):
            result = sorted(result, key=lambda x: (x['process_id']))
        else:
            result = sorted(result, key=lambda x: (x['process']))

        # All Line追加
        if object == 'Assy':
            if type != 'Y1' and type != 'Y2':
                if len(result_quantity_all) == 0:
                    result_all = {"process": "All Line", "data": data_zero}
                else:
                    result_all = models_common.supplementZero("All Line", result_quantity_all, process_at_list, 'trend')
            else:
                # get allLine
                if len(result_quantity) == 0:
                    if type == 'Y2':
                        # 获取TARGET
                        target = models_common.get_target(content, model_name)
                        result_all = {'process': 'All Line', 'data': data_zero, 'target': target,}
                    else:
                        result_all = {'process': 'All Line', 'data': data_zero, }
                else:
                    data = models_common.getAvg_allLine(result, process_at_list)
                    if type == 'Y2':
                        # 获取TARGET
                        target = models_common.get_target(content, model_name)
                        result_all = {'process': 'All Line', 'data': data, 'target': target,}
                    else:
                        result_all = {'process': 'All Line', 'data': data, }
            result.append(result_all)

        # 计算公式项追加
        if object == 'Line' and (type == 'Y1' or type == 'Y2'):
            database_list = models_common.get_config("database")
            formulaDic = {}
            assyDic = {}
            assyDic_int = {}
            for row in database_list:
                if operator.eq(row['MODEL'], model_name):
                    # 从配置文件里取得ASSY
                    assyDic = row['ASSY']
                    # 从配置文件里取得FORMULA
                    formulaDic = row['FORMULA_TREND']
                    break
            # 给key为整数的字典assyDic_int赋值
            for key in assyDic:
                assyDic_int[int(key)] = assyDic[key]
            # 字典排序
            sorted(assyDic_int.keys())

            # fpy计算公式的取得
            fpy_formula = formulaDic["FPY(main)"]
            # FPY(sub+main)计算公式的取得
            tester_yield_formula = formulaDic["FPY(sub+main)"]
            # Assembly Yield(sub+main)计算公式的取得
            assembly_yield_formula = formulaDic["Assembly Yield(sub+main)"]

            # 按配置文件里ASSY的顺序排列result
            result_temp = []
            for key in assyDic_int:
                flg = False
                for row in result:
                    if operator.eq(row['process'], assyDic_int[key]):
                        flg = True
                        result_temp.append(row)
                        break
                # 当前config里设定的Assy在result里不存在的场合
                if flg == False:
                    # 获取TARGET
                    target = models_common.get_target(assyDic_int[key], model_name)
                    result_temp.append({'process': assyDic_int[key], 'data': data_NP, 'target': target, })

            assembly_yield_list = []
            tester_yield_list = []
            fpy_list = []
            for i in range(len(process_at_list)):
                y2_list = []
                y2_list_temp = []
                for row in result_temp:
                    yield2 = row['data'][i]
                    y2_list_temp.append(yield2)
                    if operator.eq(yield2, 'NP'):
                        yield2 = float(1)
                    y2_list.append(yield2)

                # 计算y2_FPY(main)
                y2_fpy_value = models_common.get_formula_value(y2_list, y2_list_temp, fpy_formula)
                # 计算y2_FPY(sub+main)
                y2_tester_yield_value = models_common.get_formula_value(y2_list, y2_list_temp, tester_yield_formula)
                # 计算y2_Assembly Yield(sub+main)
                y2_assembly_yield_value = models_common.get_formula_value(y2_list, y2_list_temp, assembly_yield_formula)
                # 将当前计算值添加到list
                assembly_yield_list.append(y2_assembly_yield_value)
                tester_yield_list.append(y2_tester_yield_value)
                fpy_list.append(y2_fpy_value)

            # 获取TARGET
            assembly_yield_target = models_common.get_target('Assembly Yield(sub+main)', model_name)
            tester_yield_target = models_common.get_target('Assembly Yield(sub+main)', model_name)
            fpy_target = models_common.get_target('FPY(main)', model_name)
            result.append({'process': 'Assembly Yield(sub+main)', 'data':assembly_yield_list , 'target':assembly_yield_target, })
            result.append({'process': 'FPY(sub+main)', 'data': tester_yield_list, 'target':tester_yield_target, })
            result.append({'process': 'FPY(main)', 'data': fpy_list, 'target':fpy_target, })

        if type == 'Y1' or type == 'Y2':
            # 转成百分比
            for row in result:
                i = 0
                for value in row['data']:
                    if value != 'NP':
                        row['data'][i] = "%.2f%%" % (value * 100)
                    i = i + 1

    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result