# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import operator
import datetime
from MfcOpeSys.models import models_common

def initAssyData(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT process_id,assy_text,process_cd,process_text FROM m_assy ORDER BY process_id")
        rows = cur.fetchall()
        for row in rows:
            result.append({'process_id':row[0],'process_cd':row[2],'process_text':row[3],'assy_text':row[1]})
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def update_assy(model_name,process_id,assy_text):
    try:
        cur = connections[model_name].cursor()
        SQL = 'UPDATE m_assy SET assy_text = %s WHERE process_id = %s'
        cur.execute(SQL,(assy_text,process_id,))
        connections[model_name].commit
        cur.close()
        result = {'status': 'success'}
    except BaseException as exp:
        print(exp)
        result = {'status': 'fail'}
    connections[model_name].close()
    return result

#def search_AdverseRate(model_name, from_process_at, to_process_at):
    #    process_at_list = models_common.get_periodDate(from_process_at, to_process_at)
    #    result = []
    #  # get assy
    #   assyArr = models_common.get_allAssy(model_name)
    #   # output
    #   result_outputQuantity = models_common.get_outputQuantity(model_name, from_process_at, to_process_at)
    #   # ng
    #  result_ngQuantity = models_common.get_ngQuantity(model_name, from_process_at, to_process_at)
    #  try:
    #     # ngQuantity合并到outputQuantity
    #      for outputrow in result_outputQuantity:
    #        ng_quantity = 0
    #          for ngrow in result_ngQuantity:
    #               if operator.eq(ngrow['assy_text'],outputrow['assy_text']) \
    #                       and operator.eq(ngrow['process_at'], outputrow['process_at']):
    #                   outputrow["ng_quantity"] = ngrow['ng_quantity']
    #                   ng_quantity = ngrow['ng_quantity']
    #                  break
    #
    #          if (outputrow["output_quantity"] + ng_quantity) > 0:
    #              y2 = str(outputrow["output_quantity"] / ((outputrow["output_quantity"] + ng_quantity) * 1.0))
    #              y2 = y2[0:4]
    #              outputrow["y2"] = float(y2)
    #          else:
    #              outputrow["y2"] = 0.00
    #      result = setDataList(process_at_list, result_outputQuantity, 'y2', assyArr)
    #   except BaseException as exp:
    #        print(exp)
    #   connections[model_name].close()
#   return result

#def search_Ng(model_name, from_process_at, to_process_at):
    #    process_at_list = models_common.get_periodDate(from_process_at, to_process_at)
    #   result = []
    #   # get assy
    #   assyArr = models_common.get_allAssy(model_name)
    #    # ng
    #   result_ngQuantity = models_common.get_ngQuantity(model_name, from_process_at, to_process_at)
    #   try:
    #       result = setDataList(process_at_list, result_ngQuantity, 'ng', assyArr)
    #   except BaseException as exp:
    #       print(exp)
    #   connections[model_name].close()
#    return result

#def search_Ok(model_name, from_process_at, to_process_at):
    #    process_at_list = models_common.get_periodDate(from_process_at, to_process_at)
    #   result = []
    #   # get assy
    #  assyArr = models_common.get_allAssy(model_name)
    #  # output
    #  result_outputQuantity = models_common.get_outputQuantity(model_name, from_process_at, to_process_at)
    #  try:
    #       result = setDataList(process_at_list, result_outputQuantity, 'ok', assyArr)
    #   except BaseException as exp:
    #       print(exp)
    #   connections[model_name].close()
#   return result

#def setDataList(process_at_list, result_quantity, type, assyArr):
    #    result = []
    #    last_assy_text = ""
    #    last_process_at = ""
    #    data = []
    #   data_zero = []
    #    index = 0
    #    end_date = datetime.datetime.strptime(process_at_list[-1], "%Y-%m-%d")
    #    i = 0
    #   while i < len(process_at_list):
    #       data_zero.append(0)
    #       i = i + 1

    #   for row in result_quantity:
    #       begin_date = datetime.datetime.strptime(process_at_list[0], "%Y-%m-%d")
    #       current_date = datetime.datetime.strptime(row['process_at'], "%Y-%m-%d")
    #        if operator.eq(row['assy_text'], last_assy_text) == False:
    #           # 不是第一条数据的场合
    #            if index != 0:
    #               # data数组最后的补位处理
    #              while last_process_at < end_date:
    #                  data.append(0)
    #                  last_process_at += datetime.timedelta(days=1)
    #              result.append({'name': last_assy_text, 'data': data, })
    #              data = []
    #              # data数组最前端的补位处理
    #              while begin_date < current_date:
    #                  data.append(0)
    #                  begin_date += datetime.timedelta(days=1)
    #              if operator.eq('y2', type):
    #                  data.append(row['y2'])
    #              elif operator.eq('ng', type):
    #                  data.append(row['ng_quantity'])
    #               else:
    #                   data.append(row['output_quantity'])
    #           else:
    #              # data数组最前端的补位处理
    #              while begin_date < current_date:
    #                  data.append(0)
    #                   begin_date += datetime.timedelta(days=1)
    #               if operator.eq('y2', type):
    #                   data.append(row['y2'])
    #                elif operator.eq('ng', type):
    #                   data.append(row['ng_quantity'])
    #              else:
    #                 data.append(row['output_quantity'])

    #          last_assy_text = row['assy_text']
    #      else:
    #          # data数组中间的补位处理
    #          last_process_at += datetime.timedelta(days=1)
    #         while last_process_at < current_date:
    #              data.append(0)
    #             last_process_at += datetime.timedelta(days=1)
    #         if operator.eq('y2', type):
    #             data.append(row['y2'])
    #         elif operator.eq('ng', type):
    #             data.append(row['ng_quantity'])
    #         else:
    #              data.append(row['output_quantity'])
    #     index = index + 1
    #      last_process_at = current_date

    #  if len(result_quantity) > 0:
    #     # 最后一条的处理（追加到result）
    #     while last_process_at < end_date:
    #         data.append(0)
    #         last_process_at += datetime.timedelta(days=1)
    #     result.append({'name': last_assy_text, 'data': data, })

    #   for value in assyArr:
    #       flg = False
    #       for row in result_quantity:
    #           if operator.eq(row['assy_text'], value):
    #              flg = True
    #              break
    #      if flg == False:
    #          result.append({'name': value, 'data': data_zero, })

#   return result
#
def setDataList(process_at_list, result_quantity, type, objectArr, object, concent, getSum):
    result = []
    last_keyName = ""
    last_process_id = ""
    last_process_at = ""
    data = []
    data_zero = []
    index = 0
    end_date = datetime.datetime.strptime(process_at_list[-1], "%Y-%m-%d")
    i = 0
    while i < len(process_at_list):
        if operator.eq('y1', type) or operator.eq('y2', type):
            data_zero.append(0.00)
        else:
            data_zero.append(0)
        i = i + 1
    key = ''
    if operator.eq('Assy', object) or operator.eq('Process', object) or \
            (operator.eq('Line', concent) and operator.eq('Total', object)):
        key = 'line_cd'
    if operator.eq('Assy', concent):
        key = 'assy_text'
    if operator.eq('Process', concent):
        key = 'process_cd'
    if getSum:
        key = 'process_at'

    if getSum == False:
        for row in result_quantity:
            begin_date = datetime.datetime.strptime(process_at_list[0], "%Y-%m-%d")
            current_date = datetime.datetime.strptime(row['process_at'], "%Y-%m-%d")
            if operator.eq(row[key], last_keyName) == False:
                # 不是第一条数据的场合
                if index != 0:
                    # data数组最后的补位处理
                    while last_process_at < end_date:
                        if operator.eq('y1', type) or operator.eq('y2', type):
                            data.append(0.00)
                        else:
                            data.append(0)
                        last_process_at += datetime.timedelta(days=1)
                    if operator.eq('Assy', concent) or operator.eq('Process', concent):
                        result.append({'name': last_keyName, 'data': data, 'process_id': last_process_id,})
                    else:
                        result.append({'name': last_keyName, 'data': data, })
                    data = []
                    # data数组最前端的补位处理
                    while begin_date < current_date:
                        if operator.eq('y1', type) or operator.eq('y2', type):
                            data.append(0.00)
                        else:
                            data.append(0)
                        begin_date += datetime.timedelta(days=1)
                    # 根据type设定data
                    data = setDataByType(row, data, type)

                else:
                    # data数组最前端的补位处理
                    while begin_date < current_date:
                        if operator.eq('y1', type) or operator.eq('y2', type):
                            data.append(0.00)
                        else:
                            data.append(0)
                        begin_date += datetime.timedelta(days=1)
                    # 根据type设定data
                    data = setDataByType(row, data, type)

                last_keyName = row[key]
                if operator.eq('Assy', concent)  or operator.eq('Process', concent):
                    last_process_id = row['process_id']
            else:
                # data数组中间的补位处理
                last_process_at += datetime.timedelta(days=1)
                while last_process_at < current_date:
                    if operator.eq('y1', type) or operator.eq('y2', type):
                        data.append(0.00)
                    else:
                        data.append(0)
                    last_process_at += datetime.timedelta(days=1)
                # 根据type设定data
                data = setDataByType(row, data, type)

            index = index + 1
            last_process_at = current_date

    else:
        for row in result_quantity:
            begin_date = datetime.datetime.strptime(process_at_list[0], "%Y-%m-%d")
            current_date = datetime.datetime.strptime(row['process_at'], "%Y-%m-%d")
            # 不是第一条数据的场合
            if index != 0:
                # data数组中间的补位处理
                last_process_at += datetime.timedelta(days=1)
                while last_process_at < current_date:
                    data.append(0)
                    last_process_at += datetime.timedelta(days=1)
                # 根据object,concent,type设定data
                data = setDataByObjAndConcentAndType(row, data, object, concent, type)
            else:
                # data数组最前端的补位处理
                while begin_date < current_date:
                    data.append(0)
                    begin_date += datetime.timedelta(days=1)

                # 根据object,concent,type设定data
                data = setDataByObjAndConcentAndType(row, data, object, concent, type)

            index = index + 1
            last_process_at = current_date

    if len(result_quantity) > 0:
        # 最后一条的处理（追加到result）
        while last_process_at < end_date:
            if operator.eq('y1', type) or operator.eq('y2', type):
                data.append(0.00)
            else:
                data.append(0)
            last_process_at += datetime.timedelta(days=1)
        if getSum == False:
            if operator.eq('Assy', concent) or operator.eq('Process', concent):
                result.append({'name': last_keyName, 'data': data, 'process_id': last_process_id,})
            else:
                result.append({'name': last_keyName, 'data': data, })
        else:
            if operator.eq('Assy', object) or operator.eq('Process', object) or \
                    (operator.eq('Line', concent) and operator.eq('Total', object)):
                result.append({'name': 'All Line', 'data': data, })
            elif operator.eq('Assy', concent):
                result.append({'name': 'All Assy', 'data': data,})
            elif operator.eq('Process', concent):
                result.append({'name': 'All Process', 'data': data,})
    else:
        if getSum:
            if operator.eq('Assy', object) or operator.eq('Process', object) or \
                    (operator.eq('Line', concent) and operator.eq('Total', object)):
                result.append({'name': 'All Line', 'data': data_zero, })
            elif operator.eq('Assy', concent):
                result.append({'name': 'All Assy', 'data': data_zero,})
            elif operator.eq('Process', concent):
                result.append({'name': 'All Process', 'data': data_zero,})

    if getSum == False:
        if operator.eq('Assy', concent) or operator.eq('Process', concent):
            for objectArrRow in objectArr:
                flg = False
                for row in result_quantity:
                    if operator.eq('Assy', concent):
                        if operator.eq(row[key], objectArrRow['assy_text']):
                            flg = True
                            break
                    else:
                        if operator.eq(row[key], objectArrRow['process_cd']):
                            flg = True
                            break
                if flg == False:
                    if operator.eq('Assy', concent):
                        result.append({'name': objectArrRow['assy_text'], 'data': data_zero,'process_id': objectArrRow['process_id'], })
                    else:
                        result.append({'name': objectArrRow['process_cd'], 'data': data_zero,'process_id': objectArrRow['process_id'], })
        else:
            for value in objectArr:
                flg = False
                for row in result_quantity:
                    if operator.eq(row[key], value):
                        flg = True
                        break
                if flg == False:
                    result.append({'name': value, 'data': data_zero,})
    return result

def setDataByType(row, data, type):
    data_new = data
    if operator.eq('y2', type):
        data_new.append(row['y2'])
    elif operator.eq('y1', type):
        data_new.append(row['y1'])
    elif operator.eq('ng', type):
        data_new.append(row['ng_quantity'])
    elif operator.eq('input', type):
        data_new.append(row['input_quantity'])
    else:
        data_new.append(row['output_quantity'])
    return data_new

def setDataByObjAndConcentAndType(row, data, object, concent, type):
    data_new = data
    if operator.eq('Process', object) or operator.eq('Process', concent):
        if operator.eq('input', type):
            data_new.append(row['sum_input_quantity'])
        elif operator.eq('ng', type):
            data_new.append(row['sum_ng_quantity'])
        elif operator.eq('output', type):
            data_new.append(row['sum_output_quantity'])
    else:
        data_new.append(row['sum_quantity'])
    return data_new

def get_select_content(model_name,object):
    try:
        result = []
        cur = connections[model_name].cursor()
        if(object == 'Assy'):
            SQL = 'SELECT DISTINCT assy_text,min(process_id) as a FROM m_assy GROUP BY assy_text ORDER BY a;'
            cur.execute(SQL)
            rows = cur.fetchall()
            for row in rows:
                result.append(row[0])
        elif(object == 'Process'):
            SQL = 'SELECT DISTINCT process_cd,min(process_id) as a FROM m_assy GROUP BY process_cd ORDER BY a;'
            cur.execute(SQL)
            rows = cur.fetchall()
            for row in rows:
                result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def search_chart(model_name,start,end,object,content,type,lineNum):
    process_at_list = models_common.get_periodDate(start, end)
    result = []
    try:
        # get line
        lineArr = models_common.get_allLines(model_name)
        if lineArr == 101 or lineArr == 102:
            return lineArr
        if operator.eq('Total', object):
            if operator.eq('Line', content):
                if operator.eq('Input', type):
                    # input
                    result_inputQuantity = models_common.get_inputQuantity_sumOfLine(model_name, start, end, '', False)
                    if result_inputQuantity == 101 or result_inputQuantity == 102:
                        return result_inputQuantity
                    result = setDataList(process_at_list, result_inputQuantity, 'input', lineArr, 'Total', 'Line', False)
                    # sort
                    result = sorted(result, key=lambda x: (x['name']))
                    # get allLine
                    result_inputQuantity_allLine = models_common.get_inputQuantity_sumOfLine(model_name, start, end, '', True)
                    if result_inputQuantity_allLine == 101 or result_inputQuantity_allLine == 102:
                        return result_inputQuantity_allLine
                    result_sum = setDataList(process_at_list, result_inputQuantity_allLine, 'input', [], 'Total', 'Line', True)
                    result.append(result_sum[0])

                if operator.eq('Output', type):
                    # output
                    result_outputQuantity = models_common.get_outputQuantity_sumOfLine(model_name, start, end, '', False)
                    if result_outputQuantity == 101 or result_outputQuantity == 102:
                        return result_outputQuantity
                    result = setDataList(process_at_list, result_outputQuantity, 'output', lineArr, 'Total', 'Line', False)
                    # sort
                    result = sorted(result, key=lambda x: (x['name']))
                    # get allLine
                    result_outputQuantity_allLine = models_common.get_outputQuantity_sumOfLine(model_name, start, end, '', True)
                    if result_outputQuantity_allLine == 101 or result_outputQuantity_allLine == 102:
                        return result_outputQuantity_allLine
                    result_sum = setDataList(process_at_list, result_outputQuantity_allLine, 'output', [], 'Total', 'Line', True)
                    result.append(result_sum[0])

                if operator.eq('NG', type):
                    # NG
                    result_ngQuantity = models_common.get_ngQuantity_sumOfLine(model_name, start, end, '', False)
                    if result_ngQuantity == 101 or result_ngQuantity == 102:
                        return result_ngQuantity
                    result = setDataList(process_at_list, result_ngQuantity, 'ng', lineArr, 'Total', 'Line', False)
                    # sort
                    result = sorted(result, key=lambda x: (x['name']))
                    # get allLine
                    result_ngQuantity_allLine = models_common.get_ngQuantity_sumOfLine(model_name, start, end, '', True)
                    if result_ngQuantity_allLine == 101 or result_ngQuantity_allLine == 102:
                        return result_ngQuantity_allLine
                    result_sum = setDataList(process_at_list, result_ngQuantity_allLine, 'ng', [], 'Total', 'Line', True)
                    result.append(result_sum[0])

                if operator.eq('Y1', type) or operator.eq('Y2', type):
                    # Y1
                    result_inputQuantity = models_common.get_inputQuantity_sumOfLine(model_name, start, end, '', False)
                    if result_inputQuantity == 101 or result_inputQuantity == 102:
                        return result_inputQuantity
                    result_outputQuantity = models_common.get_outputQuantity_sumOfLine(model_name, start, end, '', False)
                    if result_outputQuantity == 101 or result_outputQuantity == 102:
                        return result_outputQuantity
                    result_ngQuantity = models_common.get_ngQuantity_sumOfLine(model_name, start, end, '', False)
                    if result_ngQuantity == 101 or result_ngQuantity == 102:
                        return result_ngQuantity
                    # outputQuantity,ngQuantity合并到inputQuantity
                    for inputrow in result_inputQuantity:
                        for outputrow in result_outputQuantity:
                            if operator.eq(outputrow['line_cd'], inputrow['line_cd']) and operator.eq(outputrow['process_at'], inputrow['process_at']):
                                inputrow["output_quantity"] = outputrow['output_quantity']
                                break
                        ng_quantity = 0
                        for ngrow in result_ngQuantity:
                            if operator.eq(ngrow['line_cd'], inputrow['line_cd']) and operator.eq(ngrow['process_at'],inputrow['process_at']):
                                ng_quantity = ngrow['ng_quantity']
                                break
                        inputrow["ng_quantity"] = ng_quantity

                        if inputrow["input_quantity"] > 0:
                            #y1 = str(inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0))
                            #y1 = y1[0:4]
                            #y1 = "%.2f" % (inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0) * 100)
                            y1 = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
                            inputrow["y1"] = float(y1)
                        else:
                            inputrow["y1"] = 0.00
                        if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                            #y2 = "%.2f" % (inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0) * 100)
                            y2 = inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
                            inputrow["y2"] = float(y2)
                        else:
                            inputrow["y2"] = 0.00

                    if operator.eq('Y1', type):
                        result = setDataList(process_at_list, result_inputQuantity, 'y1', lineArr, 'Total', 'Line', False)
                    else:
                        result = setDataList(process_at_list, result_inputQuantity, 'y2', lineArr, 'Total', 'Line', False)
                    # sort
                    result = sorted(result, key=lambda x: (x['name']))
                    # get allLine
                    data = models_common.getAvg_allLine(result, process_at_list)
                    result.append({'name': 'All Line', 'data': data, })
            if operator.eq('Assy', content):
                # get assy
                assyArr = models_common.get_allAssyAndProcessId(model_name)
                if assyArr == 101 or assyArr == 102:
                    return assyArr
                if operator.eq('Input', type):
                    # get input
                    result_inputQuantity = models_common.get_inputQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_inputQuantity == 101 or result_inputQuantity == 102:
                        return result_inputQuantity
                    # sort
                    result_inputQuantity = sorted(result_inputQuantity, key=lambda x: (x['assy_text'], x['process_at']))
                    result = setDataList(process_at_list, result_inputQuantity, 'input', assyArr, 'Total', 'Assy', False)
                    # get allAssy
                    result_inputQuantity_allLine = models_common.get_inputQuantity(model_name, start, end, 'All', True, '',lineNum)
                    if result_inputQuantity_allLine == 101 or result_inputQuantity_allLine == 102:
                        return result_inputQuantity_allLine
                    result_sum = setDataList(process_at_list, result_inputQuantity_allLine, 'input', [], 'Total', 'Assy', True)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    result.append(result_sum[0])
                if operator.eq('Output', type):
                    # output
                    result_outputQuantity = models_common.get_outputQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_outputQuantity == 101 or result_outputQuantity == 102:
                        return result_outputQuantity
                    # sort
                    result_outputQuantity = sorted(result_outputQuantity, key=lambda x: (x['assy_text'], x['process_at']))
                    result = setDataList(process_at_list, result_outputQuantity, 'output', assyArr, 'Total', 'Assy', False)
                    # get allAssy
                    result_outputQuantity_allLine = models_common.get_outputQuantity(model_name, start, end, 'All', True, '',lineNum)
                    if result_outputQuantity_allLine == 101 or result_outputQuantity_allLine == 102:
                        return result_outputQuantity_allLine
                    result_sum = setDataList(process_at_list, result_outputQuantity_allLine, 'output', [], 'Total', 'Assy', True)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    result.append(result_sum[0])
                if operator.eq('NG', type):
                    result_inputQuantity = models_common.get_inputQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_inputQuantity == 101 or result_inputQuantity == 102:
                        return result_inputQuantity
                    result_ngQuantity = models_common.get_ngQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_ngQuantity == 101 or result_ngQuantity == 102:
                        return result_ngQuantity
                    # ngQuantity合并到inputQuantity
                    for inputrow in result_inputQuantity:
                        ng_quantity = 0
                        for ngrow in result_ngQuantity:
                            if operator.eq(ngrow['assy_text'], inputrow['assy_text']) and operator.eq(
                                    ngrow['process_at'], inputrow['process_at']):
                                ng_quantity = ngrow['ng_quantity']
                                break
                        inputrow["ng_quantity"] = ng_quantity

                    # sort:assy_text,process_at
                    result_inputQuantity = sorted(result_inputQuantity, key=lambda x: (x['assy_text'], x['process_at']))
                    result = setDataList(process_at_list, result_inputQuantity, 'ng', assyArr, 'Total', 'Assy', False)
                    # get allAssy
                    result_ngQuantity_allLine = models_common.get_ngQuantity(model_name, start, end, 'All', True, '',lineNum)
                    if result_ngQuantity_allLine == 101 or result_ngQuantity_allLine == 102:
                        return result_ngQuantity_allLine
                    result_sum = setDataList(process_at_list, result_ngQuantity_allLine, 'ng', [], 'Total', 'Assy', True)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    result.append(result_sum[0])

                if operator.eq('Y1', type) or operator.eq('Y2', type):
                    # Y1
                    result_inputQuantity = models_common.get_inputQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_inputQuantity == 101 or result_inputQuantity == 102:
                        return result_inputQuantity
                    result_outputQuantity = models_common.get_outputQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_outputQuantity == 101 or result_outputQuantity == 102:
                        return result_outputQuantity
                    result_ngQuantity = models_common.get_ngQuantity(model_name, start, end, 'All', False, '',lineNum)
                    if result_ngQuantity == 101 or result_ngQuantity == 102:
                        return result_ngQuantity
                    # outputQuantity,ngQuantity合并到inputQuantity
                    for inputrow in result_inputQuantity:
                        for outputrow in result_outputQuantity:
                            if operator.eq(outputrow['assy_text'], inputrow['assy_text']) and operator.eq(outputrow['process_at'], inputrow['process_at']):
                                inputrow["output_quantity"] = outputrow['output_quantity']
                                break
                        ng_quantity = 0
                        for ngrow in result_ngQuantity:
                            if operator.eq(ngrow['assy_text'], inputrow['assy_text']) and operator.eq(ngrow['process_at'],inputrow['process_at']):
                                ng_quantity = ngrow['ng_quantity']
                                break
                        inputrow["ng_quantity"] = ng_quantity

                        if inputrow["input_quantity"] > 0:
                            inputrow["y1"] = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
                        else:
                            inputrow["y1"] = 0.00
                        if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                            inputrow["y2"] = inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
                        else:
                            inputrow["y2"] = 0.00
                    # sort:assy_text,process_at
                    result_inputQuantity = sorted(result_inputQuantity, key=lambda x: (x['assy_text'], x['process_at']))
                    if operator.eq('Y1', type):
                        result = setDataList(process_at_list, result_inputQuantity, 'y1', assyArr, 'Total', 'Assy', False)
                    else:
                        result = setDataList(process_at_list, result_inputQuantity, 'y2', assyArr, 'Total', 'Assy', False)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    # get FPY(main)
                    data = getAllLine(result, process_at_list, model_name)

                    result.append({'name': 'FPY(main)', 'data': data, })
            if operator.eq('Process', content):
                # get process
                processArr = models_common.get_allProcess(model_name)
                if processArr == 101 or processArr == 102:
                    return processArr
                result_quantity = models_common.get_quantity_sumOfProcess(model_name, start, end, False)
                if result_quantity == 101 or result_quantity == 102:
                    return result_quantity
                if operator.eq('Input', type):
                    result = setDataList(process_at_list, result_quantity, 'input', processArr, 'Total', 'Process', False)
                    # get allProcess
                    result_inputQuantity_allLine = models_common.get_quantity_sumOfProcess(model_name, start, end, True)
                    if result_inputQuantity_allLine == 101 or result_inputQuantity_allLine == 102:
                        return result_inputQuantity_allLine
                    result_sum = setDataList(process_at_list, result_inputQuantity_allLine, 'input', [], 'Total', 'Process', True)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    result.append(result_sum[0])
                if operator.eq('Output', type):
                    # output
                    result = setDataList(process_at_list, result_quantity, 'output', processArr, 'Total', 'Process', False)
                    # get allProcess
                    result_outputQuantity_allLine = models_common.get_quantity_sumOfProcess(model_name, start, end, True)
                    if result_outputQuantity_allLine == 101 or result_outputQuantity_allLine == 102:
                        return result_outputQuantity_allLine
                    result_sum = setDataList(process_at_list, result_outputQuantity_allLine, 'output', [], 'Total', 'Process', True)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    result.append(result_sum[0])
                if operator.eq('NG', type):
                    result = setDataList(process_at_list, result_quantity, 'ng', processArr, 'Total', 'Process', False)
                    # get allProcess
                    result_ngQuantity_allLine = models_common.get_quantity_sumOfProcess(model_name, start, end, True)
                    if result_ngQuantity_allLine == 101 or result_ngQuantity_allLine == 102:
                        return result_ngQuantity_allLine
                    result_sum = setDataList(process_at_list, result_ngQuantity_allLine, 'ng', [], 'Total', 'Process', True)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    result.append(result_sum[0])
                if operator.eq('Y1', type) or operator.eq('Y2', type):
                    # outputQuantity,ngQuantity合并到inputQuantity
                    for inputrow in result_quantity:
                        if inputrow["input_quantity"] > 0:
                            #y1 = "%.2f" % (inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0) * 100)
                            y1 = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
                            inputrow["y1"] = float(y1)
                        else:
                            inputrow["y1"] = 0.00
                        if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                            #y2 = "%.2f" % (inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0) * 100)
                            y2 = inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
                            inputrow["y2"] = float(y2)
                        else:
                            inputrow["y2"] = 0.00

                    if operator.eq('Y1', type):
                        result = setDataList(process_at_list, result_quantity, 'y1', processArr, 'Total', 'Process', False)
                    else:
                        result = setDataList(process_at_list, result_quantity, 'y2', processArr, 'Total', 'Process', False)
                    # sort
                    result = sorted(result, key=lambda x: (x['process_id']))
                    # get allProcess
                    data = models_common.getAvg_allLine(result, process_at_list)
                    result.append({'name': 'All Process', 'data': data, })
        if operator.eq('Assy', object):
            if operator.eq('Input', type):
                # input
                result_inputQuantity = models_common.get_inputQuantity_sumOfLine(model_name, start, end, content, False)
                if result_inputQuantity == 101 or result_inputQuantity == 102:
                    return result_inputQuantity
                result = setDataList(process_at_list, result_inputQuantity, 'input', lineArr, 'Assy', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                result_inputQuantity_allLine = models_common.get_inputQuantity_sumOfLine(model_name, start, end, content, True)
                if result_inputQuantity_allLine == 101 or result_inputQuantity_allLine == 102:
                    return result_inputQuantity_allLine
                result_sum = setDataList(process_at_list, result_inputQuantity_allLine, 'input', [], 'Assy', '', True)
                result.append(result_sum[0])

            if operator.eq('Output', type):
                # output
                result_outputQuantity = models_common.get_outputQuantity_sumOfLine(model_name, start, end, content, False)
                if result_outputQuantity == 101 or result_outputQuantity == 102:
                    return result_outputQuantity
                result = setDataList(process_at_list, result_outputQuantity, 'output', lineArr, 'Assy', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                result_outputQuantity_allLine = models_common.get_outputQuantity_sumOfLine(model_name, start, end, content, True)
                if result_outputQuantity_allLine == 101 or result_outputQuantity_allLine == 102:
                    return result_outputQuantity_allLine
                result_sum = setDataList(process_at_list, result_outputQuantity_allLine, 'output', [], 'Assy', '', True)
                result.append(result_sum[0])

            if operator.eq('NG', type):
                # NG
                result_ngQuantity = models_common.get_ngQuantity_sumOfLine(model_name, start, end, content, False)
                if result_ngQuantity == 101 or result_ngQuantity == 102:
                    return result_ngQuantity
                result = setDataList(process_at_list, result_ngQuantity, 'ng', lineArr, 'Assy', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                result_ngQuantity_allLine = models_common.get_ngQuantity_sumOfLine(model_name, start, end, content, True)
                if result_ngQuantity_allLine == 101 or result_ngQuantity_allLine == 102:
                    return result_ngQuantity_allLine
                result_sum = setDataList(process_at_list, result_ngQuantity_allLine, 'ng', [], 'Assy', '', True)
                result.append(result_sum[0])

            if operator.eq('Y1', type) or operator.eq('Y2', type):
                # Y1
                result_inputQuantity = models_common.get_inputQuantity_sumOfLine(model_name, start, end, content, False)
                if result_inputQuantity == 101 or result_inputQuantity == 102:
                    return result_inputQuantity
                result_outputQuantity = models_common.get_outputQuantity_sumOfLine(model_name, start, end, content, False)
                if result_outputQuantity == 101 or result_outputQuantity == 102:
                    return result_outputQuantity
                result_ngQuantity = models_common.get_ngQuantity_sumOfLine(model_name, start, end, content, False)
                if result_ngQuantity == 101 or result_ngQuantity == 102:
                    return result_ngQuantity
                # outputQuantity,ngQuantity合并到inputQuantity
                for inputrow in result_inputQuantity:
                    for outputrow in result_outputQuantity:
                        if operator.eq(outputrow['line_cd'], inputrow['line_cd']) and operator.eq(\
                                outputrow['process_at'], inputrow['process_at']):
                            inputrow["output_quantity"] = outputrow['output_quantity']
                            break
                    ng_quantity = 0
                    for ngrow in result_ngQuantity:
                        if operator.eq(ngrow['line_cd'], inputrow['line_cd']) and operator.eq(ngrow['process_at'], inputrow['process_at']):
                            ng_quantity = ngrow['ng_quantity']
                            break
                    inputrow["ng_quantity"] = ng_quantity

                    if inputrow["input_quantity"] > 0:
                        # y1 = "%.2f" % (inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)* 100)
                        y1 = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
                        inputrow["y1"] = float(y1)
                    else:
                        inputrow["y1"] = 0.00
                    if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                        #y2 = "%.2f" % (inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0) * 100)
                        y2 = inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
                        inputrow["y2"] = float(y2)
                    else:
                        inputrow["y2"] = 0.00

                if operator.eq('Y1', type):
                    result = setDataList(process_at_list, result_inputQuantity, 'y1', lineArr, 'Assy', '', False)
                else:
                    result = setDataList(process_at_list, result_inputQuantity, 'y2', lineArr, 'Assy', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                data = models_common.getAvg_allLine(result, process_at_list)
                result.append({'name': 'All Line', 'data': data, })
        if operator.eq('Process', object):
            result_quantity = models_common.get_quantity_sumOfLineProcess(model_name, start, end, content, False)
            if result_quantity == 101 or result_quantity == 102:
                return result_quantity
            if operator.eq('Input', type):
                result = setDataList(process_at_list, result_quantity, 'input', lineArr, 'Process', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                result_inputQuantity_allLine = models_common.get_quantity_sumOfLineProcess(model_name, start, end, content, True)
                if result_inputQuantity_allLine == 101 or result_inputQuantity_allLine == 102:
                    return result_inputQuantity_allLine
                result_sum = setDataList(process_at_list, result_inputQuantity_allLine, 'input', [], 'Process', '', True)
                result.append(result_sum[0])

            if operator.eq('Output', type):
                result = setDataList(process_at_list, result_quantity, 'output', lineArr, 'Process', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                result_outputQuantity_allLine = models_common.get_quantity_sumOfLineProcess(model_name, start, end, content, True)
                if result_outputQuantity_allLine == 101 or result_outputQuantity_allLine == 102:
                    return result_outputQuantity_allLine
                result_sum = setDataList(process_at_list, result_outputQuantity_allLine, 'output', [], 'Process', '', True)
                result.append(result_sum[0])

            if operator.eq('NG', type):
                result = setDataList(process_at_list, result_quantity, 'ng', lineArr, 'Process', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                result_ngQuantity_allLine = models_common.get_quantity_sumOfLineProcess(model_name, start, end, content, True)
                if result_ngQuantity_allLine == 101 or result_ngQuantity_allLine == 102:
                    return result_ngQuantity_allLine
                result_sum = setDataList(process_at_list, result_ngQuantity_allLine, 'ng', [], 'Process', '', True)
                result.append(result_sum[0])

            if operator.eq('Y1', type) or operator.eq('Y2', type):
                for inputrow in result_quantity:
                    if inputrow["input_quantity"] > 0:
                        #y1 = "%.2f" % (inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0) * 100)
                        y1 = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
                        inputrow["y1"] = float(y1)
                    else:
                        inputrow["y1"] = 0.00
                    if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                        #y2 = "%.2f" % (inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0) * 100)
                        y2 = inputrow["output_quantity"] / ((inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
                        inputrow["y2"] = float(y2)
                    else:
                        inputrow["y2"] = 0.00

                if operator.eq('Y1', type):
                    result = setDataList(process_at_list, result_quantity, 'y1', lineArr, 'Process', '', False)
                else:
                    result = setDataList(process_at_list, result_quantity, 'y2', lineArr, 'Process', '', False)
                # sort
                result = sorted(result, key=lambda x: (x['name']))
                # get allLine
                data = models_common.getAvg_allLine(result, process_at_list)
                result.append({'name': 'All Line', 'data': data, })

        if operator.eq('Y1', type) or operator.eq('Y2', type):
            # 转成百分比
            for row in result:
                i = 0
                for value in row['data']:
                    row['data'][i] = float("%.2f" % (value * 100))
                    i = i + 1

    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

def getAllLine(result, process_at_list, model_name):
    data = []
    data_zero = []
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

    i = 0
    while i < len(process_at_list):
        data_zero.append(0.00)
        i = i + 1

    # 按配置文件里ASSY的顺序排列result
    result_temp = []
    for key in assyDic_int:
        flg = False
        for row in result:
            if operator.eq(row['name'], assyDic_int[key]):
                flg = True
                result_temp.append(row)
                break
        # 当前Assy在result里不存在的场合
        if flg == False:
            result_temp.append({'name':assyDic_int[key], 'data': data_zero})

    for i in range(len(process_at_list)):
        yield_list = []
        yield_list_temp = []
        for row in result_temp:
            yield_value = float(row['data'][i])
            if yield_value == float(0):
                yield_list.append(float(1))
                yield_list_temp.append('NP')
            else:
                yield_list.append(yield_value)
                yield_list_temp.append(yield_value)

        # 计算y2_fpy
        y2_fpy_value = models_common.get_formula_value(yield_list, yield_list_temp, fpy_formula)

        # 将当前计算值添加到list
        data.append(y2_fpy_value)
    return data
