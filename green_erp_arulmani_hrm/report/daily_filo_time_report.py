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

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({           
            'get_date_to':self.get_date_to,
            'get_filo':self.get_filo,
            'get_emp_cat':self.get_emp_cat,
            'get_dept':self.get_dept,
            'convert_date':self.convert_date, 
            'float_time_convert':self.float_time_convert,
            'get_time_in_out':self.get_time_in_out,            
        })
         
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_emp_cat(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['employee_category']:            
            emp_cate_name = ''
            name_ids = [r.name for r in  wizard_data['employee_category']]
            for name in name_ids:
                emp_cate_name += name + ', '
                
                  
            sql = '''
                    select name from vsis_hr_employee_category where id = %s
                  '''%(emp_cat[0])
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                emp_categ = move['name']
                return emp_categ or False
        return ''
    
    def get_dept(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['department']:
            dept = wizard_data['department']
            dept_name = ''
            dept_name_ids = [r.name for r in sls.department_ids]
            for name in dept_name_ids:
                dept_name += name + ', '       
            sql = '''
                    select name from hr_department where id = %s
                  '''%(dept[0])
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                depart = move['name']
                return depart or False
        return ''
    
    def get_filo(self):
        wizard_data = self.localcontext['data']['form']        
        date_to = wizard_data['date_to']
        employee_category_ids= wizard_data['employee_category_ids']
        department_ids=wizard_data['department_id']
        
        if department_ids:
            department_ids = ''
            department_ids = [r.id for r in department_ids]
            department_ids = str(department_ids).replace("[", "")
            department_ids = department_ids.replace("]", "")
            
        if employee_category_ids:
            employee_category_ids = ''
            employee_category_ids = [r.id for r in employee_category_ids]
            employee_category_ids = str(employee_category_ids).replace("[", "")
            employee_category_ids = employee_category_ids.replace("]", "")
        
        sql = '''
                select distinct hr.employee_id as emp_code,hr.name_related as emp_name,
                j.name as desgn,d.name as dept,hst.work_date as work_date,hr.employee_category_id as emp_categ_id,hr.department_id as dept_id,
                (select name from vsis_hr_employee_category where id=hr.employee_category_id) emp_cat,
                hst.in_time, hst.out_time
                from arul_hr_punch_in_out_time hst
                inner join hr_employee hr on (hr.id = hst.employee_id)
                inner join hr_department d on (d.id = hr.department_id)
                inner join hr_job j on (j.id = hr.job_id)
                where hst.work_date = '%s'
                '''%(date_to)
        if employee_category_ids:
            qstr = " and hr.employee_category_id in (%s)"%(emp_category_ids)
            sql = sql+qstr
        if department_ids:
            qstr = " and hr.department_id in (%s)"%(department_ids)
            sql = sql+qstr        
        sql=sql+" order by hr.employee_id,hr.name_related"
        
        self.cr.execute(sql)   
        res = []         
        return  self.cr.dictfetchall()
            
    
    def float_time_convert(self, float_val):
        float_val = float(float_val)
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        a = str(factor * int(math.floor(val)) )
        b = str(int(round((val % 1) * 60)))
        
        
        if len(str(factor * int(math.floor(val)) ))==1:
            a = '0'+str(factor * int(math.floor(val)) )
        if len(str(int(round((val % 1) * 60))))==1:
            b = '0'+str(int(round((val % 1) * 60)))
        time =  a+ ':' + b
        return time
    
    def get_time_in_out(self,date,emp_cat,dept,type):
            
            sql = '''
                    select min(hst.in_time) as intime,max(hst.out_time) as outtime from arul_hr_audit_shift_time hst
                    inner join hr_employee hr on (hr.id = hst.employee_id)
                    where hst.work_date = '%s' 
                '''%(date)
            if emp_cat:
               qstr = " and hr.employee_category_id in (%s)"%(emp_cat)
               sql = sql+qstr
            if dept:
               qstr = " and hr.department_id in (%s)"%(dept)
               sql = sql+qstr 
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                if type == 'in_time':
                    in_time = move['intime']
                    return in_time or False
                if type == 'out_time':
                    out_time = move['outtime']
                    return out_time or False      
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

