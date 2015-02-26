# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class time_evaluation(osv.osv_memory):
    _name = "time.evaluation"
    
    _columns = {
            'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year', required = True),
            'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
            'category_id': fields.many2one('vsis.hr.employee.category', 'Employee Category'),
    }
    
    _defaults = {
        'year':int(time.strftime('%Y')),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'time.evaluation'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_time_evaluation_report', 'datas': datas}
        
time_evaluation()

