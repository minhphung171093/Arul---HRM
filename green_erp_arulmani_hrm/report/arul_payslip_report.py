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
        return wizard_data['month']

    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']

    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        emp_ids = wizard_data['employee_ids']
        month=wizard_data['month']
        year=wizard_data['year']
        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
        res = []
        for emp_id in emp_ids :
            payroll_ids = payroll_obj.search(self.cr, self.uid,[('month','=',month),('year','=',year),('employee_id','=',emp_id)])
            basic = 0
            employee_name 
            if payroll_ids:
                payroll = payroll_obj.browse(self.cr, self.uid, payroll_ids[0])
                for earning in payroll.earning_structure_line:
                    if earning.earning_parameters_id.code=='BASIC':
                        basic += earning.float
                res.append({
                    'emp_name': payroll.employee_id.name + ' ' + payroll.employee_id.last_name,
                    'basic': basic,
                })
        return res
                
                
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

