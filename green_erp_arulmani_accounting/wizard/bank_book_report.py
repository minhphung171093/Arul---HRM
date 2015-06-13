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
        'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type')
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
        'voucher_id': fields.char('Voucher No.', size = 1024),
        'opening_balance': fields.char('', size = 1024),
        'debit': fields.float('Debit (Rs.)'),
        'crebit': fields.float('Credit (Rs.)'),
        'balance': fields.float('Balance (Rs.)'),
        'date': fields.date('Date'),
        'desc': fields.char('Description', size = 1024),
        'gl_code': fields.char('GL Code', size = 1024),
        'ref': fields.char('Reference', size = 1024),
    }

tpt_bank_book_line()

class bank_book_report(osv.osv_memory):
    _name = "bank.book.report"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type')
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
        
        def get_account_master_name():  
            sql = '''
            SELECT name FROM account_account
                WHERE name LIKE '%FEDERAL BANK - TTN%'
            '''
            cr.execute(sql)
            name = cr.dictfetchone()
            return name and name['name'] or ''
        
        def get_account_master_code():  
            sql = '''
            SELECT code FROM account_account
                WHERE code LIKE '%0000111001%'
            '''
            cr.execute(sql)
            code = cr.dictfetchone()
            return code and code['code'] or ''
        
        def get_opening_balance(o):  
            date_from = o.date_from
            date_to = o.date_to
            type = o.type_trans
            balance = 0.0  
            credit = 0.0
            debit = 0.0
            sql = '''
                select sum(aml.credit) as credit, aml.date from account_move_line aml 
                where aml.credit is not null and aml.credit != 0 and aml.date < '%s' 
                and move_id in (select move_id from account_voucher where type = 'payment' and state = 'posted' and journal_id in (select id from account_journal where type = 'bank')) 
                group by aml.date
            '''%(date_from)
            cr.execute(sql)
            for move in cr.dictfetchall():
                if move['credit']:
                    credit += move['credit']
                
            sql = '''
                select sum(aml.debit) as debit, aml.date from account_move_line aml 
                where aml.debit is not null and aml.debit != 0 and aml.date < '%s' 
                and move_id in (select move_id from account_voucher where type = 'receipt' and state = 'posted' and journal_id in (select id from account_journal where type = 'bank')) 
                group by aml.date
            '''%(date_from)
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
            if type == 'payment':
                sql = '''
                        select id from account_voucher where date between '%s' and '%s' and type = 'payment' and journal_id in (select id from account_journal where type = 'bank') and state = 'posted'
                    '''%(date_from, date_to)
                cr.execute(sql)
                account_ids = [row[0] for row in cr.fetchall()]
                if account_ids:
                    cr.execute('''
                        select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, sum(aml.credit) as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s and type = 'payment' and state = 'posted') and debit is not null and debit !=0 and aa.id = aml.account_id group by av.name,aa.name, aml.account_id,av.date, aml.ref order by av.date
                    ''',(tuple(account_ids),))
                    return cr.dictfetchall()
                else: 
                    return []
            elif type == 'receipt':
                sql = '''
                        select id from account_voucher where date between '%s' and '%s' and type = 'receipt' and journal_id in (select id from account_journal where type = 'bank') and state = 'posted'
                    '''%(date_from, date_to)
                cr.execute(sql)
                account_ids = [row[0] for row in cr.fetchall()]
                if account_ids: 
                    cr.execute('''
                        select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, sum(aml.credit) as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s and type = 'receipt' and state = 'posted') and credit is not null and credit !=0 and aa.id = aml.account_id group by av.name,aa.name, aml.account_id,av.date, aml.ref order by av.date
                    
                    ''',(tuple(account_ids),))
                    return cr.dictfetchall()
                else: 
                    return []
            else:
                sql = '''
                        select id from account_voucher where date between '%s' and '%s' and journal_id in (select id from account_journal where type = 'bank') and state = 'posted'
                    '''%(date_from, date_to)
                cr.execute(sql)
                account_ids = [row[0] for row in cr.fetchall()]
                if account_ids:    
                    cr.execute('''
                        select foo.acc_name, foo.account_id, sum(foo.debit) as debit, sum(foo.credit) as credit,foo.voucher_name,foo.voucher_date, foo.ref from
                        (select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date , aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s and type = 'payment' and state = 'posted') and aml.debit is not null and aml.debit !=0 and aa.id = aml.account_id
                        union all
                        select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        aml.move_id in (select move_id from account_voucher where id in %s and type = 'receipt' and state = 'posted') and aml.credit is not null and aml.credit !=0 and aa.id = aml.account_id
                        )foo
                        group by foo.acc_name, foo.account_id, foo.voucher_name,foo.voucher_date, foo.ref order by foo.voucher_date
                    ''',(tuple(account_ids),tuple(account_ids),))
                    return cr.dictfetchall()
                else: 
                    return []
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
                'voucher_id': line['voucher_name'],
                'opening_balance': False,
                'debit': line['credit'] and line['credit'] or 0,
                'crebit': line['debit'] and line['debit'] or 0,
                'balance': get_line_balance(seq,cb),
                'date': line['voucher_date'],
                'desc': line['acc_name'],
                'gl_code': get_code_account(line['account_id']),
                'ref': line['ref'],
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
            'type_trans': cb.type_trans,
            'bank_acc_no': 'Bank Account No : '+get_account_master_code()+' - '+ get_account_master_name()
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