# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"
   
    def _get_product_qty(self, cr, uid, context=None):
        """ To obtain product quantity
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return: Quantity
        """
        if context is None:
            context = {}
        prod = self.pool.get('mrp.production').browse(cr, uid,
                                context['active_id'], context=context)
        done = 0.0
        app_quantity = 0
        for move in prod.move_created_ids2:
            if move.product_id == prod.product_id:
                if not move.scrapped:
                    done += move.product_qty
        for line in prod.move_lines:
            app_quantity += line.app_quantity
        return app_quantity
   
    _defaults = {
         'product_qty': _get_product_qty,
         'mode': lambda *x: 'consume_produce'
    }
   
#     def do_produce(self, cr, uid, ids, context=None):
#         production_id = context.get('active_id', False)
#         assert production_id, "Production Id should be specified in context as a Active ID."
#         data = self.browse(cr, uid, ids[0], context=context)
#         if context is None:
#             context = {}
#         prod = self.pool.get('mrp.production').browse(cr, uid,
#                                 context['active_id'], context=context)
#         for line in prod.move_lines:
#             app_quantity = line.app_quantity
#             self.pool.get('mrp.production').action_produce(cr, uid, production_id,
#                             app_quantity, data.mode, context=context)
#             self.pool.get('stock.move').write(cr, uid, [line.id],{'app_quantity':line.product_qty-app_quantity})
#         return {}
   
mrp_product_produce()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
