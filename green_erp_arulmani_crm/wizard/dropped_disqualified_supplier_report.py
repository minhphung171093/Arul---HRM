# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class dropped_disqualified_supplier_report(osv.osv_memory):
    _name = "dropped.disqualified.supplier.report"
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Vendor'),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),        
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': ids}
        datas['model'] = 'dropped.disqualified.supplier.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'dropped_disqualified_supplier_report', 'datas': datas}
        
dropped_disqualified_supplier_report()