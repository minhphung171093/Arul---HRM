# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
from datetime import date
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class tpt_posting_configuration(osv.osv):
    _name = 'tpt.posting.configuration'
    _columns = {
        'name': fields.selection([('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv', 'Supplier Invoice'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Payroll'),],'Document Type', required=True, states={ 'done':[('readonly', True)]}),
        'date':fields.date('Created on',readonly=True),
        'cus_inv_vat_id': fields.many2one('account.account', 'VAT Payable', states={ 'done':[('readonly', True)]}),
        'cus_inv_cst_id': fields.many2one('account.account', 'CST Payable', states={ 'done':[('readonly', True)]}),
        'cus_inv_ed_id': fields.many2one('account.account', 'Excise Duty', states={ 'done':[('readonly', True)]}),
        'cus_inv_pf_id': fields.many2one('account.account', 'P & F Charges', states={ 'done':[('readonly', True)]}),
        'cus_inv_fright_id': fields.many2one('account.account', 'Fright Charges', states={ 'done':[('readonly', True)]}),
        'cus_inv_insurance_id': fields.many2one('account.account', 'Insurance Charges', states={ 'done':[('readonly', True)]}),
        'cus_inv_price_id': fields.many2one('account.account', 'Price Difference / Rounding', states={ 'done':[('readonly', True)]}),
        'cus_pay_bank_id': fields.many2one('account.account', 'Bank Account', states={ 'done':[('readonly', True)]}),
        'cus_pay_cash_id': fields.many2one('account.account', 'Cash Accout', states={ 'done':[('readonly', True)]}),
        'sup_inv_vat_id': fields.many2one('account.account', 'VAT Receivables', states={ 'done':[('readonly', True)]}),
        'sup_inv_cst_id': fields.many2one('account.account', 'CST Receivables', states={ 'done':[('readonly', True)]}),
        'sup_inv_ed_id': fields.many2one('account.account', 'Excise Duty', states={ 'done':[('readonly', True)]}),
        'sup_inv_pf_id': fields.many2one('account.account', 'P & F Charges', states={ 'done':[('readonly', True)]}),
        'sup_inv_fright_id': fields.many2one('account.account', 'Fright Charges', states={ 'done':[('readonly', True)]}),
        'sup_inv_price_id': fields.many2one('account.account', 'Price Difference / Rounding', states={ 'done':[('readonly', True)]}),
        'sup_pay_bank_id': fields.many2one('account.account', 'Bank Account', states={ 'done':[('readonly', True)]}),
        'sup_pay_cash_id': fields.many2one('account.account', 'Cash Accout', states={ 'done':[('readonly', True)]}),
        'salari_id': fields.many2one('account.account', ' Salaries and Allowances', states={ 'done':[('readonly', True)]}),
        'pfp_id': fields.many2one('account.account', 'Provident Fund Payable', states={ 'done':[('readonly', True)]}),
        'vpf_id': fields.many2one('account.account', 'VPF', states={ 'done':[('readonly', True)]}),
        'esi_id': fields.many2one('account.account', 'ESI Payable', states={ 'done':[('readonly', True)]}),
        'staff_welfare_id': fields.many2one('account.account', 'Staff Welfare Expenses', states={ 'done':[('readonly', True)]}),
        'lic_id': fields.many2one('account.account', 'LIC-Premium-Employee', states={ 'done':[('readonly', True)]}),
        'profes_tax_id': fields.many2one('account.account', 'Profession Tax Payable', states={ 'done':[('readonly', True)]}),
        'lwf_id': fields.many2one('account.account', 'Labour welfare Fund', states={ 'done':[('readonly', True)]}),
        'staff_advance_id': fields.many2one('account.account', 'Staff Advance', states={ 'done':[('readonly', True)]}),
        'salari_payable_id': fields.many2one('account.account', 'Salaries And Allowance Payable', states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
        
    }
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state':'draft',
        'name':'cus_inv',
    }

    def bt_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
tpt_posting_configuration()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
     
    _columns = {
        'created_by':fields.char('Created By', size = 1024),
        'created_on': fields.date('Created On'),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order'),
        'vendor_ref': fields.char('Vendor Reference', size = 1024),
    }
     
account_invoice() 

# class account_invoice_line(osv.osv):
#     _inherit = "account.invoice.line"
#     
#     _columns = {
#         'created_by':fields.char('Created By', size = 1024),
#         'created_on': fields.date('Created On'),
#         'purchase_id': fields.many2one('purchase.order', 'Purchase Order'),
#         'vendor_ref': fields.char('Vendor Reference', size = 1024),
#     }
# account_invoice_line()

class tpt_posting_verification(osv.osv):
    _name = 'tpt.posting.verification'
    def amount_all_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_debits': 0.0,
                'amount_credits': 0.0,
                'amount_difference': 0.0,
            }
            debits = 0.0
            credits = 0.0
            diff=0.0
            for posting in line.gl_entry_line:
                debits += posting.debit
                credits += posting.credit
                if debits >= credits :
                    diff = debits - credits
                else:
                    diff = credits - debits 
            res[line.id]['amount_debits'] = debits
            res[line.id]['amount_credits'] = credits
            res[line.id]['amount_difference'] = diff
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.posting.verification.line').browse(cr, uid, ids, context=context):
            result[line.pos_ver_id.id] = True
        return result.keys()
    _columns = {
        'doc_type': fields.selection([('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv', 'Supplier Invoice'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Payroll'),],'Document Type', states={ 'done':[('readonly', True)]}),
        'name': fields.char('Document No.', size=1024, readonly=True ),
        'date':fields.date('Created on',readonly=True),
        'fiscal_period_id': fields.many2one('account.period', 'Fiscal Year Period', states={ 'done':[('readonly', True)]}),
        'posting_date': fields.date('Posting Date', states={ 'done':[('readonly', True)]}),
        'create_uid':fields.many2one('res.users','Created By', states={ 'done':[('readonly', True)]}),
        'amount_debits': fields.function(amount_all_line, multi='sums',string='Total Debits',
                                         store={
                'tpt.posting.verification': (lambda self, cr, uid, ids, c={}: ids, ['gl_entry_line'], 10),
                'tpt.posting.verification.line': (_get_order, ['debit', 'credit'], 10),}, 
           states={ 'done':[('readonly', True)]}),
        'amount_credits': fields.function(amount_all_line, multi='sums',string='Total Credits',
                                         store={
                'tpt.posting.verification': (lambda self, cr, uid, ids, c={}: ids, ['gl_entry_line'], 10),
                'tpt.posting.verification.line': (_get_order, ['debit', 'credit'], 10),}, 
           states={ 'done':[('readonly', True)]}),
                
        'amount_difference': fields.function(amount_all_line, multi='sums',string='Difference',
                                         store={
                'tpt.posting.verification': (lambda self, cr, uid, ids, c={}: ids, ['gl_entry_line'], 10),
                'tpt.posting.verification.line': (_get_order, ['debit', 'credit'], 10),}, 
           states={ 'done':[('readonly', True)]}),
        'gl_entry_line':fields.one2many('tpt.posting.verification.line','pos_ver_id','GL Entry',states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
        
    }
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state':'draft',
        'doc_type':'cus_inv',
        'name': '/',
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'posting.verification') or '/'
        new_id = super(tpt_posting_verification, self).create(cr, uid, vals, context)
        return new_id  

    def onchange_gl_entry(self, cr, uid, ids,doc_type = False, fiscal_period_id=False):
        vals = {}
        posting = []
        if doc_type and fiscal_period_id:
            type=''
            if doc_type == 'cus_inv':
                type = 'sale'  
            if doc_type == 'sup_inv':
                type = 'purchase'
            if type:
                sql = '''
                    select account_id,sum(debit) as sum_debit,sum(credit) as sum_credit from account_move_line
                    where period_id = %s and journal_id in (select id from account_journal where type='%s') group by account_id
                '''%(fiscal_period_id,type)
                cr.execute(sql)
                for posting_line in cr.dictfetchall(): 
                        sql = '''
                            select name from account_account
                            where id = %s 
                        '''%(posting_line['account_id'])
                        cr.execute(sql)
                        name = cr.dictfetchone()['name']
                        rs = {'gl_code_id':posting_line['account_id'],
                                'debit':posting_line['sum_debit'],
                                'credit':posting_line['sum_credit'],
                                'description':name,
                                }
                        posting.append((0,0,rs))
        return {'value': {'gl_entry_line':posting}   }
    
#     def write(self, cr, uid, ids, vals, context=None):
#         new_write = super(tpt_posting_verification, self).write(cr, uid,ids, vals, context)
#         for quotation in self.browse(cr,uid,ids):
#             if quotation.quotation_cate:
#                 if quotation.quotation_cate != 'multiple':
#                     if (len(quotation.purchase_quotation_line) > 1):
#                         raise osv.except_osv(_('Warning!'),_('You must choose Quotation category is multiple if you want more than one vendors!'))
#         return new_write    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
tpt_posting_verification()    
class tpt_posting_verification_line(osv.osv):
    _name = "tpt.posting.verification.line"
     
    _columns = {
        'gl_code_id': fields.many2one('account.account', 'GL Code'),
        'description':fields.char('Description', size = 1024),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
        'pos_ver_id': fields.many2one('tpt.posting.verification', 'Posting Verification'),
    }
 
    def create(self, cr, uid, vals, context=None):
        new_id = super(tpt_posting_verification_line, self).create(cr, uid, vals, context)
        if 'debit' in vals:
            if (vals['debit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Debit is not allowed as negative values'))
        if 'credit' in vals:
            if (vals['credit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Credit is not allowed as negative values'))
        return new_id    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(tpt_posting_verification_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.debit < 0:
                raise osv.except_osv(_('Warning!'),_('Debit is not allowed as negative values'))
            if line.credit < 0:
                raise osv.except_osv(_('Warning!'),_('Credit is not allowed as negative values'))
        return new_write
    
    def onchange_account_name(self, cr, uid, ids, gl_code_id=False):
        vals = {}
        if gl_code_id:
            account = self.pool.get('account.account').browse(cr, uid, gl_code_id)
            vals = {'description':account.name,
                }
        return {'value': vals}   
tpt_posting_verification_line() 

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    def _invoice(self, cursor, user, ids, name, arg, context=None):
        invoice_obj = self.pool.get('account.invoice')
        res = {}
        for line_id in ids:
            res[line_id] = False
        cursor.execute('SELECT l.id, i.id ' \
                        'FROM account_move_line l, account_invoice i ' \
                        'WHERE l.move_id = i.move_id ' \
                        'AND l.id IN %s',
                        (tuple(ids),))
        invoice_ids = []
        for line_id, invoice_id in cursor.fetchall():
            res[line_id] = invoice_id
            invoice_ids.append(invoice_id)
        invoice_names = {False: ''}
        for invoice_id, name in invoice_obj.name_get(cursor, user, invoice_ids, context=context):
            invoice_names[invoice_id] = name
        for line_id in res.keys():
            invoice_id = res[line_id]
            res[line_id] = (invoice_id, invoice_names[invoice_id])
        return res
    def _invoice_search(self, cursor, user, obj, name, args, context=None):
        if not args:
            return []
        invoice_obj = self.pool.get('account.invoice')
        i = 0
        while i < len(args):
            fargs = args[i][0].split('.', 1)
            if len(fargs) > 1:
                args[i] = (fargs[0], 'in', invoice_obj.search(cursor, user,
                    [(fargs[1], args[i][1], args[i][2])]))
                i += 1
                continue
            if isinstance(args[i][2], basestring):
                res_ids = invoice_obj.name_search(cursor, user, args[i][2], [],
                        args[i][1])
                args[i] = (args[i][0], 'in', [x[0] for x in res_ids])
            i += 1
        qu1, qu2 = [], []
        for x in args:
            if x[1] != 'in':
                if (x[2] is False) and (x[1] == '='):
                    qu1.append('(i.id IS NULL)')
                elif (x[2] is False) and (x[1] == '<>' or x[1] == '!='):
                    qu1.append('(i.id IS NOT NULL)')
                else:
                    qu1.append('(i.id %s %s)' % (x[1], '%s'))
                    qu2.append(x[2])
            elif x[1] == 'in':
                if len(x[2]) > 0:
                    qu1.append('(i.id IN (%s))' % (','.join(['%s'] * len(x[2]))))
                    qu2 += x[2]
                else:
                    qu1.append(' (False)')
        if qu1:
            qu1 = ' AND' + ' AND'.join(qu1)
        else:
            qu1 = ''
        cursor.execute('SELECT l.id ' \
                'FROM account_move_line l, account_invoice i ' \
                'WHERE l.move_id = i.move_id ' + qu1, qu2)
        res = cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]
    _columns = {
        'invoice': fields.function(_invoice, string='Invoice', store=True,
            type='many2one', relation='account.invoice', fnct_search=_invoice_search),
    }
account_move_line()