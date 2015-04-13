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
        
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        cus = wizard_data['customer_id']
        acount_move_line_obj = self.pool.get('account.move.line')
        acount_move_obj = self.pool.get('account.move')
        sql = '''
            select id from account_move_line 
            where move_id in (
                                select id from account_move 
                                where date between '%s' and '%s' and doc_type in ('cus_inv','cus_pay') and partner_id = %s  ) 
            '''%(date_from, date_to,cus[0])
        self.cr.execute(sql)
        cus_ids = [r[0] for r in self.cr.fetchall()]
        return acount_move_line_obj.browse(self.cr,self.uid,cus_ids)
    
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

