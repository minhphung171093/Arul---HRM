# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_month':self.get_month,
            'get_year':self.get_year,
            'get_emp':self.get_emp,
        })
        
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return self.get_month_name(wizard_data['month'])
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']
    
    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        category_id = wizard_data['category_id']
        month=wizard_data['month']
        year=wizard_data['year']
        employee_obj = self.pool.get('hr.employee')
        time_leave_eva_obj = self.pool.get('tpt.time.leave.evaluation')
        employee_attend_detail_obj = self.pool.get('arul.hr.employee.attendence.details')
        res = []
        if category_id:
            employee_ids = employee_obj.search(self.cr, self.uid,[('employee_category_id','=',category_id[0])])
        else:
            employee_ids = employee_obj.search(self.cr, self.uid,[])
#             time_leave_eva_ids = time_leave_eva_obj.search(self.cr, self.uid,[('month','=',month),('year','=',year)])
        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            sql = '''
                select count(*) as date from (select work_date from arul_hr_punch_in_out_time where EXTRACT(month from work_date)=%s and EXTRACT(year from work_date)=%s and
                    punch_in_out_id in (select id from arul_hr_employee_attendence_details where employee_id=%s)
                group by work_date) as x
            '''%(int(month), int(year),employee.id)
            self.cr.execute(sql)
            date = self.cr.dictfetchone()
            sql = '''
                select actual_work_shift_id from arul_hr_punch_in_out_time where EXTRACT(month from work_date)=%s and EXTRACT(year from work_date)=%s and
                    punch_in_out_id in (select id from arul_hr_employee_attendence_details where employee_id=%s) and actual_work_shift_id is not null
            '''%(int(month), int(year),employee.id)
            self.cr.execute(sql)
            actual_work_shift_ids = [r[0] for r in self.cr.fetchall()]
            a=0
            b=0
            c=0
            g1=0
            g2=0
            
            #TPT
            perm_onduty_count=0
            total_shift_worked=0
            #onduty_count = False
            #permission_count=False
            #PUNCH IN OUT
            sql = '''
                SELECT CASE WHEN SUM(total_shift_worked)!=0 THEN SUM(total_shift_worked) ELSE 0 END sum_punch_inout FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            s_c =  self.cr.fetchone()
            shift_count = s_c[0]
                
            #Permission
            sql = '''
                SELECT CASE WHEN SUM(total_shift_worked)!=0 THEN SUM(total_shift_worked) ELSE 0 END sum_permission FROM arul_hr_permission_onduty WHERE non_availability_type_id='permission' 
                AND EXTRACT(year FROM date) = %s AND EXTRACT(month FROM date) = %s and employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            p_c =  self.cr.fetchone()
            permission_count = p_c[0]
                
            #OnDuty
            sql = '''
                SELECT CASE WHEN SUM(total_shift_worked)!=0 THEN SUM(total_shift_worked) ELSE 0 END sum_onduty FROM arul_hr_permission_onduty WHERE non_availability_type_id='on_duty' 
                AND EXTRACT(year FROM to_date) = %s AND EXTRACT(month FROM to_date) = %s and employee_id =%s and total_shift_worked>=1
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            o_c =  self.cr.fetchone()
            onduty_count = o_c[0]
            
            total_shift_worked = shift_count + onduty_count
            perm_onduty_count =   onduty_count  
            
            ##TPT
            sql = '''
                SELECT CASE WHEN SUM(a_shift_count1)!=0 THEN SUM(a_shift_count1) ELSE 0 END a_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            t_a =  self.cr.fetchone()
            tpt_a = t_a[0]
            
            sql = '''
                SELECT CASE WHEN SUM(b_shift_count1)!=0 THEN SUM(b_shift_count1) ELSE 0 END b_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            t_b =  self.cr.fetchone()
            tpt_b = t_b[0]
            
            sql = '''
                SELECT CASE WHEN SUM(c_shift_count1)!=0 THEN SUM(c_shift_count1) ELSE 0 END c_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            t_c =  self.cr.fetchone()
            tpt_c = t_c[0]
            
            sql = '''
                SELECT CASE WHEN SUM(g1_shift_count1)!=0 THEN SUM(g1_shift_count1) ELSE 0 END g1_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            t_g1 =  self.cr.fetchone()
            tpt_g1 = t_g1[0]
            
            sql = '''
                SELECT CASE WHEN SUM(g2_shift_count1)!=0 THEN SUM(g2_shift_count1) ELSE 0 END g2_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(int(year), int(month),employee.id)
            self.cr.execute(sql)
            t_g2 =  self.cr.fetchone()
            tpt_g2 = t_g2[0]
            ##TPT    
                #TOTAL SHIFT WORKED
            #raise osv.except_osv(_('Warning!%s'),_(sql))      
            
            #total_shift_worked = round(shift_count+permission_count + onduty_count,1)
            #perm_onduty_count =  round(permission_count + onduty_count,1)   
            
                #total_shift_worked = round(shift_count) + round(permission_count) + round(onduty_count)
                
                #TPT END     
            #
            
            
            for shift in self.pool.get('arul.hr.capture.work.shift').browse(self.cr,self.uid,actual_work_shift_ids):
                if shift.code=='A':
                    a+=1
                if shift.code=='B':
                    b+=1
                if shift.code=='C':
                    c+=1
                if shift.code=='G1':
                    g1+=1
                if shift.code=='G2':
                    g2+=1
            sql = '''
                    select id from arul_hr_holiday_special where EXTRACT(month from date)=%s and EXTRACT(year from date)=%s 
            '''%(int(month), int(year))
            self.cr.execute(sql)
