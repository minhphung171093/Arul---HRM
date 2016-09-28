# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_designation_wise_total_strength_report(osv.osv_memory):
    _name = "tpt.designation.wise.total.strength.report"
    
    _columns = {
            'date_from': fields.date('From Date', required = True),
            'date_to': fields.date('To Date', required = True),   
            'employee_category' : fields.many2one('vsis.hr.employee.category', 'Employee Category',required = True),
    }

    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.designation.wise.total.strength.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'rpt_designation_wise_total_strength_report', 'datas': datas}
        
tpt_designation_wise_total_strength_report()

