# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class batch_wise_movement_analysis(osv.osv_memory):
    _name = "batch.wise.movement.analysis"
    _columns = {
            'production_date_from': fields.date('Production Date From:'),
            'production_date_to': fields.date('To:'),
            'batch_date_from': fields.date('Batch Date From:'),
            'batch_date_to': fields.date('To:'),
            'deliver_date_from': fields.date('Delivery Date From :'),
            'deliver_date_to': fields.date('To:'),
            'do_id': fields.many2one('stock.picking.out','DO Number'),
            'storage_from': fields.integer('Storage Days Range From :'),
            'storage_to': fields.integer('To:'),
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'batch.wise.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_batch_wise_movement_analysis', 'datas': datas}   
     

batch_wise_movement_analysis()
