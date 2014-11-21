# -*- coding: utf-8 -*-

import xmlrpclib
import os
import sys
from fileinput import close
os.chdir('../')
current_path = os.getcwd()
sys.path.append(current_path)
from common.oorpc import OpenObjectRPC, define_arg
import xlrd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

import psycopg2

db1_conn_string = "host='192.168.7.76' port='5432' dbname='SYNOVA' user='postgres' password='postgres'"
# db1_conn_string = "host='localhost' port='5432' dbname='SYNOVA_2602' user='postgres' password='postgres'"

def generate_absent_attendance(oorpc):
    try:
        conn1 = psycopg2.connect(db1_conn_string)
    except Exception, ex:
        connect = False
        print 'Can not connect database 7.0'
    
    print 'Connect database 7.0 successfully'
    print ''
    
    cursor1 = conn1.cursor()
    cursor1.execute('''
            SELECT id
            FROM hr_employee
            WHERE parent_id is not null
    ''')
    employee_ids = [x[0] for x in cursor1.fetchall()]
    
    cursor1 = conn1.cursor()
    cursor1.execute('''
            SELECT name::date
            FROM hr_attendance
            group by name::date
            order by name::date
    ''')
    dates = cursor1.fetchall()
    count = 0
    for date in dates:
        date = date[0].strftime('%Y-%m-%d')
        date_time = date + ' 00:00:00'
        for employee_id in employee_ids:
            atts = oorpc.search('hr.attendance', [('day','=',date),('name','>',date_time),('employee_id','=',employee_id)])
            sheet_ids = oorpc.search('hr_timesheet_sheet.sheet', [('date_from','<=',date),('date_to','>=',date_time),('employee_id','=',employee_id)])
            if not atts and sheet_ids:
                try:
#                     vals = {
#                             'name': date_time,
#                             'employee_id':employee_id,
#                             'action': 'sign_in',
#                             }
#                     new_id = oorpc.create('hr.attendance', vals)
                    cursor1.execute('''
                            INSERT INTO hr_attendance(name,day,employee_id,date_user_tz,hour_user_tz,spent_hours,sheet_id,action,department_id)
                            VALUEs ('%s','%s',%s,'%s',0.0,0.0,%s,'sign_in',
                            (SELECT CASE WHEN department_id IS NOT NULL THEN department_id ELSE NULL END FROM hr_employee WHERE id=%s))
                    '''%(date_time,date,employee_id,date,sheet_ids and sheet_ids[0] or 'Null',employee_id))
                    print count
                    count += 1
                    cursor1.execute('commit')
                except Exception, e:
                    print e
                try:
#                     vals = {
#                             'name': date_time,
#                             'employee_id':employee_id,
#                             'action': 'sign_out',
#                             }
#                     new_id = oorpc.create('hr.attendance', vals)
                    cursor1.execute('''
                            INSERT INTO hr_attendance(name,day,employee_id,date_user_tz,hour_user_tz,spent_hours,sheet_id,action,department_id)
                            VALUEs ('%s','%s',%s,'%s',0.0,0.0,%s,'sign_out',
                            (SELECT CASE WHEN department_id IS NOT NULL THEN department_id ELSE NULL END FROM hr_employee WHERE id=%s))
                    '''%(date_time,date,employee_id,date,sheet_ids and sheet_ids[0] or 'Null',employee_id))
                    print count
                    count += 1
                    cursor1.execute('commit')
                except Exception, e:
                    print e
    return True

if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('192.168.7.76', 'SYNOVA', 'admin', 'synadmin123', '8069')
#     oorpc = OpenObjectRPC('localhost', 'SYNOVA_2602', 'admin', 'synadmin123', '8069')
    print 'In progress ...'
    generate_absent_attendance(oorpc)
    print 'Done.'
    
    
    
    

