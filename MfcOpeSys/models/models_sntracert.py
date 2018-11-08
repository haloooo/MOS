# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import operator
from MfcOpeSys.models import models_common

# 获取sntracert信息
def get_sntracert(model_name, from_process_at, to_process_at, config, line, datatype_id, mode, pernum):
    result = []
    relationDic = {}
    try:
        if mode == "LINK":
            cur = connections[model_name].cursor()
            # 获取父子继承关系
            sql_relation = "WITH RECURSIVE r AS (\
                                            SELECT \
                                              child_sn,\
                                              parent_sn, \
                                              datatype_seq \
                                            FROM \
                                                m_sn_datatype_relation son \
                                            WHERE \
                                                child_sn = %s \
                                            UNION ALL \
                                            SELECT \
                                                parent.child_sn,\
                                                parent.parent_sn, \
                                            parent.datatype_seq \
                                            FROM \
                                                m_sn_datatype_relation parent,\
                                                r \
                                            WHERE \
                                                parent.child_sn = r.parent_sn \
                                    ) SELECT datatype_seq,child_sn,parent_sn FROM r ORDER BY datatype_seq"
            cur.execute(sql_relation, (datatype_id,))
            rows_relation = cur.fetchall()
            # key:son,value:parent

            for row in rows_relation:
                arr = []
                arr.append(row[1])
                arr.append(row[2])
                relationDic[row[0]] = arr

        # 最上层场合
        if len(relationDic) == 1 or mode == "INDIVID":
            # 获取数据
            resultDic = getDataByDatatype(model_name, from_process_at, to_process_at, config, line,\
                                          datatype_id, pernum, False, [], True)
            # 异常场合
            if type(resultDic) == int:
                return resultDic
            # wip的再设定
            result = set_sntracert_wip(resultDic['result'])
        else:
            # sntracert信息的取得和设定
            resultArr = set_sntracert(model_name, from_process_at, to_process_at, config, line, datatype_id, pernum, relationDic)
            # wip的再设定
            result = set_sntracert_wip(resultArr)

    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

# 设置sntracert明细的wip
def set_sntracert_wip(resultArr):
    result = resultArr
    last_ok = 0
    index = 0
    for row in result:
        if index == 0:
            row['wip'] = 0
        else:
            row['wip'] = last_ok - row['input']
        last_ok = row['ok']
        index = index + 1
    return result

# sntracert信息的取得和设定
def set_sntracert(model_name, from_process_at, to_process_at, config, line, datatype_id, pernum, relationDic):
    result = []
    try:
        # 第一工位全部信息
        result_first = {}
        # 第一工位的serial_cd数组
        result_first_serialCd = []
        index = 0
        for key in relationDic:
            index = index + 1

            # 最底层的datatype_id场合
            if relationDic[key][0] == datatype_id:

                # 获取数据
                resultDic = getDataByDatatype(model_name, from_process_at, to_process_at, config, line,\
                                                  relationDic[key][0], pernum, False, [], True)
                # 异常场合
                if type(resultDic) == int:
                    return resultDic

                if len(resultDic['result']) == 0:
                    return result
                else:
                    result = result + resultDic['result']

                    if len(resultDic['lastDataArr']) == 0:
                        return result
                    else:
                        # 获取parent的第一工位数据
                        result_firstDic = get_parentFirstData(model_name, from_process_at, to_process_at, config, line,\
                                                              relationDic[key][0], resultDic['lastDataArr'],\
                                                              relationDic[key][1], pernum)
                        # 异常场合
                        if type(result_firstDic) == int:
                            return result_firstDic

                        result_first_serialCd = result_firstDic['serial_cds']
                        result_first = result_firstDic['result']

            else:
                # parent的第一工位无数据的场合
                if len(result_first_serialCd) == 0:
                    return result
                else:
                    # 获取数据
                    resultDic = getDataByDatatype(model_name, from_process_at, to_process_at, config, line,\
                                                  relationDic[key][0], pernum, True, result_first_serialCd, False)
                    # 异常场合
                    if type(resultDic) == int:
                        return resultDic
                    if len(resultDic['result']) == 0:
                        return result
                    else:
                        # 替换第一工位的数据
                        resultDic["result"][0] = result_first
                        # 不是最上层的datatype_id场合
                        if index < len(relationDic):
                            getLastFlg = True
                        else:
                            getLastFlg = False

                        result = result + resultDic['result']
                        if len(resultDic['lastDataArr']) > 0:
                            # 不是最上层的datatype_id场合
                            if getLastFlg:
                                # 获取parent的第一工位数据
                                result_firstDic = get_parentFirstData(model_name, from_process_at, to_process_at,\
                                                                      config, line,\
                                                                      relationDic[key][0], resultDic['lastDataArr'],\
                                                                      relationDic[key][1], pernum)
                                # 异常场合
                                if type(result_firstDic) == int:
                                    return result_firstDic
                                result_first_serialCd = result_firstDic['serial_cds']
                                result_first = result_firstDic['result']
                            else:
                                return result
        return result
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    return result

