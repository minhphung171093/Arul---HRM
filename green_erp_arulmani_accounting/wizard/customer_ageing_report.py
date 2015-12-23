# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class customer_ageing_report(osv.osv_memory):
    _name = "customer.ageing.report"
    _columns = {
                'date_from': fields.date('As of Date: '),
                'customer_group': fields.selection([('export','Export'),
                                                   ('domestic','Domestic'),
                                                   ('indirect_export','Indirect Export')],
                                                    'Customer Group'),
                'customer_id': fields.many2one('res.partner','Customer'),
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'customer.aging.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'customer_ageing_report', 'datas': datas}
    
    
customer_ageing_report()

