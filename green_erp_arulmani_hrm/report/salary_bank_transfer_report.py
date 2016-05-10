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
            'get_month': self.get_month,
            'get_month_name': self.get_month_name,
            'get_year': self.get_year,   
            'get_emp': self.get_emp,
            'get_move': self.get_move,
            #'get_salary': self.get_salary,
           # 'get_sub_net': self.get_sub_net, 
                                 })
         
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return self.get_month_name(wizard_data['month'])
    
    def get_month_name(self, month):
        month = int(month)
        _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
        d = _months[month]
        return d
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']
    
   # def get_emp(self):
       # payroll_obj = self.pool.get('arul.hr.payroll.executions')
        #return payroll_obj.browse(self.cr, self.uid, self.ids[0]).payroll_executions_details_line   
        
    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        hr_emp = self.pool.get('hr.employee')
        month=wizard_data['month']
        year=wizard_data['year']
        categ_id=wizard_data['employee_category']
        categ_obj=self.pool.get('vsis.hr.employee.category')
        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
        categ1_ids=categ_obj.browse(self.cr,self.uid,categ_id[0])
        category_id=categ1_ids.id
        emp_ids=hr_emp.search(self.cr,self.uid,[('employee_category_id','=',category_id)]) 
        res = []
        for emp_id in emp_ids :
            payroll_ids = payroll_obj.search(self.cr, self.uid,[('month','=',month),('year','=',year),('employee_id','=',emp_id),('payroll_executions_id.state','in',['confirm','approve'])])
            net = 0            
            if payroll_ids:
                payroll = payroll_obj.browse(self.cr, self.uid, payroll_ids[0])
                for earning in payroll.earning_structure_line:
                    if earning.earning_parameters_id.code=='NET':
                        net += earning.float  
                res.append({
                            'emp_id': emp_id,
                            'emp_code':payroll.employee_id.employee_id,
                            'emp_name': payroll.employee_id.name + ' ' + (payroll.employee_id.last_name and payroll.employee_id.last_name or ''),
                            'bank_account': payroll.employee_id.bank_account,
                            'net':format(net,'.2f'),          
                              
                    })
            
                
        return res
    
    def get_move(self):
        move_obj = self.pool.get('account.move')
        sql = ''' select id from account_move limit 10
                '''
        self.cr.execute(sql)
        move_ids = [r[0] for r in self.cr.fetchall()]
        res = []
        
        sql = '''
        SELECT am.create_date,am.Name as document_no, am.ref, to_char(am.date,'dd-mm-yyyy') as posting_date, p.name as period, j.name as journal, rp.name as partner, am.narration,
        (select Sum(debit) from account_move_line where move_id=am.id) as amount,am.state as status
        FROM ACCOUNT_MOVE am
        Inner join account_period p on (p.id=am.period_id)
        inner join account_journal j on (j.id=am.journal_id)
        left Join res_partner rp on (rp.id=am.partner_id)  order by am.date
        --limit 10
        '''
        self.cr.execute(sql)
        
        #for move in move_obj.browse(self.cr, self.uid, move_ids):
        for move in self.cr.dictfetchall():
             res.append({
                        'name':move['document_no'],
                        'posting_date':move['posting_date'],
                        'period':move['period'],
                        'journal':move['journal'],
                        'partner':move['partner'],
                        'narration':move['narration'],
                        'amount':move['amount'],
                        'status':move['status'],
                        
                        
                        
                                                
                        })   
                
        return res
       


    
    