# 根据datatype获取数据
def getDataByDatatype(model_name, from_process_at, to_process_at, config, line, datatype_id, pernum, inheritFlg, inheritArr, firstDatatypeFlg):
    resultDic = {}
    result = []
    # 获取满足条件的工位信息
    processArr = get_processIDs(model_name, from_process_at, to_process_at, config, line, datatype_id, pernum, firstDatatypeFlg)

    # 异常场合
    if type(processArr) == int:
        return processArr
    flg = inheritFlg
    index_process = 0
    previousSerialNoArr = []
    hold_for = 0
    for row in processArr:
        result_process = {}
        # 父子继承的场合，第一工位不检索，获取子工位的最后一个工位的OK数据
        if flg and index_process == 0:
            previousSerialNoArr = inheritArr
            result.append(row)
            flg = False
        else:
            # 获取第一工位的数据
            if index_process == 0:
                firstProFlg = False
                if firstDatatypeFlg:
                    firstProFlg = True
                result_process = get_dataByProcessId(model_name, from_process_at, to_process_at, config, line,\
                                                     row['process_id'], pernum, True, previousSerialNoArr, False, firstProFlg)
            else:
                if len(previousSerialNoArr) > 0:
                    holdForFlg = False
                    if row['process_id'] == hold_for:
                        holdForFlg = True
                    # 获取工位的数据
                    result_process = get_dataByProcessId(model_name, from_process_at, to_process_at, config, line,\
                                                     row['process_id'], pernum, False, previousSerialNoArr, holdForFlg, False)
            # 异常场合
            if type(result_process) == int:
                return result_process
            if len(result_process['detail']) == 0:
                break
            else:
                row['ok'] = result_process['ok']
                row['ng'] = result_process['ng']
                row['input'] = result_process['input']
                row['yield'] = result_process['yield']
                row['ipqc'] = result_process['ipqc']
                row['detail'] = result_process['detail']
                # 翻页按钮活性设定
                if result_process['detail']:
                    if len(result_process['detail']) > pernum:
                        row['next_display'] = 0
                arr_temp = []
                for row_detail in result_process['detail']:
                    if row_detail['result'] == "OK":
                        arr_temp.append(row_detail['serial_no'])
                # 将OK数据放入数组中，作为下一个工位的输入
                previousSerialNoArr = arr_temp
                result.append(row)
                if len(previousSerialNoArr) <= 0:
                    break

        if row['hold_for'] != 0:
            hold_for = row['hold_for']
        index_process = index_process + 1

    resultDic['result'] = result
    resultDic['lastDataArr'] = previousSerialNoArr
    return resultDic

