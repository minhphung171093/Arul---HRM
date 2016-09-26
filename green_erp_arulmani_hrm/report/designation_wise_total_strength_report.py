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
import math

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

""" 
TPT-RAKESHKUMAR - 15-09-16 - Designation Wise Total Strength Report - ticket-2664
"""

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_hr_emp':self.get_hr_emp,
            'convert_date':self.convert_date,
        })
        
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_hr_emp(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        category = wizard_data['employee_category']
        
        res = []   
        emp_obj = self.pool.get('hr.job') 
        sl_no = 1
        
        sql = '''
        select jb.id,jb.name from hr_employee he
        join hr_job jb on he.job_id=jb.id
        join vsis_hr_employee_category ec on he.employee_category_id=ec.id
        join resource_resource rr on he.id=rr.id 
        where rr.active='t' and he.employee_category_id=%s
        order by jb.name
           '''%(category[0])
        self.cr.execute(sql)    
        for job_line in self.cr.dictfetchall():
            tl_count = 0 
            sql = '''
             select he.employee_id,he.name_related,he.date_of_joining,ec.name as cate_name from hr_employee he
             join vsis_hr_employee_category ec on he.employee_category_id=ec.id
             join resource_resource rr on he.id=rr.id 
             where rr.active='t' and he.job_id=%s and he.employee_category_id=%s
            '''%(job_line['id'], category[0])
            self.cr.execute(sql) 
            for emp_line in self.cr.dictfetchall():
                tl_count += 1
                res.append({
                    's_no' : sl_no  ,
                    'job_id' : job_line['name'] or False,
                    'employee_code' : emp_line['employee_id'] or False,
                    'employee_name' : emp_line['name_related'] or False,
                    'tl_count' : 1 ,
                    'cate_name' : emp_line['cate_name'] or False,
                    'date_of_joining' : emp_line['date_of_joining'] or False,
                })
            sl_no += 1
            #
            res.append({
                    's_no' : ''  ,
                    'job_id' : '',
                    'employee_code' : '',
                    'employee_name' : '',
                    'tl_count' : tl_count,
                    'cate_name' : '' ,
                    'date_of_joining' : '' ,
                })
            #
        return res      
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y') 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

