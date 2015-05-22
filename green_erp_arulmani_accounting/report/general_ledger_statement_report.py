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
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_cus': self.get_cus,
            'convert_date_cash': self.convert_date_cash,
            'get_invoice':self.get_invoice,
            'get_doc_type':self.get_doc_type,
        })
        
    def get_cus(self):
        wizard_data = self.localcontext['data']['form']
        cus = (wizard_data['customer_id'])
        cus_obj = self.pool.get('res.partner')
        return cus_obj.browse(self.cr,self.uid,cus[0])
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
            
    def convert_date_cash(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date(self):
        res = {}
        date = time.strftime('%d/%m/%Y'),
        date = datetime.strptime(date[0], DATE_FORMAT)
        day = date.day
        month = date.month
        year = date.year
        res = {
               'day': day,
               'month': month,
               'year': year,
               }
        return res

    def get_doc_type(self, doc_type):
        if doc_type == 'cus_inv':
            return "Customer Invoice"
        if doc_type == 'cus_pay':
            return "Customer Payment"
        if doc_type == 'sup_inv_po':
            return "Supplier Invoice(With PO)"
        if doc_type == 'sup_inv':
            return "Supplier Invoice(Without PO)"
        if doc_type == 'sup_pay':
            return "Supplier Payment"
        if doc_type == 'payroll':
            return "Executives Payroll"
        if doc_type == 'staff_payroll':
            return "Staff Payroll"
        if doc_type == 'worker_payroll':
            return "Workers Payroll"
        if doc_type == 'grn':
            return "GRN"
        if doc_type == 'good':
            return "Good Issue"
        if doc_type == 'do':
            return "DO"
        if doc_type == 'inventory':
            return "Inventory Transfer"
        if doc_type == 'manual':
            return "Manual Journal"
        if doc_type == 'cash_pay':
            return "Cash Payment"
        if doc_type == 'cash_rec':
            return "Cash Receipt"
        if doc_type == 'bank_pay':
            return "Bank Payment"
        if doc_type == 'bank_rec':
            return "Bank Receipt"
        if doc_type == 'ser_inv':
            return "Service Invoice"
        if doc_type == 'product':
            return "Production"
        
        
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        gl_account = wizard_data['account_id']
        acc_obj = self.pool.get('account.account')
        acc = acc_obj.browse(self.cr,self.uid,gl_account[0])
        doc_type = wizard_data['doc_type']
        doc_no = wizard_data['doc_no'] or ''
        narration = wizard_data['narration'] or ''
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        acount_move_line_obj = self.pool.get('account.move.line')
        acount_move_obj = self.pool.get('account.move')
        cus_ids = []
        if doc_no :
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and name ~'%s' and state='posted' ) and account_id = %s   
            '''%(date_from, date_to,doc_no,acc.id)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        elif narration :
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and state='posted' ) and account_id = %s and ref ~'%s'
            '''%(date_from, date_to,acc.id,narration)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        elif doc_no and narration:
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and name ~'%s' and state='posted' ) and account_id = %s and ref ~'%s'
            '''%(date_from, date_to,doc_no,acc.id,narration)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        elif doc_type :
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and doc_type in('%s') and state='posted' ) and account_id = %s   
            '''%(date_from, date_to,doc_type,acc.id)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        elif narration and doc_type :
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and doc_type in('%s') and state='posted' ) and account_id = %s and ref ~'%s'
            '''%(date_from, date_to,doc_type,acc.id,doc_no)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        elif doc_no and doc_type :
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and doc_type in('%s') and name ~'%s' and state='posted' ) and account_id = %s 
            '''%(date_from, date_to,doc_type,doc_no,acc.id)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        elif doc_no and doc_type and narration:
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and doc_type in('%s') and name ~'%s' and state='posted' ) and account_id = %s and ref ~'%s'
            '''%(date_from, date_to,doc_type,doc_no,acc.id)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        else:
            sql = '''
                select id from account_move_line 
                where move_id in (
                                    select id from account_move 
                                    where date between '%s' and '%s' and state='posted' ) and account_id = %s
            '''%(date_from, date_to,acc.id)
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
#             sql = '''
#                 select id from account_move_line 
#                 where move_id in (
#                                     select id from account_move 
#                                     where date between '%s' and '%s' and doc_type in ('cus_pay') and partner_id = %s and state='posted' ) and credit is not null and credit !=0   
#                 '''%(date_from, date_to,cus[0])
#             self.cr.execute(sql)
#             cus_ids += [r[0] for r in self.cr.fetchall()]
        return acount_move_line_obj.browse(self.cr,self.uid,cus_ids)
    
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

