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
        'cus_inv_fright_id': fields.many2one('account.account', 'Freight Charges', states={ 'done':[('readonly', True)]}),
        'cus_inv_insurance_id': fields.many2one('account.account', 'Insurance Charges', states={ 'done':[('readonly', True)]}),
        'cus_inv_price_id': fields.many2one('account.account', 'Price Difference / Rounding', states={ 'done':[('readonly', True)]}),
        'cus_pay_bank_id': fields.many2one('account.account', 'Bank Account', states={ 'done':[('readonly', True)]}),
        'cus_pay_cash_id': fields.many2one('account.account', 'Cash Account', states={ 'done':[('readonly', True)]}),
        'sup_inv_vat_id': fields.many2one('account.account', 'VAT Receivables', states={ 'done':[('readonly', True)]}),
        'sup_inv_cst_id': fields.many2one('account.account', 'CST Receivables', states={ 'done':[('readonly', True)]}),
        'sup_inv_aed_id': fields.many2one('account.account', 'AED', states={ 'done':[('readonly', True)]}),
        'sup_inv_ed_id': fields.many2one('account.account', 'Excise Duty', states={ 'done':[('readonly', True)]}),
        'sup_inv_pf_id': fields.many2one('account.account', 'P & F Charges', states={ 'done':[('readonly', True)]}),
        'sup_inv_fright_id': fields.many2one('account.account', 'Freight Charges', states={ 'done':[('readonly', True)]}),
        'sup_inv_price_id': fields.many2one('account.account', 'Price Difference / Rounding', states={ 'done':[('readonly', True)]}),
        'sup_pay_bank_id': fields.many2one('account.account', 'Bank Account', states={ 'done':[('readonly', True)]}),
        'sup_pay_cash_id': fields.many2one('account.account', 'Cash Account', states={ 'done':[('readonly', True)]}),
        'sup_tds_id': fields.many2one('account.account', 'TDS Account', states={ 'done':[('readonly', True)]}),
        'salari_id': fields.many2one('account.account', ' Salaries and Allowances', states={ 'done':[('readonly', True)]}),
        'pfp_id': fields.many2one('account.account', 'Provident Fund Payable', states={ 'done':[('readonly', True)]}),
        'vpf_id': fields.many2one('account.account', 'VPF', states={ 'done':[('readonly', True)]}),
        'esi_id': fields.many2one('account.account', 'ESI Payable', states={ 'done':[('readonly', True)]}),
        'staff_welfare_id': fields.many2one('account.account', 'Staff Welfare Expenses', states={ 'done':[('readonly', True)]}),
        'canteen_expense_id': fields.many2one('account.account', 'Canteen Expenses', states={ 'done':[('readonly', True)]}),#TPT-BM-ON 29/10/2015
        'lic_id': fields.many2one('account.account', 'LIC-Premium-Employee', states={ 'done':[('readonly', True)]}),
        'profes_tax_id': fields.many2one('account.account', 'Profession Tax Payable', states={ 'done':[('readonly', True)]}),
        'lwf_id': fields.many2one('account.account', 'Labour welfare Fund', states={ 'done':[('readonly', True)]}),
        'staff_advance_id': fields.many2one('account.account', 'Staff Advance', states={ 'done':[('readonly', True)]}),
        'salari_payable_id': fields.many2one('account.account', 'Salaries And Allowance Payable', states={ 'done':[('readonly', True)]}),
        
        'shd_id': fields.many2one('account.account', 'SHD Allowance', states={ 'done':[('readonly', True)]}),
        'it_id': fields.many2one('account.account', 'IT Deduction', states={ 'done':[('readonly', True)]}),
        'wages_id': fields.many2one('account.account', 'Wages and Allowances', states={ 'done':[('readonly', True)]}),
        'wages_payable_id': fields.many2one('account.account', ' Wages and Allowances Payable', states={ 'done':[('readonly', True)]}),
        'other_insu': fields.many2one('account.account', 'Other Insurances', states={ 'done':[('readonly', True)]}),
        'vvti_id': fields.many2one('account.account', 'VVTi Loan', states={ 'done':[('readonly', True)]}),
        'lic_hfl_id': fields.many2one('account.account', 'LIC HFL Loan', states={ 'done':[('readonly', True)]}),
        'hdfc_id': fields.many2one('account.account', 'HDFC Loan', states={ 'done':[('readonly', True)]}),
        'tmb_id': fields.many2one('account.account', 'TMB Loan', states={ 'done':[('readonly', True)]}),
        'sbt_id': fields.many2one('account.account', 'SBT Loan', states={ 'done':[('readonly', True)]}),
        'other_loan_id': fields.many2one('account.account', 'Other Loans', states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
        
    }
    _defaults = {
        'date': time.strftime('%Y-%m-%d'),
        'state':'draft',
        'name':'cus_inv',
    }
    def _check_doc_type(self, cr, uid, ids, context=None):
        for doc_type in self.browse(cr, uid, ids, context=context):
            sql = '''
                 select id from tpt_posting_configuration where id != %s and name='%s'
             '''%(doc_type.id,doc_type.name)
            cr.execute(sql)
            code_ids = [row[0] for row in cr.fetchall()]
            if code_ids:
                raise osv.except_osv(_('Warning!'),_('Document Type has already existed !!'))
#             pro_cate_ids = self.search(cr, uid, [('id','!=',pro_cate.id),('name','=',pro_cate.name),('cate_name', '=',pro_cate.cate_name)])
#             if pro_cate_ids:
#                 raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))    
                return False
            return True
    _constraints = [
        (_check_doc_type, 'Identical Data', ['name']),
            ] 
    def bt_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    
tpt_posting_configuration()


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
                                  ('sup_inv_po', 'Supplier Invoice(With PO)'),('sup_inv', 'Supplier Invoice(Without PO)'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Payroll'),
                                  ('grn', 'GRN'),
                                  ('good', 'Good Issue'),
                                  ('do', 'DO'),
                                  ('inventory', 'Inventory Transfer'),
                                  ('manual', 'Manual Journal'),
                                  ('cash_pay', 'Cash Payment'),
                                  ('cash_rec', 'Cash Receipt'),
                                  ('bank_pay', 'Bank Payment'),
                                  ('bank_rec', 'Bank Receipt'),
                                  ('product', 'Production'),],'Document Type', states={ 'done':[('readonly', True)]}),
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
#             type=''
#             type_inv=''
#             if doc_type == 'cus_inv':
#                 type = 'sale'  
#             if doc_type == 'sup_inv':
#                 type = 'purchase'
#             if type:
#                 sql = '''
#                     select account_id,sum(debit) as sum_debit,sum(credit) as sum_credit from account_move_line
#                     where period_id = %s and journal_id in (select id from account_journal where type='%s') group by account_id
#                 '''%(fiscal_period_id,type)
#                 cr.execute(sql)
#                 for posting_line in cr.dictfetchall(): 
#                         sql = '''
#                             select name from account_account
#                             where id = %s 
#                         '''%(posting_line['account_id'])
#                         cr.execute(sql)
#                         name = cr.dictfetchone()['name']
#                         rs = {'gl_code_id':posting_line['account_id'],
#                                 'debit':posting_line['sum_debit'],
#                                 'credit':posting_line['sum_credit'],
#                                 'description':name,
#                                 }
#                         posting.append((0,0,rs))
#             if doc_type == 'cus_pay':
#                 type_inv = 'out_invoice'  
#             if doc_type == 'sup_pay':
#                 type_inv = 'in_invoice'
#             if type_inv:
#                 sql = '''
#                     select account_id,sum(debit) as sum_debit,sum(credit) as sum_credit from account_move_line
#                      where journal_id in (select id from account_journal where type in ('cash','bank'))
#                      and period_id=%s and invoice in (select id from account_invoice where type='%s')
#                      group by account_id 
#                 '''%(fiscal_period_id,type_inv)
#                 cr.execute(sql)
#                 for posting_line in cr.dictfetchall(): 
#                         sql = '''
#                             select name from account_account
#                             where id = %s 
#                         '''%(posting_line['account_id'])
#                         cr.execute(sql)
#                         name = cr.dictfetchone()['name']
#                         rs = {'gl_code_id':posting_line['account_id'],
#                                 'debit':posting_line['sum_debit'],
#                                 'credit':posting_line['sum_credit'],
#                                 'description':name,
#                                 }
#                         posting.append((0,0,rs))
# #             if doc_type == 'payroll':
# #                 type = 'payroll'
            sql = '''
                    select account_id,sum(debit) as sum_debit,sum(credit) as sum_credit from account_move_line
                     where move_id in (select id from account_move where doc_type ='%s'and period_id=%s and state='draft' )
                     group by account_id 
            '''%(doc_type,fiscal_period_id)
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
        for line in self.browse(cr,uid,ids):
            sql = '''
                select id from tpt_posting_verification_line where pos_ver_id =%s 
            '''%(line.id)
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            self.pool.get('account.move').post(cr,uid,journal_ids)
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
        'doc_type': fields.related('move_id', 'doc_type', type="selection", store=True,
                selection=[('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv_po', 'Supplier Invoice(With PO)'),('sup_inv', 'Supplier Invoice(Without PO)'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Executives Payroll'),
                                  ('grn', 'GRN'),
                                  ('good', 'Good Issue'),
                                  ('do', 'DO'),
                                  ('inventory', 'Inventory Transfer'),
                                  ('manual', 'Manual Journal'),
                                  ('cash_pay', 'Cash Payment'),
                                  ('cash_rec', 'Cash Receipt'),
                                  ('bank_pay', 'Bank Payment'),
                                  ('bank_rec', 'Bank Receipt'),
                                  ('ser_inv', 'Service Invoice'),
                                  ('product', 'Production'),
                                  ('staff_payroll', 'Staff Payroll'),
                                  ('freight', 'Freight Invoice'),
                                  ('worker_payroll', 'Workers Payroll'),
                                  ('stock_adj_inc', 'Stock Adjustment Increase'),
                                  ('stock_adj_dec', 'Stock Adjustment Decrease'),
                                  ('return_do', 'Return DO'),
                                  ('asset_dp', 'Asset Depreciation'),#TPT-BM- ON13/08/2016
                                  ], string="Document Type", readonly=True, select=True),
        #vsis selected grn from pop-up Create invoice
        'tpt_grn_id': fields.many2one('stock.picking', 'GRN'),
        'tpt_grn_line_id': fields.many2one('stock.move', 'GRN line'),
    }
    
    def create(self, cr, uid, vals, context=None):
        return super(account_move_line, self).create(cr,1, vals, context)
    
    def write(self, cr, uid,ids, vals, context=None, check=False):
        return super(account_move_line, self).write(cr,1,ids,vals,context,check) 
account_move_line()

class stock_location(osv.osv):
    _inherit = "stock.location"
    _columns = {
        'gl_pos_verification_id': fields.many2one('account.account', 'Account Warehouse'),
        }
stock_location()
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
#         if context.get('search_grn_no_id'):
#             locat_obj = self.pool.get('stock.location')
#             parent_ids = locat_obj.search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
#             locat_ids = locat_obj.search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
#             location_id = locat_ids[0]
#                 
#             parent_dest_ids = locat_obj.search(cr, uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
#             location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_dest_ids[0])])
#             location_dest_id = location_dest_ids[0]
#             sql = '''
#                 select name from tpt_quanlity_inspection where state = 'done' and id in (select inspec_id from stock_move where location_id = %s and location_dest_id = %s)
#             '''%(location_id, location_dest_id)
#             cr.execute(sql)
#             picking_ids = [row[0] for row in cr.fetchall()]
#             args += [('id','in',picking_ids)]
            
        if context.get('search_grn_with_name', False):
            name = context.get('name')
            grn_ids = self.search(cr, uid, [('name','ilike',name)])
            args += [('id','in',grn_ids)]
        return super(stock_picking_in, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_grn_with_name':1,'name':name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    def write(self, cr, uid,ids, vals, context=None):
        return super(stock_picking_in, self).write(cr,1,ids,vals,context) 


    
stock_picking_in() 

# class stock_move(osv.osv):
#     _inherit = "stock.move"
#      
#     def init(self, cr):
#         sql = '''
#             select id from stock_move where picking_id is null and inspec_id is null and issue_id is null and production_id is null and id not in (select move_id from mrp_production_move_ids)
#                 and id not in (select child_id from stock_move_history_ids) and id not in (select move_id from stock_inventory_move_rel) and move_dest_id is null and purchase_line_id is null 
#                 and sale_line_id is null and tracking_id is null and prodlot_id is null
#         '''
#         cr.execute(sql)
#         move_ids = [r[0] for r in cr.fetchall()]
#         self.pool.get('stock.move').unlink(cr, 1, move_ids)
#          
#          
# stock_move()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def get_pro_account_id(self,cr,uid,name,channel):
        account = False
        account_obj = self.pool.get('account.account')
        if name and channel:
            product_name = name.strip()
            dis_channel = channel.strip()
            account_ids = []
            if dis_channel in ['VVTi Domestic','VVTI Domestic']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810001')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810031')])
            if dis_channel in ['VVTi Direct Export','VVTI Direct Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810003')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810032')])
            if dis_channel in ['VVTi Indirect Export','VVTI Indirect Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810004')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810033')])
            if account_ids:
                account = account_ids[0]
        return account
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_picking, self).write(cr, 1,ids, vals, context)
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        #TPT START - By P.VINOTHKUMAR - ON 11/04/2015 - FOR (Generate document sequence for DO Account postings)
        sql = '''
        select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        else:
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.do.import')
        vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        name=vals['name'] 
        # TPT END
        for line in self.browse(cr,uid,ids):
            if 'state' in vals and line.type == 'in' and line.state=='done':
                debit = 0.0
                credit = 0.0
                journal_line = []
                for move in line.move_lines:
                    #TPT-SSR on 03/02/2017-Trial Balance Issue
                     if context is None:
                        context = {}        
                     context.update({'date': time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
                     currency = move.purchase_line_id.order_id.currency_id.name or False
                     currency_id = move.purchase_line_id.order_id.currency_id.id or False
                     amount_inr = round(move.purchase_line_id.price_unit,2)
                     if currency_id:
                        if currency != 'INR':
                            if not move.date:
                                raise osv.except_osv(_('Warning!'),_('Please choose date of invoice!')) 
                            cur_rate_obj =self.pool.get('res.currency.rate')
                            cur_rate_ids = cur_rate_obj.search(cr, uid, [('currency_id','=',currency_id),('name','=',move.date)])
                            if not cur_rate_ids:
                                raise osv.except_osv(_('Warning!'),_('Rate of currency is not defined on %s!'%move.date)) 
                            else:
                                cur_rate_ids1 = cur_rate_obj.search(cr, uid, [('currency_id','=',currency_id),('name','=',move.date), ('rate_type', '=', 'selling')])
                                if not cur_rate_ids1:
                                    raise osv.except_osv(_('Warning!'),_('Selling Rate of Currency is not defined on %s!'%move.date))
                     else:
                            raise osv.except_osv(_('Warning!'),_('Please check again! Do not have currency for this Picking order!'))                                                     
                     
                     if currency and currency != 'INR':
                        amount_inr = round(move.purchase_line_id.price_unit,2)
                        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=context)['rate']
                        amount_inr = amount_inr/voucher_rate                     
                     amount = amount_inr * move.product_qty
                     ##
                     #amount = move.purchase_line_id.price_unit * move.product_qty
                     debit += amount - (amount*move.purchase_line_id.discount)/100
                date_period = line.date,
                sql = '''
                    select id from account_period where special = False and '%s' between date_start and date_stop and special is False
                 
                '''%(date_period)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
#                 a = self.browse(cr,uid,period_ids[0])
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                 
                sql_journal = '''
                    select id from account_journal where name='Stock Journal' or code='STJ'
                '''
                cr.execute(sql_journal)
                journal_ids = [r[0] for r in cr.fetchall()]
                if not journal_ids:
                    raise osv.except_osv(_('Warning!'),_('Please config Journal "Stock Journal"!'))
                journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                ##
                #TPT START - By P.VINOTHKUMAR - ON 12/04/2015 - FOR (Generate document sequence for GRN Account postings)
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'grn.posting.account')
                vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                name=vals['name'] 
                #TPT END
                ##
#                     if not line.warehouse.gl_pos_verification_id:
#                         raise osv.except_osv(_('Warning!'),_('Account Warehouse is not null, please configure it in Warehouse Location master !'))
            #sinh but toan
#                     journal_line = [(0,0,{
#                                         'name':line.name, 
#                                         'account_id': line.warehouse.gl_pos_verification_id and line.warehouse.gl_pos_verification_id.id,
#                                         'partner_id': line.partner_id and line.partner_id.id,
#                                         'debit':debit,
#                                         'credit':0,
#                                          
#                                        })]
                temp_flag = False
                for p in line.move_lines:
                    #TPT-SSR on 03/02/2017-Trial Balance Issue
                    amount_cer = amount_inr * p.product_qty                    
                    #amount_cer = p.purchase_line_id.price_unit * p.product_qty
                    credit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                    debit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100                    
                    #TPT-Start:  By BalamuruganPurushothaman - ON 24/12/2015
                    if p.purchase_line_id and p.purchase_line_id.taxes_id:
                        description = [r.description for r in p.purchase_line_id.taxes_id]
                        tax_amounts = [r.amount for r in p.purchase_line_id.taxes_id]
                        tax_amt = 0
                        if description:
                            description = description[0]
                            if 'CST' in description :
                                for tax in tax_amounts:
                                    tax_amt = tax
                                pf_type = p.purchase_line_id.p_f_type
                                pf = p.purchase_line_id.p_f
                                ed_type = p.purchase_line_id.ed_type
                                ed = p.purchase_line_id.ed
                                excise_duty = 0.00
                                #TPT-SSR on 03/02/2017-Trial Balance Issue
                                basic = (p.purchase_line_id.product_qty * amount_inr) - ( (p.purchase_line_id.product_qty * amount_inr)*p.purchase_line_id.discount/100)
                                #basic = (p.purchase_line_id.product_qty * p.purchase_line_id.price_unit) - ( (p.purchase_line_id.product_qty * p.purchase_line_id.price_unit)*p.purchase_line_id.discount/100)
                                if pf_type == '1' :
                                    p_f = basic * pf/100
                                elif pf_type == '2' :
                                    p_f = pf
                                elif pf_type == '3':
                                    p_f = pf * p.purchase_line_id.product_qty
                                else:
                                    p_f = pf                                
                                if ed_type == '1' :
                                    ed = (basic + p_f) * ed/100
                                elif ed_type == '2' :
                                    ed = ed
                                elif ed_type == '3' :
                                    ed = ed *  p.purchase_line_id.product_qty
                                else:
                                    ed = ed
                                excise_duty += ed
                                #credit += excise_duty
                                cst_cr_amt = (credit + excise_duty + p_f)*tax_amt/100    
                                cst_dr_amt = (debit + excise_duty + p_f)*tax_amt/100                                
                                #credit += cst_cr_amt# TPT-BM-Rollback-CST value will be added into Product Asset Account During Supplier Invoice Posting- ON 24/08/2016
                                #debit += cst_dr_amt# TPT-BM-Rollback "" - ON 24/08/2016
                    #TPT-End
                    if p.action_taken!='need':
                        temp_flag = True
                        if not p.product_id.product_asset_acc_id:
                            raise osv.except_osv(_('Warning!'),_('You need to define Product Asset GL Account for this product'))
                        journal_line.append((0,0,{
                            'name':line.name + ' - ' + p.product_id.name, 
                            'account_id': p.product_id.product_asset_acc_id and p.product_id.product_asset_acc_id.id,
                            'partner_id': line.partner_id and line.partner_id.id or False,
                            'credit':0,
                            'debit':debit,
                            'product_id':p.product_id.id,
                        }))
                        
                        if not p.product_id.purchase_acc_id:
                            raise osv.except_osv(_('Warning!'),_('You need to define Purchase GL Account for this product'))
                        journal_line.append((0,0,{
                            'name':line.name + ' - ' + p.product_id.name, 
                            'account_id': p.product_id.purchase_acc_id and p.product_id.purchase_acc_id.id,
                            'partner_id': line.partner_id and line.partner_id.id or False,
                            'credit':credit,
                            'debit':0,
                            'product_id':p.product_id.id,
                        }))
                    #
                     
                value={
                    'journal_id':journal.id,
                    'period_id':period_ids[0] ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type':'grn',
                    'grn_id':line.id,
                    'ref': line.name,
                    'name':name, # added by P.VINOTHKUMAR ON 08/04/2016
                    }
                if temp_flag is True:
                    new_jour_id = account_move_obj.create(cr,uid,value)
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id.grn:
                            try:
                                account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                            except:
                                pass
            if 'state' in vals and line.type == 'out' and line.state=='done':
                debit = 0.0
#                 so_id = line.sale_id and line.sale_id.id or False
                dis_channel = line.sale_id and line.sale_id.distribution_channel and line.sale_id.distribution_channel.name or False
                date_period = line.date
                account = False
                asset_id = False
                
                sql_journal = '''
                    select id from account_journal where name='Stock Journal' or code='STJ'
                '''
                cr.execute(sql_journal)
                journal_ids = [r[0] for r in cr.fetchall()]
                if not journal_ids:
                    raise osv.except_osv(_('Warning!'),_('Please config Journal "Stock Journal"!'))
                journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                sql = '''
                    select id from account_period where special = False and '%s' between date_start and date_stop and special is False
                  
                '''%(date_period)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                journal_line = []
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                #sinh but toan
                for p in line.move_lines:
                    if p.prodlot_id:
                        sale_id = p.sale_line_id and p.sale_line_id.order_id.id or False 
                        used_qty = p.product_qty or 0
                        if sale_id:
                            sql = '''
                                select id from tpt_batch_allotment where sale_order_id = %s and state='confirm'
                            '''%(sale_id) #TPT-By BalamuruganPurushothaman ON 29/07/2015 - TO TAKE CONFIRMED "BATCH ALLOTMENT" ONLY - SQL state='confirm is appended'
                            cr.execute(sql)
                            allot_ids = cr.dictfetchone()
                            if allot_ids:
                                allot_id = allot_ids['id']
                                sql = '''
                                select id from tpt_batch_allotment_line where sys_batch = %s and batch_allotment_id = %s
                                '''%(p.prodlot_id.id,allot_id)
                                cr.execute(sql)
                                allot_line_id = cr.dictfetchone()['id']
                                line_id = self.pool.get('tpt.batch.allotment.line').browse(cr, uid, allot_line_id)
                                used_qty += line_id.used_qty
                                sql = '''
                                    update tpt_batch_allotment_line set product_uom_qty = %s where id = %s
                                '''%(used_qty,allot_line_id)
                                cr.execute(sql)
                                if line_id.product_uom_qty == line_id.used_qty:
                                    sql = '''
                                        update tpt_batch_allotment_line set is_deliver = 't' where id = %s
                                    '''%(allot_line_id)
                                    cr.execute(sql)
                    
                    #TPT START By BalamuruganPurushothaman ON 28/07/2015 - TO SET COST PRICE OF FINISHED PRODUCT IN JOURNAL POSTING INSTEAD OF SALES PROCE WHILE DO CONFIRM PROCESS
                    #debit += p.sale_line_id and p.sale_line_id.price_unit * p.product_qty or 0  ##TPT COMMENTED
                    product = self.pool.get('product.product').browse(cr, uid, p.product_id.id)
                    debit += product.standard_price and product.standard_price * p.product_qty or 0
                    #TPT END
                    
                    #product_name = p.product_id.name    # TPT - COMMENTED By BalamuruganPurushothaman ON 20/06/2015 
                    product_name = p.product_id.default_code # TPT - Added By BalamuruganPurushothaman ON 20/06/2015 fto get GL code with respect to Product Code
                    product_id = p.product_id.id
                    #account = self.get_pro_account_id(cr,uid,product_name,dis_channel)
                    account = p.product_id.product_cose_acc_id.id
                    if not account:
#                             raise osv.except_osv(_('Warning!'),_('Account is not created for this Distribution Channel! Please check it!'))
                        if p.product_id.product_cose_acc_id:
                            account = p.product_id.product_cose_acc_id.id
                        else: 
                            raise osv.except_osv(_('Warning!'),_('Product Cost of Goods Sold Account is not configured! Please configured it!'))
                     
                    if p.product_id.product_asset_acc_id:
                        asset_id = p.product_id.product_asset_acc_id.id
                    else:
                        raise osv.except_osv(_('Warning!'),_('Product Asset Account is not configured! Please configured it!'))
                #
                doc_type = ''
                if line.document_type=='return_do': #TPT-BM-30/06/2016 - FOR RETURN
                    sql_journal = '''
                        select id from account_journal where name='Sales Refund Journal' or code='SCNJ'
                    '''
                    cr.execute(sql_journal)
                    journal_ids = [r[0] for r in cr.fetchall()]
                    if not journal_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Journal "Sales Refund Journal"!'))
                    journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                    
                    journal_line.append((0,0,{
                                'name':line.name, 
                                'account_id': account,
                                'partner_id': line.partner_id and line.partner_id.id,
                                'credit':debit,
                                'debit':0,
                                'product_id':product_id,
                            }))
                      
                    journal_line.append((0,0,{
                        'name':line.name, 
                        'account_id': asset_id,
                        'partner_id': line.partner_id and line.partner_id.id,
                        'credit':0,
                        'debit':debit,
                        'product_id':product_id,
                        }))
                    doc_type = 'return_do'
                else:
                    sql_journal = '''
                        select id from account_journal where name='Stock Journal' or code='STJ'
                    '''
                    cr.execute(sql_journal)
                    journal_ids = [r[0] for r in cr.fetchall()]
                    if not journal_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Journal "Stock Journal"!'))
                    journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                    
                    journal_line.append((0,0,{
                                'name':line.name, 
                                'account_id': account,
                                'partner_id': line.partner_id and line.partner_id.id,
                                'credit':0,
                                'debit':debit,
                                'product_id':product_id,
                            }))
                     
                    journal_line.append((0,0,{
                        'name':line.name, 
                        'account_id': asset_id,
                        'partner_id': line.partner_id and line.partner_id.id,
                        'credit':debit,
                        'debit':0,
                        'product_id':product_id,
                        }))
                    doc_type = 'do'
                #      
                value={
                    'journal_id':journal.id,
                    'period_id':period_ids[0] ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type': doc_type or '',
                    'ref': line.name,
                    'name':name, # added by P.VINOTHKUMAR ON 08/04/2016
                    }
                exist_ids = account_move_obj.search(cr, uid, [('ref', '=', line.name)])
                if not exist_ids: #TPT-BM-01/07/2016 - FOR RETURN DO GL POSTING
                    new_jour_id = account_move_obj.create(cr,uid,value)
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id.delivery_order:
                            try:
                                account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                            except:
                                pass  
#                     if so_id:
#                         sql = '''
#                         update sale_order set journal_flag = True where id = %s
#                         '''%(so_id)
#                         cr.execute(sql)
        return new_write
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_grn_with_name', False):
            name = context.get('name')
            grn_ids = self.search(cr, uid, [('name','ilike',name)])
            args += [('id','in',grn_ids)]
        return super(stock_picking, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_grn_with_name':1,'name':name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
        
stock_picking()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def get_button_ed(self, cr, uid, ids, name, args, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = False
            if invoice.purchase_id:
                for invoice_line in invoice.invoice_line:
                    if invoice_line.ed or invoice_line.aed_id_1:
                        result[invoice.id] = True
                        break
        return result
                
    _columns = {
        'bill_number': fields.char('Bill Number', size=1024),
        'bill_date': fields.date('Bill Date'),
        'cost_center_id':fields.many2one('tpt.cost.center','Cost Center'),
#         'flag_bt_ed': fields.boolean('button ed'),
        'flag_bt_ed': fields.function(get_button_ed, string='button ed', type='boolean'),
#         'doc_type':fields.selection([('supplier_invoice','Supplier Invoice'),
#                                      ('supplier_invoice_without','Supplier Invoice (Without PO)'),
#                                      ('service_invoice','Service Invoice'),
#                                      ('freight_invoice','Freight Invoice')
#                                      ],('Doc Type')),

        # VSIS new one2many grn
        'tpt_grn_line': fields.one2many('stock.picking','tpt_invoice_id','GRN Line'),
    }
    
    def bt_post_ed(self, cr, uid, ids, context=None):
        for post in self.browse(cr,uid,ids):
            sql = '''
                select id from tpt_ed_invoice_positing where invoice_id = %s and state != 'cancel'
            '''%(post.id)
            cr.execute(sql)
            ed_invoice_ids = cr.dictfetchall()
            if ed_invoice_ids:
                raise osv.except_osv(_('Warning!'),_('You have already created ED Posting!'))
            else:
                res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'green_erp_arulmani_accounting', 'ed_type_form_view')
                return {
                            'name': 'Post ED',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'view_id': res[1],
                            'res_model': 'ed.type.pop.up',
                            'domain': [],
                            'context': {'default_message':'Please Choose ED Type', 'default_invoice_id':ids[0]},
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                        }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_sup_inv_id'):
            sql = '''
                select id from account_invoice where type = 'in_invoice' and grn_no is not null and state != 'draft'
            '''
            cr.execute(sql)
            invoice_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',invoice_ids)]
        return super(account_invoice, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
      
    def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id
        if not inv.tax_line:
            for tax in compute_taxes.values():
                ait_obj.create(cr, uid, tax)
#         else:
#             tax_key = []
#             for tax in inv.tax_line:
#                 if tax.manual:
#                     continue
#                 key = (tax.tax_code_id.id, tax.base_code_id.id, tax.account_id.id, tax.account_analytic_id.id)
#                 tax_key.append(key)
#                 if not key in compute_taxes:
#                     raise osv.except_osv(_('Warning!'), _('Global taxes defined, but they are not in invoice lines !'))
#                 base = compute_taxes[key]['base']
#                 if abs(base - tax.base) > company_currency.rounding:
#                     raise osv.except_osv(_('Warning!'), _('Tax base different!\nClick on compute to update the tax base.'))
#             for key in compute_taxes:
#                 if not key in tax_key:
#                     raise osv.except_osv(_('Warning!'), _('Taxes are missing!\nClick on compute button.'))

    def onchange_sup_inv_id(self, cr, uid, ids,sup_inv_id=False, context=None):
        vals = {}
        if sup_inv_id:
            for invoice_id in self.browse(cr, uid, ids):
                sql = '''
                    delete from account_invoice_line where invoice_id = %s
                '''%(invoice_id.id)
                cr.execute(sql)
            freight_line = []
            invoice = self.pool.get('account.invoice').browse(cr, uid, sup_inv_id)
            for line in invoice.invoice_line:
                invoice_line_tax_ids = [t.id for t in line.invoice_line_tax_id]
                rs = {
                      'product_id': line.product_id and line.product_id.id or False,
                      'name': line.name,
                      'quantity': line.quantity,
                      'uos_id': line.uos_id and line.uos_id.id or False,
                      'price_unit': line.price_unit or False,
#                       'disc': line.disc or False,
#                       'p_f': line.p_f or False,
#                       'p_f_type':line.p_f_type or False,
                        'fright': line.fright,
                        'fright_type': line.fright_type,
    #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                      'invoice_line_tax_id': [(6,0,invoice_line_tax_ids)],
                      'line_net': line.line_net or False,
                      'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                  }
                freight_line.append((0,0,rs))
            vals = {
                'amount_untaxed':invoice.amount_untaxed or False,
                'p_f_charge':invoice.p_f_charge or False,
                'amount_tax': invoice.amount_tax or False,
                'invoice_line': freight_line,
                }
        return {'value': vals}

    def onchange_purchase_id(self, cr, uid, ids,purchase_id=False, context=None):
        vals = {}
        if purchase_id:
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from account_invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql)
        service_line = []
        purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        vendor = purchase.partner_id.tds_id.id
        for line in purchase.order_line:
            taxes_ids = [t.id for t in line.taxes_id]
            if purchase.po_document_type == 'service':
                sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                '''%(purchase_id, line.id)
                cr.execute(sql)
                quantity = cr.dictfetchone()['quantity']
#                 if line.product_qty > quantity:
#                     rs = {
#                           'product_id': line.product_id and line.product_id.id or False,
#                           'name': line.description,
#                           'quantity': line.product_qty - quantity or False,
#                           'uos_id': line.product_uom and line.product_uom.id or False,
#                           'price_unit': line.price_unit or False,
#                           'disc': line.discount or False,
#                           'p_f': line.p_f or False,
#                           'p_f_type':line.p_f_type or False,
#                           'ed':line.ed or False,
#                           'ed_type':line.ed_type or False,
#         #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
#                           'taxe_id': taxes_ids[0],
#                           'invoice_line_tax_id': [(6,0,taxes_ids)],
#                           'fright':line.fright or False,
#                           'fright_type':line.fright_type or False,
#                           'line_net': line.line_net or False,
#                           'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
#                           'po_line_id': line.id,
#                           'tds_id': vendor or False,
#                       }
#                     service_line.append((0,0,rs))
            if purchase.po_document_type == 'service_qty':
                vals['doc_type']='service_invoice_qty'
                sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                '''%(purchase_id, line.id)
                cr.execute(sql)
                quantity = cr.dictfetchone()['quantity']
                if line.product_qty > quantity:
                    rs = {
                          'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,
        #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                          'taxe_id': taxes_ids[0],
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'po_line_id': line.id,
                          'tds_id': vendor or False,
                      }
                    service_line.append((0,0,rs))
            else:
                rs = {
                      'product_id': line.product_id and line.product_id.id or False,
                      'name': line.description,
                      'quantity': line.product_qty or False,
                      'uos_id': line.product_uom and line.product_uom.id or False,
                      'price_unit': line.price_unit or False,
                      'disc': line.discount or False,
                      'p_f': line.p_f or False,
                      'p_f_type':line.p_f_type or False,
                      'ed':line.ed or False,
                      'ed_type':line.ed_type or False,
    #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                      'taxe_id': taxes_ids[0],
                      'invoice_line_tax_id': [(6,0,taxes_ids)],
                      'fright':line.fright or False,
                      'fright_type':line.fright_type or False,
                      'line_net': line.line_net or False,
                      'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                      'tds_id': vendor or False,
                      }
                service_line.append((0,0,rs))
        vals.update({
                'partner_id':purchase.partner_id and purchase.partner_id.id or False,
                'vendor_ref':purchase.partner_ref or False,
                'invoice_line': service_line,
                'currency_id':purchase.currency_id and purchase.currency_id.id or False,
                #'account_id':416
                })
        return {'value': vals}
    def onchange_service_purchase_id(self, cr, uid, ids,purchase_id=False, context=None):
        vals = {}
        if purchase_id:
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from account_invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql)
        service_line = []
        purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        vendor = purchase.partner_id.tds_id.id
        for line in purchase.order_line:
            taxes_ids = [t.id for t in line.taxes_id]
            if purchase.po_document_type == 'service':
                sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                '''%(purchase_id, line.id)
                cr.execute(sql)
                quantity = cr.dictfetchone()['quantity']
                if line.product_qty > quantity:
                    rs = {
                          'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,
        #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                          'taxe_id': taxes_ids[0],
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'po_line_id': line.id,
                          'tds_id': vendor or False,
                      }
                    service_line.append((0,0,rs))
            if purchase.po_document_type == 'service_qty':
                vals['doc_type']='service_invoice_qty'
                sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                '''%(purchase_id, line.id)
                cr.execute(sql)
                quantity = cr.dictfetchone()['quantity']
                if line.product_qty > quantity:
                    rs = {
                          'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,
        #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                          'taxe_id': taxes_ids[0],
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'po_line_id': line.id,
                          'tds_id': vendor or False,
                      }
                    service_line.append((0,0,rs))
            else:
                rs = {
                      'product_id': line.product_id and line.product_id.id or False,
                      'name': line.description,
                      'quantity': line.product_qty or False,
                      'uos_id': line.product_uom and line.product_uom.id or False,
                      'price_unit': line.price_unit or False,
                      'disc': line.discount or False,
                      'p_f': line.p_f or False,
                      'p_f_type':line.p_f_type or False,
                      'ed':line.ed or False,
                      'ed_type':line.ed_type or False,
    #                   'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                      'taxe_id': taxes_ids[0],
                      'invoice_line_tax_id': [(6,0,taxes_ids)],
                      'fright':line.fright or False,
                      'fright_type':line.fright_type or False,
                      'line_net': line.line_net or False,
                      'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                      'tds_id': vendor or False,
                      }
                service_line.append((0,0,rs))
        vals.update({
                'partner_id':purchase.partner_id and purchase.partner_id.id or False,
                'vendor_ref':purchase.partner_ref or False,
                #'invoice_line': service_line,
                'currency_id':purchase.currency_id and purchase.currency_id.id or False,
                #'account_id':416
                })
        return {'value': vals}
    def onchange_service_tds(self, cr, uid, ids, is_tds_applicable, purchase_id, context=None):
        vals = {}     
        if purchase_id:
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from account_invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql)   
        service_line = []
        purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        vendor = purchase.partner_id.tds_id.id
        
        for line in purchase.order_line: 
            taxes_ids = [t.id for t in line.taxes_id]
            sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                '''%(purchase_id, line.id)
            cr.execute(sql)
            quantity = cr.dictfetchone()['quantity']
            if is_tds_applicable is False:                  
                if line.product_qty > quantity:                         
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': False,}
                else:
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': False,}
            elif is_tds_applicable is True:               
                if line.product_qty > quantity:                         
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': vendor or False,}
                else:
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': vendor or False,}
            #set line here    
            service_line.append((0,0,rs))   
            #
        ##END FOR                                    
        vals = {   
                'invoice_line': service_line,
                }
        return {'value': vals}
    def onchange_without_po_tds(self, cr, uid, ids, is_tds_applicable, context=None):
        vals = {}        
        if purchase_id:
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from account_invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql) 
        service_line = []
        purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
        vendor = purchase.partner_id.tds_id.id
        
        for line in purchase.order_line: 
            taxes_ids = [t.id for t in line.taxes_id]
            sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                '''%(purchase_id, line.id)
            cr.execute(sql)
            quantity = cr.dictfetchone()['quantity']
            if is_tds_applicable is False:                  
                if line.product_qty > quantity:                         
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': False,}
                else:
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': False,}
            elif is_tds_applicable is True:               
                if line.product_qty > quantity:                         
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty - quantity or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': vendor or False,}
                else:
                    rs={'product_id': line.product_id and line.product_id.id or False,
                          'name': line.description,
                          'quantity': line.product_qty or False,
                          'uos_id': line.product_uom and line.product_uom.id or False,
                          'price_unit': line.price_unit or False,
                          'disc': line.discount or False,
                          'p_f': line.p_f or False,
                          'p_f_type':line.p_f_type or False,
                          'ed':line.ed or False,
                          'ed_type':line.ed_type or False,   
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'tds_id': vendor or False,}
            #set line here    
            service_line.append((0,0,rs))   
            #
        ##END FOR                                    
        vals = {   
                'invoice_line': service_line,
                }
        return {'value': vals}
    def create(self, cr, uid, vals, context=None):
        sql = '''
        select code from account_fiscalyear where '%s' between date_start and date_stop
       '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        if vals.get('type','')=='in_invoice' and 'purchase_id' in vals and 'sup_inv_id' not in vals:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
#             vals['doc_type']='service_invoice'
             #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
            # vsis check context to generate seq for supplier invoice
            if context is None:
                context = {}
            if not context.get('not_gen_seq_inv',False):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
            else:
                vals['name'] =  'Draft'
           #TPT END
        if vals.get('type','')=='in_invoice' and 'purchase_id' in vals and 'vendor_ref' in vals and 'sup_inv_id' not in vals:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
#             vals['doc_type']='service_invoice'
             #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
             sequence = self.pool.get('ir.sequence').get(cr, uid, 'service.invoice') or '/'
             vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
             if context.get('default_doc_type', False)=='service_invoice_qty':
                vals['doc_type']='service_invoice_qty'   
             if context.get('default_doc_type', False)=='service_invoice_amt':
                vals['doc_type']='service_invoice_amt'
           #TPT END   
           
        if vals.get('type','')=='in_invoice' and 'purchase_id' not in vals and 'sup_inv_id' not in vals:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
#             vals['doc_type']='supplier_invoice_without'
              #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
              if 'doc_type' in vals:
                  if vals.get('name','/')=='/':
                      sequence = self.pool.get('ir.sequence').get(cr, uid, 'sup.invoice.not.po') or '/'
                      vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                      #TPT END

        if vals.get('type','')=='in_invoice' and 'sup_inv_id' in vals and vals['sup_inv_id']:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.si.freight.sequence') or '/'
#             vals['doc_type']='freight_invoice'
              #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
              if vals.get('name','/')=='/':
                  sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.si.freight.sequence') or '/'
                  vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                      #TPT END
              for seq,line in enumerate(self.browse(cr, uid, vals['sup_inv_id']).invoice_line):
                bp_obj = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
                vals['invoice_line'][seq][2].update({
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'uos_id': line.uos_id.id,
                    'price_unit': line.price_unit,
                    'tds_id_2': bp_obj and bp_obj.tds_id and  bp_obj.tds_id.id or False #TPT-BalamuruganPurushothaman-30/11/2015 - Ticket No: 3151
                })
                    
        new_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        new = self.browse(cr,uid,new_id)
        if new.purchase_id.po_document_type == 'service':
            ##TPT START BY BALAMURUGAN PURUSHOTHMAN ON 15/10/2015 - TO LOAD VENDOR TDS IN SERVICE INVOICE LINE
            #===================================================================
            # for invoice_line in new.invoice_line:
            #     sql = '''
            #     update account_invoice_line set tds_id=%s where id=%s
            #     '''%(new.partner_id.tds_id.id, invoice_line.id)
            #     cr.execute(sql)
            #===================================================================
            #TPT END    
            for purchase_line in new.purchase_id.order_line:
                sql = '''
                        select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                    '''%(new.purchase_id.id, purchase_line.id)
                cr.execute(sql)
                quantity = cr.dictfetchone()['quantity']
                 
                sql = '''
                        select product_qty from purchase_order_line where order_id in (select id from purchase_order where id = %s) and id = %s
                    '''%(new.purchase_id.id, purchase_line.id)
                cr.execute(sql)
                product_qty = cr.dictfetchone()['product_qty']
                if quantity == product_qty:
                    sql = '''
                        update purchase_order_line set flag_line = 't' where id = %s and id = %s
                    '''%(purchase_line.id, purchase_line.id)
                    cr.execute(sql)
                elif quantity<product_qty:
                    sql = '''
                        update purchase_order_line set flag_line = 'f' where id = %s and id = %s
                    '''%(purchase_line.id, purchase_line.id)
                    cr.execute(sql)
                else:
                    raise osv.except_osv(_('Error!'), _('Quantity in Account Invoice is not more than quantity in Purchase Order'))
            sql = '''
                select id from purchase_order_line where flag_line = 'f' and order_id = %s
            '''%(new.purchase_id.id)
            cr.execute(sql)
            purchase_orders = [row[0] for row in cr.fetchall()]
            if purchase_orders: 
# con so luong doi voi purchase order do
                sql = '''
                        update purchase_order set flag = 'f' where id = %s
                    '''%(new.purchase_id.id)
                cr.execute(sql)
            else:
# khong con so luong doi voi purchase order do
                sql = '''
                        update purchase_order set flag = 't' where id = %s
                    '''%(new.purchase_id.id)
                cr.execute(sql)
                
            #TPT START BY RAKESHKUMAR on 03-02-2016 FOR SAME LINE ITEMS APPEARING AGAIN IN SERVICE INVOICE
            po_qty = 0
            inv_qty = 0            
            for purchase_line in new.purchase_id.order_line:
                po_qty += purchase_line.product_qty
            for invoice_line in new.invoice_line:
                inv_qty += invoice_line.quantity
            if po_qty == inv_qty:
               sql = '''
                    update purchase_order set state = 'invoice_raised' where id = %s
                '''%(new.purchase_id.id)
               cr.execute(sql)
            #TPT END BY RAKESHKUMAR on 03-02-2016 FOR SAME LINE ITEMS APPEARING AGAIN IN SERVICE INVOICE
            
        return new_id
    
     
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('type','')=='in_invoice' and 'sup_inv_id' in vals and vals['sup_inv_id']:
            for seq,line in enumerate(self.browse(cr, uid, vals['sup_inv_id']).invoice_line):
                vals['invoice_line'][seq][2].update({
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'uos_id': line.uos_id.id,
                    'price_unit': line.price_unit,
                })
        
        new_write = super(account_invoice, self).write(cr, uid,ids, vals, context)
        for new in self.browse(cr,uid,ids):
            if vals.get('state','')=='cancel' and 'state' in vals:
                sql = '''
                    select id from account_move where ed_invoice_id in (select id from tpt_ed_invoice_positing where invoice_id = %s)
                '''%(new.id)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    sql = '''
                        delete from account_move_line where move_id = %s
                    '''%(move['id'])
                    cr.execute(sql)
                    sql = '''
                        delete from account_move where id = %s
                    '''%(move['id'])
                    cr.execute(sql)
                sql = '''
                    select id from tpt_ed_invoice_positing where invoice_id = %s
                '''%(new.id)
                cr.execute(sql)
                for ed in cr.dictfetchall():
                    self.pool.get('tpt.ed.invoice.positing').bt_cancel(cr,uid,[ed['id']])
#             if new.purchase_id:
#                 for invoice_line in new.invoice_line:
#                     if not invoice_line.ed and not invoice_line.aed_id_1:
#                         sql = '''
#                             update account_invoice set flag_bt_ed = 't' where id = %s
#                         '''%(invoice_line.invoice_id.id)
#                         cr.execute(sql)
            if new.purchase_id.po_document_type == 'service':
                ##TPT START BY BALAMURUGAN PURUSHOTHMAN ON 15/10/2015 - TO LOAD VENDOR TDS IN SERVICE INVOICE LINE               
                #===============================================================
                # for invoice_line in new.invoice_line:
                #     if 'is_tds_applicable' in vals and vals['is_tds_applicable'] is False:
                #         sql = '''
                #         update account_invoice_line set tds_id=NULL where id=%s
                #         '''%(invoice_line.id)
                #         cr.execute(sql)
                #     if 'is_tds_applicable' in vals and vals['is_tds_applicable'] is True:
                #         sql = '''
                #         update account_invoice_line set tds_id=%s where id=%s
                #         '''%(new.partner_id.tds_id.id, invoice_line.id)
                #         cr.execute(sql)
                #===============================================================
                #TPT END    
                for purchase_line in new.purchase_id.order_line:
                    sql = '''
                            select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity from account_invoice_line where invoice_id in (select id from account_invoice where purchase_id = %s and state!='cancel') and po_line_id = %s
                        '''%(new.purchase_id.id, purchase_line.id)
                    cr.execute(sql)
                    quantity = cr.dictfetchone()['quantity']
                     
                    sql = '''
                            select product_qty from purchase_order_line where order_id in (select id from purchase_order where id = %s) and id = %s
                        '''%(new.purchase_id.id, purchase_line.id)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()['product_qty']
                    if quantity == product_qty:
                        sql = '''
                            update purchase_order_line set flag_line = 't' where id = %s and id = %s
                        '''%(purchase_line.id, purchase_line.id)
                        cr.execute(sql)                        
                    elif quantity<product_qty:
                        sql = '''
                            update purchase_order_line set flag_line = 'f' where id = %s and id = %s
                        '''%(purchase_line.id, purchase_line.id)
                        cr.execute(sql)     
                    else:
                        raise osv.except_osv(_('Error!'), _('Quantity in Account Invoice is not more than quantity in Purchase Order'))
                sql = '''
                    select id from purchase_order_line where flag_line = 'f' and order_id = %s
                '''%(new.purchase_id.id)
                cr.execute(sql)
                purchase_orders = [row[0] for row in cr.fetchall()]
                if purchase_orders: 
                    # con so luong doi voi purchase order do
                    sql = '''
                            update purchase_order set flag = 'f' where id = %s
                        '''%(new.purchase_id.id)
                    cr.execute(sql)
                else:
                    # khong con so luong doi voi purchase order do
                    sql = '''
                            update purchase_order set flag = 't' where id = %s
                        '''%(new.purchase_id.id)
                    cr.execute(sql)
                    #TPT START BY RAKESHKUMAR on 03-02-2016 FOR SAME LINE ITEMS APPEARING AGAIN IN SERVICE INVOICE
                po_qty = 0
                inv_qty = 0            
                for purchase_line in new.purchase_id.order_line:
                    po_qty += purchase_line.product_qty
                for invoice_line in new.invoice_line:
                    inv_qty += invoice_line.quantity
                if po_qty == inv_qty:
                   sql = '''
                        update purchase_order set state = 'invoice_raised' where id = %s
                    '''%(new.purchase_id.id)
                   cr.execute(sql)
                else:
                    sql = '''
                        update purchase_order set state = 'done' where id = %s
                    '''%(new.purchase_id.id)
                    cr.execute(sql)
                   
                #TPT END BY RAKESHKUMAR on 03-02-2016 FOR SAME LINE ITEMS APPEARING AGAIN IN SERVICE INVOICE
        return new_write
    
    def compute_invoice_totals(self, cr, uid, inv, company_currency, ref, invoice_move_lines, context=None):
        if context is None:
            context={}
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
#             if inv.currency_id.id != company_currency:
#                 context.update({'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
#                 i['currency_id'] = inv.currency_id.id
#                 i['amount_currency'] = i['price']
#                 i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
#                         company_currency, i['price'],
#                         context=context)
#             else:
            i['amount_currency'] = False
            i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund'):
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, invoice_move_lines
#     def _get_analytic_lines(self, cr, uid, id, context=None):
#         if context is None:
#             context = {}
#         inv = self.browse(cr, uid, id)
#         cur_obj = self.pool.get('res.currency')
# 
#         company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
#         if inv.type in ('out_invoice', 'in_refund'):
#             sign = 1
#         else:
#             sign = -1
# 
#         iml = self.pool.get('account.invoice.line').move_line_get(cr, uid, inv.id, context=context)
#         for il in iml:
#             if il['account_analytic_id']:
#                 if inv.type in ('in_invoice', 'in_refund'):
#                     ref = inv.reference
#                 else:
#                     ref = self._convert_ref(cr, uid, inv.number)
#                 if not inv.journal_id.analytic_journal_id:
#                     raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (inv.journal_id.name,))
#                 il['analytic_lines'] = [(0,0, {
#                     'name': il['name'],
#                     'date': inv['date_invoice'],
#                     'account_id': il['account_analytic_id'],
#                     'unit_amount': il['quantity'],
#                     'amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, il['price'], context={'date': inv.date_invoice}) * sign,
#                     'product_id': il['product_id'],
#                     'product_uom_id': il['uos_id'],
#                     'general_account_id': il['account_id'],
#                     'journal_id': inv.journal_id.analytic_journal_id.id,
#                     'ref': ref,
#                 })]
#         return iml
     
#     def group_lines(self, cr, uid, iml, line, inv):
#         """Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
#         if inv.journal_id.group_invoice_lines:
#             line2 = {}
#             length = 0
#             for x, y, l in line:
#                 tmp = self.inv_line_characteristic_hashcode(inv, l)
# 
#                 if tmp in line2:
#                     am = line2[tmp]['debit'] - line2[tmp]['credit'] + (l['debit'] - l['credit'])
#                     line2[tmp]['debit'] = (am > 0) and am or 0.0
#                     line2[tmp]['credit'] = (am < 0) and -am or 0.0
#                     line2[tmp]['tax_amount'] += l['tax_amount']
#                     line2[tmp]['analytic_lines'] += l['analytic_lines']
#                 else:
#                     line2[tmp] = l
#                 length += 1
#                 if length == len(line):
#                     am = round(am)
#                     line2[tmp]['debit'] = (am > 0) and am or 0.0
#                     line2[tmp]['credit'] = (am < 0) and -am or 0.0
#             line = []
#             for key, val in line2.items():
#                 line.append((0,0,val))
#         return line
    
    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        #phuoc
        invoice_line_obj = self.pool.get('account.invoice.line')
        #/phuoc
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        cst_flag = False
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
#             if inv.tax_line:
#                 cr.execute('delete from account_invoice_tax where invoice_id = %s', (inv.id,))
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            if (inv.type == 'in_invoice' and not inv.sup_inv_id): 
                iml = invoice_line_obj.move_line_pf(cr, uid, inv.id)
#                 iml += invoice_line_obj.move_line_fright(cr, uid, inv.id) 
#                 iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id)
                iml += invoice_line_obj.move_line_excise_duty(cr, uid, inv.id) # <!-- TPT-BM-GST-ROLLBACK -->
                iml += invoice_line_obj.move_line_aed(cr, uid, inv.id)
                name = inv['name'] or inv['supplier_invoice_number'] or '/'
                if inv.purchase_id:
                    if inv.purchase_id.po_document_type not in ('service','service_qty','service_amt'):
                        # SUPPLIER INVOICE
                        iml += invoice_line_obj.move_line_fright_change_si(cr, uid, inv.id)
                        #iml += invoice_line_obj.move_line_amount_untaxed(cr, uid, inv.id) #TPT-COMMENTED BY BM - ON 26/12/2015
                        #iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id) #TPT-COMMENTED BY BM - ON 26/12/2015
                        
                        inv_id = self.pool.get('account.invoice').browse(cr, uid, inv.id)   
                        cst_flag = False                    
                        for line in inv_id.invoice_line:    
                            description = [r.description for r in line.invoice_line_tax_id]  
                            tax_amounts = [r.amount for r in line.invoice_line_tax_id]                        
                            if description and 'CST' in description[0]:
                                cst_flag = True   
                        if cst_flag is True:
                            iml += invoice_line_obj.move_line_amount_untaxed_cst(cr, uid, inv.id, tax_amounts[0]) 
                            #TPT-BM-ON 24/08/2016
                            iml += invoice_line_obj.move_line_amount_cst_to_asset_acc(cr, uid, inv.id, tax_amounts[0])
                            #TPT-START: By BalamuruganPurushothaman - ON 08/06/2016 - CST Inclusion - TO UPDATE CST AMOUNT INTO PRODUCT MASTER TOTAL COST VALUE
                            if line.product_id and line.product_id.default_code!='CONSUMABLE': #TPT BM - ON 11/08/2016 - TO BLOCK CST POSTING FOR CONSUMABLE PPRODUCTS
                                self.cst_prod_avg_cost_update(cr, uid, inv.id, tax_amounts[0], context) 
                            #TPT END
                        else:
                            iml += invoice_line_obj.move_line_amount_untaxed(cr, uid, inv.id) 
                            iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_tds_amount_without_po(cr, uid, inv.id) 
                        iml += invoice_line_obj.move_line_amount_round_off(cr, uid, inv.id)
                        # Added by P.VINOTHKUMAR on 03/11/2017  for fixing average cost issue(fright)
                        self.prod_avg_cost_update(cr, uid, inv.id, context) 
                        
                    if inv.purchase_id.po_document_type == 'service':
                        # service inv
                        iml += invoice_line_obj.move_line_fright(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_untaxed(cr, uid, inv.id) 
                        #iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id) #TPT-COMMENTED
                        ###TPT-START-By BalamuruganPurushothaman-TO POST SWACHH BHARAT CESS %
                        description = ''
                        flag = False
                        flag1 = False
                        
                        inv_id = self.pool.get('account.invoice').browse(cr, uid, inv.id)
                        for line in inv_id.invoice_line:   
                            if line.tax_id and line.tax_id.is_swachh_bharat is True: #line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                                flag=True                          
                            # if line.tax_id and line.tax_idline.tax_id.description=='STax 14.5%':
                                #------------------------------------- flag=True
                            # if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                                #------------------------------------- flag=True
#                             if line.tax_service_credit and line.tax_service_credit.description=='STax 30% of Freight 14.5% (Cr)':
#                                 flag1=True
                        if flag is True:
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                        # Added by P.vinothkumar on 04/08/2016 for adding krishikalyan-legal,labour
                            
#                         elif line.tax_id.description in ['STax 15%'] or ['STax 15% for labour (Dr)'] or ['STax 14.5% for Legal (Dr)']:
#                             iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
#                             iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
#                             iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                        # Modified by P.vinothkumr on 24/10/2016 for fixing issue in posting    
                        elif line.tax_id.description == 'STax 15%':
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                        elif line.tax_id.description =='STax 15% for labour (Dr)':   
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                        # Added by P.vinothkumar on 21/06/2016 for nullable taxes     
                        elif not line.tax_id:
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)     
                        else:
                            iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id)
                            
#                         if flag1 is True:
#                             iml += invoice_line_obj.move_line_amount_tax_credit_14(cr, uid, inv.id) 
#                             iml += invoice_line_obj.move_line_amount_tax_credit_5(cr, uid, inv.id) 
#                         else:
#                             iml += invoice_line_obj.move_line_amount_tax_credit(cr, uid, inv.id)
                        ###TPT-END
#                         iml += invoice_line_obj.move_line_amount_tax_without_po_deducte(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_tax_credit(cr, uid, inv.id) #TPT-COMMENTED - BM
#                         iml += invoice_line_obj.move_line_amount_tax_deducte_credit(cr, uid, inv.id) 
                        iml += invoice_line_obj.move_line_tds_amount_without_po(cr, uid, inv.id) 
                        iml += invoice_line_obj.move_line_amount_round_off(cr, uid, inv.id)
                    #TPT_BM on 22/04/2016
                    #if inv.purchase_id.po_document_type == 'service_qty':
                    if inv.purchase_id.po_document_type in ('service_qty', 'service_amt'):
                        # service qty based inv
                        iml += invoice_line_obj.move_line_fright(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_untaxed_ser_qty_amt(cr, uid, inv.id) 
                        description = ''
                        flag = False
                        flag1 = False
                        
                        inv_id = self.pool.get('account.invoice').browse(cr, uid, inv.id)
                        for line in inv_id.invoice_line:   
                            if line.tax_id and line.tax_id.is_swachh_bharat is True: 
                                flag=True                          
                        if flag is True:
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)    
                        ###TPT-BM-23/06/2016
                        elif line.tax_id.description in ['STax 15%']:
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                        # Added by P.vinothkumar on 23/06/2016 for nullable taxes     
                        elif not line.tax_id:
                            iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                            iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                        # TPT-end    
                        else:
                            iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id)                           
                        iml += invoice_line_obj.move_line_amount_tax_credit(cr, uid, inv.id) #TPT-COMMENTED - BM 
                        iml += invoice_line_obj.move_line_tds_amount_without_po(cr, uid, inv.id) 
                        iml += invoice_line_obj.move_line_amount_round_off(cr, uid, inv.id)
                else:
                # sup inv without po
                    flag = False 
                    flag1 = False
                    inv_id = self.pool.get('account.invoice').browse(cr, uid, inv.id)
                    for line in inv_id.invoice_line:   
                        # Added by P.vinothkumar on 06/08/2016 condition-STax 14.5% for Legal (Dr):                         
                        if line.tax_id and line.tax_id.description in ['STax 14.5%', 'STax 14.5% for Legal (Dr)']: 
                            flag=True
#                         if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
#                             flag=True                                
#                         if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Cr)':
#                             flag=True
                    iml += invoice_line_obj.move_line_fright(cr, uid, inv.id)
                    iml += invoice_line_obj.move_line_amount_untaxed_without_po(cr, uid, inv.id) 
                    #iml += invoice_line_obj.tpt_move_line_amount_tax(cr, uid, inv.id) # TPT-BalamuruganPurushothaman - ON 04/11/2015
                    # The above line is commented by BalamuruganPurushothaman on 16/12/2015
                    if flag is True:
                        iml += invoice_line_obj.tpt_move_line_amount_tax_14(cr, uid, inv.id)
                        iml += invoice_line_obj.tpt_move_line_amount_tax_5(cr, uid, inv.id)
                        # Added by P.vinothkumar on 06/08/2016 for legal(14.5%)
                        if line.tax_id.description == 'STax 14.5% for Legal (Dr)': 
                            iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                            #TPT end
                    # Added by P.vinothkumar on 06/08/2016 for adding krishikalyan legal(14.5%)        
                    elif line.tax_id.description in ['STax 15%', 'STax 15% for Legal (Dr)']:
                        iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                    # Added by P.vinothkumar on 21/06/2016 for nullable taxes        
                    elif not line.tax_id:
                        iml += invoice_line_obj.move_line_amount_tax_sbc_14(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_tax_swachh_bharat_cess_5(cr, uid, inv.id)
                        iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id)
                                 
                    else:
                        iml += invoice_line_obj.tpt_move_line_amount_tax(cr, uid, inv.id)
#                     iml += invoice_line_obj.move_line_amount_tax_without_po_deducte(cr, uid, inv.id)
                    iml += invoice_line_obj.move_line_tds_amount_without_po(cr, uid, inv.id) 
                    iml += invoice_line_obj.move_line_amount_tax_credit(cr, uid, inv.id) #TPT-ADDED - BM - ON 06/06/2016
                    iml += invoice_line_obj.move_line_amount_round_off(cr, uid, inv.id)
            if (inv.type == 'out_invoice'):
                #TPT-BM-ON0 - 01/07/2016 - For Customer Invoice Return GL Posting
                # The "type" param is passed into the following method in addition to vice versa the posting entries of normal\
                # Since -Value is Credit, +Value is Debit
                if inv.sale_id.document_type=='saleorder':
                    iml = invoice_line_obj.move_line_customer_fright(cr, uid, inv.id, inv.sale_id.document_type) 
                    iml += invoice_line_obj.move_line_customer_insurance(cr, uid, inv.id, inv.sale_id.document_type) 
                    iml += invoice_line_obj.move_line_customer_amount_tax(cr, uid, inv.id, inv.sale_id.document_type) 
#                     iml += invoice_line_obj.move_line_customer_excise_duty(cr, uid, inv.id, inv.sale_id.document_type) 
                    iml += invoice_line_obj.move_line_customer_product_price(cr, uid, inv.id, inv.sale_id.document_type)
                    name = inv['vvt_number'] or '/'
                elif inv.sale_id.document_type=='return':
                    iml = invoice_line_obj.move_line_customer_fright(cr, uid, inv.id, inv.sale_id.document_type) 
                    iml += invoice_line_obj.move_line_customer_insurance(cr, uid, inv.id, inv.sale_id.document_type) 
                    iml += invoice_line_obj.move_line_customer_amount_tax(cr, uid, inv.id, inv.sale_id.document_type) 
#                     iml += invoice_line_obj.move_line_customer_excise_duty(cr, uid, inv.id, inv.sale_id.document_type) 
                    iml += invoice_line_obj.move_line_customer_product_price(cr, uid, inv.id, inv.sale_id.document_type)
                    name = inv['vvt_number'] or '/'
                
            if (inv.type == 'in_invoice' and inv.sup_inv_id):
                # freight invoice 
                iml = invoice_line_obj.move_line_fi_base(cr, uid, inv.id)
                #iml += invoice_line_obj.move_line_fi_debit(cr, uid, inv.id) #TPT-COMMENTED
                
                ### TPT-By BalamuruganPurushothaman - ON 13/12/2015 - Updated on 15/12/2015
                flag = False 
                flag1 = False        
                inv_id = self.pool.get('account.invoice').browse(cr, uid, inv.id)
                for line in inv_id.invoice_line:                            
                    if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                        flag=True
                    # Added by P.vinothkumar on 21/06/2016(for adding krishi kalyan tax)    
                    elif line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                        flag=True    
                    elif line.tax_id and line.tax_id.description=='STax 14.5%':
                        flag=True
#                     elif line.tax_credit and line.tax_credit.description=='STax 30% of Freight 14.5% (Cr)':
#                         flag1=True
                if flag is True:
                    iml += invoice_line_obj.move_line_fi_debit_14(cr, uid, inv.id)
                    iml += invoice_line_obj.move_line_fi_debit_5(cr, uid, inv.id)            
                else:
                    iml += invoice_line_obj.move_line_fi_debit(cr, uid, inv.id)
                #iml += invoice_line_obj.move_line_amount_tax_krishi_kalyan_cess_5(cr, uid, inv.id) #Added By P.vinothkumar - ON 21/06/2016 -for Krishi kalyan cess  
                iml += invoice_line_obj.move_line_fi_credit(cr, uid, inv.id) #TPT-COMMENTED
                iml += invoice_line_obj.move_line_tds_amount_freight(cr, uid, inv.id) 
                iml += invoice_line_obj.move_line_amount_round_off(cr, uid, inv.id)
                name = inv['name'] or inv['supplier_invoice_number'] or '/'
                #TPT-START: By BalamuruganPurushothaman - ON 28/01/2016 - TO UPDATE FREIGHT INVOICE AMOUNT INTO PRODUCT MASTER TOTAL COST VALUE
                self.prod_avg_cost_update(cr, uid, inv.id, context)   
                #TPT-END
            
#             iml += invoice_line_obj.move_line_price_total(cr, uid, inv.id)  
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)
  
            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))
  
            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))
                  
               
#             iml += ait_obj.move_line_get(cr, uid, inv.id)
  
            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'
  
            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id
            
            ###CST - 3338
            #===================================================================
            # if cst_flag is True:
            #     cst_amt = 0.00
            #     for line in inv_id.invoice_line:                        
            #         tax_amounts = [r.amount for r in line.invoice_line_tax_id]  
            #         cst_amt = total * tax_amounts[0]/100
            #         #total = 
            #     total = total+cst_amt
            #===================================================================
            ###
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False
  
                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency
  
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
#                     'price': inv.amount_total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref,
                    
            })
  
            date = inv.date_invoice or time.strftime('%Y-%m-%d')
  
            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)
  
            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))
  
            line = self.finalize_invoice_move_lines(cr, uid, inv, line)
            
            move = {
                'ref': inv.reference and inv.reference or inv.name,
#                 'doc_type':'',
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id
            ##TPT-VINOTH
            vals={}            
            sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))            
            if (inv.type == 'out_invoice'): # Modified by P.VINOTHKUMAR on 11th April 2016     
                move['doc_type'] = 'cus_inv'
                move['ref'] = inv.vvt_number
                #TPT START - By P.VINOTHKUMAR - ON 11/04/2015 - FOR (Generate document sequence for Customer Invoice Account postings)
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.customer.invoice')
                vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                CInvoice_account=vals['name'] 
                # TPT END
                move['name']=CInvoice_account
                move['ref'] = inv.vvt_number
            if (inv.type == 'in_invoice'):
                if inv.purchase_id:
                    #if inv.purchase_id.po_document_type == 'service': #TPT-BM-ON 28/04/2016
                    if inv.purchase_id.po_document_type in ('service', 'service_qty', 'service_amt'):
                        move['doc_type'] = 'ser_inv'
                        #TPT START - By P.VINOTHKUMAR - ON 13/04/2015 - FOR (Generate document sequence for service invoice account postings)
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.service.invoice')
                        #vals['name']='SI/'+fiscalyear['code']+'/'+sequence
                        vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                        Service_invoice_account=vals['name'] 
                        move['name']=Service_invoice_account
                        move['ref'] = inv.name
                    else:
                        move['doc_type'] = 'sup_inv_po'
                        move['ref'] = inv.name
                        #TPT START - By P.VINOTHKUMAR - ON 11/04/2016 - FOR (Generate document sequence for supplier invoice with po Account postings)
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.supplier.invoice.withpo')
                        #vals['name']='SUPO/'+fiscalyear['code']+'/'+sequence
                        vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                        SInvoice_account_withpo=vals['name'] 
                        move['name']=SInvoice_account_withpo
                        move['ref'] = inv.grn_no.name
                            
    #                 else:
    #                     move['doc_type'] = 'sup_inv'
                elif not inv.sup_inv_id:
                    move['doc_type'] = 'sup_inv'
                    move['ref'] = inv.name
          #TPT START - By P.VINOTHKUMAR - ON 13/04/2016 - FOR (Generate document sequence for supplier Invoice without PO Account postings)
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.supplier.invoice.notpo')
                    #vals['name']='SU/'+fiscalyear['code']+'/'+sequence
                    vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                    SInvoice_account_notpo=vals['name'] 
                    move['name']=SInvoice_account_notpo
                    move['ref'] = inv.name
                        
    #                 if inv.sup_inv_id:
    #                     move['doc_type'] = 'freight'
                else:
                    move['doc_type'] = 'freight'
                    move['ref'] = inv.name
                    #TPT START - By P.VINOTHKUMAR - ON 13/04/2016 - FOR (Generate document sequence for Freight Invoice Account postings)
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.freight.invoice')
                    #vals['name']='FI/'+fiscalyear['code']+'/'+sequence
                    vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                    FInvoice_account=vals['name'] 
                    move['name']=FInvoice_account
                    move['ref'] = inv.name
      
            ctx.update(invoice=inv)
            if context.get('tpt_review_posting',False):
                return move
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            
            
            valid_moves = move_obj.validate(cr, uid, [move_id], context)
            if not valid_moves:
                raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
            obj_sequence = self.pool.get('ir.sequence')
            for move in move_obj.browse(cr, uid, valid_moves, context=context):
                if move.name =='/':
                    new_name = False
                    journal = move.journal_id
        
        #                     if invoice and invoice.internal_number:
        #                         new_name = invoice.internal_number
        #                     else:
    #         if journal.sequence_id:
    #             c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
    #             new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
    #         else:
    #             raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
    #         if new_name:
    #             move_obj.write(cr, uid, [move.id], {'name':new_name})
            # auto posting for journal entry
            #TPT START - By P.VINOTHKUMAR - ON 13/04/2016 - FOR (validate account postings for Customer invoice)
            auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
            if auto_ids:
                auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                if inv.type == 'in_invoice' and not inv.sup_inv_id:
                    if inv.purchase_id:
                        if auto_id.supplier_invoice and inv.purchase_id.po_document_type != 'service':
                          # sup invoice
                          try:
                              move_obj.button_validate(cr,uid, [move.id], context)
                          except:
                              pass
                        if auto_id.service_invoice and inv.purchase_id.po_document_type == 'service':
                          # service invoice
                          try:
                              move_obj.button_validate(cr,uid, [move.id], context)
                          except:
                              pass
                    # Modified by P.vinothkumar on 27/09/2016 for fixing auto posting in supplier invoice without po   
                    else:
                        if auto_id.supplier_invoice_without:
                      # sup invoice without po
                            try:
                                move_obj.button_validate(cr,uid, [move.id], context)
                            except:
                                pass
                if inv.type == 'in_invoice' and inv.sup_inv_id:
                    if auto_id.freight_invoice:
                      # freight invoice
                      try:
                          move_obj.button_validate(cr,uid, [move.id], context)
                      except:
                          pass
                if inv.type == 'out_invoice':
            
                  if CInvoice_account==vals['name']:
                        # customer invoice
                    try:
                        move_obj.button_validate(cr,uid, [move.id], context)
                    except:
                        pass
#             move_obj.post(cr, uid, [move_id], context=ctx)
            
        self._log_event(cr, uid, ids)
        return True
    #TPT-START: By BalamuruganPurushothaman - ON 28/01/2016 - Freight Inclusion - TO UPDATE FREIGHT INVOICE AMOUNT INTO PRODUCT MASTER TOTAL COST VALUE  
    def prod_avg_cost_update_old(self, cr, uid, invoice_id, context=None):
        result = []
        if context is None:
            context = {}
        ctx = context.copy()
        inventory_obj = self.pool.get('tpt.product.avg.cost')
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in inv_id.invoice_line:
            sql = 'delete from tpt_product_avg_cost where product_id=%s'%(line.product_id.id)
            cr.execute(sql)       
            sql = '''
                select foo.loc as loc
                    from
                    (select st.location_id as loc from stock_move st
                        inner join stock_location l on st.location_id= l.id
                            where l.usage = 'internal'
                    union all
                    select st.location_dest_id as loc from stock_move st
                        inner join stock_location l on st.location_dest_id= l.id
                        where l.usage = 'internal'
                        )foo
                   group by foo.loc
            '''
            cr.execute(sql)
            for loc in cr.dictfetchall():
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st 
                            where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id and production_id is null
                        )foo
                '''%(line.product_id.id,loc['loc'])
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = float(inventory['ton_sl'])
                    total_cost = float(inventory['total_cost'])
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl 
                            from 
                                (
                                select st.product_qty*-1 as product_qty
                                    from stock_move st 
                                    where st.state='done'
                                        and st.product_id=%s
                                        and location_id=%s
                                        and location_dest_id != location_id
                                        and production_id is null
                                )foo
                    '''%(line.product_id.id,loc['loc'])
                    cr.execute(sql)
                    out = cr.dictfetchone()
                    if out:
                        hand_quantity = hand_quantity+float(out['ton_sl'])
                        total_cost = avg_cost*hand_quantity
                    
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty as product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.
                                 location_dest_id != st.location_id
                                 and production_id is not null
                             union all
                             select st.product_qty*-1 as product_qty
                                from stock_move st 
                                where st.state='done'
                                        and st.product_id=%s
                                            and location_id=%s
                                            and location_dest_id != location_id
                                             and production_id is not null
                            )foo
                    '''%(line.product_id.id,loc['loc'],line.product_id.id,loc['loc'])
                    cr.execute(sql)
                    hand_quantity += cr.fetchone()[0]
                    sql = '''
                        select case when sum(produce_cost)!=0 then sum(produce_cost) else 0 end produce_cost,
                            case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                            from mrp_production where location_dest_id=%s and product_id=%s and state='done'
                    '''%(loc['loc'],line.product_id.id)
                    cr.execute(sql)
                    produce = cr.dictfetchone()
                    if produce:
                        total_cost += float(produce['produce_cost'])
                        avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    base = 0.0
                    if line.fright_fi_type == '2':
                        base = round(line.fright)
                    else:
                        base = round(line.fright*line.quantity)
                    invoice_line_amt = base
                    total_cost += invoice_line_amt
                    if hand_quantity>0:
                        avg_cost = total_cost/hand_quantity
                    inventory_obj.create(cr, uid, {'product_id':line.product_id.id,
                                                   'warehouse_id':loc['loc'],
                                                   'hand_quantity':hand_quantity,
                                                   'avg_cost':avg_cost,
                                                   'total_cost':total_cost})   

        return True
    ###
    def prod_avg_cost_update(self, cr, uid, invoice_id,context=None):
        result = []
        if context is None:
            context = {}
        ctx = context.copy()
        inventory_obj = self.pool.get('tpt.product.avg.cost')
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id) 
#        currency = self.pool.get('res.currency') # RK
#        currency_id = inv_id.currency_id.id
#        freight_amt1 = 0
#        if inv_id.currency_id.name != 'INR': # RK
#                rate1 = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate'] # RK
#                freight_amt1 = freight_amt * 1/rate1      # RK
        inv_line_net_amt = 0
        location_id = False
        for line in inv_id.invoice_line: 
            freight_amt = 0           
             # Added fright_type logic by P.VINOTHKUMAR ON 06/11/2017 for fixing Avg cost issue.
            if line.fright_type=='1':
                freight_amt = line.quantity * line.price_unit * line.fright/100
            if line.fright_fi_type=='2' or line.fright_type=='2':
                freight_amt = line.fright
            if line.fright_fi_type=='3' or line.fright_type=='3':
                freight_amt = line.fright * line.quantity    
            if line.fright_fi_type=='3' and line.fright_type=='2':
                freight_amt = line.fright * line.quantity
            if line.fright_fi_type=='2' and line.fright_type=='3':
                freight_amt = line.fright                   
            # TPT CODE End 06/11/2017
           
            if line.product_id.cate_name=='spares':
                location_id = 14
            if line.product_id.cate_name=='raw':
                location_id = 15
            if line.product_id.cate_name=='consum': # Fright invoice with consumable product
                location_id = 14    
            inv_obj_ids = inventory_obj.search(cr, uid, [('product_id', '=', line.product_id.id),('warehouse_id', '=', location_id)])
            inv_ids = inventory_obj.browse(cr, uid, inv_obj_ids[0])
            hand_quantity = inv_ids.hand_quantity
            total_cost = inv_ids.total_cost
            total_cost += freight_amt
            # Added by P.VINOTHKUMAR ON 27/12/2016 for calculate current value in product avg_cost
            sql = '''
                select avg_cost,total_cost,hand_quantity
                from tpt_product_avg_cost where product_id=%s and warehouse_id=%s
                '''%(line.product_id.id, location_id)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = round(float(inventory['hand_quantity']),2)
                total_cost = round(float(inventory['total_cost']),2)
                avg_cost = round(float(inventory['avg_cost']),2)
                # commented by P.VINOTHKUMAR ON 07/11/2017 for fixing to decrease product stock value when cancel freight invoice
                #total_cost += freight_amt
                 # Added by P.VINOTHKUMAR ON 07/11/2017 for fixing to decrease product stock value when cancel freight invoice
                if inv_id.state=='cancel':
                    total_cost -= freight_amt
                else:
                    total_cost += freight_amt  
                # End 07/11/2017
                if hand_quantity>0:
                    #TPT-BM-ON 05/07/2016 - GET CST INVOICE AMT
                    cst_amt = 0
                    frt_amt = 0
                    si_frt_amt = 0
                    sql = '''
                        select 
                        
                        case when sum(ail.tpt_tax_amt)>=0 then sum(ail.tpt_tax_amt) else 0 end as cst_amt 
                        
                        from account_invoice ai
                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                        inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                        inner join account_tax t on ailt.tax_id = t.id
                        where ail.product_id=%s and ai.state not in ('draft', 'cancel') 
                        and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
                    '''%(line.product_id.id, '%', '%')
                    cr.execute(sql)
                    cst_amt = cr.fetchone()
                    if cst_amt:
                        cst_amt = cst_amt[0]
#                     #Commented by P.VINOTHKUMAR ON 06/11/2017 for calculate fright amt in fright invoice.
#                     sql = '''
#                         select 
#                         
#                         case when 
#                         SUM(case when ail.fright_fi_type='2' then ail.fright
#                         when ail.fright_fi_type='3' then ail.fright*ail.quantity
#                         else 0 end) >=0
#                         then    
#                         SUM(case when ail.fright_fi_type='2' then ail.fright
#                         when ail.fright_fi_type='3' then ail.fright*ail.quantity
#                         else 0 end)                
#                         else 0 end as frt_amt
#                         
#                         from account_invoice ai
#                         inner join account_invoice_line ail on ai.id=ail.invoice_id
#                         where ail.product_id=%s and ai.state not in ('draft', 'cancel')
#                         and ai.doc_type='freight_invoice'
#                     '''%(line.product_id.id)
#                     cr.execute(sql)
#                     frt_amt = cr.fetchone()
#                     if frt_amt:
#                         frt_amt = frt_amt[0]    
#                     #
#                     #Modified by P.VINOTHKUMAR FOR MODIFY ail.fright_type='1' in script 
#                     sql = '''
#                     select 
#                         case when 
#                             SUM(case 
#                             when ail.fright_type='1' then ((ail.quantity * ail.price_unit) + ail.p_f + ail.ed + ail.tpt_tax_amt) * ail.fright/100
#                             when ail.fright_type='2' then ail.fright
#                             when ail.fright_type='3' then ail.fright*ail.quantity
#                             when ail.fright_type is null then ail.fright
#                             else 0 end) >=0
#                             then    
#                             SUM(case 
#                             when ail.fright_type='1' then ((ail.quantity * ail.price_unit) + ail.p_f + ail.ed + ail.tpt_tax_amt) * ail.fright/100
#                             when ail.fright_type='2' then ail.fright
#                             when ail.fright_type='3' then ail.fright*ail.quantity
#                             when ail.fright_type is null then ail.fright
#                             else 0 end)                
#                             else 0 end as frt_amt
#                         from account_invoice ai
#                         inner join account_invoice_line ail on ai.id=ail.invoice_id
#                         where ail.product_id=%s and 
#                         ai.state not in ('draft', 'cancel')
#                         and ai.doc_type='supplier_invoice' and ail.fright>0  
#                     '''%(line.product_id.id)
#                     cr.execute(sql)
#                     si_frt_amt = cr.fetchone()
#                     if si_frt_amt:
#                         si_frt_amt = si_frt_amt[0]
                     # commented by P.VINOTHKUMAR ON 06/11/2017
                    #total_cost += (cst_amt + frt_amt + si_frt_amt)
                    total_cost += (cst_amt)
                    avg_cost = total_cost  / hand_quantity
                else:
                    avg_cost = 0
                #       
                sql = 'delete from tpt_product_avg_cost where id=%s'%(inv_ids.id)
                cr.execute(sql)  
                #inventory_obj.write(cr, uid, [inv_ids.id], vals, context)
                inventory_obj.create(cr, uid, {'product_id': line.product_id.id,
                                               'warehouse_id': location_id,
                                               'hand_quantity': hand_quantity,
                                               'avg_cost': avg_cost, # total_cost/hand_quantity,
                                               'total_cost': avg_cost * hand_quantity})     
        return True
    ###

    ###TPT-START: By BalamuruganPurushothaman - ON 28/01/2016 - TO UPDATE FREIGHT INVOICE AMOUNT INTO PRODUCT MASTER TOTAL COST VALUE  
    #2nd Update - TPT-BM-ON-04/06/2016 
    def cst_prod_avg_cost_update(self, cr, uid, invoice_id, tax_amounts, context=None):
        result = []
        if context is None:
            context = {}
        ctx = context.copy()
        inventory_obj = self.pool.get('tpt.product.avg.cost')
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        inv_line_net_amt = 0
        location_id = False
        for line in inv_id.invoice_line:
         #Added by P.VINOTHKUMAR on 22/12/2016 for adding freight details in supplier invoice 
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            fright = 0.0
            voucher_rate = 1
            freight_amt = 0
            basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
            basic = round(basic,2)    
            if line.fright_type=='1':
                freight_amt =  (basic + line.p_f + line.ed + line.tpt_tax_amt) * line.fright/100
            elif line.fright_type=='2':
                freight_amt = line.fright
            elif line.fright_type=='3':
                freight_amt = line.fright*line.quantity
            print freight_amt    
            description = [r.description for r in line.invoice_line_tax_id]
            if description and 'CST' in description[0]:                    
                print line.tpt_tax_amt
                inv_line_net_amt += line.tpt_tax_amt
                if line.product_id.cate_name=='spares':
                    location_id = 14
                if line.product_id.cate_name=='raw':
                    location_id = 15  
                inv_obj_ids = inventory_obj.search(cr, uid, [('product_id', '=', line.product_id.id),('warehouse_id', '=', location_id)])
                inv_ids = inventory_obj.browse(cr, uid, inv_obj_ids[0])
                hand_quantity = inv_ids.hand_quantity
                total_cost = inv_ids.total_cost
                total_cost += line.tpt_tax_amt  
                total_cost += freight_amt

                #===============================================================
                # vals = {'total_cost': total_cost,
                #         'avg_cost': total_cost/hand_quantity, 
                #         }
                #===============================================================
                
                #
#                 sql = '''
#                 select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                 (select st.product_qty,st.price_unit*st.product_qty as price_unit
#                     from stock_move st 
#                     where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id and production_id is null
#                 )foo
#                 '''%(line.product_id.id, location_id)
                sql = '''
                select avg_cost,total_cost,hand_quantity
                from tpt_product_avg_cost where product_id=%s and warehouse_id=%s
                '''%(line.product_id.id, location_id)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = round(float(inventory['hand_quantity']),2)
                    total_cost = round(float(inventory['total_cost']),2)
                    avg_cost = round(float(inventory['avg_cost']),2)
                    total_cost += line.tpt_tax_amt
                    total_cost += round(freight_amt,2)
                    if hand_quantity>0:
                        #TPT-BM-ON 05/07/2016 - GET CST INVOICE AMT
                        cst_amt = 0.0
                        sql = '''
                        select 
                        case when sum(ail.tpt_tax_amt)>=0 then sum(ail.tpt_tax_amt) else 0 end as cst_amt 
                        from account_invoice ai
                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                        inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                        inner join account_tax t on ailt.tax_id = t.id
                        where ail.product_id=%s and ai.state not in ('draft', 'cancel') 
                        and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
                        '''%(line.product_id.id, '%', '%')
                        cr.execute(sql)
                        cst_amt = cr.fetchone()
                        if cst_amt:
                            cst_amt = cst_amt[0]
                        
                        frt_amt = 0.0
                        si_frt_amt = 0.0
                        sql = '''
                            select

                            case when 
                            SUM(case when ail.fright_fi_type='2' then ail.fright
                            when ail.fright_fi_type='3' then ail.fright*ail.quantity
                            else 0 end) >=0
                            then 
                            SUM(case when ail.fright_fi_type='2' then ail.fright
                            when ail.fright_fi_type='3' then ail.fright*ail.quantity
                            else 0 end)
                            else 0 end as frt_amt
                            
                            from account_invoice ai
                            inner join account_invoice_line ail on ai.id=ail.invoice_id
                            where ail.product_id=%s and ai.state not in ('draft', 'cancel')
                            and ai.doc_type='freight_invoice'
                        '''%(line.product_id.id)
                        cr.execute(sql)
                        frt_amt = cr.fetchone()
                        if frt_amt:
                            frt_amt = frt_amt[0]
                            
                        total_cost += (cst_amt + frt_amt)
                        avg_cost = total_cost  / hand_quantity
                        #hand_quantity = round(hand_quantity,2)
                    else:
                        avg_cost = 0

                
                sql = 'delete from tpt_product_avg_cost where id=%s'%(inv_ids.id)
                cr.execute(sql)  
                #inventory_obj.write(cr, uid, [inv_ids.id], vals, context)
                inventory_obj.create(cr, uid, {'product_id': line.product_id.id,
                                               'warehouse_id': location_id,
                                               'hand_quantity': hand_quantity,
                                               'avg_cost': avg_cost, # total_cost/hand_quantity,
                                               'total_cost': avg_cost * hand_quantity})     
        return True
    ##
    ##
    ## 
    ##
    
    # vsis inherit
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        return {
            'date_maturity': x.get('date_maturity', False),
            'partner_id': part,
            'name': x['name'][:64],
            'date': date,
            'debit': x['price']>0 and x['price'],
            'credit': x['price']<0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_lines': x.get('analytic_lines', []),
            'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'tax_code_id': x.get('tax_code_id', False),
            'tax_amount': x.get('tax_amount', False),
            'ref': x.get('ref', False),
            'quantity': x.get('quantity',1.00),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uos_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
            # vsis add
            'tpt_grn_id':x.get('tpt_grn_id', False),
            'tpt_grn_line_id':x.get('tpt_grn_line_id', False),
        }
 # Added by P.VINOTHKUMAR ON 07/11/2017 - In the time of cancelling fright invoice, product's freight value will be decreased...
    def action_cancel(self, cr, uid, ids, context=None):
        invoice_vals1 = super(account_invoice,self).action_cancel(cr, uid, ids, context=context)
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.type!='out_invoice':
                self.prod_avg_cost_update(cr, uid, inv.id, context)
        return True
    
account_invoice()
#TPT-BM ON 22/04/2016 - MAINTENANCE MODULE CHANGES
#tpt_third_service_entry calss in defined here to avoid throwing error while upgrading module, 
#since the hierarchy of upgrade is Accounting, Maintenance module
class tpt_third_service_entry(osv.osv):
    _name = "tpt.third.service.entry"
    _columns = {
        'write_date': fields.datetime('Updated on',readonly = True),  
    }
tpt_third_service_entry() 
class tpt_third_service_entry_line(osv.osv):
    _name = "tpt.third.service.entry.line"
    _columns = {
        'write_date': fields.datetime('Updated on',readonly = True),     
    }
tpt_third_service_entry_line()     
#  
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
        'third_party_id': fields.many2one('tpt.third.service.entry', 'Service Entry'), #TPT-BM ON 22/04/2016 - MAINTENANCE MODULE CHANGES
        'third_party_line_id': fields.many2one('tpt.third.service.entry.line', 'Service Entry Line'), #TPT-BM ON 25/04/2016 - MAINTENANCE MODULE CHANGES
        #vsis selected grn from pop-up Create invoice
        'tpt_grn_id': fields.many2one('stock.picking', 'GRN'),
        'tpt_grn_line_id': fields.many2one('stock.move', 'GRN line'),
    }
    #TPT-BM-25/04/2016-MAINTENACE MODULE CHANGES
    def create(self, cr, uid, vals, context=None):
        if 'third_party_line_id' in vals: 
            third_party_obj = self.pool.get('tpt.third.service.entry.line')
            third_party_line = third_party_obj.browse(cr, uid, vals['third_party_line_id'], context=context)
            vals.update({
                'price_unit': third_party_line.price_unit or 0,
                'quantity': third_party_line.product_uom_qty or 0,
                'uos_id': third_party_line.uom_id and third_party_line.uom_id.id or False,
                         })
        new_id = super(account_invoice_line, self).create(cr, uid, vals, context)
        if 'third_party_line_id' in vals:
            third_val = {'is_invoiced':True}
            third_party_obj.write(cr,uid,[vals['third_party_line_id']],third_val) 
        return new_id 
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'third_party_line_id' in vals:
            third_party_obj = self.pool.get('tpt.third.service.entry.line')
            third_party_line = third_party_obj.browse(cr, uid, vals['third_party_line_id'], context=context)
            vals.update({
                'price_unit': third_party_line.price_unit or 0,
                'quantity': third_party_line.product_uom_qty or 0,
                'uos_id': third_party_line.uom_id and third_party_line.uom_id.id or False,
                         })
            third_val = {'is_invoiced':True}
            third_party_obj.write(cr,uid,[vals['third_party_line_id']],third_val) 
        new_write = super(account_invoice_line, self).write(cr, uid,ids, vals, context)
        return new_write
    #TPT END
    def onchange_third_party_line_id(self, cr, uid, ids, third_party_line_id, context=None):
        if not third_party_line_id:
            return {'value': {
                'price_unit': False,
                'quantity': False,
                'uos_id': False
            }}
        third_party_line = self.pool.get('tpt.third.service.entry.line').browse(cr, uid, third_party_line_id, context=context)
        result = {
            'price_unit': third_party_line.price_unit or 0,
            'quantity': third_party_line.product_uom_qty or 0,
            'uos_id': third_party_line.uom_id and third_party_line.uom_id.id or False,
        } 
        return {'value': result}
        
    def get_pro_account_id(self,cr,uid,name,channel):
        account = False
        account_obj = self.pool.get('account.account')
        if name and channel:
            product_name = name.strip()
            dis_channel = channel.strip()
            account_ids = []
            if dis_channel in ['VVTi Domestic','VVTI Domestic']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810001')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810031')])
            if dis_channel in ['VVTi Direct Export','VVTI Direct Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810003')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810032')])
            if dis_channel in ['VVTi Indirect Export','VVTI Indirect Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810004')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810033')])
            if account_ids:
                account = account_ids[0]
        return account
    
    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        for line in inv.invoice_line:
            mres = self.move_line_get_item(cr, uid, line, inv, context)
            if not mres:
                continue
            res.append(mres)
            tax_code_found= False
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id,
                    (line.price_unit * (1.0 - (line['discount'] or 0.0) / 100.0)),
                    line.quantity, line.product_id,
                    inv.partner_id)['taxes']:
 
                if inv.type in ('out_invoice', 'in_invoice'):
                    tax_code_id = tax['base_code_id']
                    tax_amount = line.price_subtotal * tax['base_sign']
                else:
                    tax_code_id = tax['ref_base_code_id']
                    tax_amount = line.price_subtotal * tax['ref_base_sign']
 
                if tax_code_found:
                    if not tax_code_id:
                        continue
                    res.append(self.move_line_get_item(cr, uid, line, inv, context))
                    res[-1]['price'] = 0.0
                    res[-1]['account_analytic_id'] = False
                elif not tax_code_id:
                    continue
                tax_code_found = True
 
                res[-1]['tax_code_id'] = tax_code_id
                res[-1]['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, tax_amount, context={'date': inv.date_invoice})
        return res
 
    def move_line_get_item(self, cr, uid, line, inv, context=None):
        return {
            'type':'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit':line.price_unit,
            'quantity':line.quantity,
# phuoc            'price':line.price_subtotal,
#phuoc        
            'price':inv.p_f_charge,
#/phuoc        
            'account_id':line.account_id.id,
            'product_id':line.product_id.id,
            'uos_id':line.uos_id.id,
            'account_analytic_id':line.account_analytic_id.id,
            'taxes':line.invoice_line_tax_id,
            # vsis add
            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
        }  
    def move_line_amount_untaxed(self, cr, uid, invoice_id):
        res = []
        #TPT-SSR on 03/02/2017-Trial Balance Issue
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
        ##    
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            basic = round(basic,2)
            sql = '''
                SELECT purchase_acc_id FROM product_product WHERE id=%s and purchase_acc_id is not null
            '''%(t['product_id'])
            cr.execute(sql)          
            purchase_acc_id = cr.dictfetchone()
            if not purchase_acc_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
            if currency != 'INR':
                voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'])['rate']
                basic = basic/voucher_rate
            if basic:
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': basic,
                    'account_id': purchase_acc_id and purchase_acc_id['purchase_acc_id'] or False,
                    'account_analytic_id': t['account_analytic_id'],
                    # vsis add
                    'tpt_grn_id':t and t['tpt_grn_id'] or False,
                    'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
        return res
    def move_line_amount_untaxed_ser_qty_amt(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            basic = round(basic,2)
            #===================================================================
            # sql = '''
            #     SELECT purchase_acc_id FROM product_product WHERE id=%s and purchase_acc_id is not null
            # '''%(t['product_id'])
            # cr.execute(sql)          
            # purchase_acc_id = cr.dictfetchone()
            # if not purchase_acc_id:
            #     raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
            #===================================================================
            account_id =  t['account_id']  
            if basic:
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': basic,
                    'account_id': account_id, #purchase_acc_id and purchase_acc_id['purchase_acc_id'] or False,
                    'account_analytic_id': t['account_analytic_id'],
                    # vsis add
                    'tpt_grn_id':t and t['tpt_grn_id'] or False,
                    'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
        return res
    def move_line_amount_cst_to_asset_acc(self, cr, uid, invoice_id, tax_amounts):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        #for t in cr.dictfetchall():
        for line in inv_id.invoice_line:
            basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
            ###
            ed = 0.00
            aed = 0.00
            p_f = 0.0
            cst_vals = 0.0
            if line.ed_type == '1' :
                ed = (basic) * line.ed/100
                ed = round(ed,2)
            elif line.ed_type == '2' :
                ed = line.ed
                ed = round(ed,2)
            elif line.ed_type == '3' :
                ed = line.ed * line.quantity
                ed = round(ed,2)
            else:
                ed = line.ed
                ed = round(ed,2) 
            aed = line.aed_id_1 or 0.00
            ##
            if (line.p_f_type == '1'):
                 p_f = basic * line.p_f/100
            elif (line.p_f_type == '2'):
                 p_f =  line.p_f
            elif (line.p_f_type == '3'):
                 p_f =  line.p_f * line.quantity
            else:
                 p_f = line.p_f
            ##
            ###
            cst_basic = basic+ed+aed+p_f
            #basic += cst_basic * tax_amounts/100
            cst_vals += cst_basic * tax_amounts/100
            basic = round(cst_vals,2)
            sql = '''
                SELECT purchase_acc_id FROM product_product WHERE id=%s and purchase_acc_id is not null
            '''%(line.product_id.id)
            cr.execute(sql)
            purchase_acc_id = cr.dictfetchone()
            if not purchase_acc_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
            if basic:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': basic,
                    'account_id': line.product_id.product_asset_acc_id.id or False,
                    #'account_analytic_id': line.account_analytic_id,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                    })
        return res
    def move_line_amount_untaxed_cst(self, cr, uid, invoice_id, tax_amounts):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            ###
            ed = 0.00
            aed = 0.00
            p_f = 0.0
            if t['ed_type'] == '1' :
                ed = (basic) * t['ed']/100
                ed = round(ed,2)
            elif t['ed_type'] == '2' :
                ed = t['ed']
                ed = round(ed,2)
            elif t['ed_type'] == '3' :
                ed = t['ed'] * t['quantity']
                ed = round(ed,2)
            else:
                ed = t['ed']
                ed = round(ed,2) 
            aed = t['aed_id_1'] or 0.00
            ##
            if (t['p_f_type'] == '1'):
                 p_f = basic * t['p_f']/100
            elif (t['p_f_type'] == '2'):
                 p_f =  t['p_f']
            elif (t['p_f_type'] == '3'):
                 p_f =  t['p_f'] * t['quantity']
            else:
                 p_f = t['p_f']
            ##
            ###
            cst_basic = basic+ed+aed+p_f
            #basic += cst_basic * tax_amounts/100 #TPT-BM-ON 24/08/2016 - adding cst value in GRIR ac is blocked
            basic = round(basic,2)
            sql = '''
                SELECT purchase_acc_id FROM product_product WHERE id=%s and purchase_acc_id is not null
            '''%(t['product_id'])
            cr.execute(sql)
            purchase_acc_id = cr.dictfetchone()
            if not purchase_acc_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
            if basic:
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': basic,
                    'account_id': purchase_acc_id and purchase_acc_id['purchase_acc_id'] or False,
                    'account_analytic_id': t['account_analytic_id'],
                    # vsis add
                    'tpt_grn_id':t and t['tpt_grn_id'] or False,
                    'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
        return res
    def move_line_amount_untaxed_without_po(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            basic = round(basic,2)
            if basic:
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': basic,
                    'account_id': t['account_id'],
                    'account_analytic_id': t['account_analytic_id'],
                    # vsis add
                    'tpt_grn_id':t and t['tpt_grn_id'] or False,
                    'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
        return res
    
    def move_line_tds_amount_without_po(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            tds_amount = 0
            if line.tds_id:    
                tds_amount = line.quantity * line.price_unit * line.tds_id.amount/100
                tds_amount = round(tds_amount,2)
                if not line.tds_id.gl_account_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master for TDS %'))
                if tds_amount:   
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': -tds_amount,
                        'account_id': line.tds_id and line.tds_id.gl_account_id and line.tds_id.gl_account_id.id or False,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                    })
        return res 
    
    def move_line_tds_amount_freight(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if invoice.sup_inv_id:
            for line in invoice.invoice_line:
                tds_amount = 0
                if line.tds_id_2:    
                    if line.fright_fi_type == '2':
                        base = round(line.fright,2)
                        tax_tds_amount = base*(line.tds_id_2 and line.tds_id_2.amount/100 or 0)
                        tax_tds_amount = round(tax_tds_amount,2)
                    else:
                        base = round(line.fright*line.quantity,2)
                        tax_tds_amount = base*(line.tds_id_2 and line.tds_id_2.amount/100 or 0)
                        tax_tds_amount = round(tax_tds_amount,2)
                    if line.tds_id_2 and not line.tds_id_2.gl_account_id:
                        raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master for TDS %'))
                    if tax_tds_amount:   
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': -tax_tds_amount,
                            'account_id': line.tds_id_2 and line.tds_id_2.gl_account_id and line.tds_id_2.gl_account_id.id or False,
                            'account_analytic_id': line.account_analytic_id.id,
                            # vsis add
                            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res 
     
    def move_line_customer_product_price(self, cr, uid, invoice_id, type, context = None):
        res = []
        account = False
        if context is None:
            context = {}
        ctx = context.copy()
        
        voucher_rate = 1
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            channel = inv_id.delivery_order_id and inv_id.delivery_order_id.sale_id and inv_id.delivery_order_id.sale_id.distribution_channel and inv_id.delivery_order_id.sale_id.distribution_channel.name or False
            currency = inv_id.currency_id.name
            currency_id = inv_id.currency_id.id
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            product_id = self.pool.get('product.product').browse(cr, uid, t['product_id'])
             #name = product_id.name or False # TPT - COMMENTED By BalamuruganPurushothaman ON 20/06/2015
            name = product_id.default_code or False # TPT - Added By BalamuruganPurushothaman ON 20/06/2015 fto get GL code with respect to Product Code
            account = self.get_pro_account_id(cr,uid,name,channel)
            if not account:
                sql = '''
                SELECT sale_acc_id FROM product_product WHERE id=%s and sale_acc_id is not null
                '''%(t['product_id'])
                cr.execute(sql)
                sale_acc_id = cr.dictfetchone()
                if not sale_acc_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
                else:
                    account = sale_acc_id['sale_acc_id']
            if currency != 'INR':
                voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
            price = t['price_unit']*t['quantity']/voucher_rate
            if type=='return':
                price = -price          
            if price:
                if round(price):
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': round(price),
        #                 'account_id': sale_acc_id and sale_acc_id['sale_acc_id'] or False,
                        'account_id': account,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
        return res
    def move_line_customer_excise_duty(self, cr, uid, invoice_id, type, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        account_line_ids = [r[0] for r in cr.fetchall()]
        for line in self.browse(cr,uid,account_line_ids):
#             cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
#             for account in cr.dictfetchall():
#             ed_amount = (line.quantity * line.price_unit) * (line.invoice_id.excise_duty_id.amount and line.invoice_id.excise_duty_id.amount/100 or 0) / voucher_rate
            ed_amount = (line.quantity * line.price_unit) / voucher_rate
            sql = '''
                    SELECT cus_inv_ed_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_ed_id is not null
                '''
            cr.execute(sql)
            cus_inv_ed_id = cr.dictfetchone()
            if not cus_inv_ed_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            if ed_amount:
                if round(ed_amount):
                    price = 0.0
                    if type=='return':
                        price = -round(ed_amount)
                    else:
                        price = round(ed_amount)
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': price or 0.0,
                        'account_id': cus_inv_ed_id and cus_inv_ed_id['cus_inv_ed_id'] or False,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                    })
        return res  

    def move_line_amount_tax_credit(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.tax_service_credit:
                if line.tax_service_credit.gl_account_id:
                    account = line.tax_service_credit.gl_account_id.id
                else:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                
                tax_value = line.tax_service_credit.amount/100

                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': -tax,
                        'account_id': account,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    
    ###
    def move_line_amount_tax_credit_14(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.tax_service_credit:
                if line.tax_service_credit.gl_account_id:
                    account = line.tax_service_credit.gl_account_id.id
                else:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                
                #tax_value = line.tax_service_credit.amount/100
                tax_value = 14.00/100
                tax_value = tax_value*30/100  
                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': -tax,
                        'account_id': account,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    def move_line_amount_tax_credit_5(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.tax_service_credit:
                if line.tax_service_credit.gl_account_id:
                    account = line.tax_service_credit.gl_account_id.id
                else:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                
                #tax_value = line.tax_service_credit.amount/100
                tax_value = 0.5/100
                tax_value = tax_value*30/100  
                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': -tax,
                        'account_id': 4871, #account, #SWACHH BHARAT CESS ACCOUNT - CODE: 0000450036
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    ###
    
    def move_line_amount_tax_deducte_credit(self, cr, uid, invoice_id, context = None):
        res = []
        sum_tax = 0
        sum_tax_round = 0
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
        if not account_ids:
            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
        for account in self.browse(cr,uid,account_ids):
            for line in inv_id.invoice_line:
                basic = 0.0
                p_f = 0.0
                ed = 0.0
                tax_value = 0.0
                if line.tax_service_credit:
                    basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                    basic = round(basic)
                    if line.p_f_type == '1' :
                        p_f = basic * line.p_f/100
                        p_f = round(p_f)
                    elif line.p_f_type == '2' :
                        p_f = line.p_f
                        p_f = round(p_f)
                    elif line.p_f_type == '3' :
                        p_f = line.p_f * line.quantity
                        p_f = round(p_f)
                    else:
                        p_f = line.p_f
                        p_f = round(p_f)
                    if line.ed_type == '1' :
                        ed = (basic + p_f) * line.ed/100
                        ed = round(ed)
                    elif line.ed_type == '2' :
                        ed = line.ed
                        ed = round(ed)
                    elif line.ed_type == '3' :
                        ed = line.ed * line.quantity
                        ed = round(ed)
                    else:
                        ed = line.ed
                        ed = round(ed)                
                    
                    tax_value = line.tax_service_credit.amount/100
    
                    if line.aed_id_1:
                        tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    else:
                        tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    sum_tax += round(tax,2)
            sum_tax_round = round(sum_tax)
            deducte = sum_tax_round - round(sum_tax,2)
            if deducte > 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                    })
       
            if deducte < 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                    })
        return res
    
    ###TPT-ON 16/12/2015
    def move_line_amount_tax_deducte_credit_14(self, cr, uid, invoice_id, context = None):
        res = []
        sum_tax = 0
        sum_tax_round = 0
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
        if not account_ids:
            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
        for account in self.browse(cr,uid,account_ids):
            for line in inv_id.invoice_line:
                basic = 0.0
                p_f = 0.0
                ed = 0.0
                tax_value = 0.0
                if line.tax_service_credit:
                    basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                    basic = round(basic)
                    if line.p_f_type == '1' :
                        p_f = basic * line.p_f/100
                        p_f = round(p_f)
                    elif line.p_f_type == '2' :
                        p_f = line.p_f
                        p_f = round(p_f)
                    elif line.p_f_type == '3' :
                        p_f = line.p_f * line.quantity
                        p_f = round(p_f)
                    else:
                        p_f = line.p_f
                        p_f = round(p_f)
                    if line.ed_type == '1' :
                        ed = (basic + p_f) * line.ed/100
                        ed = round(ed)
                    elif line.ed_type == '2' :
                        ed = line.ed
                        ed = round(ed)
                    elif line.ed_type == '3' :
                        ed = line.ed * line.quantity
                        ed = round(ed)
                    else:
                        ed = line.ed
                        ed = round(ed)                
                    
                    #tax_value = line.tax_service_credit.amount/100
                    tax_value += 14.00/100
                    tax_value = tax_value*30/100
    
                    if line.aed_id_1:
                        tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    else:
                        tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    sum_tax += round(tax,2)
            sum_tax_round = round(sum_tax)
            deducte = sum_tax_round - round(sum_tax,2)
            if deducte > 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                    })
       
            if deducte < 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                    })
        return res
    def move_line_amount_tax_deducte_credit_5(self, cr, uid, invoice_id, context = None):
        res = []
        sum_tax = 0
        sum_tax_round = 0
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
        if not account_ids:
            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
        for account in self.browse(cr,uid,account_ids):
            for line in inv_id.invoice_line:
                basic = 0.0
                p_f = 0.0
                ed = 0.0
                tax_value = 0.0
                if line.tax_service_credit:
                    basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                    basic = round(basic)
                    if line.p_f_type == '1' :
                        p_f = basic * line.p_f/100
                        p_f = round(p_f)
                    elif line.p_f_type == '2' :
                        p_f = line.p_f
                        p_f = round(p_f)
                    elif line.p_f_type == '3' :
                        p_f = line.p_f * line.quantity
                        p_f = round(p_f)
                    else:
                        p_f = line.p_f
                        p_f = round(p_f)
                    if line.ed_type == '1' :
                        ed = (basic + p_f) * line.ed/100
                        ed = round(ed)
                    elif line.ed_type == '2' :
                        ed = line.ed
                        ed = round(ed)
                    elif line.ed_type == '3' :
                        ed = line.ed * line.quantity
                        ed = round(ed)
                    else:
                        ed = line.ed
                        ed = round(ed)                
                    
                    #tax_value = line.tax_service_credit.amount/100
                    tax_value += 0.5/100
                    tax_value = tax_value*30/100
    
                    if line.aed_id_1:
                        tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    else:
                        tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    sum_tax += round(tax,2)
            sum_tax_round = round(sum_tax)
            deducte = sum_tax_round - round(sum_tax,2)
            if deducte > 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': 4871, #account, #SWACHH BHARAT CESS ACCOUNT - CODE: 0000450036
                    'account_analytic_id': False,
                    })
       
            if deducte < 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': 4871, #account, #SWACHH BHARAT CESS ACCOUNT - CODE: 0000450036
                    'account_analytic_id': False,
                    })
        return res
    ###
    def move_line_amount_tax(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            is_gst = False
            account_cgst_id = False
            account_sgst_id = False
            account_igst_id = False
            for gst_tax in line.invoice_line_tax_id:
                if 'GST' in gst_tax.description.upper():
                    is_gst = True
                    if gst_tax.child_depend:
                        for tax_child in gst_tax.child_ids:
                            if not tax_child.gl_account_id:
                                raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(tax_child.name)))
                            if 'CGST' in tax_child.description.upper():
                                account_cgst_id = tax_child.gl_account_id.id
                            if 'SGST' in tax_child.description.upper():
                                account_sgst_id = tax_child.gl_account_id.id
                    else:
                        if 'IGST' in gst_tax.description.upper():
                            if not gst_tax.gl_account_id:
                                raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(gst_tax.name)))
                            account_igst_id = gst_tax.gl_account_id.id
                    break
                
            if is_gst:
                tax_cgst = line.tax_cgst_amount * voucher_rate
                tax_sgst = line.tax_sgst_amount * voucher_rate
                tax_igst = line.tax_igst_amount * voucher_rate
                if tax_cgst:
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax_cgst,2),
                        'account_id': account_cgst_id,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                if tax_sgst:
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax_sgst,2),
                        'account_id': account_sgst_id,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                if tax_igst:
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax_igst,2),
                        'account_id': account_igst_id,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
            else:
                basic = 0.0
                p_f = 0.0
                ed = 0.0
                tax_value = 0.0
                if line.invoice_line_tax_id:
                    tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                    for tax_gl_account_id in tax_gl_account_ids:
                        if tax_gl_account_id:
                            account = tax_gl_account_id.id
                        else:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                    basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                    basic = round(basic,2)
                    if line.p_f_type == '1' :
                        p_f = basic * line.p_f/100
                        p_f = round(p_f,2)
                    elif line.p_f_type == '2' :
                        p_f = line.p_f
                        p_f = round(p_f,2)
                    elif line.p_f_type == '3' :
                        p_f = line.p_f * line.quantity
                        p_f = round(p_f,2)
                    else:
                        p_f = line.p_f
                        p_f = round(p_f,2)
                    if line.ed_type == '1' :
                        ed = (basic + p_f) * line.ed/100
                        ed = round(ed,2)
                    elif line.ed_type == '2' :
                        ed = line.ed
                        ed = round(ed,2)
                    elif line.ed_type == '3' :
                        ed = line.ed * line.quantity
                        ed = round(ed,2)
                    else:
                        ed = line.ed
                        ed = round(ed,2)                
                    tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                     
                    for tax_amount in tax_amounts:
                        tax_value += tax_amount/100
                         
                    if line.aed_id_1:
                        tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                        tax = round(tax,2)      
                    else:
                        tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                        tax = round(tax,2)
                    if tax:    
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': round(tax,2),
                            'account_id': account,
                            'account_analytic_id': line.account_analytic_id.id,
                            # vsis add
                            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                            })
        return res
    ###
    ###
    def move_line_amount_tax_cst(self, cr, uid, invoice_id, context = None):       
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:              
            tax_amounts = [r.amount for r in line.invoice_line_tax_id]
            for tax_amount in tax_amounts:
                tax_value += tax_amount/100
                
                     
                
            return tax
    ###
    def move_line_amount_tax_sbc_14(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.invoice_line_tax_id:
                tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                for tax_gl_account_id in tax_gl_account_ids:
                    if tax_gl_account_id:
                        account = tax_gl_account_id.id
                    else:
                        raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                #tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                 
                #===============================================================
                # for tax_amount in tax_amounts:
                #     tax_value += tax_amount/100
                #===============================================================
                tax_value += 14.00/100    
                #Added by P.vinothkumar on 21/06/2016 for calculate tax(krishi kalyan)     
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_value = tax_value*30/100
                #Added by P.vinothkumar on 21/06/2016 for calculate tax(krishi kalyan)   
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_value = tax_value*30/100      
                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                # Added by P.vinothkumar on 24/10/2016 for calculate null tax values    
                elif not line.tax_id:
                    tax=0.0          
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax,2),
                        'account_id': account,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    ###
    def move_line_amount_tax_swachh_bharat_cess_5(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.invoice_line_tax_id:
                tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                for tax_gl_account_id in tax_gl_account_ids:
                    if tax_gl_account_id:
                        account = tax_gl_account_id.id
                    else:
                        raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                #tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                 
                #===============================================================
                # for tax_amount in tax_amounts:
                #     tax_value += tax_amount/100
                #===============================================================
                tax_value = 0.5/100
#                 if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
#                     tax_value = tax_value*30/100     
                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                # Added by P.vinothkumar on 21/06/2016 for calculate null tax values    
                elif not line.tax_id:
                    tax=0.0          
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)                     
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax,2),
                        'account_id': 4871, #account, #SWACHH BHARAT CESS ACCOUNT - CODE: 0000450036
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    ###
    def move_line_amount_tax_krishi_kalyan_cess_5(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.invoice_line_tax_id:
                tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                for tax_gl_account_id in tax_gl_account_ids:
                    if tax_gl_account_id:
                        account = tax_gl_account_id.id
                    else:
                        raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                #tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                 
                #===============================================================
                # for tax_amount in tax_amounts:
                #     tax_value += tax_amount/100
                #===============================================================
                tax_value = 0.5/100
                #Added By P.vinothkumar - ON 21/06/2016 - FOR (calculate tax for krishikalanyan cess) 
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax = 0.0
               #Added By P.vinothkumar - ON 21/06/2016 - FOR (calculate tax for krishikalanyan cess)   
                elif line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_value = tax_value*30/100
                    base_amount = round(line.fright,2)
                    tax= (base_amount)* (tax_value) * voucher_rate
                    tax = round(tax,2)     
                elif line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                #Added By P.vinothkumar - ON 21/06/2016 - FOR (tax is nullable)         
                elif not line.tax_id:
                    tax=0.0          
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)                     
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax,2),
                        'account_id': 5091, #account, #KRISHI KALYAN CESS ACCOUNT - CODE: 0000450036
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    #TPT-BalamuruganPurushothaman - ON 04/11/2015 - TO CREATE POSTGING ENTRY FOR TAX AMOUNT
    def tpt_move_line_amount_tax(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            
            is_gst = False
            account_cgst_id = False
            account_sgst_id = False
            account_igst_id = False
            if line.tax_id:
                if 'GST' in line.tax_id.description.upper():
                    is_gst = True
                    if line.tax_id.child_depend:
                        for tax_child in line.tax_id.child_ids:
                            if not tax_child.gl_account_id:
                                raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(tax_child.name)))
                            if 'CGST' in tax_child.description.upper():
                                account_cgst_id = tax_child.gl_account_id.id
                            if 'SGST' in tax_child.description.upper():
                                account_sgst_id = tax_child.gl_account_id.id
                    else:
                        if 'IGST' in line.tax_id.description.upper():
                            if not line.tax_id.gl_account_id:
                                raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(line.tax_id.name)))
                            account_igst_id = line.tax_id.gl_account_id.id
                
            if is_gst:
                tax_cgst = line.tax_cgst_amount * voucher_rate
                tax_sgst = line.tax_sgst_amount * voucher_rate
                tax_igst = line.tax_igst_amount * voucher_rate
                if tax_cgst:
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax_cgst,2),
                        'account_id': account_cgst_id,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                if tax_sgst:
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax_sgst,2),
                        'account_id': account_sgst_id,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                if tax_igst:
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax_igst,2),
                        'account_id': account_igst_id,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
            else:
            
                basic = 0.0
                p_f = 0.0
                ed = 0.0
                tax_value = 0.0
                #if line.invoice_line_tax_id:
                if line.tax_id:
                    tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                    #===============================================================
                    # for tax_gl_account_id in tax_gl_account_ids:
                    #     if tax_gl_account_id:
                    #         account = tax_gl_account_id.id
                    #     else:
                    #         raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                    #===============================================================
                    account = line.tax_id.gl_account_id and line.tax_id.gl_account_id.id or False
                    basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                    basic = round(basic,2)
                    if line.p_f_type == '1' :
                        p_f = basic * line.p_f/100
                        p_f = round(p_f,2)
                    elif line.p_f_type == '2' :
                        p_f = line.p_f
                        p_f = round(p_f,2)
                    elif line.p_f_type == '3' :
                        p_f = line.p_f * line.quantity
                        p_f = round(p_f,2)
                    else:
                        p_f = line.p_f
                        p_f = round(p_f,2)
                    if line.ed_type == '1' :
                        ed = (basic + p_f) * line.ed/100
                        ed = round(ed,2)
                    elif line.ed_type == '2' :
                        ed = line.ed
                        ed = round(ed,2)
                    elif line.ed_type == '3' :
                        ed = line.ed * line.quantity
                        ed = round(ed,2)
                    else:
                        ed = line.ed
                        ed = round(ed,2)                
                    tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                    
                    for tax_amount in tax_amounts:
                        tax_value += tax_amount/100
                        
                    if line.aed_id_1:
                        tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                        tax = round(tax,2)      
                    else:
                        tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                        tax = round(tax,2)
                    tax = (basic +  ed)* (line.tax_id and line.tax_id.amount / 100 or 0)
                    if tax:    
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': round(tax,2),
                            'account_id': account,
                            'account_analytic_id': line.account_analytic_id.id,
                            # vsis add
                            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                            })
        return res
    
    ###TPT-ON 16/12/2015
    def tpt_move_line_amount_tax_14(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            #if line.invoice_line_tax_id:
            if line.tax_id:
                tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                #===============================================================
                # for tax_gl_account_id in tax_gl_account_ids:
                #     if tax_gl_account_id:
                #         account = tax_gl_account_id.id
                #     else:
                #         raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                #===============================================================
                account = line.tax_id.gl_account_id and line.tax_id.gl_account_id.id or False
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                
                #===============================================================
                # for tax_amount in tax_amounts:
                #     tax_value += tax_amount/100
                #===============================================================
                if line.tax_id and line.tax_id.description=='STax 14.5%':
                    tax_value += 14.00/100
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_value += 14.00/100
                    tax_value += tax_value*30/100
#                 if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Cr)':
#                     tax_value += 14.00/100
#                     tax_value += tax_value*30/100
                # Added by P.vinothkumar on 06/08/2016 for adding legal(14.5%)     
                if line.tax_id and line.tax_id.description=='STax 14.5% for Legal (Dr)':
                    tax_value += 14.00/100 

                    
                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)      
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                tax = (basic +  ed)* tax_value #(line.tax_id and line.tax_id.amount / 100 or 0)
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax,2),
                        'account_id': account,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    def tpt_move_line_amount_tax_5(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            #if line.invoice_line_tax_id:
            if line.tax_id:
                tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                #===============================================================
                # for tax_gl_account_id in tax_gl_account_ids:
                #     if tax_gl_account_id:
                #         account = tax_gl_account_id.id
                #     else:
                #         raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                #===============================================================
                account = line.tax_id.gl_account_id and line.tax_id.gl_account_id.id or False
                basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                basic = round(basic,2)
                if line.p_f_type == '1' :
                    p_f = basic * line.p_f/100
                    p_f = round(p_f,2)
                elif line.p_f_type == '2' :
                    p_f = line.p_f
                    p_f = round(p_f,2)
                elif line.p_f_type == '3' :
                    p_f = line.p_f * line.quantity
                    p_f = round(p_f,2)
                else:
                    p_f = line.p_f
                    p_f = round(p_f,2)
                if line.ed_type == '1' :
                    ed = (basic + p_f) * line.ed/100
                    ed = round(ed,2)
                elif line.ed_type == '2' :
                    ed = line.ed
                    ed = round(ed,2)
                elif line.ed_type == '3' :
                    ed = line.ed * line.quantity
                    ed = round(ed,2)
                else:
                    ed = line.ed
                    ed = round(ed,2)                
                tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                
                #===============================================================
                # for tax_amount in tax_amounts:
                #     tax_value += tax_amount/100
                #===============================================================
                if line.tax_id and line.tax_id.description=='STax 14.5%':
                    tax_value += 0.5/100
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_value += 0.5/100
                    tax_value += tax_value*30/100
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_value += 0.5/100
                    tax_value += tax_value*30/100    
                    
#                 if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Cr)':
#                     tax_value += 0.5/100
#                     tax_value += tax_value*30/100
                    
                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    tax = round(tax,2)      
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    tax = round(tax,2)
                tax = (basic +  ed)* tax_value #(line.tax_id and line.tax_id.amount / 100 or 0)
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax,2),
                        'account_id': 4871, #account, #SWACHH BHARAT CESS ACCOUNT - CODE: 0000450036
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    ###
    def move_line_amount_tax_without_po_deducte(self, cr, uid, invoice_id, context = None):
        res = []
        sum_tax = 0.0
        sum_tax_round = 0.0
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
        if not account_ids:
            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
        for account in self.browse(cr,uid,account_ids):
            for line in inv_id.invoice_line:
                basic = 0.0
                p_f = 0.0
                ed = 0.0
                tax_value = 0.0
                if line.invoice_line_tax_id:
                    tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                    for tax_amount in tax_amounts:
                        tax_value += tax_amount/100
                    basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                    basic = round(basic)
                    if line.p_f_type == '1' :
                        p_f = basic * line.p_f/100
                        p_f = round(p_f)
                    elif line.p_f_type == '2' :
                        p_f = line.p_f
                        p_f = round(p_f)
                    elif line.p_f_type == '3' :
                        p_f = line.p_f * line.quantity
                        p_f = round(p_f)
                    else:
                        p_f = line.p_f
                        p_f = round(p_f)
                    if line.ed_type == '1' :
                        ed = (basic + p_f) * line.ed/100
                        ed = round(ed)
                    elif line.ed_type == '2' :
                        ed = line.ed
                        ed = round(ed)
                    elif line.ed_type == '3' :
                        ed = line.ed * line.quantity
                        ed = round(ed)
                    else:
                        ed = line.ed
                        ed = round(ed)
                    if line.aed_id_1:
                        tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                    else:
                        tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                    sum_tax += round(tax,2)
            sum_tax_round = round(sum_tax)
            deducte = sum_tax_round - round(sum_tax,2)
            if deducte > 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                    })
       
            if deducte < 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                    })
        return res
    
    def move_line_amount_tax1(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif line.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.invoice_line_tax_id:
                tax_gl_account_ids = [r.gl_account_id for r in line.invoice_line_tax_id]
                for tax_gl_account_id in tax_gl_account_ids:
                    if tax_gl_account_id:
                        account = tax_gl_account_id.id
                    else:
                        raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master !'))
                tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                
                for tax_amount in tax_amounts:
                    tax_value += tax_amount/100

                if line.aed_id_1:
                    tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                else:
                    tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                if tax:    
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price': round(tax),
                        'account_id': account,
                        'account_analytic_id': line.account_analytic_id.id,
                        # vsis add
                        'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                        'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                    
#                     if 'CST' in tax_name:
#                         tax_amounts = [r.amount for r in line.invoice_line_tax_id]
#                         for tax_amount in tax_amounts:
#                             tax_value += tax_amount/100
#                             basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
#                             if line.p_f_type == '1' :
#                                 p_f = basic * line.p_f/100
#                             elif line.p_f_type == '2' :
#                                 p_f = line.p_f
#                             elif line.p_f_type == '3' :
#                                 p_f = line.p_f * line.quantity
#                             else:
#                                 p_f = line.p_f
#                             if line.ed_type == '1' :
#                                 ed = (basic + p_f) * line.ed/100
#                             elif line.ed_type == '2' :
#                                 ed = line.ed
#                             elif line.ed_type == '3' :
#                                 ed = line.ed * line.quantity
#                             else:
#                                 ed = line.ed
#                             tax = (basic + p_f + ed)*(tax_value) * voucher_rate
#                         sql = '''
#                             SELECT sup_inv_cst_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_cst_id is not null
#                         '''
#                         cr.execute(sql)
#                         sup_inv_cst_id = cr.dictfetchone()
#                         if sup_inv_cst_id:
#                             account = sup_inv_cst_id and sup_inv_cst_id['sup_inv_cst_id'] or False
#                         else:
#                             raise osv.except_osv(_('Warning!'),_('Account is not null, please configure CST Receivables in GL Posting Configrution !'))
#                         if tax:    
#                             if round(tax):
#                                 res.append({
#                                     'type':'tax',
#                                     'name':line.name,
#                                     'price_unit': line.price_unit,
#                                     'quantity': 1,
#                                     'price': round(tax),
#                                     'account_id': account,
#                                     'account_analytic_id': line.account_analytic_id.id,
#                                     })
#                             break
#                     elif 'VAT' in tax_name:
#                         tax_amounts = [r.amount for r in line.invoice_line_tax_id]
#                         for tax_amount in tax_amounts:
#                             tax_value += tax_amount/100
#                             basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
#                             if line.p_f_type == '1' :
#                                 p_f = basic * line.p_f/100
#                             elif line.p_f_type == '2' :
#                                 p_f = line.p_f
#                             elif line.p_f_type == '3' :
#                                 p_f = line.p_f * line.quantity
#                             else:
#                                 p_f = line.p_f
#                             if line.ed_type == '1' :
#                                 ed = (basic + p_f) * line.ed/100
#                             elif line.ed_type == '2' :
#                                 ed = line.ed
#                             elif line.ed_type == '3' :
#                                 ed = line.ed * line.quantity
#                             else:
#                                 ed = line.ed
#                             tax = (basic + p_f + ed)*(tax_value) * voucher_rate
#                         sql = '''
#                             SELECT sup_inv_vat_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_vat_id is not null
#                         '''
#                         cr.execute(sql)
#                         sup_inv_vat_id = cr.dictfetchone()
#                         if sup_inv_vat_id:
#                             account = sup_inv_vat_id and sup_inv_vat_id['sup_inv_vat_id'] or False
#                         else:
#                             raise osv.except_osv(_('Warning!'),_('Account is not null, please configure VAT Receivables in GL Posting Configrution !'))
#                         if tax:     
#                             if round(tax):
#                                 res.append({
#                                     'type':'tax',
#                                     'name':line.name,
#                                     'price_unit': line.price_unit,
#                                     'quantity': 1,
#                                     'price': round(tax),
#                                     'account_id': account,
#                                     'account_analytic_id': line.account_analytic_id.id,
#                                 })
#                             break
#                     else:
#                         tax_amounts = [r.amount for r in line.invoice_line_tax_id]
#                         for tax_amount in tax_amounts:
#                             tax_value += tax_amount/100
#                             basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
#                             if line.p_f_type == '1' :
#                                 p_f = basic * line.p_f/100
#                             elif line.p_f_type == '2' :
#                                 p_f = line.p_f
#                             elif line.p_f_type == '3' :
#                                 p_f = line.p_f * line.quantity
#                             else:
#                                 p_f = line.p_f
#                             if line.ed_type == '1' :
#                                 ed = (basic + p_f) * line.ed/100
#                             elif line.ed_type == '2' :
#                                 ed = line.ed
#                             elif line.ed_type == '3' :
#                                 ed = line.ed * line.quantity
#                             else:
#                                 ed = line.ed
#                             tax = (basic + p_f + ed)*(tax_value) * voucher_rate
#                         sql = '''
#                             SELECT sup_inv_vat_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_vat_id is not null
#                         '''
#                         cr.execute(sql)
#                         sup_inv_vat_id = cr.dictfetchone()
#                         if sup_inv_vat_id:
#                             account = sup_inv_vat_id and sup_inv_vat_id['sup_inv_vat_id'] or False
#                         sql = '''
#                             SELECT sup_inv_cst_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_cst_id is not null
#                         '''
#                         cr.execute(sql)
#                         sup_inv_cst_id = cr.dictfetchone()
#                         if sup_inv_cst_id:
#                             account = sup_inv_cst_id and sup_inv_cst_id['sup_inv_cst_id'] or False
#                         if sup_inv_vat_id or sup_inv_cst_id:
#                             if tax:  
#                                 if round(tax):
#                                     res.append({
#                                         'type':'tax',
#                                         'name':line.name,
#                                         'price_unit': line.price_unit,
#                                         'quantity': 1,
#                                         'price': round(tax),
#                                         'account_id': account,
#                                         'account_analytic_id': line.account_analytic_id.id,
#                                     })
#                                     break
#                                 break
#                         else :
#                                 raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
        return res
    
    def move_line_customer_amount_tax(self, cr, uid, invoice_id, type, context = None):
        res = []
        voucher_rate = 1
        tax = 0.0
        if context is None:
            context = {}
        ctx = context.copy()
#         ctx.update({'date': time.strftime('%Y-%m-%d')})
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            if inv_id.sale_tax_id and 'GST' in inv_id.sale_tax_id.description.upper():
                tax_cgst = 0
                tax_sgst = 0
                tax_igst = 0
                if inv_id.sale_tax_id.child_depend:
                    for tax_child in inv_id.sale_tax_id.child_ids:
                        if not tax_child.gl_account_id:
                            raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(tax_child.name)))
                        if 'CGST' in tax_child.description.upper():
                            tax_cgst = inv_id.amount_total_cgst_tax
                            account_cgst_id = tax_child.gl_account_id.id
                        if 'SGST' in tax_child.description.upper():
                            tax_sgst = inv_id.amount_total_sgst_tax
                            account_sgst_id = tax_child.gl_account_id.id
                else:
                    if 'IGST' in inv_id.sale_tax_id.description.upper():
                        if not inv_id.sale_tax_id.gl_account_id:
                            raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(inv_id.sale_tax_id.name)))
                        tax_igst = inv_id.amount_total_igst_tax
                        account_igst_id = inv_id.sale_tax_id.gl_account_id.id
                tax_cgst = tax_cgst / voucher_rate
                tax_sgst = tax_sgst / voucher_rate
                tax_igst = tax_igst / voucher_rate
                if type=='return':
                    tax_cgst = -round(tax_cgst)
                    tax_sgst = -round(tax_sgst)
                    tax_igst = -round(tax_igst)
                else:
                    tax_cgst = round(tax_cgst)
                    tax_sgst = round(tax_sgst)
                    tax_igst = round(tax_igst)
                if tax_cgst:
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': tax_cgst,
                        'account_id': account_cgst_id,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
                if tax_sgst:
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': tax_sgst,
                        'account_id': account_sgst_id,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
                if tax_igst:
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': tax_igst,
                        'account_id': account_igst_id,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
            else:
                cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
                for account in cr.dictfetchall():
                    tax = account['amount_tax'] / voucher_rate
                    if type=='return':
                        tax = -round(tax)
                    else:
                        tax = round(tax)
                    if inv_id.sale_tax_id:
                        if 'CST' in inv_id.sale_tax_id.name:
                            sql = '''
                                SELECT cus_inv_cst_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_cst_id is not null
                            '''
                            cr.execute(sql)
                            cus_inv_cst_id = cr.dictfetchone()
                            if cus_inv_cst_id:
                                account = cus_inv_cst_id and cus_inv_cst_id['cus_inv_cst_id'] or False
                            else :
                                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure CST Payable in GL Posting Configrution !'))
                            if tax:
                                if round(tax):
                                    res.append({
                                        'type':'tax',
                                        'name':t['name'],
                                        'price_unit': t['price_unit'],
                                        'quantity': 1,
                                        'price': tax,
                                        'account_id': account,
                                        'account_analytic_id': t['account_analytic_id'],
                                        # vsis add
                                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                                    })
                                    break
                        elif 'VAT' in inv_id.sale_tax_id.name:
                            sql = '''
                                SELECT cus_inv_vat_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_vat_id is not null
                            '''
                            cr.execute(sql)
                            cus_inv_vat_id = cr.dictfetchone()
                            if cus_inv_vat_id:
                                account = cus_inv_vat_id and cus_inv_vat_id['cus_inv_vat_id'] or False
                            else :
                                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure VAT Payable in GL Posting Configrution !'))
                            if tax:    
                                if round(tax):
                                    res.append({
                                        'type':'tax',
                                        'name':t['name'],
                                        'price_unit': t['price_unit'],
                                        'quantity': 1,
                                        'price': tax,
                                        'account_id': account,
                                        'account_analytic_id': t['account_analytic_id'],
                                        # vsis add
                                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                                    })
                                    break
                        else:
                            sql = '''
                                SELECT cus_inv_vat_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_vat_id is not null
                            '''
                            cr.execute(sql)
                            cus_inv_vat_id = cr.dictfetchone()
                            if cus_inv_vat_id:
                                account = cus_inv_vat_id and cus_inv_vat_id['cus_inv_vat_id'] or False
                            sql = '''
                                SELECT cus_inv_cst_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_cst_id is not null
                            '''
                            cr.execute(sql)
                            cus_inv_cst_id = cr.dictfetchone()
                            if cus_inv_cst_id:
                                account = cus_inv_cst_id and cus_inv_cst_id['cus_inv_cst_id'] or False
                            if cus_inv_cst_id or cus_inv_vat_id:
                                if tax:
                                    if round(tax):
                                        res.append({
                                            'type':'tax',
                                            'name':t['name'],
                                            'price_unit': t['price_unit'],
                                            'quantity': 1,
                                            'price': tax,
                                            'account_id': account,
                                            'account_analytic_id': t['account_analytic_id'],
                                            # vsis add
                                            'tpt_grn_id':t and t['tpt_grn_id'] or False,
                                            'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                                        })
                                        break
                            else :
                                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            break
        return res 
    
    def move_line_fright(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
                sql = '''
                    SELECT sup_inv_fright_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_fright_id is not null
                '''
                cr.execute(sql)
                sup_inv_fright_id = cr.dictfetchone()
                if not sup_inv_fright_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
                if account['fright']:    
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': account['fright'],
                        'account_id': sup_inv_fright_id and sup_inv_fright_id['sup_inv_fright_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
                    break
                break
            break
        return res 
    
    def move_line_amount_round_off(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
                else:
                    if account['amount_round_off']:    
                        res.append({
                            'type':'tax',
                            'name':t['name'],
                            'price_unit': t['price_unit'],
                            'quantity': 1,
                            'price': account['amount_round_off'],
                            'account_id': account_ids[0],
                            'account_analytic_id': t['account_analytic_id'],
                            # vsis add
                            'tpt_grn_id':t and t['tpt_grn_id'] or False,
                            'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
                break
            break
        return res
    
    def move_line_fright_change_si(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            fright = 0.0
            tax_value = 0.0
            if line.product_id.product_asset_acc_id:
                account = line.product_id.product_asset_acc_id.id
            else:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Product Asset Account in Product master !'))
            tax_amounts = [r.amount for r in line.invoice_line_tax_id]
            for tax_amount in tax_amounts:
                tax_value += tax_amount/100
            basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
            basic = round(basic,2)
            if line.p_f_type == '1' :
                p_f = basic * line.p_f/100
                p_f = round(p_f,2)
            elif line.p_f_type == '2' :
                p_f = line.p_f
                p_f = round(p_f,2)
            elif line.p_f_type == '3' :
                p_f = line.p_f * line.quantity
                p_f = round(p_f,2)
            else:
                p_f = line.p_f
                p_f = round(p_f,2)
            if line.ed_type == '1' :
                ed = (basic + p_f) * line.ed/100
                ed = round(ed,2)
            elif line.ed_type == '2' :
                ed = line.ed
                ed = round(ed,2)
            elif line.ed_type == '3' :
                ed = line.ed * line.quantity
                ed = round(ed,2)
            else:
                ed = line.ed
                ed = round(ed,2)
            if line.aed_id_1:
                tax = (basic + p_f + ed + line.aed_id_1)*(tax_value) * voucher_rate
                tax = round(tax,2)
            else:
                tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                tax = round(tax,2)
            if line.fright_type == '1' :
                if currency != 'INR':
                    fright = ((basic + p_f + ed + tax) * line.fright/100)/ voucher_rate
                    fright = round(fright,2)
                else:
                    fright = (basic + p_f + ed + tax) * line.fright/100
                    fright = round(fright,2)
            elif line.fright_type == '2' :
                if currency != 'INR':
                    fright = (line.fright)/ voucher_rate
                    fright = round(fright,2)
                else:
                    fright = line.fright
                    fright = round(fright,2)
            elif line.fright_type == '3' :
                if currency != 'INR':
                    fright = (line.fright * line.quantity)/ voucher_rate
                    fright = round(fright,2)
                else:
                    fright = line.fright * line.quantity
                    fright = round(fright,2)
            else:
                if currency != 'INR':
                    fright = (line.fright)/ voucher_rate
                    fright = round(fright,2)
                else:
                    fright = line.fright
                    fright = round(fright,2)
            if fright:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': fright,
                    'account_id': account,
                    'account_analytic_id': line.account_analytic_id and line.account_analytic_id.id or False,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                })
        return res 
    
    def move_line_customer_fright(self, cr, uid, invoice_id, type, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            sql = '''
                    SELECT cus_inv_fright_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_fright_id is not null
                '''
            cr.execute(sql)
            cus_inv_fright_id = cr.dictfetchone()
            if not cus_inv_fright_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            if t['freight']:
                if round(t['freight']):
                    price = 0.0
                    if type=='return':
                        price = -round(t['freight'] * t['quantity']/ voucher_rate)
                    else:
                        price = round(t['freight'] * t['quantity']/ voucher_rate)
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': price or 0.00,
                        'account_id': cus_inv_fright_id and cus_inv_fright_id['cus_inv_fright_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                    })
        return res 
    
    def move_line_customer_insurance(self, cr, uid, invoice_id, type, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
#         if inv_id.sale_tax_id and inv_id.sale_tax_id.:
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            sql = '''
                    SELECT cus_inv_insurance_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_insurance_id is not null
                '''
            cr.execute(sql)
            cus_inv_insurance_id = cr.dictfetchone()
            if not cus_inv_insurance_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            if t['insurance']:
                if (t['insurance']): # By BalamuruganPurushothaman ON 20/06/2015 Removed roundoff to get the insurance value for all the decimals.
                    #TPT-BM - ON 01/07/2016
                    price = 0.0
                    if type=='return':
                        price = -round(t['insurance'] * t['quantity']/ voucher_rate)
                    else:
                        price = round(t['insurance'] * t['quantity']/ voucher_rate)
                    #TPT-BM
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': price or 0.00,
                        'account_id': cus_inv_insurance_id and cus_inv_insurance_id['cus_inv_insurance_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                    })
        return res
    
    
    def move_line_excise_duty(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
#             basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
#             if (t['p_f_type'] == '1'):
#                 p_f = basic * t['p_f']/100
#             else:
#                 p_f = t['p_f']
#             if t['ed_type'] == '1' :
#                 ed = (basic + p_f) * t['ed']/100
#             else:
#                 ed = t['ed']
                sql = '''
                    SELECT sup_inv_ed_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_ed_id is not null
                '''
                cr.execute(sql)
                sup_inv_ed_id = cr.dictfetchone()
                if not sup_inv_ed_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
                if account['excise_duty']:
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': account['excise_duty'],
                        'account_id': sup_inv_ed_id and sup_inv_ed_id['sup_inv_ed_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
                    break
            break
        return res
    
    def move_line_aed(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
        for account in cr.dictfetchall():
            sql = '''
                SELECT sup_inv_aed_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_aed_id is not null
            '''
            cr.execute(sql)
            sup_inv_aed_id = cr.dictfetchone()
            if not sup_inv_aed_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            if account['aed']:    
                res.append({
                    'type':'tax',
                    'name':'/',
                    'price_unit': account['aed'],
                    'quantity': 1,
                    'price': account['aed'],
                    'account_id': sup_inv_aed_id and sup_inv_aed_id['sup_inv_aed_id'] or False,
                    'account_analytic_id': False,
                })
                break
            break
        return res
    
    def move_line_pf(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
#             basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
#             if (t['p_f_type'] == '1'):
#                 p_f = basic * t['p_f']/100
#             else:
#                 p_f = t['p_f']
                
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
                sql = '''
                    SELECT sup_inv_pf_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_pf_id is not null
                '''
                cr.execute(sql)
                sup_inv_pf_id = cr.dictfetchone()
                if not sup_inv_pf_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
                if account['p_f_charge']:
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': account['p_f_charge'],
                        'account_id': sup_inv_pf_id and sup_inv_pf_id['sup_inv_pf_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                        # vsis add
                        'tpt_grn_id':t and t['tpt_grn_id'] or False,
                        'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                    })
                    break
                break
            break
        return res 
    def move_line_price_different(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (t['invoice_id'],))
            for account in cr.dictfetchall():
                result = False
                total = account['amount_untaxed'] + account['p_f_charge'] + account['excise_duty'] + account['amount_tax'] + account['fright']
                if (total < account['amount_total']):
                    result = account['amount_total'] - total
                if (total > account['amount_total']):
                    result = -(total - account['amount_total'])
                sql = '''
                    SELECT sup_inv_price_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_price_id is not null
                '''
                cr.execute(sql)
                sup_inv_price_id = cr.dictfetchone()
                if not sup_inv_price_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
                if result:
                    res.append({
                        'type':'tax',
                        'name':account['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': result,
                        'account_id': sup_inv_price_id and sup_inv_price_id['sup_inv_price_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                    })
                    break
            break
        return res
    
    def move_line_fi_base(self, cr, uid, invoice_id, context = None):
        res = []
        account = False
        if context is None:
            context = {}
        ctx = context.copy()
#         ctx.update({'date': time.strftime('%Y-%m-%d')})
        voucher_rate = 1
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name
            currency_id = inv_id.currency_id.id
            #ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
            #TPT-By BalamuruganPurushothaman - ON 22/02/2016 -  TO TAKE CURRENCY RATE BASED ON INVOICE TYPE
            if inv_id.type=='in_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'buying' })
            elif inv_id.type=='out_invoice':
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d'), 'rate_type': 'selling'})
            else:
                ctx.update({'date': inv_id.date_invoice or time.strftime('%Y-%m-%d')})
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            product_id = self.pool.get('product.product').browse(cr, uid, t['product_id'])
            name = product_id.name or False
            sql = '''
            SELECT product_asset_acc_id FROM product_product WHERE id=%s and product_asset_acc_id is not null
            '''%(t['product_id'])
            cr.execute(sql)
            product_asset_acc_id = cr.dictfetchone()
            if not product_asset_acc_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Product Asset Account in Material master !'))
            else:
                account = product_asset_acc_id['product_asset_acc_id']
            if currency != 'INR':
                voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
            
            if t['fright_fi_type'] == '2':
                price = t['fright']
                price = round(price,2)
            else:
                price = t['fright']*t['quantity']
                price = round(price,2)
            if price:
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': price,
    #                 'account_id': sale_acc_id and sale_acc_id['sale_acc_id'] or False,
                    'account_id': account,
                    'account_analytic_id': t['account_analytic_id'],
                    # vsis add
                    'tpt_grn_id':t and t['tpt_grn_id'] or False,
                    'tpt_grn_line_id':t and t['tpt_grn_line_id'] or False,
                })           
        return res
    
    def move_line_fi_debit(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
        # Added by P.VINOTHKUMAR ON 05/12/2017 for fixing GST/IGST in freight invoice 
            if line.tax_id and not line.tax_id.gl_account_id and not line.tax_id.child_ids:
                 raise osv.except_osv(_('Warning!'),_('GL Account is not null, please configure it in Tax Master!'))
            if line.tax_id and 'GST' in line.tax_id.description.upper():
                tax_cgst = 0
                tax_sgst = 0
                tax_igst = 0
                if line.tax_id.child_ids:
                    for tax_child in line.tax_id.child_ids:
                        if 'CGST' in tax_child.description.upper():
                            tax_cgst = invoice.amount_total_cgst_tax
                            account_cgst_id = tax_child.gl_account_id.id
                        if 'SGST' in tax_child.description.upper():
                            tax_sgst = invoice.amount_total_sgst_tax
                            account_sgst_id = tax_child.gl_account_id.id
                else:
                    if 'IGST' in line.tax_id.description.upper():
                        if not line.tax_id.gl_account_id.id:
                            raise osv.except_osv(_('Warning!'),_('GL account should be configured for Tax "%s"!'%(line.tax_id.name)))
                        tax_igst = invoice.amount_total_igst_tax
                        account_igst_id = line.tax_id.gl_account_id.id
                 # Commented by P.VINOTHKUMAR ON ON 05/12/2017 for fixing GST/IGST in freight invoice          
               #TPT End     
#             if line.fright_fi_type == '2':
#                 base_amount = round(line.fright,2)
#                 tax_debit_amount = base_amount*(line.tax_id and line.tax_id.amount/100 or 0)
#                 tax_debit_amount = round(tax_debit_amount,2)
#             else:
#                 base_amount = round(line.fright*line.quantity,2)
#                 tax_debit_amount = base_amount*(line.tax_id and line.tax_id.amount/100 or 0)
#                 tax_debit_amount = round(tax_debit_amount,2)
#             if tax_debit_amount:
#                 res.append({
#                     'type':'tax',
#                     'name':line.name,
#                     'price_unit': line.price_unit,
#                     'quantity': 1,
#                     'price': tax_debit_amount,
#                     'account_id': line.tax_id and line.tax_id.gl_account_id and account_tax_id or False,
#                     'account_analytic_id': line.account_analytic_id.id,
#                     # vsis add
#                     'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
#                     'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
#                 })
                if tax_cgst:
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': tax_cgst,
                            'account_id': account_cgst_id or False,
                            'account_analytic_id': line.account_analytic_id.id,
                            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                if tax_sgst:
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': tax_sgst,
                            'account_id': account_sgst_id or False,
                            'account_analytic_id': line.account_analytic_id.id,
                            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
                if tax_igst:
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': tax_igst,
                            'account_id': account_igst_id or False,
                            'account_analytic_id': line.account_analytic_id.id,
                            'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                            'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                        })
        return res
    def move_line_fi_debit_14(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            if line.tax_id and not line.tax_id.gl_account_id:
                raise osv.except_osv(_('Warning!'),_('GL Account is not null, please configure it in Tax Master!'))
            tax = 0
            #tax = 
            if line.fright_fi_type == '2':
                base_amount = round(line.fright,2)
                tax_debit_amount = base_amount*(14.00/100 or 0)
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100
                #TPT START - By P.vinothkumar - ON 21/06/2016 - FOR (calculate tax for STax 30% of Freight 15% (Dr))    
                elif line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100    
                tax_debit_amount = round(tax_debit_amount,2)
            else:
                base_amount = round(line.fright*line.quantity,2)
                tax_debit_amount = base_amount*(14.00/100 or 0)
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100
                #TPT START - By P.vinothkumar - ON 21/06/2016 - FOR (calculate tax for STax 30% of Freight 15% (Dr))    
                elif line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100    
                tax_debit_amount = round(tax_debit_amount,2)
            
            if tax_debit_amount:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': tax_debit_amount,
                    'account_id': line.tax_id and line.tax_id.gl_account_id and line.tax_id.gl_account_id.id or False,
                    'account_analytic_id': line.account_analytic_id.id,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                })
        return res
    def move_line_fi_debit_5(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            if line.tax_id and not line.tax_id.gl_account_id:
                raise osv.except_osv(_('Warning!'),_('GL Account is not null, please configure it in Tax Master!'))
            if line.fright_fi_type == '2':
                base_amount = round(line.fright,2)
                tax_debit_amount = base_amount*(0.5/100 or 0)
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100
                #TPT START - By P.vinothkumar - ON 21/06/2016 - FOR (calculate tax for STax 30% of Freight 15% (Dr))     
                elif line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100     
                tax_debit_amount = round(tax_debit_amount,2)
            else:
                base_amount = round(line.fright*line.quantity,2)
                tax_debit_amount = base_amount*(0.5/100 or 0)
                if line.tax_id and line.tax_id.description=='STax 30% of Freight 14.5% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100
                 #TPT START - By P.vinothkumar - ON 21/06/2016 - FOR (calculate tax for STax 30% of Freight 15% (Dr))    
                elif line.tax_id and line.tax_id.description=='STax 30% of Freight 15% (Dr)':
                    tax_debit_amount = tax_debit_amount*30/100 
                #TPT end   
                tax_debit_amount = round(tax_debit_amount,2)
            
            if tax_debit_amount:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': tax_debit_amount,
                    'account_id': 4871,
                    'account_analytic_id': line.account_analytic_id.id,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                })
        return res
    def move_line_fi_debit_deducte(self, cr, uid, invoice_id):
        res = []
        sum_deducte = 0.0
        sum_deducte_round = 0.0
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
        if not account_ids:
            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
        for account in self.browse(cr,uid,account_ids):
            for line in invoice.invoice_line:
                if line.fright_fi_type == '2':
                    base_amount = round(line.fright)
                    tax_debit_amount = base_amount*(line.tax_id and line.tax_id.amount/100 or 0)
                else:
                    base_amount = round(line.fright*line.quantity)
                    tax_debit_amount = base_amount*(line.tax_id and line.tax_id.amount/100 or 0)
                
                if tax_debit_amount:
                    sum_deducte += round(tax_debit_amount,2)
            sum_deducte_round = round(sum_deducte)
            deducte = sum_deducte_round - round(sum_deducte,2)
            if deducte > 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                })
            if deducte < 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                })
        return res
    
    
    def move_line_fi_credit(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            if line.tax_credit and not line.tax_credit.gl_account_id:
                raise osv.except_osv(_('Warning!'),_('GL Account is not null, please configure it in Tax Master!'))
            if line.fright_fi_type == '2':
                base_amount = round(line.fright,2)
                tax_credit_amount = base_amount*(line.tax_credit and line.tax_credit.amount/100 or 0)
                tax_credit_amount = round(tax_credit_amount,2)
            else:
                base_amount = round(line.fright*line.quantity,2)
                tax_credit_amount = base_amount*(line.tax_credit and line.tax_credit.amount/100 or 0)
                tax_credit_amount = round(tax_credit_amount,2)
            if tax_credit_amount:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': -tax_credit_amount,
                    'account_id': line.tax_credit and line.tax_credit.gl_account_id and line.tax_credit.gl_account_id.id or False,
                    'account_analytic_id': line.account_analytic_id.id,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                })
        return res
    ###
    def move_line_fi_credit_14(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            if line.tax_credit and not line.tax_credit.gl_account_id:
                raise osv.except_osv(_('Warning!'),_('GL Account is not null, please configure it in Tax Master!'))
            if line.fright_fi_type == '2':
                base_amount = round(line.fright,2)
                tax_credit_amount = base_amount*(14.00/100 or 0)
                tax_credit_amount = tax_credit_amount*30/100
                tax_credit_amount = round(tax_credit_amount,2)
            else:
                base_amount = round(line.fright*line.quantity,2)
                tax_credit_amount = base_amount*(14.00/100 or 0)
                tax_credit_amount = tax_credit_amount*30/100
                tax_credit_amount = round(tax_credit_amount,2)
            if tax_credit_amount:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': -tax_credit_amount,
                    'account_id': line.tax_credit and line.tax_credit.gl_account_id and line.tax_credit.gl_account_id.id or False,
                    'account_analytic_id': line.account_analytic_id.id,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                })
        return res
    def move_line_fi_credit_5(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            if line.tax_credit and not line.tax_credit.gl_account_id:
                raise osv.except_osv(_('Warning!'),_('GL Account is not null, please configure it in Tax Master!'))
            if line.fright_fi_type == '2':
                base_amount = round(line.fright,2)
                tax_credit_amount = base_amount*(0.5/100 or 0)
                tax_credit_amount = tax_credit_amount*30/100
                tax_credit_amount = round(tax_credit_amount,2)
            else:
                base_amount = round(line.fright*line.quantity,2)
                tax_credit_amount = base_amount*(0.5/100 or 0)
                tax_credit_amount = tax_credit_amount*30/100
                tax_credit_amount = round(tax_credit_amount,2)
            if tax_credit_amount:
                res.append({
                    'type':'tax',
                    'name':line.name,
                    'price_unit': line.price_unit,
                    'quantity': 1,
                    'price': -tax_credit_amount,
                    'account_id': 4871,
                    'account_analytic_id': line.account_analytic_id.id,
                    # vsis add
                    'tpt_grn_id':line.tpt_grn_id and line.tpt_grn_id.id or False,
                    'tpt_grn_line_id':line.tpt_grn_line_id and line.tpt_grn_line_id.id or False,
                })
        return res
    ###
    
    def move_line_fi_credit_deducte(self, cr, uid, invoice_id):
        res = []
        sum_deducte = 0.0
        sum_deducte_round = 0.0
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000484008'])])
        if not account_ids:
            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000484008 and name is PRICE DIFF/ROUNDING in Account master !'))
        for account in self.browse(cr,uid,account_ids):
            for line in invoice.invoice_line:
                if line.fright_fi_type == '2':
                    base_amount = round(line.fright)
                    tax_credit_amount = base_amount*(line.tax_credit and line.tax_credit.amount/100 or 0)
                else:
                    base_amount = round(line.fright*line.quantity)
                    tax_credit_amount = base_amount*(line.tax_credit and line.tax_credit.amount/100 or 0)
                
                if tax_credit_amount:
                    sum_deducte += round(tax_credit_amount,2)
            sum_deducte_round = round(sum_deducte)
            deducte = sum_deducte_round - round(sum_deducte,2)
            if deducte > 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                })
            if deducte < 0:
                res.append({
                    'type':'tax',
                    'name':'',
                    'price_unit': 0,
                    'quantity': 1,
                    'price': -deducte,
                    'account_id': account.id,
                    'account_analytic_id': False,
                })
        return res
    
account_invoice_line()

class tpt_ed_invoice_positing(osv.osv):
    _name = "tpt.ed.invoice.positing"
    
    _columns = {
        'name':fields.char('Document No', size = 1024, required = True, readonly = True),
        'supplier_id':fields.many2one('res.partner', 'Supplier', readonly=True),
        'invoice_id':fields.many2one('account.invoice', 'Invoice No', readonly=True),
        'date':fields.date('Posting Date',states={'posted': [('readonly', False)]}),
        'create_uid':fields.many2one('res.users','Created By', readonly=True),
        'created_on': fields.datetime('Created On', readonly=True),
        'tpt_ed_invoice_positing_line': fields.one2many('tpt.ed.invoice.positing.line','ed_invoice_id','ED Invoice'),
        'ed_type':fields.selection(
                        [('spare_ed_12.36', 'Spares ED value of 12.36%'),
                         ('spare_ed_aed', 'Spares ED value with AED'),
                         ('spare_ed_12.5', 'Spares ED value of 12.5%'),
                         ('raw_ed_12.36', 'Raw material ED value of 12.36%'),
                         ('raw_ed_aed', 'Raw material ED value with AED'),
                         ('raw_ed_12.5', 'Raw material ED value of 12.5%'),
                         ('raw_ed_15', 'Raw material ED value of 15%'), #TPT-BM-ON 03/06/2016 - ed posting screen - validate button
                         ],
                        'ED Type', readonly=True),
        'state':fields.selection([('draft', 'Draft'),('posted', 'Posted'),('cancel', 'Cancelled')],'Status', readonly=True),
        }
    _defaults= {
        'state': 'draft',
        'name': '/',       
                }
    
    def bt_validate(self, cr, uid, ids, context=None):
        for ed in self.browse(cr, uid, ids):
            move_line = []
            for ed_line in ed.tpt_ed_invoice_positing_line:
                move_line.append((0,0,
                                  {
                                   'name': ed.name,
                                   'account_id': ed_line.gl_account_id.id,
                                   'debit': ed_line.debit,
                                   'credit': ed_line.credit,
                                   }))
            sql = '''
                select id from account_journal where name='Purchase Journal' or code='EXJ'
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            if not journal_ids:
                raise osv.except_osv(_('Warning!'),_('Please config Journal "Purchase Journal"!'))
                
            sql = '''
                select id from account_period where '%s' between date_start and date_stop
            '''%(ed.date)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            value={
                    'journal_id':journal_ids[0],
                    'period_id':period_ids[0] ,
                    'ref': ed.name,
                    'date': ed.date,
                    'ed_invoice_id': ed.id,
                    'line_id': move_line,
                    'doc_type': False
                    }
            new_jour_id = self.pool.get('account.move').create(cr,uid,value)
            #TPT-SSR-ON 12/01/2017 - ed posting auto Post
            move_pool = self.pool.get('account.move')
            auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
            if auto_ids:
                auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)             
                if auto_id.ed_posting:
                        try:#                          
                            move_pool.post(cr, uid, [new_jour_id], context={})
                        except:
                            pass  
             ##           
        return self.write(cr, uid, ids,{'state':'posted'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def _check_date(self, cr, uid, ids, context=None):
        for ed in self.browse(cr, uid, ids, context=context):
            if ed.date < ed.invoice_id.date_invoice:
                raise osv.except_osv(_('Warning!'),_('Date should not be less than Invoice Posting Date'))
                return False
            if ed.date > time.strftime('%Y-%m-%d'):
                raise osv.except_osv(_('Warning!'),_('Date should not allow future date'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.ed.invoice.positing.import')
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        return super(tpt_ed_invoice_positing, self).create(cr, uid, vals, context)
    
    
    
tpt_ed_invoice_positing()

class tpt_ed_invoice_positing_line(osv.osv):
    _name = "tpt.ed.invoice.positing.line"
    
    _columns = {
        'ed_invoice_id':fields.many2one('tpt.ed.invoice.positing', 'ED Invoice',ondelete='cascade'),
        'gl_account_id':fields.many2one('account.account', 'GL Code'),
        'gl_desc':fields.char('GL Description', size = 1024),
        'debit':fields.float('Debit'),
        'credit':fields.float('Credit'),
        }
    
tpt_ed_invoice_positing_line()

class tpt_product_avg_cost(osv.osv):
    _name = "tpt.product.avg.cost"
    
    _columns = {
        'product_id':fields.many2one('product.product', 'Product', ondelete = 'cascade'),
        'warehouse_id':fields.many2one('stock.location', 'Warehouse'),
        'hand_quantity' : fields.float('On hand Quantity'),
        'avg_cost' : fields.float('Avg Cost'),
        'total_cost' : fields.float('Total Cost'),
        }
    
tpt_product_avg_cost()

class product_product(osv.osv):
    _inherit = "product.product"
    
    _defaults = {
         'uom_id':False,          
                 }
#     def init(self,cr):
#         category_obj = self.pool.get('product.category')
#         category_ids = category_obj.search(cr, 1, [('cate_name','=','spares')])
#         for category in category_obj.browse(cr, 1, category_ids):
#             produc_ids = self.search(cr, 1, [('categ_id','=',category.id)])
#             self.write(cr, 1, produc_ids, {
#                 'property_account_income':category.property_account_income_categ and category.property_account_income_categ.id or False,
#                 'property_account_expense':category.property_account_expense_categ and category.property_account_expense_categ.id or False,
#             })
    
#     def init(self, cr):
#         account_obj = self.pool.get('account.account')
#         purchase_gl_account_ids = account_obj.search(cr, 1, [('code','=','0000119503')])
#         if not purchase_gl_account_ids:
#             raise osv.except_osv(_('Warning!'),_('Please config GL account 0000119503 – GRIR Clearing Account-Spares'))
#         expense_gl_account_ids = account_obj.search(cr, 1, [('code','=','0000404010')])
#         if not purchase_gl_account_ids:
#             raise osv.except_osv(_('Warning!'),_('Please config GL account 0000404010 STORES & SPARES AND CONSUMABLES'))
#         product_asset_account_ids = account_obj.search(cr, 1, [('code','=','0000119501')])
#         if not purchase_gl_account_ids:
#             raise osv.except_osv(_('Warning!'),_('Please config GL account 0000119501 SP-General Stores and Spares'))
#         category_obj = self.pool.get('product.category')
#         category_ids = category_obj.search(cr, 1, [('cate_name','=','spares')])
#         for category in category_obj.browse(cr, 1, category_ids):
#             produc_ids = self.search(cr, 1, [('categ_id','=',category.id)])
#             self.write(cr, 1, produc_ids, {
#                 'purchase_acc_id':purchase_gl_account_ids[0],
#                 'property_account_expense':expense_gl_account_ids[0],
#                 'product_asset_acc_id':product_asset_account_ids[0],
#             })
    ###TPT-START : Auto Product GL Account Creation on 14/10/2015
    def create(self, cr, uid, vals, context=None):
        
        if 'cate_name' in vals and vals['cate_name']=='spares':
            incomeaccount_id = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119503'])]) #income & purchase account id for spares
            expenseaccount_id = self.pool.get('account.account').search(cr, uid, [('code','in',['0000404010'])]) # Expense Account for Spares  0000404010
            assetaccount_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119501'])]) # Asset Account for Spares  0000119501
            vals.update({'purchase_acc_id':incomeaccount_id[0]})
            vals.update({'product_asset_acc_id':assetaccount_ids[0]})
            vals.update({'property_account_income':incomeaccount_id[0]})
            vals.update({'property_account_expense':expenseaccount_id[0]})
                
        return super(product_product, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'cate_name' in vals and vals['cate_name'] in ('finish', 'raw', 'service', 'assets'):
#             vals.update({'purchase_acc_id':False, 'product_asset_acc_id':False, 
#                      'property_account_income':False, 'property_account_expense':False})
            vals.update({'property_account_income':False, 'property_account_expense':False})
        if 'cate_name' in vals and vals['cate_name']=='spares':
            incomeaccount_id = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119503'])]) #income & purchase account id for spares
            expenseaccount_id = self.pool.get('account.account').search(cr, uid, [('code','in',['0000404010'])]) # Expense Account for Spares  0000404010
            assetaccount_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119501'])]) # Asset Account for Spares  0000119501
            vals.update({'purchase_acc_id':incomeaccount_id[0]})
            vals.update({'product_asset_acc_id':assetaccount_ids[0]})
            vals.update({'property_account_income':incomeaccount_id[0]})
            vals.update({'property_account_expense':expenseaccount_id[0]})
        if 'tpt_description' in vals and vals['tpt_description']:
            incomeaccount_id = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119503'])]) #income & purchase account id for spares
            expenseaccount_id = self.pool.get('account.account').search(cr, uid, [('code','in',['0000404010'])]) # Expense Account for Spares  0000404010
            assetaccount_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119501'])]) # Asset Account for Spares  0000119501
            vals.update({'purchase_acc_id':incomeaccount_id[0]})
            vals.update({'product_asset_acc_id':assetaccount_ids[0]})
            vals.update({'property_account_income':incomeaccount_id[0]})
            vals.update({'property_account_expense':expenseaccount_id[0]})
            
        new_write = super(product_product, self).write(cr, uid,ids, vals, context)
        return new_write  
    #TPT-END  
    def _avg_cost(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result
        inventory_obj = self.pool.get('tpt.product.avg.cost')
        for id in ids:
            sql = 'delete from tpt_product_avg_cost where product_id=%s'%(id)
            cr.execute(sql)
            sql = '''
                select foo.loc as loc
                    from
                    (select st.location_id as loc from stock_move st
                        inner join stock_location l on st.location_id= l.id
                            where l.usage = 'internal'
                    union all
                    select st.location_dest_id as loc from stock_move st
                        inner join stock_location l on st.location_dest_id= l.id
                        where l.usage = 'internal'
                        )foo
                   group by foo.loc
            '''
            cr.execute(sql)
            for loc in cr.dictfetchall():
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st 
                            where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id and production_id is null
                        )foo
                '''%(id,loc['loc'])
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity =float(inventory['ton_sl'])
                    total_cost = float(inventory['total_cost'])
                    # Modified by P.VINOTHKUMAR ON 22/11/2016 for round(avg_cost)
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl 
                            from 
                                (
                                select st.product_qty*-1 as product_qty
                                    from stock_move st 
                                    where st.state='done'
                                        and st.product_id=%s
                                        and location_id=%s
                                        and location_dest_id != location_id
                                        and production_id is null
                                )foo
                    '''%(id,loc['loc'])
                    cr.execute(sql)
                    out = cr.dictfetchone()
                    if out:
                        hand_quantity = hand_quantity+float(out['ton_sl'])
                        total_cost = avg_cost*hand_quantity
                    
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty as product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.
                                 location_dest_id != st.location_id
                                 and production_id is not null
                             union all
                             select st.product_qty*-1 as product_qty
                                from stock_move st 
                                where st.state='done'
                                        and st.product_id=%s
                                            and location_id=%s
                                            and location_dest_id != location_id
                                             and production_id is not null
                            )foo
                    '''%(id,loc['loc'],id,loc['loc'])
                    cr.execute(sql)
                    hand_quantity += cr.fetchone()[0]
                    sql = '''
                        select case when sum(produce_cost)!=0 then sum(produce_cost) else 0 end produce_cost,
                            case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                            from mrp_production where location_dest_id=%s and product_id=%s and state='done'
                    '''%(loc['loc'],id)
                    cr.execute(sql)
                    produce = cr.dictfetchone()
                    if produce:
#                         hand_quantity += float(produce['product_qty'])
                        total_cost += float(produce['produce_cost'])
                        # Added and Modified by P.VINOTHKUMAR ON 23/11/2016 for round(avg_cost)
                         #hand_quantity = round(hand_quantity,2)
                         # Added and Modified by P.VINOTHKUMAR ON 23/11/2016 for round(avg_cost)
                        avg_cost = hand_quantity and total_cost/hand_quantity
                        
                    #TPT START - BM - ON 05/07/2016 - GET CST INVOICE ATM + FREIGHT AMT ADDED in TOTAL COST
                    cst_amt = 0.00
                    frt_amt = 0.00
                    si_frt_amt = 0.00
                    #total_cost = 0.0 commented by BM -ON 26/09/2016 - to solve issue in updating avg, total cost
                    sql = '''
                        select case when sum(ail.tpt_tax_amt) is NULL then 0 else sum(ail.tpt_tax_amt) end as cst_amt from account_invoice ai
                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                        inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                        inner join account_tax t on ailt.tax_id = t.id
                        where ail.product_id=%s and ai.state not in ('draft', 'cancel') 
                        and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
                    '''%(id, '%', '%')
                    cr.execute(sql)
                    cst_amt = cr.fetchone()
                    if cst_amt:
                        cst_amt = cst_amt[0]
                    #
                    sql = '''
                        select 
                        case when 
                        sum(case when ail.fright_fi_type='2' then ail.fright
                        when ail.fright_fi_type='3' then ail.fright*ail.quantity
                        else 0 end) is NULL then 0 else 
                        sum(case when ail.fright_fi_type='2' then ail.fright
                        when ail.fright_fi_type='3' then ail.fright*ail.quantity
                        else 0 end) end frt_amt
                        from account_invoice ai
                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                        where ail.product_id=%s and ai.state not in ('draft', 'cancel')
                        and ai.doc_type='freight_invoice'
                    '''%(id)
                    cr.execute(sql)
                    frt_amt = cr.fetchone()
                    if frt_amt:
                        frt_amt = frt_amt[0]    
                   # Modify following query on 06/11/2017 by P.VINOTHKUMAR
                    sql = '''
                    select 
                        case when 
                            SUM(case 
                            when ail.fright_type='1' then ail.quantity * ail.price_unit * ail.fright/100
                            when ail.fright_type='2' then ail.fright
                            when ail.fright_type='3' then ail.fright*ail.quantity
                            when ail.fright_type is null then ail.fright
                            else 0 end) >=0
                            then    
                            SUM(case 
                            when ail.fright_type='1' then ail.quantity * ail.price_unit * ail.fright/100
                            when ail.fright_type='2' then ail.fright
                            when ail.fright_type='3' then ail.fright*ail.quantity
                            when ail.fright_type is null then ail.fright
                            else 0 end)                
                            else 0 end as frt_amt
                        from account_invoice ai
                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                        where ail.product_id=%s and 
                        ai.state not in ('draft', 'cancel')
                        and ai.doc_type='supplier_invoice' and ail.fright>0 
                        
                    '''%(id)
                    cr.execute(sql)
                    si_frt_amt = cr.fetchone()
                    if si_frt_amt:
                        si_frt_amt = si_frt_amt[0]
                    #      
                    if hand_quantity>0 and loc['loc'] in [14, 15]: #Spares, Raw respectively 
                        total_cost += (cst_amt + frt_amt + si_frt_amt)
                        # Modified by P.VINOTHKUMAR ON 23/11/2016 for round(avg_cost,2)
                        #hand_quantity = round(hand_quantity,2)
                        # Remove round off for hand_quantity ON 02/11/2017 by P.VINOTHKUMAR
                        #avg_cost = round(total_cost  / hand_quantity,2)
                        hand_quantity = hand_quantity
                        avg_cost = total_cost  / hand_quantity
                        
                    inventory_obj.create(cr, uid, {'product_id':id,
                                                   'warehouse_id':loc['loc'],
                                                   'hand_quantity':hand_quantity,
                                                   'avg_cost':avg_cost,
                                                   'total_cost':avg_cost * hand_quantity})
            result[id] = 'Avg Cost'
        return result
    
    def _get_product(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
            # Added by BM and P.VINOTHKUMAR on 09/11/2017
            if not line.issue_id and line.product_id.id!=13030 and not line.move_dest_id and line.state!='cancel':
                result[line.product_id.id] = True           
        return result.keys()
    
    _columns = {
        'purchase_acc_id': fields.many2one('account.account', 'Purchase GL Account'),
        'sale_acc_id': fields.many2one('account.account', 'Sales GL Account'),
        'product_asset_acc_id': fields.many2one('account.account', 'Product Asset Account'),
        'product_cose_acc_id': fields.many2one('account.account', 'Product Cost of Goods Sold Account'),
        'avg_cost':fields.function(_avg_cost,type='char', string='Avg Cost',
            store={
                'stock.move': (_get_product, ['price_unit', 'location_id', 'location_dest_id', 'product_qty','state','product_id'], 20),
                   }),
        'avg_cost_line':fields.one2many('tpt.product.avg.cost','product_id','Avg Cost Line'),
        'chapter': fields.char('Chapter ID', size = 1024),
        'warehouse_id':fields.many2one('stock.location', 'Sale Warehouse'),
        'prod_dest_id':fields.many2one('stock.location', 'Production Destination Location'),
        'product_credit_id': fields.many2one('account.account', 'Product Credit Account'),
        }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_with_name', False):
            name = context.get('name')
            product_ids = self.search(cr, uid, ['|',('name','ilike',name),('default_code','ilike',name)])
            args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_product_with_name':1,'name':name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
product_product()

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
# Hàm update Report Cash/Bank, update field từ type_trans thành type    (phuoc)

    def init(self, cr):
        sql = '''
             update account_voucher set type=type_trans where type_trans is not null;
        '''
        cr.execute(sql)
        
# end
    
    #TPT-START
    #TPT - Commented By BalamuruganPurushothaman - ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
    
    #===========================================================================
    # def _get_tpt_currency_amount(self, cr, uid, ids, name, args, context=None):
    #     res = {}
    #     if context is None:
    #         context = {}
    #     for voucher in self.browse(cr, uid, ids, context=context):
    #         amount = 0
    #         if voucher.tpt_currency_id and voucher.tpt_currency_amount:
    #             context.update({'date': voucher.date or time.strftime('%Y-%m-%d')})
    #             voucher_rate = self.pool.get('res.currency').read(cr, uid, voucher.tpt_currency_id.id, ['rate'], context=context)['rate']
    #             amount = voucher.tpt_currency_amount/voucher_rate
    #         res[voucher.id] = amount
    #     return res
    #===========================================================================
    
    #TPT - Commented By BalamuruganPurushothaman - ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
    def _get_tpt_currency_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        if context is None:
            context = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            amount = 0
            res[voucher.id] = {
                        'tpt_amount': 0.0
                        }
            if voucher.tpt_currency_id and voucher.tpt_currency_amount and voucher.tpt_exchange_rate:       
                amount = voucher.tpt_currency_amount/voucher.tpt_exchange_rate
            res[voucher.id]['tpt_amount'] = amount
        return res
    #TPT-END
    ###
    def compute_total_amt(self, cr, uid, ids, context=None):
        tax_pool = self.pool.get('account.tax')
        partner_pool = self.pool.get('res.partner')
        position_pool = self.pool.get('account.fiscal.position')
        voucher_line_pool = self.pool.get('account.voucher.line')
        voucher_pool = self.pool.get('account.voucher')
        if context is None: context = {}

        for voucher in voucher_pool.browse(cr, uid, ids, context=context):
            voucher_amount = 0.0
            for line in voucher.line_ids:
                if line.type=='cr':
                    voucher_amount += line.untax_amount or line.amount

            total = voucher_amount
            
            self.write(cr, uid, [voucher.id], {'tpt_sub_total_amt':total})
        return True
    
    def _tpt_sub_total(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        #currency_obj = self.pool.get('res.currency')
        res = {}
        debit = credit = 0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = {
                        'tpt_amount_total': 0.0
                        }
            for dr in voucher.line_dr_ids:
                debit += dr.amount
            for cr in voucher.line_cr_ids:
                credit += cr.amount
            res[voucher.id]['tpt_amount_total'] =  credit
        return res
    def _amount_all_credit_debit(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'credit_total': 0.0,
                'debit_total': 0.0,
                'total_diff': 0.0,
            }
            val1 = 0.0
            val2 = 0.0
            val3 = 0.0
            for line1 in line.line_cr_ids:
                #val1 += line.amount_original 
                val1 += line1.amount_unreconciled
            for line2 in line.line_dr_ids:
                val2 += line2.amount_unreconciled
            res[line.id]['credit_total'] = val1
            res[line.id]['debit_total'] = val2
            val3 = val1 - val2 
            res[line.id]['total_diff'] = val3
        return res
    ###
    def _get_partner(self, cr, uid, context=None):
        if context is None: context = {}
        #context.set('partner_id', False)
        #context['partner_id'] = False
        return context.get('partner_id', False)
        #return False
    _columns = {
        'name': fields.char( 'Journal no.',size = 256, readonly=True, states={'draft':[('readonly',False)]}),
        'memo':fields.char('Memo', size=256, readonly=True, states={'draft':[('readonly',False)]}),
        'cheque_date': fields.date('Cheque Date'),
        'reconciliation_date': fields.date('Reconciliation Date'),
        'cheque_no': fields.char('Cheque No'),
        'sum_amount': fields.float('Amount'),
        'type_trans':fields.selection([
            ('payment','Payment'),
            ('receipt','Receipt'),
        ],'Default Type', readonly=True, states={'draft':[('readonly',False)]}),
                
        'type_cash_bank':fields.selection([
            ('cash','Cash'),
            ('bank','Bank'),
            ('journal','Journal Voucher'),
        ],'Cash/Bank Type', readonly=True, states={'draft':[('readonly',False)]}),
                
        'cheque_number': fields.char('Cheque Number'),
        'bank_name': fields.char('Bank Name'),
        'tpt_journal':fields.selection([('cash','Cash'),('bank','Bank')],'Type'),
        'tpt_cus_reconcile':fields.boolean('Cus Reconcile',readonly =True ),
        'tpt_sup_reconcile':fields.boolean('Sup Reconcile',readonly =True ),
        'state':fields.selection(
            [('draft','Draft'),
             ('cancel','Cancelled'),
             ('proforma','Pro-forma'),
             ('posted','Posted'),
             ('reconcile', 'Reconciled')
            ], 'Status', readonly=True, size=32, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),
        'tpt_currency_id':fields.many2one('res.currency','Currency', readonly=True, states={'draft':[('readonly',False)]}),
        'is_tpt_currency':fields.boolean('Is TPT Currency'),
        'tpt_amount':fields.function(_get_tpt_currency_amount,type='float',string='Paid Amount (INR)', multi='sum',),
        'tpt_currency_amount':fields.float('Paid Amount'),
        'payee':fields.char('Payee', size=1024),
        'employee_id':fields.many2one('hr.employee','Employee'),
        'cost_center_id':fields.many2one('tpt.cost.center','Cost Center', readonly=True, states={'draft':[('readonly',False)]}),
        'tpt_exchange_rate':fields.float('Realization Rate', digits=(12,14),),#TPT
        'tpt_sub_total_amt':fields.float('Total'),#TPT
        'tpt_amount_total': fields.function(_tpt_sub_total, type='float', readonly=True, store = True, string='Total', multi='sub_total' ),#TPT
        'purchase_id':fields.many2one('purchase.order','PO Number', readonly=True, states={'draft':[('readonly',False)]}),
        'tpt_bank_re':fields.boolean('Bank Reconciliation Updated'),
        
        'status': fields.selection([('reconcile', 'Reconciled'), ('unreconcile', 'Un-Reconciled'), 
                                    ('confirmed', 'Confirmed')],'Reconcile-Status'),  #TPT
        'credit_total':fields.function(_amount_all_credit_debit, type='float', multi='sum1',string='Credit'),
        'debit_total':fields.function(_amount_all_credit_debit, type='float', multi='sum2',string='Debit'),
        'total_diff':fields.function(_amount_all_credit_debit, type='float', multi='sum3',string='Diff: Cr-Db'),
        'partner_id':fields.many2one('res.partner', 'Partner', readonly=True, states={'draft':[('readonly',False)]}),
        'tpt_partner_id':fields.many2one('res.partner', 'Partner',  states={'draft':[('readonly',False)]}),
        'tpt_date': fields.date('Date', states={'draft':[('readonly',False)]})
        }
    #
    def action_auto_reconcile(self, cr, uid, ids, context=None):
       # Added by P.vinothkumar on 08/07/2016 for auto reconciliation process:

        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        reconcile_pool=self.pool.get('account.move.reconcile')
        voucher_line_pool=self.pool.get('account.voucher.line')
        account_invoice=self.pool.get('account.invoice')
        account_voucher=self.pool.get('account.voucher')
        #
        sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
                '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        vals={}
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.cash.receipt')
        vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] 
        name=vals['name'] 
        #
        for voucher in self.browse(cr, uid, ids, context):
  
            # Generate move entry
            #for voucher in self.browse(cr, uid, ids, context):
            move = {
                    'name': name,
                    'journal_id': voucher.journal_id.id,
                    'narration': voucher.narration,
                    'date': voucher.date,
                    'ref': voucher.number.replace('/',''),
                    'doc_type': 'cash_rec',
                    'period_id': voucher.period_id.id,
                    #'line_id':[(0,0,move_line)]
                    }       
             
            move_id = move_pool.create(cr, uid, move, context=context)
 
            #-------------------------------Invoice part---------------------------------------
            # Fetch invoice details
            sql = '''
            select id, number, amount_total_inr as inv_amt from account_invoice where state='open' and partner_id=%s order by date_invoice,id
            '''%(voucher.partner_id.id)
            cr.execute(sql)
            amount, temp = 0, 0
            moveline = []
            invoices_list = ''
            cash_payment=voucher.amount
            allocated_amt=cash_payment
            for invoice in cr.dictfetchall():
                if allocated_amt > 0:                
                    amount += invoice['inv_amt']
                    rec={
                           'opening_reconcile':'f',
                           'type':'auto'
                          }
                    rec_id=reconcile_pool.create(cr,uid,rec,context=context) 
                    # Create moveline for invoice
                    moveline =  {
                        'name': invoice['number'],
                        'partner_id': voucher.partner_id.id,
                        'journal_id': voucher.journal_id.id,
                        'period_id': voucher.period_id.id,
                        'ref': voucher.number.replace('/',''),
                        'doc_type': 'cash_rec',
                        'debit':0.00,
                        'credit': round(invoice['inv_amt'],2) or 0,
                        'date': voucher.date,
                        'move_id':int(move_id),
                        'reconcile_id':int(rec_id),
                        }   
                    # added by P.vinothkumar on 22/07/2016
                     # Fetch Total invoice amount
                    advance_amount = 0
                    sql='''
                       select case when (sum(a.credit)-sum(a.debit)) is null then 0 else (sum(a.credit)-sum(a.debit))  
                       end as amount from(select credit,debit from account_move_line aml
                       join account_voucher av on aml.name=av.number 
                       where av.partner_id=%s and aml.reconcile_partial_id is not null union all select null,null)a 
                       '''%(voucher.partner_id.id)
                    cr.execute(sql)
                    advance_amount=cr.fetchone()[0]   
                    
                    if voucher.amount + advance_amount >= amount: #FULL RECONCILIATION
                        move_line_id=move_line_pool.create(cr, uid, moveline, context=context)
                        # Update reconcile id in posted invoice.
                        sql = '''
                        update account_move_line set reconcile_id=%s where id=(select aml.id from account_move_line aml join account_move am on 
                        am.id=aml.move_id and am.name='%s' and credit=0.00)
                        '''%(int(rec_id),invoice['number'])
                        cr.execute(sql)
                          
                        sql = '''
                             update account_invoice set state='paid' where id=%s
                       '''%(invoice['id'])
                        cr.execute(sql)
                        invoices_list +=  str(invoice['number']) +' : '+ str(invoice['inv_amt']) +'\n' 
                        
                         
                    elif voucher.amount <= amount: # Partial reconciliation
                          moveline = {}
                          # Fetch paid amount from previous CR posting
                          sql = '''
                         select case when sum(a.amount)is null then 0 else sum(amount) end as amount from 
                        (select credit as amount from account_move_line where 
                         name='%s' and reconcile_partial_id is not null
                         union all SELECT NULL)a
                         '''%invoice['number']
                          cr.execute(sql)
                          paid_amt = cr.dictfetchone()['amount']
                          allocated_amt = round(allocated_amt,2)
                          # paided amount > 0
                          if paid_amt > 0:
                              allocated_amt = invoice['inv_amt'] - paid_amt
                              moveline.update({
                                          'reconcile_id':int(rec_id),
                                          'reconcile_partial_id':'',    
                                              })  
                          # Not allocated any payment  
                          else:
                              moveline.update({
                                          'reconcile_partial_id':int(rec_id),# modified by P.vinothkumar on 13/07/2016  
                                              })
                          moveline.update({
                            'name': invoice['number'],
                            'partner_id': voucher.partner_id.id,
                            'journal_id': voucher.journal_id.id,
                            'period_id': voucher.period_id.id,
                            'ref': voucher.number.replace('/',''),
                            'doc_type': 'cash_rec',
                            'credit':  allocated_amt or 0,
                            'date': voucher.date,
                            'move_id':int(move_id),
                            #'reconcile_partial_id':int(rec_id),# modified by P.vinothkumar on 13/07/2016
                            })  
                          move_line_id=move_line_pool.create(cr, uid, moveline, context=context)
                          
                          # Update partial_ids in invoice postings
                          sql = '''
                              update account_move_line set reconcile_partial_id=%s where id=(select aml.id from account_move_line aml join account_move am on 
                              am.id=aml.move_id and am.name='%s' and credit=0.00)
                                '''%(int(rec_id),invoice['number'])
                          cr.execute(sql)
                           # already paided amount > 0
                          if paid_amt > 0:
                              allocated_amt = invoice['inv_amt'] - paid_amt
                            # Update reconcile_id and partial reconcile_id for CR previous Posting    
                              sql='''
                                  update account_move_line set reconcile_partial_id=null,reconcile_id=
                                  (select reconcile_id from account_move_line where name='%(inv_no)s' and move_id=(%(move_id)s))
                                  where name='%(inv_no)s'and move_id!=(%(move_id)s)
                                  '''%{'inv_no':invoice['number'],
                                     'move_id':int(move_id),
                                     }
                              cr.execute(sql) 
                              # Update reconcile_id and partial reconcile_id for invoice Posting 
                              sql='''
                                  update account_move_line set reconcile_id=(select reconcile_id from account_move_line where name='%(inv_no)s' 
                                  and move_id=(%(move_id)s)),reconcile_partial_id=null 
                                  where id=(select aml.id from account_move_line aml join account_move am on am.id=aml.move_id and am.name='%(inv_no)s' 
                                  and credit=0.00)
                                  '''%{'inv_no':invoice['number'],
                                       'move_id':int(move_id),
                                       } 
                              cr.execute(sql)
                              # update status='paid' after checking all payments are completed
                              sql = '''
                                     update account_invoice set state='paid' where id=%s
                                    '''%(invoice['id'])
                              cr.execute(sql)
                          
                          #print sql, allocated_amt
                        
                          invoices_list +=  str(invoice['number']) +' : '+ str(allocated_amt) +'\n'
                          
                          
                    
                allocated_amt -= invoice['inv_amt']
                    
            ####END FOR LOOP FOR INVOICE 
           # -----------------------------------Voucher part----------------------
 
            advance_amount = 0
            sql='''
               select case when (sum(a.credit)-sum(a.debit)) is null then 0 else (sum(a.credit)-sum(a.debit))  
               end as amount from(select credit,debit from account_move_line aml
               join account_voucher av on aml.name=av.number 
               where av.partner_id=%s and aml.reconcile_partial_id is not null union all select null,null)a 
               '''%(voucher.partner_id.id)
            cr.execute(sql)
            advance_amount=cr.fetchone()[0]
            
            
            rec={
                     'opening_reconcile':'f',
                     'type':'auto'
                 }
            rec_id = reconcile_pool.create(cr,uid,rec,context=context)
            moveline={}
            
         # Total invoice amount
            sql = '''
                 select case when sum(debit) is null then 0 else sum(debit) end as invoice_amount from account_move_line aml
                 inner join account_invoice ai on aml.ref=ai.vvt_number
                 where ai.type='out_invoice' and ai.partner_id='%s'
                '''%(voucher.partner_id.id)
                
            cr.execute(sql)
            total_invoice_amount = cr.fetchone()[0]
                      
            # Fetch Total paid amount
            sql='''
            select sum(amount) as paid_amt from account_voucher where partner_id='%s' and state not in('draft')
            '''%(voucher.partner_id.id)
            cr.execute(sql)
            total_paid_amount = cr.fetchone()[0]
            remaining_amount = 0.0
            
        # Calculate remaining payment amount
            remaining_amount  =  total_paid_amount - total_invoice_amount
            
         # Check condition if customer gives advance amount or not   
            if advance_amount != 0: 
                # Fetch advance paid id
                sql='''select case when a.partial_id is null then 0 else a.partial_id end as partial_id,
                       case when a.name is null then 'CUP' else a.name end as vou_name
                       from (select distinct aml.reconcile_partial_id as partial_id,aml.name
                       from account_move_line aml
                       join account_voucher av on aml.name=av.number 
                       where av.partner_id=%s and aml.reconcile_partial_id is not null union all 
                        select null,null)a where a.partial_id != 0
                     '''%(voucher.partner_id.id)
                cr.execute(sql)
                
                for payments in cr.dictfetchall():
                    payment_id = payments['partial_id']
                    voucher_number = payments['vou_name']
                
                moveline.update({
                    'name': voucher_number,
                    'partner_id': voucher.partner_id.id,
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'ref': voucher.number.replace('/',''),
                    'doc_type': 'cash_rec',
                    'debit': advance_amount,
                    'credit':0.00,
                    'date': voucher.date,
                    'move_id': int(move_id),
                    'reconcile_id': payment_id,
                    'reconcile_partial_id':''
                    })
                move_line_id=move_line_pool.create(cr, uid, moveline, context=context)
                
                moveline.update({
                             'reconcile_id':int(rec_id),
                             'debit' : voucher.amount,
                             'reconcile_partial_id' : '' 
                             })
                
                # update reconcile_id for current payment posting(Added by P.vinothkumar on 25/07/2016
                sql=''' update account_move_line set reconcile_id=
                        '%(rec_id)s' where move_id in (select id from account_move where name='%(vou_no)s') and debit=0.00
                       '''%{'vou_no': voucher.number,
                            'rec_id': int(rec_id)
                        }
                cr.execute(sql)

             # update reconcile_id and partial reconcile_id for previous CR and payment postings  
                sql=''' update account_move_line set reconcile_partial_id=null,reconcile_id=(select distinct reconcile_partial_id from
                       account_move_line where partner_id='%(partner_id)s' and reconcile_partial_id is not null)
                       where partner_id='%(partner_id)s' and reconcile_partial_id is not null 
                       '''%{'partner_id': voucher.partner_id.id
                        }
                cr.execute(sql)
                       
            else:
                
                if remaining_amount > 0:
                    partial_payment =voucher.amount - remaining_amount
                    moveline={}
                    moveline.update({
                                      'debit' : partial_payment,
                                      'reconcile_partial_id' : int(rec_id),
                                      'reconcile_id' : ''
                                     })
                    # Update partial_ids in payment postings
                    sql = '''
                      update account_move_line set reconcile_partial_id=%s where 
                      id=(select aml.id from account_move_line aml join account_move am on 
                      am.id=aml.move_id and am.name='%s' and debit=0.00)
                        '''%(int(rec_id),voucher.number)
                    cr.execute(sql)
                     
                else:
                    moveline.update({
                                     'reconcile_id' : int(rec_id),
                                     'debit' : voucher.amount,
                                     'reconcile_partial_id' : ''
                                     })

            moveline.update({
                    'name': voucher.number,
                    'partner_id': voucher.partner_id.id,
                    'journal_id': voucher.journal_id.id,
                    'period_id': voucher.period_id.id,
                    'ref': voucher.number.replace('/',''),
                    'doc_type': 'cash_rec',
                    #'debit': voucher_amount,
                    'credit':0.00,
                    'date': voucher.date,
                    'move_id':int(move_id),
    #                     'reconcile_id':int(rec_id),
    #                     'reconcile_partial_id':''
                    })
         
            move_line_id=move_line_pool.create(cr, uid, moveline, context=context)

            # update state=reconciled
            sql = '''
                   update account_voucher set state='reconcile' where id=%s
                   '''%(voucher.id)
            cr.execute(sql)
       
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'green_erp_arulmani_hrm', 'alert_permission_form_view')
            return {
                    'name': 'Invoice-Payment Info',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'alert.form',
                    'domain': [],
                    'context': {'default_message':'%s'%invoices_list,},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    }
        
        return True 
    #TPT VINOTHKUMAR end(16/07/2016)
    #   
    def voucher_print_button(self, cr, uid, ids, context={}):
        '''This function prints the Journal Voucher in Accounting'''
        for this_id in self.browse(cr, uid, ids, context):
            datas = {
                'model': 'account.voucher',
                'ids': ids,
                'form': self.read(cr, uid, ids[0], context=context),
                }
            return {'type': 'ir.actions.report.xml', 'report_name': 'voucher1.print', 'datas': datas, 'context': context, 'nodestroy': True}
    
    def print_voucher(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'accout.voucher',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account_voucher_report',
            }     
    #TPT-By BalamuruganPurushothaman - ON 12/11/2015 - TO AVOID LOADING DEFAULT CUSTOMER(VVTi Pigments) IN VOUCHER SCREENS    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(account_voucher, self).default_get(cr, uid, fields, context=context)
        journal = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'cash')])
        if context.get('get_customer_reconcile'):
            res.update({'journal_id': journal[0],'tpt_cus_reconcile': True})
        if context.get('get_supp_reconcile'):
            res.update({'journal_id': journal[0],'tpt_sup_reconcile': True})
#         user = self.pool.get('res.users').browse(cr, uid, uid)
#         partner_id = user.company_id.partner_id.id
#         res.update({'partner_id': partner_id})
         
        return res
    
    def _default_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('type',False) and context['type']=='general': 
            journal_pool = self.pool.get('account.journal')
            ids = journal_pool.search(cr, uid, ['|',('code', '=', 'MISC'),('name', 'ilike', 'Miscellaneous Journal')])
            if ids:
                return ids[0]
        journal_pool = self.pool.get('account.journal')
        journal_type = context.get('journal_type', False)
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.bank.statement',context=context)
        if journal_type:
            ids = journal_pool.search(cr, uid, [('type', '=', journal_type),('company_id','=',company_id)])
            if ids:
                return ids[0]
        return False
    
    def _get_tpt_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and user.company_id.currency_id.id or False 
    
    def _get_is_tpt_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        return user.company_id and user.company_id.currency_id and True or False 
    
    _defaults = {
        'name': '/',
        'journal_id': _default_journal_id,
        'tpt_currency_id': _get_tpt_currency,
        'is_tpt_currency': _get_is_tpt_currency,
        'status': 'unreconcile',
#         'partner_id': 1,
    }
    
    def _check_sum_amount(self, cr, uid, ids, context=None):
        for account in self.browse(cr, uid, ids, context=context):
            amount = 0
            if account.sum_amount:
                for line in account.line_ids:
                    amount += line.amount
                if (account.sum_amount != amount):
                    raise osv.except_osv(_('Warning!'),_('The Debit and Credit Amount should be matched'))
                    return False
        return True
    _constraints = [
        (_check_sum_amount, 'Identical Data', []),
    ]
    
    def onchange_tpt_currency(self, cr, uid, ids, tpt_currency_id, currency_id, type, context=None):
        if context is None:
            context = {}
        vals = {}
        if type in ['receipt','payment']:
            if tpt_currency_id and currency_id:
                if tpt_currency_id!=currency_id:
                    vals = {
                        'is_tpt_currency': False
                    }
                else:
                    vals = {
                        'is_tpt_currency': True
                    }
        return {'value': vals}
    
    def onchange_tpt_currency_amount(self, cr, uid, ids, tpt_currency_id, tpt_currency_amount, type, date, context=None):
        if context is None:
            context = {}
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if date and date > current:
            vals.update({'date':current})
            warning = {
                'title': _('Warning!'),
                'message': _('Date: Not allow future date!')
            }
        if type in ['receipt','payment']:
            vals.update({
                'amount': 0,
                'tpt_amount': 0,
            })
            if tpt_currency_id and tpt_currency_amount and date:
                if date > current:
                    context.update({'date': current})
                else:
                    context.update({'date': date})
#                 context.update({'date': time.strftime('%Y-%m-%d')})
                voucher_rate = self.pool.get('res.currency').read(cr, uid, tpt_currency_id, ['rate'], context=context)['rate']
                vals.update({
                    'amount': tpt_currency_amount/voucher_rate,
                    'tpt_amount': tpt_currency_amount/voucher_rate,
                })
        return {'value': vals,'warning':warning}
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        #Modified by P.VINOTHKUMAR ON 19th April 2016
        sql = '''
        select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        if 'journal_id' in vals:
            aj = self.pool.get('account.journal').browse(cr, uid, vals['journal_id'])   
            if aj.code=='MISC': 
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.journal.voucher.sequence')
                if vals.get('name','/')=='/':
                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                
            if 'type_trans' in vals and vals['type_trans'] or vals['journal_id']: 
                        if aj.type == 'bank': 
                            if  vals['type']=='payment':
                                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.bank.payment') 
                                if vals.get('name','/')=='/':
                                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'   
                            if  vals['type']== 'receipt' :
                                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.bank.receipt') 
                                if vals.get('name','/')=='/':
                                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/' 
                        if aj.type == 'cash':
                            if vals['type']=='payment':         
                                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.cash.payment') 
                                if vals.get('name','/')=='/':
                                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                            if vals['type']=='receipt':         
                                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.cash.receipt') 
                                if vals.get('name','/')=='/':
                                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/' 
                        else:
                            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.journal.voucher.sequence') 
                            if vals.get('name','/')=='/':
                                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'  
                        vals.update({'name': vals['name'] or'/'})      
        if context.get('journal_type', False) in ['cash', 'bank']: 
            if 'type_trans' in vals:
                if  context.get('journal_type', False) == 'bank': 
                    if 'type_trans' in vals and vals['type_trans']=='payment':
                                sequence = self.pool.get('ir.sequence').get(cr, uid, 'bank.payment') 
                                if vals.get('name','/')=='/':
                                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.bank.payment') or '/'
                                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'   
                    if 'type_trans' in vals and vals['type_trans'] == 'receipt':
                                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.bank.receipt') 
                                if vals.get('name','/')=='/':
                                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/' 
                if  context.get('journal_type', False) == 'cash':
                    if 'type_trans' in vals and vals['type_trans'] == 'payment':       
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.cash.payment') 
                        if vals.get('name','/')=='/':
                            vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                    if 'type_trans' in vals and vals['type_trans'] == 'receipt' :        
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.cash.receipt') 
                        if vals.get('name','/')=='/':
                            vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        if 'tpt_partner_id' in vals:
            vals.update({'partner_id':vals['tpt_partner_id']
                     })
        else:
            vals['tpt_partner_id']=vals['partner_id']
#         new_id = super(account_voucher, self).create(cr, uid, vals, context)
            
        if context is None:
            context = {}
        #TPT-START - BM on 13/06/2016
        if vals.get('tpt_date', False) and vals['tpt_date']:
            vals['date']=vals['tpt_date']
        #TPT_END
        voucher_id = super(account_voucher, self).create(cr, uid, vals, context)

        voucher = self.browse(cr, uid, voucher_id)
        if voucher.type_trans:
            total = 0
            sql = '''
                update account_voucher set type_cash_bank = 'cash' where journal_id in (select id from account_journal where type = 'cash')
            '''
            cr.execute(sql)
            sql = '''
                update account_voucher set type_cash_bank = 'bank' where journal_id in (select id from account_journal where type = 'bank')
            '''
            cr.execute(sql)
            for line in voucher.line_ids:
                total += line.amount 
            if voucher.sum_amount != total:
                raise osv.except_osv(_('Warning!'),
                    _('Total amount in Voucher Entry must equal Amount!'))
        elif context.get('journal_entry_create',False):
            sql = '''
                update account_voucher set type_cash_bank = 'journal' where id = %s
            '''%(voucher_id)
            cr.execute(sql)
            total_debit = 0
            total_credit = 0
            for line in voucher.line_ids:
                if line.type=='dr':
                    total_debit += round(line.amount,2)
                if line.type=='cr':
                    total_credit += round(line.amount,2) 
            if round(total_debit,2) != round(total_credit,2):
                raise osv.except_osv(_('Warning!'),
                    _('Total Debit must be equal Total Credit!'))
        
        if context.get('tpt_show_cr', False):
            total = 0
            for cr in voucher.line_cr_ids:
                total += cr.amount
            if voucher.amount<total:
                raise osv.except_osv(_('Warning!'),
                        _('Allocated amount is not greater than open balance!'))
                
        if context.get('tpt_show_dr', False):
            total = 0
            for dr in voucher.line_dr_ids:
                total += dr.amount
            if voucher.amount<total:
                raise osv.except_osv(_('Warning!'),
                        _('Allocated amount is not greater than open balance!'))
        
        return voucher_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        #TPT-START - BM on 13/06/2016 - For Customer Reconciliation screen - date user selectable that should be updated into account move line table
        if vals.get('tpt_date', False):#vals['tpt_date']:
            vals['date']=vals['tpt_date']
        #TPT_END
        new_write = super(account_voucher, self).write(cr, uid, ids, vals, context)
        for voucher in self.browse(cr, uid, ids):
            
            if context.get('tpt_show_cr', False):
                total = 0
                for cr in voucher.line_cr_ids:
                    total += cr.amount
                if voucher.amount<total:
                    raise osv.except_osv(_('Warning!'),
                            _('Allocated amount is not greater than open balance!'))
                    
            if context.get('tpt_show_dr', False):
                total = 0
                for dr in voucher.line_dr_ids:
                    total += dr.amount
                if voucher.amount<total:
                    raise osv.except_osv(_('Warning!'),
                            _('Allocated amount is not greater than open balance!'))
            
            if voucher.type_trans and voucher.type_cash_bank != 'journal':
                total = 0
                for line in voucher.line_ids:
                    total += line.amount 
                if voucher.sum_amount != total:
                    raise osv.except_osv(_('Warning!'),
                        _('Total amount in Voucher Entry must equal Amount!'))
            if voucher.type_trans and voucher.type_cash_bank == 'journal':
                sql = '''
                    update account_voucher set type_trans = '' where id = %s
                '''%(voucher.id)
                cr.execute(sql)
            if context.get('journal_entry_create',False):
                sql = '''
                    update account_voucher set type_cash_bank = 'journal' where id = %s
                '''%(voucher.id)
                cr.execute(sql)
                total_debit = 0
                total_credit = 0
                for line in voucher.line_ids:
                    if line.type=='dr':
                        total_debit += round(line.amount,2)
                    if line.type=='cr':
                        total_credit += round(line.amount,2) 
                if round(total_debit,2) != round(total_credit,2):
                    raise osv.except_osv(_('Warning!'),
                        _('Total Debit must be equal Total Credit!'))
#             else:
#                 sql = '''
#                     update account_voucher set type_trans = 'payment' where type = 'payment'
#                 '''
#                 cr.execute(sql)
#                 sql = '''
#                     update account_voucher set type_trans = 'receipt' where type = 'receipt'
#                 '''
#                 cr.execute(sql)
        return new_write
    
    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        '''
        Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        # TODO: is there any other alternative then the voucher type ??
        # ANSWER: We can have payment and receipt "In Advance".
        # TODO: Make this logic available.
        # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
#phuoc    
        if voucher.type_trans:   
            if voucher.type_trans in ('payment'):
                credit = voucher.sum_amount
                account_id = voucher.account_id.id
                sql = '''
                    update account_voucher set type = 'payment' where id = %s
                '''%(voucher.id)
                if not context.get('tpt_voucher', False):
                    cr.execute(sql)
            elif voucher.type_trans in ('receipt'):
                debit = voucher.sum_amount
                account_id = voucher.account_id.id
                sql = '''
                    update account_voucher set type = 'receipt' where id = %s
                '''%(voucher.id)
                if not context.get('tpt_voucher', False):
                    cr.execute(sql)
#/phuoc
        else:
            if voucher.type in ('purchase', 'payment'):
                if voucher.tpt_currency_id.name=='INR':
                    credit = voucher.paid_amount_in_company_currency #TPT-Commented By BalamuruganPurushothaman ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
                #credit = voucher.tpt_amount #TPT-Added By BalamuruganPurushothaman ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
                else:                 
                    credit = voucher.tpt_amount #TPT-Added By BalamuruganPurushothaman ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
                if voucher.type == 'payment':
                    if voucher.journal_id.type == 'cash':
                        sql = '''
                            SELECT sup_pay_cash_id FROM tpt_posting_configuration WHERE name = 'sup_pay' and sup_pay_cash_id is not null
                        '''
                        cr.execute(sql)
                        sup_pay_cash_id = cr.dictfetchone()
                        if not sup_pay_cash_id:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Cash Account for Document Type is Supplier Payment in GL Posting Configrution !'))
                        account_id = sup_pay_cash_id and sup_pay_cash_id['sup_pay_cash_id'] or False
                    else:
                        sql = '''
                            SELECT sup_pay_bank_id FROM tpt_posting_configuration WHERE name = 'sup_pay' and sup_pay_bank_id is not null
                        '''
                        cr.execute(sql)
                        sup_pay_bank_id = cr.dictfetchone()
                        if not sup_pay_bank_id:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Bank Account for Document Type is Supplier Payment in GL Posting Configrution !'))
                        account_id = sup_pay_bank_id and sup_pay_bank_id['sup_pay_bank_id'] or False
                else:
                    account_id = voucher.account_id.id
            elif voucher.type in ('sale', 'receipt'):
                if voucher.tpt_currency_id.name=='INR':
                    debit = voucher.paid_amount_in_company_currency #TPT-Commented By BalamuruganPurushothaman ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
                else:
                    debit = voucher.tpt_amount or 0.0  #TPT-Added By BalamuruganPurushothaman ON 18/08/2015- TO TAKE REALIZATION RATE AS EXCHANGE RATE
                if voucher.type == 'receipt':
                    if voucher.journal_id.type == 'cash':
                        sql = '''
                            SELECT cus_pay_cash_id FROM tpt_posting_configuration WHERE name = 'cus_pay' and cus_pay_cash_id is not null
                        '''
                        cr.execute(sql)
                        cus_pay_cash_id = cr.dictfetchone()
                        if not cus_pay_cash_id:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Cash Account for Document Type is Customer Payment in GL Posting Configrution !'))
                        account_id = cus_pay_cash_id and cus_pay_cash_id['cus_pay_cash_id'] or False
                    else:
                        sql = '''
                            SELECT cus_pay_bank_id FROM tpt_posting_configuration WHERE name = 'cus_pay' and cus_pay_bank_id is not null
                        '''
                        cr.execute(sql)
                        cus_pay_bank_id = cr.dictfetchone()
                        if not cus_pay_bank_id:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Bank Account for Document Type is Customer Payment in GL Posting Configrution !'))
                        account_id = cus_pay_bank_id and cus_pay_bank_id['cus_pay_bank_id'] or False
                else:
                    account_id = voucher.account_id.id
            if debit < 0: credit = -debit; debit = 0.0
            if credit < 0: debit = -credit; credit = 0.0
            sign = debit - credit < 0 and -1 or 1
#         if debit < 0: credit = -debit; debit = 0.0
#         if credit < 0: debit = -credit; credit = 0.0
#         sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        move_line = {
                'name': voucher.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': account_id,
                'move_id': move_id,
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'partner_id': voucher.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher.amount or 0.0,
                'date': voucher.date,
                'date_maturity': voucher.date_due
            }
# phuoc
#         if voucher.type:
#             if voucher.type in ('purchase', 'payment'):
#                 if voucher.journal_id.type == 'cash':
#                     sql = '''
#                         SELECT sup_pay_cash_id FROM tpt_posting_configuration WHERE name = 'sup_pay' and sup_pay_cash_id is not null
#                     '''
#                     cr.execute(sql)
#                     sup_pay_cash_id = cr.dictfetchone()
#                     if not sup_pay_cash_id:
#                         raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Cash Account for Document Type is Supplier Payment in GL Posting Configrution !'))
#                     account_id = sup_pay_cash_id and sup_pay_cash_id['sup_pay_cash_id'] or False
#                 else:
#                     sql = '''
#                         SELECT sup_pay_bank_id FROM tpt_posting_configuration WHERE name = 'sup_pay' and sup_pay_bank_id is not null
#                     '''
#                     cr.execute(sql)
#                     sup_pay_bank_id = cr.dictfetchone()
#                     if not sup_pay_bank_id:
#                         raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Bank Account for Document Type is Supplier Payment in GL Posting Configrution !'))
#                     account_id = sup_pay_bank_id and sup_pay_bank_id['sup_pay_bank_id'] or False
#                 move_line.update({
#                     'account_id': account_id,
#                 })
# end phuoc
        return move_line
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []
        tpt_move_line = []
        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date or time.strftime('%Y-%m-%d')})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = voucher.type in ('payment', 'purchase') and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'
#phuoc
            if voucher.type_trans:
                if (voucher.type_trans=='payment'):
                    tot_line += amount
                    move_line['debit'] = amount
                else:
                    tot_line -= amount
                    move_line['credit'] = amount
#/phuoc    
            else:
                if (line.type=='dr'):
                    tot_line += amount
                    move_line['debit'] = amount
                else:
                    tot_line -= amount
                    move_line['credit'] = amount
                
            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    sign = voucher.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            rec_ids = []
            if context.get('tpt_voucher',False):
                tpt_move_line.append((0,0,move_line))
            else:
                voucher_line = move_line_obj.create(cr, uid, move_line)
                rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                if context.get('tpt_voucher',False):
                    tpt_move_line.append((0,0,exch_lines[0]),(0,0,exch_lines[1]))
                else:
                    new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                    move_line_obj.create(cr, uid, exch_lines[1], context)
                    rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                if context.get('tpt_voucher',False):
                    tpt_move_line.append((0,0,move_line_foreign_currency))
                else:
                    new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                    rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids, tpt_move_line)
    
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date or time.strftime('%Y-%m-%d')})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            line_total = 0.0
#phuoc
            if voucher.type_trans:
                if voucher.type_trans == 'payment':
                    move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
                    move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
                    line_total = move_line_brw.debit - move_line_brw.credit
                rec_list_ids = []
                line_total, rec_list_ids,tpt_move_line = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
                if voucher.type_trans == 'receipt':
                    ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
                    if ml_writeoff:
                        move_line_pool.create(cr, uid, ml_writeoff, local_context)
#phuoc
            else:
                if not voucher.line_cr_ids or not voucher.line_dr_ids or voucher.writeoff_amount!=0:
                    if voucher.type_cash_bank != 'journal':
                        move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
                        move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
                        line_total = move_line_brw.debit - move_line_brw.credit
                rec_list_ids = []
                if voucher.type == 'sale':
                    line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
                elif voucher.type == 'purchase':
                    line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
    #             Create one move line per voucher line where amount is not 0.0
                
                line_total, rec_list_ids,tpt_move_line = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
    
                # Create the writeoff line if needed
                if voucher.type_cash_bank != 'journal':
                    ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
                    if ml_writeoff:
                        move_line_pool.create(cr, uid, ml_writeoff, local_context)
#                         sql = '''
#                             update account_voucher set type_trans = 'payment', sum_amount = %s where type = 'payment' and id = %s
#                         '''%(voucher.id, voucher.amount)
#                         cr.execute(sql)
#                         sql = '''
#                             update account_voucher set type_trans = 'receipt', sum_amount = %s where type = 'receipt' and id = %s
#                         '''%(voucher.id, voucher.amount)
#                         cr.execute(sql)
        
            
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
                
            ###
            auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
            if auto_ids:
                auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                if voucher.type_trans:
                    if voucher.journal_id.type == 'cash' and auto_id.cash_transactions:
                        try:
#                             move_pool.button_validate(cr,uid, [move.id], context)
                            move_pool.post(cr, uid, [move_id], context={})
                        except:
                            pass
                        
                    if voucher.journal_id.type == 'bank' and auto_id.bank_transactions:
                        try:
                            move_pool.post(cr, uid, [move_id], context={})
                        except:
                            pass
                else: 
                    if voucher.journal_id.type in ['bank', 'cash'] and  voucher.type=='receipt' and voucher.tpt_cus_reconcile==False and auto_id.customer_payment and voucher.type_cash_bank != 'journal':
                        try:
                            move_pool.post(cr, uid, [move_id], context={})
                        except:
                            pass
                    if voucher.journal_id.type in ['bank', 'cash'] and  voucher.type=='payment' and voucher.tpt_sup_reconcile==False and auto_id.supplier_payment and voucher.type_cash_bank != 'journal':
                        try:
                            move_pool.post(cr, uid, [move_id], context={})
                        except:
                            pass
                    if voucher.type_cash_bank == 'journal' and auto_id.journal_vouchers:
                        try:
                            move_pool.post(cr, uid, [move_id], context={})
                        except:
                            pass
            ###
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True
    
    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference
        ##
        ##TPT-START BM - ON 03/05/2016 - FOR THROWING WARNINIG WHEN DIFFERENCE AMT IS NOT ZERO - IN CUSTOMER RECONCILIATION SCREEN
        if voucher.tpt_cus_reconcile is True and voucher.writeoff_amount!=0:
            raise osv.except_osv(_('Warning !'), _('Cr Dr not matched'))
        ##TPT END
        #TPT START - By P.VINOTHKUMAR - ON 13/04/2016 - FOR (Generate document sequence for Supplier Payment Account postings)
        sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        vals={}
        if voucher.journal_id.code=='MISC':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.journal.voucher')       
#             vals['name']='MISC/'+fiscalyear['code']+'/'+sequence
            vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
            name=vals['name']   
        if voucher.type=='receipt' and voucher.journal_id.name=='Cash' or voucher.journal_id.name=='Bank' and voucher.type=='receipt':    
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'customer.payment.account')
            vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
            name=vals['name'] 
            # Commented by P.vinothkumar on 27/06/2016 for fix wrongly displayed Narration in General ledger Number(Ticket No.3580)
#             ref = name.replace('/','')
#             ref1=ref
             # Added condition by P.vinothkumar on 27/06/2016 for fix wrongly displayed Narration in General ledger Number(Ticket No.3580)
            if not voucher.reference:
                ref = name.replace('/','')
            else:
                ref = voucher.reference
            # TPT end

            #===================================================================
            # seq_obj = self.pool.get('ir.sequence') 
            # seq_ids = seq_obj.search(cr, uid, [('code','=','customer.payment.account')]) 
            # seq_id = seq_obj.browse(cr, uid, seq_ids[0])
            # name = str(seq_id.prefix)+'/'+fiscalyear['code']+'/'+str(seq_id.number_next_actual)
            # #name = seq_id.prefix +'/'+fiscalyear['code']+'/'+'%%0%sd' % str(seq_id.padding) % seq_id.number_next_actual
            #===================================================================
        elif voucher.type=='payment' and voucher.journal_id.name=='Cash' or voucher.journal_id.name=='Bank' and voucher.type=='payment':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.supplier.payment')
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] 
                #vals['name']='SUP/'+fiscalyear['code']+'/'+sequence
                name=vals['name']        
        ##
        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
            'cost_center_id': voucher.cost_center_id.id, # added by P.vinothkumar on 23/09/2016 for adding cost_center_id from voucher
        }
        #TPT-VINOTH-COMMENTED ON 25/04/2016
        #=======================================================================
        # if voucher.type_trans:
        #     if voucher.journal_id.type == 'bank': 
        #         if voucher.type_trans == 'payment':
        #             move['doc_type'] = 'bank_pay'
        #         if voucher.type_trans == 'receipt':
        #             move['doc_type'] = 'bank_rec'
        #     if voucher.journal_id.type == 'cash':
        #         if voucher.type_trans == 'payment':
        #             move['doc_type'] = 'cash_pay'
        #         if voucher.type_trans == 'receipt':
        #             move['doc_type'] = 'cash_rec'
        #=======================================================================
        #TPT-VINOTH-UPDATED ON 25/04/2016
        if not voucher.tpt_journal:      
            if voucher.type_trans or voucher.journal_id :
                 #TPT-VINOTH-UPDATED ON 26/04/2016# 
                if voucher.journal_id.type == 'bank': 
                    if voucher.type_trans == 'payment':
                        move['doc_type'] = 'bank_pay'
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.bank.payment') 
                        #vals['name']='BP/'+fiscalyear['code']+'/'+sequence
                        vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                        name=vals['name'] 
                        move['name']=name
                    if voucher.type == 'payment' and voucher.type_trans != 'receipt':
                        move['doc_type'] = 'bank_pay'
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.bank.payment') 
                        #vals['name']='BP/'+fiscalyear['code']+'/'+sequence
                        vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                        name=vals['name'] 
                        move['name']=name             
                    if voucher.type_trans == 'receipt':
                        move['doc_type'] = 'bank_rec'
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.bank.receipt')
                        #vals['name']='BR/'+fiscalyear['code']+'/'+sequence
                        vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                        name=vals['name'] 
                        move['name']=name
                    if voucher.type == 'receipt' and voucher.type_trans != 'payment':
                        move['doc_type'] = 'bank_rec'
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.bank.receipt')
                        #vals['name']='BR/'+fiscalyear['code']+'/'+sequence
                        vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                        name=vals['name'] 
                        move['name']=name                       
                        
            if voucher.journal_id.type == 'cash':
                 #TPT-VINOTH-UPDATED ON 26/04/2016# 
                if voucher.type_trans == 'payment':
                    move['doc_type'] = 'cash_pay'
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.cash.payment')
                    #vals['name']='CP/'+fiscalyear['code']+'/'+sequence
                    vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                    name=vals['name']
                    move['name']=name
                if voucher.type=='payment' and voucher.type_trans != 'receipt':
                    move['doc_type'] = 'cash_pay'
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.cash.payment')
                    #vals['name']='CP/'+fiscalyear['code']+'/'+sequence
                    vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                    name=vals['name']
                    move['name']=name
                if voucher.type_trans == 'receipt':
                    move['doc_type'] = 'cash_rec'
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.cash.receipt')
                    #vals['name']='CR/'+fiscalyear['code']+'/'+sequence
                    vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                    name=vals['name'] 
                    move['name']=name
                if voucher.type=='receipt' and voucher.type_trans != 'payment':
                    move['doc_type'] = 'cash_rec'
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.cash.receipt')
                    #vals['name']='CR/'+fiscalyear['code']+'/'+sequence
                    vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                    name=vals['name'] 
                    move['name']=name
        else:
            if (voucher.journal_id.type == 'bank' or voucher.journal_id.type == 'cash'):
                if voucher.type == 'receipt' and voucher.type_cash_bank != 'journal':
                    move['doc_type'] = 'cus_pay'
#                     sql = '''
#                         update account_voucher set type_trans = 'receipt', sum_amount = %s where id = %s
#                     '''%(voucher_id, voucher.amount)
#                     cr.execute(sql)
                if voucher.type == 'payment' and voucher.type_cash_bank != 'journal':
                    move['doc_type'] = 'sup_pay'
#                     sql = '''
#                         update account_voucher set type_trans = 'payment', sum_amount = %s where id = %s
#                     '''%(voucher_id, voucher.amount)
#                     cr.execute(sql)
        return move
    def writeoff_move_line_get(self, cr, uid, voucher_id, line_total, move_id, name, company_currency, current_currency, context=None):
        '''
        Set a dict to be use to create the writeoff move line.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param line_total: Amount remaining to be allocated on lines.
        :param move_id: Id of account move where this line will be added.
        :param name: Description of account move line.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        currency_obj = self.pool.get('res.currency')
        move_line = {}

        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        current_currency_obj = voucher.currency_id or voucher.journal_id.company_id.currency_id
#         if (voucher.journal_id.type == 'bank' and voucher.type == 'payment' 

        if not currency_obj.is_zero(cr, uid, current_currency_obj, line_total):
            diff = line_total
            account_id = False
            write_off_name = ''
            if voucher.type_trans:
                voucher.partner_id = False
            if voucher.partner_id:
                if voucher.payment_option == 'with_writeoff':
                    account_id = voucher.writeoff_acc_id.id
                    write_off_name = voucher.comment
                elif voucher.type in ('sale', 'receipt'):
                    if voucher.partner_id.supplier:
                       account_id = voucher.partner_id.property_account_payable and voucher.partner_id.property_account_payable.id or False
                       if not account_id:
                           raise osv.except_osv(_('Warning !'), _("Please configure Account Payable for this customer!"))
                    else:
#  start  phuoc                         
                       account_id = voucher.partner_id.property_account_receivable and voucher.partner_id.property_account_receivable.id or False
                       if not account_id:
                           raise osv.except_osv(_('Warning !'), _("Please configure Account Receivable for this customer!"))
#                         if voucher.journal_id.type == 'cash':
#                             sql = '''
#                                 SELECT cus_pay_cash_id FROM tpt_posting_configuration WHERE name = 'cus_pay' and cus_pay_cash_id is not null
#                             '''
#                             cr.execute(sql)
#                             cus_pay_cash_id = cr.dictfetchone()
#                             if not cus_pay_cash_id:
#                                 raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Cash Account for Document Type is Customer Payment in GL Posting Configrution !'))
#                             account_id = cus_pay_cash_id and cus_pay_cash_id['cus_pay_cash_id'] or False
#                         else:
#                             sql = '''
#                                 SELECT cus_pay_bank_id FROM tpt_posting_configuration WHERE name = 'cus_pay' and cus_pay_bank_id is not null
#                             '''
#                             cr.execute(sql)
#                             cus_pay_bank_id = cr.dictfetchone()
#                             if not cus_pay_bank_id:
#                                 raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Bank Account for Document Type is Customer Payment in GL Posting Configrution !'))
#                             account_id = cus_pay_bank_id and cus_pay_bank_id['cus_pay_bank_id'] or False
# end phuoc
                else:
                    if voucher.partner_id.customer:
                        account_id = voucher.partner_id.property_account_receivable and voucher.partner_id.property_account_receivable.id or False
                        if not account_id:
                           raise osv.except_osv(_('Warning !'), _("Please configure Account Receivable for this customer!"))
                    else:
                        account_id = voucher.partner_id.property_account_payable and voucher.partner_id.property_account_payable.id or False
                        if not account_id:
                           raise osv.except_osv(_('Warning !'), _("Please configure Account Payable for this customer!"))
#                         if voucher.journal_id.type == 'cash':
#                             sql = '''
#                                 SELECT sup_pay_cash_id FROM tpt_posting_configuration WHERE name = 'sup_pay' and sup_pay_cash_id is not null
#                             '''
#                             cr.execute(sql)
#                             sup_pay_cash_id = cr.dictfetchone()
#                             if not sup_pay_cash_id:
#                                 raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Cash Account for Document Type is Supplier Payment in GL Posting Configrution !'))
#                             account_id = sup_pay_cash_id and sup_pay_cash_id['sup_pay_cash_id'] or False
#                         else:
#                             sql = '''
#                                 SELECT sup_pay_bank_id FROM tpt_posting_configuration WHERE name = 'sup_pay' and sup_pay_bank_id is not null
#                             '''
#                             cr.execute(sql)
#                             sup_pay_bank_id = cr.dictfetchone()
#                             if not sup_pay_bank_id:
#                                 raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Bank Account for Document Type is Supplier Payment in GL Posting Configrution !'))
#                             account_id = sup_pay_bank_id and sup_pay_bank_id['sup_pay_bank_id'] or False
            else:
                account_id = voucher.account_id.id
            sign = voucher.type == 'payment' and -1 or 1
            move_line = {
                'name': write_off_name or name,
                'account_id': account_id,
                'move_id': move_id,
#                 'partner_id': voucher.partner_id.id,
                'date': voucher.date,
                'credit': diff > 0 and diff or 0.0,
                'debit': diff < 0 and -diff or 0.0,
                'amount_currency': company_currency <> current_currency and (sign * -1 * voucher.writeoff_amount) or 0.0,
                'currency_id': company_currency <> current_currency and current_currency or False,
                'analytic_account_id': voucher.analytic_id and voucher.analytic_id.id or False,
            }
            if voucher.type_trans:
                move_line.update({
                                  'partner_id': False,
                                  })
            else:
                move_line.update({
                                  'partner_id': voucher.partner_id.id,
                                  })

        return move_line
    
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'

        if not context.get('move_line_ids', False):
            ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        remaining_amount = price
        #voucher line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
#                         rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
#                         rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = False

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default
    
    def onchange_journal_voucher(self, cr, uid, ids, line_ids=False, tax_id=False, price=0.0, partner_id=False, journal_id=False, ttype=False, company_id=False, context=None):
        """price
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        default = {
            'value':{},
        }
        journal_pool = self.pool.get('account.journal')
        if not journal_id:
            return default
        if not partner_id and journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            account_id = False
            if journal.type in ('sale','sale_refund'):
                account_id = partner.property_account_receivable.id
            elif journal.type in ('purchase', 'purchase_refund','expense'):
                account_id = partner.property_account_payable.id
            else:
                if not journal.default_credit_account_id or not journal.default_debit_account_id:
                    raise osv.except_osv(_('Error!'), _('Please define default credit/debit accounts on the journal "%s".') % (journal.name))
                account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
            default['value']['account_id'] = account_id
            return default

        partner_pool = self.pool.get('res.partner')

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        tr_type = False
        if journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
            tr_type = 'sale'
        elif journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
            tr_type = 'purchase'
        else:
            if not journal.default_credit_account_id or not journal.default_debit_account_id:
                raise osv.except_osv(_('Error!'), _('Please define default credit/debit accounts on the journal "%s".') % (journal.name))
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
            tr_type = 'receipt'

        default['value']['account_id'] = account_id
        default['value']['type'] = ttype or tr_type
        default['value']['partner_id'] = partner_id
        vals = self.onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, time.strftime('%Y-%m-%d'), price, ttype, company_id, context)
        default['value'].update(vals.get('value'))
        return default
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{} }
        ###  onchange field tpt_journal de an hien field
        if journal:
            if journal.type == "cash":
                vals['value'].update({'tpt_journal':'cash','cheque_date':False, 'cheque_number':False, 'bank_name':False})
            else:
                vals['value'].update({'tpt_journal':'bank'})
        ###
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        vals['value'].update({'currency_id': currency_id})
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
#         if partner_id:
#             res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
#             for key in res.keys():
#                 vals[key].update(res[key])
                
        if context.get('tpt_remove_dr_cr',False):
            vals['value']['line_dr_ids']=False
            vals['value']['line_cr_ids']=False
            
        if context.get('tpt_show_cr',False):
            vals['value']['line_dr_ids']=False
            
        if context.get('tpt_show_dr',False):
            vals['value']['line_cr_ids']=False
            
        return vals
    
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        for key in vals.keys():
            res[key].update(vals[key])
        if context.get('tpt_remove_dr_cr',False):
            res['value']['line_dr_ids']=False
            res['value']['line_cr_ids']=False
             
        if context.get('tpt_show_cr',False):
            res['value']['line_dr_ids']=False
             
        if context.get('tpt_show_dr',False):
            res['value']['line_cr_ids']=False
#         return res
        return {'value': {}}
    
    def onchange_type_trans(self, cr, uid, ids, type_trans, context=None):
        return {'value': {'type': type_trans}}
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        if not journal_id:
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=ctx)
        vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])
        #TODO: can probably be removed now
        #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
        # [pre_line, line_cr_ids, payment_rate...] for type purchase.
        # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
        # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
        # onchange returns a value for them
        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        if context.get('tpt_remove_dr_cr',False):
            res['value']['line_dr_ids']=False
            res['value']['line_cr_ids']=False
            
        if context.get('tpt_show_cr',False):
            res['value']['line_dr_ids']=False
            
        if context.get('tpt_show_dr',False):
            res['value']['line_cr_ids']=False
            
        return res
    
    def onchange_date(self, cr, uid, ids, date, currency_id, payment_rate_currency_id, amount, company_id, context=None):
        """
        @param date: latest value from user input for field date
        @param args: other arguments
        @param context: context arguments, like lang, time zone
        @return: Returns a dict which contains new values, and context
        """
        if context is None:
            context ={}
        res = {'value': {},'warning':{}}
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if date and date > current:
            vals.update({'date':current})
            warning = {
                'title': _('Warning!'),
                'message': _('Date: Not allow future date!')
            }
            res.update({'value':vals,'warning':warning})
        
        
        #set the period of the voucher
        period_pool = self.pool.get('account.period')
        currency_obj = self.pool.get('res.currency')
        ctx = context.copy()
        ctx.update({'company_id': company_id, 'account_period_prefer_normal': True})
        voucher_currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        pids = period_pool.find(cr, uid, date, context=ctx)
        if pids:
            res['value'].update({'period_id':pids[0]})
        if payment_rate_currency_id:
            ctx.update({'date': date})
            payment_rate = 1.0
            if payment_rate_currency_id != currency_id:
                tmp = currency_obj.browse(cr, uid, payment_rate_currency_id, context=ctx).rate
                payment_rate = tmp / currency_obj.browse(cr, uid, voucher_currency_id, context=ctx).rate
            vals = self.onchange_payment_rate_currency(cr, uid, ids, voucher_currency_id, payment_rate, payment_rate_currency_id, date, amount, company_id, context=context)
            vals['value'].update({'payment_rate': payment_rate})
            for key in vals.keys():
                res[key].update(vals[key])
        return res
    #
    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', False)

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False
    def _get_journal(self, cr, uid, context=None):
        if context is None: context = {}
        invoice_pool = self.pool.get('account.invoice')
        journal_pool = self.pool.get('account.journal')
        if context.get('invoice_id', False):
            currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
            journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id)], limit=1)
            return journal_id and journal_id[0] or False
        if context.get('journal_id', False):
            return context.get('journal_id')
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context.get('search_default_journal_id')

        ttype = context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        res = self._make_journal_search(cr, uid, ttype, context=context)
        return res and res[0] or False

    def _get_tax(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if not journal_id:
            ttype = context.get('type', 'bank')
            res = journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
            if not res:
                return False
            journal_id = res[0]

        if not journal_id:
            return False
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
            return tax_id
        return False

    def _get_payment_rate_currency(self, cr, uid, context=None):
        """
        Return the default value for field payment_rate_currency_id: the currency of the journal
        if there is one, otherwise the currency of the user's company
        """
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.currency:
                return journal.currency.id
        #no journal given in the context, use company currency as default
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id

    def _get_currency(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.currency:
                return journal.currency.id
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id

    def _get_partner(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('partner_id', False)

    def _get_reference(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('reference', False)

    def _get_narration(self, cr, uid, context=None):
        if context is None: context = {}
        return context.get('narration', False)

    def _get_amount(self, cr, uid, context=None):
        if context is None:
            context= {}
        return context.get('amount', 0.0)
    def _get_journal_currency(self, cr, uid, ids, name, args, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = voucher.journal_id.currency and voucher.journal_id.currency.id or voucher.company_id.currency_id.id
        return res

    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        currency_obj = self.pool.get('res.currency')
        res = {}
        debit = credit = 0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            sign = voucher.type == 'payment' and -1 or 1
            for l in voucher.line_dr_ids:
                debit += l.amount
            for l in voucher.line_cr_ids:
                credit += l.amount
            currency = voucher.currency_id or voucher.company_id.currency_id
            res[voucher.id] =  currency_obj.round(cr, uid, currency, voucher.amount - sign * (credit - debit))
        return res
    #===========================================================================
    # _defaults = {
    #     'active': True,
    #     'period_id': _get_period,
    #     'partner_id': _get_partner,
    #     'journal_id':_get_journal,
    #     'currency_id': _get_currency,
    #     'reference': _get_reference,
    #     'narration':_get_narration,
    #     'amount': _get_amount,
    #     'type':_get_type,
    #     'state': 'draft',
    #     'pay_now': 'pay_now',
    #     'name': '',
    #     'date': lambda *a: time.strftime('%Y-%m-%d'),
    #     'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=c),
    #     'tax_id': _get_tax,
    #     'payment_option': 'without_writeoff',
    #     'comment': _('Write-Off'),
    #     'payment_rate': 1.0,
    #     'payment_rate_currency_id': _get_payment_rate_currency,
    # }    
    #===========================================================================
#          
account_voucher()

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
                'journal_flag':fields.boolean('Journal Flag',readonly =True ),
    }
sale_order()

class tpt_material_issue(osv.osv):
    _inherit = "tpt.material.issue"
    
    def init(self, cr):
        sql = '''
             update purchase_order_line set item_text=(select item_text from tpt_purchase_quotation_line
                 where po_indent_id = purchase_order_line.po_indent_no and product_id = purchase_order_line.product_id
                     and product_uom_qty=purchase_order_line.product_qty limit 1)
        '''
        cr.execute(sql)
        sql ='''
            update stock_move set item_text=(select item_text from purchase_order_line where id=stock_move.purchase_line_id limit 1)
        '''
        cr.execute(sql)
        
    _columns = {
                'gl_account_id': fields.many2one('account.account', 'GL Account',states={'done':[('readonly', True)]}),
                'warehouse':fields.many2one('stock.location','Source Location',states={'done':[('readonly', True)]}),
                'dest_warehouse_id': fields.many2one('stock.location','Destination Location',states={'done':[('readonly', True)]}),
                
                }
    
#     def _check_stock_qty(self, cr, uid, ids, context=None):
#         for issue in self.browse(cr, uid, ids, context=context):
#             for line in issue.material_issue_line:
#                 sql = '''
#                     select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty, product_id 
#                     from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where name = %s) group by product_id
#                 '''%(issue.name.id)
#                 cr.execute(sql)
#                 for sum in cr.dictfetchall():
#                     product_id = self.pool.get('product.product').browse(cr,uid,sum['product_id'])
#                     sql = '''
#                         select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
#                             (select st.product_qty
#                                 from stock_move st 
#                                 where st.state='done' and st.product_id=%s and st.location_dest_id = %s 
#                             union all
#                             select st.product_qty*-1
#                                 from stock_move st 
#                                 where st.state='done' and st.product_id=%s and st.location_id = %s
#                             )foo
#                     '''%(sum['product_id'],issue.warehouse.id,sum['product_id'],issue.warehouse.id)
#                     cr.execute(sql)
#                     ton_sl = cr.dictfetchone()['ton_sl']
#                     if sum['product_isu_qty'] > ton_sl:
#                         raise osv.except_osv(_('Warning!'),_("You are confirm %s but only %s available for this product '%s' " %(sum['product_isu_qty'], ton_sl,product_id.default_code)))
#                         return False
#         return True
#     _constraints = [
#         (_check_stock_qty, 'Identical Data', []),
#     ]
    
    def bt_approve(self, cr, uid, ids, context=None):
        price = 0.0
        product_price = 0.0
        tpt_cost = 0
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        journal_line = []
        dest_id = False
        move_obj = self.pool.get('stock.move')
                
        
        for line in self.browse(cr, uid, ids):
            if line.request_type == 'production':
                dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
            else:
                location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
                if location_ids:
                    dest_id = location_ids[0]
            
            for p in line.material_issue_line:
                onhand_qty = 0.0
                location_id = False
                locat_ids = []
                parent_ids = []
                cate_name = p.product_id.categ_id and p.product_id.categ_id.cate_name or False
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty, product_id 
                    from tpt_material_issue_line where product_id = %s and material_issue_id in (select id from tpt_material_issue where name = %s) group by product_id
                '''%(p.product_id.id, line.name.id)
                cr.execute(sql)
                for sum in cr.dictfetchall():
                    product_id = self.pool.get('product.product').browse(cr,uid,sum['product_id'])
                    sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id = %s 
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id = %s
                            )foo
                    '''%(sum['product_id'],line.warehouse.id,sum['product_id'],line.warehouse.id)
                    cr.execute(sql)
                    ton_sl = cr.dictfetchone()['ton_sl']
                    if sum['product_isu_qty'] > ton_sl:
                        raise osv.except_osv(_('Warning!'),_("You are confirm %s but only %s available for this product '%s' " %(sum['product_isu_qty'], ton_sl,product_id.default_code)))
#                 if cate_name == 'finish':
#                     parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
#                     if parent_ids:
#                         locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
#                     if locat_ids:
#                         location_id = locat_ids[0]
#                         sql = '''
#                             select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
#                                 (select st.product_qty as product_qty
#                                     from stock_move st 
#                                     where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
#                                  union all
#                                  select st.product_qty*-1 as product_qty
#                                     from stock_move st 
#                                     where st.state='done'
#                                     and st.product_id=%s
#                                                 and location_id=%s
#                                                 and location_dest_id != location_id
#                                 )foo
#                         '''%(p.product_id.id,location_id,p.product_id.id,location_id)
#                         cr.execute(sql)
#                         onhand_qty = cr.dictfetchone()['onhand_qty']
                if cate_name == 'raw':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                    location_id = locat_ids[0]
                if cate_name == 'spares':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                if location_id and cate_name != 'finish':
                    if p.product_id.id==10733:
                        print ""
                    sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                                and st.location_dest_id != st.location_id
                                and ( picking_id is not null 
                                or inspec_id is not null 
                                or (st.id in (select move_id from stock_inventory_move_rel))
                        )
                    '''%(location_id,p.product_id.id,line.date_expec)
                    cr.execute(sql)
                    inventory = cr.dictfetchone()
                    if inventory:
                        hand_quantity = inventory['ton_sl'] or 0
                        total_cost = inventory['total_cost'] or 0
    #                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                       select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl, case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and issue_id is not null
                            
                    '''%(location_id,p.product_id.id,line.date_expec)
                    cr.execute(sql)
                    for issue in cr.dictfetchall():
                        hand_quantity_issue = issue['ton_sl'] or 0
                        total_cost_issue = issue['total_cost'] or 0
                    #TPT By Balamurugan Purushothaman on 14/10/2015 - To avoid throwing Warning - Physical Inventories to Material Issue
                    opening_stock_value = 0
                    if (hand_quantity-hand_quantity_issue)!=0:
                        opening_stock_value = (total_cost-total_cost_issue)/(hand_quantity-hand_quantity_issue)
                    #===========================================================
                    # ##TPT-By Balamurugan Purushothaman - ON 31/08/2016 - TO TAKE AVG COST AS UNIT PRICE FOR STOCK_MOVE ENTRIES
                    # avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',p.product_id.id),('warehouse_id','=',line.warehouse.id)])
                    # unit = 1
                    # if avg_cost_ids:
                    #     avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                    #     unit = avg_cost_id.avg_cost or 0
                    # opening_stock_value = unit * p.product_isu_qty
                    # ##TPT-END
                    #===========================================================
                    
                rs = {
                      'name': '/',
                      'product_id':p.product_id and p.product_id.id or False,
                      'product_qty':p.product_isu_qty or False,
                      'product_uom':p.uom_po_id and p.uom_po_id.id or False,
                      'location_id':line.warehouse and line.warehouse.id or False,
                      'location_dest_id':dest_id,
                      'issue_id':line.id,
                      'date':line.date_expec or False,
                      'price_unit': opening_stock_value or 0,
                      }
                
                move_id = move_obj.create(cr,uid,rs)
                # boi vi field price unit tu dong lam tron 2 so thap phan nen phai dung sql de update lai
                sql = '''
                        update stock_move set price_unit = %s where id = %s
                '''%(opening_stock_value, move_id)
                cr.execute(sql)
                move_obj.action_done(cr, uid, [move_id])
                cr.execute(''' update stock_move set date=%s,date_expected=%s where id=%s ''',(line.date_expec,line.date_expec,move_id,))
            date_period = line.date_expec
            sql = '''
                select id from account_journal where name='Stock Journal' or code='STJ'
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            if not journal_ids:
                raise osv.except_osv(_('Warning!'),_('Please config Journal "Stock Journal"!'))
            sql = '''
                select id from account_period where '%s' between date_start and date_stop and special is False
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
             
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                
            for mater in line.material_issue_line:
#                 price += mater.product_id.standard_price * mater.product_isu_qty
                acc_expense = mater.product_id and mater.product_id.property_account_expense and mater.product_id.property_account_expense.id or False
                acc_asset = mater.product_id and mater.product_id.product_asset_acc_id and mater.product_id.product_asset_acc_id.id or False
                if not acc_expense or not acc_asset:
                    raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for all materials!'))
                avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                unit = 1
                if avg_cost_ids:
                    avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                    unit = avg_cost_id.avg_cost or 0
                sql = '''
                    select price_unit from stock_move where product_id=%s and product_qty=%s and issue_id=%s
                '''%(mater.product_id.id,mater.product_isu_qty,mater.material_issue_id.id)
                cr.execute(sql)
                move_price = cr.fetchone()
                if move_price and move_price[0] and move_price[0]>0:
                    unit=move_price[0]
                if not unit or unit<0:
                    unit=1
                price += unit * mater.product_isu_qty
                product_price = unit * mater.product_isu_qty
                
                journal_line.append((0,0,{
                            'name':line.doc_no + ' - ' + mater.product_id.name, 
                            'account_id': acc_asset,
                            'debit':0,
                            'credit':product_price,
                            'product_id':mater.product_id.id,
                                       }))
                journal_line.append((0,0,{
                            'name':line.doc_no + ' - ' + mater.product_id.name, 
                            'account_id': acc_expense,
                            'credit':0,
                            'debit':product_price,
                            'product_id':mater.product_id.id,
                        }))
            value={
                'journal_id':journal_ids[0],
                'period_id':period_ids[0] ,
                'ref': line.doc_no,
                'date': date_period,
                'material_issue_id': line.id,
                'line_id': journal_line,
                'doc_type':'good'
                }
            new_jour_id = account_move_obj.create(cr,uid,value)
            auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
            if auto_ids:
                auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                if auto_id.material_issue:
                    try:
                        account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                    except:
                        pass
            self.write(cr, uid, ids,{'state':'done'})
        return True  
    
    def bt_create_posting(self, cr, uid, ids, context=None):
        
        price = 0.0
        product_price = 0.0
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        journal_line = []
        dest_id = False
        move_obj = self.pool.get('stock.move')
        acc_ids = []
        for line in self.browse(cr, uid, ids):
            journal_line = []
            sql = '''
                select id from account_move where material_issue_id = %s
            '''%(line.id)
            cr.execute(sql)
            acc_ids = cr.dictfetchone()
            if acc_ids:
                raise osv.except_osv(_('Warning!'),_('This Material issue was created Posting!'))
            if line.state=='done':
                date_period = line.date_expec
                sql = '''
                    select id from account_journal where name='Stock Journal' or code='STJ'
                '''
                cr.execute(sql)
                journal_ids = [r[0] for r in cr.fetchall()]
                if not journal_ids:
                    raise osv.except_osv(_('Warning!'),_('Please config Journal "Stock Journal"!'))
                sql = '''
                    select id from account_period where '%s' between date_start and date_stop and special is False
                '''%(date_period)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                 
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                    
                for mater in line.material_issue_line:
    #                 price += mater.product_id.standard_price * mater.product_isu_qty
                    acc_expense = mater.product_id and mater.product_id.property_account_expense and mater.product_id.property_account_expense.id or False
                    acc_asset = mater.product_id and mater.product_id.product_asset_acc_id and mater.product_id.product_asset_acc_id.id or False
                    if not acc_expense or not acc_asset:
                        raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for materials %s!'%(mater.product_id.default_code)))
                    avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                    unit = 1
                    if avg_cost_ids:
                        avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                        unit = avg_cost_id.avg_cost or 0
                    sql = '''
                        select price_unit from stock_move where product_id=%s and product_qty=%s and issue_id=%s
                    '''%(mater.product_id.id,mater.product_isu_qty,mater.material_issue_id.id)
                    cr.execute(sql)
                    move_price = cr.fetchone()
                    if move_price and move_price[0] and move_price[0]>0:
                        unit=move_price[0]
                    if not unit or unit<0:
                        unit=1
                    price += unit * mater.product_isu_qty
                    product_price = unit * mater.product_isu_qty
                
                    journal_line.append((0,0,{
                                            'name':line.doc_no + ' - ' + mater.product_id.name, 
                                            'account_id': acc_asset,
                                            'debit':0,
                                            'credit':product_price,
                                            'product_id':mater.product_id.id,
                                             
                                           }))
                    journal_line.append((0,0,{
                                'name':line.doc_no + ' - ' + mater.product_id.name, 
                                'account_id': acc_expense,
                                'credit':0,
                                'debit':product_price,
                                'product_id':mater.product_id.id,
                            }))
                value={
                    'journal_id':journal_ids[0],
                    'period_id':period_ids[0] ,
                    'ref': line.doc_no,
                    'date': date_period,
                    'material_issue_id': line.id,
                    'line_id': journal_line,
                    'doc_type':'good'
                    }
                new_jour_id = account_move_obj.create(cr,uid,value)
                auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                if auto_ids:
                    auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                    if auto_id.material_issue:
                        try:
                            account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                        except:
                            pass
                print 'TPT Create Done', line.id,line.doc_no
        return True
    
tpt_material_issue()    

class tpt_hr_payroll_approve_reject(osv.osv):
    _inherit = 'tpt.hr.payroll.approve.reject'    
#         def approve_payroll(self, cr, uid, ids, context=None):
#         for line in self.browse(cr,uid,ids):
#             payroll_obj = self.pool.get('arul.hr.payroll.executions')
#             payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state','=','confirm')])
#             for payroll in payroll_obj.browse(cr,uid,payroll_ids):
#                 payroll_obj.write(cr, uid, payroll.id, {'state':'approve'})
#         return self.write(cr, uid, line.id, {'state':'done'})

    def get_account_amount(self,cr,uid,payroll_ids):
        res = {}
        welfare = 0.0
        if payroll_ids:
#             payroll_ids = str(payroll_ids).replace("[","(")
#             payroll_ids = payroll_ids.replace("]",")")
            
            sql_gross = '''
                select sum(float) as gross_salary from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='GROSS_SALARY')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_gross)
            gross = cr.dictfetchone()['gross_salary'] or 0.0
            sql_provident = '''
                select sum(float) as provident from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='PF.D')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_provident)
            provident = cr.dictfetchone()['provident'] or 0.0
            sql_vpf = '''
                select sum(float) as vpf from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='VPF.D')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_vpf)
            vpf = cr.dictfetchone()['vpf'] or 0.0
            sql_tax = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='PT')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_tax)
            tax = cr.dictfetchone()['tax'] or 0.0
            sql_lwf = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LWF')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_lwf)
            lwf = cr.dictfetchone()['tax'] or 0.0
            
            sql_prem = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='INS_LIC_PREM')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_prem)
            lic_premium = cr.dictfetchone()['tax'] or 0.0
            
            ### Excutive & Staff - Worker
            sql_ins = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='INS_OTHERS')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_ins)
            ins_oth = cr.dictfetchone()['tax'] or 0.0
            
            sql_loan = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LOAN_VVTI')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_loan)
            vvt_loan = cr.dictfetchone()['tax'] or 0.0
            
            sql_hdfc = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LOAN_HDFC')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_hdfc)
            vvt_hdfc = cr.dictfetchone()['tax'] or 0.0
            
            sql_hfl = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LOAN_LIC_HFL')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_hfl)
            hfl = cr.dictfetchone()['tax'] or 0.0
            
            sql_tmb = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LOAN_TMB')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_tmb)
            tmb = cr.dictfetchone()['tax'] or 0.0
            
            sql_sbt = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LOAN_SBT')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_sbt)
            sbt = cr.dictfetchone()['tax'] or 0.0
            
            sql_other = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LOAN_OTHERS')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_other)
            other = cr.dictfetchone()['tax'] or 0.0
            
            sql_oa = '''
                select sum(float) as allowance from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='OA')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_oa)
            oa = cr.dictfetchone()['allowance'] or 0.0
            
            sql_other = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='IT')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_other)
            it = cr.dictfetchone()['tax'] or 0.0
            
#             sql_ma = '''
#                 select sum(float) as allowance from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='MA')
#                 and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
#             '''%(payroll_ids)
#             cr.execute(sql_ma)
#             ma = cr.dictfetchone()['allowance'] or 0.0
#             welfare = oa + ma
            sql_welfare = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='F.D')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_welfare)
            welfare = cr.dictfetchone()['tax'] or 0.0
            
            #TPT - BM - ON 29/10/2015
            sql_canteen = ''' 
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='C.D')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_canteen)
            canteen = cr.dictfetchone()['tax'] or 0.0
            
            sql_esi = '''
                select sum(float) as tax from arul_hr_payroll_other_deductions where deduction_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='ESI.D')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_esi)
            esi = cr.dictfetchone()['tax'] or 0.0
            
            sql_ma = '''
                select sum(float) as allowance from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='SHD')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_ma)
            shd = cr.dictfetchone()['allowance'] or 0.0
            
            ### END Excutive & Staff - Worker
            
            sum_credit = (round(provident) + round(vpf) + round(tax) + round(lwf) + round(welfare) + round(canteen) + round(lic_premium) +
                           + round(ins_oth) + round(vvt_loan) + round(vvt_hdfc) + round(hfl) + round(tmb) + round(sbt) + round(other) + round(esi) + round(it))
            diff = round(gross) - sum_credit
            gross = round(gross) - round(shd)
            
            res = {'gross':round(gross),
                   'provident':round(provident),
                   'vpf':round(vpf),
                   'tax':round(tax),
                   'lwf':round(lwf),
                   'lic_premium':round(lic_premium),
                   'welfare':round(welfare),
                   'canteen':round(canteen),#TPT
                   'ins_oth':round(ins_oth),
                   'vvt_loan':round(vvt_loan),
                   'vvt_hdfc':round(vvt_hdfc),
                   'hfl':round(hfl),
                   'sbt':round(sbt),
                   'other':round(other),
                   'tmb':round(tmb),
                   'diff':round(diff),
                   'it':round(it),
                   'shd':round(shd),
                   'esi':round(esi),
                   }
        return res
    
    def approve_payroll(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            account_move_obj = self.pool.get('account.move')
            period_obj = self.pool.get('account.period')
            payroll_obj = self.pool.get('arul.hr.payroll.executions')
            payroll_area_obj = self.pool.get('arul.hr.payroll.area')
            payroll_excutive_id = False
            payroll_staff_id = False
            payroll_workers_id = False
            
            excutive_ids = payroll_area_obj.search(cr, uid, [('code', '=', 'S1')])
            if excutive_ids:
                payroll_excutive_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state','=','confirm'),('payroll_area_id','=',excutive_ids[0])])
                if payroll_excutive_ids:
                    payroll_excutive_id = payroll_excutive_ids[0]
                
            staff_ids = payroll_area_obj.search(cr, uid, [('code', '=', 'S2')])
            if staff_ids:
                payroll_staff_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state','=','confirm'),('payroll_area_id','=',staff_ids[0])])
                if payroll_staff_ids:
                    payroll_staff_id = payroll_staff_ids[0]
            
            workers_ids = payroll_area_obj.search(cr, uid, [('code', '=', 'S3')])
            if workers_ids:
                payroll_workers_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state','=','confirm'),('payroll_area_id','=',workers_ids[0])])
                if payroll_workers_ids:
                    payroll_workers_id = payroll_workers_ids[0]
            
            configuration_obj = self.pool.get('tpt.posting.configuration')
            configuration_ids = configuration_obj.search(cr, uid, [('name', '=','payroll'),('state', '=','done')])
            if not configuration_ids:
                raise osv.except_osv(_('Warning!'),_('GL Posting Configuration is missed. Please configure it in GL Posting Configuration master!'))
            year = str(line.year)
            month = str(line.month)
            sql_journal = '''
                select id from account_journal where name='Payroll Journal'
            '''
            cr.execute(sql_journal)
            journal_ids = [r[0] for r in cr.fetchall()]
            if not journal_ids:
                raise osv.except_osv(_('Warning!'),_('Please config Journal "Payroll Journal"!'))
            journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0]) 
            for configuration in configuration_obj.browse(cr,uid,configuration_ids):
                gross_acc = configuration.salari_id and configuration.salari_id.id or False
                provident_acc = configuration.pfp_id and configuration.pfp_id.id or False
                vpf_acc = configuration.vpf_id and configuration.vpf_id.id or False
                welfare_acc = configuration.staff_welfare_id and configuration.staff_welfare_id.id or False
                canteen_acc = configuration.canteen_expense_id and configuration.canteen_expense_id.id or False#TPT-BM-ON 29/10/2015
                lic_premium_acc = configuration.lic_id and configuration.lic_id.id or False
                pro_tax_acc = configuration.profes_tax_id and configuration.profes_tax_id.id or False
                lwf_acc = configuration.lwf_id and configuration.lwf_id.id or False
                other_insu_acc = configuration.other_insu and configuration.other_insu.id or False
                vvti_acc = configuration.vvti_id and configuration.vvti_id.id or False
                lic_hfl_acc = configuration.lic_hfl_id and configuration.lic_hfl_id.id or False
                hdfc_acc = configuration.hdfc_id and configuration.hdfc_id.id or False
                tmb_acc = configuration.tmb_id and configuration.tmb_id.id or False
                sbt_acc = configuration.sbt_id and configuration.sbt_id.id or False
                other_loan_acc = configuration.other_loan_id and configuration.other_loan_id.id or False
                it_acc = configuration.it_id and configuration.it_id.id or False
                shd_acc = configuration.shd_id and configuration.shd_id.id or False
                esi_acc = configuration.esi_id and configuration.esi_id.id or False
                
                salari_acc = configuration.salari_payable_id and configuration.salari_payable_id.id or False
                wages_acc = configuration.wages_id and configuration.wages_id.id or False
                wages_payable_acc = configuration.wages_payable_id and configuration.wages_payable_id.id or False
                if not gross_acc or not provident_acc or not vpf_acc or not welfare_acc or not lic_premium_acc \
                or not pro_tax_acc or not lwf_acc or not other_insu_acc or not vvti_acc or not lic_hfl_acc or not hdfc_acc \
                or not tmb_acc or not sbt_acc or not other_loan_acc or not salari_acc or not wages_acc or not wages_payable_acc or not it_acc or not shd_acc or not esi_acc:
                    raise osv.except_osv(_('Warning!'),_('GL Posting Configuration is missed. Please configure it in GL Posting Configuration master!'))
                
            if payroll_excutive_id:
                excutive = payroll_obj.browse(cr,uid,payroll_excutive_id)
                sql = '''
                    select id
                    from account_period where EXTRACT(year from date_start)='%s' and EXTRACT(month from date_start)='%s'
                '''%(year,month)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                
                for period_id in period_obj.browse(cr,uid,period_ids):
                    res1 = {}
                    journal_s1_line = []
                    res1 = self.get_account_amount(cr,uid,payroll_excutive_id)
                    if res1['gross'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': gross_acc,
                                    'debit':res1['gross'],
                                    'credit':0,
                                   }))
                    if res1['shd'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': shd_acc,
                                    'debit':res1['shd'],
                                    'credit':0,
                                   }))
                    if res1['provident'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': provident_acc,
                                    'debit':0,
                                    'credit':res1['provident'],
                                   }))
                    if res1['vpf'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': vpf_acc,
                                    'debit':0,
                                    'credit':res1['vpf'],
                                   }))
                    if res1['esi'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': esi_acc,
                                    'debit':0,
                                    'credit':res1['esi'],
                                   }))
                    if res1['welfare'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': welfare_acc,
                                    'debit':0,
                                    'credit':res1['welfare'],
                                   }))
                    if res1['canteen'] > 0: #TPT-BM-ON 29/10/2015
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': canteen_acc,
                                    'debit':0,
                                    'credit':res1['canteen'],
                                   }))
                    if res1['lic_premium'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lic_premium_acc,
                                    'debit':0,
                                    'credit':res1['lic_premium'],
                                   }))
                    if res1['tax'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': pro_tax_acc,
                                    'debit':0,
                                    'credit':res1['tax'],
                                   }))
                    if res1['lwf'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lwf_acc,
                                    'debit':0,
                                    'credit':res1['lwf'],
                                   }))
                    if res1['ins_oth'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': other_insu_acc,
                                    'debit':0,
                                    'credit':res1['ins_oth'],
                                   }))
                    if res1['vvt_loan'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': vvti_acc, 
                                    'debit':0,
                                    'credit':res1['vvt_loan'],
                                   }))
                    if res1['vvt_hdfc'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': hdfc_acc,
                                    'debit':0,
                                    'credit':res1['vvt_hdfc'],
                                   }))
                    if res1['hfl'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lic_hfl_acc,
                                    'debit':0,
                                    'credit':res1['hfl'],
                                   }))
                    if res1['sbt'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': sbt_acc,
                                    'debit':0,
                                    'credit':res1['sbt'],
                                   }))
                    if res1['other'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': other_loan_acc,
                                    'debit':0,
                                    'credit':res1['other'],
                                   }))
                    if res1['tmb'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': tmb_acc,
                                    'debit':0,
                                    'credit':res1['tmb'],
                                   }))
                    if res1['it'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': it_acc,
                                    'debit':0,
                                    'credit':res1['it'],
                                   }))
                    if res1['diff'] > 0:
                        journal_s1_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': salari_acc,
                                    'debit':0,
                                    'credit':res1['diff'],
                                   }))
                    
                value_s1={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': line.post_date,#time.strftime('%Y-%m-%d'),
                    'line_id': journal_s1_line,
                    'doc_type':'payroll'
                    }
                context.update({'get_tpt_payroll': 'excutive'})
                if context.get('tpt_review_posting',False) and context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'excutive':
                    return value_s1
                if context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'posting':
                    new_s1_jour_id = account_move_obj.create(cr,uid,value_s1)
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id.payroll:
                            try:
                                account_move_obj.button_validate(cr,uid, [new_s1_jour_id], context)
                            except:
                                pass
                    payroll_obj.write(cr, uid, excutive.id, {'state':'approve'})
            if payroll_staff_id:
                context.update({'get_tpt_payroll': 'excutive'})
                staff = payroll_obj.browse(cr,uid,payroll_staff_id)
                sql = '''
                    select id
                    from account_period where EXTRACT(year from date_start)='%s' and EXTRACT(month from date_start)='%s'
                '''%(year,month)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                for period_id in period_obj.browse(cr,uid,period_ids):
                    res2 = {}
                    journal_s2_line = []   
                    res2 = self.get_account_amount(cr,uid,payroll_staff_id)
                    if res2['gross'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': gross_acc,
                                    'debit':res2['gross'],
                                    'credit':0,
                                   }))
                    if res2['shd'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': shd_acc,
                                    'debit':res2['shd'],
                                    'credit':0,
                                   }))
                    if res2['provident'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': provident_acc,
                                    'debit':0,
                                    'credit':res2['provident'],
                                   }))
                    if res2['vpf'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': vpf_acc,
                                    'debit':0,
                                    'credit':res2['vpf'],
                                   }))
                    if res2['esi'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': esi_acc,
                                    'debit':0,
                                    'credit':res2['esi'],
                                   }))
                    if res2['welfare'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': welfare_acc,
                                    'debit':0,
                                    'credit':res2['welfare'],
                                   }))
                    if res2['canteen'] > 0: #TPT-BM-ON 29/10/2015
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': canteen_acc,
                                    'debit':0,
                                    'credit':res2['canteen'],
                                   }))
                    if res2['lic_premium'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lic_premium_acc,
                                    'debit':0,
                                    'credit':res2['lic_premium'],
                                   }))
                    if res2['tax'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': pro_tax_acc,
                                    'debit':0,
                                    'credit':res2['tax'],
                                   }))
                    if res2['lwf'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lwf_acc,
                                    'debit':0,
                                    'credit':res2['lwf'],
                                   }))
                    if res2['ins_oth'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': other_insu_acc,
                                    'debit':0,
                                    'credit':res2['ins_oth'],
                                   }))
                    if res2['vvt_loan'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': vvti_acc, 
                                    'debit':0,
                                    'credit':res2['vvt_loan'],
                                   }))
                    if res2['vvt_hdfc'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': hdfc_acc,
                                    'debit':0,
                                    'credit':res2['vvt_hdfc'],
                                   }))
                    if res2['hfl'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lic_hfl_acc,
                                    'debit':0,
                                    'credit':res2['hfl'],
                                   }))
                    if res2['sbt'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': sbt_acc,
                                    'debit':0,
                                    'credit':res2['sbt'],
                                   }))
                    if res2['other'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': other_loan_acc,
                                    'debit':0,
                                    'credit':res2['other'],
                                   }))
                    if res2['tmb'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': tmb_acc,
                                    'debit':0,
                                    'credit':res2['tmb'],
                                   }))
                    if res2['it'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': it_acc,
                                    'debit':0,
                                    'credit':res2['it'],
                                   }))
                    if res2['diff'] > 0:
                        journal_s2_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': salari_acc,
                                    'debit':0,
                                    'credit':res2['diff'],
                                   }))
                    
                value_s2={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': line.post_date,#time.strftime('%Y-%m-%d'),
                    'line_id': journal_s2_line,
                    'doc_type':'staff_payroll'
                    }
                context.update({'get_tpt_payroll': 'staff'})
                if context.get('tpt_review_posting',False) and context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'staff':
                    return value_s2
                if context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'posting':
                    new_s2_jour_id = account_move_obj.create(cr,uid,value_s2)
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id.payroll:
                            try:
                                account_move_obj.button_validate(cr,uid, [new_s2_jour_id], context)
                            except:
                                pass
                    payroll_obj.write(cr, uid, staff.id, {'state':'approve'})
            if payroll_workers_id:
                workers = payroll_obj.browse(cr,uid,payroll_workers_id)
                sql = '''
                    select id
                    from account_period where EXTRACT(year from date_start)='%s' and EXTRACT(month from date_start)='%s'
                '''%(year,month)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                
                for period_id in period_obj.browse(cr,uid,period_ids):
                    res3 = {}
                    journal_s3_line = []
                    res3 = self.get_account_amount(cr,uid,payroll_workers_id)
                    if res3['gross'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': wages_acc,
                                    'debit':res3['gross'],
                                    'credit':0,
                                   }))
                    if res3['shd'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': shd_acc,
                                    'debit':res3['shd'],
                                    'credit':0,
                                   }))
                    if res3['provident'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': provident_acc,
                                    'debit':0,
                                    'credit':res3['provident'],
                                   }))
                    if res3['vpf'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': vpf_acc,
                                    'debit':0,
                                    'credit':res3['vpf'],
                                   }))
                    if res3['esi'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': esi_acc,
                                    'debit':0,
                                    'credit':res3['esi'],
                                   }))
                    if res3['welfare'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': welfare_acc,
                                    'debit':0,
                                    'credit':res3['welfare'],
                                   }))
                    if res3['canteen'] > 0: #TPT-BM-ON 29/10/2015
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': canteen_acc,
                                    'debit':0,
                                    'credit':res3['canteen'],
                                   }))
                    if res3['lic_premium'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lic_premium_acc,
                                    'debit':0,
                                    'credit':res3['lic_premium'],
                                   }))
                    if res3['tax'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': pro_tax_acc,
                                    'debit':0,
                                    'credit':res3['tax'],
                                   }))
                    if res3['lwf'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lwf_acc,
                                    'debit':0,
                                    'credit':res3['lwf'],
                                   }))
                    if res3['ins_oth'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': other_insu_acc,
                                    'debit':0,
                                    'credit':res3['ins_oth'],
                                   }))
                    if res3['vvt_loan'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': vvti_acc, 
                                    'debit':0,
                                    'credit':res3['vvt_loan'],
                                   }))
                    if res3['vvt_hdfc'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': hdfc_acc,
                                    'debit':0,
                                    'credit':res3['vvt_hdfc'],
                                   }))
                    if res3['hfl'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': lic_hfl_acc,
                                    'debit':0,
                                    'credit':res3['hfl'],
                                   }))
                    if res3['sbt'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': sbt_acc,
                                    'debit':0,
                                    'credit':res3['sbt'],
                                   }))
                    if res3['other'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': other_loan_acc,
                                    'debit':0,
                                    'credit':res3['other'],
                                   }))
                    if res3['tmb'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': tmb_acc,
                                    'debit':0,
                                    'credit':res3['tmb'],
                                   }))
                    if res3['it'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': it_acc,
                                    'debit':0,
                                    'credit':res3['it'],
                                   }))
                    if res3['diff'] > 0:
                        journal_s3_line.append((0,0,{
                                    'name':line.year, 
                                    'account_id': wages_payable_acc,
                                    'debit':0,
                                    'credit':res3['diff'],
                                   }))
                
                value_s3={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': line.post_date,#time.strftime('%Y-%m-%d'),
                    'line_id': journal_s3_line,
                    'doc_type':'worker_payroll'
                    }
                context.update({'get_tpt_payroll': 'worker'})
                if context.get('tpt_review_posting',False) and context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'worker':
                    return value_s3
                if context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'posting':
                    new_s3_jour_id = account_move_obj.create(cr,uid,value_s3)
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id.payroll:
                            try:
                                account_move_obj.button_validate(cr,uid, [new_s3_jour_id], context)
                            except:
                                pass
                    payroll_obj.write(cr, uid, workers.id, {'state':'approve'})
        return self.write(cr, uid, line.id, {'state':'done'})
    
#     def approve_payroll(self, cr, uid, ids, context=None):
#         for line in self.browse(cr,uid,ids):
#             account_move_obj = self.pool.get('account.move')
#             period_obj = self.pool.get('account.period')
#             payroll_obj = self.pool.get('arul.hr.payroll.executions')
#             payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state','=','confirm')])
#             configuration_obj = self.pool.get('tpt.posting.configuration')
#             configuration_ids = configuration_obj.search(cr, uid, [('name', '=','payroll')])
#             gross = 0.0
#             year = str(line.year)
#             month = str(line.month)
#                
#             for payroll in payroll_obj.browse(cr,uid,payroll_ids):
#                 sql = '''
#                     select id
#                     from account_period where EXTRACT(year from date_start)='%s' and EXTRACT(month from date_start)='%s'
#                 '''%(year,month)
#                 cr.execute(sql)
#                 period_ids = [r[0] for r in cr.fetchall()]
#                 if not period_ids:
#                     raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
#                 for period_id in period_obj.browse(cr,uid,period_ids):
#                     if payroll_ids:
#                         payroll_ids = str(payroll_ids).replace("[","(")
#                         payroll_ids = payroll_ids.replace("]",")")
#                         sql_journal = '''
#                         select id from account_journal
#                         '''
#                         cr.execute(sql_journal)
#                         journal_ids = [r[0] for r in cr.fetchall()]
#                         journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0]) 
#     
#                         sql_gross = '''
#                             select sum(float) as gross_salary from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='GROSS_SALARY')
#                             and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id in %s)
#                         '''%(payroll_ids)
#                         cr.execute(sql_gross)
#                         gross = cr.dictfetchone()['gross_salary']
#                         sql_provident = '''
#                             select sum(float) as provident from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='PF.D')
#                             and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id in %s)
#                         '''%(payroll_ids)
#                         cr.execute(sql_provident)
#                         provident = cr.dictfetchone()['provident']
#                         sql_vpf = '''
#                             select sum(float) as vpf from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='VPF.D')
#                             and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id in %s)
#                         '''%(payroll_ids)
#                         cr.execute(sql_vpf)
#                         vpf = cr.dictfetchone()['vpf']
#                         sql_tax = '''
#                             select sum(float) as tax from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='PT')
#                             and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id in %s)
#                         '''%(payroll_ids)
#                         cr.execute(sql_tax)
#                         tax = cr.dictfetchone()['tax']
#                         sql_lwf = '''
#                             select sum(float) as tax from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_deduction_parameters where code='LWF')
#                             and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id in %s)
#                         '''%(payroll_ids)
#                         cr.execute(sql_lwf)
#                         lwf = cr.dictfetchone()['tax']
#                         welfare = 0.0
#                         lic_premium = 0.0
#                         staff_adv = 0.0
#                         sum_credit = (provident+vpf+tax+lwf+welfare+lic_premium+staff_adv)
#                         diff = gross - sum_credit
#                         for configuration in configuration_obj.browse(cr,uid,configuration_ids):
#                             gross_acc = configuration.salari_id.id
#                             provident_acc = configuration.pfp_id.id
#                             vpf_acc = configuration.vpf_id.id
#                             welfare_acc = configuration.staff_welfare_id.id
#                             lic_premium_acc = configuration.lic_id.id
#                             pro_tax_acc = configuration.profes_tax_id.id
#                             lwf_acc = configuration.lwf_id.id
#                             staff_adv_acc = configuration.staff_advance_id.id
#                             salari_acc = configuration.salari_payable_id.id
#                             if not gross_acc:
#                                 raise osv.except_osv(_('Warning!'),_('Gross Salary is not null, please configure it in GL Posting Configuration master !'))
#                             journal_line = [(0,0,{
#                                             'name':line.year, 
#                                             'account_id': gross_acc,
#                                             'debit':gross,
#                                             'credit':0,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': provident_acc,
#                                             'debit':0,
#                                             'credit':provident,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': vpf_acc,
#                                             'debit':0,
#                                             'credit':vpf,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': welfare_acc,
#                                             'debit':0,
#                                             'credit':0,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': lic_premium_acc,
#                                             'debit':0,
#                                             'credit':0,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': pro_tax_acc,
#                                             'debit':0,
#                                             'credit':tax,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': lwf_acc,
#                                             'debit':0,
#                                             'credit':lwf,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': staff_adv_acc,
#                                             'debit':0,
#                                             'credit':0,
#                                            }),(0,0,{
#                                             'name':line.year, 
#                                             'account_id': salari_acc,
#                                             'debit':0,
#                                             'credit':diff,
#                                            }),]
#     #                     for p in line.move_lines:
#     #                         amount_cer = p.purchase_line_id.price_unit * p.product_qty
#     #                         credit += amount_cer - amount_cer*p.purchase_line_id.discount
#     #                         journal_line.append((0,0,{
#     #                             'name':line.name, 
#     #                             'account_id': p.product_id.purchase_acc_id and p.product_id.purchase_acc_id.id,
#     #                             'partner_id': line.partner_id and line.partner_id.id,
#     #                             'credit':credit,
#     #                             'debit':0,
#     #                         }))
#                              
#                         value={
#                             'journal_id':journal.id,
#                             'period_id':period_id.id ,
#                             'date': time.strftime('%Y-%m-%d'),
#                             'line_id': journal_line,
#                             'doc_type':'payroll'
#                             }
#                         new_jour_id = account_move_obj.create(cr,uid,value)
#                 payroll_obj.write(cr, uid, payroll.id, {'state':'approve'})
#         return self.write(cr, uid, line.id, {'state':'done'})
tpt_hr_payroll_approve_reject()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
                'produce_cost': fields.float('Produce Cost'),
                }
    def write(self, cr, uid, ids, vals, context=None): # Ref tpt_maintenace.py - bt_approve method
        new_write = super(mrp_production, self).write(cr, uid,ids, vals, context)
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        stock_move_obj = self.pool.get('stock.move')
        journal_line = []
        credit = 0
        price = 0
        debit = 0
        for line in self.browse(cr,uid,ids):
            sql = '''
                    select id from account_journal where name = 'Stock Journal'
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            date_period = line.date_planned
            sql = '''
                select id from account_period where '%s' between date_start and date_stop and special is False
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
# neu co them freight vao trong report thi phai xac dinh lai price unit cho data moi = cach cong them value cua freight vao total_cost_in  
            move_date_ids = stock_move_obj.search(cr, uid, [('production_id','=',line.id)])
            if move_date_ids:
                stock_move_obj.write(cr, 1, move_date_ids,{'date':line.date_planned})
            sql='''
                select move_id from mrp_production_move_ids where production_id = %s
            '''%(line.id)
            cr.execute(sql)
            move_material_ids = [row[0] for row in cr.fetchall()]
            if move_material_ids:
                stock_move_obj.write(cr, 1, move_material_ids,{'date':line.date_planned})
            if 'state' in vals and line.state=='done':
                for p in line.move_created_ids2:
                    prod_ware = self.pool.get('product.product').browse(cr, uid, p.product_id.id)
                    if not prod_ware.prod_dest_id:
                        raise osv.except_osv(_('Warning'), _('Production Destination Location is not null, please configure it in Product Master of %s !'%prod_ware.default_code))
                    else:
                        stock_move_obj.write(cr, 1, [p.id],{'location_dest_id':prod_ware.prod_dest_id.id})
#                             sql = '''
#                                 update stock_move set location_dest_id = %s where id = %s
#                             '''%(prod_ware.prod_dest_id.id,p.id)
#                             cr.execute(sql)
                for mat in line.move_lines2:
                    categ = mat.product_id.categ_id.cate_name
                    if categ=='finish':
                        sql = '''
                            select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
                            case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
                                and location_dest_id != location_id
                                and  (action_taken = 'direct'
                                or (inspec_id is not null and location_dest_id = %s)
                                or (production_id is not null and location_dest_id = %s)
                                or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
                        )
                        '''%(mat.product_id.id,line.date_planned,line.location_src_id.id,line.location_src_id.id)
                        cr.execute(sql)
                        inventory = cr.dictfetchone()
                        if inventory:
                            hand_quantity_in = inventory['ton_sl'] or 0
                            total_cost_in = inventory['total_cost'] or 0
                        sql = '''
                            select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
                            case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
                                and location_dest_id != location_id
                                and  (issue_id is not null
                                or (location_id = %s and id in (select move_id from mrp_production_move_ids))
                        )
                        '''%(mat.product_id.id,line.date_planned, line.location_src_id.id)
                        cr.execute(sql)
                        inventory = cr.dictfetchone()
                        if inventory:
                            hand_quantity_out = inventory['ton_sl'] or 0
                            hand_quantity_out = hand_quantity_out - mat.product_qty
                            total_cost_out = inventory['total_cost'] or 0
                        price_unit = (hand_quantity_in-hand_quantity_out) and (total_cost_in-total_cost_out)/(hand_quantity_in-hand_quantity_out)
                        if price_unit<0:
                            price_unit = 0
                        stock_move_obj.write(cr, 1, [mat.id],{'price_unit':price_unit})
                        cost = price_unit*mat.product_qty or 0
                        debit += round(cost,2)
                        if cost:
                            if mat.product_id.default_code not in ['M0501010005','M0501010004','M0501010002']:
                                if line.product_id.product_credit_id:
                                    journal_line.append((0,0,{
                                                    'name':mat.product_id.default_code, 
                                                    'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                    'debit':0,
                                                    'credit':round(cost,2),
                                                   }))
                                else:
                                    raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                            else:
                                if mat.product_id.product_asset_acc_id:
                                    journal_line.append((0,0,{
                                                    'name':mat.product_id.default_code, 
                                                    'account_id': mat.product_id.product_asset_acc_id and mat.product_id.product_asset_acc_id.id,
                                                    'debit':0,
                                                    'credit':round(cost,2),
                                                   }))
                                else:
                                    raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
#                         avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mat.product_id.id),('warehouse_id','=',line.location_src_id.id)])
#                         if avg_cost_ids:
#                             avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
#                             unit = avg_cost_id.avg_cost
#                             cost = unit * mat.product_qty
#                             price += cost
#                             if cost:
#                                 if mat.product_id.purchase_acc_id:
#                                     journal_line.append((0,0,{
#                                                     'name':mat.product_id.code, 
#                                                     'account_id': mat.product_id.purchase_acc_id and mat.product_id.purchase_acc_id.id,
#                                                     'debit':cost,
#                                                     'credit':0,
#                                                    }))
#                                 else:
#                                     raise osv.except_osv(_('Warning!'),_("Purchase GL Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.code))
                    
                    if categ=='raw':
                        parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                        if mat.product_id.default_code == 'M0501060001':
                  # Commented by P.VINOTHKUMAR ON 16/11/2017 for fixing coal and coal fines average cost issue
#                           if locat_ids[0] == line.location_src_id.id:
#                                 sql = '''
#                                     select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
#                                     case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                                     from stock_move st
#                                     where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
#                                         and location_dest_id != location_id
#                                         and  (action_taken = 'direct'
#                                         or (inspec_id is not null and location_dest_id = %s)
#                                         or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
#                                 )
#                                 '''%(mat.product_id.id,line.date_planned, locat_ids[0])
#                                 cr.execute(sql)
#                                 inventory = cr.dictfetchone()
#                                 if inventory:
#                                     hand_quantity_in = inventory['ton_sl'] or 0
#                                     total_cost_in = inventory['total_cost'] or 0
#                                     
#                                 sql = '''
#                                     select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
#                                     case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                                     from stock_move st
#                                     where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
#                                         and location_dest_id != location_id
#                                         and  (issue_id is not null
#                                         or (location_id = %s and id in (select move_id from mrp_production_move_ids))
#                                 )
#                                 '''%(mat.product_id.id,line.date_planned, locat_ids[0])
#                                 cr.execute(sql)
#                                 inventory = cr.dictfetchone()
#                                 if inventory:
#                                     hand_quantity_out = inventory['ton_sl'] or 0
#                                     hand_quantity_out = hand_quantity_out - mat.product_qty
#                                     total_cost_out = inventory['total_cost'] or 0
#                                 price_unit = (hand_quantity_in-hand_quantity_out) and (total_cost_in-total_cost_out)/(hand_quantity_in-hand_quantity_out)
#                                 sql = '''
#                                     update stock_move set price_unit = %s where id = %s
#                                 '''%(price_unit, mat.id)
#                                 cr.execute(sql)
#                                 cost = price_unit*mat.product_qty or 0
                               # Commented TPT end
                               # Added by P.VINOTHKUMAR ON 16/11/2017 FOR fixing Average cost issue in production  for coal and coal fines product
                                warehouse_id = line.location_src_id.id
                                destination_id = line.location_dest_id.id
                                avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mat.product_id.id),('warehouse_id','=',warehouse_id)]) 
                                if avg_cost_ids:
                                    avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                                    unit = avg_cost_id.avg_cost or 0
                                    # Added the following logic by P.VINOTHKUMAR AND BM on 09/11/2017 for fixing average cost and total issues
                                    issue_value = unit * mat.product_qty
                                    runtime_total_cost = avg_cost_id.total_cost - issue_value
                                    runtime_qty = avg_cost_id.hand_quantity - mat.product_qty
                                    vals = {'total_cost' : runtime_total_cost, 
                                            'hand_quantity': runtime_qty}
                                    avg_cost_obj.write(cr, uid, avg_cost_id.id, vals)
                                       
                                cost = issue_value
                                
                                if destination_id:
                                    avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',p.product_id.id),('warehouse_id','=',destination_id)])
                                    if avg_cost_ids:
                                       avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                                       unit1 = unit or 0
                                       issue_value = (avg_cost_id.total_cost) + (unit1 * mat.product_qty)
                                       issue_qty = avg_cost_id.hand_quantity + mat.product_qty
                                       avg_cost = issue_value/issue_qty
                                       vals = {'total_cost' : issue_value, 
                                               'hand_quantity':  issue_qty,
                                               'avg_cost': avg_cost
                                               }
                                       avg_cost_obj.write(cr, uid, avg_cost_id.id, vals)
               # TPT end by P.VINOTHKUMAR ON 16/11/2017  FOR fixing Average cost issue in production  for coal and coal fines
                                debit += round(cost,2)
                                if cost:
                                    if line.product_id.product_credit_id:
                                        journal_line.append((0,0,{
                                                        'name':mat.product_id.code, 
                                                        'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                        'debit':0,
                                                        'credit':round(cost,2),
                                                       }))
                                    else:
                                        raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                              # Commented by P.VINOTHKUMAR ON 16/11/2017 for fixing coal and coal fines average cost issue      
#                             else:
#                                 avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mat.product_id.id),('warehouse_id','=',line.location_src_id.id)])
#                                 if avg_cost_ids:
#                                     avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
#                                     unit = avg_cost_id.avg_cost
#                                     cost = unit * mat.product_qty
#                                     debit += round(cost,2)
#                                     if cost:
#                                         if line.product_id.product_credit_id:
#                                             journal_line.append((0,0,{
#                                                             'name':mat.product_id.code, 
#                                                             'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
#                                                             'debit':0,
#                                                             'credit':round(cost,2),
#                                                            }))
#                                         else:
#                                             raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                            # Commented TPT end
                        else:
#                             stock_move_obj.search(cr, uid, [('date','=',line.date_planned),('product_id','=',mat.product_id.id),('issue_id','!=',False)])
                            sql='''
                                select price_unit from stock_move where date<='%s' and product_id=%s 
                                    and issue_id in (select id from tpt_material_issue where request_type='production')
                                    order by date desc 
                            '''%(line.date_planned,mat.product_id.id)
                            cr.execute(sql)
                            #move_ids = cr.fetchone()
                            move_ids = cr.dictfetchone()
                            if move_ids:
                                #move_ids = move_ids[0] prev
                                move_ids = move_ids['price_unit']
                                stock_move_obj.write(cr, 1, [mat.id],{'price_unit':move_ids})
                                price_raw = move_ids * (mat.product_qty or 0)
                                debit += round(price_raw,2)
                                if line.product_id.product_credit_id:
                                    journal_line.append((0,0,{
                                                        'name':mat.product_id.code, 
                                                        'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                        'debit':0,
                                                        'credit':round(price_raw,2),
                                                               }))
                                else:
                                    raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured! Please configured it!"))
                            else:
                                raise osv.except_osv(_('Warning!'),_("Do not have material issue for this Production Declaration! Please check it!"))
                
                for produce in line.move_created_ids2:
                    if produce.product_id.id != line.product_id.id: 
                        sql = '''
                            select price_unit from mrp_subproduct where bom_id=%s and product_id=%s
                        '''%(line.bom_id.id,produce.product_id.id)
                        cr.execute(sql)
                        price_ids = cr.fetchone()
                        produce_price = (price_ids and price_ids[0] or 0) * (produce.product_qty or 0)
                        debit -= round(produce_price,2)
                        if line.product_id.product_asset_acc_id:
                            journal_line.append((0,0,{
                                                    'name':produce.product_id.default_code, 
                                                    'account_id': produce.product_id.product_asset_acc_id and produce.product_id.product_asset_acc_id.id,
                                                    'debit':round(produce_price,2),
                                                    'credit':0,
                                                   }))
                        else:
                            raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(produce.product_id.default_code))
#                 for act in line.bom_id.activities_line:
                for act in line.activities_line:
                    if line.product_id.product_credit_id:
#                         credit += act.product_cost
                        debit += act.product_cost and round(act.product_cost,2) or 0
                        journal_line.append((0,0,{
                                                'name':act.activities_id.code, 
                                                'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                'debit':0,
                                                'credit':act.product_cost and round(act.product_cost,2) or 0,
                                               }))
                    else:
                        raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured! Please configured it!"))
#                         raise osv.except_osv(_('Warning!'),_("Activity Account is not configured for Activity '%s'! Please configured it!")%(act.activities_id.code))
#                 credit += price
                if debit:
                    if line.product_id.product_asset_acc_id:
                        journal_line.append((0,0,{
                                                'name':line.product_id.code, 
                                                'account_id': line.product_id.product_asset_acc_id and line.product_id.product_asset_acc_id.id,
                                                'debit': round(debit,2),
                                                'credit':0,
                                               }))
                    else:
                        raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(line.product_id.default_code))
                    unit_produce = debit/line.product_qty
                    move_ids = stock_move_obj.search(cr, uid, [('product_id','=',line.product_id.id),('production_id','=',line.id)])
                    if move_ids:
                        stock_move_obj.write(cr, 1, move_ids,{'price_unit':unit_produce})
                ##
                #TPT START - By P.VINOTHKUMAR - ON 15/04/2016 - FOR (Generate document sequence for Production Account postings)
                vals={}
                sql = '''
                   select code from account_fiscalyear where '%s' between date_start and date_stop
                '''%(time.strftime('%Y-%m-%d'))
                cr.execute(sql)
                fiscalyear = cr.dictfetchone()
                if not fiscalyear:
                     raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
                else:
                     sequence = self.pool.get('ir.sequence').get(cr, uid, 'account.production')
                vals['name'] = sequence and sequence+'/'+fiscalyear['code'] or '/'
                Production_account=vals['name']   
                sql = '''
                   update mrp_production set produce_cost = %s where id=%s 
               '''%(credit,line.id)
                cr.execute(sql)  
                ## TPT-END     
                #print journal_line
                value={
                            'journal_id':journal_ids[0],
                            'period_id':period_ids[0] ,
                            'doc_type':'product',
                            'date': line.date_planned,
                            'line_id': journal_line,
                            'product_dec': line.id,
                            'ref': line.name,
                            'name':Production_account,
                        }
                new_jour_id = account_move_obj.create(cr,uid,value)
                auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                if auto_ids:
                    auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                    if auto_id.production_declaration:
                        try:
                            account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                        except:
                            pass
                sql = '''
                    update mrp_production set produce_cost = %s where id=%s 
                '''%(credit,line.id)
                cr.execute(sql)
                
        return new_write
mrp_production()

class account_move(osv.osv):
    _inherit = 'account.move'
    _columns = {
           'doc_type': fields.selection([('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv_po', 'Supplier Invoice(With PO)'),('sup_inv', 'Supplier Invoice(Without PO)'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Executives Payroll'),
                                  ('grn', 'GRN'),
                                  ('good', 'Good Issue'),
                                  ('do', 'DO'),
                                  ('inventory', 'Inventory Transfer'),
                                  ('manual', 'Manual Journal'),
                                  ('cash_pay', 'Cash Payment'),
                                  ('cash_rec', 'Cash Receipt'),
                                  ('bank_pay', 'Bank Payment'),
                                  ('bank_rec', 'Bank Receipt'),
                                  ('ser_inv', 'Service Invoice'),
                                  ('product', 'Production'),
                                  ('staff_payroll', 'Staff Payroll'),
                                  ('freight', 'Freight Invoice'),
                                  ('worker_payroll', 'Workers Payroll'),
                                  ('stock_adj_inc', 'Stock Adjustment Increase'),
                                  ('stock_adj_dec', 'Stock Adjustment Decrease'),
                                  ('return_do', 'Return DO'), #TPT-BM-01/07/2016
                                  ('asset_dp', 'Asset Depreciation'),#TPT-BM- ON13/08/2016
                                  ('material_return_request', 'Material Return Request'),
                                  ],
                                        'Document Type'),  
        'material_issue_id': fields.many2one('tpt.material.issue','Material Issue',ondelete='restrict'), 
        'ed_invoice_id': fields.many2one('tpt.ed.invoice.positing','ED Invoice Posting',ondelete='restrict'),  
        'grn_id': fields.many2one('stock.picking','GRN',ondelete='restrict'),
        'do_id': fields.many2one('stock.picking','DO',ondelete='restrict'), #TPT-BalamuruganPurushothaman
        'product_dec': fields.many2one('mrp.production','Production',ondelete='restrict'), 
        'state': fields.selection([('draft','Draft'),('posted','Posted'),
                                    ('cancel','Cancelled')
                                   ],
                                  'Status' ),
        'cost_center_id':fields.many2one('tpt.cost.center','Cost Center'),
                }
    
    def onchange_tpt_date(self, cr, uid, ids, date=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if date and date > current:
            vals = {'date':current}
            warning = {
                'title': _('Warning!'),
                'message': _('Date: Not allow future date!')
            }
        return {'value':vals,'warning':warning}
    
    def create(self, cr, uid, vals, context=None):
        return super(account_move, self).create(cr,1, vals, context)
    
    def write(self, cr, uid,ids, vals, context=None):
        return super(account_move, self).write(cr,1,ids,vals,context) 
    
account_move()

class tpt_activities(osv.osv):
    _inherit = 'tpt.activities'
    _columns = {
                'act_acc_id': fields.many2one('account.account', 'Activity Account'),
                }
tpt_activities()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'cate_name':fields.selection([('raw','Raw Materials'),('finish','Finished Product'),('spares','Spares'),('consum','Consumables'),('assets','Assets'),('service','Services')], 'Category Name', required = True),
        }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['cate_name'], context)
 
        for record in reads:
            cate_name = record['cate_name']
            name = ''
            if cate_name == 'raw':
                name = 'Raw Materials'
            if cate_name == 'finish':
                name = 'Finished Product'
            if cate_name == 'spares':
                name = 'Spares'
            if cate_name == 'consum':
                name = 'Consumables'
            if cate_name == 'assets':
                name = 'Assets'
            if cate_name == 'service':
                name = 'Service'
            res.append((record['id'], name))
        return res
product_category()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'Partner'
    #TPT By BalamuruganPurushothaman - Incident No: 2991 - ON 14/10/2015 
    # Credit Used fields should take effective in the following entries: Cash, Bank, Journal Entries, Customer Invoice Posting, Customer Payment etc
    def _tpt_credit_debit_get(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = {
                'tpt_credit': 0.0,
            }
            credit = 0
            sql  = '''
                select SUM(debit-credit) from account_move_line where 
                account_id=(select id from account_account where code = '0000'||'%s')
            '''%(partner.customer_code)
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
                credit = credit[0]
            res[partner.id]['tpt_credit'] = credit    
        return res
    def _asset_difference_search(self, cr, uid, obj, name, type, args, context=None):
        if not args:
            return []
        having_values = tuple(map(itemgetter(2), args))
        where = ' AND '.join(
            map(lambda x: '(SUM(bal2) %(operator)s %%s)' % {
                                'operator':x[1]},args))
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
        cr.execute(('SELECT pid AS partner_id, SUM(bal2) FROM ' \
                    '(SELECT CASE WHEN bal IS NOT NULL THEN bal ' \
                    'ELSE 0.0 END AS bal2, p.id as pid FROM ' \
                    '(SELECT (debit-credit) AS bal, partner_id ' \
                    'FROM account_move_line l ' \
                    'WHERE account_id IN ' \
                            '(SELECT id FROM account_account '\
                            'WHERE type=%s AND active) ' \
                    'AND reconcile_id IS NULL ' \
                    'AND '+query+') AS l ' \
                    'RIGHT JOIN res_partner p ' \
                    'ON p.id = partner_id ) AS pl ' \
                    'GROUP BY pid HAVING ' + where), 
                    (type,) + having_values)
        res = cr.fetchall()
        if not res:
            return [('id','=','0')]
        return [('id','in',map(itemgetter(0), res))]
    #TPT-END
    def _tpt_credit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'receivable', args, context=context)
    _columns = {
        'tpt_credit': fields.function(_tpt_credit_debit_get, #TPT
            string='Credit Used.', multi='sums'),
        'property_account_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Payable",
            view_load=True,
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=False),
        'property_account_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Receivable",
            view_load=True,
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=False),
        'is_tds_applicable': fields.boolean('IsTDSApplicable'),
        'section': fields.char('With Holding Tax', ),
        'tds_id': fields.many2one('account.tax', 'TDS %'),
        'vendor_type': fields.selection([('manu', 'Manufacturer'),('trade', 'Traders'),('first_stage', 'First Stage'),('Import', 'import')],'Vendor Type'),
        }
    _defaults = {
        'vendor_code':'/',
    }
    
#     def _check_vendor_code(self, cr, uid, ids, context=None):
#         for vendor in self.browse(cr, uid, ids, context=context):
#             if vendor.vendor_code:
#                 vendor_ids = self.search(cr, uid, [('id','!=',vendor.id),('vendor_code','=',vendor.vendor_code)])
#                 if vendor_ids:  
#                     raise osv.except_osv(_('Warning!'),_('The Vendor Code must be unique!'))
#                     return False
#         return True
#     _constraints = [
#         (_check_vendor_code, 'Identical Data', []),
#     ]
    
    def create(self, cr, uid, vals, context=None):
        if 'customer' in vals and vals['customer']:
            acc_obj = self.pool.get('account.account')
            acc_type_ids = self.pool.get('account.account.type').search(cr,uid, [('code','=','receivable')])
            if 'customer_account_group_id' in vals and vals['customer_account_group_id']:
                group = self.pool.get('customer.account.group').browse(cr,uid,vals['customer_account_group_id'])
                if 'VVTI Sold to Party' in group.name:
                    vals['customer_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.sold.group.customer') or '/'
                    if 'arulmani_type' in vals and vals['arulmani_type']=='export':
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119002')])
                    if 'arulmani_type' in vals and vals['arulmani_type']=='domestic':
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119001')])
                    if 'arulmani_type' in vals and vals['arulmani_type']=='indirect_export':
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119003')])
                    if acc_parent_ids:
                        acc_id = acc_obj.create(cr,uid,{
                            'code':'0000' + vals['customer_code'],
                            'name': vals['name'],
                            'type':'receivable',
                            'user_type':acc_type_ids[0],
                            'parent_id':acc_parent_ids[0],
                                                        })
                        vals.update({'property_account_receivable':acc_id})
                    else:
                        raise osv.except_osv(_('Warning!'),_('GL account 0000119002, 0000119001 or 0000119003 does not exist in the system. Please check it!'))
                elif 'VVTI Ship to Party' in group.name:
                    vals['customer_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.ship.group.customer') or '/'
                elif 'VVTI Indent Comm.' in group.name:
                    vals['customer_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.indent.group.customer') or '/'
                else:
                    raise osv.except_osv(_('Warning!'),_('You only create Customer Code for (VVTI Sold to Party, VVTI Ship to Party, VVTI Indent Comm.) in Customer Account Group'))
#             if 'arulmani_type' in vals and vals['arulmani_type']=='export':
#                 acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119002')])
#             if 'arulmani_type' in vals and vals['arulmani_type']=='domestic':
#                 acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119001')])
#             if 'arulmani_type' in vals and vals['arulmani_type']=='indirect_export':
#                 acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119003')])
#             acc_id = acc_obj.create(cr,uid,{
#                 'code':'0000' + vals['customer_code'],
#                 'name': vals['name'],
#                 'type':'receivable',
#                 'user_type':acc_type_ids[0],
#                 'parent_id':acc_parent_ids[0],
#                                             })
#             vals.update({'property_account_receivable':acc_id})
        if 'supplier' in vals and vals['supplier']:
            acc_obj = self.pool.get('account.account')
            acc_parent_ids = []
            acc_type_ids = self.pool.get('account.account.type').search(cr,uid, [('code','=','payable')])
            # Added by P.vinothkumar on 17/10/2016 for validate pan and tin no must be 10 digits
            if 'pan_tin' in vals:
                pan = vals['pan_tin'].replace(" ", "")
                if pan == '':
                    raise osv.except_osv(_('Warning!'),_('Please Provide the pan number!'))
                if len(pan) < 10:
                    raise osv.except_osv(_('Warning!'),_('Please enter 10 digits PAN'))
            if 'tin' in vals:
                tin = vals['tin'].replace(" ", "")
                if tin == '':
                    raise osv.except_osv(_('Warning!'),_('Please Provide the tin number!'))
                if len(tin) < 11:
                    raise osv.except_osv(_('Warning!'),_('Please enter 10 digits TIN'))
            if 'vendor_group_id' in vals and vals['vendor_group_id']:
                group = self.pool.get('tpt.vendor.group').browse(cr,uid,vals['vendor_group_id'])
                if 'Domestic' in group.name:
                    if vals.get('vendor_code','/')=='/':
                        vals['vendor_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.domestic.vendor') or '/'
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000215201')])
                        if not acc_parent_ids:
                            raise osv.except_osv(_('Warning!'),_('Please create GL Account for code is "0000215201" and name is "SUNDRY CREDITORS – DOMESTIC"!!'))
                elif 'Spares' in group.name:
                    if vals.get('vendor_code','/')=='/':
                        vals['vendor_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.spares.vendor') or '/'
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000215204')])
                        if not acc_parent_ids:
                            raise osv.except_osv(_('Warning!'),_('Please create GL Account for code is "0000215204" and name is "SUNDRY CREDITORS - SPARES SUPPLIERS"!!'))
                elif 'Service Providers' in group.name:
                    if vals.get('vendor_code','/')=='/':
                        vals['vendor_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.service.providers.vendor') or '/'
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000215203')])
                        if not acc_parent_ids:
                            raise osv.except_osv(_('Warning!'),_('Please create GL Account for code is "0000215203" and name is "SUNDRY CREDITORS - SERVICE PROVIDERS"!!'))
                elif 'Transporters and C & F' in group.name:
                    if vals.get('vendor_code','/')=='/':
                        vals['vendor_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.transporters.vendor') or '/'
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000215200')])
                        if not acc_parent_ids:
                            raise osv.except_osv(_('Warning!'),_('Please create GL Account for code is "0000215200" and name is "SUNDRY CREDITORS - TRANSPORTES AND C&F"!!'))
                elif 'Foreign' in group.name:
                    if vals.get('vendor_code','/')=='/':
                        vals['vendor_code'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.foreign.vendor') or '/'
                        acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000215202')])
                        if not acc_parent_ids:
                            raise osv.except_osv(_('Warning!'),_('Please create GL Account for code is "0000215202" and name is "SUNDRY CREDITORS - FOREIGN"!!'))
                else:
                    raise osv.except_osv(_('Warning!'),_('Can not create Vendor Code for this Vendor Class'))
            if acc_parent_ids:
                acc_id = acc_obj.create(cr,uid,{
                    'code':vals['vendor_code'],
                    'name': vals['name'],
                    'type':'payable',
                    'reconcile': True,
                    'user_type':acc_type_ids[0],
                    'parent_id':acc_parent_ids[0],
                                                })
                vals.update({'property_account_payable':acc_id})
        return super(res_partner, self).create(cr, uid, vals, context)
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_partner_with_name', False):
            name = context.get('name')
            partner_ids = self.search(cr, uid, [('name','ilike',name)])
            args += [('id','in',partner_ids)]
        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_partner_with_name':1,'name':name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
res_partner()

class account_tax(osv.osv):
    _inherit = 'account.tax'
    
    _columns = {
        'gl_account_id': fields.many2one('account.account', 'GL Account'),
        'section': fields.char('Section', size = 20),
        'is_stax_report':fields.boolean('Is STax Report Applicable'), #TPT-Y on 16/10/2015
        'is_swachh_bharat':fields.boolean('Is Swachh Bharat Cess Applicable'), #TPT-BM on 12/01/2016 - SWACHH BHARAT CESS
        #'is_krishi_kalyan':fields.boolean('Is Krishi Kalyan Cess Applicable'), #TPT-BM on 01/06/2016 - KRISHI KALYAN CESS
        'is_vat_report':fields.boolean('Is VAT Report Applicable'), #TPT vinoth on 18/01/2016 
        }
    _default = {
       'is_stax_report':False,
       'is_swachh_bharat':False,
       'is_krishi_kalyan':False,
       'is_vat_report':False,
       'is_cst_report':False
    }
    
account_tax()

class res_currency(osv.osv):
    _inherit = 'res.currency'
    
    def _current_rate(self, cr, uid, ids, name, arg, context=None):
        return self._current_rate_computation(cr, uid, ids, name, arg, True, context=context)

    def _current_rate_silent(self, cr, uid, ids, name, arg, context=None):
        return self._current_rate_computation(cr, uid, ids, name, arg, False, context=context)

    def _current_rate_computation(self, cr, uid, ids, name, arg, raise_on_no_rate, context=None):
        if context is None:
            context = {}
        res = {}
        if 'date' in context:
            date = context['date']
        else:
            date = time.strftime('%Y-%m-%d')
        date = date or time.strftime('%Y-%m-%d')
        # Convert False values to None ...
        currency_rate_type = context.get('currency_rate_type_id') or None
        # ... and use 'is NULL' instead of '= some-id'.
        operator = '=' if currency_rate_type else 'is'
        for id in ids:
            cr.execute("SELECT currency_id, rate FROM res_currency_rate WHERE currency_id = %s AND name <= %s AND currency_rate_type_id " + operator +" %s ORDER BY name desc LIMIT 1" ,(id, date, currency_rate_type))
            if cr.rowcount:
                id, rate = cr.fetchall()[0]
                res[id] = rate
            elif not raise_on_no_rate:
                res[id] = 0
            else:
                p =self.browse(cr,uid,id)
                raise osv.except_osv(_('Error!'),_("No currency rate associated for currency %s for the given period" % (p.name)))
        return res

    _columns = {
        'rate': fields.function(_current_rate, string='Current Rate', digits=(12,14),
            help='The rate of the currency to the currency of rate 1.'),
        'rate_silent': fields.function(_current_rate_silent, string='Current Rate', digits=(12,14),
            help='The rate of the currency to the currency of rate 1 (0 if no rate defined).'),
        'rounding': fields.float('Rounding Factor', digits=(12,14)),
        }
    
res_currency()

class res_currency_rate(osv.osv):
    _inherit = 'res.currency.rate'
    _columns = {
        'rate': fields.float('Rate', digits=(12,14), help='The rate of the currency to the currency of rate 1'),
        'rate_type': fields.selection([('buying','Buying Rate'),('selling','Selling Rate')],'Rate Type'),#TPT-BM
    }
    
res_currency_rate()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the last pending upstream move
                other_upstream_move_ids = self.search(cr, uid, [('id','not in',move_ids),('state','not in',['done','cancel']),
                                            ('move_dest_id','=',move.move_dest_id.id)], context=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed','done','assigned'):
                todo.append(move.id)
            if move.picking_id:
                self.write(cr, uid, move_ids, {'state': 'done', 'date': move.picking_id.date}, context=context)
            elif move.inspec_id:
                self.write(cr, uid, move_ids, {'state': 'done', 'date': move.inspec_id.date}, context=context)
            else:
                self.write(cr, uid, move_ids, {'state': 'done', 'date': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}, context=context)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)

        for id in move_ids:
             wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True
    _columns = {
        'stock_adj_id': fields.many2one('stock.adjustment', 'Stock Adjustment', ondelete='restrict'),
                }
stock_move()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def write(self, cr, uid,ids, vals, context=None):
        return super(purchase_order, self).write(cr,1,ids,vals,context)
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_po_multi_grn', False):
            sql = '''
                select purchase_id
                
                from stock_picking 
                
                where state='done' and invoice_state='2binvoiced' and purchase_id is not null
                
                and warehouse not in (select id from stock_location where name ='Block List')
                
                and purchase_id not in (select purchase_id from stock_picking sp left join tpt_quanlity_inspection qi on sp.id=qi.name where qi.state!='done')
                
                group by purchase_id
            '''
            cr.execute(sql)
            po_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',po_ids)]
            
        return super(purchase_order, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_po_with_name':1,'name':name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
     
purchase_order()

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    def write(self, cr, uid,ids, vals, context=None):
        return super(stock_picking_out, self).write(cr,1,ids,vals,context) 
stock_picking_out()



class tpt_bank_reconciliation(osv.osv):
    _name = 'tpt.bank.reconciliation'
    _columns = {
        'name': fields.many2one('account.account', 'Bank GL Account', required=True, states={ 'done':[('readonly', True)]}),
        'date': fields.date('Payment Date', states={ 'done':[('readonly', True)]}),
        'reconciliation_line': fields.one2many('tpt.bank.reconciliation.line', 'bank_reconciliation_id', 'Line', states={ 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
    }
    _defaults = {
        'state': 'draft',
    }

    def onchange_account(self, cr, uid, ids, account_id=False, date = False, context=None):
        if context is None:
            context={}
        vals = {}
        if ids:
            cr.execute(''' delete from tpt_bank_reconciliation_line where bank_reconciliation_id in %s ''',(tuple(ids),))
        if account_id:
            tt_debit = 0.0
            tt_credit = 0.0
            voucher_obj = self.pool.get('account.voucher')
            voucher_ids = voucher_obj.search(cr, uid, [('account_id','=',account_id),('reconciliation_date','=',False)])
            if date:
                voucher_ids = voucher_obj.search(cr, uid, [('account_id','=',account_id),('reconciliation_date','=',False), ('date','=',date)])
            reconciliation_line = []
            for voucher in voucher_obj.browse(cr, uid, voucher_ids):
                doc_type = ''
                debit = 0.0
                credit = 0.0
                
                if voucher.journal_id.type=='bank':
                    if not voucher.tpt_sup_reconcile and voucher.type == 'payment':
                        doc_type='Supplier Payments'
                    if not voucher.tpt_sup_reconcile and voucher.type == 'receipt':
                        doc_type='Customer Payments'
                    if voucher.type_trans:
                        doc_type='Bank Transaction'
                    for move_id in voucher.move_ids:
                        if move_id.account_id.id == account_id:
                            if move_id.debit:
                                debit = move_id.debit
                            if move_id.credit:
                                credit = move_id.credit
                
                tt_debit += debit
                tt_credit += credit
                reconciliation_line.append((0,0,{
                    'partner_id': voucher.partner_id and voucher.partner_id.id or False,
                    'name': voucher.name,
                    'doc_type': doc_type,
                    'reference': voucher.reference,
                    'date': voucher.date,
                    'cheque_no': voucher.cheque_no,
                    'cheque_date': voucher.cheque_date,
                    'account_id': voucher.account_id and voucher.account_id.id or False,
                    'amount': voucher.amount,
                    'debit': debit,
                    'credit': credit,
                    'voucher_id': voucher.id,
                }))
            reconciliation_line.append((0,0,{
                'cheque_no': 'Total',
                'debit': tt_debit,
                'credit': tt_credit,
            }))
            reconciliation_line.append((0,0,{
                'cheque_no': 'Net Balance',
                'debit': tt_debit-tt_credit,
            }))
            vals = {'reconciliation_line':reconciliation_line}
        return {'value': vals}

    def bt_confirm(self, cr, uid, ids, context=None):
        for bank_reconciliation in self.browse(cr, uid, ids):
            for line in bank_reconciliation.reconciliation_line:
                if line.reconciliation_date:
                    cr.execute(''' update account_voucher set reconciliation_date=%s where id=%s ''',(line.reconciliation_date,line.voucher_id.id,))
        return self.write(cr, uid, ids,{'state':'done'})
    
tpt_bank_reconciliation()

class tpt_bank_reconciliation_line(osv.osv):
    _name = 'tpt.bank.reconciliation.line'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer/Verdor'),
        'name': fields.char('Voucher No', size=1024),
        'doc_type': fields.char('Document Type', size=1024),
        'reference': fields.char('Payment Ref', size=1024),
        'date': fields.date('Payment Date'),
        'cheque_no': fields.char('Cheque No', size=1024),
        'cheque_date': fields.date('Cheque Date'),
        'reconciliation_date': fields.date('Reconciliation Date'),
        'account_id': fields.many2one('account.account', 'Bank GL Account'),
        'voucher_id': fields.many2one('account.voucher', 'Voucher'),
        'amount': fields.float('Payment Amount'),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
        'bank_reconciliation_id': fields.many2one('tpt.bank.reconciliation', 'Bank Reconciliation', ondelete='cascade'),
    }
    
tpt_bank_reconciliation_line()

class tpt_auto_posting(osv.osv):
    _name = "tpt.auto.posting"
    _columns = {
        'name':fields.char('Name', size = 1024),
        'grn':fields.boolean('GRN'),
        'supplier_invoice':fields.boolean('Supplier Invoice'),
        'material_issue':fields.boolean('Material Issue'),
        'delivery_order':fields.boolean('Delivery Order'),
        'customer_invoice':fields.boolean('Customer Invoice'),
        'supplier_payment':fields.boolean('Supplier Payment'),
        'customer_payment':fields.boolean('Customer payment'),
        'cash_transactions':fields.boolean('Cash Transactions'),
        'bank_transactions':fields.boolean('Bank Transactions'),
        'supplier_invoice_without':fields.boolean('Supplier Invoice (Without PO)'),
        'service_invoice':fields.boolean('Service Invoice'),
        'freight_invoice':fields.boolean('Freight Invoice'),
        'journal_vouchers':fields.boolean('Journal Vouchers'),
        'production_declaration':fields.boolean('Production Declaration'),
        'payroll':fields.boolean('Payroll'),
        'material_return_request':fields.boolean('Material Return Request'),
        'ed_posting':fields.boolean('ED Invoice Posting'),
    }
    _defaults = {
        'name':'Auto Account Posting Configuration',
    }
    def _check_name(self, cr, uid, ids, context=None):
        for auto in self.browse(cr, uid, ids, context=context):
            auto_ids = self.search(cr, uid, [('id','!=',auto.id),('name','=',auto.name)])
            if auto_ids:
                raise osv.except_osv(_('Warning!'),_('Can not have more than one Auto Account Posting Configuration!'))           
                return False
            return True
        
    _constraints = [
        (_check_name, 'Identical Data', ['name']),
    ] 
    
#     def split_auto_posting(self,cr,uid,stri):
#         move_obj = self.pool.get('account.move')
#         grn_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=',stri)])
#         if grn_ids:
#             try:
#                 move_obj.button_validate(cr, uid, grn_ids, context)
#             except:
#                 pass
#         return True
    
    def auto_posting(self, cr, uid, context=None):
#         auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid,[])
#         if auto_ids:
#             auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
#             move_obj = self.pool.get('account.move')
#             if auto_id.grn:
# #                 stri = 'grn'
# #                 self.split_auto_posting(cr,uid,stri)
#                 grn_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','grn')])
#                 for grn_id in grn_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [grn_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.customer_payment:
#                 cus_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','cus_pay')])
#                 for cus_id in cus_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [cus_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.supplier_payment:
#                 sup_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','sup_pay')])
#                 for sup_id in sup_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [sup_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.supplier_invoice:
#                 sup_inv_po_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','sup_inv_po')])
#                 for sup_inv_po_id in sup_inv_po_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [sup_inv_po_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.customer_invoice:
#                 cus_inv_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','cus_inv')])
#                 for cus_inv_id in cus_inv_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [cus_inv_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.material_issue:
#                 issue_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','good')])
#                 for issue_id in issue_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [issue_id], context)
#                     except:
#                         pass
#             if auto_id.delivery_order:
#                 do_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','do')])
#                 for do_id in do_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [do_id], context)
#                     except:
#                         pass
#             
#             if auto_id.cash_transactions:
#                 cash_pay_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','cash_pay')])
#                 for cash_pay_id in cash_pay_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [cash_pay_id], context)
#                     except:
#                         pass
#                     
#                 cash_rec_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','cash_rec')])
#                 for cash_rec_id in cash_rec_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [cash_rec_id], context)
#                     except:
#                         pass
#             
#             if auto_id.bank_transactions:
#                 bank_pay_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','bank_pay')])
#                 for bank_pay_id in bank_pay_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [bank_pay_id], context)
#                     except:
#                         pass
#                     
#                 bank_rec_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','bank_rec')])
#                 for bank_rec_id in bank_rec_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [bank_rec_id], context)
#                     except:
#                         pass
#             
#             if auto_id.supplier_invoice_without:
#                 sup_wi_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','sup_inv')])
#                 for sup_wi_id in sup_wi_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [sup_wi_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.service_invoice:
#                 ser_inv_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','ser_inv')])
#                 for ser_inv_id in ser_inv_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [ser_inv_id], context)
#                     except:
#                         pass
#             
#             if auto_id.freight_invoice:
#                 freight_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','freight')])
#                 for freight_id in freight_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [freight_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.production_declaration:
#                 product_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','product')])
#                 for product_id in product_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [product_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.journal_vouchers:
#                 voucher_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=',False)])
#                 for voucher_id in voucher_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [voucher_id], context)
#                     except:
#                         pass
#                     
#             if auto_id.payroll:
#                 payroll_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','payroll')])
#                 for payroll_id in payroll_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [payroll_id], context)
#                     except:
#                         pass
#                     
#                 staff_payroll_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','staff_payroll')])
#                 for staff_payroll_id in staff_payroll_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [staff_payroll_id], context)
#                     except:
#                         pass
#                     
#                 worker_payroll_ids = move_obj.search(cr, uid,[('state','=','draft'),('doc_type','=','worker_payroll')])
#                 for worker_payroll_id in worker_payroll_ids:
#                     try:
#                         move_obj.button_validate(cr, uid, [worker_payroll_id], context)
#                     except:
#                         pass
                    
        return True  
tpt_auto_posting()

class tpt_bank_reconciliation(osv.osv):
    _name = 'tpt.bank.reconciliation'
    _columns = {
        'name': fields.many2one('account.account', 'Bank GL Account', required=True),
        'date': fields.date('Payment Date'),
        'reconciliation_line': fields.one2many('tpt.bank.reconciliation.line', 'bank_reconciliation_id', 'Line'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
        'action_type': fields.selection([('action_reconcile', 'Load Reconciled Data'), ('action_unreconcile', 'Load Un-Reconciled Data'), 
                                    ('action_confirm', 'Load Confirmed Data')],'Action Type'), 
    }
    _defaults = {
        'state': 'draft',
    }
    def _check_state(self, cr, uid, ids, context=None):
        for bank in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_bank_reconciliation where id != %s and state = 'draft'
            '''%(bank.id)
            cr.execute(sql)
            bank_ids = [row[0] for row in cr.fetchall()]
            if bank_ids:  
                raise osv.except_osv(_('Warning!'),_('Can not create more than one record in this window!'))
        return True
    _constraints = [
        (_check_state, 'Identical Data', ['state']),
    ] 

    def onchange_account(self, cr, uid, ids, account_id=False, date = False, context=None):
        if context is None:
            context={}
        vals = {}
        if ids:
            cr.execute(''' delete from tpt_bank_reconciliation_line where bank_reconciliation_id in %s ''',(tuple(ids),))
        if account_id:
            tt_debit = 0.0
            tt_credit = 0.0
            voucher_obj = self.pool.get('account.voucher')
            voucher_ids = voucher_obj.search(cr, uid, [('account_id','=',account_id),('reconciliation_date','=',False)])
            if date:
                voucher_ids = voucher_obj.search(cr, uid, [('account_id','=',account_id),('reconciliation_date','=',False), ('date','=',date)])
            reconciliation_line = []
            for voucher in voucher_obj.browse(cr, uid, voucher_ids):
                doc_type = ''
                debit = 0.0
                credit = 0.0
                
                if voucher.journal_id.type=='bank':
                    if not voucher.tpt_sup_reconcile and voucher.type == 'payment':
                        doc_type='Supplier Payments'
                    if not voucher.tpt_sup_reconcile and voucher.type == 'receipt':
                        doc_type='Customer Payments'
                    if voucher.type_trans:
                        doc_type='Bank Transaction'
                    for move_id in voucher.move_ids:
                        if move_id.account_id.id == account_id:
                            if move_id.debit:
                                debit = move_id.debit
                            if move_id.credit:
                                credit = move_id.credit
                
                tt_debit += debit
                tt_credit += credit
                reconciliation_line.append((0,0,{
                    'partner_id': voucher.partner_id and voucher.partner_id.id or False,
                    'name': voucher.name,
                    'doc_type': doc_type,
                    'reference': voucher.reference,
                    'date': voucher.date,
                    'cheque_no': voucher.cheque_no,
                    'cheque_date': voucher.cheque_date,
                    'account_id': voucher.account_id and voucher.account_id.id or False,
                    'amount': voucher.amount,
                    'debit': debit,
                    'credit': credit,
                    'voucher_id': voucher.id,
                }))
            reconciliation_line.append((0,0,{
                'cheque_no': 'Total',
                'debit': tt_debit,
                'credit': tt_credit,
            }))
            reconciliation_line.append((0,0,{
                'cheque_no': 'Net Balance',
                'debit': tt_debit-tt_credit,
            }))
            vals = {'reconciliation_line':reconciliation_line}
        return {'value': vals}
    
    def bt_load(self, cr, uid, ids,context=None):
        if context is None:
            context={}
        vals = {}
        if ids:
            cr.execute(''' delete from tpt_bank_reconciliation_line where bank_reconciliation_id in %s ''',(tuple(ids),))
        
        for bank in self.browse(cr, uid, ids):
            if bank.name:
                tt_debit = 0.0
                tt_credit = 0.0
                voucher_obj = self.pool.get('account.voucher')
                ###TPTT-START - By BalamuruganPurushothaman ON 10/09/2015 
                is_reconciled = False
                is_unreconciled = False
                is_confirmed = False
                ### FROM POSTING ENTRIES
                sql = '''
                select av.id from account_voucher av
                inner join account_move am on av.move_id=am.id
                inner join account_move_line aml on am.id=aml.move_id
                where aml.account_id=(select id from account_account where id=%s)
                '''%bank.name.id
                cr.execute(sql)
                voucher_ids = [r[0] for r in cr.fetchall()]
                ###
                if not bank.date:
                    if bank.action_type=='action_unreconcile':
                        voucher_ids = voucher_obj.search(cr, uid, [('id','in',voucher_ids), ('status','=','unreconcile')])
                        is_unreconciled = True
                    elif bank.action_type=='action_reconcile':
                        voucher_ids = voucher_obj.search(cr, uid, [('id','in',voucher_ids), ('status','=','reconcile')])
                        is_reconciled = True
                    elif bank.action_type=='action_confirm':
                        voucher_ids = voucher_obj.search(cr, uid, [('id','in',voucher_ids), ('status','in',['confirmed'])])
                        is_confirmed = True
                #===============================================================
                # if bank.date:
                #     #voucher_ids = voucher_obj.search(cr, uid, [('account_id','=',bank.name.id),('reconciliation_date','=',False),('tpt_bank_re','=',False),('date','=',bank.date)])
                #     voucher_ids = voucher_obj.search(cr, uid, [('account_id','=',bank.name.id),('date','=',bank.date)])
                #===============================================================
                else:
                    if bank.action_type=='action_unreconcile':
                        voucher_ids = voucher_obj.search(cr, uid, [('id','in',voucher_ids), ('status','=','unreconcile'),('date','=',bank.date)])
                        is_unreconciled = True
                    elif bank.action_type=='action_reconcile':
                        voucher_ids = voucher_obj.search(cr, uid, [('id','in',voucher_ids), ('status','=','reconcile'),('date','=',bank.date)])
                        is_reconciled = True
                    elif bank.action_type=='action_confirm':
                        voucher_ids = voucher_obj.search(cr, uid, [('id','in',voucher_ids), ('status','in',['confirmed']),('date','=',bank.date)])
                        is_confirmed = True
                ###TPT-END
                reconciliation_line = []                                                        
                for voucher in voucher_obj.browse(cr, uid, voucher_ids):
                    doc_type = ''
                    debit = 0.0
                    credit = 0.0
                    
                    if voucher.journal_id.type=='bank':
                        if not voucher.tpt_sup_reconcile and voucher.type == 'payment':
                            doc_type='Supplier Payments'
                        if not voucher.tpt_sup_reconcile and voucher.type == 'receipt':
                            doc_type='Customer Payments'
                        if voucher.type_trans:
                            doc_type='Bank Transaction'
                        for move_id in voucher.move_ids:
                            if move_id.account_id.id == bank.name.id:
                                if move_id.debit:
                                    debit = move_id.debit
                                if move_id.credit:
                                    credit = move_id.credit
                    
                    tt_debit += debit
                    tt_credit += credit
                    ###
                    ###
                    reconciliation_line.append((0,0,{
                        'partner_id': voucher.partner_id and voucher.partner_id.id or False,
                        'name': voucher.number, #voucher.name, TPT-By Balamurugan Purushothaman on 10/09/2015
                        'doc_type': doc_type,
                        'reference': voucher.reference,
                        'date': voucher.date,
                        'cheque_no': voucher.cheque_no,
                        'cheque_date': voucher.cheque_date,
                        'account_id': voucher.account_id and voucher.account_id.id or False,
                        'amount': voucher.amount,
                        'debit': debit,
                        'credit': credit,
                        'voucher_id': voucher.id,
                        'reconciliation_date':voucher.reconciliation_date,
                        'status': voucher.status,
                        'is_reconciled': is_reconciled,
                        'is_unreconciled': is_unreconciled,
                        'is_confirmed': is_confirmed,
                    }))
                reconciliation_line.append((0,0,{
                    'cheque_no': 'Total',
                    'debit': tt_debit,
                    'credit': tt_credit,
                }))
                reconciliation_line.append((0,0,{
                    'cheque_no': 'Net Balance',
                    'debit': tt_debit-tt_credit,
                }))
                vals = {'reconciliation_line':reconciliation_line}
        return self.write(cr, uid, ids,vals)

    def bt_confirm(self, cr, uid, ids, context=None):
        for bank_reconciliation in self.browse(cr, uid, ids):
            ### TO THROW WARNING IF FORM TYPE IS "Un-Reconcile" WHEN CONFIRM
            sql = '''
                select id from tpt_bank_reconciliation_line where status='unreconcile' and reconciliation_date is not null
                and bank_reconciliation_id=%s
                '''%bank_reconciliation.id
            cr.execute(sql)
            bank_ids = [row[0] for row in cr.fetchall()]
            if bank_ids:  
                sql = '''
                select name from tpt_bank_reconciliation_line where status='unreconcile' and reconciliation_date is not null
                and bank_reconciliation_id=%s
                '''%bank_reconciliation.id
                cr.execute(sql)
                vouchers='' 
                for row in cr.fetchall():
                    vouchers = vouchers +'\n'+ row[0]                               
                raise osv.except_osv(_('Status Can not be "Un_reconciled" for the following Vouchers: '),_(vouchers))
            ###
            ###
            sql = '''
                select id from tpt_bank_reconciliation_line where status='confirmed' and reconciliation_date is not null
                and is_unreconciled='t'
                and bank_reconciliation_id=%s
                '''%bank_reconciliation.id
            cr.execute(sql)
            uc_ids = [row[0] for row in cr.fetchall()]
            if uc_ids:  
                sql = '''
                select name from tpt_bank_reconciliation_line where status='confirmed' and reconciliation_date is not null
                and is_unreconciled='t'
                and bank_reconciliation_id=%s
                '''%bank_reconciliation.id
                cr.execute(sql)
                vouchers='' 
                for row in cr.fetchall():
                    vouchers = vouchers +'\n'+ row[0]                               
                raise osv.except_osv(_('Status Can not be Changed to "Confirmed" directly from Un-Reconciled, for the following Vouchers: '),_(vouchers))
            ###
            for line in bank_reconciliation.reconciliation_line:
                if line.reconciliation_date:
                    cr.execute(''' update account_voucher set reconciliation_date=%s,tpt_bank_re='t', status=%s where id=%s ''',(line.reconciliation_date,line.status, line.voucher_id.id,))
        
            #Auto Reload
            self.bt_load(cr, uid, ids, context)   
            #
            #Info - to view status of Processing
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                                'green_erp_arulmani_accounting', 'alert_bank_form_view')           
            return {
                                        'name': 'Information',
                                        'view_type': 'form',
                                        'view_mode': 'form',
                                        'view_id': res[1],
                                        'res_model': 'alert.form.accounting',
                                        'domain': [],
                                        'context': {'default_message':'Updated Successfully!','audit_id':ids[0]},
                                        'type': 'ir.actions.act_window',
                                        'target': 'new',
                                    }
        return True
    
    
tpt_bank_reconciliation()

class tpt_bank_reconciliation_line(osv.osv):
    _name = 'tpt.bank.reconciliation.line'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer/Verdor'),
        'name': fields.char('Voucher No', size=1024),
        'doc_type': fields.char('Document Type', size=1024),
        'reference': fields.char('Payment Ref', size=1024),
        'date': fields.date('Payment Date'),
        'cheque_no': fields.char('Cheque No', size=1024),
        'cheque_date': fields.date('Cheque Date'),
        'reconciliation_date': fields.date('Reconciliation Date'),
        'account_id': fields.many2one('account.account', 'Bank GL Account'),
        'voucher_id': fields.many2one('account.voucher', 'Voucher'),
        'amount': fields.float('Payment Amount'),
        'debit': fields.float('Debit'),
        'credit': fields.float('Credit'),
        'bank_reconciliation_id': fields.many2one('tpt.bank.reconciliation', 'Bank Reconciliation', ondelete='cascade'),
        
        'status': fields.selection([('reconcile', 'Reconciled'), ('unreconcile', 'Un-Reconciled'), 
                                    ('confirmed', 'Confirmed')],'Status'), 
        
        'is_reconciled':fields.boolean('Is Reconciled',readonly =True ), 
        'is_unreconciled':fields.boolean('Is Un-Reconciled',readonly =True ),  
        'is_confirmed':fields.boolean('Is Confirmed',readonly =True ),         
                
    }
    
tpt_bank_reconciliation_line()


### TPT-START - ON 09/10/2015 - By BalamuruganPurushothaman - C-FORM
class tpt_cform_invoice(osv.osv):
    _name = 'tpt.cform.invoice'
    _columns = {
        #'name': fields.many2one('account.account', 'Bank GL Account', required=True),
        #'date': fields.date('Payment Date'),
        'name': fields.char('Name'),
        'cform_line': fields.one2many('tpt.cform.invoice.line', 'cform_id', 'Line'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
        'invoice_type':fields.selection([('to_be_collected', 'To be collected'),('collected', 'collected')],'Invoices'),
    }
    _defaults = {
        'state': 'draft',
        'name': 'Update C-Form',
        'invoice_type': 'to_be_collected',
    }
    def _check_state(self, cr, uid, ids, context=None):
        for bank in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_cform_invoice where id != %s and state = 'draft'
            '''%(bank.id)
            cr.execute(sql)
            bank_ids = [row[0] for row in cr.fetchall()]
            if bank_ids:  
                raise osv.except_osv(_('Warning!'),_('Can not create more than one record in this window!'))
        return True
    
    _constraints = [
        (_check_state, 'Identical Data', ['state']),
    ] 

    def bt_load(self, cr, uid, ids,context=None):
        if context is None:
            context={}
        vals = {}
        if ids:
            cr.execute(''' delete from tpt_cform_invoice_line where cform_id in %s ''',(tuple(ids),))
        for bank in self.browse(cr, uid, ids):
            invoice_obj = self.pool.get('account.invoice')
            invoice_domain = [('type', '=', 'out_invoice'), ('state', 'in' ,('open','paid')), ('sale_tax_id', 'ilike', 'CST')]
            if bank.invoice_type=='to_be_collected':
                invoice_domain = invoice_domain+[('form_type' ,'=', 'tbc')]
            invoice_ids = invoice_obj.search(cr, uid, invoice_domain)
            cform_line = []
            for invoice in invoice_obj.browse(cr, uid, invoice_ids):  
                for line in invoice.invoice_line:
                    product_id = line.product_id and line.product_id.id 
                    quantity = line.quantity or ''
                    uom_id = line.uos_id and line.uos_id.id    
                
                form_number = False
                form_date = False
                form_type = invoice.form_type or ''
                status = 'pending'
                if bank.invoice_type=='collected':
                    form_number = invoice.form_number
                    form_date = invoice.form_date
                    form_type = 'tbc'
                    status = 'pending'
                    if form_number or form_date:
                        form_type = 'cform'
                        status = 'received'
                
                cform_line.append((0,0,{
                    'invoice_no': invoice.vvt_number or '',      
                               
                    #'partner_id': invoice.partner_id and invoice.partner_id.id or False,
                    'date_invoiced': invoice.date_invoice,   
                    'sales_region' : invoice.partner_id and invoice.partner_id.state_id and  invoice.partner_id.state_id.name or '' ,       
                    'city' : invoice.partner_id and invoice.partner_id.city or '' ,                 
                    'invoice_id': invoice.id or False,
                    'bill_amount': invoice.amount_total or 0,
                    'form_type': form_type,
                    'customer_code':  '['+invoice.partner_id.customer_code+'] '+ invoice.partner_id.name,
                    'product_id': product_id or False,
                    'quantity': quantity or '',
                    'uom_id': uom_id or False,    
                    'gross_amt':invoice.amount_untaxed or 0,
                    'cst_amt':invoice.amount_tax or 0,
                    'form_number': form_number,
                    'form_date': form_date,
                    'status': status,
                }))
                
       
            vals = {'cform_line':cform_line}
        return self.write(cr, uid, ids,vals)

    def bt_confirm(self, cr, uid, ids, context=None):
        for cform in self.browse(cr, uid, ids):
            ### TO THROW WARNING IF FORM TYPE IS "To Be Collect" WHEN CONFIRM
            sql = '''
                select id from tpt_cform_invoice_line where form_type='tbc' and form_number is not null
                and cform_id=%s
                '''%cform.id
            cr.execute(sql)
            bank_ids = [row[0] for row in cr.fetchall()]
            if bank_ids:  
                sql = '''
                select invoice_no from tpt_cform_invoice_line where form_type='tbc' and form_number is not null
                and cform_id=%s
                '''%cform.id
                cr.execute(sql)
                invoice='' 
                for row in cr.fetchall():
                    invoice = invoice +'\n'+ row[0]                               
                raise osv.except_osv(_('Form Type Can not be "To Be Collect" for the following Invoices: '),_(invoice))
            ##TPT-BM-ON 06/06/2016 - CFORM WRITE ISSUE WHEN FORM NUMBER IS BLANK
            sql = '''
                select invoice_no from tpt_cform_invoice_line where form_type!='tbc' and form_number is null
                and cform_id=%s
                '''%cform.id
            cr.execute(sql)
            invoice='' 
            invoice_ids = cr.fetchall()
            if invoice_ids:
                for row in invoice_ids:
                    invoice = invoice +'\n'+ row[0]                               
                raise osv.except_osv(_('Form Number Can not be Empty for the following Invoices: '),_(invoice))
            ###
            for line in cform.cform_line:
                if line.form_number and line.form_date:
                    sql = ''' 
                    update account_invoice set form_number='%s',form_type='%s', form_date='%s' where id=%s 
                    '''%(line.form_number,line.form_type, line.form_date, line.invoice_id.id)
                    cr.execute(sql)
            ###
        self.bt_load(cr, uid, ids, context)
        return True
    
tpt_cform_invoice()

class tpt_cform_invoice_line(osv.osv):
    _name = 'tpt.cform.invoice.line'
    _columns = {  
        #'name': fields.char('Voucher No', size=1024),
        'invoice_no': fields.char('Invoice No', size=1024),
        'customer_code': fields.char('Customer'),  
        'partner_id': fields.many2one('res.partner', 'Customer'),  
        'date_invoiced': fields.date('Invoice Date'),
        'sales_region': fields.char('Sales Region'),
        'city': fields.char('City'),
        'product_id': fields.many2one('product.product', 'Product'),  
        'quantity': fields.float('Qty'),
        'uom_id': fields.many2one('product.uom', 'UOM'),  
        'gross_amt': fields.float('Gross Amt'),#
        'cst_amt': fields.float('CST Amt'),#
        'bill_amount': fields.float('Net Total'),# [('domestic','Domestic/Indirect Export'),('export','Export')],
        'form_type': fields.selection([('cform', 'C-Form'), ('fform', 'F-Form'), ('hform', 'H-Form'), ('iform', 'I-Form'),  
                                       ('na', 'Not Applicable'), ('tbc', 'To Be Collect')],'Form Type'), 
        'form_number': fields.char('Form Number'),
        'form_date': fields.date('Form Date'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice ID'),
        'cform_id': fields.many2one('tpt.cform.invoice', 'C Form', ondelete='cascade'),
        'status': fields.selection([('received', 'Received'),('pending', 'Pending')], 'Status'), # Added by SSR - 7-3-2017 - Ticket No - 3839
    }    
    _defaults = {
        'status': 'pending',        
    }
    def onchange_type(self, cr, uid, ids, type, context=None):
        if type=='tbc':
            raise osv.except_osv(_('Warning!'),_('Select other than "To Be Collect"!'))
        return True
    
tpt_cform_invoice_line()

# Created by P.VINOTHKUMAR ON 01/02/2016 for adding field carry_forward
class account_account(osv.osv):
     _inherit = 'account.account'
     _columns = {
                 'carry_forward':fields.boolean('Carry Forward'),
                 }
     _defaults= {
                  'carry_forward' : True,
                  }
