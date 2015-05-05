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
        })
        
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return self.get_month_name(wizard_data['month'])
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']
    
    def get_payroll(self):
        wizard_data = self.localcontext['data']['form']
        month=wizard_data['month']
        year=wizard_data['year']
        payroll_oj = self.pool.get('arul.hr.payroll.executions.details')
        sql = '''
            select id from arul_hr_payroll_executions_details where month = '%s' and year = '%s'
            '''%(str(month), str(year))
        self.cr.execute(sql)
        payroll_ids = [r[0] for r in self.cr.fetchall()]
        return payroll_oj.browse(self.cr,self.uid,payroll_ids)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

