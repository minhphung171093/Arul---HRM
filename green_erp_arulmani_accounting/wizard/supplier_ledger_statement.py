# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class supplier_ledger_statement(osv.osv_memory):
    _name = "supplier.ledger.statement"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'supplier_id':fields.many2one('res.partner','Supplier',required=True),
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
        
        #TPT-Y on 23/09/2015
        def get_opening_balance(sls):  
            date_from = sls.date_from
            #date_to = sls.date_to
            sup = sls.supplier_id.id
            is_posted = sls.is_posted
            
            balance = 0.0  
            credit = 0.0
            debit = 0.0
            if is_posted is True:
                sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state='posted'                    
                    and aml.account_id =(
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s ) 
                    ))
                    '''%(date_from,sup)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    credit += move['credit']
                    
                sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state='posted'                    
                    and aml.account_id =(
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s ) 
                    ))
                '''%(date_from,sup)
                
                cr.execute(sql)
                for move in cr.dictfetchall():
                    debit += move['debit']    
                balance = debit - credit
            else:
                sql = '''
                    select case when coalesce(sum(aml.credit),0)=0 then 0 else sum(aml.credit) end as credit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state in ('draft','posted')                   
                    and aml.account_id =(
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s ) 
                    ))
                '''%(date_from,sup)                
                cr.execute(sql)
                for move in cr.dictfetchall(): 
                    credit += move['credit']
                    
                sql = '''
                    select case when coalesce(sum(aml.debit),0)=0 then 0 else sum(aml.debit) end as debit 
                    from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date < '%s' and am.state in ('draft','posted')                   
                    and aml.account_id =(
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s ) 
                    )) 
                '''%(date_from,sup)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    debit += move['debit']    
                balance = debit - credit
            return balance or 0.00
        
        def convert_date_cash(date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
         
        def get_invoice(sls):
            res = {}
            date_from = sls.date_from
            date_to = sls.date_to
            sup = sls.supplier_id.id
            is_posted = sls.is_posted
            acount_move_line_obj = self.pool.get('account.move.line')
            acount_move_obj = self.pool.get('account.move')
            sup_ids = []
            if is_posted is True:
                sql = '''
                    select aml.id from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date between '%s' and '%s' 
                    and am.state='posted' 
                    and aml.account_id =(
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s ) 
                    )) order by am.date
                    '''%(date_from, date_to,sup)
                cr.execute(sql)
                sup_ids = [r[0] for r in cr.fetchall()]
            else:
                sql = '''
                    select aml.id from account_move_line aml 
                    inner join account_move am on (aml.move_id = am.id)
                    left join res_partner p on (p.id=am.partner_id)
                    inner join account_account aa on (aa.id=aml.account_id)
                    where am.date between '%s' and '%s' 
                    and am.state in ('draft','posted') 
                    and aml.account_id =(
                    select id from account_account where id in (
                    select btrim(value_reference,'account.account,')::Integer
                    from ir_property where res_id in ('res.partner,'|| %s ) 
                    )) order by am.date
                    '''%(date_from, date_to,sup)
                cr.execute(sql)
                sup_ids = [r[0] for r in cr.fetchall()]
#             sql = '''
#                 select id from account_move_line 
#                 where move_id in (
#                                     select id from account_move 
#                                     where date between '%s' and '%s' and doc_type in ('sup_pay') and partner_id = %s and state='posted') and credit is not null and credit !=0
#                 '''%(date_from, date_to,sup)
#             cr.execute(sql)
#             sup_ids += [r[0] for r in cr.fetchall()]
            return acount_move_line_obj.browse(cr,uid,sup_ids)
         
        def get_bill_no(move_id, doc_type):
            if doc_type == 'sup_inv_po' or doc_type == 'sup_inv' or doc_type=='ser_inv' or doc_type=='freight':
                cr.execute('''select bill_number from account_invoice where move_id =%s''', (move_id,))
            else:
                return ''
            number = cr.fetchone()
            return number and number[0] or ''
        
        def get_inv_no(move_id, doc_type):
            if doc_type == 'sup_inv_po' or doc_type == 'sup_inv' or doc_type=='ser_inv' or doc_type=='freight':
                cr.execute('''select name from account_invoice where move_id =%s''', (move_id,))
            else:
                return ''
            number = cr.fetchone()
            return number and number[0] or ''
         
        def get_bill_date(move_id, doc_type):
            if doc_type == 'sup_inv_po' or doc_type == 'sup_inv' or doc_type=='ser_inv' or doc_type=='freight':
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
         
        #TPT-Y on 23/09/2015
        def get_total_debit(get_move_ids, get_opening_balance):
            debit = 0.0
            for move in get_move_ids:
                debit += move['debit']    
            return debit+get_opening_balance
        
        #TPT-Y on 23/09/2015
        def get_total_balance(get_move_ids, get_opening_balance):
            debit = 0.0
            credit = 0.0
            balance = 0.0
            for move in get_move_ids:
                debit += move['debit']
                credit += move['credit']      
            balance = (debit+get_opening_balance) - credit
            return balance
        
        #TPT-Y on 23/09/2015
        def get_total(cash):
            sum = 0.0
            for line in cash:
                sum += line.credit
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
            if doc_type == 'sup_inv_po' or doc_type=='freight':
                cr.execute('''select name from purchase_order where id in (select purchase_id from account_invoice where move_id =%s)''', (move_id,))
            number = cr.fetchone()
            return number and number[0] or ''
        def get_po_id(move_id, doc_type):
            if doc_type == 'sup_inv_po' or doc_type=='freight':
                cr.execute('''select id from purchase_order where id in (select purchase_id from account_invoice where move_id =%s)''', (move_id,))
            number = cr.fetchone()
            return number and number[0] or ''
     
        def get_so_date(move_id, doc_type):
            if doc_type == 'sup_inv_po' or doc_type=='freight':
                cr.execute('''select date_order from purchase_order where id in (select purchase_id from account_invoice where move_id =%s)''', (move_id,))
            date = cr.fetchone()
            return date and date[0] or ''
        
        cr.execute('delete from tpt_supplier_ledger')
        sls_obj = self.pool.get('tpt.supplier.ledger')
        sls = self.browse(cr, uid, ids[0])
        sls_line = []
        sls_line.append((0,0,{
                'cheque_no': 'Opening Balance:', #TPT-Y on 23/09/2015
                'debit': get_opening_balance(sls), #TPT-Y on 23/09/2015,
                
            }))
        for line in get_invoice(sls):
            sls_line.append((0,0,{
                'date': line.move_id and line.move_id.date or '',
                'document_no': line.move_id and line.move_id.name or '',
                'narration': line.move_id and line.move_id.narration or '',
                'sale_order_no': get_so_no(line.move_id.id, line.move_id.doc_type) + ' ' + get_so_date(line.move_id.id, line.move_id.doc_type), #YuVi
                'reference': line.move_id and line.move_id.ref or '',
                'invoice_no': get_inv_no(line.move_id.id, line.move_id.doc_type),
                'bill_no': get_bill_no(line.move_id.id, line.move_id.doc_type),
                'bill_date': get_bill_date(line.move_id.id, line.move_id.doc_type),
                'cheque_no': get_cheque_no(line.move_id.id),
                'cheque_date': get_cheque_date(line.move_id.id),
                'debit': line.debit and line.debit or '',
                'credit': line.credit and line.credit or '',
                'order_id': get_po_id(line.move_id.id, line.move_id.doc_type) or False, 
                'move_id':line.move_id and line.move_id.id or False,
            }))
        sls_line.append((0,0,{
                'cheque_no': 'Total',
                'debit': get_total_debit(get_invoice(sls), get_opening_balance(sls)), #TPT-Y on 23/09/2015
                'credit': get_total(get_invoice(sls)), #TPT-Y on 23/09/2015
            }))
        sls_line.append((0,0,{
                'cheque_no': 'Balance',
                'credit': get_total_balance(get_invoice(sls), get_opening_balance(sls)), #TPT-Y on 23/09/2015
            }))
        vals = {
                'name': 'Supplier Ledger Statement',
                'date_from_title': 'Date From: ',
                'date_to_title': 'Date To: ',
                'sup_code_title': 'Supplier Code: ',
                'sup_name_title': 'Supplier Name: ',
                'date_from': sls.date_from,
                'date_to': sls.date_to,
                'sup_code': sls.supplier_id and sls.supplier_id.vendor_code or '',
                'sup_name': sls.supplier_id.name,
                'supplier_id': sls.supplier_id.id,
                'is_posted': sls.is_posted,
                'sup_ledger_line': sls_line,
                }
        sls_id = sls_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_supplier_ledger_form')
        return {
                        'name': 'Supplier Ledger Statement',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'tpt.supplier.ledger',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': sls_id,
                    }
        
supplier_ledger_statement()
   
   
class tpt_supplier_ledger(osv.osv_memory): 
    _name = "tpt.supplier.ledger"
    _columns = {
                'name': fields.char('Supplier Ledger Statement', size = 1024), 
                'date_from': fields.date('Date From: '),
                'date_from_title': fields.char('', size = 1024),
                'date_to_title': fields.char('', size = 1024),
                'sup_code_title': fields.char('', size = 1024),
                'sup_name_title': fields.char('', size = 1024),
                'date_to': fields.date('Date To: '),
                'sup_code': fields.char('Supplier Code: ', size = 1024),
                'sup_name': fields.char('Supplier Name: ', size = 1024),
                'supplier_id':fields.many2one('res.partner','Supplier'),
                'is_posted': fields.boolean('Is Posted'),
                'sup_ledger_line': fields.one2many('tpt.supplier.ledger.line', 'ledger_id', 'Supplier Ledger Statement Line'),
                }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.supplier.ledger'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'supplier_ledger_statement_report', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.supplier.ledger'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'supplier_ledger_statement_report_pdf', 'datas': datas}
    
tpt_supplier_ledger()  

class tpt_supplier_ledger_line(osv.osv_memory):
    _name = "tpt.supplier.ledger.line"
    _columns = {
        'ledger_id': fields.many2one('tpt.supplier.ledger', 'Supplier Ledger', ondelete='cascade'),
        'date': fields.date('Posting Date'),
        'document_no': fields.char('Posting Doc.No.', size = 1024),
        'reference': fields.char('Reference', size = 1024),        
        'narration': fields.char('Narration', size = 1024),
        'sale_order_no': fields.char('Purchase Order No. & Date', size = 1024),
        'invoice_no': fields.char('System Inv. No', size = 1024),
        'bill_no': fields.char('Bill No', size = 1024),
        'bill_date': fields.date('Bill Date'),
        'cheque_no':fields.char('Cheque No', size = 1024),
        'cheque_date': fields.date('Cheque Date'),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
        'order_id':fields.many2one('purchase.order','Purchase Order'),
        'move_id':fields.many2one('account.move','Document Number'),
    }

tpt_supplier_ledger_line()      