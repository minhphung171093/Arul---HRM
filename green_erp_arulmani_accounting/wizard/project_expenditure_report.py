# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class project_expenditure(osv.osv_memory):
    _name = "project.expenditure"
    
    _columns = {
            'date_from': fields.date('Date From', required='1'),
            'date_to': fields.date('Date To', required='1'),
            'project_id': fields.many2one('tpt.project','Project Title'),        
                }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'project.expenditure'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'project_expenditure_report', 'datas': datas}
        
project_expenditure()
