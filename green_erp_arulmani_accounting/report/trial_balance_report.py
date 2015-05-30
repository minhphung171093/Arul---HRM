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
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.result_acc = []
        self.localcontext.update({
            'sum_debit':self._sum_debit,
            'sum_credit':self._sum_credit,
            'lines': self.lines,
            'get_account':self.get_account,
            'get_account_name':self.get_account_name,
            'get_fiscal_year':self.get_fiscal_year,
            'get_display_acc':self.get_display_acc,
            'get_target_move':self.get_target_move,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            
        })
        
    def _sum_debit(self, period_id=False, journal_id=False):
        if journal_id and isinstance(journal_id, int):
            journal_id = [journal_id]
        if period_id and isinstance(period_id, int):
            period_id = [period_id]
        if not journal_id:
            journal_id = self.journal_ids
        if not period_id:
            period_id = self.period_ids
        if not (period_id and journal_id):
            return 0.0
        self.cr.execute('SELECT SUM(debit) FROM account_move_line l '
                        'WHERE period_id IN %s AND journal_id IN %s ' + self.query_get_clause + ' ',
                        (tuple(period_id), tuple(journal_id)))
        return self.cr.fetchone()[0] or 0.0
 
    def _sum_credit(self, period_id=False, journal_id=False):
        if journal_id and isinstance(journal_id, int):
            journal_id = [journal_id]
        if period_id and isinstance(period_id, int):
            period_id = [period_id]
        if not journal_id:
            journal_id = self.journal_ids
        if not period_id:
            period_id = self.period_ids
        if not (period_id and journal_id):
            return 0.0
        self.cr.execute('SELECT SUM(credit) FROM account_move_line l '
                        'WHERE period_id IN %s AND journal_id IN %s '+ self.query_get_clause+'',
                        (tuple(period_id), tuple(journal_id)))
        return self.cr.fetchone()[0] or 0.0
    
    def get_account(self):
        wizard_data = self.localcontext['data']['form']
        acc = wizard_data['chart_account_id']
#         account_obj = self.pool.get('account.account')
        return acc[0]
    
    def get_account_name(self):
        name = ''
        wizard_data = self.localcontext['data']['form']
        acc = wizard_data['chart_account_id']
        account_obj = self.pool.get('account.account')
        account_id = account_obj.browse(self.cr,self.uid,acc[0])
        if account_id:
            name = account_id.name + ' ' + account_id.code
        return name
    
    def get_fiscal_year(self):
        fiscal_name = ''
        wizard_data = self.localcontext['data']['form']
        fiscal = wizard_data['fiscalyear_id']
        fiscal_obj = self.pool.get('account.fiscalyear')
        fiscal_id = fiscal_obj.browse(self.cr,self.uid,fiscal[0])
        if fiscal_id:
            fiscal_name = fiscal_id.name
        return fiscal_name
    
    def get_display_acc(self):
        display_acc = ''
        display = ''
        wizard_data = self.localcontext['data']['form']
        display_acc = wizard_data['display_account']
        if display_acc == 'all':
            display = 'All'
        elif display_acc == 'movement':
            display = 'With Movements'
        elif display_acc == 'not_zero':
            display = 'With balance is not equal to 0'
        return display
    
    def get_target_move(self):
        target_move = ''
        target = ''
        wizard_data = self.localcontext['data']['form']
        target_move = wizard_data['target_move']
        if target_move == 'posted':
            target = 'All Posted Entries'
        elif target_move == 'all':
            target = 'All Entries'
        return target
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def lines(self,ids):
        done = {}
        state = ''
        def _process_child(accounts, disp_acc, parent, date, state, context=None):
            sumdebit = 0
            sumcredit = 0
            if context is None:
                context = {}
            account_rec = [acct for acct in accounts if acct['id']==parent][0]
            currency_obj = self.pool.get('res.currency')
            acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
            currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
            
#                 account_obj = self.pool.get('account.account')
            child_ids = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, [account_rec['id']], context=context)
#                 strdate =  date[:4] + '-' + date[5:7] + '-' + date[8:10]
            if child_ids:
                acc_ids = str(child_ids).replace("[","(")
                acc_ids = str(acc_ids).replace("]",")")
                sql = ''' 
                    select case when sum(debit)!=0 then sum(debit) else 0 end sumdebit 
                    from account_move_line where account_id in %s and date < '%s' 
                        and move_id in (select id from account_move where state in %s) 
                '''%(acc_ids,date,state)
                self.cr.execute(sql)
#                 self.cr.execute('''
#                     select case when sum(debit)!=0 then sum(debit) else 0 end sumdebit 
#                     from account_move_line where account_id in %s and date < '%s'
#                         ''',(tuple(child_ids),strdate),)
                sumdebit = self.cr.fetchone()[0]
                
#                 self.cr.execute('''
#                     select case when sum(credit)!=0 then sum(debit) else 0 end sumcredit 
#                     from account_move_line where account_id in %s and date < '%s'
#                         ''',(tuple(child_ids),strdate),)
                sql = ''' 
                    select case when sum(credit)!=0 then sum(debit) else 0 end sumcredit 
                    from account_move_line where account_id in %s and date < '%s'
                        and move_id in (select id from account_move where state in %s) 
                '''%(acc_ids,date,state)
                self.cr.execute(sql)
                sumcredit = self.cr.fetchone()[0]
            
            res = {
                'id': account_rec['id'],
                'type': account_rec['type'],
                'code': account_rec['code'],
                'name': account_rec['name'],
                'level': account_rec['level'],
                'open_debit': sumdebit,
                'open_credit': sumcredit,
                'debit': account_rec['debit'],
                'credit': account_rec['credit'],
                'balance': account_rec['balance'],
                'parent_id': account_rec['parent_id'],
                'bal_type': '',
            }
            self.sum_debit += account_rec['debit']
            self.sum_credit += account_rec['credit']
            if disp_acc == 'movement':
                if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
            elif disp_acc == 'not_zero':
                if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                    self.result_acc.append(res)
            else:
                self.result_acc.append(res)
            if account_rec['child_id']:
                for child in account_rec['child_id']:
                    _process_child(accounts,disp_acc,child,date,state,context=context)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}
            
        form=self.localcontext['data']['form']
        ctx = self.localcontext.copy()
#         ctx = {}
        ctx['target_move'] = form['target_move']
        if ctx['target_move'] == 'posted':
            state = '''('posted')'''
        else :
            state = '''('draft','posted')'''
            
        ctx['fiscalyear'] = form['fiscalyear_id'][0]
#         if form['filter'] == 'filter_period':
#             ctx['period_from'] = form['period_from']
#             ctx['period_to'] = form['period_to']
        if form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, [ids], ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id'], ctx)

        for parent in [parents]:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent,ctx['date_from'], state, ctx)
        return self.result_acc
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

