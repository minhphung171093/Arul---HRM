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
     
     
      
#     def check_tax_lines(self, cr, uid, inv, compute_taxes, ait_obj):
#         company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id
#         if not inv.tax_line:
#             for tax in compute_taxes.values():
#                 ait_obj.create(cr, uid, tax)
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
#                 
#                 
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
                if inv.purchase_id:
                    iml += invoice_line_obj.move_line_amount_untaxed(cr, uid, inv.id) 
                else:
                    iml += invoice_line_obj.move_line_amount_untaxed_without_po(cr, uid, inv.id) 
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
  
            ctx.update(invoice=inv)
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move_obj.post(cr, uid, [move_id], context=ctx)
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
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['price_unit'],
                'quantity': 1,
                'price': basic,
                'account_id': purchase_acc_id and purchase_acc_id['purchase_acc_id'] or False,
                'account_analytic_id': t['account_analytic_id'],
                })
        return res
    
    def move_line_amount_untaxed_without_po(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            basic = (t['quantity'] * t['price_unit']) - ( (t['quantity'] * t['price_unit'])*t['disc']/100)
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['price_unit'],
                'quantity': 1,
                'price': basic,
                'account_id': t['gl_code_id'],
                'account_analytic_id': t['account_analytic_id'],
                })
        return res
     
    def move_line_customer_product_price(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            sql = '''
            SELECT purchase_acc_id FROM product_product WHERE id=%s and purchase_acc_id is not null
            '''%(t['product_id'])
            cr.execute(sql)
            purchase_acc_id = cr.dictfetchone()
            if not purchase_acc_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in Material master !'))
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['price_unit'],
                'quantity': 1,
                'price': t['price_unit']*t['quantity'],
                'account_id': purchase_acc_id and purchase_acc_id['purchase_acc_id'] or False,
                'account_analytic_id': t['account_analytic_id'],
            })
        return res
    def move_line_customer_excise_duty(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        account_line_ids = [r[0] for r in cr.fetchall()]
        for line in self.browse(cr,uid,account_line_ids):
#             cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
#             for account in cr.dictfetchall():
            ed_amount = (line.quantity * line.price_unit) * (line.invoice_id.excise_duty_id.amount and line.invoice_id.excise_duty_id.amount/100 or 1)
            sql = '''
                    SELECT cus_inv_ed_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_ed_id is not null
                '''
            cr.execute(sql)
            cus_inv_ed_id = cr.dictfetchone()
            if not cus_inv_ed_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            res.append({
                'type':'tax',
                'name':line.name,
                'price_unit': line.price_unit,
                'quantity': 1,
                'price':ed_amount,
                'account_id': cus_inv_ed_id and cus_inv_ed_id['cus_inv_ed_id'] or False,
                'account_analytic_id': line.account_analytic_id.id,
            })
        return res  
    def move_line_amount_tax(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
                tax = account['amount_tax']
#         invoice_ids = [r[0] for r in cr.fetchall()]
#         for invoice_line in self.browse(cr,uid,invoice_ids):
#             basic = (invoice_line.quantity * invoice_line.price_unit) - ( (invoice_line.quantity * invoice_line.price_unit)*invoice_line.disc/100)
#             if (invoice_line.p_f_type == '1'):
#                 p_f = basic * invoice_line.p_f/100
#             else:
#                 p_f = invoice_line.p_f
#             if invoice_line.ed_type == '1' :
#                 ed = (basic + p_f) * invoice_line.ed/100
#             else:
#                 ed = invoice_line.ed
#             
#             tax_amounts = [r.amount for r in invoice_line.invoice_line_tax_id]
#             tax = 0
#             for tax_amount in tax_amounts:
#                 tax += tax_amount/100
#             amount_total_tax = (basic + p_f + ed)*(tax)
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
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': tax,
                        'account_id': account,
                        'account_analytic_id': t['account_analytic_id'],
                    })
                else :
                        raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
                break
            break
        return res
    
    def move_line_customer_amount_tax(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            cr.execute('SELECT * FROM account_invoice WHERE id=%s', (invoice_id,))
            for account in cr.dictfetchall():
                tax = account['amount_tax']
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
                    res.append({
                        'type':'tax',
                        'name':t['name'],
                        'price_unit': t['price_unit'],
                        'quantity': 1,
                        'price': tax,
                        'account_id': account,
                        'account_analytic_id': t['account_analytic_id'],
                    })
                else :
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
                break
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
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': account['fright'],
                    'account_id': sup_inv_fright_id and sup_inv_fright_id['sup_inv_fright_id'] or False,
                    'account_analytic_id': t['account_analytic_id'],
                })
                break
            break
        return res 
    def move_line_customer_fright(self, cr, uid, invoice_id):
        res = []
        cr.execute('SELECT * FROM account_invoice_line WHERE invoice_id=%s', (invoice_id,))
        for t in cr.dictfetchall():
            sql = '''
                    SELECT cus_inv_fright_id FROM tpt_posting_configuration WHERE name = 'cus_inv' and cus_inv_fright_id is not null
                '''
            cr.execute(sql)
            cus_inv_fright_id = cr.dictfetchone()
            if not cus_inv_fright_id:
                raise osv.except_osv(_('Warning!'),_('Account is not null, please configure it in GL Posting Configrution !'))
            res.append({
                'type':'tax',
                'name':t['name'],
                'price_unit': t['price_unit'],
                'quantity': 1,
                'price': t['freight'],
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
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': account['excise_duty'],
                    'account_id': sup_inv_ed_id and sup_inv_ed_id['sup_inv_ed_id'] or False,
                    'account_analytic_id': t['account_analytic_id'],
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
                res.append({
                    'type':'tax',
                    'name':t['name'],
                    'price_unit': t['price_unit'],
                    'quantity': 1,
                    'price': account['p_f_charge'],
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

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'purchase_acc_id': fields.many2one('account.account', 'Purchase GL Account'),
        'sale_acc_id': fields.many2one('account.account', 'Sales GL Account'),
        'product_asset_acc_id': fields.many2one('account.account', 'Product Asset Account'),
        'product_cose_acc_id': fields.many2one('account.account', 'Product Cost of Goods Sold Account'),
        }
    
product_product()
    