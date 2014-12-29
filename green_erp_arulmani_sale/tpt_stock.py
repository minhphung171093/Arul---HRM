# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar
import openerp.addons.decimal_precision as dp

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'cons_loca':fields.char('Consignee Location', size = 64),
        'warehouse':fields.char('Warehouse', size = 64),
        'transporter':fields.char('Transporter Name', size = 64),
        'truck':fields.char('Truck Number', size = 64),
        'remarks':fields.text('Remarks'),
        'doc_status':fields.selection([('completed','Completed')],'Document Status'),
                }
    
stock_picking()

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'cons_loca':fields.char('Consignee Location', size = 64),
        'warehouse':fields.char('Warehouse', size = 64),
        'transporter':fields.char('Transporter Name', size = 64),
        'truck':fields.char('Truck Number', size = 64),
        'remarks':fields.text('Remarks'),
        'doc_status':fields.selection([('completed','Completed')],'Document Status'),
                }
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = "stock.move"
    def get_phy_batch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for physical in self.browse(cr, uid, ids, context=context):
            res[physical.id] = {
                'phy_batch': physical.prodlot_id and physical.prodlot_id.phy_batch_no or False,
            }
        return res
    _columns = {
#         'name': fields.char('Movement ID', size = 1024, required=True),
#         'warehouse_id': fields.many2one('stock.location', 'Source Warehouse'),
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),  
#         'do_ref_id': fields.many2one('stock.picking.out','DO Reference'),   
        'application_id': fields.many2one('crm.application','Application'),   
        'prodlot_id': fields.many2one('stock.production.lot', 'System Serial No.', states={'done': [('readonly', True)]}, help="Serial number is used to put a serial number on the production", select=True), 
#         'sys_batch':fields.many2one('stock.production.lot','System Serial No.'), 
#         'phy_batch':fields.char('Physical Batch No.', size = 1024)
        'phy_batch':fields.function(get_phy_batch,type='char', size = 1024,string='Physical Serial No.',multi='sum',store=True),
#         'reason': fields.text("Reason for move"),
#         'product_id': fields.many2one('product.product', 'Product', required=False, select=True, domain=[('type','<>','service')],states={'done': [('readonly', True)]}),
#         'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=False,states={'done': [('readonly', True)]}),
                }
#     _defaults = {
#         'name': '/',
#     }
#     
#     def create(self, cr, uid, vals, context=None):
#         if vals.get('name','/')=='/':
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.stock.move.import') or '/'
#         return super(stock_move, self).create(cr, uid, vals, context=context)
    
stock_move()
