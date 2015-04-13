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
from datetime import date
from dateutil.rrule import rrule, DAILY
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
            'get_cash': self.get_cash,
            'convert_date_cash': self.convert_date_cash,
            'get_total_debit': self.get_total_debit,
            'get_total_credit': self.get_total_credit,
            'get_date': self.get_date,
            'get_convert_date': self.get_convert_date,
            'date_range': self.date_range,
            'get_each_date': self.get_each_date,
            'get_total_balance': self.get_total_balance,
            'get_line_balance': self.get_line_balance,
            
        })
    def get_convert_date(self, datetime):
        date_convert =''
        if datetime:
            datetime = str(datetime)
            date = datetime[:10]
        return date
        
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
    
    def get_date(self, date):
        res = {}
#         date = time.strftime('%Y-%m-%d'),
        date_sec = datetime.strptime(date, DATE_FORMAT)
        day = date_sec.day
        month = date_sec.month
        year = date_sec.year
        res = {
               'day': day,
               'month': month,
               'year': year,
               }
        return res
        
    def get_cash(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        type = wizard_data['type_trans']
        account_voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.move.line')
        if type == 'payment':
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'bank'), ('type_trans', '=', 'payment')])
        elif type == 'receipt':
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'bank'), ('type_trans', '=', 'receipt')])
        else:
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'bank')])
        return account_voucher_obj.browse(self.cr,self.uid,account_ids)

    def date_range(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        type = wizard_data['type_trans']
        date_from1 = date(self.get_date(date_from)['year'], self.get_date(date_from)['month'], self.get_date(date_from)['day'])
        date_to1 = date(self.get_date(date_to)['year'], self.get_date(date_to)['month'], self.get_date(date_to)['day'])
        date_arr = []
        account_voucher_obj = self.pool.get('account.voucher')
        for single_date in rrule(DAILY, dtstart=date_from1, until=date_to1):
            if type == 'payment':
                account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '=', self.get_convert_date(single_date)), ('type_cash_bank', '=', 'bank'), ('type_trans', '=', 'payment')])
            elif type == 'receipt':
                account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '=', self.get_convert_date(single_date)), ('type_cash_bank', '=', 'bank'), ('type_trans', '=', 'receipt')])
            else:   
                account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '=', self.get_convert_date(single_date)), ('type_cash_bank', '=', 'bank')])
            if account_ids:
                date_arr.append(self.get_convert_date(single_date))
        return date_arr

    def get_each_date(self, single_date):
        account_voucher_obj = self.pool.get('account.voucher')
        wizard_data = self.localcontext['data']['form']
        type = wizard_data['type_trans']
        account_ids = []
        if type == 'payment':
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '=', single_date), ('type_cash_bank', '=', 'bank'), ('type_trans', '=', 'payment')])
        elif type == 'receipt':
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '=', single_date), ('type_cash_bank', '=', 'bank'), ('type_trans', '=', 'receipt')])
        else:
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '=', single_date), ('type_cash_bank', '=', 'bank')])
        return account_voucher_obj.browse(self.cr,self.uid,account_ids)
           
    def get_line_balance(self, get_each_date):  
        balance = 0.0  
        credit = 0.0
        debit = 0.0
        for voucher in get_each_date:
            for line in voucher.move_ids:
                credit += line.credit
                debit += line.debit
        balance = debit - credit
        return balance
            
    def get_total_debit(self, cash):
        debit = 0.0
        for voucher in cash:
            for line in voucher.move_ids:
                debit += line.debit
        return debit
    
    def get_total_credit(self, cash):
        credit = 0.0
        for voucher in cash:
            for line in voucher.move_ids:
                credit += line.credit
        return credit
    
    def get_total_balance(self, cash):
        debit = 0.0
        credit = 0.0
        balance = 0.0
        for voucher in cash:
            for line in voucher.move_ids:
                credit += line.credit
                debit += line.debit
        balance = debit - credit
        return balance
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

