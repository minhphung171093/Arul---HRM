# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class tpt_account_balance_report(osv.osv):
    _name = "tpt.account.balance.report"
    
    _columns = {    
        'name': fields.char('', readonly=True),
        'balance_report_line':fields.one2many('tpt.account.balance.report.line','balance_report_id','Balance Report Line'),
        'date_from': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
        'chart_account_id':fields.many2one('account.account','Chart of Account'),
        'fiscalyear_id':fields.many2one('account.fiscalyear','Fiscal Year'),
        'display_account': fields.selection([('all','All'), ('movement','With movements'),
                                            ('not_zero','With balance is not equal to 0'),
                                            ],'Display Accounts'),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves'),
        'filter': fields.selection([('filter_date', 'Date')], "Filter by"),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.account.balance.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trial_balance_report', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.account.balance.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trial_balance_report_pdf', 'datas': datas}
    
tpt_account_balance_report()

class tpt_account_balance_report_line(osv.osv):
    _name = "tpt.account.balance.report.line"
    
    _columns = {    
        'balance_report_id':fields.many2one('tpt.account.balance.report','Balance Report',ondelete='cascade'),
        'code': fields.char('Code', size = 1024),
        'account': fields.char('Account', size = 1024),
        'open_debit': fields.float('Opening Debit'),
        'open_credit': fields.float('Opening Credit'),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
        'close_bal': fields.float('Close'),
    }
    
tpt_account_balance_report_line()

class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    
    _columns = {
        'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
    }
    
    def print_aeroo_report(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'account.common.report'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'trial_balance_report', 'datas': datas}
    
