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
            'get_leave_balance':self.get_leave_balance,
            
        })
    #def get_pf_no(self, employee):
    #    esi_no = ''
    #     if employee and employee.statutory_ids:
    #        esi_no = employee.statutory_ids[0].name
    #    return esi_no     
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return self.get_month_name(wizard_data['month'])
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']
    
#     def get_payroll(self):
#         wizard_data = self.localcontext['data']['form']
#         month=wizard_data['month']
#         year=wizard_data['year']
#         payroll_oj = self.pool.get('arul.hr.payroll.executions.details')
#         sql = '''
#             select id from arul_hr_payroll_executions_details where month = '%s' and year = '%s'
#             '''%(str(month), str(year))
#         self.cr.execute(sql)
#         payroll_ids = [r[0] for r in self.cr.fetchall()]
#         return payroll_oj.browse(self.cr,self.uid,payroll_ids)
    
    def get_leave_balance(self):
        wizard_data = self.localcontext['data']['form']
        month=wizard_data['month']
        year=wizard_data['year']
        employee=wizard_data['employee']
        employee_category=wizard_data['employee_category']
        department=wizard_data['department']
        employee_obj = self.pool.get('hr.employee')
        
        res = []
        
        if department:
            employee_ids = employee_obj.search(self.cr, self.uid,[('department_id', '=', department)])
        elif department and employee_category:
            employee_ids = employee_obj.search(self.cr, self.uid,[('department_id', '=', department),('employee_category_id', '=', employee_category)])
        elif department and employee_category and employee:
            employee_ids = employee_obj.search(self.cr, self.uid,[('department_id', '=', department),
                                                                  ('employee_category_id', '=', employee_category),
                                                                  ('employee_id', '=', employee[0]),
                                                                  ])
        elif employee:
            employee_ids = employee_obj.search(self.cr, self.uid,[('id', '=', employee[0])])
        elif employee_category:
            employee_ids = employee_obj.search(self.cr, self.uid,[('employee_category_id', '=', employee_category[0])])

        for employee in employee_obj.browse(self.cr, self.uid, employee_ids):
            
            ### START CL
            cl_count_pm = 0
            cl_count_total_days = 0
            cl_count_cb = 0
            open_bal = 0  
            cl_count_ob = 0                          
            sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
                SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s 
                AND EXTRACT(month FROM date_from) = %s AND employee_id =%s AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('CL'))
                and state='done'  
            '''%(year,month,employee.id)
            self.cr.execute(sql)
            temp_cl = self.cr.fetchone()
            cl_count_pm = temp_cl[0] 
            
            sql = '''
                select  
                CASE WHEN SUM(total_day)!=0 THEN 
                SUM(total_day) ELSE 0 END total_day
                from employee_leave_detail
                where emp_leave_id in (select id from employee_leave where year = '%s'
                and employee_id = (select id from hr_employee where id= %s) )
                and leave_type_id = (select id from arul_hr_leave_types where code = 'CL')
            '''%(year,employee.id)
            self.cr.execute(sql)
            temp_cl = self.cr.fetchone()
            
            cl_count_total_days = temp_cl[0]  # CL Opening Balance
            
            sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
            SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s
                AND EXTRACT(month FROM date_from) between 4 and %s-1 AND
                 employee_id = (select id from hr_employee where id=%s) AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('CL'))
                and state='done'
            '''%(year,int(month),employee.id)
            self.cr.execute(sql)
            temp_cl = self.cr.fetchone()
            cl_count_cb = temp_cl[0]  # CL Closing Balance for Prev Month
            
            open_bal = cl_count_total_days - cl_count_cb
            
            cl_count_cb = open_bal - cl_count_pm
            
            ### END CL
            
            ### START SL
            sl_count_pm = 0
            sl_count_total_days = 0
            sl_count_cb = 0
            sl_open_bal = 0  
            sl_count_ob = 0                          
            sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
                SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s 
                AND EXTRACT(month FROM date_from) = %s AND employee_id =%s AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('SL'))
                and state='done'  
            '''%(year,month,employee.id)
            self.cr.execute(sql)
            temp_sl = self.cr.fetchone()
            sl_count_pm = temp_sl[0] 
            
            sql = '''
                select  
                CASE WHEN SUM(total_day)!=0 THEN 
            SUM(total_day) ELSE 0 END total_day
                from employee_leave_detail
                where emp_leave_id in (select id from employee_leave where year = '%s'
                and employee_id = (select id from hr_employee where id= %s) )
                and leave_type_id = (select id from arul_hr_leave_types where code = 'SL')
            '''%(year,employee.id)
            self.cr.execute(sql)
            temp_sl = self.cr.fetchone()
            sl_count_total_days = temp_sl[0] # CL Opening Balance
            
            sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
            SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s
                AND EXTRACT(month FROM date_from) between 4 and %s-1 AND
                 employee_id = (select id from hr_employee where id=%s) AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('SL'))
                and state='done'
            '''%(year,int(month),employee.id)
            self.cr.execute(sql)
            temp_sl = self.cr.fetchone()
            sl_count_cb = temp_sl[0]  # CL Closing Balance for Prev Month
            
            sl_open_bal = sl_count_total_days - sl_count_cb
            
            sl_count_cb = sl_open_bal - sl_count_pm
            
            ### END SL
            
             ### START PL
            pl_count_pm = 0
            pl_count_total_days = 0
            pl_count_cb = 0
            pl_open_bal = 0  
            pl_count_ob = 0                          
            sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
                SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s 
                AND EXTRACT(month FROM date_from) = %s AND employee_id =%s AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('PL'))
                and state='done'  
            '''%(year,month,employee.id)
            self.cr.execute(sql)
            temp_pl = self.cr.fetchone()
            pl_count_pm = temp_pl[0]
            
            sql = '''
                select CASE WHEN SUM(total_day)!=0 THEN 
            SUM(total_day) ELSE 0 END total_day from employee_leave_detail
                where emp_leave_id in (select id from employee_leave where year = '%s'
                and employee_id = (select id from hr_employee where id= %s) )
                and leave_type_id = (select id from arul_hr_leave_types where code = 'PL')
            '''%(year,employee.id)
            self.cr.execute(sql)
            temp_pl = self.cr.fetchone()
            pl_count_total_days = temp_pl[0]
            
            sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
            SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s
                AND EXTRACT(month FROM date_from) between 4 and %s-1 AND
                 employee_id = (select id from hr_employee where id=%s) AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('PL'))
                and state='done'
            '''%(year,int(month),employee.id)
            self.cr.execute(sql)
            temp_pl = self.cr.fetchone()
            pl_count_cb = temp_pl[0]  # CL Closing Balance for Prev Month
            
            pl_open_bal = pl_count_total_days - pl_count_cb
            
            pl_count_cb = pl_open_bal - pl_count_pm
            
            ### END PL
            
            
            res.append({
                        'employee_id':employee.employee_id,
                        'emp_name':employee.name,
                        'designation':employee.job_id.name,
                        'cl_count_pm':cl_count_pm,
                        'cl_count_total_days':cl_count_total_days,
                        'cl_count_cb':cl_count_cb,
                        'cl_count_ob':open_bal,
                        'sl_count_pm':sl_count_pm,
                        'sl_count_total_days':sl_count_total_days,
                        'sl_count_cb':sl_count_cb,
                        'sl_count_ob':sl_open_bal,                        
                        'pl_count_pm':pl_count_pm,
                        'pl_count_total_days':pl_count_total_days,
                        'pl_count_cb':pl_count_cb,
                        'pl_count_ob':pl_open_bal,
                                                
                        })
             
        return res
    
    
                
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

