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
        'lic_id': fields.many2one('account.account', 'LIC-Premium-Employee', states={ 'done':[('readonly', True)]}),
        'profes_tax_id': fields.many2one('account.account', 'Profession Tax Payable', states={ 'done':[('readonly', True)]}),
        'lwf_id': fields.many2one('account.account', 'Labour welfare Fund', states={ 'done':[('readonly', True)]}),
        'staff_advance_id': fields.many2one('account.account', 'Staff Advance', states={ 'done':[('readonly', True)]}),
        'salari_payable_id': fields.many2one('account.account', 'Salaries And Allowance Payable', states={ 'done':[('readonly', True)]}),
        
        
        
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
                                  ('worker_payroll', 'Workers Payroll')], string="Document Type", readonly=True, select=True),
    }
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
        if context.get('search_grn_no_id'):
            sql = '''
                select picking_id from stock_move where state = 'cancel' group by picking_id
            '''
            cr.execute(sql)
            picking_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',picking_ids)]
            
        if context.get('search_grn_with_name', False):
            name = context.get('name')
            grn_ids = self.search(cr, uid, [('name','like',name)])
            args += [('id','in',grn_ids)]
        return super(stock_picking_in, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_grn_with_name':1,'name':name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)


    
stock_picking_in() 

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
        new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
#         stock_picking_in = self.pool.get('stock.picking.in').browse(cr,uid,vals['backorder_id'])
        for line in self.browse(cr,uid,ids):
            if 'state' in vals and line.type == 'in' and line.state=='done':
                debit = 0.0
                credit = 0.0
                for move in line.move_lines:
                    amount = move.purchase_line_id.price_unit * move.product_qty
                    debit += amount - (amount*move.purchase_line_id.discount)/100
                date_period = line.date,
                sql = '''
                    select id from account_period where special = False and '%s' between date_start and date_stop
                 
                '''%(date_period)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
#                 a = self.browse(cr,uid,period_ids[0])
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                 
                for period_id in period_obj.browse(cr,uid,period_ids):
                    sql_journal = '''
                    select id from account_journal
                    '''
                    cr.execute(sql_journal)
                    journal_ids = [r[0] for r in cr.fetchall()]
                    journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                    if not line.warehouse.gl_pos_verification_id:
                        raise osv.except_osv(_('Warning!'),_('Account Warehouse is not null, please configure it in Warehouse Location master !'))
                #sinh but toan
                    journal_line = [(0,0,{
                                        'name':line.name, 
                                        'account_id': line.warehouse.gl_pos_verification_id and line.warehouse.gl_pos_verification_id.id,
                                        'partner_id': line.partner_id and line.partner_id.id,
                                        'debit':debit,
                                        'credit':0,
                                         
                                       })]
                    for p in line.move_lines:
                        amount_cer = p.purchase_line_id.price_unit * p.product_qty
                        credit += amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                        if not p.product_id.purchase_acc_id:
                            raise osv.except_osv(_('Warning!'),_('You need to define Purchase GL Account for this product'))
                        journal_line.append((0,0,{
                            'name':line.name, 
                            'account_id': p.product_id.purchase_acc_id and p.product_id.purchase_acc_id.id,
                            'partner_id': line.partner_id and line.partner_id.id or False,
                            'credit':credit,
                            'debit':0,
                        }))
                         
                    value={
                        'journal_id':journal.id,
                        'period_id':period_id.id ,
                        'date': date_period,
                        'line_id': journal_line,
                        'doc_type':'grn'
                        }
                    new_jour_id = account_move_obj.create(cr,uid,value)
            if 'state' in vals and line.type == 'out' and line.state=='done':
                debit = 0.0
#                 so_id = line.sale_id and line.sale_id.id or False
                dis_channel = line.sale_id and line.sale_id.distribution_channel and line.sale_id.distribution_channel.name or False
                date_period = line.date
                account = False
                asset_id = False
                sql_journal = '''
                    select id from account_journal
                    '''
                cr.execute(sql_journal)
                journal_ids = [r[0] for r in cr.fetchall()]
                journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                sql = '''
                    select id from account_period where special = False and '%s' between date_start and date_stop
                  
                '''%(date_period)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                journal_line = []
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                for period_id in period_obj.browse(cr,uid,period_ids):
                #sinh but toan
                    for p in line.move_lines:
                        debit += p.sale_line_id and p.sale_line_id.price_unit * p.product_qty or 0
                        product_name = p.product_id.name
                        account = self.get_pro_account_id(cr,uid,product_name,dis_channel)
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
                        journal_line.append((0,0,{
                                    'name':line.name, 
                                    'account_id': account,
                                    'partner_id': line.partner_id and line.partner_id.id,
                                    'credit':0,
                                    'debit':debit,
                                }))
                         
                        journal_line.append((0,0,{
                            'name':line.name, 
                            'account_id': asset_id,
                            'partner_id': line.partner_id and line.partner_id.id,
                            'credit':debit,
                            'debit':0,
                        }))
                          
                    value={
                        'journal_id':journal.id,
                        'period_id':period_id.id ,
                        'date': date_period,
                        'line_id': journal_line,
                        'doc_type':'do'
                        }
                    new_jour_id = account_move_obj.create(cr,uid,value)
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
            grn_ids = self.search(cr, uid, [('name','like',name)])
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
     
    _columns = {
        'bill_number': fields.char('Bill Number', size=1024),
        'bill_date': fields.date('Bill Date'),
    }
      
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


    def onchange_purchase_id(self, cr, uid, ids,purchase_id=False, context=None):
        vals = {}
        if purchase_id:
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql)
        service_line = []
        purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
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
                          'invoice_line_tax_id': [(6,0,taxes_ids)],
                          'fright':line.fright or False,
                          'fright_type':line.fright_type or False,
                          'line_net': line.line_net or False,
                          'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                          'po_line_id': line.id,
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
                      'invoice_line_tax_id': [(6,0,taxes_ids)],
                      'fright':line.fright or False,
                      'fright_type':line.fright_type or False,
                      'line_net': line.line_net or False,
                      'account_id':line.product_id and line.product_id.purchase_acc_id and line.product_id.purchase_acc_id.id or False,
                      }
                service_line.append((0,0,rs))
        vals = {
                'partner_id':purchase.partner_id and purchase.partner_id.id or False,
                'vendor_ref':purchase.partner_ref or False,
                'invoice_line': service_line,
                }
        return {'value': vals}
    
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(account_invoice, self).create(cr, uid, vals, context=context)
        new = self.browse(cr,uid,new_id)
        if new.purchase_id.po_document_type == 'service':
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
        return new_id
     
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(account_invoice, self).write(cr, uid,ids, vals, context)
        for new in self.browse(cr,uid,ids):
            if new.purchase_id.po_document_type == 'service':
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
#             iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
#             for account_line in inv.invoice_line: 
#             iml = invoice_line_obj.move_line_price_different(cr, uid, inv.id)
            if (inv.type == 'in_invoice'): 
                iml = invoice_line_obj.move_line_pf(cr, uid, inv.id)
                iml += invoice_line_obj.move_line_fright(cr, uid, inv.id) 
                iml += invoice_line_obj.move_line_amount_tax(cr, uid, inv.id)
                iml += invoice_line_obj.move_line_excise_duty(cr, uid, inv.id)
                iml += invoice_line_obj.move_line_aed(cr, uid, inv.id)
                if inv.purchase_id:
                    iml += invoice_line_obj.move_line_amount_untaxed(cr, uid, inv.id) 
                    iml += invoice_line_obj.move_line_tds_amount_without_po(cr, uid, inv.id) 
                else:
                    iml += invoice_line_obj.move_line_amount_untaxed_without_po(cr, uid, inv.id) 
                    iml += invoice_line_obj.move_line_tds_amount_without_po(cr, uid, inv.id) 
            if (inv.type == 'out_invoice'):
                iml = invoice_line_obj.move_line_customer_fright(cr, uid, inv.id) 
                iml += invoice_line_obj.move_line_customer_amount_tax(cr, uid, inv.id) 
                iml += invoice_line_obj.move_line_customer_excise_duty(cr, uid, inv.id) 
                iml += invoice_line_obj.move_line_customer_product_price(cr, uid, inv.id)
                
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
  
            name = inv['name'] or inv['supplier_invoice_number'] or '/'
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
                    'ref': ref
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
            if (inv.type == 'out_invoice'):
                move['doc_type'] = 'cus_inv'
            if (inv.type == 'in_invoice'):
                if inv.purchase_id:
                    if inv.purchase_id.po_document_type == 'service':
                        move['doc_type'] = 'ser_inv'
                    else:
                        move['doc_type'] = 'sup_inv_po'
                        move['ref'] = inv.grn_no.name
                else:
                    move['doc_type'] = 'sup_inv'
  
            ctx.update(invoice=inv)
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
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))
                    if new_name:
                        move_obj.write(cr, uid, [move.id], {'name':new_name})
