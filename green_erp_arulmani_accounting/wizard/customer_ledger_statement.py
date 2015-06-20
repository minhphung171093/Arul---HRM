# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class customer_ledger_statement(osv.osv_memory):
    _name = "customer.ledger.statement"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'customer_id':fields.many2one('res.partner','Customer',required=True),
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
        
        def convert_date_cash(date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
        
        def get_invoice(cls):
            res = {}
            date_from = cls.date_from
            date_to = cls.date_to
            cus = cls.customer_id.id
            is_posted = cls.is_posted
            
            acount_move_line_obj = self.pool.get('account.move.line')
            acount_move_obj = self.pool.get('account.move')
            cus_ids = []
            if is_posted is True:
                sql = '''
                    select aml.id from account_move_line aml inner join account_move am on aml.move_id = am.id
                    where am.date between '%s' and '%s' and am.doc_type in ('cus_inv') and am.partner_id = %s and am.state='posted' and aml.debit is not null and aml.debit !=0
                    or (am.date between '%s' and '%s' and am.doc_type in ('cus_pay') and am.partner_id = %s and am.state='posted' and aml.credit is not null and aml.credit !=0)
                        order by am.date  
                    '''%(date_from, date_to,cus,date_from, date_to,cus)
                cr.execute(sql)
                cus_ids = [r[0] for r in cr.fetchall()]
            else:
                sql = '''
                    select aml.id from account_move_line aml inner join account_move am on aml.move_id = am.id
                    where am.date between '%s' and '%s' and am.doc_type in ('cus_inv') and am.partner_id = %s and am.state='draft' and aml.debit is not null and aml.debit !=0
                    or (am.date between '%s' and '%s' and am.doc_type in ('cus_pay') and am.partner_id = %s and am.state='draft' and aml.credit is not null and aml.credit !=0)
                        order by am.date  
                    '''%(date_from, date_to,cus,date_from, date_to,cus)
                cr.execute(sql)
                cus_ids = [r[0] for r in cr.fetchall()]
#             sql = '''
#                 select id from account_move_line 
#                 where move_id in (
#                                     select id from account_move 
#                                     where date between '%s' and '%s' and doc_type in ('cus_pay') and partner_id = %s and state='posted' ) and credit is not null and credit !=0   
#                 '''%(date_from, date_to,cus)
#             cr.execute(sql)
#             cus_ids += [r[0] for r in cr.fetchall()]
            return acount_move_line_obj.browse(cr,uid,cus_ids)
        
        def get_bill_no(move_id, doc_type):
            if doc_type == 'cus_inv':
                cr.execute('''select vvt_number from account_invoice where move_id =%s''', (move_id,))
            else:
                cr.execute('''select number from account_voucher where move_id =%s''', (move_id,))
            number = cr.fetchone()
            return number and number[0] or ''
        
        def get_bill_date(move_id, doc_type):
            if doc_type == 'cus_inv':
                cr.execute('''select bill_date from account_invoice where move_id =%s''', (move_id,))
            else:
                cr.execute('''select date from account_voucher where move_id =%s''', (move_id,))
            date = cr.fetchone()
            return date and date[0] or False
        
        def get_cheque_no(move_id):
            sql = '''
                select cheque_number from account_voucher where move_id = %s
            '''%(move_id)
            cr.execute(sql)
            p = cr.dictfetchone()
            return p and p['cheque_number'] or ''
    
        def get_cheque_date(move_id):
            sql = '''
                select cheque_date from account_voucher where move_id = %s
            '''%(move_id)
            cr.execute(sql)
            p = cr.fetchone()
            return p and p[0] or False
        
        def get_total(cash,type):
            sum = 0.0
            for line in cash:
                if type == 'credit':
                    sum += line.credit
                if type == 'debit':
                    sum += line.debit
            return sum
        
        def get_balance(get_invoice):
            credit = 0.0
            debit = 0.0
            for line in get_invoice:
                debit += line.debit
                credit += line.credit
            balance = float(debit) - float(credit)
            balance = float(balance)
            return balance
        
        def get_so_no(move_id, doc_type):
            number = ''
            if doc_type == 'cus_inv':
                cr.execute('''select name from sale_order where id in (select sale_id from account_invoice where move_id =%s)''', (move_id,))
            number = cr.fetchone()
            return number and number[0] or ''
    
        def get_so_date(move_id, doc_type):
            if doc_type == 'cus_inv':
                cr.execute('''select date_order from sale_order where id in (select sale_id from account_invoice where move_id =%s)''', (move_id,))
            date = cr.fetchone()
            return date and date[0] or ''
        
        cr.execute('delete from tpt_customer_ledger')
        cls_obj = self.pool.get('tpt.customer.ledger')
        cls = self.browse(cr, uid, ids[0])
        cls_line = []
        for line in get_invoice(cls):
            cls_line.append((0,0,{
                'date': line.move_id and line.move_id.date or '',
                'document_no': line.move_id and line.move_id.name or '',
                'narration': line.move_id and line.move_id.ref or '',
                'sale_order_no': get_so_no(line.move_id.id, line.move_id.doc_type) + ' - ' + get_so_date(line.move_id.id, line.move_id.doc_type),
                'bill_no': get_bill_no(line.move_id.id, line.move_id.doc_type),
                'bill_date': get_bill_date(line.move_id.id, line.move_id.doc_type),
                'cheque_no': get_cheque_no(line.move_id.id),
                'cheque_date': get_cheque_date(line.move_id.id),
                'debit': line.debit and line.debit or '',
                'credit': line.credit and line.credit or '',
            }))
        cls_line.append((0,0,{
                'cheque_no': 'Total',
                'debit': get_total(get_invoice(cls),'debit'),
                'credit': get_total(get_invoice(cls),'credit'),
            }))
        cls_line.append((0,0,{
                'cheque_no': 'Balance',
                'credit': get_balance(get_invoice(cls)),
            }))
        vals = {
                'name': 'Customer Ledger Statement',
                'date_from_title': 'Date From: ',
                'date_to_title': 'Date To: ',
                'cus_code_title': 'Customer Code: ',
                'cus_name_title': 'Customer Name: ',
                'date_from': cls.date_from,
                'date_to': cls.date_to,
                'cus_code': cls.customer_id.customer_code,
                'cus_name': cls.customer_id.name,
                'customer_id': cls.customer_id.id,
                'is_posted': cls.is_posted,
                'cus_ledger_line': cls_line,
                }
        cls_id = cls_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_customer_ledger_form')
        return {
                        'name': 'Customer Ledger Statement',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'tpt.customer.ledger',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': cls_id,
                    }
        
customer_ledger_statement()
   
   
class tpt_customer_ledger(osv.osv_memory): 
    _name = "tpt.customer.ledger"
    _columns = {
                'name': fields.char('Customer Ledger Statement', size = 1024),  
                'date_from': fields.date('Date From: '),
                'date_from_title': fields.char('', size = 1024),
                'date_to_title': fields.char('', size = 1024),
                'cus_code_title': fields.char('', size = 1024),
                'cus_name_title': fields.char('', size = 1024),
                'date_to': fields.date('Date To: '),
                'cus_code': fields.char('Customer Code: ', size = 1024),
                'cus_name': fields.char('Customer Name: ', size = 1024),
                'customer_id':fields.many2one('res.partner','Customer'),
                'is_posted': fields.boolean('Is Posted'),
                'cus_ledger_line': fields.one2many('tpt.customer.ledger.line', 'ledger_id', 'Customer Ledger Statement Line'),
                }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.customer.ledger'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'customer_ledger_statement_report', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.customer.ledger'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'customer_ledger_statement_report_pdf', 'datas': datas}
    
tpt_customer_ledger()  

class tpt_customer_ledger_line(osv.osv_memory):
    _name = "tpt.customer.ledger.line"
    _columns = {
        'ledger_id': fields.many2one('tpt.customer.ledger', 'Customer Ledger', ondelete='cascade'),
        'date': fields.date('Date'),
        'document_no': fields.char('Document No.', size = 1024),
        'narration': fields.char('Narration', size = 1024),
        'sale_order_no': fields.char('Sale Order No.', size = 1024),
        'bill_no': fields.char('Bill No', size = 1024),
        'bill_date': fields.date('Bill Date'),
        'cheque_no':fields.char('Cheque No', size = 1024),
        'cheque_date': fields.date('Cheque Date'),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
    }

tpt_customer_ledger_line()      
