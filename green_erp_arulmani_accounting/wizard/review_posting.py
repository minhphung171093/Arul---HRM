# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import openerp.addons.decimal_precision as dp

# class review_posting(osv.osv_memory):
#     _name = "review.posting"
#     _inherit = "account.move"
#     
#     def default_get(self, cr, uid, fields, context=None):
#         if context is None:
#             context = {}
#         res = super(review_posting, self).default_get(cr, uid, fields, context=context)
#         context.update({'tpt_review_posting':True})
#         if context.get('tpt_invoice',False):
#             vals = self.pool.get('account.invoice').action_move_create(cr, uid, context['active_ids'], context)
#             res.update(vals)
#         return res
#     _columns = {
#         'line_id': fields.one2many('review.posting.line', 'move_id', 'Entries', states={'posted':[('readonly',True)]}),
#     }
# review_posting()
# 
# class review_posting_line(osv.osv_memory):
#     _name = "review.posting.line"
#     _inherit = "account.move.line"
#     _columns = {
#         'move_id': fields.many2one('review.posting', 'Review Posting', ondelete='cascade'),
#     }
# review_posting()
class review_posting(osv.osv_memory):
    _name = "review.posting"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(review_posting, self).default_get(cr, uid, fields, context=context)
        context.update({'tpt_review_posting':True})
        if context.get('tpt_invoice',False):
            vals = self.pool.get('account.invoice').action_move_create(cr, uid, context['active_ids'], context)
            res.update(vals)
        if context.get('tpt_voucher',False):
            voucher_obj = self.pool.get('account.voucher')
            voucher_id = context['active_id']
            voucher = voucher_obj.browse(cr, uid, voucher_id)
            vals = voucher_obj.account_move_get(cr, uid, voucher_id, context)
            move_line = []
            line_total = 0
            if voucher.type_trans:
                if voucher.type_trans == 'payment':
                    rs = voucher_obj.first_move_line_get(cr,uid,voucher_id, False, False, False, context)
                    move_line.append((0,0,rs))
                    line_total = rs['debit'] - rs['credit']
                rec_list_ids = []
                line_total, rec_list_ids,tpt_move_line = voucher_obj.voucher_move_line_create(cr, uid, voucher_id, line_total, False, False, False, context)
                move_line += tpt_move_line
                if voucher.type_trans == 'receipt':
                    ml_writeoff = voucher_obj.writeoff_move_line_get(cr, uid, voucher.id, line_total, False, False, False, False, context)
                    if ml_writeoff:
                        move_line.append((0,0,ml_writeoff))
#phuoc
            else:
                if not voucher.line_cr_ids or not voucher.line_dr_ids or voucher.writeoff_amount!=0:
                    if voucher.type_cash_bank != 'journal':
                        rs = voucher_obj.first_move_line_get(cr,uid,voucher_id, False, False, False, context)
                        move_line.append((0,0,rs))
                        line_total = rs['debit'] - rs['credit']
                rec_list_ids = []
                if voucher.type == 'sale':
                    line_total = line_total - voucher_obj._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context)
                elif voucher.type == 'purchase':
                    line_total = line_total + voucher_obj._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context)
    #             Create one move line per voucher line where amount is not 0.0
                
                line_total, rec_list_ids,tpt_move_line = voucher_obj.voucher_move_line_create(cr, uid, voucher_id, line_total, False, False, False, context)
                move_line += tpt_move_line
                # Create the writeoff line if needed
                if voucher.type_cash_bank != 'journal':
                    ml_writeoff = voucher_obj.writeoff_move_line_get(cr, uid, voucher.id, line_total, False, False, False, False, context)
                    if ml_writeoff:
                        move_line.append((0,0,ml_writeoff))
            
            vals['line_id'] = move_line
            res.update(vals)    
        return res

    _columns = {
        'line_id': fields.one2many('review.posting.line', 'move_id', 'Entries'),
        'period_id': fields.many2one('account.period', 'Period'),
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
                                  ('worker_payroll', 'Workers Payroll')],'Document Type'), 
        'ref': fields.char('Reference', size=64),
        'date': fields.date('Date'),
    }
    
review_posting()

class review_posting_line(osv.osv_memory):
    _name = "review.posting.line"
    
    _columns = {
        'move_id': fields.many2one('review.posting', 'Review Posting', ondelete='cascade'),
        'name': fields.char('Name', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', select=1, ondelete='restrict'),
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
        'date_maturity': fields.date('Due date', select=True),
        'debit': fields.float('Debit', digits_compute=dp.get_precision('Account')),
        'credit': fields.float('Credit', digits_compute=dp.get_precision('Account')),
        'amount_currency': fields.float('Amount Currency', help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits_compute=dp.get_precision('Account')),
        'currency_id': fields.many2one('res.currency', 'Currency', help="The optional other currency if it is a multi-currency entry."),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Account', help="The Account can either be a base tax code or a tax code account."),
        'tax_amount': fields.float('Tax/Base Amount', digits_compute=dp.get_precision('Account'), select=True, help="If the Tax account is a tax code account, this field will contain the taxed amount.If the tax account is base tax code, "\
                    "this field will contain the basic amount(without tax)."),
        'reconcile_id': fields.many2one('account.move.reconcile', 'Reconcile', readonly=True, ondelete='set null', select=2),
        'reconcile_partial_id': fields.many2one('account.move.reconcile', 'Partial Reconcile', readonly=True, ondelete='set null', select=2),
        'state': fields.selection([('draft','Unbalanced'), ('valid','Balanced')], 'Status', readonly=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
    }
review_posting_line()
