# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class cost_center_expense_wizard(osv.osv_memory):
    _name = "cost.center.expense.wizard"
    
    _columns = {
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'section_id': fields.many2one('arul.hr.section', 'Section'),
        'cost_center_ids': fields.many2many('tpt.cost.center', 'cost_center_expense_tpt_cc_ref', 'cce_id', 'cc_id', 'Cost Center'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'cost.center.expense.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'cost_center_expense_report', 'datas': datas}
        
cost_center_expense_wizard()
