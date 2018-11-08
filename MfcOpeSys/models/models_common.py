# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import connections
import json
import os
import operator
import datetime
import re

from MfcOpeSys.models import models_ngreport


def get_config(key):
    # 加载配置文件
    file_path = os.getcwd() + '/config/config.json'
    fp = open(file_path)
    json_data = json.load(fp)
    return json_data[key]


def get_models():
    result = []
    try:
        from django.conf import settings
        for model_name in settings.DATABASES:
            if model_name != 'default':
                if len(model_name) > 8:
                    dis = model_name[0:8] + '...'
                else:
                    dis = model_name
                result.append({'name': model_name, 'dis': dis})
                result.sort(key=lambda x: x["name"])
    except BaseException as exp:
        print(exp)
    return result


def get_lines(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT DISTINCT line_cd FROM m_work ORDER BY line_cd")
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_assys(model_name, line):
    result = []
    assy_result = []
    fin_result = []
    try:
        cur = connections[model_name].cursor()
        cur.execute('SELECT DISTINCT assy_text,min(process_id) as a FROM m_assy GROUP BY assy_text ORDER BY a;')
        assy_rows = cur.fetchall()
        for row in assy_rows:
            assy_result.append(row[0])
        cur.execute("SELECT assy_text FROM m_work where line_cd = (%s)",
                    (line,))
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])

        for item in assy_result:
            for item_ in result:
                if (item == item_):
                    fin_result.append(item)
    except BaseException as exp:
        print(exp)
        fin_result = databaseException(exp)
    connections[model_name].close()
    return fin_result


def get_datatypeIds(model_name, line):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT \
                    datatype_id,\
                    MIN( process_id ) process_id \
                FROM\
                    ( SELECT DISTINCT datatype_id, process_id FROM m_assy assy INNER JOIN m_work ON m_work.assy_text = assy.assy_text AND m_work.line_cd = %s AND assy.tracert_sw = 'ON') T1 \
                GROUP BY datatype_id \
                ORDER BY process_id"
        cur.execute(sql, (line,))
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_tps(model_name, line, assy):
    result = []
    sql_line = ""
    sql_assy = ""
    try:
        if line != 'All Line' and line != '':
            sql_line = " AND line_cd = '" + line + "' "
        if assy != 'All Assy' and assy != '':
            sql_assy = " AND assy_text = '" + assy + "' "
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT \
                        time_part,\
                        time_val_s,\
                        time_val_e \
                    FROM\
                        m_work A\
                        LEFT JOIN m_time_table B ON A.time_tbl_cd = B.time_tbl_cd \
                    WHERE\
                        1=1 " + sql_line + sql_assy + \
              "ORDER BY time_part"
        cur.execute(sql)
        rows = cur.fetchall()
        result_temp1 = []
        result_temp2 = []
        for row in rows:
            if row[0] == "All" or row[0] == "Day" or row[0] == "Night":
                result_temp1.append({"time_part": row[0], "time_val_s": row[1], "time_val_e": row[2], })
            else:
                result_temp2.append({"time_part": row[0], "time_val_s": row[1], "time_val_e": row[2], })

        result = result_temp1
        result.extend(result_temp2)
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_configs(model_name, from_process_at, to_process_at):
    from_process_at = from_process_at + '+08'
    to_process_at = to_process_at + '+08'
    result = []
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT DISTINCT\
                        config_cd \
                        FROM\
                            t_1_sn_target \
                        WHERE config_cd IS NOT NULL AND config_cd <> '' \
                        AND process_at >= %s \
                        AND process_at <= %s \
                        ORDER BY config_cd", (from_process_at, to_process_at,))
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_processdetail(model_name, line, assy, process_at, time_part, flg, selectedModel):
    result = []
    sql = ""
    last_process_id = ''
    if operator.eq(flg, "First"):
        auto_tablename = 't_1_auto_io_1st'
        defect_tablename = 't_1_defect_1st'
    else:
        auto_tablename = 't_1_auto_io_2nd'
        defect_tablename = 't_1_defect_2nd'
    try:
        cur = connections[model_name].cursor()
        sql_okAndNg = "FROM\
                                            m_assy A\
                                            INNER JOIN m_work work ON A.assy_text = work.assy_text\
                                            AND line_cd = '(line_cd)'\
                                            LEFT JOIN (\
                                        SELECT\
                                            auto.process_id,\
                                            SUM( quantity ) AS ng_quantity \
                                        FROM\
                                            m_assy A\
                                            INNER JOIN (auto_tablename) auto ON A.process_id = auto.process_id \
                                            AND A.assy_text = '(assy)' \
                                        WHERE\
                                            process_at = '(process_at)'\
                                            AND time_part = '(time_part)' \
                                            AND judge_text = 'ng' \
                                            AND line_cd = '(line_cd)'\
                                        GROUP BY\
                                            auto.process_id \
                                            ) AS auto_ng ON A.process_id = auto_ng.process_id\
                                            LEFT JOIN (\
                                        SELECT\
                                            process_id,\
                                            SUM( quantity ) AS ok_quantity \
                                        FROM\
                                            (\
                                        SELECT\
                                            auto.process_id,\
                                            quantity \
                                        FROM\
                                            m_assy A\
                                            INNER JOIN (auto_tablename) auto ON A.process_id = auto.process_id \
                                            AND A.assy_text = '(assy)'\
                                        WHERE\
                                            process_at = '(process_at)'\
                                            AND time_part = '(time_part)' \
                                            AND judge_text = 'ok' \
                                            AND line_cd = '(line_cd)'\
                                            ) AS ok \
                                        GROUP BY\
                                            process_id \
                                            ) AS auto_ok ON A.process_id = auto_ok.process_id"
        if operator.eq(selectedModel, "Inspect"):
            sql = "SELECT\
                        process_id,\
                        process_cd,\
                        process_text,\
                        ok_quantity,\
                        ng_quantity,\
                        data_seq,\
                        inspect_cd,\
                        COALESCE(inspect_count, 0) AS inspect_count \
                    FROM\
                      (\
                    SELECT DISTINCT\
                        A.process_id,\
                        A.process_seq,\
                        A.process_cd,\
                        A.process_text,\
                        auto_ok.ok_quantity,\
                        auto_ng.ng_quantity,\
                        defect.data_seq,\
                        defect.inspect_cd,\
                        defect.inspect_count " + sql_okAndNg + \
                  " LEFT JOIN (\
              SELECT\
                  auto.process_id,\
                  auto.data_seq,\
                  defect.inspect_cd,\
                  COUNT( defect.inspect_cd ) AS inspect_count \
              FROM\
                  m_assy assy\
                  LEFT JOIN (auto_tablename) auto ON assy.process_id = auto.process_id \
                  AND process_at = '(process_at)' \
                  AND time_part = '(time_part)'\
                  AND judge_text = 'ng'\
                  AND line_cd = '(line_cd)'\
                  LEFT JOIN (defect_tablename) defect ON auto.data_seq = defect.data_seq \
              WHERE\
                  assy.assy_text = '(assy)' \
                  AND defect.inspect_cd IS NOT NULL \
              GROUP BY\
                  auto.process_id,\
                  auto.data_seq,\
                  defect.inspect_cd \
                  ) AS defect ON A.process_id = defect.process_id \
              WHERE\
                  A.assy_text = '(assy)'\
                  ) AS B \
              ORDER BY\
                  process_id,\
                  inspect_cd"
        else:
            sql = "SELECT\
                        process_id,\
                        process_cd,\
                        process_text,\
                        ok_quantity,\
                        ng_quantity,\
                        data_seq,\
                        serial_cd,\
                        COALESCE(serial_cd_count, 0) AS serial_cd_count \
                    FROM\
                      (\
                    SELECT DISTINCT\
                        A.process_id,\
                        A.process_seq,\
                        A.process_cd,\
                        A.process_text,\
                        auto_ok.ok_quantity,\
                        auto_ng.ng_quantity,\
                        defect.data_seq,\
                        defect.serial_cd,\
                        defect.serial_cd_count " + sql_okAndNg + \
                  " LEFT JOIN (\
              SELECT\
                  auto.process_id,\
                  auto.data_seq,\
                  defect.serial_cd,\
                  COUNT( defect.serial_cd ) AS serial_cd_count \
              FROM\
                  m_assy assy\
                  LEFT JOIN (auto_tablename) auto ON assy.process_id = auto.process_id \
                  AND process_at = '(process_at)' \
                  AND time_part = '(time_part)'\
                  AND judge_text = 'ng'\
                  AND line_cd = '(line_cd)'\
                  LEFT JOIN (defect_tablename) defect ON auto.data_seq = defect.data_seq \
              WHERE\
                  assy.assy_text = '(assy)' \
                  AND defect.inspect_cd IS NOT NULL \
              GROUP BY\
                  auto.process_id,\
                  auto.data_seq,\
                  defect.serial_cd \
                  ) AS defect ON A.process_id = defect.process_id \
              WHERE\
                  A.assy_text = '(assy)'\
                  ) AS B \
              ORDER BY\
                  process_seq,\
                  serial_cd"

        sql = sql.replace("(assy)", assy).replace("(process_at)", process_at).replace("(time_part)", time_part) \
            .replace("(auto_tablename)", auto_tablename).replace("(defect_tablename)", defect_tablename) \
            .replace("(line_cd)", line)
        cur.execute(sql)
        rows = cur.fetchall()
        index = 0
        ng = 0
        inspect_count = 0
        if operator.eq(selectedModel, "Inspect"):
            for row in rows:
                current_process_id = row[0]
                if row[4] is None or row[4] == 0:
                    if last_process_id != current_process_id:
                        index = index + 1
                        result.append(
                            {"process_id": int(row[0]), \
                             "process_code": row[1], \
                             "process_name": row[2], \
                             "inspect_cnt": 0, \
                             "detail": [] \
                             })
                else:
                    if operator.eq(last_process_id, current_process_id):
                        inspect_count = inspect_count + int(row[7])
                        result[index - 1]['detail'].append(
                            {"name": row[6], "num": int(row[7]), "data_seq": int(row[5]), })
                        result[index - 1]['inspect_cnt'] = inspect_count
                    else:
                        index = index + 1
                        inspect_count = int(row[7])
                        result.append( \
                            {"process_id": int(row[0]), "process_code": row[1], "process_name": row[2],
                             "inspect_cnt": inspect_count, \
                             "detail": [{"name": row[6], "num": int(row[7]), "data_seq": int(row[5]), }], })

                last_process_id = current_process_id
        else:
            for row in rows:
                current_process_id = row[0]
                if row[4] is None or row[4] == 0:
                    if last_process_id != current_process_id:
                        index = index + 1
                        if row[3] is None or row[3] == 0:
                            yield2 = float(0)
                            ok_quantity = 0
                        else:
                            yield2 = float(1)
                            ok_quantity = int(row[3])
                        result.append(
                            {"process_id": int(row[0]), \
                             "process_code": row[1], \
                             "process_name": row[2], \
                             "ok": ok_quantity, \
                             "ng": ng, \
                             "yield": "%.2f%%" % (yield2 * 100), \
                             "detail": [] \
                             })
                else:
                    if operator.eq(last_process_id, current_process_id):
                        result[index - 1]['detail'].append({"name": row[6], "num": int(row[7]), })
                    else:
                        if row[3] is None:
                            ok_quantity = 0
                        else:
                            ok_quantity = int(row[3])
                        index = index + 1
                        if ok_quantity + int(row[4]) == 0:
                            yield2 = float(0)
                        else:
                            yield2 = ok_quantity / ((ok_quantity + int(row[4])) * 1.0)
                        result.append( \
                            {"process_id": int(row[0]), "process_code": row[1], "process_name": row[2], \
                             "ok": ok_quantity, "ng": int(row[4]), \
                             "yield": "%.2f%%" % (yield2 * 100), \
                             "detail": [{"name": row[6], "num": int(row[7]), }], })
                last_process_id = current_process_id

    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_defectdetail(model_name, data_seq, inspect_cd, flg):
    result = []
    if operator.eq(flg, "First"):
        defect_tablename = 't_1_defect_1st'
    else:
        defect_tablename = 't_1_defect_2nd'
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT\
                    defect.serial_cd,\
                    defect.inspect_cd,\
                    inspect.inspect_name,\
                    vendor.vendor_text \
                FROM\
                    (defect_tablename) defect\
                LEFT JOIN m_inspect inspect \
                  ON defect.inspect_cd = inspect.inspect_cd\
                LEFT JOIN m_ppp_vendor vendor \
                  ON substring( defect.serial_cd FROM 1 FOR 3 ) = vendor.ppp_cd \
                WHERE\
                    defect.data_seq = %s \
                    AND defect.inspect_cd = %s \
                ORDER BY defect.serial_cd"
        sql = sql.replace("(defect_tablename)", defect_tablename)
        cur.execute(sql, (data_seq, inspect_cd))
        rows = cur.fetchall()
        for row in rows:
            result.append({"serial_cd": row[0], "inspect_cd": row[1], "inspect_name": row[2], "vendor_text": row[3], })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


