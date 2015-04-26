# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class batch_wise_stock(osv.osv_memory):
    _name = "batch.wise.stock"
    _columns = {    
                'product_id':fields.many2one('product.product','Product Code'),
                'location_id':fields.many2one('stock.location','Warehouse Location',required=True),
                'application_id':fields.many2one('crm.application','Application'),
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'batch.wise.stock'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'batch_wise_stock_report', 'datas': datas}
        
batch_wise_stock()