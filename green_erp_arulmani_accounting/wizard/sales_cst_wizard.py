# -*- coding: utf-8 -*-
""" 
TPT - By P.Vinothkumar  - on 29/01/2016
Sales CST Report : Display the Sales CST  values for the selected date range
"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class sales_cstreport(osv.osv_memory):
    _name = "sales.cstreport"
    _columns = {
        'date_from': fields.date('From Date', required = True),
        'date_to': fields.date('To Date', required = True),   
        #'order_type':fields.selection([('domestic','Domestic/Indirect Export'),('export','Export')],'Invoice Type'),
        #'tax':fields.many2one('account.tax','Tax', domain="[('type_tax_use','=','sales')]",), 
        'tax':fields.many2one('account.tax','Tax'), # Added on 02/04/2016 by P.VINOTHKUMAR
        'application': fields.many2one('crm.application', 'Application'), # Added on 02/04/2016 by P.VINOTHKUMAR
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'sales.cstreport'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'rpt_salescstreport', 'datas': datas}
    
    
sales_cstreport()

