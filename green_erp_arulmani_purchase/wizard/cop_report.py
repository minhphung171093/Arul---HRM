# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class cop_report(osv.osv):
    _name = "cop.report"
    _columns = {    
        'product_id': fields.many2one('product.product', 'Material'),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
        'bom_ids': fields.many2many('mrp.bom', 'mrp_bom_cop_ref', 'cop_id', 'bom_id', 'Norms'),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'cop.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids': ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'cop_report', 'datas': datas}
    
cop_report()

