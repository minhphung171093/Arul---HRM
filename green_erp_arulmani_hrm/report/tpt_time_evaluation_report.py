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
                    punch_in_out_id in (select id from arul_hr_employee_attendence_details where employee_id=%s)
            '''%(int(month), int(year),employee.id)
            self.cr.execute(sql)
            actual_work_shift_ids = [r[0] for r in self.cr.fetchall()]
            a=0
            b=0
            c=0
            g1=0
            g2=0
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
            res.append({
                'emp_id': employee.employee_id or '',
                'emp_name': employee.name + ' ' + (employee.last_name and employee.last_name or ''),
                'date':date and date['date'] or '',
                'a':a,
                'b':b,
                'c':c,
                'g1':g1,
                'g2':g2,
                'total': a+b+c+g1+g2,
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

