# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
import locale
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"
from openerp import netsvc

class tpt_auto_reconciliation(osv.osv_memory):
    _name = "tpt.auto.reconciliation"
    _columns = {
        'tpt_date_from': fields.date('Date From', required=True),
        'tpt_date_to': fields.date('Date To', required=True),
        'tpt_partner_ids': fields.many2many('res.partner', 'tpt_auto_recon_partner_ref', 'auto_recon_id', 'partner_id', 'Partners'),
    }
    
    def bt_customer_reconciliation(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        this = self.browse(cr, uid, ids[0])
        voucher_ids = []
        partner_ids = [r.id for r in this.tpt_partner_ids]
        if not partner_ids:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('customer','=',True)])
        journal = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'cash')])
        voucher_obj = self.pool.get('account.voucher')
        move_line_pool = self.pool.get('account.move.line')
        for partner_id in partner_ids:
            move_line_ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('date','>=',this.tpt_date_from), ('date','<=',this.tpt_date_to), ('account_id.type', '=', 'receivable'), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)])
            ctx = context
            ctx['move_line_ids'] = move_line_ids
            ctx['type'] = 'receipt'
            ctx['get_customer_reconcile'] = True
            voucher_vals = {
                'partner_id': partner_id,
                'journal_id': journal[0],
                'tpt_cus_reconcile': True,
                'type': 'receipt',
            }
            value = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal[0], 0, False, 'receipt', False, ctx)['value']
            cr_ids = value.get('line_cr_ids', [])
            dr_ids = value.get('line_dr_ids', [])
            line_cr_ids = []
            line_dr_ids = []
            
            total_cr = 0
            total_dr = 0
            
            for line_cr in cr_ids:
                total_cr += line_cr['amount_unreconciled']
            for line_dr in dr_ids:
                total_dr += line_dr['amount_unreconciled']
                
            remaining_amount = 0
                
            if total_cr>total_dr:
                remaining_amount = total_dr
                for line_dr in dr_ids:
                    new_line_dr = line_dr
                    new_line_dr['amount'] = line_dr['amount_unreconciled']
                    new_line_dr['reconcile'] = True
                    line_dr_ids.append((0,0,new_line_dr))
                
                for line_cr in cr_ids:
                    new_line_cr = line_cr
                    if remaining_amount and remaining_amount<line_cr['amount_unreconciled']:
                        new_line_cr['amount'] = remaining_amount
                        remaining_amount = 0
                        line_cr_ids.append((0,0,new_line_cr))
                    if remaining_amount and remaining_amount>=line_cr['amount_unreconciled']:
                        new_line_cr['amount'] = line_cr['amount_unreconciled']
                        new_line_cr['reconcile'] = True
                        remaining_amount = remaining_amount-line_cr['amount_unreconciled']
                        line_cr_ids.append((0,0,new_line_cr))
                
            if total_dr>total_cr:
                remaining_amount = total_cr
                for line_cr in cr_ids:
                    new_line_cr = line_cr
                    new_line_cr['amount'] = line_cr['amount_unreconciled']
                    new_line_cr['reconcile'] = True
                    line_cr_ids.append((0,0,new_line_cr))
                
                for line_dr in dr_ids:
                    new_line_dr = line_dr
                    if remaining_amount and remaining_amount<line_dr['amount_unreconciled']:
                        new_line_dr['amount'] = remaining_amount
                        remaining_amount = 0
                        line_dr_ids.append((0,0,new_line_dr))
                    if remaining_amount and remaining_amount>=line_dr['amount_unreconciled']:
                        new_line_dr['amount'] = line_dr['amount_unreconciled']
                        new_line_dr['reconcile'] = True
                        remaining_amount = remaining_amount-line_dr['amount_unreconciled']
                        line_dr_ids.append((0,0,new_line_dr))
                
            if line_cr_ids and line_dr_ids:
                value['line_cr_ids'] = line_cr_ids
                value['line_dr_ids'] = line_dr_ids
                voucher_vals.update(value)
                
                voucher_id = voucher_obj.create(cr, uid, voucher_vals, ctx)
                wf_service.trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
                voucher_ids.append(voucher_id)
                
        model_obj = self.pool.get('ir.model.data')
        model, tree_id = model_obj.get_object_reference(cr, uid, 
                                            'green_erp_arulmani_accounting', 'view_reconcile_tree')
        model, form_id = model_obj.get_object_reference(cr, uid, 
                                            'green_erp_arulmani_accounting', 'view_vendor_receipt_form_reconcile')
        return {
            'name': 'Customer Reconciliation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'),(form_id, 'form')],
            'res_model': 'account.voucher',
            'domain': [('id','in',voucher_ids)],
            'context': {},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
    
    def bt_supplier_reconciliation(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        this = self.browse(cr, uid, ids[0])
        voucher_ids = []
        partner_ids = [r.id for r in this.tpt_partner_ids]
        if not partner_ids:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('supplier','=',True)])
        journal = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'cash')])
        voucher_obj = self.pool.get('account.voucher')
        move_line_pool = self.pool.get('account.move.line')
        for partner_id in partner_ids:
            move_line_ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('date','>=',this.tpt_date_from), ('date','<=',this.tpt_date_to), ('account_id.type', '=', 'payable'), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)])
            ctx = context
            ctx['move_line_ids'] = move_line_ids
            ctx['type'] = 'payment'
            ctx['get_supp_reconcile'] = True
            voucher_vals = {
                'partner_id': partner_id,
                'journal_id': journal[0],
                'tpt_sup_reconcile': True,
                'type': 'payment',
            }
            value = voucher_obj.onchange_partner_id(cr, uid, [], partner_id, journal[0], 0, False, 'payment', False, ctx)['value']
            cr_ids = value.get('line_cr_ids', [])
            dr_ids = value.get('line_dr_ids', [])
            line_cr_ids = []
            line_dr_ids = []
            
            total_cr = 0
            total_dr = 0
            
            for line_cr in cr_ids:
                total_cr += line_cr['amount_unreconciled']
            for line_dr in dr_ids:
                total_dr += line_dr['amount_unreconciled']
                
            remaining_amount = 0
                
            if total_cr>total_dr:
                remaining_amount = total_dr
                for line_dr in dr_ids:
                    new_line_dr = line_dr
                    new_line_dr['amount'] = line_dr['amount_unreconciled']
                    new_line_dr['reconcile'] = True
                    line_dr_ids.append((0,0,new_line_dr))
                
                for line_cr in cr_ids:
                    new_line_cr = line_cr
                    if remaining_amount and remaining_amount<line_cr['amount_unreconciled']:
                        new_line_cr['amount'] = remaining_amount
                        remaining_amount = 0
                        line_cr_ids.append((0,0,new_line_cr))
                    if remaining_amount and remaining_amount>=line_cr['amount_unreconciled']:
                        new_line_cr['amount'] = line_cr['amount_unreconciled']
                        new_line_cr['reconcile'] = True
                        remaining_amount = remaining_amount-line_cr['amount_unreconciled']
                        line_cr_ids.append((0,0,new_line_cr))
                
            if total_dr>total_cr:
                remaining_amount = total_cr
                for line_cr in cr_ids:
                    new_line_cr = line_cr
                    new_line_cr['amount'] = line_cr['amount_unreconciled']
                    new_line_cr['reconcile'] = True
                    line_cr_ids.append((0,0,new_line_cr))
                
                for line_dr in dr_ids:
                    new_line_dr = line_dr
                    if remaining_amount and remaining_amount<line_dr['amount_unreconciled']:
                        new_line_dr['amount'] = remaining_amount
                        remaining_amount = 0
                        line_dr_ids.append((0,0,new_line_dr))
                    if remaining_amount and remaining_amount>=line_dr['amount_unreconciled']:
                        new_line_dr['amount'] = line_dr['amount_unreconciled']
                        new_line_dr['reconcile'] = True
                        remaining_amount = remaining_amount-line_dr['amount_unreconciled']
                        line_dr_ids.append((0,0,new_line_dr))
                
            if line_cr_ids and line_dr_ids:
                value['line_cr_ids'] = line_cr_ids
                value['line_dr_ids'] = line_dr_ids
                voucher_vals.update(value)
                
                voucher_id = voucher_obj.create(cr, uid, voucher_vals, ctx)
                wf_service.trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
                voucher_ids.append(voucher_id)
                
        model_obj = self.pool.get('ir.model.data')
        model, tree_id = model_obj.get_object_reference(cr, uid, 
                                            'green_erp_arulmani_accounting', 'view_reconcile_tree')
        model, form_id = model_obj.get_object_reference(cr, uid, 
                                            'green_erp_arulmani_accounting', 'view_vendor_payment_form_reconcile')
        return {
            'name': 'Supplier Reconciliation',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_id, 'tree'),(form_id, 'form')],
            'res_model': 'account.voucher',
            'domain': [('id','in',voucher_ids)],
            'context': {},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

tpt_auto_reconciliation()
