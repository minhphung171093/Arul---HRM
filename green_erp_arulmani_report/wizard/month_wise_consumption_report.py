# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class month_wise_consumption_wizard(osv.osv_memory):
    _name = "month.wise.consumption.wizard"
    
    _columns = {
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
        'bom_ids': fields.many2many('mrp.bom', 'mrp_bom_month_wise_consumption_ref', 'bom_id', 'month_wise_consumption_id', 'Norms'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'month.wise.consumption.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'month_wise_consumption_report', 'datas': datas}
        
month_wise_consumption_wizard()