#             move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
     
    
#     def line_get_convert(self, cr, uid, x, part, date, context=None):
#         return {
#             'date_maturity': x.get('date_maturity', False),
#             'partner_id': part,
#             'name': x['name'][:64],
#             'date': date,
#             'debit': x['price']>0 and x['price'],
#             'credit': x['price']<0 and -x['price'],
#             'account_id': x['account_id'],
#             'analytic_lines': x.get('analytic_lines', []),
#             'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
#             'currency_id': x.get('currency_id', False),
#             'tax_code_id': x.get('tax_code_id', False),
#             'tax_amount': x.get('tax_amount', False),
#             'ref': x.get('ref', False),
#             'quantity': x.get('quantity',1.00),
#             'product_id': x.get('product_id', False),
#             'product_uom_id': x.get('uos_id', False),
#             'analytic_account_id': x.get('account_analytic_id', False),
#         }

    
account_invoice()
 
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
     
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
        }  
    def move_line_amount_untaxed(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            sql = '''
                SELECT purchase_acc_id FROM product_product WHERE id=%s and purchase_acc_id is not null
            '''%(t['product_id'])
            cr.execute(sql)
            purchase_acc_id = cr.dictfetchone()
            if not purchase_acc_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
            if basic:
                if round(basic):
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': round(basic),
                        'account_id': purchase_acc_id and purchase_acc_id['purchase_acc_id'] or False,
                        'account_analytic_id': t['account_analytic_id'],
                        })
        return res
    
    def move_line_amount_untaxed_without_po(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            if basic:
                if round(basic):
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': round(basic),
                        'account_id': t['account_id'],
                        'account_analytic_id': t['account_analytic_id'],
                        })
        return res
    
    def move_line_tds_amount_without_po(self, cr, uid, invoice_id):
        res = []
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        for line in invoice.invoice_line:
            tds_amount = 0
            if line.tds_id:    
                tds_amount = line.quantity * line.price_unit * line.tds_id.amount/100
                if not line.tds_id.gl_account_id:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure GL Account in Tax master for TDS %'))
                if tds_amount:   
                    if round(tds_amount):
                        res.append({
                            'type':'tax',
                            'name':line.name,
                            'price_unit': line.price_unit,
                            'quantity': 1,
                            'price': round(-tds_amount),
                            'account_id': line.tds_id and line.tds_id.gl_account_id and line.tds_id.gl_account_id.id or False,
                            'account_analytic_id': line.account_analytic_id.id,
                        })
        return res 
     
    def move_line_customer_product_price(self, cr, uid, invoice_id, context = None):
        res = []
        account = False
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': time.strftime('%Y-%m-%d')})
        voucher_rate = 1
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            channel = inv_id.delivery_order_id and inv_id.delivery_order_id.sale_id and inv_id.delivery_order_id.sale_id.distribution_channel and inv_id.delivery_order_id.sale_id.distribution_channel.name or False
            currency = inv_id.currency_id.name
            currency_id = inv_id.currency_id.id
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            product_id = self.pool.get('product.product').browse(cr, uid, t['product_id'])
            name = product_id.name or False
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
            price = t['price_unit']*t['quantity']*voucher_rate
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
                    })
        return res
    def move_line_customer_excise_duty(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': time.strftime('%Y-%m-%d')})
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        account_line_ids = [r[0] for r in cr.fetchall()]
        for line in self.browse(cr,uid,account_line_ids):
#             cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
#             for account in cr.dictfetchall():
            ed_amount = voucher_rate * (line.quantity * line.price_unit) * (line.invoice_id.excise_duty_id.amount and line.invoice_id.excise_duty_id.amount/100 or 1)
            sql = '''
                    SELECT cus_inv_ed_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_ed_id is not null
                '''
            cr.execute(sql)
            cus_inv_ed_id = cr.dictfetchone()
            if not cus_inv_ed_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            if ed_amount:
                if round(ed_amount):
                    res.append({
                        'type':'tax',
                        'name':line.name,
                        'price_unit': line.price_unit,
                        'quantity': 1,
                        'price':round(ed_amount),
                        'account_id': cus_inv_ed_id and cus_inv_ed_id['cus_inv_ed_id'] or False,
                        'account_analytic_id': line.account_analytic_id.id,
                    })
        return res  
    def move_line_amount_tax(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': time.strftime('%Y-%m-%d')})
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        for line in inv_id.invoice_line:
            basic = 0.0
            p_f = 0.0
            ed = 0.0
            tax_value = 0.0
            if line.invoice_line_tax_id:
                tax_names = [r.name for r in line.invoice_line_tax_id]
                for tax_name in tax_names:
                    if 'CST' in tax_name:
                        tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                        for tax_amount in tax_amounts:
                            tax_value += tax_amount/100
                            basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                            if line.p_f_type == '1' :
                                p_f = basic * line.p_f/100
                            elif line.p_f_type == '2' :
                                p_f = line.p_f
                            elif line.p_f_type == '3' :
                                p_f = line.p_f * line.quantity
                            else:
                                p_f = line.p_f
                            if line.ed_type == '1' :
                                ed = (basic + p_f) * line.ed/100
                            elif line.ed_type == '2' :
                                ed = line.ed
                            elif line.ed_type == '3' :
                                ed = line.ed * line.quantity
                            else:
                                ed = line.ed
                            tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                        sql = '''
                            SELECT sup_inv_cst_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_cst_id is not null
                        '''
                        cr.execute(sql)
                        sup_inv_cst_id = cr.dictfetchone()
                        if sup_inv_cst_id:
                            account = sup_inv_cst_id and sup_inv_cst_id['sup_inv_cst_id'] or False
                        else:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure CST Receivables in GL Posting Configrution !'))
                        if tax:    
                            if round(tax):
                                res.append({
                                    'type':'tax',
                                    'name':line.name,
                                    'price_unit': line.price_unit,
                                    'quantity': 1,
                                    'price': round(tax),
                                    'account_id': account,
                                    'account_analytic_id': line.account_analytic_id.id,
                                    })
                            break
                    elif 'VAT' in tax_name:
                        tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                        for tax_amount in tax_amounts:
                            tax_value += tax_amount/100
                            basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                            if line.p_f_type == '1' :
                                p_f = basic * line.p_f/100
                            elif line.p_f_type == '2' :
                                p_f = line.p_f
                            elif line.p_f_type == '3' :
                                p_f = line.p_f * line.quantity
                            else:
                                p_f = line.p_f
                            if line.ed_type == '1' :
                                ed = (basic + p_f) * line.ed/100
                            elif line.ed_type == '2' :
                                ed = line.ed
                            elif line.ed_type == '3' :
                                ed = line.ed * line.quantity
                            else:
                                ed = line.ed
                            tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                        sql = '''
                            SELECT sup_inv_vat_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_vat_id is not null
                        '''
                        cr.execute(sql)
                        sup_inv_vat_id = cr.dictfetchone()
                        if sup_inv_vat_id:
                            account = sup_inv_vat_id and sup_inv_vat_id['sup_inv_vat_id'] or False
                        else:
                            raise osv.except_osv(_('Warning!'),_('Account is not null, please configure VAT Receivables in GL Posting Configrution !'))
                        if tax:     
                            if round(tax):
                                res.append({
                                    'type':'tax',
                                    'name':line.name,
                                    'price_unit': line.price_unit,
                                    'quantity': 1,
                                    'price': round(tax),
                                    'account_id': account,
                                    'account_analytic_id': line.account_analytic_id.id,
                                })
                            break
                    else:
                        tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                        for tax_amount in tax_amounts:
                            tax_value += tax_amount/100
                            basic = (line.quantity * line.price_unit) - ( (line.quantity * line.price_unit)*line.disc/100)
                            if line.p_f_type == '1' :
                                p_f = basic * line.p_f/100
                            elif line.p_f_type == '2' :
                                p_f = line.p_f
                            elif line.p_f_type == '3' :
                                p_f = line.p_f * line.quantity
                            else:
                                p_f = line.p_f
                            if line.ed_type == '1' :
                                ed = (basic + p_f) * line.ed/100
                            elif line.ed_type == '2' :
                                ed = line.ed
                            elif line.ed_type == '3' :
                                ed = line.ed * line.quantity
                            else:
                                ed = line.ed
                            tax = (basic + p_f + ed)*(tax_value) * voucher_rate
                        sql = '''
                            SELECT sup_inv_vat_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_vat_id is not null
                        '''
                        cr.execute(sql)
                        sup_inv_vat_id = cr.dictfetchone()
                        if sup_inv_vat_id:
                            account = sup_inv_vat_id and sup_inv_vat_id['sup_inv_vat_id'] or False
                        sql = '''
                            SELECT sup_inv_cst_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_cst_id is not null
                        '''
                        cr.execute(sql)
                        sup_inv_cst_id = cr.dictfetchone()
                        if sup_inv_cst_id:
                            account = sup_inv_cst_id and sup_inv_cst_id['sup_inv_cst_id'] or False
                        if sup_inv_vat_id or sup_inv_cst_id:
                            if tax:  
                                if round(tax):
                                    res.append({
                                        'type':'tax',
                                        'name':line.name,
                                        'price_unit': line.price_unit,
                                        'quantity': 1,
                                        'price': round(tax),
                                        'account_id': account,
                                        'account_analytic_id': line.account_analytic_id.id,
                                    })
                                    break
                                break
                        else :
                                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
        return res
    
    def move_line_customer_amount_tax(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': time.strftime('%Y-%m-%d')})
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
        if currency != 'INR':
            voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
                tax = account['amount_tax'] * voucher_rate
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
                                        'price': round(tax),
                                        'account_id': account,
                                        'account_analytic_id': t['account_analytic_id'],
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
                                        'price': round(tax),
                                        'account_id': account,
                                        'account_analytic_id': t['account_analytic_id'],
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
                                        'price': round(tax),
                                        'account_id': account,
                                        'account_analytic_id': t['account_analytic_id'],
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
                    if round(account['fright']):
                        res.append({
                            'type':'tax',
                            'name':t['name'],
                            'price_unit': t['price_unit'],
                            'quantity': 1,
                            'price': round(account['fright']),
                            'account_id': sup_inv_fright_id and sup_inv_fright_id['sup_inv_fright_id'] or False,
                            'account_analytic_id': t['account_analytic_id'],
                        })
                        break
                break
        return res 
    def move_line_customer_fright(self, cr, uid, invoice_id, context = None):
        res = []
        voucher_rate = 1
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': time.strftime('%Y-%m-%d')})
        inv_id = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv_id:
            currency = inv_id.currency_id.name or False
            currency_id = inv_id.currency_id.id or False
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
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': round(t['freight'] * voucher_rate),
                        'account_id': cus_inv_fright_id and cus_inv_fright_id['cus_inv_fright_id'] or False,
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
                    if round(account['excise_duty']):
                        res.append({
                            'type':'tax',
                            'name':t['name'],
                            'price_unit': t['price_unit'],
                            'quantity': 1,
                            'price': round(account['excise_duty']),
                            'account_id': sup_inv_ed_id and sup_inv_ed_id['sup_inv_ed_id'] or False,
                            'account_analytic_id': t['account_analytic_id'],
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
                if round(account['aed']):
                    res.append({
                        'type':'tax',
                        'name':'/',
                        'price_unit': account['aed'],
                        'quantity': 1,
                        'price': round(account['aed']),
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
                    if round(account['p_f_charge']):
                        res.append({
                            'type':'tax',
                            'name':t['name'],
                            'price_unit': t['price_unit'],
                            'quantity': 1,
                            'price': round(account['p_f_charge']),
                            'account_id': sup_inv_pf_id and sup_inv_pf_id['sup_inv_pf_id'] or False,
                            'account_analytic_id': t['account_analytic_id'],
                        })
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
#     def move_line_price_total(self, cr, uid, invoice_id):
#         res = []
#         cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
#         for t in cr.dictfetchall():
#             cr.execute('SELECT * FROM account_invoice WHERE id=%s', (t['invoice_id'],))
#             for account in cr.dictfetchall():
#                 sql = '''
#                     SELECT sup_inv_price_id FROM tpt_posting_configuration WHERE name = 'sup_inv' and sup_inv_price_id is not null
#                 '''
#                 cr.execute(sql)
#                 sup_inv_price_id = cr.dictfetchone()
#                 if not sup_inv_price_id:
#                     raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
#                 res.append({
#                     'type':'tax',
#                     'name':account['name'],
#                     'price_unit': t['price_unit'],
#                     'quantity': 1,
#                     'price': account['amount_total'],
#                     'account_id': sup_inv_price_id and sup_inv_price_id['sup_inv_price_id'] or False,
#                     'account_analytic_id': t['account_analytic_id'],
#                 })
#                 break
#             break
#         return res   
account_invoice_line()

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
    
#     def init(self,cr):
#         category_obj = self.pool.get('product.category')
#         category_ids = category_obj.search(cr, 1, [('cate_name','=','spares')])
#         for category in category_obj.browse(cr, 1, category_ids):
#             produc_ids = self.search(cr, 1, [('categ_id','=',category.id)])
#             self.write(cr, 1, produc_ids, {
#                 'property_account_income':category.property_account_income_categ and category.property_account_income_categ.id or False,
#                 'property_account_expense':category.property_account_expense_categ and category.property_account_expense_categ.id or False,
#             })
    
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
                        avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    inventory_obj.create(cr, uid, {'product_id':id,
                                                   'warehouse_id':loc['loc'],
                                                   'hand_quantity':hand_quantity,
                                                   'avg_cost':avg_cost,
                                                   'total_cost':total_cost})
            result[id] = 'Avg Cost'
        return result
    
    def _get_product(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('stock.move').browse(cr, uid, ids, context=context):
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
        }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_with_name', False):
            name = context.get('name')
            product_ids = self.search(cr, uid, ['|',('name','like',name),('default_code','like',name)])
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
    
    def _get_tpt_currency_amount(self, cr, uid, ids, name, args, context=None):
        res = {}
        if context is None:
            context = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            amount = 0
            if voucher.tpt_currency_id and voucher.tpt_currency_amount:
                context.update({'date': time.strftime('%Y-%m-%d')})
                voucher_rate = self.pool.get('res.currency').read(cr, uid, voucher.tpt_currency_id.id, ['rate'], context=context)['rate']
                amount = voucher.tpt_currency_amount/voucher_rate
            res[voucher.id] = amount
        return res
    
    _columns = {
        'name': fields.char( 'Journal no.',size = 256),
        'memo':fields.char('Memo', size=256, readonly=True, states={'draft':[('readonly',False)]}),
        'cheque_date': fields.date('Cheque Date'),
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
             ('posted','Posted')
            ], 'Status', readonly=True, size=32, track_visibility='onchange',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Voucher. \
                        \n* The \'Pro-forma\' when voucher is in Pro-forma status,voucher does not have an voucher number. \
                        \n* The \'Posted\' status is used when user create voucher,a voucher number is generated and voucher entries are created in account \
                        \n* The \'Cancelled\' status is used when user cancel voucher.'),
        'tpt_currency_id':fields.many2one('res.currency','Currency'),
        'is_tpt_currency':fields.boolean('Is TPT Currency'),
        'tpt_amount':fields.function(_get_tpt_currency_amount,type='float',string='Paid Amount (INR)'),
        'tpt_currency_amount':fields.float('Paid Amount'),
        'payee':fields.char('Payee', size=1024),
        'employee_id':fields.many2one('hr.employee','Employee'),
        }
    
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(account_voucher, self).default_get(cr, uid, fields, context=context)
        journal = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'cash')])
        if context.get('get_customer_reconcile'):
            res.update({'journal_id': journal[0],'tpt_cus_reconcile': True})
        if context.get('get_supp_reconcile'):
            res.update({'journal_id': journal[0],'tpt_sup_reconcile': True})
        user = self.pool.get('res.users').browse(cr, uid, uid)
        partner_id = user.company_id.partner_id.id
        res.update({'partner_id': partner_id})
        
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
    
    def onchange_tpt_currency_amount(self, cr, uid, ids, tpt_currency_id, tpt_currency_amount, type, context=None):
        if context is None:
            context = {}
        vals = {}
        if type in ['receipt','payment']:
            vals = {
                'amount': 0,
                'tpt_amount': 0,
            }
            if tpt_currency_id and tpt_currency_amount:
                context.update({'date': time.strftime('%Y-%m-%d')})
                voucher_rate = self.pool.get('res.currency').read(cr, uid, tpt_currency_id, ['rate'], context=context)['rate']
                vals = {
                    'amount': tpt_currency_amount/voucher_rate,
                    'tpt_amount': tpt_currency_amount/voucher_rate,
                }
        return {'value': vals}
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.journal.voucher.sequence') or '/'
        new_id = super(account_voucher, self).create(cr, uid, vals, context)
        if context is None:
            context = {}
        new = self.browse(cr, uid, new_id)
        if new.type_trans:
            total = 0
            sql = '''
                update account_voucher set type_cash_bank = 'cash' where journal_id in (select id from account_journal where type = 'cash')
            '''
            cr.execute(sql)
            sql = '''
                update account_voucher set type_cash_bank = 'bank' where journal_id in (select id from account_journal where type = 'bank')
            '''
            cr.execute(sql)
            for line in new.line_ids:
                total += line.amount 
            if new.sum_amount != total:
                raise osv.except_osv(_('Warning!'),
                    _('Total amount in Voucher Entry must equal Amount!'))
        elif context.get('journal_entry_create',False):
            sql = '''
                update account_voucher set type_cash_bank = 'journal' where id = %s
            '''%(new_id)
            cr.execute(sql)
            total_debit = 0
            total_credit = 0
            for line in new.line_ids:
                if line.type=='dr':
                    total_debit += line.amount
                if line.type=='cr':
                    total_credit += line.amount 
            if total_debit != total_credit:
                raise osv.except_osv(_('Warning!'),
                    _('Total Debit must be equal Total Credit!'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        new_write = super(account_voucher, self).write(cr, uid, ids, vals, context)
        for voucher in self.browse(cr, uid, ids):
            if voucher.type_trans:
                total = 0
                for line in voucher.line_ids:
                    total += line.amount 
                if voucher.sum_amount != total:
                    raise osv.except_osv(_('Warning!'),
                        _('Total amount in Voucher Entry must equal Amount!'))
            elif context.get('journal_entry_create',False):
                sql = '''
                    update account_voucher set type_cash_bank = 'journal' where id = %s
                '''%(voucher.id)
                cr.execute(sql)
                total_debit = 0
                total_credit = 0
                for line in voucher.line_ids:
                    if line.type=='dr':
                        total_debit += line.amount
                    if line.type=='cr':
                        total_credit += line.amount 
                if total_debit != total_credit:
                    raise osv.except_osv(_('Warning!'),
                        _('Total Debit must be equal Total Credit!'))
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
            elif voucher.type_trans in ('receipt'):
                debit = voucher.sum_amount
                account_id = voucher.account_id.id
#/phuoc
        else:
            if voucher.type in ('purchase', 'payment'):
                credit = voucher.paid_amount_in_company_currency
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
                debit = voucher.paid_amount_in_company_currency
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

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
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
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
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
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids)
    
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
            ctx.update({'date': voucher.date})
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
                line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
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
                
                line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
    
                # Create the writeoff line if needed
                if voucher.type_cash_bank != 'journal':
                    ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
                    if ml_writeoff:
                        move_line_pool.create(cr, uid, ml_writeoff, local_context)
        
            
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
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

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
        }
        if voucher.type_trans:
            if voucher.journal_id.type == 'bank': 
                if voucher.type_trans == 'payment':
                    move['doc_type'] = 'bank_pay'
                if voucher.type_trans == 'receipt':
                    move['doc_type'] = 'bank_rec'
            if voucher.journal_id.type == 'cash':
                if voucher.type_trans == 'payment':
                    move['doc_type'] = 'cash_pay'
                if voucher.type_trans == 'receipt':
                    move['doc_type'] = 'cash_rec'
        else:
            if (voucher.journal_id.type == 'bank' or voucher.journal_id.type == 'cash'):
                if voucher.type == 'receipt':
                    move['doc_type'] = 'cus_pay'
                if voucher.type == 'payment':
                    move['doc_type'] = 'sup_pay'
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
        if partner_id:
            res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
            for key in res.keys():
                vals[key].update(res[key])
        return vals
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
    _columns = {
                'gl_account_id': fields.many2one('account.account', 'GL Account'),
                'warehouse':fields.many2one('stock.location','Source Location'),
                'dest_warehouse_id': fields.many2one('stock.location','Destination Location'),
                }
    def bt_approve(self, cr, uid, ids, context=None):
        price = 0.0
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
                if cate_name == 'finish':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                        sql = '''
                            select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
                                (select st.product_qty as product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                                 union all
                                 select st.product_qty*-1 as product_qty
                                    from stock_move st 
                                    where st.state='done'
                                    and st.product_id=%s
                                                and location_id=%s
                                                and location_dest_id != location_id
                                )foo
                        '''%(p.product_id.id,location_id,p.product_id.id,location_id)
                        cr.execute(sql)
                        onhand_qty = cr.dictfetchone()['onhand_qty']
                if cate_name == 'raw':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                if cate_name == 'spares':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                if location_id and cate_name != 'finish':
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
                            (select st.product_qty as product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                             union all
                             select st.product_qty*-1 as product_qty
                                from stock_move st 
                                where st.state='done'
                                        and st.product_id=%s
                                            and location_id=%s
                                            and location_dest_id != location_id
                            )foo
                    '''%(p.product_id.id,location_id,p.product_id.id,location_id)
                    cr.execute(sql)
                    onhand_qty = cr.dictfetchone()['onhand_qty']
                if (p.product_isu_qty > onhand_qty):
                    raise osv.except_osv(_('Warning!'),_('Issue quantity are %s but only %s available for this product in stock.' %(p.product_isu_qty, onhand_qty)))
                rs = {
                      'name': '/',
                      'product_id':p.product_id and p.product_id.id or False,
                      'product_qty':p.product_isu_qty or False,
                      'product_uom':p.uom_po_id and p.uom_po_id.id or False,
                      'location_id':line.warehouse and line.warehouse.id or False,
                      'location_dest_id':dest_id,
                      
                      }
                move_id = move_obj.create(cr,uid,rs)
                move_obj.action_done(cr, uid, [move_id])
            
            if not line.warehouse.gl_pos_verification_id:
                    raise osv.except_osv(_('Warning!'),_('Account Warehouse is not null, please configure it in Warehouse Location master !'))
            for mater in line.material_issue_line:
#                 price += mater.product_id.standard_price * mater.product_isu_qty
                avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                if avg_cost_ids:
                    avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                    unit = avg_cost_id.avg_cost or 0
                    price += unit * mater.product_isu_qty
            date_period = line.date_expec,
            sql = '''
                select id from account_journal
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            sql = '''
                select id from account_period where '%s' between date_start and date_stop
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            for period_id in period_obj.browse(cr,uid,period_ids):
                if not line.warehouse.gl_pos_verification_id:
                    raise osv.except_osv(_('Warning!'),_('Account Warehouse is not null, please configure it in Warehouse Location master !'))
                journal_line = [(0,0,{
                                        'name':line.date_expec, 
                                        'account_id': line.warehouse.gl_pos_verification_id and line.warehouse.gl_pos_verification_id.id,
#                                         'partner_id': line.partner_id and line.partner_id.id,
                                        'debit':0,
                                        'credit':price,
                                        
                                       })]
                if line.gl_account_id:
                    journal_line.append((0,0,{
                                'name':line.date_expec, 
                                'account_id': line.gl_account_id and line.gl_account_id.id,
#                                 'partner_id': line.partner_id and line.partner_id.id,
                                'credit':0,
                                'debit':price,
                            }))
                else: 
                    raise osv.except_osv(_('Warning!'),_('GL Account is not configured! Please configured it!'))
                value={
                    'journal_id':journal_ids[0],
                    'period_id':period_id.id ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type':'good'
                    }
                new_jour_id = account_move_obj.create(cr,uid,value)
            self.write(cr, uid, ids,{'state':'done'})
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
            
            sql_ma = '''
                select sum(float) as allowance from arul_hr_payroll_earning_structure where earning_parameters_id in (select id from arul_hr_payroll_earning_parameters where code='MA')
                and executions_details_id in (select id from arul_hr_payroll_executions_details where payroll_executions_id = %s)
            '''%(payroll_ids)
            cr.execute(sql_ma)
            ma = cr.dictfetchone()['allowance'] or 0.0
            welfare = oa + ma
            
            ### END Excutive & Staff - Worker
            
            sum_credit = (provident + vpf + tax + lwf + welfare + lic_premium +
                           + ins_oth + vvt_loan + vvt_hdfc + hfl + tmb + sbt + other)
            diff = gross - sum_credit
            
            res = {'gross':gross,
                   'provident':provident,
                   'vpf':vpf,
                   'tax':tax,
                   'lwf':lwf,
                   'lic_premium':lic_premium,
                   'welfare':welfare,
                   'ins_oth':ins_oth,
                   'vvt_loan':vvt_loan,
                   'vvt_hdfc':vvt_hdfc,
                   'hfl':hfl,
                   'sbt':sbt,
                   'other':other,
                   'tmb':tmb,
                   'diff':diff,
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
            select id from account_journal
            '''
            cr.execute(sql_journal)
            journal_ids = [r[0] for r in cr.fetchall()]
            journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0]) 
            for configuration in configuration_obj.browse(cr,uid,configuration_ids):
                gross_acc = configuration.salari_id and configuration.salari_id.id or False
                provident_acc = configuration.pfp_id and configuration.pfp_id.id or False
                vpf_acc = configuration.vpf_id and configuration.vpf_id.id or False
                welfare_acc = configuration.staff_welfare_id and configuration.staff_welfare_id.id or False
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
               
                salari_acc = configuration.salari_payable_id and configuration.salari_payable_id.id or False
                wages_acc = configuration.wages_id and configuration.wages_id.id or False
                wages_payable_acc = configuration.wages_payable_id and configuration.wages_payable_id.id or False
                if not gross_acc or not provident_acc or not vpf_acc or not welfare_acc or not lic_premium_acc \
                or not pro_tax_acc or not lwf_acc or not other_insu_acc or not vvti_acc or not lic_hfl_acc or not hdfc_acc \
                or not tmb_acc or not sbt_acc or not other_loan_acc or not salari_acc or not wages_acc or not wages_payable_acc:
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
                    
                    res1 = self.get_account_amount(cr,uid,payroll_excutive_id)
                    
                    
                    journal_s1_line = [(0,0,{
                                    'name':line.year, 
                                    'account_id': gross_acc,
                                    'debit':res1['gross'],
                                    'credit':0,
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': provident_acc,
                                    'debit':0,
                                    'credit':res1['provident'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': vpf_acc,
                                    'debit':0,
                                    'credit':res1['vpf'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': welfare_acc,
                                    'debit':0,
                                    'credit':res1['welfare'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lic_premium_acc,
                                    'debit':0,
                                    'credit':res1['lic_premium'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': pro_tax_acc,
                                    'debit':0,
                                    'credit':res1['tax'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lwf_acc,
                                    'debit':0,
                                    'credit':res1['lwf'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': other_insu_acc,
                                    'debit':0,
                                    'credit':res1['ins_oth'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': vvti_acc, 
                                    'debit':0,
                                    'credit':res1['vvt_loan'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': hdfc_acc,
                                    'debit':0,
                                    'credit':res1['vvt_hdfc'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lic_hfl_acc,
                                    'debit':0,
                                    'credit':res1['hfl'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': sbt_acc,
                                    'debit':0,
                                    'credit':res1['sbt'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': other_loan_acc,
                                    'debit':0,
                                    'credit':res1['other'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': tmb_acc,
                                    'debit':0,
                                    'credit':res1['tmb'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': salari_acc,
                                    'debit':0,
                                    'credit':res1['diff'],
                                   }),]
                value_s1={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': time.strftime('%Y-%m-%d'),
                    'line_id': journal_s1_line,
                    'doc_type':'payroll'
                    }
                new_s1_jour_id = account_move_obj.create(cr,uid,value_s1)
                payroll_obj.write(cr, uid, excutive.id, {'state':'approve'})
            if payroll_staff_id:
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
                        
                    res2 = self.get_account_amount(cr,uid,payroll_staff_id)
                    
                    journal_s2_line = [(0,0,{
                                    'name':line.year, 
                                    'account_id': gross_acc,
                                    'debit':res2['gross'],
                                    'credit':0,
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': provident_acc,
                                    'debit':0,
                                    'credit':res2['provident'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': vpf_acc,
                                    'debit':0,
                                    'credit':res2['vpf'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': welfare_acc,
                                    'debit':0,
                                    'credit':res2['welfare'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lic_premium_acc,
                                    'debit':0,
                                    'credit':res2['lic_premium'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': pro_tax_acc,
                                    'debit':0,
                                    'credit':res2['tax'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lwf_acc,
                                    'debit':0,
                                    'credit':res2['lwf'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': other_insu_acc,
                                    'debit':0,
                                    'credit':res2['ins_oth'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': vvti_acc, 
                                    'debit':0,
                                    'credit':res2['vvt_loan'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': hdfc_acc,
                                    'debit':0,
                                    'credit':res2['vvt_hdfc'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lic_hfl_acc,
                                    'debit':0,
                                    'credit':res2['hfl'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': sbt_acc,
                                    'debit':0,
                                    'credit':res2['sbt'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': other_loan_acc,
                                    'debit':0,
                                    'credit':res2['other'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': tmb_acc,
                                    'debit':0,
                                    'credit':res2['tmb'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': salari_acc,
                                    'debit':0,
                                    'credit':res2['diff'],
                                   }),]
                value_s2={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': time.strftime('%Y-%m-%d'),
                    'line_id': journal_s2_line,
                    'doc_type':'staff_payroll'
                    }
                new_s2_jour_id = account_move_obj.create(cr,uid,value_s2)
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
                        
                    res3 = self.get_account_amount(cr,uid,payroll_workers_id)
                    
                    journal_s3_line = [(0,0,{
                                    'name':line.year, 
                                    'account_id': wages_acc,
                                    'debit':res3['gross'],
                                    'credit':0,
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': provident_acc,
                                    'debit':0,
                                    'credit':res3['provident'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': vpf_acc,
                                    'debit':0,
                                    'credit':res3['vpf'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': welfare_acc,
                                    'debit':0,
                                    'credit':res3['welfare'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lic_premium_acc,
                                    'debit':0,
                                    'credit':res3['lic_premium'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': pro_tax_acc,
                                    'debit':0,
                                    'credit':res3['tax'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lwf_acc,
                                    'debit':0,
                                    'credit':res3['lwf'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': other_insu_acc,
                                    'debit':0,
                                    'credit':res3['ins_oth'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': vvti_acc, 
                                    'debit':0,
                                    'credit':res3['vvt_loan'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': hdfc_acc,
                                    'debit':0,
                                    'credit':res3['vvt_hdfc'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': lic_hfl_acc,
                                    'debit':0,
                                    'credit':res3['hfl'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': sbt_acc,
                                    'debit':0,
                                    'credit':res3['sbt'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': other_loan_acc,
                                    'debit':0,
                                    'credit':res3['other'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': tmb_acc,
                                    'debit':0,
                                    'credit':res3['tmb'],
                                   }),(0,0,{
                                    'name':line.year, 
                                    'account_id': wages_payable_acc,
                                    'debit':0,
                                    'credit':res3['diff'],
                                   }),]
                value_s3={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': time.strftime('%Y-%m-%d'),
                    'line_id': journal_s3_line,
                    'doc_type':'worker_payroll'
                    }
                new_s3_jour_id = account_move_obj.create(cr,uid,value_s3)
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
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(mrp_production, self).write(cr, uid,ids, vals, context)
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        journal_line = []
        credit = 0
        price = 0
        for line in self.browse(cr,uid,ids):
            sql = '''
                    select id from account_journal
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            date_period = line.date_planned,
            sql = '''
                select id from account_period where '%s' between date_start and date_stop
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            for period_id in period_obj.browse(cr,uid,period_ids):
        
                if 'state' in vals and line.state=='done':
                    for mat in line.move_lines2:
                        avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mat.product_id.id),('warehouse_id','=',line.location_src_id.id)])
                        if avg_cost_ids:
                            avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                            unit = avg_cost_id.avg_cost
                            cost = unit * mat.product_qty
                            price += cost
                            if cost:
                                if mat.product_id.purchase_acc_id:
                                    journal_line.append((0,0,{
                                                    'name':mat.product_id.code, 
                                                    'account_id': mat.product_id.purchase_acc_id and mat.product_id.purchase_acc_id.id,
                                                    'debit':cost,
                                                    'credit':0,
                                                   }))
                                else:
                                    raise osv.except_osv(_('Warning!'),_("Purchase GL Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.code))
                    for act in line.bom_id.activities_line:
                        if act.activities_id.act_acc_id:
                            credit += act.product_cost
                            journal_line.append((0,0,{
                                                    'name':act.activities_id.code, 
                                                    'account_id': act.activities_id.act_acc_id and act.activities_id.act_acc_id.id,
                                                    'debit':act.product_cost or 0,
                                                    'credit':0,
                                                   }))
                        else:
                            raise osv.except_osv(_('Warning!'),_("Activity Account is not configured for Activity '%s'! Please configured it!")%(act.activities_id.code))
                    credit += price
                    if credit:
                        if line.product_id.product_asset_acc_id:
                            journal_line.append((0,0,{
                                                    'name':line.product_id.code, 
                                                    'account_id': line.product_id.product_asset_acc_id and line.product_id.product_asset_acc_id.id,
                                                    'debit': 0,
                                                    'credit':credit ,
                                                   }))
                        else:
                            raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(line.product_id.code))
                    value={
                                'journal_id':journal_ids[0],
                                'period_id':period_id.id ,
                                'doc_type':'product',
                                'date': time.strftime('%Y-%m-%d'),
                                'line_id': journal_line,
                            }
                    new_jour_id = account_move_obj.create(cr,uid,value)
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
                                  ('worker_payroll', 'Workers Payroll')],'Document Type'),     
                                  
                }
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
    _columns = {
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
        'tds_id': fields.many2one('account.tax', 'TDS %'),
        'vendor_type': fields.selection([('manu', 'Manufacturer'),('trade', 'Traders'),('first_stage', 'First Stage'),('Import', 'import')],'Vendor Type'),
        }
    _defaults = {
        'vendor_code':'/',
    }
    
    def _check_vendor_code(self, cr, uid, ids, context=None):
        for vendor in self.browse(cr, uid, ids, context=context):
            if vendor.vendor_code:
                vendor_ids = self.search(cr, uid, [('id','!=',vendor.id),('vendor_code','=',vendor.vendor_code)])
                if vendor_ids:  
                    raise osv.except_osv(_('Warning!'),_('The Vendor Code must be unique!'))
                    return False
        return True
    _constraints = [
        (_check_vendor_code, 'Identical Data', []),
    ]
    
    def create(self, cr, uid, vals, context=None):
        if 'customer' in vals and vals['customer']:
            acc_obj = self.pool.get('account.account')
            acc_type_ids = self.pool.get('account.account.type').search(cr,uid, [('code','=','receivable')])
            if 'arulmani_type' in vals and vals['arulmani_type']=='export':
                acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119002')])
            if 'arulmani_type' in vals and vals['arulmani_type']=='domestic':
                acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119001')])
            if 'arulmani_type' in vals and vals['arulmani_type']=='indirect_export':
                acc_parent_ids = self.pool.get('account.account').search(cr,uid, [('code','=','0000119003')])
            acc_id = acc_obj.create(cr,uid,{
                'code':'0000' + vals['customer_code'],
                'name': vals['name'],
                'type':'receivable',
                'user_type':acc_type_ids[0],
                'parent_id':acc_parent_ids[0],
                                            })
            vals.update({'property_account_receivable':acc_id})
        if 'supplier' in vals and vals['supplier']:
            acc_obj = self.pool.get('account.account')
            acc_parent_ids = []
            acc_type_ids = self.pool.get('account.account.type').search(cr,uid, [('code','=','payable')])
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
            partner_ids = self.search(cr, uid, [('name','like',name)])
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
    }
    
res_currency_rate()
    
