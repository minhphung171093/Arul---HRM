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
        'type': fields.selection([('approve','Approve'),('reject','Reject')]),
        'quantity': fields.float('Quantity', required=True, degits=(16,3)),
        'inspection_quantity': fields.float('Inspection Quantity', degits=(16,3)),
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
                   
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
#             move_obj.action_done(cr, uid, [line.need_inspec_id.id])
            if line.remaining_qty==wizard.quantity:
                inspection_obj.write(cr, uid, [line.id], {'state':'done'})
            else:
                inspection_obj.write(cr, uid, [line.id], {'state':'remaining','remaining_qty': line.remaining_qty-wizard.quantity})
                
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
            
        parent_dest_ids = locat_obj.search(cr, uid, [('name','=','Blocked List'),('usage','=','view')])
        if not parent_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Blocked List warehouse, please check it!'))
        location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Blocked List','Block List']),('location_id','=',parent_dest_ids[0])])
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
                  
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
            if line.remaining_qty==wizard.quantity:
                inspection_obj.write(cr, uid, [line.id], {'state':'done'})
            else:
                inspection_obj.write(cr, uid, [line.id], {'state':'remaining','remaining_qty': line.remaining_qty-wizard.quantity})
        return {'type': 'ir.actions.act_window_close'}
    
approve_reject_quanlity_inspection()