# 获取parent的第一工位数据
def get_parentFirstData(model_name, from_process_at, to_process_at, config, line, datatype_id, lastDataArr, parentDatatype, pernum):
    result = {}
    resultDic = {}
    serial_cd = []
    from_process_at = from_process_at + '+08'
    to_process_at = to_process_at + '+08'
    try:
        cur = connections[model_name].cursor()
        # 获取第一工位的process相关信息
        sql = "SELECT\
                    assy.process_id,\
                    assy.process_text,\
                    assy.assy_text,\
                    tracert.process_cd,\
                    assy.hold_for \
                FROM\
                    t_1_sn_tracert tracert\
                    INNER JOIN t_1_sn_target target ON tracert.serial_cd = target.serial_cd \
                    AND target.line_cd = '(line_cd)' \
                    AND target.config_cd = '(config_cd)' \
                    INNER JOIN m_assy assy ON assy.datatype_id = target.datatype_id\
                    AND assy.process_cd = tracert.process_cd \
                    AND assy.tracert_sw = 'ON' \
                    AND assy.datatype_id = '(datatype_id)'\
                ORDER BY\
                    assy.process_id\
                    limit 1"
        sql = sql.replace("(line_cd)", line).replace("(datatype_id)", parentDatatype).replace("(config_cd)", config)
        cur.execute(sql)
        rows = cur.fetchall()
        first_processId = ""
        for row in rows:
            first_processId = str(row[0])
            result = {"process_id": row[0], "process_code": row[3], "process_name": row[1], "assy_name": row[2],\
                 "ok": 0, "ng": 0, "input": 0, \
                 "yield": "0.00%", "ipqc": 0, "wip": 0, \
                 "index": 0, "s_index": 0, "e_index": pernum, "first_display": 1, "next_display": 1,\
                 "detail": [], "hold_for": row[4], }
        # 获取第一工位的OK，NG，detail等相关信息
        sql = "SELECT\
                    tracert.serial_cd,\
                    tracert.judge_text \
                FROM\
                    t_1_sn_tracert tracert\
                    INNER JOIN t_1_sn_target target ON tracert.serial_cd = target.serial_cd \
                    AND target.line_cd = '(line_cd)' \
                    AND target.config_cd = '(config_cd)' \
                    AND tracert.serial_cd IN ( SELECT serial_cd FROM t_1_sn_matg WHERE child_cd IN ( %s ) AND datatype_id = '(datatype_id)' ) \
                    INNER JOIN m_assy assy ON assy.datatype_id = target.datatype_id \
                    AND assy.process_cd = tracert.process_cd \
                    AND assy.tracert_sw = 'ON' \
                    AND assy.datatype_id = '(parent_datatype_id)'\
                    AND assy.process_id = '(process_id)'\
                ORDER BY tracert.serial_cd" % ','.join(['%s'] * len(lastDataArr))
        sql = sql.replace("(line_cd)", line).replace("(datatype_id)", datatype_id).replace("(config_cd)", config)\
            .replace("(parent_datatype_id)", parentDatatype).replace("(process_id)", first_processId)
        cur.execute(sql, lastDataArr)
        rows = cur.fetchall()
        ok_quantity = 0
        ng_quantity = 0
        ipqc_quantity = 0
        for row in rows:
            detailResult = ''
            yield2 = '0.00%'
            if operator.eq(row[1], '0'):
                detailResult = 'OK'
                ok_quantity = ok_quantity + 1
            elif operator.eq(row[1], '1'):
                detailResult = 'NG'
                ng_quantity = ng_quantity + 1
            elif operator.eq(row[1], 'IPQC'):
                detailResult = 'IPQC'
                ipqc_quantity = ipqc_quantity + 1

            if ok_quantity + ng_quantity > 0:
                yield2 = "%.2f%%" % (ok_quantity / ((ok_quantity + ng_quantity) * 1.0) * 100)

            result['ok'] = ok_quantity
            result['ng'] = ng_quantity
            result['input'] = ok_quantity + ng_quantity + ipqc_quantity
            result['yield'] = yield2
            result['ipqc'] = ipqc_quantity
            result['detail'].append({"serial_no": row[0], "result": detailResult, })
            # 翻页按钮活性设定
            if result['detail']:
                if len(result['detail']) > pernum:
                    result['next_display'] = 0

            serial_cd.append(row[0])

    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    resultDic['result'] = result
    resultDic['serial_cds'] = serial_cd
    return resultDic