# def get_exceldata(model_name,mode_name,assy_text,plan_date,in_quantity,out_quantity,before_quantity,after_quantity):
#     result = []
#     try:
#         cur = connections[model_name].cursor()
#         sql = 'INSERT INTO m_plan(mode_name,assy_text,plan_date,in_quantity,out_quantity,before_quantity,after_quantity)VALUES(%s,%s,%s,%s,%s,%s,%s)'
#         cur.executemany(sql,(mode_name, assy_text, plan_date, in_quantity, out_quantity, before_quantity, after_quantity,))
#         connections[model_name].commit
#         result = {'status': "success"}
#     except BaseException as exp:
#         print(exp)
#         result = {'status': "fail"}
#     connections[model_name].close()
#     return result

def get_exceldata(model_name, param):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = 'INSERT INTO m_plan(mode_name,assy_text,plan_date,in_quantity,out_quantity,before_quantity,after_quantity,revision)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.executemany(sql, param)
        connections[model_name].commit
        result = {'status': "success"}
    except BaseException as exp:
        print(exp)
        result = {'status': "fail"}
    connections[model_name].close()
    return result


def deletePlanData(model_name, plan_date):
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT to_regclass('m_plan') is not null as EXISTS")
        rows = cur.fetchall()
        for row in rows:
            exits = row[0]
        if exits:
            cur.execute('DELETE FROM m_plan WHERE plan_date = %s;', (plan_date,))
            connections[model_name].commit
    except BaseException as exp:
        print(exp)
    connections[model_name].close()


def get_inputQuantity(model_name, from_process_at, to_process_at, time_type, getSum, line, lineNum):
    result = []
    subSql_sum1 = ""
    subSql_sum2 = ""
    try:
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( input_quantity ) AS sum_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"

        cur = connections[model_name].cursor()

        if line != "" and line != "All Line":
            sql = subSql_sum1 + "SELECT\
                                first_process.assy_text,\
                                first_process.process_at,\
                                auto_ok.process_id,\
                                auto_ok.ok_quantity AS first_ok_quantity,\
                                COALESCE(auto_ng.ng_quantity,0) AS first_ng_quantity,\
                                ( ok_quantity + COALESCE(ng_quantity,0) ) AS input_quantity \
                            FROM\
                                (\
                            SELECT\
                                process_id,\
                                process_at,\
                                SUM( quantity ) AS ok_quantity \
                            FROM\
                                (\
                            SELECT\
                                process_id,\
                                process_at,\
                                quantity \
                            FROM\
                                t_1_auto_io_" + lineNum + " \
                            WHERE\
                                process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' \
                                AND judge_text = 'ok' \
                                AND time_part = %s \
                                AND line_cd = '(line_cd)' \
                                ) AS auto \
                            GROUP BY\
                                process_id,\
                                process_at \
                                ) AS auto_ok\
                                INNER JOIN (\
                            SELECT\
                                assy_text,\
                                process_at,\
                                MIN( process_id ) AS process_id \
                            FROM\
                                (\
                            SELECT\
                                assy_text,\
                                auto2.process_at,\
                                auto2.process_id,\
                                SUM( auto2.quantity ) \
                            FROM\
                                m_assy\
                                INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id\
                                AND auto2.judge_text = 'ok' \
                                AND auto2.quantity > 0 \
                                AND time_part = %s \
                                AND process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' \
                                AND line_cd = '(line_cd)' \
                            GROUP BY\
                                assy_text,\
                                process_at,\
                                auto2.process_id \
                                ) AS a \
                            GROUP BY\
                                assy_text,\
                                process_at \
                                ) AS first_process ON auto_ok.process_id = first_process.process_id \
                                AND auto_ok.process_at = first_process.process_at\
                                LEFT JOIN (\
                            SELECT\
                                process_id,\
                                process_at,\
                                SUM( quantity ) AS ng_quantity \
                            FROM\
                                ( SELECT process_id, process_at, quantity FROM t_1_auto_io_" + lineNum + " WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND judge_text = 'ng' AND time_part = %s \
                                    AND line_cd = '(line_cd)' \
                                ) AS auto \
                            GROUP BY\
                                process_id,\
                                process_at \
                                ) AS auto_ng ON auto_ng.process_id = first_process.process_id \
                                AND auto_ng.process_at = first_process.process_at \
                            ORDER BY\
                                auto_ok.process_id,\
                                first_process.process_at" + subSql_sum2
            sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at) \
                .replace("(line_cd)", line)
            cur.execute(sql, (time_type, time_type, time_type,))
        else:
            sql = subSql_sum1 + "SELECT\
                                t1.assy_text,\
                                t1.process_at,\
                                first_process.process_id,\
                                t1.first_ok_quantity,\
                                t1.first_ng_quantity,\
                                ( t1.first_ok_quantity + t1.first_ng_quantity ) AS input_quantity \
                            FROM\
                                (\
                            SELECT \
                                first_process.assy_text,\
                                first_process.process_at,\
                                SUM( auto_ok.ok_quantity ) AS first_ok_quantity,\
                                SUM( COALESCE ( auto_ng.ng_quantity, 0 ) ) AS first_ng_quantity \
                            FROM\
                                (\
                            SELECT \
                                line_cd,\
                                process_id,\
                                process_at,\
                                SUM( quantity ) AS ok_quantity \
                            FROM\
                                (\
                            SELECT \
                                line_cd,\
                                process_id,\
                                process_at,\
                                quantity \
                            FROM \
                                t_1_auto_io_" + lineNum + " \
                            WHERE \
                                process_at >= '(from_process_at)' \
                                AND process_at <= '(to_process_at)' \
                                AND judge_text = 'ok' \
                                AND time_part = %s \
                                ) AS auto \
                            GROUP BY \
                                line_cd,process_id,process_at \
                                ) AS auto_ok \
                                INNER JOIN (\
                            SELECT\
                                line_cd,\
                                assy_text,\
                                process_at,\
                                MIN( process_id ) AS process_id \
                            FROM\
                                (\
                            SELECT \
                                line_cd,\
                                assy_text,\
                                auto2.process_at,\
                                auto2.process_id,\
                                SUM( auto2.quantity ) \
                            FROM \
                                m_assy \
                                INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id \
                                AND auto2.judge_text = 'ok' \
                                AND auto2.quantity > 0 \
                                AND time_part = %s \
                                AND process_at >= '(from_process_at)' \
                                AND process_at <= '(to_process_at)' \
                            GROUP BY \
                                line_cd,assy_text,process_at,auto2.process_id \
                                ) AS A \
                            GROUP BY \
                                line_cd,assy_text,process_at \
                                ) AS first_process ON auto_ok.process_id = first_process.process_id \
                                AND auto_ok.process_at = first_process.process_at \
                                AND auto_ok.line_cd = first_process.line_cd \
                                LEFT JOIN (\
                            SELECT \
                                line_cd,\
                                process_id,\
                                process_at,\
                                SUM( quantity ) AS ng_quantity \
                            FROM\
                                (\
                            SELECT \
                                line_cd,\
                                process_id,\
                                process_at,\
                                quantity \
                            FROM \
                                t_1_auto_io_" + lineNum + " \
                            WHERE \
                                process_at >= '(from_process_at)' \
                                AND process_at <= '(to_process_at)' \
                                AND judge_text = 'ng' \
                                AND time_part = %s \
                                ) AS auto \
                            GROUP BY \
                                line_cd,process_id,process_at \
                                ) AS auto_ng ON auto_ng.process_id = first_process.process_id \
                                AND auto_ng.process_at = first_process.process_at \
                                AND auto_ng.line_cd = first_process.line_cd \
                            GROUP BY \
                                first_process.assy_text,\
                                first_process.process_at\
                                ) AS t1 \
                                INNER JOIN (\
                            SELECT \
                                assy_text,\
                                process_at,\
                                MIN( process_id ) AS process_id \
                            FROM\
                                (\
                            SELECT \
                                assy_text,\
                                auto2.process_at,\
                                auto2.process_id,\
                                SUM( auto2.quantity ) \
                            FROM \
                                m_assy \
                                INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id \
                                AND auto2.judge_text = 'ok' \
                                AND auto2.quantity > 0 \
                                AND time_part = %s \
                                AND process_at >= '(from_process_at)' \
                                AND process_at <= '(to_process_at)' \
                            GROUP BY \
                                assy_text,process_at,auto2.process_id \
                                ) AS A \
                            GROUP BY \
                                assy_text,process_at \
                                ) AS first_process ON t1.assy_text = first_process.assy_text \
                                AND t1.process_at = first_process.process_at \
                            ORDER BY \
                                process_id,process_at" + subSql_sum2
            sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at)
            cur.execute(sql, (time_type, time_type, time_type, time_type,))

        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })
        else:
            for row in rows:
                result.append({"assy_text": row[0], "process_at": str(row[1]), "process_id": row[2], \
                               "first_ok_quantity": int(row[3]), "first_ng_quantity": int(row[4]), \
                               "input_quantity": int(row[5]), })

    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_outputQuantity(model_name, from_process_at, to_process_at, time_type, getSum, line, lineNum):
    result = []
    subSql_sum1 = ""
    subSql_sum2 = ""
    try:
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( output_quantity ) AS sum_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"

        cur = connections[model_name].cursor()

        if line != "" and line != "All Line":
            sql = subSql_sum1 + "SELECT\
                                last_process.assy_text,\
                                auto_ok.process_at,\
                                auto_ok.process_id,\
                                auto_ok.ok_quantity AS output_quantity\
                            FROM\
                                (\
                            SELECT\
                                process_id,\
                                process_at,\
                                SUM( quantity ) AS ok_quantity\
                            FROM\
                                (\
                            SELECT\
                                process_id,\
                                process_at,\
                                quantity\
                            FROM\
                                t_1_auto_io_" + lineNum + "\
                            WHERE\
                                process_at >= '(from_process_at)' AND process_at <= '(to_process_at)'\
                                AND judge_text = 'ok' \
                                AND time_part = %s \
                                AND line_cd = '(line_cd)' \
                                ) AS auto\
                            GROUP BY\
                                process_id,process_at\
                                ) AS auto_ok\
                                INNER JOIN (\
                            SELECT\
                                assy_text,\
                                process_at,\
                                MAX( process_id ) AS process_id\
                            FROM\
                                (\
                            SELECT\
                                assy_text,\
                                auto2.process_at,\
                                auto2.process_id,\
                                SUM( auto2.quantity )\
                            FROM\
                                m_assy\
                                INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id\
                                AND auto2.judge_text = 'ok'\
                                AND auto2.quantity > 0  \
                                AND time_part = %s \
                                AND process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' \
                                AND line_cd = '(line_cd)' \
                            GROUP BY\
                                assy_text,\
                                process_at,\
                                auto2.process_id\
                            ORDER BY\
                                assy_text,\
                                process_at,\
                                process_id\
                                ) AS a\
                            GROUP BY\
                                assy_text,process_at\
                                ) AS last_process ON auto_ok.process_id = last_process.process_id\
                                AND auto_ok.process_at = last_process.process_at\
                            ORDER BY auto_ok.process_id,auto_ok.process_at" + subSql_sum2
            sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at) \
                .replace("(line_cd)", line)
            cur.execute(sql, (time_type, time_type,))
        else:
            sql = subSql_sum1 + "SELECT\
                        t1.assy_text,\
                        t1.process_at,\
                        last_process.process_id,\
                        t1.output_quantity \
                    FROM\
                        (\
                    SELECT \
                        last_process.assy_text,\
                        last_process.process_at,\
                        SUM( auto_ok.ok_quantity ) AS output_quantity \
                    FROM\
                        (\
                    SELECT \
                        line_cd,\
                        process_id,\
                        process_at,\
                        SUM( quantity ) AS ok_quantity \
                    FROM\
                        (\
                    SELECT \
                        line_cd,\
                        process_id,\
                        process_at,\
                        quantity \
                    FROM \
                        t_1_auto_io_" + lineNum + " \
                    WHERE \
                        process_at >= '(from_process_at)' \
                        AND process_at <= '(to_process_at)' \
                        AND judge_text = 'ok' \
                        AND time_part = %s \
                        ) AS auto \
                    GROUP BY \
                        line_cd,process_id,process_at \
                        ) AS auto_ok \
                        INNER JOIN (\
                    SELECT \
                        line_cd,\
                        assy_text,\
                        process_at,\
                        MAX( process_id ) AS process_id \
                    FROM\
                        (\
                    SELECT \
                        line_cd,\
                        assy_text,\
                        auto2.process_at,\
                        auto2.process_id,\
                        SUM( auto2.quantity ) \
                    FROM \
                        m_assy \
                        INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id \
                        AND auto2.judge_text = 'ok' \
                        AND auto2.quantity > 0 \
                        AND time_part = %s \
                        AND process_at >= '(from_process_at)' \
                        AND process_at <= '(to_process_at)' \
                    GROUP BY \
                        line_cd,assy_text,process_at,auto2.process_id \
                        ) AS A \
                    GROUP BY \
                        line_cd,assy_text,process_at \
                        ) AS last_process ON auto_ok.process_id = last_process.process_id \
                        AND auto_ok.process_at = last_process.process_at \
                        AND auto_ok.line_cd = last_process.line_cd \
                    GROUP BY \
                        last_process.assy_text,last_process.process_at \
                        ) AS t1 \
                        INNER JOIN (\
                    SELECT \
                        assy_text,\
                        process_at,\
                        MAX( process_id ) AS process_id \
                    FROM\
                        (\
                    SELECT \
                        assy_text,\
                        auto2.process_at,\
                        auto2.process_id,\
                        SUM( auto2.quantity ) \
                    FROM \
                        m_assy \
                        INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id \
                        AND auto2.judge_text = 'ok' \
                        AND auto2.quantity > 0 \
                        AND time_part = %s \
                        AND process_at >= '(from_process_at)' \
                        AND process_at <= '(to_process_at)' \
                    GROUP BY \
                        assy_text,process_at,auto2.process_id \
                        ) AS A \
                    GROUP BY \
                        assy_text,process_at \
                        ) AS last_process ON t1.assy_text = last_process.assy_text \
                        AND t1.process_at = last_process.process_at \
                    ORDER BY \
                        process_id,process_at" + subSql_sum2
            sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at)
            cur.execute(sql, (time_type, time_type, time_type,))

        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })
        else:
            for row in rows:
                result.append({"assy_text": row[0], "process_at": str(row[1]), "process_id": row[2],
                               "output_quantity": int(row[3]), })

    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_ngQuantity(model_name, from_process_at, to_process_at, time_type, getSum, line, lineNum):
    # process_at_list = get_periodDate(from_process_at, to_process_at)
    # process_at_list.append(time_type)
    subSql_sum1 = ""
    subSql_sum2 = ""
    subSql_line = ""
    result = []
    try:
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( ng_quantity ) AS sum_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
        if line != "" and line != "All Line":
            subSql_line = " AND line_cd = '" + line + "' "
        cur = connections[model_name].cursor()
        sql = subSql_sum1 + "SELECT\
                    ng_total.assy_text,\
                    process_at,\
                    ng_quantity,\
                    assy.p_id \
                FROM\
                    (\
                SELECT\
                    m_assy.assy_text,\
                    auto_ng.process_at,\
                    SUM( auto_ng.ng_quantity ) AS ng_quantity \
                FROM\
                    m_assy\
                    INNER JOIN (\
                SELECT\
                    process_id,\
                    process_at,\
                    SUM( quantity ) AS ng_quantity \
                FROM\
                    (\
                SELECT\
                    process_id,\
                    process_at,\
                    quantity \
                FROM\
                    t_1_auto_io_" + lineNum + " \
                WHERE\
                    process_at >= %s \
                    AND process_at <= %s \
                    AND judge_text = 'ng' \
                    AND time_part = %s" + subSql_line + \
              ") AS auto \
              GROUP BY\
                  process_id,\
                  process_at \
                  ) AS auto_ng ON m_assy.process_id = auto_ng.process_id \
              GROUP BY\
                  m_assy.assy_text,\
                  auto_ng.process_at \
                  ) ng_total\
                  LEFT JOIN ( SELECT DISTINCT assy_text, MIN( process_id ) AS p_id FROM m_assy GROUP BY assy_text ) assy ON assy.assy_text = ng_total.assy_text \
              ORDER BY assy.p_id" + subSql_sum2

        cur.execute(sql, (from_process_at, to_process_at, time_type,))
        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })
        else:
            for row in rows:
                result.append({"assy_text": row[0], "process_at": str(row[1]), "ng_quantity": int(row[2]), })

    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_periodDate(begin_date, end_date):
    date_list = []
    if operator.eq(end_date, '') == False:
        begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += datetime.timedelta(days=1)
    else:
        date_list.append(begin_date)
    return date_list


