# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class load_line_from_norm(osv.osv_memory):
    _name = "load.line.from.norm"
    _columns = {    
                'bom_id':fields.many2one('mrp.bom','Norm',required=True),
                'message': fields.text(string="Message ", readonly=True),  
                }
            
    def tick_ok(self, cr, uid, ids, context=None):
        tick = self.browse(cr, uid, ids[0])
        material_req_id = context.get('active_id')
        material_req = self.pool.get('tpt.material.request').browse(cr, uid, material_req_id)
        materials = []
        for line in tick.bom_id.bom_lines:
            materials.append((0,0,{
                  'product_id': line.product_id and line.product_id.id or False,
                  'dec_material': line.product_id and line.product_id.name or '',
                  }))
        self.pool.get('tpt.material.request').write(cr,uid,[material_req.id],{
                                                             'material_request_line': materials
                                                            })
        return True
        
load_line_from_norm()