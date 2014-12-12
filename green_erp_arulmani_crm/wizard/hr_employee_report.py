# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class list_employee_report(osv.osv_memory):
    _name = "list.employee.report"
    _columns = {
            'active_selection':fields.selection([('active','Active'),('inactive','Inactive'),('both','Both')], 'Active Selection',required = True) ,        
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
             
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'list.employee.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'list_employee_report', 'datas': datas}
        
list_employee_report()