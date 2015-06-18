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
            'get_total': self.get_total,
            'get_invoice':self.get_invoice,
            'get_doc_type':self.get_doc_type,
            'get_balance':self.get_balance,
            'get_cheque_no': self.get_cheque_no,
            'get_bill_no': self.get_bill_no,
            'get_bill_date': self.get_bill_date,
            'get_cheque_date': self.get_cheque_date,
            'get_so_no': self.get_so_no,
            'get_so_date': self.get_so_date,
        })
        
    def get_cus(self):
        wizard_data = self.localcontext['data']['form']
        sup = (wizard_data['supplier_id'])
        sup_obj = self.pool.get('res.partner')
        return sup_obj.browse(self.cr,self.uid,sup[0])
    
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
        if doc_type == 'sup_inv':
            return "SUPPLIER INVOICE (without po)"
        if doc_type == 'sup_inv_po':
            return "SUPPLIER INVOICE"
        if doc_type == 'sup_pay':
            return "SUPPLIER PAYMENT"
        
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sup = wizard_data['supplier_id']
        acount_move_line_obj = self.pool.get('account.move.line')
        acount_move_obj = self.pool.get('account.move')
        sup_ids = []
        sql = '''
        
            select aml.id from account_move_line aml 
            inner join account_move am on aml.move_id = am.id
            inner join res_partner p on (p.id=am.partner_id)
            inner join account_account aa on (aa.id=aml.account_id)
                where am.date between '%s' and '%s' and am.doc_type in ('sup_inv_po','sup_inv','sup_pay','ser_inv') 
                and am.partner_id = %s and am.state='posted' and p.vendor_code=aa.code
                    order by am.date
        
            '''%(date_from, date_to,sup[0])
        self.cr.execute(sql)
        sup_ids = [r[0] for r in self.cr.fetchall()]
#         sql = '''
#             select id from account_move_line 
#             where move_id in (
#                                 select id from account_move 
#                                 where date between '%s' and '%s' and doc_type in ('sup_pay') and partner_id = %s and state='posted' ) and credit is not null and credit !=0   
#             '''%(date_from, date_to,sup[0])
#         self.cr.execute(sql)
#         sup_ids += [r[0] for r in self.cr.fetchall()]
        return acount_move_line_obj.browse(self.cr,self.uid,sup_ids)
    
    def get_bill_no(self, move_id, doc_type):
        if doc_type == 'sup_inv_po' or doc_type == 'sup_inv':
            self.cr.execute('''select name from account_invoice where move_id =%s''', (move_id,))
        else:
            self.cr.execute('''select number from account_voucher where move_id =%s''', (move_id,))
        number = self.cr.fetchone()
        return number and number[0] or ''
    
    def get_so_no(self, move_id, doc_type):
        number = ''
        if doc_type == 'sup_inv_po':
            self.cr.execute('''select name from purchase_order where id in (select purchase_id from account_invoice where move_id =%s)''', (move_id,))
        number = self.cr.fetchone()
        return number and number[0] or ''
    
    def get_so_date(self, move_id, doc_type):
        date = ''
        if doc_type == 'sup_inv_po':
            self.cr.execute('''select date_order from purchase_order where id in (select purchase_id from account_invoice where move_id =%s)''', (move_id,))
        date = self.cr.fetchone()
        return date and date[0] or ''
    
    def get_bill_date(self, move_id, doc_type):
        if doc_type == 'sup_inv_po' or doc_type == 'sup_inv':
            self.cr.execute('''select bill_date from account_invoice where move_id =%s''', (move_id,))
        else:
            self.cr.execute('''select date from account_voucher where move_id =%s''', (move_id,))
        date = self.cr.fetchone()
        return date and date[0] or ''
    
    def get_total(self, cash,type):
        sum = 0.0
        for line in cash:
            if type == 'credit':
                sum += line.credit
            if type == 'debit':
                sum += line.debit
        return sum
    def get_balance(self, get_invoice):
        credit = 0.0
        debit = 0.0
        for line in get_invoice:
            debit += line.debit
            credit += line.credit
        balance = float(debit) - float(credit)
        balance = float(balance)
        return balance
    
    def get_cheque_no(self, move_id):
        sql = '''
            select cheque_number from account_voucher where move_id = %s
        '''%(move_id)
        self.cr.execute(sql)
        p = self.cr.dictfetchone()
        return p and p['cheque_number'] or ''
    
    def get_cheque_date(self, move_id):
        sql = '''
            select cheque_date from account_voucher where move_id = %s
        '''%(move_id)
        self.cr.execute(sql)
        p = self.cr.dictfetchone()
        return p and p['cheque_date'] or ''
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