# 获取满足条件的工位信息
def get_dataByProcessId(model_name, from_process_at, to_process_at, config, line, process_id, pernum, firstFlg, previousSerialNoArr, holdForFlg, firstProFlg):
    result = {}
    from_process_at = from_process_at + '+08'
    to_process_at = to_process_at + '+08'
    sub_serial_sql = ""
    sub_judge_sql = ""
    sub_datetime_sql = ""
    # 不是第一工位的场合
    if firstFlg == False:
        sub_serial_sql = " AND tracert.serial_cd IN( %s ) "
        # 当前检索的工位数据是hold_for数据
        if holdForFlg:
            sub_judge_sql = " AND tracert.judge_text IN ( '1','IPQC') "
    # 是第一datatype且是第一工位的场合
    if firstProFlg:
        sub_datetime_sql = " AND tracert.process_at >= '" + from_process_at + "' AND tracert.process_at <= '" + to_process_at + "' "
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT \
                    tracert.serial_cd,\
                    tracert.judge_text \
                FROM \
                    t_1_sn_tracert tracert \
                    INNER JOIN t_1_sn_target target ON tracert.serial_cd = target.serial_cd " + sub_serial_sql + \
            "AND target.line_cd = '(line_cd)' \
                    AND target.config_cd = '(config_cd)' " + sub_datetime_sql + \
            "INNER JOIN m_assy assy ON assy.datatype_id = target.datatype_id \
            AND assy.process_cd = tracert.process_cd \
            AND assy.process_id = '(process_id)' " + sub_judge_sql + \
            "ORDER BY tracert.serial_cd"
        sql = sql.replace("(line_cd)", line).replace("(process_id)", str(process_id)).replace("(config_cd)", config)
        if firstFlg:
            cur.execute(sql)
        else:
            sql = sql % ','.join(['%s'] * len(previousSerialNoArr))
            cur.execute(sql, previousSerialNoArr)
        rows = cur.fetchall()
        ok_quantity = 0
        ng_quantity = 0
        ipqc_quantity = 0
        data_exist_flg = False
        holdFor_input = len(previousSerialNoArr)
        detail = []
        detail_temp = []
        yield2 = "0.00%"
        next_display = 1
        for row in rows:
            data_exist_flg = True
            detailResult = ''
            if operator.eq(row[1], '0'):
                detailResult = 'OK'
                ok_quantity = ok_quantity + 1
            elif operator.eq(row[1], '1'):
                detailResult = 'NG'
                ng_quantity = ng_quantity + 1
            elif operator.eq(row[1], 'IPQC'):
                detailResult = 'IPQC'
                ipqc_quantity = ipqc_quantity + 1

            detail.append({"serial_no": row[0], "result": detailResult, })

            # 当前检索的工位数据是hold_for数据
            if holdForFlg:
                detail_temp.append(row[0])

        # 当前检索的工位数据是hold_for数据
        if holdForFlg:
            # 翻页按钮活性设定
            if holdFor_input > pernum:
                next_display = 0
            # holdFor工位的NG数据不存在的场合
            if data_exist_flg == False:
                for value in previousSerialNoArr:
                    detail.append({"serial_no": value, "result": "OK", })
                result = {"ok": holdFor_input, "ng": 0, "input": holdFor_input,\
                          "yield": "100.00%", "ipqc": 0, "wip": 0,\
                           "next_display": next_display,\
                          "detail": detail, }
            else:
                ok_quantity = holdFor_input - ng_quantity - ipqc_quantity
                if ok_quantity + ng_quantity > 0:
                    yield2 = "%.2f%%" % (ok_quantity / ((ok_quantity + ng_quantity) * 1.0) * 100)
                for value in previousSerialNoArr:
                    if value not in detail_temp:
                        detail.append({"serial_no": value, "result": "OK", })
                # detail按照序列号排序
                detail = sorted(detail, key=lambda x: (x['serial_no']))
                result = {"ok": ok_quantity, "ng": ng_quantity, "input": holdFor_input,\
                          "yield": yield2, "ipqc": ipqc_quantity, "wip": 0,\
                          "next_display": next_display,\
                          "detail": detail, }
        else:
            if ok_quantity + ng_quantity > 0:
                yield2 = "%.2f%%" % (ok_quantity / ((ok_quantity + ng_quantity) * 1.0) * 100)
            # 翻页按钮活性设定
            if len(detail) > pernum:
                next_display = 0
            result = {"ok": ok_quantity, "ng": ng_quantity, "input": ok_quantity + ng_quantity + ipqc_quantity,\
                      "yield": yield2, "ipqc": ipqc_quantity, "wip": 0,\
                      "next_display": next_display,\
                      "detail": detail, }

    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result

# 获取满足条件的工位信息
def get_processIDs(model_name, from_process_at, to_process_at, config, line, datatype_id, pernum, firstDatatypeFlg):
    result = []
    from_process_at = from_process_at + '+08'
    to_process_at = to_process_at + '+08'
    sql1 = "SELECT \
	            process_id,\
	            process_text,\
	            assy_text,\
	            process_cd,\
	            hold_for \
            FROM("
    sql2 = "SELECT DISTINCT \
                                assy.process_id,\
                                assy.process_text,\
                                assy.assy_text,\
                                tracert.process_cd,\
                                assy.hold_for \
                            FROM \
                                t_1_sn_tracert tracert \
                                INNER JOIN t_1_sn_target target ON tracert.serial_cd = target.serial_cd \
                                AND target.line_cd = '(line_cd)' \
                                AND target.config_cd = '(config_cd)' "
    sql3 = "INNER JOIN m_assy assy ON assy.datatype_id = target.datatype_id \
                        AND assy.process_cd = tracert.process_cd \
                        AND assy.tracert_sw = 'ON' \
                        AND assy.datatype_id = '(datatype_id)' \
                    ORDER BY assy.process_id "
    sql_limit = " LIMIT 1 ) t1 UNION "
    sql_offset = " OFFSET 1 ) t2 ORDER BY process_id"
    # 是第一datatype的场合
    if firstDatatypeFlg:
        sub_datetime_sql = " AND tracert.process_at >= '" + from_process_at + "' AND tracert.process_at <= '" + to_process_at + "' "
        sql = sql1 + sql2 + sql3 + sql_limit + sql1 + sql2 + sub_datetime_sql + sql3 + sql_offset
    else:
        sql = sql2 + sql3
    try:
        cur = connections[model_name].cursor()
        sql = sql.replace("(line_cd)", line).replace("(datatype_id)", datatype_id).replace("(config_cd)", config)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append( \
                {"process_id": row[0], "process_code": row[3], "process_name": row[1], "assy_name": row[2],\
                 "ok": 0, "ng": 0, "input": 0,\
                 "yield": "0.00%", "ipqc": 0, "wip": 0,\
                 "index": 0, "s_index": 0, "e_index": pernum, "first_display": 1, "next_display": 1,\
                 "detail": [], "hold_for": row[4], })
    except BaseException as exp:
        print(exp)
        result = models_common.databaseException(exp)
    connections[model_name].close()
    return result
