# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class leave_balance(osv.osv_memory):
    _name = "leave.balance"
    
    _columns = {
            'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year', required = True),
            'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),          
            'employee': fields.many2one('hr.employee', 'Employee',ondelete='restrict'),
            'employee_category': fields.many2one('vsis.hr.employee.category', 'Employee Category'),            
            'department': fields.many2one('hr.department', 'Department',ondelete='restrict'),
            'is_active': fields.boolean('Is Active'),
            
    }
    
    _defaults = {
        'year':int(time.strftime('%Y')),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'leave.balance'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'leave_balance_report', 'datas': datas}
        
leave_balance()

