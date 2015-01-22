# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class tick_purchase_chart(osv.osv_memory):
    _name = "tick.purchase.chart"
    _columns = {    
                'po_document_type':fields.selection([('asset','VV Asset PO'),
                                                     ('standard','VV Standard PO'),
                                                     ('local','VV Local PO'),
                                                     ('return','VV Return PO'),
                                                     ('service','VV Service PO'),
                                                     ('out','VV Out Service PO')],'PO Document Type',required=True),
                'message': fields.text(string="Message ", readonly=True),    
                }
            
    def tick_ok(self, cr, uid, ids, context=None):
        purchase_line = []
        purchase_order_obj = self.pool.get('purchase.order')
        q_id = context.get('active_id')
        chart = self.pool.get('tpt.purchase.quotation').browse(cr, uid, q_id)
        location_ids=self.pool.get('stock.warehouse').search(cr, uid,[('company_id','=',chart.supplier_id.company_id.id)])
        location = self.pool.get('stock.warehouse').browse(cr, uid, location_ids[0])
        
        vals = purchase_order_obj.onchange_partner_id(cr, uid, [q_id],chart.supplier_id.id)['value']
        tick = self.browse(cr, uid, ids[0])
        
        for line in chart.purchase_quotation_line:
            purchase_line.append((0,0,{
                                        'po_indent_no':line.po_indent_id.id,
                                       'product_id':line.product_id.id,
                                       'product_qty':line.product_uom_qty,
                                       'product_uom':line.uom_po_id.id,
                                       'price_unit':line.price_unit,
                                        'name':'/',
                                       }))
        vals.update({
                    'po_document_type': tick.po_document_type,
                    'quotation_no':chart.id,
                    'partner_id':chart.supplier_id.id,
                    'partner_ref':chart.quotation_ref,
                    'purchase_tax_id':chart.tax_id.id,
                    'date_order':chart.date_quotation,
                    'location_id':location.lot_stock_id.id,
                    'invoice_method': 'picking',
                    'order_line': purchase_line,
                    })
        new_po_id = purchase_order_obj.create(cr, uid, vals)
        sql = '''
            update tpt_purchase_quotation set state = 'done' where id = %s
        '''%(chart.id)
        cr.execute(sql)
        
        
        
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'purchase', 'purchase_order_form')
        return {
                    'name': 'Purchase Order',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'purchase.order',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': new_po_id,
                }
        
tick_purchase_chart()