#             date_holiday = self.cr.dictfetchone()
            holiday_ids = [r[0] for r in self.cr.fetchall()]
            date_holiday_count =  0
            if holiday_ids:
                for date_holiday in self.pool.get('arul.hr.holiday.special').browse(self.cr, self.uid, holiday_ids):
                    
                    sql = '''
                        select count(work_date) as date_holiday_count 
                        from arul_hr_punch_in_out_time 
                        where work_date = '%s' and EXTRACT(month from work_date)=%s and EXTRACT(year from work_date)=%s and
                            punch_in_out_id in (select id from arul_hr_employee_attendence_details where employee_id=%s)
                    '''%(date_holiday.date, int(month), int(year),employee.id)
                    self.cr.execute(sql)
                    date_holiday_count = self.cr.dictfetchone()['date_holiday_count']
                    date_holiday_count += date_holiday_count 
                    #raise osv.except_osv(_('Warning!%s'),_(sql)) 
            special_holiday_worked_count =  0                              
            sql = '''
                        SELECT COUNT(work_date) AS date_holiday_count 
                        FROM arul_hr_punch_in_out_time 
                        WHERE work_date IN (SELECT date FROM arul_hr_holiday_special 
                        WHERE EXTRACT(month from date)=%s AND EXTRACT(year from date)=%s ) AND 
                        EXTRACT(month from work_date)=%s AND EXTRACT(year from work_date)=%s AND
                        punch_in_out_id IN (SELECT id FROM arul_hr_employee_attendence_details WHERE employee_id=%s)
                    '''%(int(month), int(year), int(month), int(year), employee.id)
            self.cr.execute(sql)
            special_holiday_worked_count = self.cr.dictfetchone()['date_holiday_count']    
                
            sql = '''
                select leave_type_id 
                from arul_hr_employee_leave_details 
                where employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done' group by leave_type_id
            '''%(employee.id,int(month), int(year))
            self.cr.execute(sql)
            leave_type_ids = [r[0] for r in self.cr.fetchall()]
            c_off = False
            c_l = False
            s_l = False
            p_l = False
            esi = False
            lop = False
            available_leave = False
            for leave_type in self.pool.get('arul.hr.leave.types').browse(self.cr,self.uid,leave_type_ids):
                
                if (leave_type.code=='C.Off' or leave_type.name=='Compensatory Off'):
                    sql = '''
                        select case when sum(days_total)!=0 then sum(days_total) else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    c_off = self.cr.dictfetchone()
                    sql = '''
                        select case when available_leave!=0 then available_leave else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    available_leave = self.cr.dictfetchone()
                    
                if (leave_type.code=='CL' or leave_type.name=='Casual Leave'):
                    sql = '''
                        select case when sum(days_total)!=0 then sum(days_total) else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    c_l = self.cr.dictfetchone()
                    
                if (leave_type.code=='SL' or leave_type.name=='Sick Leave'):
                    sql = '''
                        select case when sum(days_total)!=0 then sum(days_total) else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    s_l = self.cr.dictfetchone()
                    
                if (leave_type.code=='PL' or leave_type.name=='Privilege Leave'):
                    sql = '''
                        select case when sum(days_total)!=0 then sum(days_total) else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    p_l = self.cr.dictfetchone()
                    
                if (leave_type.code=='ESI' or leave_type.name=='ESI Leave'):
                    sql = '''
                        select case when sum(days_total)!=0 then sum(days_total) else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    esi = self.cr.dictfetchone()
                    
                if (leave_type.code=='LOP' or leave_type.name=='LOP'):
                    sql = '''
                        select case when sum(days_total)!=0 then sum(days_total) else 0 end sum_leave 
                        from arul_hr_employee_leave_details 
                        where leave_type_id = %s and employee_id = %s and EXTRACT(month from date_from)=%s and EXTRACT(year from date_from)=%s and state = 'done'
                    '''%(leave_type.id,employee.id,int(month), int(year))
                    self.cr.execute(sql)
                    lop = self.cr.dictfetchone()
            
            sql = '''
                select id from arul_hr_punch_in_out_time where EXTRACT(month from work_date)=%s and EXTRACT(year from work_date)=%s and
                        punch_in_out_id in (select id from arul_hr_employee_attendence_details where employee_id=%s) order by work_date, id
                '''%(int(month), int(year),employee.id)
            self.cr.execute(sql)
            punch_in_out_time_ids = [r[0] for r in self.cr.fetchall()]
            A = self.pool.get('arul.hr.punch.in.out.time').browse(self.cr, self.uid, punch_in_out_time_ids)
            c_off_day = 0
            
            for i,line1 in enumerate(A):
                date1 = line1.work_date
                if (line1.planned_work_shift_id and line1.planned_work_shift_id.code != 'W') or (line1.actual_work_shift_id and line1.actual_work_shift_id.code != 'W'):
