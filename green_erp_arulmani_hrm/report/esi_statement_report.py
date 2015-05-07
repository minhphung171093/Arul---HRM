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
            'get_emp':self.get_emp,
            'get_esi_no': self.get_esi_no,
            'get_no_of_day_work': self.get_no_of_day_work,
            'get_no_of_shift_work': self.get_no_of_shift_work,
            'get_gross': self.get_gross,
            'get_esi_employer': self.get_esi_employer,
            'get_esi_employee': self.get_esi_employee,
            'get_gross_earning': self.get_gross_earning,
        })
    
    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        month = wizard_data['month']
        year = wizard_data['year']
        sql = '''
            select executions_details_id from arul_hr_payroll_other_deductions
                where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='ESI.D') and "float"!=0
                    and executions_details_id in (select id from arul_hr_payroll_executions_details where month='%s' and year='%s')
                group by executions_details_id
        '''%(month,year)
        self.cr.execute(sql)
        payroll_detail_obj = self.pool.get('arul.hr.payroll.executions.details')
        payroll_detail_ids = [r[0] for r in self.cr.fetchall()]
        return payroll_detail_obj.browse(self.cr, self.uid, payroll_detail_ids)
    
    def get_esi_no(self, employee):
        esi_no = ''
        if employee and employee.statutory_ids:
            esi_no = employee.statutory_ids[0].esi_no
        return esi_no
    
    def get_no_of_day_work(self, employee):
        wizard_data = self.localcontext['data']['form']
        month = wizard_data['month']
        year = wizard_data['year']
        sql = '''
            select count(*) as no_of_day_work
                from arul_hr_punch_in_out_time
                    where EXTRACT(month from work_date)=%s and EXTRACT(year from work_date)=%s and
                        punch_in_out_id in (select id from arul_hr_employee_attendence_details where employee_id=%s)
        '''%(int(month), int(year),employee.id)
        self.cr.execute(sql)
        no_of_day_work = self.cr.fetchone()
        return no_of_day_work
    
    def get_no_of_shift_work(self, employee):
        wizard_data = self.localcontext['data']['form']
        month = wizard_data['month']
        year = wizard_data['year']
        sql = '''
            SELECT CASE WHEN SUM(a_shift_count)!=0 THEN SUM(a_shift_count) ELSE 0 END a_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
            AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
            '''%(int(year), int(month),employee.id)
        self.cr.execute(sql)
        t_a =  self.cr.fetchone()
        tpt_a = t_a[0]
        
        sql = '''
            SELECT CASE WHEN SUM(b_shift_count)!=0 THEN SUM(b_shift_count) ELSE 0 END b_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
            AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
            '''%(int(year), int(month),employee.id)
        self.cr.execute(sql)
        t_b =  self.cr.fetchone()
        tpt_b = t_b[0]
        
        sql = '''
            SELECT CASE WHEN SUM(c_shift_count)!=0 THEN SUM(c_shift_count) ELSE 0 END c_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
            AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
            '''%(int(year), int(month),employee.id)
        self.cr.execute(sql)
        t_c =  self.cr.fetchone()
        tpt_c = t_c[0]
        
        sql = '''
            SELECT CASE WHEN SUM(g1_shift_count)!=0 THEN SUM(g1_shift_count) ELSE 0 END g1_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
            AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
            '''%(int(year), int(month),employee.id)
        self.cr.execute(sql)
        t_g1 =  self.cr.fetchone()
        tpt_g1 = t_g1[0]
        
        sql = '''
            SELECT CASE WHEN SUM(g2_shift_count)!=0 THEN SUM(g2_shift_count) ELSE 0 END g2_shift FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
            AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
            '''%(int(year), int(month),employee.id)
        self.cr.execute(sql)
        t_g2 =  self.cr.fetchone()
        tpt_g2 = t_g2[0]
        
        return tpt_a+tpt_b+tpt_c+tpt_g1+tpt_g2
    
    def get_gross(self, employee):
        wizard_data = self.localcontext['data']['form']
        month = wizard_data['month']
        year = wizard_data['year']
        sql = '''
            select sum(float) from arul_hr_payroll_earning_structure
                where executions_details_id in (select id from arul_hr_payroll_executions_details where employee_id=%s and month='%s' and year='%s')
                    and earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='GROSS_SALARY')
        '''%(employee.id,month,year)
        self.cr.execute(sql)
        gross =  self.cr.fetchone()
        return gross

    def get_gross_earning(self, employee):
        wizard_data = self.localcontext['data']['form']
#         month = wizard_data['month']
#         year = wizard_data['year']
        sql = '''
            select CASE WHEN SUM(float)!=0 THEN SUM(float) ELSE 0 END sum_float from arul_hr_payroll_earning_structure earn, arul_hr_payroll_employee_structure stru
                where earn.earning_structure_id = stru.id and stru.employee_id = '%s'
        '''%(employee.id)
        self.cr.execute(sql)
        gross =  self.cr.fetchone()
        return gross
    
    def get_esi_employer(self, employee):
        esi_employer=0
        if employee.employee_category_id and employee.employee_sub_category_id:
            sql = '''
                select case when employer_esi_con!=0 then employer_esi_con else 0 end employer_esi_con from arul_hr_payroll_contribution_parameters where employee_category_id=%s and sub_category_id=%s
            '''%(employee.employee_category_id.id,employee.employee_sub_category_id.id)
            self.cr.execute(sql)
            esi = self.cr.fetchone()
        if esi:
            gross = self.get_gross(employee)
            esi_employer = esi[0]*(gross and gross[0] or 0)/100
        return esi_employer
    
    def get_esi_employee(self, employee):
        wizard_data = self.localcontext['data']['form']
        month = wizard_data['month']
        year = wizard_data['year']
        sql = '''
            select sum(float) from arul_hr_payroll_other_deductions
                where executions_details_id in (select id from arul_hr_payroll_executions_details where employee_id=%s and month='%s' and year='%s')
                    and deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='ESI.D')
        '''%(employee.id,month,year)
        self.cr.execute(sql)
        esi_employee =  self.cr.fetchone()
        return esi_employee
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

