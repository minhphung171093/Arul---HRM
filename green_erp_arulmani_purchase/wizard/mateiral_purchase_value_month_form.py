# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class mateiral_purchase_value_month(osv.osv_memory):
    _name = "mateiral.purchase.value.month"
    _columns = {
             'year': fields.many2one('account.fiscalyear','Year'),
             'material_cate':fields.many2one('product.category','Material Category:'),
             'material_ids': fields.many2many('product.product', 'material_ref_report', 'mate_pur_month_id', 'product_id', 'Material'),  
             'avg_value': fields.selection(
            [('0', '0'),            
            ('1', '1 to 5000'),
            ('5001', '5001 to 10000'),
            ('all', 'All'),],
            'Average Value'),
                             
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'grn.detail.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'grn_line_report_xls', 'datas': datas}   
     

mateiral_purchase_value_month()