# trường hợp không 'W' và planned = actual                        
                    if (line1.planned_work_shift_id == line1.actual_work_shift_id):
                        if line1.in_time > line1.out_time:
                            time_total_actual = 24 - line1.in_time + line1.out_time
                        else:
                            time_total_actual = line1.out_time - line1.in_time
                        if line1.diff_day and (line1.in_time <= line1.out_time):
                            time_total_actual += 24
                        
                        if line1.planned_work_shift_id.start_time > line1.planned_work_shift_id.end_time:
                            time_total_planned = 24 - line1.planned_work_shift_id.start_time + line1.planned_work_shift_id.end_time
                        else:
                            time_total_planned = line1.planned_work_shift_id.end_time - line1.planned_work_shift_id.start_time
                        extra_hours = time_total_actual - time_total_planned
                        if extra_hours >= 4 and extra_hours < 8:
                            c_off_day += 0.5
                        if extra_hours >= 8 and extra_hours < 12:
                            c_off_day += 1
                        if extra_hours >= 12 and extra_hours < 16:
                            c_off_day += 1.5
                        if extra_hours >= 16:
                            c_off_day += 2
                        
                        B = A[i+1:]
                        for j,line2 in enumerate(B):
                            date2 = line2.work_date
                            if (date1==date2):
                                if line2.in_time > line2.out_time:
                                    time_total_actual = 24 - line2.in_time + line2.out_time
                                else:
                                    time_total_actual = line2.out_time - line2.in_time
                                if line2.diff_day and (line2.in_time <= line2.out_time):
                                    time_total_actual += 24
                                # tinh sum_c_off lam them 1 ca
                                if line2.actual_work_shift_id:
                                    if line2.actual_work_shift_id.start_time > line2.actual_work_shift_id.end_time:
                                        shift_hours = 24-line2.actual_work_shift_id.start_time + line2.actual_work_shift_id.end_time
                                    else:
                                        shift_hours = line2.actual_work_shift_id.end_time - line2.actual_work_shift_id.start_time
                                elif line2.planned_work_shift_id:
                                    if line2.planned_work_shift_id.start_time > line2.planned_work_shift_id.end_time:
                                        shift_hours = 24-line2.planned_work_shift_id.start_time + line2.planned_work_shift_id.end_time
                                    else:
                                        shift_hours = line2.planned_work_shift_id.end_time - line2.planned_work_shift_id.start_time
                                else:
                                    shift_hours = 8
                                extra_hours = time_total_actual-shift_hours
                                if extra_hours >= 4 and extra_hours < 8:
                                    c_off_day += 0.5
                                if extra_hours >= 8 and extra_hours < 12:
                                    c_off_day += 1
                                if extra_hours >= 12 and extra_hours < 16:
                                    c_off_day += 1.5
                                if extra_hours >= 16:
                                    c_off_day += 2
                                c_off_day += 1
                                if j==0:
                                    index = i+j+1
                                test = A.pop(index)
                            else: 
                                break
