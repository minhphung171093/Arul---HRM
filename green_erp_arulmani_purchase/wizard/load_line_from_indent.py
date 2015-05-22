# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class load_line_from_indent(osv.osv_memory):
    _name = "load.line.from.indent"
    _columns = {    
                'indent_id':fields.many2one('tpt.purchase.indent','Indent',required=True),
                'message': fields.text(string="Message ", readonly=True),  
                }
            
    def tick_ok(self, cr, uid, ids, context=None):
        tick = self.browse(cr, uid, ids[0])
        indent_line_id = context.get('active_id')
        indent_line = self.pool.get('tpt.request.for.quotation').browse(cr, uid, indent_line_id)
        lines = []
        for line in tick.indent_id.purchase_product_line:
            if line.state == '++' or line.state == 'rfq_raised' :
                lines.append((0,0,{
                  'po_indent_id': line.pur_product_id and line.pur_product_id.id or False,
                  'description': line.description,
                  'item_text': line.item_text,
                  'recom_vendor': line.recom_vendor,
                  'product_uom_qty': line.product_uom_qty - line.rfq_qty,
                  'uom_id': line.uom_po_id and line.uom_po_id.id or False ,
#                   'state': line.state,
                  'indent_line_id': line.id ,
                  'product_id':line.product_id.id and line.product_id.id or False,
                   
                  }))
        self.pool.get('tpt.request.for.quotation').write(cr,uid,[indent_line.id],{
                                                             'rfq_line': lines
                                                            })
        return True
        
load_line_from_indent()