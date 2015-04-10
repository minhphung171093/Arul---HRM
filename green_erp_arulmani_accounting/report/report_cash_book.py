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
            'get_cash': self.get_cash,
            'convert_date_cash': self.convert_date_cash,
            'get_total': self.get_total,
        })
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
        date = time.strftime('%Y-%m-%d'),
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
        
    def get_cash(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        type = wizard_data['type_trans']
        account_voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.move.line')
        
        if type == 'payment':
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash'), ('type_trans', '=', 'payment')])
        if type == 'receipt':
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash'), ('type_trans', '=', 'receipt')])
        else:
            account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash')])
#             list_line = []
#             for vouc in account_voucher_obj.browse(self.cr,self.uid,account_ids):
#                 for line in vouc.move_ids:
#                     list_line.append(line)
        return account_voucher_obj.browse(self.cr,self.uid,account_ids)
    
    def get_total(self, cash):
        credit = 0.0
        for voucher in cash:
            for line in voucher.move_ids:
                credit += line.credit
        return credit
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