# trường hợp không 'W' và planned != actual
#                     else:
# trường hợp có 'W'                          
                else: 
# trường hợp có 'W' và planned = actual
                    if (line1.planned_work_shift_id == line1.actual_work_shift_id):
                        if line1.in_time > line1.out_time:
                            time_total_actual = 24 - line1.in_time + line1.out_time
                        else:
                            time_total_actual = line1.out_time - line1.in_time
                        if line1.diff_day and (line1.in_time <= line1.out_time):
                            time_total_actual += 24
                        
                        if line1.planned_work_shift_id.start_time > line1.planned_work_shift_id.end_time:
                            time_total_planned = 24 - line1.planned_work_shift_id.start_time + line1.planned_work_shift_id.end_time
                        else:
                            time_total_planned = line1.planned_work_shift_id.end_time - line1.planned_work_shift_id.start_time
                        extra_hours = time_total_actual - time_total_planned
                        if extra_hours >= 4 and extra_hours < 8:
                            c_off_day += 0.5
                        if extra_hours >= 8 and extra_hours < 12:
                            c_off_day += 1
                        if extra_hours >= 12 and extra_hours < 16:
                            c_off_day += 1.5
                        if extra_hours >= 16:
                            c_off_day += 2
                        
                        B = A[i+1:]
                        for j,line2 in enumerate(B):
                            date2 = line2.work_date
                            if (date1==date2):
                                if line2.in_time > line2.out_time:
                                    time_total_actual = 24 - line2.in_time + line2.out_time
                                else:
                                    time_total_actual = line2.out_time - line2.in_time
                                if line2.diff_day and (line2.in_time <= line2.out_time):
                                    time_total_actual += 24
                                shift_hours = 0
                                extra_hours = time_total_actual-shift_hours
                                if extra_hours >= 4 and extra_hours < 8:
                                    c_off_day += 0.5
                                if extra_hours >= 8 and extra_hours < 12:
                                    c_off_day += 1
                                if extra_hours >= 12 and extra_hours < 16:
                                    c_off_day += 1.5
                                if extra_hours >= 16:
                                    c_off_day += 2
                                c_off_day += 1
                                if j==0:
                                    index = i+j+1
                                test = A.pop(index)
                            else: 
                                break
#                     else:
                        #trường họp có W và planned != actual
                    
            #
                
            res.append({
                'emp_id': employee.employee_id or '',
                'emp_name': employee.name + ' ' + (employee.last_name and employee.last_name or ''),
                'date':date and date['date'] or '',
                'a':tpt_a,
                'b':tpt_b,
                'c':tpt_c,
                'g1':tpt_g1,
                'g2':tpt_g2,
                #'total': a+b+c+g1+g2,
                'total': tpt_a+tpt_b+tpt_c+tpt_g1+tpt_g2,
                'c_off': c_off and c_off['sum_leave'] or '',
                'c_l': c_l and c_l['sum_leave'] or '',
                's_l': s_l and s_l['sum_leave'] or '',
                'p_l': p_l and p_l['sum_leave'] or '',
                'esi': esi and esi['sum_leave'] or '',
                'lop': lop and lop['sum_leave'] or '',
                'c_off_day': c_off_day,
                #'date_holiday_count':date_holiday_count or '', #TPT COMMENTED
                'date_holiday_count':special_holiday_worked_count or '',
                'perm_onduty_count':perm_onduty_count,
                'total_shift_worked':total_shift_worked,
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

