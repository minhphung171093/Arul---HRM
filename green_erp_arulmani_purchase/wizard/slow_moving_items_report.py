# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class slow_moving_items_report(osv.osv):
    _name = "slow.moving.items.report"
    _columns = {    
        'product_id': fields.many2one('product.product', 'Material'),
        'percentage_in_range_from':fields.selection([(num, str(num)) for num in range(0, 101)], 'Percentage in range from'),
        'percentage_in_range_to':fields.selection([(num, str(num)) for num in range(0, 101)], 'Percentage in range to'),
        'stock_value_from':fields.float('Stock value from'),
        'stock_value_to':fields.float('Stock value to'),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'slow.moving.items.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids': ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'slow_moving_items_report', 'datas': datas}
    
slow_moving_items_report()

