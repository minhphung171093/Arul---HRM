# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

#TPT-Y 05Nov2015
#===============================================================================
# class account_balance_report(osv.osv_memory):
#      _inherit = "account.balance.report"
#      _columns = {
#              'display_account': fields.selection([('all','All'),
#                                  ('movement','All without zero balance'),
#                                  ],'Display Accounts'),
#             'tb_type': fields.selection([('tb', 'Trial Balance'),
#                                      ('customer_tb', 'Customer Trial Balance'),
#                                      ('supplier_tb', 'Supplier Trial Balance'),
#                                         ], 'Type'),
#              }
#      _defaults = {
#              'display_account':'all'
#              }
# account_balance_report()
#===============================================================================


class tpt_account_balance_report(osv.osv_memory):
    _name = "tpt.account.balance.report"
    
    _columns = {    
        'name': fields.char('', readonly=True),
        'balance_report_line':fields.one2many('tpt.account.balance.report.line','balance_report_id','Balance Report Line'),
        'date_from': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
        'chart_account_id':fields.many2one('account.account','Chart of Account'),
        'fiscalyear_id':fields.many2one('account.fiscalyear','Fiscal Year'),
        #=======================================================================
        # 'display_account': fields.selection([('all','All'), ('movement','With movements'),
        #                                     ('not_zero','With balance is not equal to 0'),
        #                                     ],'Display Accounts'),
        #=======================================================================
                
         #======================================================================
         # 'display_account': fields.selection([('all','All'),
         #                                      ('movement','All without zero balance'),
         #                                      ],'Display Accounts'), #TPT-Y on 05Nov2015
         #======================================================================
         'display_account': fields.selection([('all','All')
                                              ,('movement','With movements'),
                                               ('not_zero','With balance is not equal to 0'),
                                               ],'Display Accounts'), #TPT-Y on 05Nov2015
        
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves'),
        'filter': fields.selection([('filter_date', 'Date')], "Filter by"),
        
        'tb_type': fields.selection([('tb', 'Trial Balance'),
                                     ('customer_tb', 'Customer Trial Balance'),
                                     ('supplier_tb', 'Supplier Trial Balance'),
                                        ], 'Type'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.account.balance.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_ids':ids})
#         datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trial_balance_report', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'tpt.account.balance.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trial_balance_report_pdf', 'datas': datas}
    
tpt_account_balance_report()

class tpt_account_balance_report_line(osv.osv_memory):
    _name = "tpt.account.balance.report.line"
    
    _columns = {    
        'balance_report_id':fields.many2one('tpt.account.balance.report','Balance Report',ondelete='cascade'),
        'code': fields.char('Code', size = 1024),
        'account': fields.char('Account', size = 1024),
        'open_debit': fields.float('Opening Debit'),
        'open_credit': fields.float('Opening Credit'),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
        'close_bal': fields.float('Close'), #TPT-Y on 05Nov2015
        'close_debit': fields.float('Closing Debit'), #TPT-Y Commented on 05Nov2015 # TPT-BM-Enable ON 06/05/2016
        'close_credit': fields.float('Closing Credit'), #TPT-Y Commented on 05Nov2015 # TPT-BM-Enable ON 06/05/2016
    }
    
tpt_account_balance_report_line()

class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    
    _columns = {
        'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
        'tb_type': fields.selection([#('tb', 'Trial Balance'),
                                     ('customer_tb', 'Customer Trial Balance'),
                                     ('supplier_tb', 'Vendor Trial Balance'),
                                        ], 'Type'), 
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                        ], 'Target Moves', required=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),
    }
    _defaults = {
                'filter': 'filter_date'
                }
    def onchange_fiscalyear_id(self, cr, uid, ids,fiscalyear_id=False, context=None): 
        fiscal_obj = self.pool.get('account.fiscalyear')  
        for fiscal_date in fiscal_obj.browse(cr, uid, [fiscalyear_id], context):
             date_start = fiscal_date.date_start
             date_stop  = fiscal_date.date_stop
        return {'value': {'date_from': date_start,  'date_to': date_stop,}}  
    
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
        
        
        #TPT-Y on 05Nov2015
        #=======================================================================
        # def get_total(cash,type):
        #     sum = 0.00
        #     for line in cash:
        #         if type == 'open_debit':
        #             sum += line['open_debit']
        #         if type == 'open_credit':
        #             sum += line['open_credit']
        #         if type == 'debit':
        #             sum += line['debit']
        #         if type == 'credit':
        #             sum += line['credit']
        #         #===============================================================
        #         # if type == 'close_bal':
        #         #     sum += line['close_bal']
        #         # if type == 'close_debit':
        #         #     sum += line['balance_debit']
        #         # if type == 'close_credit':
        #         #     sum += line['balance_credit']
        #         #===============================================================
        #     return round(sum,2) or 0.00
        # 
        #=======================================================================
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
        def get_total_od(invoice):
            sum = 0.00        
            for line in invoice:
                if line['open_debit']:                                                                       
                    sum += line['open_debit']   
            return sum or 0.00
        def get_total_oc(invoice):
            sum = 0.00        
            for line in invoice:
                if line['open_credit']:                                                                       
                    sum += line['open_credit']   
            return sum or 0.00
        def get_total_d(invoice):
            sum = 0.00        
            for line in invoice:
                if line['debit']:                                                                       
                    sum += line['debit']   
            return sum or 0.00
        def get_total_c(invoice):
            sum = 0.00        
            for line in invoice:
                if line['credit']:                                                                       
                    sum += line['credit']   
            return sum or 0.00
        def get_total_cd(invoice):
            sum = 0.00        
            for line in invoice:
                if line['balance_debit']:                                                                       
                    sum += line['balance_debit']   
            return sum or 0.00
        def get_total_cc(invoice):
            sum = 0.00        
            for line in invoice:
                if line['balance_credit']:                                                                       
                    sum += line['balance_credit']   
            return sum or 0.00
        def get_total_tot(invoice):
            sum = 0.00        
            for line in invoice:
                if line['balance']:                                                                       
                    sum += line['balance']   
            return sum or 0.00
        def get_total(invoice):
            sum = 0.00        
            for line in invoice:
                if line['open_debit']:                                                                       
                    sum += line['open_debit']   
                if line['open_credit']:                                                                       
                    sum += line['open_credit']   
                if line['balance_debit']:                                                                       
                    sum += line['balance_debit']   
                if line['balance_credit']:                                                                       
                    sum += line['balance_credit']   
                if line['balance']:                                                                       
                    sum += line['balance']   
            return sum or 0.00
        def lines(o,ids,vendor_child_ids,context=None):
            done = {}
            state = ''
            result_acc = []
            res = []
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
                child_ids = self.pool.get('account.account')._get_children_and_consol(cr, uid, [account_rec['id']], context=context)
                
                #TPT-BalamuruganPurushothaman-ON 11/05/2016-FOR CUSTOMER/VENDOR TRIAL BALANCE
                # this snippet will remove the given ids from the overall child_ids
                if o.tb_type:
                    child_ids = [x for x in child_ids if x not in vendor_child_ids]
                ##TPT-END
                #TPT-BM-ON 14/07/2016 - 3619, 3622 - changed to compare as account_move date instead of account_move_line date column
                if child_ids:
                    acc_ids = str(child_ids).replace("[","(")
                    acc_ids = str(acc_ids).replace("]",")")
                    
                    sql = ''' 
                        select case when sum(aml.debit)!=0 then sum(aml.debit) else 0 end open_sumdebit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and am.date < '%s'and am.state in %s 
                    '''%(acc_ids,from_date,state)
                    cr.execute(sql)
                    open_sumdebit = cr.fetchone()[0]
                    
                    sql = ''' 
                        select case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end open_sumcredit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and am.date < '%s'and am.state in %s 
                    '''%(acc_ids,from_date,state)
                    cr.execute(sql)
                    open_sumcredit = cr.fetchone()[0]
                    
                    sql = ''' 
                         select case when sum(aml.debit)!=0 then sum(aml.debit) else 0 end sumdebit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and am.date between '%s' and '%s' and am.state in %s 
                    '''%(acc_ids,from_date,to_date,state)
                    cr.execute(sql)
                    sumdebit = cr.fetchone()[0]
                    
                    sql = ''' 
                         select case when sum(aml.credit)!=0 then sum(aml.credit) else 0 end sumcredit
                        from account_move_line aml
                        join account_move am on (am.id=aml.move_id)
                        where aml.account_id in %s and am.date between '%s' and '%s' and am.state in %s 
                    '''%(acc_ids,from_date,to_date,state)
                    cr.execute(sql)
                    sumcredit = cr.fetchone()[0]
                    #print sql
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
                
                #TPT-START : BalamuruganPurushothaman - ON 05/05/2016 - FOR TRIAL BALANCE REPORT HIERARCHY FIX
                code = account_rec['code']
                name = account_rec['name']   
                if len(account_rec['code'])==2:
                    code = '  '+account_rec['code']
                    name = '  '+account_rec['name']
                if len(account_rec['code'])==3:
                    code = '    '+account_rec['code']
                    name = '    '+account_rec['name']
                if len(account_rec['code'])==4:
                    code = '      '+account_rec['code']
                    name = '      '+account_rec['name']
                if len(account_rec['code'])==5:
                    code = '        '+account_rec['code']
                    name = '        '+account_rec['name']
                if len(account_rec['code'])==10:
                    code = '          '+account_rec['code']
                    name = '          '+account_rec['name']
                #TPT END
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': code, #account_rec['code'],#TPT BM
                    'name': name, #account_rec['name'],#TPT BM
                    'level': account_rec['level'],
                    'open_debit': open_sumdebit, # YuVi
                    'open_credit': open_sumcredit, # YuVi
                    'debit': sumdebit,  # YuVi
                    'credit': sumcredit, # YuVi
                    'balance': (open_sumdebit+sumdebit)-(open_sumcredit+sumcredit), # YuVi
                     #TPT-Y on 05Nov2015
                    'balance_debit': (open_sumdebit+sumdebit), #TPT-Y Commented on 05Nov2015 #TPT BM - Enabled ON 06/05/2016
                    'balance_credit': (open_sumcredit+sumcredit), #TPT-Y Commented on 05Nov2015 #TPT BM - Enabled ON 06/05/2016   
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                    'parent_left': account_rec['parent_left'],
                }
                
