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
            'get_opening_balance':self.get_opening_balance,
            'get_total_debit':self.get_total_debit, #TPT-Y on 23/09/2015
            'get_total_balance':self.get_total_balance, #TPT-Y on 23/09/2015
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
            return "CUSTOMER INVOICE"
        if doc_type == 'cus_pay':
            return "CUSTOMER PAYMENT"
    
    #TPT-Y on 23/09/2015
    def get_total(self,cash):
        sum = 0.0
        for line in cash:
            sum += line.credit
        return sum
        
    #TPT-Y on 23/09/2015
    def get_total_debit(self,get_move_ids, get_opening_balance):
        debit = 0.0
        for move in get_move_ids:
            debit += move['debit']    
        return debit+get_opening_balance
    
    #TPT-Y on 23/09/2015
    def get_total_balance(self,get_move_ids, get_opening_balance):
        debit = 0.0
        credit = 0.0
        balance = 0.0
        for move in get_move_ids:
            debit += move['debit']
            credit += move['credit']      
        balance = (debit+get_opening_balance) - credit
        return balance
        
    #TPT-Y on 23/09/2015   
    def get_opening_balance(self):
            wizard_data = self.localcontext['data']['form']
            date_from = wizard_data['date_from']            
            cus = wizard_data['customer_id']
            is_posted = wizard_data['is_posted']           
            balance = 0.0  
            credit = 0.0
            debit = 0.0
            if is_posted is True:
                sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state='posted'
                    and aml.account_id = (
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s) and name='property_account_receivable'
                    ))  
                    '''%(date_from,cus[0])
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    credit += move['credit']
                    
                sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state='posted' 
                    and aml.account_id = (
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s) and name='property_account_receivable'
                    )) 
                '''%(date_from,cus[0])
                
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    debit += move['debit']    
                balance = debit - credit
            else:
                sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state in ('draft','posted') 
                    and aml.account_id = (
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s) and name='property_account_receivable'
                    ))
                '''%(date_from,cus[0])                
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():  
                    credit += move['credit']
                    
                sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state in ('draft','posted')
                    and aml.account_id = (
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s) and name='property_account_receivable'
                    )) 
                '''%(date_from,cus[0])
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    debit += move['debit']    
                balance = debit - credit
            return balance or 0.00
        
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        cus = wizard_data['customer_id']
        is_posted = wizard_data['is_posted']
        
        acount_move_line_obj = self.pool.get('account.move.line')
        acount_move_obj = self.pool.get('account.move')
        cus_ids = []
        if is_posted is True:
            sql = '''
                select aml.id from account_move_line aml 
                    inner join account_move am on aml.move_id = am.id
                    inner join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date between '%s' and '%s' 
                    and am.state='posted' 
                    and aml.account_id = (
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s) and name='property_account_receivable'
                    )) order by am.date 
                '''%(date_from, date_to,cus[0])
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
        else:
            sql = '''
                select aml.id from account_move_line aml 
                    inner join account_move am on aml.move_id = am.id
                    inner join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date between '%s' and '%s'
                    and am.state in ('draft','posted') 
                    and aml.account_id = (
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s) and name='property_account_receivable'
                    )) order by am.date  
                '''%(date_from, date_to,cus[0])
            self.cr.execute(sql)
            cus_ids = [r[0] for r in self.cr.fetchall()]
#         sql = '''
#             select id from account_move_line 
#             where move_id in (
#                                 select id from account_move 
#                                 where date between '%s' and '%s' and doc_type in ('cus_pay') and partner_id = %s and state='posted' ) and credit is not null and credit !=0   
#             '''%(date_from, date_to,cus[0])
#         self.cr.execute(sql)
#         cus_ids += [r[0] for r in self.cr.fetchall()]
        return acount_move_line_obj.browse(self.cr,self.uid,cus_ids)
    
    def get_bill_no(self, move_id, doc_type):
        if doc_type == 'cus_inv':
            self.cr.execute('''select vvt_number from account_invoice where move_id =%s''', (move_id,))
        else:
             return ''
        number = self.cr.fetchone()
        return number and number[0] or ''
    
    def get_so_no(self, move_id, doc_type):
        number = ''
        if doc_type == 'cus_inv':
            self.cr.execute('''select name from sale_order where id in (select sale_id from account_invoice where move_id =%s)''', (move_id,))
        number = self.cr.fetchone()
        return number and number[0] or ''
    
    def get_so_date(self, move_id, doc_type):
        date = ''
        if doc_type == 'cus_inv':
            self.cr.execute('''select date_order from sale_order where id in (select sale_id from account_invoice where move_id =%s)''', (move_id,))
        date = self.cr.fetchone()
        return date and date[0] or ''
    
    
    def get_bill_date(self, move_id, doc_type):
        if doc_type == 'cus_inv':
            self.cr.execute('''select bill_date from account_invoice where move_id =%s''', (move_id,))
        else:
            self.cr.execute('''select date from account_voucher where move_id =%s''', (move_id,))
        date = self.cr.fetchone()
        return date and date[0] or ''
    
    #===========================================================================
    # def get_total(self, cash,type):
    #     sum = 0.0
    #     for line in cash:
    #         if type == 'credit':
    #             sum += line.credit
    #         if type == 'debit':
    #             sum += line.debit
    #     return sum
    #===========================================================================
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

