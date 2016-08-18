# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class alert_warning_form_purchase(osv.osv_memory):
    _name = "alert.warning.form.purchase"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(alert_warning_form_purchase, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            po_line = self.pool.get('purchase.order.line').browse(cr, uid, context['active_id'], context=context)
            ton_sl = 0
            mess = ''
            if po_line.product_id:
                if po_line.product_id.categ_id.cate_name != 'consum':
                    sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id=%s and st.location_dest_id in (select id from stock_location
                                                                                                where usage = 'internal')
                                    union all
                                    select st.product_qty*-1
                                        from stock_move st 
                                        where st.state='done' and st.product_id=%s and st.location_id in (select id from stock_location
                                                                                                where usage = 'internal')
                                    )foo
                    '''%(po_line.product_id.id,po_line.product_id.id)
                    cr.execute(sql)
                    ton_sl = cr.dictfetchone()['ton_sl']
                    mess = 'Current Stock Position of product %s (%s) is %s %s'%(po_line.product_id.name,po_line.product_id.default_code,ton_sl,po_line.product_uom.name)
                else:
                    mess = 'The system does not manage quantity on stock for Consumable Product!'
            res.update({'name': mess})
        return res
    
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                }
alert_warning_form_purchase()

class approve_reject_quanlity_inspection(osv.osv_memory):
    _name = "approve.reject.quanlity.inspection"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(approve_reject_quanlity_inspection, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id',False):
            inspection_obj = self.pool.get('tpt.quanlity.inspection')
            inspection = inspection_obj.browse(cr, uid, context.get('active_id'))
            res.update({'quantity':inspection.remaining_qty,'inspection_quantity':inspection.remaining_qty})
        return res
    
    _columns = {    
        'type': fields.selection([('approve','Approved'),('reject','Reject')]),
        'quantity': fields.float('Quantity', required=True, digits=(16,3)),
        'inspection_quantity': fields.float('Inspection Quantity', digits=(16,3)),
    }
    
    def onchange_quantity(self, cr, uid, ids,quantity=False,inspection_quantity=False, context=None):
        vals = {}
        if quantity and inspection_quantity and quantity>inspection_quantity:
            warning = {  
                      'title': _('Warning!'),  
                      'message': _('Can not choose Quantity greater than Remaining Quantity'),  
                      }  
            vals['quantity']=inspection_quantity
            return {'value': vals,'warning':warning}
        return {'value': vals}
    
    def bt_approve(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0])
        move_obj = self.pool.get('stock.move')
        inspection_obj = self.pool.get('tpt.quanlity.inspection')
        inspection_ids = context.get('active_ids',[])
        locat_obj = self.pool.get('stock.location')
        location_id = False
        location_dest_id = False
        parent_ids = locat_obj.search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
        if not parent_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection warehouse, please check it!'))
        locat_ids = locat_obj.search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
        if not locat_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection  location in Quality Inspection  warehouse, please check it!'))
        else:
            location_id = locat_ids[0]
             
        parent_dest_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
        if not parent_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
        
        for line in inspection_obj.browse(cr,uid,inspection_ids):
            
            if line.product_id.categ_id.cate_name=='raw':
                location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_dest_ids[0])])
            if line.product_id.categ_id.cate_name=='spares':
                location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Spares','Spare','spares','spare']),('location_id','=',parent_dest_ids[0])])
            if not location_dest_ids:
                raise osv.except_osv(_('Warning!'),_('System does not have Raw Material location in Store warehouse, please check it!'))
            else:
                location_dest_id = location_dest_ids[0]
            
            rs = {
                  'name': '/',
                  'product_id':line.product_id and line.product_id.id or False,
                  'product_qty':wizard.quantity,
                  'product_uom':line.product_id.uom_po_id and line.product_id.uom_po_id.id or False,
                  'location_id':location_id,
                  'location_dest_id':location_dest_id,
                  'inspec_id':line.id,
                  'date':line.date,
                  'price_unit':line.price_unit or 0,
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
#             move_obj.action_done(cr, uid, [line.need_inspec_id.id])
            
            #TPT-BM on 18/08/2016-TO CREATE GRN POSTING ENTRY FROM QUALITY INSPECTION FOR EVRY TIME QTY GET APPROVED
            journal_line = []
            date_period = line.date,
            sql = '''
                select id from account_period where special = False and '%s' between date_start and date_stop and special is False
             
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            #to get journal id 
            sql_journal = '''
            select id from account_journal
            '''
            cr.execute(sql_journal)
            journal_ids = [r[0] for r in cr.fetchall()]
            journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
            #for seq generation
            sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'grn.posting.account')
            name = sequence and sequence+'/'+fiscalyear['code'] or '/'
            temp_flag = False
            account_move_obj = self.pool.get('account.move')
            grn_obj = self.pool.get('stock.picking')
            for grn_line in line.name.move_lines:
                if grn_line.action_taken=='need':
                    amount_cer = grn_line.purchase_line_id.price_unit * wizard.quantity
                    credit = amount_cer - (amount_cer*grn_line.purchase_line_id.discount)/100
                    debit = amount_cer - (amount_cer*grn_line.purchase_line_id.discount)/100                    
                    if grn_line.purchase_line_id and grn_line.purchase_line_id.taxes_id:
                        description = [r.description for r in grn_line.purchase_line_id.taxes_id]
                        tax_amounts = [r.amount for r in grn_line.purchase_line_id.taxes_id]
                        tax_amt = 0
                        if description:
                            description = description[0]
                            if 'CST' in description :
                                for tax in tax_amounts:
                                    tax_amt = tax
                                pf_type = grn_line.purchase_line_id.p_f_type
                                pf = grn_line.purchase_line_id.p_f
                                ed_type = grn_line.purchase_line_id.ed_type
                                ed = grn_line.purchase_line_id.ed
                                excise_duty = 0.00
                                basic = (grn_line.purchase_line_id.product_qty * grn_line.purchase_line_id.price_unit) - ( (grn_line.purchase_line_id.product_qty * grn_line.purchase_line_id.price_unit)*grn_line.purchase_line_id.discount/100)
                                if pf_type == '1' :
                                    p_f = basic * pf/100
                                elif pf_type == '2' :
                                    p_f = pf
                                elif pf_type == '3':
                                    p_f = pf * grn_line.purchase_line_id.product_qty
                                else:
                                    p_f = pf                                
                                if ed_type == '1' :
                                    ed = (basic + p_f) * ed/100
                                elif ed_type == '2' :
                                    ed = ed
                                elif ed_type == '3' :
                                    ed = ed *  grn_line.purchase_line_id.product_qty
                                else:
                                    ed = ed
                                excise_duty += ed
                                cst_cr_amt = (credit + excise_duty + p_f)*tax_amt/100    
                                cst_dr_amt = (debit + excise_duty + p_f)*tax_amt/100                                
                                credit += cst_cr_amt
                                debit += cst_dr_amt
                    #
                    if not grn_line.product_id.product_asset_acc_id:
                        raise osv.except_osv(_('Warning!'),_('You need to define Product Asset GL Account for this product'))
                    journal_line.append((0,0,{
                        'name':grn_line.name + ' - ' + grn_line.product_id.name, 
                        'account_id': grn_line.product_id.product_asset_acc_id and grn_line.product_id.product_asset_acc_id.id,
                        'partner_id': line.name.partner_id and line.name.partner_id.id or False,
                        'credit':0,
                        'debit':debit,
                        'product_id':grn_line.product_id.id,
                    }))
                    
                    if not line.product_id.purchase_acc_id:
                        raise osv.except_osv(_('Warning!'),_('You need to define Purchase GL Account for this product'))
                    journal_line.append((0,0,{
                        'name':line.name.name + ' - ' + grn_line.product_id.name, 
                        'account_id': grn_line.product_id.purchase_acc_id and grn_line.product_id.purchase_acc_id.id,
                        'partner_id': line.name.partner_id and line.name.partner_id.id or False,
                        'credit':credit,
                        'debit':0,
                        'product_id':grn_line.product_id.id,
                    }))
                    value={
                    'journal_id':journal.id,
                    'period_id':period_ids[0] ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type':'grn',
                    'grn_id':line.id,
                    'ref': line.name.name,
                    'name':name, 
                    }
                    new_jour_id = account_move_obj.create(cr,uid,value)
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id.grn:
                            try:
                                account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                            except:
                                pass
            #tpt-end
            
            if line.remaining_qty==wizard.quantity or wizard.inspection_quantity==wizard.quantity:
                qty_approve = line.qty_approve
                qty_approve += wizard.quantity
                inspection_obj.write(cr, uid, [line.id], {'state':'done','remaining_qty':0,'qty_approve':qty_approve})
            else:
                qty_approve = line.qty_approve
                qty_approve += wizard.quantity
                inspection_obj.write(cr, uid, [line.id], {'state':'remaining','remaining_qty': line.remaining_qty-wizard.quantity,'qty_approve':qty_approve})
                
        return {'type': 'ir.actions.act_window_close'}
    
    def bt_reject(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0])
        move_obj = self.pool.get('stock.move')
        inspection_obj = self.pool.get('tpt.quanlity.inspection')
        inspection_ids = context.get('active_ids',[])
        locat_obj = self.pool.get('stock.location')
        location_id = False
        location_dest_id = False
        parent_ids = locat_obj.search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
        if not parent_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection warehouse, please check it!'))
        locat_ids = locat_obj.search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
        if not locat_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection  location in Quality Inspection  warehouse, please check it!'))
        else:
            location_id = locat_ids[0]
            
        parent_dest_ids = locat_obj.search(cr, uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
        if not parent_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Blocked List warehouse, please check it!'))
        location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_dest_ids[0])])
        if not location_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Blocked List location in Blocked List warehouse, please check it!'))
        else:
            location_dest_id = location_dest_ids[0]
        for line in inspection_obj.browse(cr,uid,inspection_ids):
            rs = {
                  'name': '/',
                  'product_id':line.product_id and line.product_id.id or False,
                  'product_qty':wizard.quantity,
                  'product_uom':line.product_id.uom_po_id and line.product_id.uom_po_id.id or False,
                  'location_id':location_id,
                  'location_dest_id':location_dest_id,
                  'inspec_id':line.id,
                  'date':line.date,
                  'price_unit':line.price_unit or 0,
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
            if line.remaining_qty==wizard.quantity or wizard.inspection_quantity==wizard.quantity:
                inspection_obj.write(cr, uid, [line.id], {'state':'done','remaining_qty':0})
            else:
                inspection_obj.write(cr, uid, [line.id], {'state':'remaining','remaining_qty': line.remaining_qty-wizard.quantity})
        return {'type': 'ir.actions.act_window_close'}
    
approve_reject_quanlity_inspection()

class pr_cancel(osv.osv_memory):
    _name = "pr.cancel"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                'reason': fields.char('Reason', size=1024, ),
                }
    
    def action_confirm(self, cr, uid, ids, context=None): 
        audit_id = context.get('audit_id')
        do_obj = self.pool.get('tpt.purchase.product').browse(cr, uid, audit_id)
        popup_id = self.pool.get('pr.cancel').browse(cr, uid, ids[0])
        reason = popup_id.reason
        
        space_removed = reason.replace(" ", "")
        if space_removed == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the Reason!'))
        
        sql = ''' update tpt_purchase_product set reason_for_cancel='%s',state='cancel_by_purchase' where id=%s
        '''%(reason,audit_id)
        cr.execute(sql) 
        
        return {'type': 'ir.actions.act_window_close'}   
    
    
pr_cancel()


class pr_copy(osv.osv_memory):
    _name = "pr.copy"
    _columns = { 
                'message': fields.text(string="Message ", readonly=True),       
                'copied_pr_id': fields.many2one('tpt.purchase.indent','Newly Copied PR', ondelete='cascade'),                
                }
    
pr_copy()

class po_close(osv.osv_memory):
    _name = "po.close"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                'reason': fields.char('Reason', size=1024, ),
                }
    
    def bt_close(self, cr, uid, ids, context=None): 
        audit_id = context.get('audit_id')
        po_obj = self.pool.get('purchase.order').browse(cr, uid, audit_id)
        popup_id = self.pool.get('po.close').browse(cr, uid, ids[0])
        reason = popup_id.reason
        
        space_removed = reason.replace(" ", "")
        if space_removed == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the Reason!'))
        
        sql = ''' update purchase_order set reason_for_close='%s',state='close' where id=%s
        '''%(reason,audit_id)
        cr.execute(sql) 
        
        return {'type': 'ir.actions.act_window_close'}   
    
    
po_close()