#                 self.sum_debit += account_rec['debit']
#                 self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                      if not currency_obj.is_zero(cr, uid, currency, res['credit']) or not currency_obj.is_zero(cr, uid, currency, res['debit']) or not currency_obj.is_zero(cr, uid, currency, res['balance']):
                      #if not currency_obj.is_zero(cr, uid, currency, res['credit']) or not currency_obj.is_zero(cr, uid, currency, res['debit']) or not currency_obj.is_zero(cr, uid, currency, res['balance_debit']) or not currency_obj.is_zero(cr, uid, currency, res['balance_credit']):
                        result_acc.append(res)
                elif disp_acc == 'not_zero':
                     #if not currency_obj.is_zero(cr, uid, currency, res['balance']): #TPT-Y on 05Nov2015
                     if not currency_obj.is_zero(cr, uid, currency, res['balance_debit']) or not currency_obj.is_zero(cr, uid, currency, res['balance_credit']): #TPT-Y on 05Nov2015
                        result_acc.append(res)
                #elif disp_acc == 'all':
                else:
                    result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        #_process_child(accounts,disp_acc,child,from_date,to_date,state,context=context) #TPT-Y on 05Nov2015
                        _process_child(accounts,disp_acc,child,from_date,to_date,state,context=context) #TPT-Y on 05Nov2015
    
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
            ctx['type'] = 'receivable'
            parents = ids
            child_ids = obj_account._get_children_and_consol(cr, uid, [ids], ctx)
            if child_ids:
                ids = child_ids
            #accounts = obj_account.read(cr, uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id','parent_left'], ctx)
            accounts = obj_account.read(cr, uid, ids, ['type','code','name','debit','credit','balance_debit','balance_credit','parent_id','level','child_id','parent_left'], ctx) #TPT-Y on 05Nov2015
    
            for parent in [parents]:
                    if parent in done:
                        continue
                    done[parent] = 1
                    _process_child(accounts,o.display_account,parent,ctx['date_from'],ctx['date_to'],state, ctx)
            return result_acc
        ##Report Start
        cr.execute('delete from tpt_account_balance_report')
        
        def getKey(item):
            return item['parent_left']
        
        balance_obj = self.pool.get('tpt.account.balance.report')
        balance = self.browse(cr, uid, ids[0])
        balance_line = []
        vals = []
        ##TPT-BM-11/05/2016 - FOR CUSTOMER/VENDOR TRIAL BALANCE REPORT
        vendor_child_ids = []
        name = 'Trial Balance'
        if balance.tb_type:
            if balance.tb_type=='customer_tb':
                sql = '''
                select aa.id from account_account aa
                inner join res_partner rs on right(aa.code,10)=rs.vendor_code
                union     
                select id from account_account where type='other'
                union
                select 3578 id
                '''
                cr.execute(sql)
                acc_ids =  cr.dictfetchall()  
                name = 'Customer Trial Balance'
            if balance.tb_type=='supplier_tb':
                sql = '''
                select aa.id from account_account aa
                inner join res_partner rs on right(aa.code,6)=rs.customer_code
                union     
                select id from account_account where type='other'
                union
                select 3578 id
                '''
                cr.execute(sql)
                acc_ids =  cr.dictfetchall()  
                name = 'Vendor Trial Balance'      
            for ids in acc_ids:
                vendor_child_ids.append(ids['id'])
            
        ##
        values = lines(balance,get_account(balance), vendor_child_ids,context) #TPT-BM-11/05/2016- vendor_child_ids AS NEW PARAM
        values = sorted(values, key=getKey)
               
        for line in values:
            #if  line['id']  not in  vendor_child_ids:
            balance_line.append((0,0,{
                'code': line['code'],
                'account': line['name'],
                'open_debit': line['open_debit'],
                'open_credit': line['open_credit'],
                'debit': line['debit'],
                'credit': line['credit'],
                'close_bal': line['balance'],
                'close_debit': line['balance_debit'], #TPT-Y Commented on 05Nov2015 # TPT-BM-Enabled ON 06/05/2016
                'close_credit': line['balance_credit'], #TPT-Y Commented on 05Nov2015 # TPT-BM-Enabled ON 06/05/2016                
            }))
