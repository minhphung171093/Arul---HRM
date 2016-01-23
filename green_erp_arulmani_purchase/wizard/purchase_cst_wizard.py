# -*- coding: utf-8 -*-
""" 
TPT - By P.Vinothkumar  - on 21/01/2016
Purchase CST Report : Display the Purchase CST values for the selected date range
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class purchase_cstreport(osv.osv_memory):
    _name = "purchase.cstreport"
    _columns = {
                'date_from': fields.date('From Date', required = True),
                'date_to': fields.date('To Date', required = True),   
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'purchase.cstreport'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'rpt_purchasecstreport', 'datas': datas}
    
    
purchase_cstreport()

