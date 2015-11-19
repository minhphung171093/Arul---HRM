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
TPT - By BalamuruganPurushothaman - Incident No: 3269 - on 17/11/2015
Canteen Deduction Report : Display the Canteen Deduction Amt for the Month given
"""

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_emp':self.get_emp,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
        })
    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        category = wizard_data['employee_category']
        
        res = []   
        emp_obj = self.pool.get('hr.employee') 
        sl_no = 1
        
        sql = '''
        select distinct employee_id from tpt_canteen_deduction where issue_date between '%s' and '%s'
        and state='approve'
        '''%(date_from, date_to)
        
        if category[1]=='Executives(S1)':
            sql += "and employee_id in (select id from hr_employee where employee_category_id=%s)"%category[0]
        elif category[1]=='Staff(S2)':
            sql += "and employee_id in (select id from hr_employee where employee_category_id=%s)"%category[0]
        elif category[1]=='Workers(S3)':
            sql += "and employee_id in (select id from hr_employee where employee_category_id=%s)"%category[0]
        
        self.cr.execute(sql)     
        
        for line in self.cr.dictfetchall():
            emp_id = line['employee_id'] or False
            emp_ids = emp_obj.browse(self.cr,self.uid,emp_id)
            emp_code = emp_ids.employee_id
            emp_name = emp_ids.name_related
            emp_categ = emp_ids.employee_category_id
            sql = '''
            select case when sum(no_of_book)>0 then sum(no_of_book) else 0 end count from tpt_canteen_deduction where issue_date between '%s' and '%s'
            and employee_id=%s and state='approve' and book_type_id=(select id from tpt_canteen_book_type where name='Breakfast')
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            bf = self.cr.fetchall()
            bf = bf[0]
            
            sql = '''
            select case when sum(no_of_book)>0 then sum(no_of_book) else 0 end count from tpt_canteen_deduction where issue_date between '%s' and '%s'
            and employee_id=%s and state='approve' and book_type_id=(select id from tpt_canteen_book_type where name='Lunch')
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            lunch = self.cr.fetchall()
            lunch = lunch[0]
            
            sql = '''
            select case when sum(no_of_book)>0 then sum(no_of_book) else 0 end count from tpt_canteen_deduction where issue_date between '%s' and '%s'
            and employee_id=%s and state='approve' and book_type_id=(select id from tpt_canteen_book_type where name='Dinner')
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            dinner = self.cr.fetchall()
            dinner = dinner[0]
            
            sql = '''
            select case when sum(no_of_book)>0 then sum(no_of_book) else 0 end count from tpt_canteen_deduction where issue_date between '%s' and '%s'
            and employee_id=%s and state='approve' and book_type_id=(select id from tpt_canteen_book_type where name='Night tiffin')
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            night_tiffin = self.cr.fetchall()
            night_tiffin = night_tiffin[0]
            
            sql = '''
            select case when sum(no_of_book)>0 then sum(no_of_book) else 0 end count from tpt_canteen_deduction where issue_date between '%s' and '%s'
            and employee_id=%s and state='approve' and book_type_id=(select id from tpt_canteen_book_type where name='Non Veg')
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            non_veg = self.cr.fetchall()
            non_veg = non_veg[0]
            
            sql = '''
            select case when sum(no_of_book)>0 then sum(no_of_book) else 0 end count from tpt_canteen_deduction where issue_date between '%s' and '%s'
            and employee_id=%s and state='approve' and book_type_id=(select id from tpt_canteen_book_type where name='Omlette')
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            omlette = self.cr.fetchall()
            omlette = omlette[0]
            
            sql = '''   
                 
            select case when sum(net_value)>0 then sum(net_value) else 0 end count from tpt_canteen_deduction 
            where issue_date between '%s' and '%s'
            and employee_id=%s
            and state='approve'
            '''%(date_from, date_to,emp_id)
            self.cr.execute(sql) 
            emp_dec_amt = self.cr.fetchall()
            emp_dec_amt = emp_dec_amt[0]
            
            res.append({
                's_no' : sl_no  ,
                'employee_code' : emp_code or False,
                'employee_name' : emp_name or False,
                'employee_categ' : emp_categ or False,
                'bf_count' : bf or 0,
                'lunch_count' : lunch or 0,
                'dinner' : dinner or 0,
                'night_tiffin' : night_tiffin or 0,
                'non_veg' : non_veg or 0,
                'omlette' : omlette or 0, 
                'emp_dec_amt' : emp_dec_amt or 0,
            })
            sl_no += 1
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

