# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import openerp.addons.decimal_precision as dp

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
        if context.get('tpt_issue',False):
            price = 0.0
            product_price = 0.0
            account_move_obj = self.pool.get('account.move')
            period_obj = self.pool.get('account.period')
            journal_obj = self.pool.get('account.journal')
            avg_cost_obj = self.pool.get('tpt.product.avg.cost')
            journal_line = []
            dest_id = False
            move_obj = self.pool.get('stock.move')
#             line = self.pool.get('tpt.material.issue').browse(cr, uid, context['active_id'])
            for line in self.pool.get('tpt.material.issue').browse(cr, uid, context['active_ids']):
                date_period = line.date_expec
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
                    
                    for mater in line.material_issue_line:
        #                 price += mater.product_id.standard_price * mater.product_isu_qty
                        acc_expense = mater.product_id and mater.product_id.property_account_expense and mater.product_id.property_account_expense.id or False
                        acc_asset = mater.product_id and mater.product_id.product_asset_acc_id and mater.product_id.product_asset_acc_id.id or False
                        if not acc_expense or not acc_asset:
                            raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for all materials!'))
                        avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                        if avg_cost_ids:
                            avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                            unit = avg_cost_id.avg_cost or 0
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
                    vals={
                        'journal_id':journal_ids[0],
                        'period_id':period_id.id ,
                        'ref': line.doc_no,
                        'date': date_period,
                        'material_issue_id': line.id,
                        'line_id': journal_line,
                        'doc_type':'good'
                        }
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