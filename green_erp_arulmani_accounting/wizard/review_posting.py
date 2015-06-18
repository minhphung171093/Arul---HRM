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
        if context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'worker' and context.get('get_tpt_payroll',False) and context.get('get_tpt_payroll',False) == 'worker':
            vals = self.pool.get('tpt.hr.payroll.approve.reject').approve_payroll(cr, uid, context['active_ids'], context)
            res.update(vals)
        if context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'excutive' and context.get('get_tpt_payroll',False) and context.get('get_tpt_payroll',False) == 'excutive':
            vals = self.pool.get('tpt.hr.payroll.approve.reject').approve_payroll(cr, uid, context['active_ids'], context)
            res.update(vals)
        if context.get('tpt_approve_payroll',False) and context.get('tpt_approve_payroll',False) == 'staff' and context.get('get_tpt_payroll',False) and context.get('get_tpt_payroll',False) == 'staff':
            vals = self.pool.get('tpt.hr.payroll.approve.reject').approve_payroll(cr, uid, context['active_ids'], context)
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
        if context.get('tpt_preview_grn',False): 
            account_move_obj = self.pool.get('account.move')
            period_obj = self.pool.get('account.period')
            for line in self.pool.get('stock.picking').browse(cr,uid,context['active_ids']):
                if line.type == 'in' and line.state=='done':
                    debit = 0.0
                    credit = 0.0
                    journal_line = []
                    for move in line.move_lines:
                        amount = move.purchase_line_id.price_unit * move.product_qty
                        debit += amount - (amount*move.purchase_line_id.discount)/100
                    date_period = line.date,
                    sql = '''
                        select id from account_period where special = False and '%s' between date_start and date_stop
                     
                    '''%(date_period)
                    cr.execute(sql)
                    period_ids = [r[0] for r in cr.fetchall()]
                    if not period_ids:
                        raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                     
                    for period_id in period_obj.browse(cr,uid,period_ids):
                        sql_journal = '''
                        select id from account_journal
                        '''
                        cr.execute(sql_journal)
                        journal_ids = [r[0] for r in cr.fetchall()]
                        journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                        for p in line.move_lines:
                            amount_cer = p.purchase_line_id.price_unit * p.product_qty
                            credit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                            debit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
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
                             
                        vals={
                            'journal_id':journal.id,
                            'period_id':period_id.id ,
                            'date': date_period,
                            'line_id': journal_line,
                            'doc_type':'grn'
                            }
                        res.update(vals)            
        if context.get('tpt_delivery',False): 
            account_move_obj = self.pool.get('account.move')
            period_obj = self.pool.get('account.period')
            for line in self.pool.get('stock.picking').browse(cr,uid,context['active_ids']):
           
                if line.type == 'out' and line.state=='done':
                    debit = 0.0
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
                            if p.prodlot_id:
                                sale_id = p.sale_line_id and p.sale_line_id.order_id.id or False 
                                used_qty = p.product_qty or 0
                                if sale_id:
                                    sql = '''
                                        select id from tpt_batch_allotment where sale_order_id = %s
                                    '''%(sale_id)
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
                        
                        debit += p.sale_line_id and p.sale_line_id.price_unit * p.product_qty or 0
                        product_name = p.product_id.name
                        product_id = p.product_id.id
                        account = self.pool.get('stock.picking').get_pro_account_id(cr,uid,product_name,dis_channel)
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
                          
                    vals={
                        'journal_id':journal.id,
                        'period_id':period_id.id ,
                        'date': date_period,
                        'line_id': journal_line,
                        'doc_type':'do'
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
        if context.get('tpt_preview_mrp',False):
            account_move_obj = self.pool.get('account.move')
            period_obj = self.pool.get('account.period')
            journal_obj = self.pool.get('account.journal')
            avg_cost_obj = self.pool.get('tpt.product.avg.cost')
            mrp_obj = self.pool.get('mrp.production')
            journal_line = []
            credit = 0
            price = 0
            for line in mrp_obj.browse(cr,uid,context['active_ids']):
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
            
                    for mat in line.move_lines:
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
                    vals={
                                'journal_id':journal_ids[0],
                                'period_id':period_id.id ,
                                'doc_type':'product',
                                'date': time.strftime('%Y-%m-%d'),
                                'line_id': journal_line,
                            }
                    res.update(vals)
                    sql = '''
                        update mrp_production set produce_cost = %s where id=%s 
                    '''%(credit,line.id)
                    cr.execute(sql)
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