# -*- coding: utf-8 -*-
""" 
TPT - By P.Vinothkumar  - on 23/01/2016
Sales VAT Report : Display the Sales VAT  values for the selected date range
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class sales_vatreport(osv.osv_memory):
    _name = "sales.vatreport"
    _columns = {
                'date_from': fields.date('From Date', required = True),
                'date_to': fields.date('To Date', required = True),   
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sales.vatreport'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'rpt_salesvatreport', 'datas': datas}
    
    
sales_vatreport()