#         def _sum_debit(self, period_id=False, journal_id=False):
#             if journal_id and isinstance(journal_id, int):
#                 journal_id = [journal_id]
#             if period_id and isinstance(period_id, int):
#                 period_id = [period_id]
#             if not (period_id and journal_id):
#                 return 0.0
#             self.cr.execute('SELECT SUM(debit) FROM account_move_line l '
#                             'WHERE period_id IN %s AND journal_id IN %s ' + self.query_get_clause + ' ',
#                             (tuple(period_id), tuple(journal_id)))
#             return self.cr.fetchone()[0] or 0.0
#  
#         def _sum_credit(self, period_id=False, journal_id=False):
#             if journal_id and isinstance(journal_id, int):
#                 journal_id = [journal_id]
#             if period_id and isinstance(period_id, int):
#                 period_id = [period_id]
#             if not journal_id:
#                 journal_id = self.journal_ids
#             if not period_id:
#                 period_id = self.period_ids
#             if not (period_id and journal_id):
#                 return 0.0
#             self.cr.execute('SELECT SUM(credit) FROM account_move_line l '
#                             'WHERE period_id IN %s AND journal_id IN %s '+ self.query_get_clause+'',
#                             (tuple(period_id), tuple(journal_id)))
#             return self.cr.fetchone()[0] or 0.0
        
        def get_account(o):
            acc = o.chart_account_id.id
    #         account_obj = self.pool.get('account.account')
            return acc
        
        def get_account_name(o):
            name = ''
            acc = o.chart_account_id.id
            account_obj = self.pool.get('account.account')
            account_id = account_obj.browse(cr,uid,acc)
            if account_id:
                name = account_id.name + ' ' + account_id.code
            return name
        
        def get_fiscal_year(o):
            fiscal_name = ''
            wizard_data = self.localcontext['data']['form']
            fiscal = o.fiscalyear_id and o.fiscalyear_id.id or False
            if not fiscal:
                raise osv.except_osv(_('Warning!'),_('Need to select Fiscal Year!'))
            fiscal_obj = self.pool.get('account.fiscalyear')
            fiscal_id = fiscal_obj.browse(self.cr,self.uid,fiscal)
            if fiscal_id:
                fiscal_name = fiscal_id.name
            return fiscal_name
        
        def get_display_acc(o):
            display_acc = ''
            display = ''
            display_acc = o.display_account
            if display_acc == 'all':
                display = 'All'
            elif display_acc == 'movement':
                display = 'With Movements'
            elif display_acc == 'not_zero':
                display = 'With balance is not equal to 0'
            return display
        
        def get_target_move(o):
            target_move = ''
            target = ''
            target_move = o.target_move
            if target_move == 'posted':
                target = 'All Posted Entries'
            elif target_move == 'all':
                target = 'All Entries'
            return target
        
        def get_date_from(o):
            date = datetime.strptime(o.date_from, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
        def get_date_to(o):
            date = datetime.strptime(o.date_to, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
        def lines(o,ids,context=None):
            done = {}
            state = ''
            result_acc = []
            def _process_child(accounts, disp_acc, parent, from_date,to_date, state, context=None): #YuVi
                sumdebit = 0
                sumcredit = 0
                open_sumdebit = 0 #Yuvi
                open_sumcredit = 0 #Yuvi
                if context is None:
                    context = {}
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(cr, uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                
    #                 account_obj = self.pool.get('account.account')
                child_ids = self.pool.get('account.account')._get_children_and_consol(cr, uid, [account_rec['id']], context=context)
    #                 strdate =  date[:4] + '-' + date[5:7] + '-' + date[8:10]
                if child_ids:
                    acc_ids = str(child_ids).replace("[","(")
                    acc_ids = str(acc_ids).replace("]",")")
                    
                    sql = ''' 
                        select case when sum(aml.debit)!=0 then sum(aml.debit) else 0 end open_sumdebit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and aml.date < '%s'and am.state in %s 
                    '''%(acc_ids,from_date,state)
                    cr.execute(sql)
    #                 self.cr.execute('''
    #                     select case when sum(debit)!=0 then sum(debit) else 0 end sumdebit 
    #                     from account_move_line where account_id in %s and date < '%s'
    #                         ''',(tuple(child_ids),strdate),)
                    open_sumdebit = cr.fetchone()[0]
                    
                    sql = ''' 
                        select case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end open_sumcredit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and aml.date < '%s'and am.state in %s 
                    '''%(acc_ids,from_date,state)
                    cr.execute(sql)
   
                    open_sumcredit = cr.fetchone()[0]
                    
    #                 self.cr.execute('''
    #                     select case when sum(credit)!=0 then sum(debit) else 0 end sumcredit 
    #                     from account_move_line where account_id in %s and date < '%s'
    #                         ''',(tuple(child_ids),strdate),)
                    sql = ''' 
                         select case when sum(aml.debit)!=0 then sum(aml.debit) else 0 end sumdebit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and aml.date between '%s' and '%s' and am.state in %s 
                    '''%(acc_ids,from_date,to_date,state)
                    cr.execute(sql)
                    sumdebit = cr.fetchone()[0]
                    
                    sql = ''' 
                         select case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end sumcredit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and aml.date between '%s' and '%s' and am.state in %s 
                    '''%(acc_ids,from_date,to_date,state)
                    cr.execute(sql)
                    sumcredit = cr.fetchone()[0]
                    #TPT-Code commented for closing balance                
    #===========================================================================
    #                 
    #                 sql = ''' 
    #                     select case when sum(debit)!=0 then sum(debit) else 0 end sumdebit 
    #                     from account_move_line where account_id in %s and date < '%s' 
    #                         and move_id in (select id from account_move where state in %s) 
    #                 '''%(acc_ids,date,state)
    #                 cr.execute(sql)
    # #                 self.cr.execute('''
    # #                     select case when sum(debit)!=0 then sum(debit) else 0 end sumdebit 
    # #                     from account_move_line where account_id in %s and date < '%s'
    # #                         ''',(tuple(child_ids),strdate),)
    #                 sumdebit = cr.fetchone()[0]
    #                 
    # #                 self.cr.execute('''
    # #                     select case when sum(credit)!=0 then sum(debit) else 0 end sumcredit 
    # #                     from account_move_line where account_id in %s and date < '%s'
    # #                         ''',(tuple(child_ids),strdate),)
    #                 sql = ''' 
    #                     select case when sum(credit)!=0 then sum(debit) else 0 end sumcredit 
    #                     from account_move_line where account_id in %s and date < '%s'
    #                         and move_id in (select id from account_move where state in %s) 
    #                 '''%(acc_ids,date,state)
    #                 cr.execute(sql)
    #                 sumcredit = cr.fetchone()[0]
    #===========================================================================
    
                    
                
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'open_debit': open_sumdebit, # YuVi
                    'open_credit': open_sumcredit, # YuVi
                    'debit': sumdebit,  # YuVi
                    'credit': sumcredit, # YuVi
                    'balance': (open_sumdebit+sumdebit)-(open_sumcredit+sumcredit), # YuVi
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                    'parent_left': account_rec['parent_left'],
                }
#                 self.sum_debit += account_rec['debit']
#                 self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(cr, uid, currency, res['credit']) or not currency_obj.is_zero(cr, uid, currency, res['debit']) or not currency_obj.is_zero(cr, uid, currency, res['balance']):
                        result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(cr, uid, currency, res['balance']):
                        result_acc.append(res)
                else:
                    result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child,from_date,to_date,state,context=context) #YuVi
    
            obj_account = self.pool.get('account.account')
#             if not ids:
#                 ids = self.ids
            if not ids:
                return []
            if not done:
                done={}
                
#             form=self.localcontext['data']['form']
            ctx = context.copy()
    #         ctx = {}
            ctx['target_move'] = o.target_move
            if ctx['target_move'] == 'posted':
                state = '''('posted')'''
            else :
                state = '''('draft','posted')'''
                
            ctx['fiscalyear'] = o.fiscalyear_id.id
    #         if form['filter'] == 'filter_period':
    #             ctx['period_from'] = form['period_from']
    #             ctx['period_to'] = form['period_to']
            if o.filter == 'filter_date':
                ctx['date_from'] = o.date_from
                ctx['date_to'] =  o.date_to
            ctx['state'] = o.target_move
            parents = ids
            child_ids = obj_account._get_children_and_consol(cr, uid, [ids], ctx)
            if child_ids:
                ids = child_ids
            accounts = obj_account.read(cr, uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id','parent_left'], ctx)
    
            for parent in [parents]:
                    if parent in done:
                        continue
                    done[parent] = 1
                    _process_child(accounts,o.display_account,parent,ctx['date_from'],ctx['date_to'],state, ctx)
            return result_acc
    
        cr.execute('delete from tpt_account_balance_report')
        
        def getKey(item):
            return item['parent_left']
        
        balance_obj = self.pool.get('tpt.account.balance.report')
        balance = self.browse(cr, uid, ids[0])
        balance_line = []
        values = lines(balance,get_account(balance),context)
        values = sorted(values, key=getKey)
        for line in values:
            balance_line.append((0,0,{
                'code': line['code'],
                'account': line['name'],
                'open_debit': line['open_debit'],
                'open_credit': line['open_credit'],
                'debit': line['debit'],
                'credit': line['credit'],
                'close_bal': line['balance'],
                
            }))
        vals = {
            'name': 'Trial Balance',
            'date_from': balance.date_from,
            'date_to': balance.date_to,
            'chart_account_id':balance.chart_account_id and balance.chart_account_id.id or False,
            'fiscalyear_id':balance.fiscalyear_id and balance.fiscalyear_id.id or False,
            'display_account': balance.display_account,
            'target_move': balance.target_move,
            'filter': balance.filter,
            'balance_report_line': balance_line,
        }
        balance_id = balance_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'tpt_account_report_balance_form_view')
        return {
                    'name': 'Trial Balance',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.account.balance.report',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': balance_id,
                }
    
    
account_balance_report()