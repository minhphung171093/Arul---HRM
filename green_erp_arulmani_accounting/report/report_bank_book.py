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
            'get_opening_balance': self.get_opening_balance,
            'get_line_balance': self.get_line_balance,
            'get_ids': self.get_ids,
            'get_do_no': self.get_do_no,
            'get_move_ids': self.get_move_ids,
            'get_account_master_code': self.get_account_master_code,
            'get_account_master_name': self.get_account_master_name,
            'get_code_account': self.get_code_account,
#             'get_account_name': self.get_account_name,
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
        if date:
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
    
    def get_ids(self, single_date):
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
        return account_ids
    
    def get_line_balance(self, seq):  
        move = self.get_move_ids()
        opening_balance = self.get_opening_balance()
        balance = 0.0
        for i in range(0, seq+1):
            balance += (move[i]['credit'] - move[i]['debit'])
        return opening_balance + balance
    
    def get_account_master_name(self):  
        sql = '''
            SELECT name FROM account_account
                WHERE name LIKE '%FEDERAL BANK - TTN%'
        '''
        self.cr.execute(sql)
        name = self.cr.dictfetchone()
        return name and name['name'] or ''
    
    def get_account_master_code(self):  
        sql = '''
            SELECT code FROM account_account
                WHERE code LIKE '%0000111001%'
        '''
        self.cr.execute(sql)
        code = self.cr.dictfetchone()
        return code and code['code'] or ''
    
    def get_opening_balance(self):  
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        type = wizard_data['type_trans']
        balance = 0.0  
        credit = 0.0
        debit = 0.0
        sql = '''
            select sum(aml.credit) as credit, aml.date from account_move_line aml 
            where aml.credit is not null and aml.credit != 0 and aml.date < '%s' 
            and move_id in (select move_id from account_voucher where state = 'posted' and (type_trans = 'payment' or type = 'payment') and (type_cash_bank = 'bank' or journal_id in (select id from account_journal where type = 'bank'))) 
            group by aml.date
        '''%(date_from)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
            credit += move['credit']
            
        sql = '''
            select sum(aml.debit) as debit, aml.date from account_move_line aml 
            where aml.debit is not null and aml.debit != 0 and aml.date < '%s' 
            and move_id in (select move_id from account_voucher where state = 'posted' and (type_trans = 'receipt' or type = 'receipt') and (type_cash_bank = 'bank' or journal_id in (select id from account_journal where type = 'bank'))) 
            group by aml.date
        '''%(date_from)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
            debit += move['debit']    
        balance = debit - credit
        return balance
    
    def get_do_no(self, account_id):
        account_voucher_obj = self.pool.get('account.voucher')
        voucher = account_voucher_obj.browse(self.cr,self.uid,account_id)
        return voucher.name
    
    def get_move_ids(self):
        account_voucher_obj = self.pool.get('account.voucher')
        move_lines = []
        date_arr = []
        wizard_data = self.localcontext['data']['form']
        type = wizard_data['type_trans']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        if type == 'payment':
            sql = '''
                    select id from account_voucher where date between '%s' and '%s' and type = 'payment' and journal_id in (select id from account_journal where type = 'bank') and state = 'posted'
                    union
                    select id from account_voucher where date between '%s' and '%s' and type_cash_bank = 'bank' and type_trans = 'payment' and state = 'posted'
                '''%(date_from, date_to, date_from, date_to)
            self.cr.execute(sql)
            account_ids = [row[0] for row in self.cr.fetchall()]
            if account_ids:
                self.cr.execute('''
                    select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, sum(aml.credit) as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s) and debit is not null and debit !=0 and aa.id = aml.account_id group by av.name,aa.name, aml.account_id,av.date, aml.ref order by av.date
                ''',(tuple(account_ids),))
                return self.cr.dictfetchall()
            else:
                return []
        elif type == 'receipt':
            sql = '''
                    select id from account_voucher where date between '%s' and '%s' and type = 'receipt' and journal_id in (select id from account_journal where type = 'bank') and state = 'posted'
                    union
                    select id from account_voucher where date between '%s' and '%s' and type_cash_bank = 'bank' and type_trans = 'receipt' and state = 'posted'
                '''%(date_from, date_to, date_from, date_to)
            self.cr.execute(sql)
            account_ids = [row[0] for row in self.cr.fetchall()]
            if account_ids:
                self.cr.execute('''
                    select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, sum(aml.credit) as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s) and credit is not null and credit !=0 and aa.id = aml.account_id group by av.name,aa.name, aml.account_id,av.date, aml.ref order by av.date
                ''',(tuple(account_ids),))
                return self.cr.dictfetchall()
            else:
                return []
        else:
            sql = '''
                    select id from account_voucher where date between '%s' and '%s' and journal_id in (select id from account_journal where type = 'bank') and state = 'posted'
                    union
                    select id from account_voucher where date between '%s' and '%s' and type_cash_bank = 'bank' and state = 'posted'
                '''%(date_from, date_to, date_from, date_to)
            self.cr.execute(sql)
            account_ids = [row[0] for row in self.cr.fetchall()]
            if account_ids:
                self.cr.execute('''
                    select foo.acc_name, foo.account_id, sum(foo.debit) as debit, sum(foo.credit) as credit,foo.voucher_name,foo.voucher_date, foo.ref from
                        (select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date , aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s and (type_trans = 'payment' or type = 'payment')) and aml.debit is not null and aml.debit !=0 and aa.id = aml.account_id
                        union all
                        select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s and (type_trans = 'receipt' or type = 'receipt')) and aml.credit is not null and aml.credit !=0 and aa.id = aml.account_id
                        )foo
                        group by foo.acc_name, foo.account_id, foo.voucher_name,foo.voucher_date, foo.ref order by foo.voucher_date
                ''',(tuple(account_ids),tuple(account_ids),))
                return self.cr.dictfetchall()
            else:
                return []
            
    def get_code_account(self, code_id):
        code = ''
        if code_id:
            account = self.pool.get('account.account').browse(self.cr,self.uid,code_id)
            code = account.code
        return code 
        
    def get_total_debit(self, get_move_ids, get_opening_balance):
        debit = 0.0
        for move in get_move_ids:
            debit += move['credit']    
        return debit+get_opening_balance
    
    def get_total_credit(self, get_move_ids):
        credit = 0.0
        for move in get_move_ids:
            credit += move['debit']    
        return credit
    
    def get_total_balance(self, get_move_ids, get_opening_balance):
        debit = 0.0
        credit = 0.0
        balance = 0.0
        for move in get_move_ids:
            debit += move['credit']
            credit += move['debit']      
        balance = (debit+get_opening_balance) - credit
        return balance
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

