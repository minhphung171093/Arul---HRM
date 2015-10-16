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
            'get_InOut':self.get_InOut,
            'get_workdate':self.get_workdate,
            'float_time_convert':self.float_time_convert,
            'get_date':self.get_date,
            'get_shift_type':self.get_shift_type,
        })
        
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')     
    
    def float_time_convert(self, float_val):
        if float_val:
            float_val = float(float_val)
            factor = float_val < 0 and -1 or 1
            val = abs(float_val)
            a = str(factor * int(math.floor(val)) )
            b = str(int(round((val % 1) * 60)))
            
            
            if len(str(factor * int(math.floor(val)) ))==1:
                a = '0'+str(factor * int(math.floor(val)) )
            if len(str(int(round((val % 1) * 60))))==1:
                b = '0'+str(int(round((val % 1) * 60)))
            if b==60:
                a = int(a)
                a += 1
                a = str(a)
                b = '00'
            time =  a+ ':' + b
            return time
        else:
            return ''
    
    def get_InOut(self):
        wizard_data = self.localcontext['data']['form']
        workdate=wizard_data['workdate']
        shift_type=wizard_data['shift_type']
        if shift_type=='a_shift':
            shift_type='A'
        if shift_type=='g1_shift':
            shift_type='G1'
        if shift_type=='g2_shift':
            shift_type='G2'
        if shift_type=='b_shift':
            shift_type='B'
        if shift_type=='c_shift':
            shift_type='C'
       
        shifts_ids = []
        c_earlier_entries_ids = []  
        if shift_type=='C': # to fetch C Shift earlier entries
            sql = '''
              select emp.employee_id, emp.name_related employeename, COALESCE(ast.ref_in_time,0.0) as ref_in_time, 
              COALESCE(ast.ref_out_time,0.0) as ref_out_time
                from arul_hr_audit_shift_time ast
             inner join hr_employee emp on ast.employee_id=emp.id
             where ref_in_time between (select min_in_time from tpt_work_shift where 
             code='B+C HALF') and (select max_in_time from tpt_work_shift where
             code='B+C HALF') and ast.work_date='%s'
             order by emp.employee_id
            '''%(workdate)               
            self.cr.execute(sql)
            c_earlier_entries_ids = self.cr.dictfetchall()  
        sql = '''
          select emp.employee_id, emp.name_related employeename, COALESCE(ast.ref_in_time,0.0) as ref_in_time, 
          COALESCE(ast.ref_out_time,0.0) as ref_out_time
            from arul_hr_audit_shift_time ast
         inner join hr_employee emp on ast.employee_id=emp.id
         where ref_in_time between (select min_in_time from tpt_work_shift where 
         code='%s') and (select max_in_time from tpt_work_shift where
         code='%s') and ast.work_date='%s'
         order by emp.employee_id
        '''%(shift_type, shift_type, workdate)               
        self.cr.execute(sql)
        shifts_ids = self.cr.dictfetchall()
        
        if shift_type=='C':
            c_earlier_entries_ids += shifts_ids   
            shifts_ids = c_earlier_entries_ids     
        
        res = []
        s_no = 1
        for line in shifts_ids: #self.cr.dictfetchall():
            res.append({
                        's_no':s_no,
                        'employee_id': line['employee_id'] or '',
                        'employeename': line['employeename'] or '',
                        'ref_in_time': line['ref_in_time'] or '',                  
                        })
            s_no += 1
        return res     
    
    def get_workdate(self):
        wizard_data = self.localcontext['data']['form']
        workdate=wizard_data['workdate']
        return   workdate   
    def get_shift_type(self):
        wizard_data = self.localcontext['data']['form']
        shift_type=wizard_data['shift_type']
        if shift_type=='a_shift':
            shift_type='A'
        if shift_type=='g1_shift':
            shift_type='G1'
        if shift_type=='g2_shift':
            shift_type='G2'
        if shift_type=='b_shift':
            shift_type='B'
        if shift_type=='c_shift':
            shift_type='C'
        return   shift_type   
         
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