#             balance_line.append((0,0,{
#                 'open_debit': get_total(lines(balance,get_account(balance),context),'open_debit'),
#                 'open_credit': get_total(lines(balance,get_account(balance),context),'open_credit'),
#                 'debit': get_total(lines(balance,get_account(balance),context),'debit'),
#                 'credit': get_total(lines(balance,get_account(balance),context),'credit'),
#                 #'close_bal': get_total(lines(balance,get_account(balance),context),'close_bal'), #TPT-Y on 22/09/2015
#                 #'close_debit': get_total(lines(balance,get_account(balance),context),'close_debit'), #TPT-Y on 22/09/2015
#                 #'close_credit': get_total(lines(balance,get_account(balance),context),'close_credit'), #TPT-Y on 22/09/2015
#                 }))
        #=======================================================================
        # balance_line.append((0,0,{
        #                 #'account' : 'Total',                  
        #                 'open_debit': get_total_od(values) or 0.00,    
        #                 'open_credit': get_total_oc(values) or 0.00, 
        #                 'debit': get_total_d(values) or 0.00,    
        #                 'credit': get_total_c(values) or 0.00, 
        #                 'close_debit': get_total_cd(values) or 0.00, 
        #                 'close_credit': get_total_cc(values) or 0.00, 
        #                 'close_bal': get_total_tot(values) or 0.00,  
        #                  }))
        #=======================================================================

        vals = {
                'name': name or '',
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
                    'name': name or '',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.account.balance.report',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': balance_id,
                }
    
    
account_balance_report()