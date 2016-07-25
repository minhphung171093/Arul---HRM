# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from datetime import date
import time
import datetime
import math
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from datetime import datetime, timedelta

class arul_hr_payroll_contribution_parameters(osv.osv):
    _inherit = 'arul.hr.payroll.contribution.parameters'
    
    _columns = {
        'contribution_parameters_history_line': fields.one2many('arul.hr.payroll.contribution.parameters.history', 'contribution_parameters_id','History'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        history_obj = self.pool.get('arul.hr.payroll.contribution.parameters.history')
        for line in self.browse(cr, uid, ids):
            history_vals = {}
            if vals.get('emp_lwf_amt', False):
                history_vals.update({
                    'employer_lwf_con_amt': line.employer_lwf_con_amt,
                    'emp_lwf_amt': line.emp_lwf_amt,
                })
            if vals.get('employer_lwf_con_amt', False):
                history_vals.update({
                    'employer_lwf_con_amt': line.employer_lwf_con_amt,
                    'emp_lwf_amt': line.emp_lwf_amt,
                })
            if history_vals:
                history_vals.update({
                    'date': time.strftime('%Y-%m-%d'),
                    'contribution_parameters_id': line.id,
                })
                history_obj.create(cr, uid, history_vals)
        return super(arul_hr_payroll_contribution_parameters, self).write(cr, uid, ids, vals, context)
    
arul_hr_payroll_contribution_parameters()

class arul_hr_payroll_contribution_parameters_history(osv.osv):
    _name = 'arul.hr.payroll.contribution.parameters.history'
    
    _columns = {
        'contribution_parameters_id':fields.many2one('arul.hr.payroll.contribution.parameters','Payroll Contribution Parameters', ondelete='cascade'),
        'date': fields.date('Date'),
        'emp_lwf_amt': fields.float('Employee Labor Welfare Fund (LWF) Amt'),
        'employer_lwf_con_amt': fields.float('Employer LWF Contribution Amt'),
    }
    
arul_hr_payroll_contribution_parameters_history()


