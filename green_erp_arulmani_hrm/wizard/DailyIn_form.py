# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class daily_in(osv.osv_memory):
    _name = "daily.in"
    
    _columns = {
            'workdate': fields.date('Work Date', required = True),
#             'a_shift':  fields.boolean('A'),
#             'g1_shift':  fields.boolean('G1'),
#             'g2_shift':  fields.boolean('G2'),
#             'b_shift':  fields.boolean('B'),
#             'c_shift':  fields.boolean('C'),
            'shift_type':fields.selection([('a_shift', 'A'),('g1_shift', 'G1'),
                                      ('g2_shift', 'G2'),('b_shift', 'B'),
                                      ('c_shift', 'C')],'Shift Type'),
            'blank_space':fields.char('')
            
    }
    
    _defaults = {
       
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'daily.inout'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daily_in_report', 'datas': datas}
   
        
daily_in()