def getVariableConvert(actual_y1, actual_y2):
    actual_y = []
    y1 = actual_y1
    y2 = actual_y2
    if operator.eq(actual_y1, "-"):
        y1 = float(0)
        y2 = float(0)

    actual_y = [y1, y2]
    return actual_y


# 1和2
def get_lineFirstProcess(model_name, process_at, lineNum):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT \
                    line_cd,\
                    assy_text,\
                    dayornight,\
                    MIN ( process_id ) AS process_id \
                FROM\
                    (\
                SELECT \
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    auto2.time_part AS dayornight,\
                    SUM ( auto2.quantity ) \
                FROM \
                    m_assy \
                    INNER JOIN t_1_auto_io_" + lineNum + " auto2 ON m_assy.process_id = auto2.process_id \
                    AND auto2.judge_text = 'ok' \
                    AND process_at = '(process_at)' \
                    AND ( time_part = 'Day' OR time_part = 'Night' ) \
                GROUP BY \
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    dayornight \
                    ) AS A \
                GROUP BY \
                    line_cd,assy_text,dayornight"
        sql = sql.replace("(process_at)", process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"line_cd": row[0], "assy_text": row[1], "dayornight": row[2], "process_id": row[3], })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_inputQuantity_line(model_name, process_at, lineNum):
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
                 AND (time_part = 'Day' OR time_part = 'Night')\
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
                    AND auto2.judge_text = 'ok'\
                    AND process_at = '(process_at)' \
                    AND (time_part = 'Day' OR time_part = 'Night')\
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
                    AND (time_part = 'Day' OR time_part = 'Night')\
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
            result.append(
                {"line_cd": row[0], "assy_text": row[1], "process_id": row[2], "first_ok_quantity": int(row[3]),
                 "first_ng_quantity": int(row[4]), "dayornight": row[5], "input_quantity": int(row[6]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_outputQuantity_line(model_name, process_at, lineNum):
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
                    process_at = '(process_at)'\
                    AND judge_text = 'ok'\
                    AND (time_part = 'Day' OR time_part = 'Night')\
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
                    AND auto2.judge_text = 'ok'\
                    AND auto2.quantity > 0\
                    AND process_at = '(process_at)'\
                    AND (time_part = 'Day' OR time_part = 'Night')\
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
            result.append({"line_cd": row[0], "assy_text": row[1], "process_id": row[2], "dayornight": row[3],
                           "output_quantity": int(row[4]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_ngQuantity_line(model_name, process_at, lineNum):
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
                    AND (time_part = 'Day' OR time_part = 'Night')\
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
            result.append({"line_cd": row[0], "assy_text": row[1], "dayornight": row[2], "ng_quantity": int(row[3]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_inputQuantity_sumOfLine(model_name, from_process_at, to_process_at, assy, getSum):
    subSql_assy = ""
    subSql_sum1 = ""
    subSql_sum2 = ""
    result = []
    try:
        if assy != '' and assy is not None:
            subSql_assy = "WHERE m_assy.assy_text = '" + assy + "'"
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( input_quantity ) AS sum_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
        cur = connections[model_name].cursor()

        sql = subSql_sum1 + "SELECT\
                    line_cd,\
                    process_at,\
                    SUM( input_quantity ) AS input_quantity \
                FROM\
                    (\
                SELECT\
                    first_process.line_cd,\
                    first_process.assy_text,\
                    auto_ok.process_at,\
                    auto_ok.process_id,\
                    auto_ok.ok_quantity AS first_ok_quantity,\
                    COALESCE ( auto_ng.ng_quantity, 0 ) AS first_ng_quantity,\
                    ( ok_quantity + COALESCE ( ng_quantity, 0 ) ) AS input_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    process_at,\
                    SUM( quantity ) AS ok_quantity \
                FROM\
                    t_1_auto_io_2nd\
                WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND time_part = 'All' AND judge_text = 'ok' \
                GROUP BY\
                    line_cd,\
                    process_id, \
                    process_at\
                    ) AS auto_ok\
                    INNER JOIN (\
                SELECT\
                    line_cd,\
                    assy_text,\
                    process_at,\
                    MIN( process_id ) AS process_id \
                FROM\
                    (\
                SELECT\
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    process_at,\
                    SUM( auto2.quantity )\
                FROM\
                    m_assy\
                    INNER JOIN t_1_auto_io_2nd auto2 ON m_assy.process_id = auto2.process_id \
                    AND auto2.quantity > 0 \
                    AND auto2.judge_text = 'ok' \
                    AND time_part = 'All'\
                    AND process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' " + subSql_assy + \
              " GROUP BY\
                  auto2.line_cd,\
                  assy_text,\
                  auto2.process_id, \
                  process_at\
              ORDER BY\
                  assy_text,\
                  process_id \
                  ) AS a \
              GROUP BY\
                  line_cd,\
                  assy_text, \
                  process_at\
                  ) AS first_process ON auto_ok.process_id = first_process.process_id \
                  AND auto_ok.line_cd = first_process.line_cd\
                  AND auto_ok.process_at = first_process.process_at\
                  LEFT JOIN (\
              SELECT\
                  line_cd,\
                  process_id,\
                  process_at,\
                  SUM( quantity ) AS ng_quantity \
              FROM\
                t_1_auto_io_2nd\
              WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND time_part = 'All' AND judge_text = 'ng'\
              GROUP BY\
                  line_cd,\
                  process_id, \
                  process_at\
                  ) AS auto_ng ON auto_ng.process_id = first_process.process_id \
                  AND auto_ng.line_cd = first_process.line_cd \
                AND auto_ng.process_at = auto_ok.process_at\
              ORDER BY\
                  first_process.line_cd,\
                  auto_ok.process_id \
                  ) AS MAIN \
              GROUP BY line_cd,process_at \
              ORDER BY line_cd,process_at" + subSql_sum2
        sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })
        else:
            for row in rows:
                result.append({"line_cd": row[0], "process_at": str(row[1]), "input_quantity": int(row[2]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_outputQuantity_sumOfLine(model_name, from_process_at, to_process_at, assy, getSum):
    subSql_assy = ""
    subSql_sum1 = ""
    subSql_sum2 = ""
    result = []
    try:
        if assy != '' and assy is not None:
            subSql_assy = "WHERE m_assy.assy_text = '" + assy + "'"
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( output_quantity ) AS sum_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
        cur = connections[model_name].cursor()
        sql = subSql_sum1 + "SELECT\
                    line_cd,\
                    process_at,\
                    SUM( output_quantity ) AS output_quantity\
                FROM\
                    (\
                SELECT DISTINCT\
                    last_process.line_cd,\
                    last_process.assy_text,\
                    auto_ok.process_id,\
                    auto_ok.process_at,\
                    auto_ok.ok_quantity AS output_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    process_at,\
                    SUM( quantity ) AS ok_quantity \
                FROM\
                    t_1_auto_io_2nd\
                WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND time_part = 'All' AND judge_text = 'ok' \
                GROUP BY\
                    line_cd,\
                    process_id, \
                    process_at\
                    ) AS auto_ok\
                    INNER JOIN (\
                SELECT\
                    line_cd,\
                    assy_text,\
                    process_at,\
                    MAX( process_id ) AS process_id \
                FROM\
                    (\
                SELECT\
                    auto2.line_cd,\
                    assy_text,\
                    auto2.process_id,\
                    process_at,\
                    SUM( auto2.quantity ) \
                FROM\
                    m_assy\
                    INNER JOIN t_1_auto_io_2nd auto2 ON m_assy.process_id = auto2.process_id \
                    AND auto2.judge_text = 'ok' \
                    AND auto2.quantity > 0 \
                    AND time_part = 'All'\
                    AND process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' " + subSql_assy + \
              " GROUP BY\
                  auto2.line_cd,\
                  assy_text,\
                  auto2.process_id, \
                  process_at\
                  ) AS a \
              GROUP BY\
                  line_cd,\
                  assy_text, \
                  process_at\
                  ) AS last_process ON auto_ok.process_id = last_process.process_id \
                  AND auto_ok.line_cd = last_process.line_cd \
                  AND auto_ok.process_at = last_process.process_at\
              ORDER BY\
                  last_process.line_cd,\
                  auto_ok.process_id \
                  ) AS MAIN \
              GROUP BY line_cd,process_at \
              ORDER BY line_cd,process_at" + subSql_sum2
        sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })
        else:
            for row in rows:
                result.append({"line_cd": row[0], "process_at": str(row[1]), "output_quantity": int(row[2]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_ngQuantity_sumOfLine(model_name, from_process_at, to_process_at, assy, getSum):
    subSql_assy = ""
    subSql_sum1 = ""
    subSql_sum2 = ""
    result = []
    try:
        if assy != '' and assy is not None:
            subSql_assy = "WHERE m_assy.assy_text = '" + assy + "'"
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( ng_quantity ) AS sum_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
        cur = connections[model_name].cursor()
        sql = subSql_sum1 + "SELECT\
                    line_cd,\
                    process_at,\
                    SUM( ng_quantity ) AS ng_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    assy_text,\
                    process_at,\
                    SUM( ng_quantity ) AS ng_quantity \
                FROM\
                    (\
                SELECT DISTINCT\
                    auto_ng.line_cd,\
                    m_assy.assy_text,\
                    auto_ng.process_id,\
                    process_at,\
                    auto_ng.ng_quantity AS ng_quantity \
                FROM\
                    m_assy\
                    INNER JOIN (\
                SELECT\
                    line_cd,\
                    process_id,\
                    process_at,\
                    SUM( quantity ) AS ng_quantity \
                FROM\
                    t_1_auto_io_2nd \
                WHERE\
                    process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' \
                    AND judge_text = 'ng' \
                    AND time_part = 'All'\
                GROUP BY\
                    line_cd,\
                    process_id, \
                    process_at\
                    ) AS auto_ng ON m_assy.process_id = auto_ng.process_id " + subSql_assy + \
              " ) AS t1 \
           GROUP BY\
               line_cd,\
               assy_text, \
               process_at\
               ) AS main \
           GROUP BY\
               line_cd,process_at \
           ORDER BY line_cd,process_at" + subSql_sum2
        sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append({"process_at": str(row[0]), "sum_quantity": int(row[1]), })
        else:
            for row in rows:
                result.append({"line_cd": row[0], "process_at": str(row[1]), "ng_quantity": int(row[2]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_quantity_sumOfProcess(model_name, from_process_at, to_process_at, getSum):
    result = []
    subSql_sum1 = ""
    subSql_sum2 = ""
    try:
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( output_quantity ) AS sum_output_quantity, \
                        SUM( ng_quantity ) AS sum_ng_quantity,SUM( input_quantity ) AS sum_input_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
        cur = connections[model_name].cursor()
        sql = subSql_sum1 + "SELECT\
                    m_assy.process_cd,\
                    m_assy.process_id,\
                    auto_ok.process_at,\
                    COALESCE ( auto_ok.quantity, 0 ) AS output_quantity,\
                    COALESCE ( auto_ng.quantity, 0 ) AS ng_quantity,\
                    COALESCE ( auto_ok.quantity, 0 ) + COALESCE ( auto_ng.quantity, 0 ) AS input_quantity \
                FROM\
                    m_assy\
                    INNER JOIN ( SELECT process_id,process_at,SUM( quantity ) AS quantity FROM t_1_auto_io_2nd WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND judge_text = 'ok' AND time_part = 'All' GROUP BY process_id,process_at ) AS auto_ok ON m_assy.process_id = auto_ok.process_id\
                    INNER JOIN ( SELECT process_id,process_at,SUM( quantity ) AS quantity FROM t_1_auto_io_2nd WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND judge_text = 'ng' AND time_part = 'All' GROUP BY process_id,process_at ) AS auto_ng ON m_assy.process_id = auto_ng.process_id \
                  AND auto_ok.process_at = auto_ng.process_at\
                ORDER BY process_id,process_at" + subSql_sum2
        sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at)
        cur.execute(sql)
        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append(
                    {"process_at": str(row[0]), "sum_output_quantity": int(row[1]), "sum_ng_quantity": int(row[2]),
                     "sum_input_quantity": int(row[3]), })
        else:
            for row in rows:
                result.append({"process_cd": row[0], "process_id": row[1], "process_at": str(row[2]),
                               "output_quantity": int(row[3]), "ng_quantity": int(row[4]), \
                               "input_quantity": int(row[5]), })

    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_quantity_sumOfLineProcess(model_name, from_process_at, to_process_at, process_cd, getSum):
    subSql_sum1 = ""
    subSql_sum2 = ""
    result = []
    try:
        if getSum:
            subSql_sum1 = "SELECT process_at,SUM( output_quantity ) AS sum_output_quantity, \
                        SUM( ng_quantity ) AS sum_ng_quantity,SUM( input_quantity ) AS sum_input_quantity FROM("
            subSql_sum2 = ")AS TB GROUP BY process_at ORDER BY process_at"
        cur = connections[model_name].cursor()
        sql = subSql_sum1 + "SELECT\
                    auto_ok.line_cd,\
                    m_assy.process_cd,\
                    auto_ok.process_at,\
                    COALESCE (auto_ok.ok_quantity, 0) AS output_quantity,\
                    COALESCE ( auto_ng.ng_quantity, 0 ) AS ng_quantity,\
                    ( COALESCE (auto_ok.ok_quantity, 0) + COALESCE ( ng_quantity, 0 ) ) AS input_quantity \
                FROM\
                    (\
                SELECT\
                    line_cd,\
                    process_id,\
                    process_at,\
                    SUM( quantity ) AS ok_quantity \
                FROM\
                  t_1_auto_io_2nd\
                WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND judge_text = 'ok' AND time_part = 'All' \
                GROUP BY\
                    line_cd,\
                    process_id, \
                    process_at\
                    ) AS auto_ok\
                INNER JOIN m_assy\
                ON m_assy.process_id = auto_ok.process_id\
                    LEFT JOIN (\
                SELECT\
                    line_cd,\
                    process_id,\
                    process_at,\
                    SUM( quantity ) AS ng_quantity \
                FROM\
                  t_1_auto_io_2nd\
                WHERE process_at >= '(from_process_at)' AND process_at <= '(to_process_at)' AND judge_text = 'ng' AND time_part = 'All' \
                GROUP BY\
                    line_cd,\
                    process_id, \
                    process_at\
                    ) AS auto_ng ON auto_ng.process_id = auto_ok.process_id \
                    and auto_ng.line_cd = auto_ok.line_cd\
                AND auto_ng.process_at = auto_ok.process_at\
                WHERE m_assy.process_cd = '(process_cd)'\
                ORDER BY\
                    auto_ok.line_cd,\
                    auto_ok.process_at" + subSql_sum2
        sql = sql.replace("(from_process_at)", from_process_at).replace("(to_process_at)", to_process_at).replace(
            "(process_cd)", process_cd)
        cur.execute(sql)
        rows = cur.fetchall()
        if getSum:
            for row in rows:
                result.append(
                    {"process_at": str(row[0]), "sum_output_quantity": int(row[1]), "sum_ng_quantity": int(row[2]),
                     "sum_input_quantity": int(row[3]), })
        else:
            for row in rows:
                result.append(
                    {"line_cd": row[0], "process_cd": row[1], "process_at": str(row[2]), "output_quantity": int(row[3]), \
                     "ng_quantity": int(row[4]), "input_quantity": int(row[5]), })

    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_allAssy(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT\
                    assy_text \
                FROM\
                    ( SELECT assy_text, process_id, ROW_NUMBER ( ) OVER ( PARTITION BY assy_text ORDER BY process_id ) RANK FROM m_assy ) AS A1 \
                WHERE\
                    RANK = 1 \
                ORDER BY process_id"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_allAssyAndProcessId(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT\
                    assy_text, \
                    process_id\
                FROM\
                    ( SELECT assy_text, process_id, ROW_NUMBER ( ) OVER ( PARTITION BY assy_text ORDER BY process_id ) RANK FROM m_assy ) AS A1 \
                WHERE\
                    RANK = 1 \
                ORDER BY process_id"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"assy_text": row[0], "process_id": row[1]})
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_allProcess(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT\
                    process_cd,process_id\
                FROM\
                    m_assy\
                ORDER BY process_id"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"process_cd": row[0], "process_id": row[1]})
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_allLines(model_name):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT \
                    line_cd \
                FROM\
                    m_work \
                ORDER BY line_cd"
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append(row[0])
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_summary_offset(model_name, date):
    result = []
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT\
                    assy.assy_text,\
                    COALESCE ( summary.ng_count, 0 ) AS ng_count\
                FROM\
                    m_assy assy\
                    LEFT JOIN m_summary_offset summary ON assy.assy_text = summary.assy_text\
                    AND summary.date = '(date)' \
                ORDER BY assy.assy_text"
        sql = sql.replace("(date)", date)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            result.append({"assy_text": row[0], "ng_count": int(row[1]), })
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_summaryDetail(model_name, search_date, time_type, lineNum):
    models_ngreport.check_planTable(model_name)
    # process_at = (datetime.date.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    process_at = search_date
    summary_detail = []
    result = {}
    # input
    result_inputQuantity = get_inputQuantity(model_name, process_at, process_at, time_type, False, '', lineNum)  # 1和2
    if result_inputQuantity == 101 or result_inputQuantity == 102:
        return result_inputQuantity
    # output
    result_outputQuantity = get_outputQuantity(model_name, process_at, process_at, time_type, False, '', lineNum)  # 1和2
    if result_outputQuantity == 101 or result_outputQuantity == 102:
        return result_outputQuantity
    # ng
    result_ngQuantity = get_ngQuantity(model_name, process_at, process_at, time_type, False, '', lineNum)  # 1和2
    if result_ngQuantity == 101 or result_ngQuantity == 102:
        return result_ngQuantity
    # summary_offset的ng的取得
    result_summaryOffset_ng = get_summary_offset(model_name, process_at)
    if result_summaryOffset_ng == 101 or result_summaryOffset_ng == 102:
        return result_summaryOffset_ng
    try:
        database_list = get_config("database")
        assyDic = {}
        formulaDic = {}
        fpy_sub_formula_dic = {}
        for row in database_list:
            if operator.eq(row['MODEL'], model_name):
                # 从配置文件里取得ASSY
                assyDic = row['ASSY']
                # 从配置文件里取得FORMULA
                formulaDic = row['FORMULA_SUMMARY']
                break

        fpy_sub_formula = formulaDic["Assembly Yield(sub+main)"]
        assembly_yield_sub_formula = formulaDic["Assy Yield(main)"]
        fpy_formula = formulaDic["FPY(sub+main)"]
        assembly_yield_formula = formulaDic["FPY(main)"]
        before_formula = formulaDic["Before"]
        after_formula = formulaDic["After"]

        # 将Assembly Yield(sub+main)的计算公式存放到字典
        for i in range(len(fpy_sub_formula)):
            fpy_sub_formula_dic[i] = fpy_sub_formula[i].split(',')

        cur = connections[model_name].cursor()
        cur.execute("SELECT\
                        assy_text,\
                        in_quantity,\
                        out_quantity,\
                        before_quantity,\
                        after_quantity \
                    FROM\
                        (\
                    SELECT\
                        *,\
                        ROW_NUMBER () OVER ( PARTITION BY assy_text, in_quantity, out_quantity, before_quantity, after_quantity ORDER BY process_id ) RANK \
                    FROM\
                        (\
                    SELECT DISTINCT\
                        m_assy.assy_text,\
                        m_assy.process_id,\
                        in_quantity,\
                        out_quantity,\
                        before_quantity,\
                        after_quantity \
                    FROM\
                        m_assy\
                        LEFT JOIN m_plan ON m_plan.assy_text = m_assy.assy_text \
                        AND m_plan.mode_name = %s \
                        AND m_plan.plan_date = %s \
                        ) AS a1 \
                        ) AS a2 \
                    WHERE\
                        RANK = 1 \
                    ORDER BY process_id", (model_name, process_at))
        rows = cur.fetchall()
        for row in rows:
            actual_in = 0
            actual_out = 0
            actual_ng = 0
            actual_y2 = ""
            actual_y1 = ""
            plan_yield = "-"
            plan_in = "-"
            plan_out = "-"
            before = "-"
            after = "-"
            summaryOffset_ng = 0
            for inputrow in result_inputQuantity:
                if operator.eq(inputrow['assy_text'], row[0]):
                    actual_in = inputrow['input_quantity']
                    break
            for outputrow in result_outputQuantity:
                if operator.eq(outputrow['assy_text'], row[0]):
                    actual_out = outputrow['output_quantity']
                    break
            for ngrow in result_ngQuantity:
                if operator.eq(ngrow['assy_text'], row[0]):
                    actual_ng = ngrow['ng_quantity']
                    break

            if (time_type == 'All'):
                for summaryOffset_ngrow in result_summaryOffset_ng:
                    if operator.eq(summaryOffset_ngrow['assy_text'], row[0]):
                        summaryOffset_ng = summaryOffset_ngrow['ng_count']
                        break

            if row[1] is not None and row[1] >= 0:
                if row[1] > 0:
                    plan_yield = "%.2f%%" % (row[2] / (row[1] * 1.0) * 100)
                else:
                    plan_yield = "0.00%"
                plan_in = row[1]
            if row[2] is not None and row[2] >= 0:
                plan_out = row[2]
            if row[3] is not None and row[3] >= 0:
                before = row[3]
            if row[4] is not None and row[4] >= 0:
                after = row[4]

            if actual_in <= 0:
                actual_y1 = float(0)
            else:
                actual_y1 = actual_out / (actual_in * 1.0)
            if (time_type == 'All'):
                if actual_ng - summaryOffset_ng < 0:
                    actual_ng = 0
                else:
                    actual_ng = actual_ng - summaryOffset_ng
            if actual_out + actual_ng <= 0:
                actual_y2 = float(0)
            else:
                actual_y2 = actual_out / ((actual_out + actual_ng) * 1.0)
            actual_y2_y1 = actual_y2 - actual_y1

            summary_detail.append({"assy": row[0], "plan_in": plan_in, "plan_out": plan_out, \
                                   "plan_yield": plan_yield, \
                                   "before": before, "after": after, \
                                   "actual_in": str(actual_in), "actual_out": str(actual_out), \
                                   "actual_y2": actual_y2, "actual_y1": actual_y1, \
                                   "y2_y1": "%.2f%%" % (actual_y2_y1 * 1.0 * 100), "ng": int(actual_ng), })
        y1 = {}
        y2 = {}
        y1_temp = {}
        y2_temp = {}
        before = {}
        after = {}
        assy_len = len(assyDic)
        # get y1,y2,sum_before,sum_after
        for key in assyDic:
            before_value = 0
            after_value = 0
            for row in summary_detail:
                if operator.eq(row['assy'], assyDic[key]):
                    actual_y = getVariableConvert(row['actual_y1'], row['actual_y2'])
                    if actual_y[0] == float(0):
                        y1[int(key)] = float(1)
                        y1_temp[int(key)] = 'NP'
                    else:
                        y1[int(key)] = actual_y[0]
                        y1_temp[int(key)] = actual_y[0]
                    if actual_y[1] == float(0):
                        y2[int(key)] = float(1)
                        y2_temp[int(key)] = 'NP'
                    else:
                        y2[int(key)] = actual_y[1]
                        y2_temp[int(key)] = actual_y[1]

                    if operator.eq(row['before'], "-") == False:
                        before_value = row['before']
                    if operator.eq(row['after'], "-") == False:
                        after_value = row['after']
                    before[int(key)] = before_value
                    after[int(key)] = after_value
                    break
        # 字典排序
        sorted(y1.keys())
        sorted(y2.keys())
        sorted(y1_temp.keys())
        sorted(y2_temp.keys())
        sorted(before.keys())
        sorted(after.keys())
        index = 0
        # y1,y2不存在的情况，默认设为0.00
        while index < assy_len:
            if index not in y1.keys():
                y1[index] = float(1)
                y1_temp[index] = 'NP'
            if index not in y2.keys():
                y2[index] = float(1)
                y2_temp[index] = 'NP'
            if index not in before.keys():
                before[index] = float(0)
            if index not in after.keys():
                after[index] = float(0)
            index = index + 1

        y1_list = []
        y2_list = []
        y1_list_temp = []
        y2_list_temp = []
        before_list = []
        after_list = []
        # y1,y2,before,after的值保存在数组中
        for key in y1:
            y1_list.append(y1[key])
            y2_list.append(y2[key])
            y1_list_temp.append(y1_temp[key])
            y2_list_temp.append(y2_temp[key])
            before_list.append(before[key])
            after_list.append(after[key])

        # y1,y2转成百分比
        index = 0
        for row in summary_detail:
            if operator.eq(row['actual_y1'], "-") == False:
                summary_detail[index]['actual_y1'] = "%.2f%%" % (row['actual_y1'] * 100)
                summary_detail[index]['actual_y2'] = "%.2f%%" % (row['actual_y2'] * 100)
            index = index + 1

        # 计算y1_fpy_sub,y2_fpy_sub
        y1_fpy_sub_value = get_formula_value(y1_list, y1_list_temp, fpy_sub_formula)
        y2_fpy_sub_value = get_formula_value(y2_list, y2_list_temp, fpy_sub_formula)

        # 计算y1_assembly_yield_sub,y2_assembly_yield_sub
        y1_assembly_yield_sub_value = get_formula_value(y1_list, y1_list_temp, assembly_yield_sub_formula)
        y2_assembly_yield_sub_value = get_formula_value(y2_list, y2_list_temp, assembly_yield_sub_formula)

        # 计算y1_fpy,y2_fpy
        y1_fpy_value = get_formula_value(y1_list, y1_list_temp, fpy_formula)
        y2_fpy_value = get_formula_value(y2_list, y2_list_temp, fpy_formula)

        # 计算y1_assembly_yield,y2_assembly_yield
        y1_assembly_yield_value = get_formula_value(y1_list, y1_list_temp, assembly_yield_formula)
        y2_assembly_yield_value = get_formula_value(y2_list, y2_list_temp, assembly_yield_formula)

        # 计算sum_before
        sum_before = get_formula_value([], before_list, before_formula)
        # 计算sum_after
        sum_after = get_formula_value([], after_list, after_formula)

        summary = {"y1_fpy_sub": "%.2f%%" % (y1_fpy_sub_value * 100), \
                   "y1_assembly_yield_sub": "%.2f%%" % (y1_assembly_yield_sub_value * 100), \
                   "y1_fpy": "%.2f%%" % (y1_fpy_value * 100), \
                   "y1_assembly_yield": "%.2f%%" % (y1_assembly_yield_value * 100), \
                   "y2_fpy_sub": "%.2f%%" % (y2_fpy_sub_value * 100), \
                   "y2_assembly_yield_sub": "%.2f%%" % (y2_assembly_yield_sub_value * 100), \
                   "y2_fpy": "%.2f%%" % (y2_fpy_value * 100), \
                   "y2_assembly_yield": "%.2f%%" % (y2_assembly_yield_value * 100), \
                   "before_summary": sum_before, \
                   "after_summary": sum_after, }
        result['summary_detail'] = summary_detail
        result['summary'] = summary
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def get_lineSummaryDetail(model_name, search_date, time_type, lineNum):
    # process_at = (datetime.date.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    # yestoday = (datetime.date.today()- datetime.timedelta(days=1)).strftime('%m/%d')
    process_at = search_date
    temp = search_date.split('-')
    yestoday = temp[1] + "/" + temp[2]
    result = []
    header_data = []
    lineArr = []
    # 页面跳转用
    lines_hid = []
    lineArr_temp = []
    dateArr = []
    dayNightArr = []
    # 各个line的first processid的取得
    lineOfFirstPro = get_lineFirstProcess(model_name, process_at, lineNum)
    if lineOfFirstPro == 101 or lineOfFirstPro == 102:
        return lineOfFirstPro
    # input
    result_inputQuantity = get_inputQuantity_line(model_name, process_at, lineNum)
    if result_inputQuantity == 101 or result_inputQuantity == 102:
        return result_inputQuantity
    # output
    result_outputQuantity = get_outputQuantity_line(model_name, process_at, lineNum)
    if result_outputQuantity == 101 or result_outputQuantity == 102:
        return result_outputQuantity
    # ng
    result_ngQuantity = get_ngQuantity_line(model_name, process_at, lineNum)
    if result_ngQuantity == 101 or result_ngQuantity == 102:
        return result_ngQuantity
    # get assy
    assyArr = get_allAssy(model_name)
    if assyArr == 101 or assyArr == 102:
        return assyArr

    try:
        database_list = get_config("database")
        assyDic = {}
        assyDic_int = {}
        formulaDic = {}
        fpy_sub_formula_dic = {}
        for row in database_list:
            if operator.eq(row['MODEL'], model_name):
                # 从配置文件里取得ASSY
                assyDic = row['ASSY']
                # 从配置文件里取得FORMULA
                formulaDic = row['FORMULA_SUMMARY']
                break

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
                        and row['dayornight'] == inputrow['dayornight']:
                    flag = False
            if flag:
                result_inputQuantity.append(
                    {"line_cd": row['line_cd'], "assy_text": row['assy_text'], "process_id": row['process_id'],
                     "first_ok_quantity": 0, "first_ng_quantity": 0, "dayornight": row['dayornight'],
                     "input_quantity": 0, })

        # outputQuantity,ngQuantity合并到inputQuantity
        for inputrow in result_inputQuantity:
            output_quantity = 0
            for outputrow in result_outputQuantity:
                if operator.eq(outputrow['line_cd'], inputrow['line_cd']) and operator.eq(outputrow['assy_text'],
                                                                                          inputrow['assy_text']) \
                        and operator.eq(outputrow['dayornight'], inputrow['dayornight']):
                    output_quantity = outputrow['output_quantity']
                    break
            inputrow["output_quantity"] = output_quantity
            ng_quantity = 0
            for ngrow in result_ngQuantity:
                if operator.eq(ngrow['line_cd'], inputrow['line_cd']) and operator.eq(ngrow['assy_text'],
                                                                                      inputrow['assy_text']) \
                        and operator.eq(ngrow['dayornight'], inputrow['dayornight']):
                    ng_quantity = ngrow['ng_quantity']
                    break
            inputrow["ng_quantity"] = ng_quantity

            if inputrow["input_quantity"] > 0:
                inputrow["y1"] = inputrow["output_quantity"] / (inputrow["input_quantity"] * 1.0)
            else:
                inputrow["y1"] = 0
            if inputrow["output_quantity"] + inputrow["ng_quantity"] > 0:
                inputrow["y2"] = inputrow["output_quantity"] / (
                    (inputrow["output_quantity"] + inputrow["ng_quantity"]) * 1.0)
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
        for row in rows:
            if operator.eq(row[0], last_line) == False:
                lineArr.append(row[0])
                lineArr_temp.append(row[0])
                dateArr.append(yestoday)
                dateArr.append(yestoday)
                dayNightArr.append("Day")
                dayNightArr.append("Night")
                last_line = row[0]
                lines_hid.append(row[0])
                lines_hid.append(row[0])

        lineArr.append("All Line")
        dateArr.append(yestoday)
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
                        if operator.eq(inputrow['dayornight'], 'Day'):
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
                                # y1_day[int(key)] = inputrow['y1']
                                # y2_day[int(key)] = inputrow['y2']
                                # y1_day_temp[int(key)] = inputrow['y1']
                                # y2_day_temp[int(key)] = inputrow['y2']
                        if operator.eq(inputrow['dayornight'], 'Night'):
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
                                # y1_night[int(key)] = inputrow['y1']
                                # y2_night[int(key)] = inputrow['y2']
                                # y1_night_temp[int(key)] = inputrow['y1']
                                # y2_night_temp[int(key)] = inputrow['y2']
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
            y1_fpy_sub_day_value = get_formula_value(y1_day_list, y1_day_list_temp, fpy_sub_formula)
            y1_fpy_sub_night_value = get_formula_value(y1_night_list, y1_night_list_temp, fpy_sub_formula)
            y2_fpy_sub_day_value = get_formula_value(y2_day_list, y2_day_list_temp, fpy_sub_formula)
            y2_fpy_sub_night_value = get_formula_value(y2_night_list, y2_night_list_temp, fpy_sub_formula)
            # 计算Assy Yield(main)
            y1_assembly_yield_sub_day_value = get_formula_value(y1_day_list, y1_day_list_temp,
                                                                assembly_yield_sub_formula)
            y1_assembly_yield_sub_night_value = get_formula_value(y1_night_list, y1_night_list_temp,
                                                                  assembly_yield_sub_formula)
            # 计算FPY(sub+main)
            y1_fpy_day_value = get_formula_value(y1_day_list, y1_day_list_temp, fpy_formula)
            y1_fpy_night_value = get_formula_value(y1_night_list, y1_night_list_temp, fpy_formula)
            # 计算FPY(main)
            y1_assembly_yield_day_value = get_formula_value(y1_day_list, y1_day_list_temp, assembly_yield_formula)
            y1_assembly_yield_night_value = get_formula_value(y1_night_list, y1_night_list_temp, assembly_yield_formula)
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

        img_path = get_config("img_path")
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
                            and operator.eq(inputrow['dayornight'], 'Day'):
                        input_day = int(inputrow['input_quantity'])
                        output_day = int(inputrow['output_quantity'])
                        ng_day = int(inputrow['ng_quantity'])
                        if inputrow['y2'] != 0:
                            yield_day = "%.2f%%" % (inputrow['y2'] * 100)
                    elif operator.eq(inputrow['line_cd'], line) and operator.eq(inputrow['assy_text'], assy) \
                            and operator.eq(inputrow['dayornight'], 'Night'):
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
                sums = "%.2f%%" % (sum(output_data_int) / ((sum(output_data_int) + sum(ng_data_int)) * 1.0) * 100)
            else:
                sums = "NP"
            yield_data.append(sums)

            assy_data.append(input_data)
            assy_data.append(output_data)
            assy_data.append(ng_data)
            assy_data.append(yield_data)
            img_full_name = img_path + getPicture(assy)

            # 获取Target
            target = get_target(assy, model_name)
            result_assy.append({"name": assy, "target": target, "img": img_full_name, "data": assy_data, })
            result_allLine.append(
                {"assy_text": assy, "input_quantity": sum(input_data_int), "output_quantity": sum(output_data_int), \
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
                        y2_list_temp.append(
                            row["output_quantity"] / ((row["output_quantity"] + row["ng_quantity"]) * 1.0))
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
        y1_fpy_sub_value = get_formula_value(y1_list, y1_list_temp, fpy_sub_formula)
        y2_fpy_sub_value = get_formula_value(y2_list, y2_list_temp, fpy_sub_formula)

        # 计算Assy Yield(main)
        y1_assembly_yield_sub_value = get_formula_value(y1_list, y1_list_temp, assembly_yield_sub_formula)
        # 计算FPY(sub+main)
        y1_fpy_value = get_formula_value(y1_list, y1_list_temp, fpy_formula)
        # 计算FPY(main)
        y1_assembly_yield_value = get_formula_value(y1_list, y1_list_temp, assembly_yield_formula)
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

        result.append({"name": "VS", "img": "", "data": header_data, "lines": lines_hid})
        result.extend(result_assy)
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def getPicture(picName):
    imgPath = os.getcwd() + '/static/images'
    picName = picName.split('.')[0]
    for root, dirs, files in os.walk(imgPath):
        for file in files:
            file_ = file.split('.')[0]
            if (picName.lower() == file_.lower()):
                return file
    return 'noimage.png'


def getPlanData(model_name, plan_date, revision):
    result = []
    try:
        cur = connections[model_name].cursor()
        # cur.execute('SELECT assy_text,in_quantity,out_quantity,before_quantity,after_quantity FROM m_plan WHERE plan_date=%s AND revision=%s AND mode_name=%s',(plan_date,revision,model_name))

        cur.execute(
            'SELECT assy_text,in_quantity,out_quantity,before_quantity,after_quantity FROM m_plan WHERE plan_date=%s AND mode_name=%s',
            (plan_date, model_name))

        rows = cur.fetchall()
        for row in rows:
            result.append({'assy_text': row[0], 'in': row[1], 'out': row[2], 'before': row[3], 'after': row[4]})
        # cur.execute('DELETE FROM m_plan WHERE plan_date=%s AND revision=%s AND mode_name=%s',(plan_date,revision,model_name))
        cur.execute('DELETE FROM m_plan WHERE plan_date=%s AND mode_name=%s',
                    (plan_date, model_name))
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


def getLine(model_name, assy):
    result = ''
    try:
        cur = connections[model_name].cursor()
        cur.execute("SELECT\
                    line_cd \
                FROM\
                    m_work \
                WHERE\
                    assy_text = %s \
                ORDER BY line_cd", (assy,))
        rows = cur.fetchall()
        for row in rows:
            result = row[0]
            break
    except BaseException as exp:
        print(exp)
        result = databaseException(exp)
    connections[model_name].close()
    return result


# def get_history(model_name, start_date, end_date, line):
#    process_at_list = get_periodDate(start_date, end_date)
#    result = []
#    # input
#    result_inputQuantity = get_inputQuantity(model_name, start_date, end_date, 'All', False, line)
#    if result_inputQuantity == 101 or result_inputQuantity == 102:
#        return result_inputQuantity
#    # output
#    result_outputQuantity = get_outputQuantity(model_name, start_date, end_date, 'All', False, line)
#    if result_outputQuantity == 101 or result_outputQuantity == 102:
#        return result_outputQuantity
#    # ng
#    result_ngQuantity = get_ngQuantity(model_name, start_date, end_date, 'All', False, line)
#    if result_ngQuantity == 101 or result_ngQuantity == 102:
#        return result_ngQuantity
#    # get assy
#    assyArr = get_allAssyAndProcessId(model_name)
#    if assyArr == 101 or assyArr == 102:
#        return assyArr
#    try:
#        # 计算y2，合并到inputQuantity
#        for inputrow in result_inputQuantity:
#            output_quantity = 0
#            for outputrow in result_outputQuantity:
#                if operator.eq(outputrow['assy_text'], inputrow['assy_text']) and operator.eq(outputrow['process_at'], inputrow['process_at']):
#                    output_quantity = outputrow['output_quantity']
#                    break
#            ng_quantity = 0
#            for ngrow in result_ngQuantity:
#                if operator.eq(ngrow['assy_text'], inputrow['assy_text']) and operator.eq(ngrow['process_at'], inputrow['process_at']):
#                    ng_quantity = ngrow['ng_quantity']
#                    break
#            if output_quantity > 0:
#                inputrow["y2"] = output_quantity / ((output_quantity + ng_quantity)*1.0)
#            else:
#                inputrow["y2"] = "NP"
#        # sort
#        result_inputQuantity = sorted(result_inputQuantity, key=lambda x: (x['assy_text'], x['process_at']))
#        # 设定目标json数据
#        result = setDataList(process_at_list, result_inputQuantity, assyArr, model_name)
#        # sort
#        result = sorted(result, key=lambda x: (x['process_id']))
#
#        database_list = get_config("database")
#        formulaDic = {}
#        assyDic = {}
#        assyDic_int = {}
#        for row in database_list:
#            if operator.eq(row['MODEL'], model_name):
#                # 从配置文件里取得ASSY
#                assyDic = row['ASSY']
#                # 从配置文件里取得FORMULA
#                formulaDic = row['FORMULA_TREND']
#                break
#        # 给key为整数的字典assyDic_int赋值
#        for key in assyDic:
#            assyDic_int[int(key)] = assyDic[key]
#        # 字典排序
#        sorted(assyDic_int.keys())
#
#        # fpy计算公式的取得
#        fpy_formula = formulaDic["FPY(main)"]
#        # FPY(sub+main)计算公式的取得
#        tester_yield_formula = formulaDic["FPY(sub+main)"]
#        # Assembly Yield(sub+main)计算公式的取得
#        assembly_yield_formula = formulaDic["Assembly Yield(sub+main)"]
#
#        data_zero = []
#        i = 0
#        while i < len(process_at_list):
#            data_zero.append("NP")
#            i = i + 1
#
#        # 按配置文件里ASSY的顺序排列result
#        result_temp = []
#        for key in assyDic_int:
#            flg = False
#            for row in result:
#                if operator.eq(row['process'], assyDic_int[key]):
#                    flg = True
#                    result_temp.append(row)
#                    break
#            # 当前config里设定的Assy在result里不存在的场合
#            if flg == False:
#                # 获取TARGET
#                target = get_target(assyDic_int[key], model_name)
#                result_temp.append({'process': assyDic_int[key], 'yield': data_zero, 'target': target, })
#
#        assembly_yield_list = []
#        tester_yield_list = []
#        fpy_list = []
#        for i in range(len(process_at_list)):
#            y2_list = []
#            y2_list_temp = []
#            for row in result_temp:
#                yield2 = row['yield'][i]
#                y2_list_temp.append(yield2)
#                if operator.eq(yield2, 'NP'):
#                    yield2 = float(1)
#                y2_list.append(yield2)
#
#            # 计算y2_FPY(main)
#            y2_fpy_value = get_formula_value(y2_list, y2_list_temp, fpy_formula)
#            # 计算y2_FPY(sub+main)
#            y2_tester_yield_value = get_formula_value(y2_list, y2_list_temp, tester_yield_formula)
#            # 计算y2_Assembly Yield(sub+main)
#            y2_assembly_yield_value = get_formula_value(y2_list, y2_list_temp, assembly_yield_formula)
#            # 将当前计算值添加到list
#            assembly_yield_list.append(y2_assembly_yield_value)
#            tester_yield_list.append(y2_tester_yield_value)
#            fpy_list.append(y2_fpy_value)
#
#        # 获取TARGET
#        assembly_yield_target = get_target('Assembly Yield(sub+main)', model_name)
#        tester_yield_target = get_target('Assembly Yield(sub+main)', model_name)
#        fpy_target = get_target('FPY(main)', model_name)
#        result.append({'process': 'Assembly Yield(sub+main)', 'yield':assembly_yield_list , 'target':assembly_yield_target, })
#        result.append({'process': 'FPY(sub+main)', 'yield': tester_yield_list, 'target':tester_yield_target, })
#        result.append({'process': 'FPY(main)', 'yield': fpy_list, 'target':fpy_target, })
#
#        # y2转成百分比
#        for row in result:
#            i = 0
#            for value in row['yield']:
#                if value != 'NP':
#                    row['yield'][i] = "%.2f%%" % (value * 100)
#                i = i + 1
#
#    except BaseException as exp:
#        print(exp)
#        result = 102
#    connections[model_name].close()
#    return result

def setHistoryList(list, npList, summaryValue):
    historyList = list
    np_flg = True
    # 判断公式包含的所有yield是否全是NP
    for value in npList:
        if value == False:
            np_flg = False
            break
    if np_flg:
        historyList.append('NP')
    else:
        historyList.append(summaryValue)
    return historyList


def setDataList(process_at_list, result_quantity, objectArr, model_name, object, content, typeName):
    result = []
    last_text = ""
    last_process_at = ""
    last_process_id = ""
    data = []
    data_zero = []
    index = 0
    end_date = datetime.datetime.strptime(process_at_list[-1], "%Y-%m-%d")
    if object == 'Line':
        process_name = "assy_text"
    else:
        process_name = "line_cd"
    i = 0
    while i < len(process_at_list):
        data_zero.append("NP")
        i = i + 1

    for row in result_quantity:
        begin_date = datetime.datetime.strptime(process_at_list[0], "%Y-%m-%d")
        current_date = datetime.datetime.strptime(row['process_at'], "%Y-%m-%d")
        if operator.eq(row[process_name], last_text) == False:
            # 不是第一条数据的场合
            if index != 0:
                # data数组最后的补位处理
                while last_process_at < end_date:
                    data.append("NP")
                    last_process_at += datetime.timedelta(days=1)
                # 获取TARGET
                if typeName == "Y2":
                    if object == 'Line':
                        target_assy = last_text
                    else:
                        target_assy = content
                    target = get_target(target_assy, model_name)
                    if object == 'Line':
                        result.append(
                            {'process': last_text, 'data': data, 'process_id': last_process_id, 'target': target, })
                    else:
                        result.append({'process': last_text, 'data': data, 'target': target, })
                else:
                    if object == 'Line':
                        result.append({'process': last_text, 'data': data, 'process_id': last_process_id, })
                    else:
                        result.append({'process': last_text, 'data': data, })
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

            last_text = row[process_name]
            if object == 'Line':
                last_process_id = row['process_id']
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
        # 获取TARGET
        if typeName == "Y2":
            if object == 'Line':
                target_assy = last_text
            else:
                target_assy = content
            target = get_target(target_assy, model_name)
            if object == 'Line':
                result.append({'process': last_text, 'data': data, 'process_id': last_process_id, 'target': target, })
            else:
                result.append({'process': last_text, 'data': data, 'target': target, })
        else:
            if object == 'Line':
                result.append({'process': last_text, 'data': data, 'process_id': last_process_id, })
            else:
                result.append({'process': last_text, 'data': data, })

    for objectRow in objectArr:
        flg = False
        if object == 'Line':
            for row in result_quantity:
                if operator.eq(row[process_name], objectRow[process_name]):
                    flg = True
                    break
        else:
            for row in result_quantity:
                if operator.eq(row[process_name], objectRow):
                    flg = True
                    break

        if flg == False:
            # 获取TARGET
            if typeName == "Y2":
                if object == 'Line':
                    target = get_target(objectRow[process_name], model_name)
                    result.append(
                        {'process': objectRow[process_name], 'data': data_zero, 'process_id': objectRow['process_id'],
                         'target': target, })
                else:
                    target = get_target(content, model_name)
                    result.append({'process': objectRow, 'data': data_zero, 'target': target, })
            else:
                if object == 'Line':
                    result.append({'process': objectRow[process_name], 'data': data_zero,
                                   'process_id': objectRow['process_id'], })
                else:
                    result.append({'process': objectRow, 'data': data_zero, })

    return result


# 取背景色的target值
def get_target(val, model):
    result = get_config('database')
    for item in result:
        if (item['MODEL'] == model):
            target = item['TARGET']
            break
    for item in result:
        if (item['MODEL'] == model):
            assy = item['ASSY']
            break
    flag = False
    if (val == 'Assembly Yield(sub+main)' or val == 'FPY(sub+main)' or val == 'FPY(main)'):
        return target[val]
    for item in assy:
        if (val == assy[item]):
            flag = True
            for key in target:
                if (item == key):
                    return target[key]
    if (flag == False):
        return 0


def search_defect(model_name, startTime, endTime, line, assy, time_part, top_rank, target, mode):
    result = {}
    result_x = []
    result_y_left = []
    result_y_right = []
    result_inspectInfo = []
    sql_line = ""
    sql_assy = ""
    sql_where_assy = ""
    sql_limit = " LIMIT " + top_rank
    sql_offset = " OFFSET " + top_rank + ") AS T1"
    if line != 'All Line':
        sql_line = " AND line_cd = '" + line + "' "
    if assy != 'All Assy':
        sql_assy = " AND assy_text = '" + assy + "' "
        sql_where_assy = " WHERE assy_text = '" + assy + "' "
    if mode == 'Pareto':
        sql_orderBy = " ORDER BY failed_quantity DESC,inspect_cd ASC "
    else:
        sql_orderBy = " ORDER BY detractor DESC,inspect_cd ASC "
    if target == 'Inspect':
        sql_partition = "PARTITION BY serial_cd,inspect_cd ORDER BY inspect_cd"
    else:
        sql_partition = "PARTITION BY serial_cd ORDER BY inspect_cd"
    try:
        cur = connections[model_name].cursor()
        sql = "SELECT DISTINCT \
                    inspect.inspect_cd,\
                    assy.process_cd,\
                    assy.assy_text,\
                    COALESCE ( auto_ok.ok_quantity, 0 ) AS ok_quantity,\
                    COALESCE ( auto_ng.ng_quantity, 0 ) AS ng_quantity,\
                    COALESCE ( inspect.inspect_count, 0 ) AS failed_quantity,\
                    ( COALESCE ( auto_ok.ok_quantity, 0 ) + COALESCE ( auto_ng.ng_quantity, 0 ) ) AS input_quantity, \
                    COALESCE ( inspect.inspect_count, 0 )/( COALESCE ( auto_ok.ok_quantity, 0 ) + COALESCE ( auto_ng.ng_quantity, 0 ) ) AS detractor\
                FROM\
                    m_assy assy\
                    INNER JOIN (\
                SELECT\
                    auto.process_id,\
                    SUM( quantity ) AS ok_quantity \
                FROM\
                    m_assy A\
                    INNER JOIN t_1_auto_io_2nd auto ON A.process_id = auto.process_id \
                WHERE\
                    process_at >= '(startTime)' \
                    AND process_at <= '(endTime)' \
                    AND time_part = '(time_part)' \
                    AND judge_text = 'ok' " + sql_line + sql_assy + \
              "GROUP BY\
              auto.process_id \
              ) AS auto_ok ON assy.process_id = auto_ok.process_id\
              INNER JOIN (\
          SELECT\
              auto.process_id,\
              SUM( quantity ) AS ng_quantity \
          FROM\
              m_assy A\
              INNER JOIN t_1_auto_io_2nd auto ON A.process_id = auto.process_id \
          WHERE\
              process_at >= '(startTime)' \
              AND process_at <= '(endTime)' \
              AND time_part = '(time_part)' \
              AND judge_text = 'ng' \
              AND quantity > 0 " + sql_line + sql_assy + \
              "GROUP BY\
                  auto.process_id \
                  ) AS auto_ng ON assy.process_id = auto_ng.process_id \
                  INNER JOIN t_1_auto_io_2nd auto ON auto_ng.process_id = auto.process_id \
                  AND process_at >= '(startTime)' \
                  AND process_at <= '(endTime)'\
                  AND time_part = '(time_part)' \
                  AND judge_text = 'ng' \
                  AND quantity > 0 " + sql_line + \
              "INNER JOIN t_1_defect_2nd defect ON auto.data_seq = defect.data_seq \
              INNER JOIN ( \
              SELECT \
                  process_id,\
                  inspect_cd,\
                  COUNT( inspect_cd ) inspect_count \
              FROM \
                  ( \
              SELECT \
                  process_id,\
                  t2.data_seq, \
                  serial_cd, \
                  inspect_cd \
              FROM \
                  ( \
              SELECT \
                  data_seq,\
                  serial_cd,\
                  inspect_cd,\
                  ROW_NUMBER ( ) OVER ( " + sql_partition + \
              ") RANK \
        FROM \
            ( \
        SELECT \
            defect.data_seq,\
            defect.serial_cd,\
            defect.inspect_cd \
        FROM\
            m_assy A \
            INNER JOIN t_1_auto_io_2nd auto ON A.process_id = auto.process_id \
            INNER JOIN t_1_defect_2nd defect ON auto.data_seq = defect.data_seq \
        WHERE\
            process_at >= '(startTime)' \
            AND process_at <= '(endTime)' AND time_part = '(time_part)' AND judge_text = 'ng' AND quantity > 0 " + sql_line + sql_assy + \
              "ORDER BY defect.serial_cd, defect.inspect_cd \
                  ) AS t1 \
                  ) AS t2 INNER JOIN t_1_auto_io_2nd auto ON auto.data_seq = t2.data_seq \
              WHERE \
                  RANK = 1 \
                  ) defect1 \
              GROUP BY process_id,inspect_cd \
              ) AS inspect ON defect.inspect_cd = inspect.inspect_cd \
              AND assy.process_id = inspect.process_id " + sql_where_assy + sql_orderBy
        sql = sql.replace("(startTime)", startTime).replace("(endTime)", endTime).replace("(time_part)", time_part)
        # top数据取得
        cur.execute(sql + sql_limit)
        rows_limit = cur.fetchall()
        # 所有数据的取得
        cur.execute(sql)
        rows_all = cur.fetchall()

        count = 0
        sum_detractor = float(0)
        sum_fail = 0
        result_y_right_temp = []
        search_result_limit = []
        search_result_all = []
        for row in rows_limit:
            count = count + 1
            detractor = int(row[5]) / (int(row[6]) * 1.0)
            search_result_limit.append(
                {"NG_Inspect": row[0], "Input": int(row[6]), "Failed": int(row[5]), "Detractor": detractor, })
        for row in rows_all:
            search_result_all.append({"NG_Inspect": row[0], "Process": row[1], "Assy": row[2], "Input": int(row[6]),
                                      "Failed": int(row[5]), })

        # 设定表格数据
        for row in search_result_all:
            sum_fail = sum_fail + row['Failed']
            sum_detractor = sum_detractor + row['Failed'] / (row['Input'] * 1.0)
            # 设定表格数据
            detractor = float("%.2f" % (row['Failed'] / (row['Input'] * 1.0) * 100))
            yield2 = float("%.2f" % ((1 - row['Failed'] / (row['Input'] * 1.0)) * 100))
            if mode == 'Pareto':
                result_inspectInfo.append({"NG_Inspect": row['NG_Inspect'], "Process": row['Process'], \
                                           "Assy": row['Assy'], "Input": row['Input'], "Failed": row['Failed'], \
                                           "Detractor": detractor, "Yield": yield2, "Cum": sum_fail, })
            else:
                result_inspectInfo.append({"NG_Inspect": row['NG_Inspect'], "Process": row['Process'], \
                                           "Assy": row['Assy'], "Input": row['Input'], "Failed": row['Failed'], \
                                           "Detractor": detractor, "Yield": yield2, "Cum": sum_detractor, })
        # 设定表格数据的Cum
        index = 0
        for row in result_inspectInfo:
            if mode == 'Pareto':
                result_inspectInfo[index]['Cum'] = float("%.2f" % (row['Cum'] / (sum_fail * 1.0) * 100))
            else:
                result_inspectInfo[index]['Cum'] = float("%.2f" % (row['Cum'] / (sum_detractor * 1.0) * 100))
            index = index + 1

        # Others数据取得
        if count == int(top_rank):
            if mode == 'Pareto':
                cur.execute(
                    "SELECT 'All Others' as inspect_cd,SUM(failed_quantity) as failed_quantity,SUM(input_quantity) as input_quantity FROM(" + sql + sql_offset)
            else:
                cur.execute(
                    "SELECT 'All Others' as inspect_cd,SUM(failed_quantity) as failed_quantity,SUM(input_quantity) as input_quantity,SUM(detractor) as detractor FROM(" + sql + sql_offset)
            rows = cur.fetchall()
            for row in rows:
                if row[2] is not None and row[2] > 0:
                    if mode == 'Pareto':
                        search_result_limit.append(
                            {"NG_Inspect": row[0], "Input": int(row[2]), "Failed": int(row[1]), })
                    else:
                        search_result_limit.append({"NG_Inspect": row[0], "Input": int(row[2]), "Failed": int(row[1]), \
                                                    "Detractor": float(row[3]), })
        if count > 0:
            # sort(按Failed的降序排列)
            # search_result_limit.sort(key=lambda x: x["Failed"], reverse=True)
            sum_fail = 0
            sum_detractor = float(0)
            # 设定图标数据
            for row in search_result_limit:
                # 设定x坐标（inspect_cd）
                result_x.append(row['NG_Inspect'])
                if mode == 'Pareto':
                    sum_fail = sum_fail + row['Failed']
                    # 设定y_left坐标（Failed数量）
                    result_y_left.append(row['Failed'])
                    # 设定y_right坐标（Failed的累积比率）
                    result_y_right_temp.append(sum_fail)
                else:
                    sum_detractor = sum_detractor + row['Detractor']
                    # 设定y_left坐标（Detractor）
                    result_y_left.append(float("%.2f" % (row['Detractor'] * 100)))
                    # 设定y_right坐标（Detractor的累积比率）
                    result_y_right_temp.append(sum_detractor)

            # 设定y_right坐标（Failed百分比）
            for value in result_y_right_temp:
                if mode == 'Pareto':
                    result_y_right.append(float("%.2f" % (value / (sum_fail * 1.0) * 100)))
                else:
                    result_y_right.append(float("%.2f" % (value / (sum_detractor * 1.0) * 100)))
        if len(result_x) == 0 or len(result_y_left) == 0 or len(result_y_right) == 0 or len(result_inspectInfo) == 0:
            result = []
        else:
            result = {"x": result_x, "y_left": result_y_left, "y_right": result_y_right,
                      "inspect_info": result_inspectInfo, }

    except BaseException as exp:
        print(exp)
        return [{"status": "fail"}]
    connections[model_name].close()
    return result


# 计算公式取值共同方法
def get_formula_value(orgValueList, orgValueList_temp, formula):
    last_value = float(0)
    # 取最小值
    if type(formula) == list:
        formula_min_dic = {}
        npFlg_list = []
        for i in range(len(formula)):
            formula_min_dic[i] = formula[i].split(',')
        min_list = []
        # 取最小值
        for key in formula_min_dic:
            np_flg = True
            sub_value = float(1)
            for value in formula_min_dic[key]:
                sub_value = sub_value * orgValueList[int(value)]
                if orgValueList_temp[int(value)] != 'NP':
                    np_flg = False
            min_list.append(sub_value)
            npFlg_list.append(np_flg)

        np_flg = True
        # 判断公式包含的所有yield是否全是NP
        for value in npFlg_list:
            if value == False:
                np_flg = False
                break
        if np_flg == False:
            last_value = min(min_list)
        return last_value

    else:  # 取乘积
        product_list = []
        pattern_list = re.compile(r"\[[^\[\]]*\]")
        pattern_sum = re.compile(r"\([^\(\)]*\)")
        # 存放公式中所有数组
        result_list = pattern_list.findall(formula)
        # 存放公式中所有求和字符串
        result_sum = pattern_sum.findall(formula)
        product_formula = formula
        # 获取每项list的最小值，并保存在product_list里
        for value in result_list:
            formula_min_dic = {}
            # 字符窜转成数组
            min_sub_list = value.replace("['", '').replace("']", '').split("','")
            for i in range(len(min_sub_list)):
                formula_min_dic[i] = min_sub_list[i].split(',')
            min_list = []
            npFlg_list = []
            # 取最小值
            for key in formula_min_dic:
                np_flg = True
                sub_value = float(1)
                for value1 in formula_min_dic[key]:
                    sub_value = sub_value * orgValueList[int(value1)]
                    if orgValueList_temp[int(value1)] != 'NP':
                        np_flg = False
                min_list.append(sub_value)
                npFlg_list.append(np_flg)
            # 将结果保存到list
            product_list = setHistoryList(product_list, npFlg_list, min(min_list))
            # 计算公式里除去求最小值部分
            product_formula = product_formula.replace(value + ',', '').replace(',' + value, '')

        # 获取每项求和公式的和，并保存在product_list里
        for value in result_sum:
            sum_sub_list = value.replace("(", '').replace(")", '').split(",")
            sub_value = float(0)
            for value1 in sum_sub_list:
                if orgValueList_temp[int(value1)] != 'NP':
                    sub_value = sub_value + orgValueList_temp[int(value1)]
            if sub_value == float(0):
                sub_value = 'NP'
            # 将结果保存到list
            product_list.append(sub_value)
            # 计算公式里除去求和部分
            product_formula = product_formula.replace("," + value, '').replace(value + ",", '').replace(value, '')

        # 求取最后乘积部分的值
        if product_formula != '':
            product_formula = product_formula.replace("'", "")
            sub_product_list = product_formula.split(",")
            sub_value = float(1)
            np_flg = True
            for value in sub_product_list:
                sub_value = sub_value * orgValueList[int(value)]
                if orgValueList_temp[int(value)] != 'NP':
                    np_flg = False
            if np_flg:
                sub_value = 'NP'
            # 将结果保存到list
            product_list.append(sub_value)

        # 计算last_value
        np_flg = True
        for value in product_list:
            if value != 'NP':
                np_flg = False
                break
        if np_flg == False:
            sub_value = float(1)
            for value in product_list:
                if value != 'NP':
                    sub_value = sub_value * value
            last_value = sub_value
        return last_value


def databaseException(exp):
    if 'could not connect to server' in str(exp):
        # return {'status': "fail", 'msg': 'Connect to database failed[101]'}
        return 101
    else:
        # return {'status': "fail", 'msg': 'Operate to database failed[102]'}
        return 102


def checkConnection(model):
    try:
        cur = connections[model].cursor()
    except BaseException as exp:
        print(exp)
        return 'ng'
    else:
        return 'ok'


def getAvg_allLine(result, process_at_list):
    data = []
    i = 0
    while i < len(process_at_list):
        sum_yield = 0.00
        j = 0
        for row in result:
            j = j + 1
            value = row['data'][i]
            if type(value) == type('a') or type(value) == type(u'a'):
                value = 0.00
            sum_yield = sum_yield + value
        # data.append(float("%.2f" % (sum_yield / (j * 1.0))))
        data.append(float(sum_yield / (j * 1.0)))
        i = i + 1
    return data


# 补0处理
def supplementZero(name, listData, process_at_list, type):
    data = []
    index = 0
    end_date = datetime.datetime.strptime(process_at_list[-1], "%Y-%m-%d")
    for row in listData:
        begin_date = datetime.datetime.strptime(process_at_list[0], "%Y-%m-%d")
        current_date = datetime.datetime.strptime(row['process_at'], "%Y-%m-%d")
        # 不是第一条数据的场合
        if index != 0:
            # data数组中间的补位处理
            last_process_at += datetime.timedelta(days=1)
            while last_process_at < current_date:
                data.append(0)
                last_process_at += datetime.timedelta(days=1)
        else:
            # data数组最前端的补位处理
            while begin_date < current_date:
                data.append(0)
                begin_date += datetime.timedelta(days=1)

        # 设定data
        data.append(row['sum_quantity'])

        index = index + 1
        last_process_at = current_date

    if len(listData) > 0:
        # 最后一条的处理（追加到result）
        while last_process_at < end_date:
            data.append(0)
            last_process_at += datetime.timedelta(days=1)
    if type == 'trend_chart':
        result = {"name": name, "data_tb": data, 'data': data}
    else:
        result = {"process": name, "data": data}
    return result
