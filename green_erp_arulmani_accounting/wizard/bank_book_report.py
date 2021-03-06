# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_bank_book(osv.osv):
    _name = "tpt.bank.book"
    _columns = {
        'name': fields.char('SI.No', readonly=True),
        'bank_acc_no': fields.char('SI.No', readonly=True),
        'cb_line': fields.one2many('tpt.bank.book.line', 'cb_id', 'Bank Book Line'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type'),
        'type_recon':fields.selection([('unreconcile', 'UnReconcile'),('reconcile', 'Reconcile'),('confirmed', 'Confirmed')],'Reconcile type'),#TPT-Y
        'account_id':fields.many2one('account.account','Bank GL Account'),
        'is_posted': fields.boolean('Is Posted'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.bank.book'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_bank_book_xls', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.bank.book'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_bank_book', 'datas': datas}
    
tpt_bank_book()

class tpt_bank_book_line(osv.osv):
    _name = "tpt.bank.book.line"
    _columns = {
        'cb_id': fields.many2one('tpt.bank.book', 'Bank Book', ondelete='cascade'),
        'voucher_id': fields.char('GL Doc No', size = 1024),
        'opening_balance': fields.char('', size = 1024),
        'debit': fields.float('Debit (Rs.)'),
        'crebit': fields.float('Credit (Rs.)'),
        'balance': fields.float('Balance (Rs.)'),
        'date': fields.date('Date'),
        'desc': fields.char('GL Name', size = 1024),
        'gl_code': fields.char('GL Code', size = 1024),
        'ref': fields.char('Reference', size = 1024),
        'gl_doc_no': fields.char('Transaction No.', size = 1024),
        'voucher_desc': fields.char('Description', size = 1024),
        'cheque_no': fields.char('Cheque No.', size = 1024),
        'cheque_date': fields.char('Cheque Date', size = 1024),
        'move_id':fields.many2one('account.move','Document No'),
    }

tpt_bank_book_line()

class bank_book_report(osv.osv_memory):
    _name = "bank.book.report"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type'),
                'type_recon':fields.selection([('unreconcile', 'UnReconcile'),('reconcile', 'Reconcile'),('confirmed', 'Confirmed')],'Reconcile type'),#TPT-Y
                'account_id':fields.many2one('account.account','Bank GL Account'),
                'is_posted': fields.boolean('Is Posted'),
                }
    
    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def print_report(self, cr, uid, ids, context=None):
        
        def get_line_balance(seq,o):  
            move = get_move_ids(o)
            opening_balance = get_opening_balance(o)
            balance = 0.0
            for i in range(0, seq+1):
                balance += (move[i]['credit'] - move[i]['debit'])
            return opening_balance + balance
        
        def get_account_master_name(bank_id):  
            if bank_id:
                sql = '''
                SELECT name FROM account_account
                    WHERE id=%s
                '''%(bank_id.id)
                cr.execute(sql)
                name = cr.dictfetchone()
                return name and name['name'] or ''
            else:
                return ''
        
        def get_account_master_code(bank_id):  
            if bank_id:
                sql = '''
                SELECT code FROM account_account
                    WHERE id=%s
                '''%(bank_id.id)
                cr.execute(sql)
                code = cr.dictfetchone()
                return code and code['code'] or ''
            else:
                return ''
        
        def get_opening_balance(o):  
            date_from = o.date_from
            date_to = o.date_to
            type = o.type_trans
            is_posted = o.is_posted
            account_id = o.account_id
            balance = 0.0  
            credit = 0.0
            debit = 0.0
            if is_posted is True:
                sql = '''
                    select sum(aml.credit) as credit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where aml.credit>0 and av.state in ('posted') and av.date < '%s'
                '''%(account_id.id,date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    if move['credit']:
                        credit += move['credit']
                    
                sql = '''
                    select sum(aml.debit) as debit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where aml.debit>0 and av.state in ('posted') and av.date < '%s'
                '''%(account_id.id,date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    if move['debit']:
                        debit += move['debit']    
                balance = debit - credit
            else:
                sql = '''
                    select sum(aml.credit) as credit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where aml.credit>0 and av.state in ('draft','posted') and av.date < '%s'
                '''%(account_id.id,date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    if move['credit']:
                        credit += move['credit']
                    
                sql = '''
                    select sum(aml.debit) as debit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where aml.debit>0 and av.state in ('draft','posted') and av.date < '%s'
                '''%(account_id.id,date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    if move['debit']:
                        debit += move['debit']    
                balance = debit - credit
            return balance
        
        def get_move_ids(o):
            account_voucher_obj = self.pool.get('account.voucher')
            move_lines = []
            date_arr = []
            date_from = o.date_from
            date_to = o.date_to
            type = o.type_trans
            rec_type = o.type_recon
            account_id = o.account_id
            is_posted = o.is_posted
            
            #TPT-Y
            sql = '''
                    select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                    av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
                    av.cheque_no cheque_no_1,
                    case when av.cheque_no is null then av.cheque_number
                    else av.cheque_no end as cheque_no,
                    av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc,av.payee as payee, am.id as move_id
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    inner join account_voucher av on av.move_id = aml.move_id
                    inner join (
                    select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
                    )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                    where av.date between '%s' and '%s'
                '''%(account_id.id,date_from, date_to)
            if type:
                qstr = " and av.type = '%s'"%(type)
                sql = sql+qstr
            if rec_type:
                qstr = " and av.status in ('%s')"%(rec_type)
                sql = sql+qstr
            if is_posted:
                qstr = " and av.state in ('posted')"
                sql = sql+qstr
            else:
                qstr = " and av.state in ('draft','posted')"
                sql = sql+qstr
            sql=sql+" group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date, av.number,av.narration,av.cheque_number, am.id  order by av.date,av.cheque_no,av.cheque_number "
            
            cr.execute(sql)
            return cr.dictfetchall()
            
            #===================================================================
            # if is_posted is True:
            #         if type == 'payment':
            #                 cr.execute('''
            #                     select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
            #                     av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
            #                     av.cheque_no cheque_no_1,
            #                     case when av.cheque_no is null then av.cheque_number
            #                     else av.cheque_no end as cheque_no,
            #                     av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc
            #                     from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account aa on (aa.id=aml.account_id)
            #                     inner join account_voucher av on av.move_id = aml.move_id
            #                     inner join (
            #                     select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
            #                     )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
            #                     where av.type in ('payment') and av.state in ('posted') and av.date between %s and %s 
            #                     group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date,
            #                     av.number,av.narration,av.cheque_number
            #                     order by av.date,av.cheque_no,av.cheque_number
            #                 ''',(account_id.id,date_from, date_to,))
            #                 return cr.dictfetchall()
            #         elif type == 'receipt':
            #                 cr.execute('''
            #                     select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
            #                     av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
            #                     av.cheque_no cheque_no_1,
            #                     case when av.cheque_no is null then av.cheque_number
            #                     else av.cheque_no end as cheque_no,
            #                     av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc
            #                     from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account aa on (aa.id=aml.account_id)
            #                     inner join account_voucher av on av.move_id = aml.move_id
            #                     inner join (
            #                     select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
            #                     )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
            #                     where av.type in ('receipt') and av.state in ('posted') and av.date between %s and %s  
            #                     group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date,
            #                     av.number,av.narration,av.cheque_number
            #                     order by av.date,av.cheque_no,av.cheque_number
            #                 
            #                 ''',(account_id.id,date_from, date_to,))
            #                 return cr.dictfetchall()
            #         else:
            #                 cr.execute('''
            #                     select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
            #                     av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
            #                     av.cheque_no cheque_no_1,
            #                     case when av.cheque_no is null then av.cheque_number
            #                     else av.cheque_no end as cheque_no,
            #                     av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc
            #                     from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account aa on (aa.id=aml.account_id)
            #                     inner join account_voucher av on av.move_id = aml.move_id
            #                     inner join (
            #                     select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
            #                     )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
            #                     where av.type in ('payment','receipt') and av.state in ('posted') and av.date between %s and %s 
            #                     group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date,
            #                     av.number,av.narration,av.cheque_number
            #                     order by av.date,av.cheque_no,av.cheque_number
            #                 ''',(account_id.id,date_from, date_to,))
            #                 return cr.dictfetchall()
            #  
            # else: #MAJOR IF ELSE
            #         if type == 'payment':
            #                 cr.execute('''
            #                     select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
            #                     av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
            #                     av.cheque_no cheque_no_1,
            #                     case when av.cheque_no is null then av.cheque_number
            #                     else av.cheque_no end as cheque_no, 
            #                     av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc
            #                     from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account aa on (aa.id=aml.account_id)
            #                     inner join account_voucher av on av.move_id = aml.move_id
            #                     inner join (
            #                     select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
            #                     )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
            #                     where av.type in ('payment') and av.state in ('draft','posted') and av.date between %s and %s  
            #                     group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date,
            #                     av.number,av.narration,av.cheque_number
            #                     order by av.date,av.cheque_no,av.cheque_number
            #                 ''',(account_id.id,date_from, date_to,))
            #                 return cr.dictfetchall()
            #         elif type == 'receipt':
            #                 cr.execute('''
            #                     select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
            #                     av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
            #                     av.cheque_no cheque_no_1,
            #                     case when av.cheque_no is null then av.cheque_number
            #                     else av.cheque_no end as cheque_no, 
            #                     av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc
            #                     from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account aa on (aa.id=aml.account_id)
            #                     inner join account_voucher av on av.move_id = aml.move_id
            #                     inner join (
            #                     select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
            #                     )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
            #                     where av.type in ('receipt') and av.state in ('draft','posted') and av.date between %s and %s  
            #                     group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date,
            #                     av.number,av.narration,av.cheque_number
            #                     order by av.date,av.cheque_no,av.cheque_number
            #                 ''',(account_id.id,date_from, date_to,))
            #                 return cr.dictfetchall()
            #         else:
            #                 cr.execute('''
            #                     select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
            #                     av.name as voucher_name,av.date as voucher_date,aml.ref as ref, aml.name as voucher_desc,
            #                     av.cheque_no cheque_no_1,
            #                     case when av.cheque_no is null then av.cheque_number
            #                     else av.cheque_no end as cheque_no,                 
            #                     av.cheque_date cheque_date,av.number as voucher_no,av.narration as desc
            #                     from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account aa on (aa.id=aml.account_id)
            #                     inner join account_voucher av on av.move_id = aml.move_id
            #                     inner join (
            #                     select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
            #                     inner join account_move am on (am.id=aml.move_id)
            #                     inner join account_account acc on (acc.id=aml.account_id and acc.id=%s)
            #                     )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
            #                     where av.type in ('receipt','payment') and av.state in ('draft','posted') and av.date between %s and %s  
            #                     group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name,av.cheque_no, av.cheque_date,
            #                     av.number,av.narration,av.cheque_number
            #                     order by av.date,av.cheque_no,av.cheque_number
            #                 ''',(account_id.id,date_from, date_to,))
            #                 return cr.dictfetchall()
            #===================================================================
                        
                        
        def get_code_account(code_id):
            code = ''
            if code_id:
                account = self.pool.get('account.account').browse(cr,uid,code_id)
                code = account.code
            return code 
            
        def get_total_debit(get_move_ids, get_opening_balance):
            debit = 0.0
            for move in get_move_ids:
                debit += move['credit']    
            return debit+get_opening_balance
        
        def get_total_credit(get_move_ids):
            credit = 0.0
            for move in get_move_ids:
                credit += move['debit']    
            return credit
        
        def get_total_balance(get_move_ids, get_opening_balance):
            debit = 0.0
            credit = 0.0
            balance = 0.0
            for move in get_move_ids:
                debit += move['credit']
                credit += move['debit']      
            balance = (debit+get_opening_balance) - credit
            return balance
        
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'cash.book.report'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'report_cash_book', 'datas': datas}
        cr.execute('delete from tpt_bank_book')
        cb_obj = self.pool.get('tpt.bank.book')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        cb_line.append((0,0,{
            'voucher_id': False,
            'opening_balance': 'Opening Balance:',
            'debit': get_opening_balance(cb),

        }))
        for seq, line in enumerate(get_move_ids(cb)):
            cb_line.append((0,0,{
                'voucher_id': line['voucher_name'], #TPT-Y on 03Sept2015
                'opening_balance': False,
                'debit': line['credit'] and line['credit'] or 0,
                'crebit': line['debit'] and line['debit'] or 0,
                'balance': get_line_balance(seq,cb),
                'date': line['voucher_date'],
                'desc': line['acc_name'],
                'gl_doc_no': line['voucher_no'], #TPT-Y
                'gl_code': get_code_account(line['account_id']),
                'ref': line['ref'], 
                'voucher_desc': line['desc'],  
                'cheque_no': line['cheque_no'],
                'cheque_date': line['cheque_date'],
                'move_id': line['move_id'] or False,
            }))
        cb_line.append((0,0,{
            'voucher_id': False,
            'opening_balance': 'Days Total',
            'debit': get_total_debit(get_move_ids(cb), get_opening_balance(cb)),
            'crebit': get_total_credit(get_move_ids(cb)),
            'balance': get_total_balance(get_move_ids(cb), get_opening_balance(cb)),
            'date':False,
            'desc':False,
        }))
        vals = {
            'name': 'Bank Book for the Period: ',
            'cb_line': cb_line,
            'date_from': cb.date_from,
            'date_to': cb.date_to,
            #'type_trans': 'Transaction type : '+ cb.type_trans,
            'type_trans': cb.type_trans,
            'type_recon': cb.type_recon, #TPT-Y
            'is_posted': cb.is_posted,
            'account_id' : cb.account_id.id,
            #'bank_acc_no': 'Bank Account No : '+get_account_master_code()+' - '+ get_account_master_name()
            'bank_acc_no': 'Bank Account No : '+get_account_master_code(cb.account_id)+' - '+ get_account_master_name(cb.account_id)
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_bank_book_form')
        return {
                    'name': 'Bank Book Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.bank.book',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                }
        
bank_book_report()