# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_cash_book(osv.osv_memory):
    _name = "tpt.cash.book"
    _columns = {
        'name': fields.char('SI.No', readonly=True),
        'cash_acc_no': fields.char('SI.No', readonly=True),
        'cb_line': fields.one2many('tpt.cash.book.line', 'cb_id', 'Cash Book Line'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type'),
        'is_posted': fields.boolean('Is Posted'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.cash.book'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_cash_book_xls_test', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.cash.book'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_cash_book', 'datas': datas}
    
tpt_cash_book()

class tpt_cash_book_line(osv.osv_memory):
    _name = "tpt.cash.book.line"
    _columns = {
        'cb_id': fields.many2one('tpt.cash.book', 'Cash Book', ondelete='cascade'),
        'voucher_id': fields.char('Posting Doc No.', size = 1024),
        'opening_balance': fields.char('', size = 1024),
        'debit': fields.float('Debit (Rs.)'),
        'crebit': fields.float('Credit (Rs.)'),
        'balance': fields.float('Balance (Rs.)'),
        'date': fields.date('Date'),
        'desc': fields.char('GL Name', size = 1024),
        'gl_code': fields.char('GL Code', size = 1024),
        'ref': fields.char('Reference', size = 1024),
        'payee': fields.char('Payee', size = 1024),
        'voucher_desc': fields.char('Description', size = 1024),
        #'is_posted': fields.boolean('Is Posted'),
        'trans_no': fields.char('Transaction No', size = 1024),#TPT-P
    }

tpt_cash_book_line()

class cash_book_report(osv.osv_memory):
    _name = "cash.book.report"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type'),
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
        
        def get_account_master_name():  
            sql = '''
                SELECT name FROM account_account
                    WHERE name LIKE '%CASH IN HAND%'
            '''
            cr.execute(sql)
            name = cr.dictfetchone()
            return name and name['name'] or ''
        
        def get_account_master_code():  
            sql = '''
                SELECT code FROM account_account
                    WHERE code LIKE '%0000110001%'
            '''
            cr.execute(sql)
            code = cr.dictfetchone()
            return code and code['code'] or ''
        
        def get_opening_balance(o):  
            date_from = o.date_from
            date_to = o.date_to
            type = o.type_trans
            is_posted = o.is_posted
            
            balance = 0.0  
            credit = 0.0
            debit = 0.0
            if is_posted is True:
                sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id  and aa.code='0000110001')
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where av.type in ('payment','receipt') and aml.credit>0 and av.state in ('posted') and av.date < '%s'
                 '''%(date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    credit += move['credit']
                    
                sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id  and aa.code='0000110001')
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where av.type in ('payment','receipt') and aml.debit>0 and av.state in ('posted') and av.date < '%s'
                '''%(date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    debit += move['debit']    
                balance = debit - credit
            else:
                sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id  and aa.code='0000110001')
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where av.type in ('payment','receipt') and aml.credit>0 and av.state in ('draft','posted') and av.date < '%s'
                '''%(date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    credit += move['credit']
                    
                sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id  and aa.code='0000110001')
                    inner join account_voucher av on (av.move_id = aml.move_id)
                    where av.type in ('payment','receipt') and aml.debit>0 and av.state in ('draft','posted') and av.date < '%s'
                '''%(date_from)
                cr.execute(sql)
                for move in cr.dictfetchall():
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
            is_posted = o.is_posted
            
            if is_posted is True:
                if type == 'payment':
                    sql = '''
                            select id from account_voucher where date between '%s' and '%s' and type = 'payment' and journal_id in 
                            (select id from account_journal where type in ('cash','general')) and state in ('posted')
                        '''%(date_from, date_to)
                    cr.execute(sql)
                    account_ids = [row[0] for row in cr.fetchall()]
    #                 account_ids = account_voucher_obj.search(cr,uid,[('date', '>=', date_from),('date', '<=', date_to), ('type', '=', 'payment')])
                    if account_ids:
                        #=======================================================
                        # cr.execute('''
                        #     select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, 
                        #     sum(aml.credit) as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref, av.payee, aml.name , aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'payment' and state in ('draft','posted')) and debit is not null and debit !=0 and aa.id = aml.account_id 
                        #     group by av.name,aa.name, aml.account_id,av.date, aml.ref, av.payee, aml.name order by av.date
                        # ''',(tuple(account_ids),))
                        #=======================================================
                        cr.execute(''' 
                            select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                            av.name as voucher_name,av.date as voucher_date,aml.ref as ref, av.payee, aml.name as voucher_desc,av.number as trans_no
                            from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account aa on (aa.id=aml.account_id)
                            inner join account_voucher av on av.move_id = aml.move_id
                            inner join (
                            select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account acc on (acc.id=aml.account_id and acc.code='0000110001')
                            )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                            where av.type in ('payment') and av.state in ('posted') and av.id in %s 
                            group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name, av.number
                            order by av.date
                        ''', (tuple(account_ids),) )
                        return cr.dictfetchall()
                    else:
                        return []
                elif type == 'receipt':
                    sql = '''
                            select id from account_voucher where date between '%s' and '%s' and type = 'receipt' 
                            and journal_id in (select id from account_journal where type in ('cash','general')) 
                            and state in ('posted')
                        '''%(date_from, date_to)
                    cr.execute(sql)
                    account_ids = [row[0] for row in cr.fetchall()]
    #                 account_ids = account_voucher_obj.search(cr,uid,[('date', '>=', date_from),('date', '<=', date_to), ('type', '=', 'receipt')])
                    if account_ids:
                        #=======================================================
                        # cr.execute('''
                        #     select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, sum(aml.credit) as credit,av.name as voucher_name,
                        #     av.date as voucher_date, aml.ref as ref, av.payee payee, aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'receipt' and state in ('draft','posted')) and credit is not null and credit !=0 and aa.id = aml.account_id 
                        #     group by av.name,aa.name, aml.account_id,av.date, aml.ref, av.payee, aml.name order by av.date
                        # 
                        # ''',(tuple(account_ids),))
                        #=======================================================
                        cr.execute(''' 
                            select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                            av.name as voucher_name,av.date as voucher_date,aml.ref as ref, av.payee, aml.name as voucher_desc,av.number as trans_no
                            from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account aa on (aa.id=aml.account_id)
                            inner join account_voucher av on av.move_id = aml.move_id
                            inner join (
                            select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account acc on (acc.id=aml.account_id and acc.code='0000110001')
                            )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                            where av.type in ('receipt') and av.state in ('posted') and av.id in %s 
                            group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name, av.number
                            order by av.date
                        ''', (tuple(account_ids),) )
                        return cr.dictfetchall()
                    else:
                        return []
                else:
                    sql = '''
                            select id from account_voucher where date between '%s' and '%s' and journal_id in 
                            (select id from account_journal where type in ('cash','general')) and state in ('posted')
                        '''%(date_from, date_to)
                    cr.execute(sql)
                    account_ids = [row[0] for row in cr.fetchall()]
    #                 account_ids = account_voucher_obj.search(cr,uid,[('date', '>=', date_from),('date', '<=', date_to)])
                    if account_ids:
                        #=======================================================
                        # cr.execute('''
                        #     select foo.acc_name, foo.account_id, sum(foo.debit) as debit, sum(foo.credit) as credit,foo.voucher_name,foo.voucher_date, foo.ref, foo.payee, foo.voucher_desc from
                        #     (select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date , aml.ref as ref, av.payee, 
                        #     aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'payment' and state in ('draft','posted')) and aml.debit is not null and aml.debit !=0 and aa.id = aml.account_id
                        #     union all
                        #     select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref, av.payee, 
                        #     aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'receipt' and state in ('draft','posted')) and aml.credit is not null and aml.credit !=0 and aa.id = aml.account_id
                        #     )foo
                        #     group by foo.acc_name, foo.account_id, foo.voucher_name,foo.voucher_date, foo.ref, foo.payee, foo.voucher_desc order by foo.voucher_date
                        # ''',(tuple(account_ids),tuple(account_ids),))
                        #=======================================================
                        ###
                        cr.execute('''
                            select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                            av.name as voucher_name,av.date as voucher_date,aml.ref as ref, av.payee, aml.name as voucher_desc,av.number as trans_no
                            from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account aa on (aa.id=aml.account_id)
                            inner join account_voucher av on av.move_id = aml.move_id
                            inner join (
                            select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account acc on (acc.id=aml.account_id and acc.code='0000110001')
                            )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                            where av.type in ('payment','receipt') and av.state in ('posted') and av.id in %s 
                            group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name, av.number
                            order by av.date
                        ''',(tuple(account_ids),))
                        ###
                        return cr.dictfetchall()
                    else:
                        return [] 
            else: # POSTED ELSE PART
                if type == 'payment':
                    sql = '''
                            select id from account_voucher where date between '%s' and '%s' and type = 'payment' 
                            and journal_id in (select id from account_journal where type in ('cash','general')) and state in ('draft','posted')
                        '''%(date_from, date_to)
                    cr.execute(sql)
                    account_ids = [row[0] for row in cr.fetchall()]
    #                 account_ids = account_voucher_obj.search(cr,uid,[('date', '>=', date_from),('date', '<=', date_to), ('type', '=', 'payment')])
                    if account_ids:
                        #=======================================================
                        # cr.execute('''
                        #     select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, 
                        #     sum(aml.credit) as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref, av.payee, aml.name , aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'payment' and state in ('draft','posted')) and debit is not null and debit !=0 and aa.id = aml.account_id 
                        #     group by av.name,aa.name, aml.account_id,av.date, aml.ref, av.payee, aml.name order by av.date
                        # ''',(tuple(account_ids),))
                        #=======================================================
                        cr.execute(''' 
                            select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                            av.name as voucher_name,av.date as voucher_date,aml.ref as ref, av.payee, aml.name as voucher_desc,av.number as trans_no
                            from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account aa on (aa.id=aml.account_id)
                            inner join account_voucher av on av.move_id = aml.move_id
                            inner join (
                            select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account acc on (acc.id=aml.account_id and acc.code='0000110001')
                            )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                            where av.type in ('payment') and av.state in ('draft','posted') and av.id in %s 
                            group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name, av.number
                            order by av.date
                        ''', (tuple(account_ids),) )
                        return cr.dictfetchall()
                    else:
                        return []
                elif type == 'receipt':
                    sql = '''
                            select id from account_voucher where date between '%s' and '%s' and type = 'receipt' and journal_id in (select id from account_journal where type in ('cash','general')) and state in ('draft','posted')
                        '''%(date_from, date_to)
                    cr.execute(sql)
                    account_ids = [row[0] for row in cr.fetchall()]
    #                 account_ids = account_voucher_obj.search(cr,uid,[('date', '>=', date_from),('date', '<=', date_to), ('type', '=', 'receipt')])
                    if account_ids:
                        #=======================================================
                        # cr.execute('''
                        #     select aa.name as acc_name, aml.account_id, sum(aml.debit) as debit, sum(aml.credit) as credit,av.name as voucher_name,
                        #     av.date as voucher_date, aml.ref as ref, av.payee payee, aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'receipt' and state in ('draft','posted')) and credit is not null and credit !=0 and aa.id = aml.account_id 
                        #     group by av.name,aa.name, aml.account_id,av.date, aml.ref, av.payee, aml.name order by av.date
                        # 
                        # ''',(tuple(account_ids),))
                        #=======================================================
                        cr.execute(''' 
                            select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                            av.name as voucher_name,av.date as voucher_date,aml.ref as ref, av.payee, aml.name as voucher_desc,av.number as trans_no
                            from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account aa on (aa.id=aml.account_id)
                            inner join account_voucher av on av.move_id = aml.move_id
                            inner join (
                            select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account acc on (acc.id=aml.account_id and acc.code='0000110001')
                            )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                            where av.type in ('receipt') and av.state in ('draft','posted') and av.id in %s 
                            group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name, av.number
                            order by av.date
                        ''', (tuple(account_ids),) )
                        return cr.dictfetchall()
                    else:
                        return []
                else:
                    sql = '''
                            select id from account_voucher where date between '%s' and '%s' and journal_id in (select id from account_journal where type in ('cash','general')) and state in ('draft','posted')
                        '''%(date_from, date_to)
                    cr.execute(sql)
                    account_ids = [row[0] for row in cr.fetchall()]
    #                 account_ids = account_voucher_obj.search(cr,uid,[('date', '>=', date_from),('date', '<=', date_to)])
                    if account_ids:
                        #=======================================================
                        # cr.execute('''
                        #     select foo.acc_name, foo.account_id, sum(foo.debit) as debit, sum(foo.credit) as credit,foo.voucher_name,foo.voucher_date, foo.ref, foo.payee, foo.voucher_desc from
                        #     (select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date , aml.ref as ref, av.payee, 
                        #     aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'payment' and state in ('draft','posted')) and aml.debit is not null and aml.debit !=0 and aa.id = aml.account_id
                        #     union all
                        #     select aa.name as acc_name, aml.account_id, aml.debit as debit, aml.credit as credit,av.name as voucher_name,av.date as voucher_date, aml.ref as ref, av.payee, 
                        #     aml.name voucher_desc
                        #     from account_account aa, account_move_line aml,account_voucher av where av.move_id = aml.move_id and
                        #     aml.move_id in (select move_id from account_voucher where id in %s and type = 'receipt' and state in ('draft','posted')) and aml.credit is not null and aml.credit !=0 and aa.id = aml.account_id
                        #     )foo
                        #     group by foo.acc_name, foo.account_id, foo.voucher_name,foo.voucher_date, foo.ref, foo.payee, foo.voucher_desc order by foo.voucher_date
                        # ''',(tuple(account_ids),tuple(account_ids),))
                        #=======================================================
                        ###
                        cr.execute('''
                            select aa.name as acc_name,aml.account_id,sum(aml.debit) as debit,sum(aml.credit) as credit,
                            av.name as voucher_name,av.date as voucher_date,aml.ref as ref, av.payee, aml.name as voucher_desc,av.number as trans_no
                            from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account aa on (aa.id=aml.account_id)
                            inner join account_voucher av on av.move_id = aml.move_id
                            inner join (
                            select distinct am.id as cash_header_id,aml.account_id as cash_account_id from account_move_line aml
                            inner join account_move am on (am.id=aml.move_id)
                            inner join account_account acc on (acc.id=aml.account_id and acc.code='0000110001')
                            )a on (a.cash_header_id=am.id and cash_account_id<>aml.account_id)
                            where av.type in ('payment','receipt') and av.state in ('draft','posted') and av.id in %s 
                            group by aa.name,aml.account_id,av.name,av.date,aml.ref,av.payee,aml.name, av.number
                            order by av.date
                        ''',(tuple(account_ids),))
                        ###
                        return cr.dictfetchall()
                    else:
                        return []    
            ###
                
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
        cr.execute('delete from tpt_cash_book')
        cb_obj = self.pool.get('tpt.cash.book')
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
                'payee': line['payee'],
                'voucher_desc': line['voucher_desc'],
                'trans_no': line['trans_no'],
                
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
            'name': 'Cash Book for the Period: ',
            'cb_line': cb_line,
            'date_from': cb.date_from,
            'date_to': cb.date_to,
            'type_trans': cb.type_trans,
            'is_posted': cb.is_posted,
            'cash_acc_no': 'Cash Account No : '+get_account_master_code()+' - '+ get_account_master_name()
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_cash_book_form')
        return {
                    'name': 'Cash Book Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.cash.book',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                }
        
cash_book_report()