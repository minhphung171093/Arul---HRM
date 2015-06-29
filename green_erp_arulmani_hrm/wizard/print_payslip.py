# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class print_payslip(osv.osv_memory):
    _name = "print.payslip"
    
#     def default_get(self, cr, uid, fields, context=None):
#         if context is None:
#             context = {}
#         context.update({'tpt_emp_in_active':True})
#         res = super(print_payslip, self).default_get(cr, uid, fields, context=context)
#         return res
    
    _columns = {
            'employee_ids': fields.many2many('hr.employee','print_payslip_ref', 'print_payslip_id', 'employee_id', 'Employee', required=True),
            'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year', required = True),
            'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
    }
    
    _defaults = {
                 
        'year':int(time.strftime('%Y')),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'print.payslip'
        context.update({'active_test': False})
        datas['form'] = self.read(cr, uid, ids)[0]
        line = self.browse(cr, uid, ids[0],context)
        employee_ids = [e.id for e in line.employee_ids]
        datas['form'].update({'active_id':context.get('active_ids',False),'employee_ids':employee_ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'arul_payslip_report', 'datas': datas}
        
print_payslip()

