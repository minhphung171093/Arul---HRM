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
            'get_payroll':self.get_payroll,
            'get_epf_wages': self.get_epf_wages,
            'get_epf_contribution_due': self.get_epf_contribution_due,
            'get_eps_contribution_due': self.get_eps_contribution_due,
        })
        
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
    
    def get_payroll(self):
        wizard_data = self.localcontext['data']['form']
        month=wizard_data['month']
        year=wizard_data['year']
        payroll_oj = self.pool.get('arul.hr.payroll.executions.details')
        sql = '''
            select pa.id from arul_hr_payroll_executions_details pa,hr_employee em 
                where pa.month = '%s' and pa.year = '%s' and em.id = pa.employee_id order by em.employee_id
            '''%(str(month), str(year))
        self.cr.execute(sql)
        payroll_ids = [r[0] for r in self.cr.fetchall()]
        return payroll_oj.browse(self.cr,self.uid,payroll_ids)
    
    def get_epf_wages(self, earning):
        epf_wages = 0
        for line in earning:
            if line.earning_parameters_id.code == 'BASIC':
                epf_wages += line.float
            elif line.earning_parameters_id.code == 'DA':
                epf_wages += line.float
        return epf_wages
        
    def get_epf_contribution_due(self, deduction):
        epf_contribution_due = 0.0
        for line in deduction:
            if line.deduction_parameters_id.code == 'PF.D':
                epf_contribution_due += line.float
        return epf_contribution_due
        
    def get_eps_contribution_due(self, employee):
        if employee.employee_category_id and employee.employee_sub_category_id:
            sql = '''
                select case when employer_pension_con!=0 then employer_pension_con else 0 end employer_pension_con from arul_hr_payroll_contribution_parameters where employee_category_id=%s and sub_category_id=%s
            '''%(employee.employee_category_id.id,employee.employee_sub_category_id.id)
            self.cr.execute(sql)
            pension = self.cr.fetchone()
            if pension:
                return pension and pension[0] or 0
            else:
                return 0
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

