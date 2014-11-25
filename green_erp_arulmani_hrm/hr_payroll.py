# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime



class arul_hr_payroll_area(osv.osv):
    _name = 'arul.hr.payroll.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_code_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            payroll_name_ids = self.search(cr, uid, [('id','!=',payroll.id),('name','=',payroll.name)])
            if payroll_code_ids or payroll_name_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
    
arul_hr_payroll_area()

class arul_hr_payroll_sub_area(osv.osv):
    _name = 'arul.hr.payroll.sub.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]

class arul_hr_payroll_deduction_parameters(osv.osv):
    _name = 'arul.hr.payroll.deduction.parameters'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
        'code': fields.char('Code', size=1024, required = True),
        'description': fields.text('Description'),
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
arul_hr_payroll_deduction_parameters()

class arul_hr_payroll_contribution_parameters(osv.osv):
    _name = 'arul.hr.payroll.contribution.parameters'
    _columns = {
        'emp_pf_con': fields.float('Employee PF Contribution (%)'),
        'employer_pension_con': fields.float('Employer Pension Contribution (%)'),
        'pension_limit_amt': fields.float('Pension Limit Amt'),
        'emp_esi_limit': fields.float('Employee ESI Limit (%)'),
        'emp_esi_con': fields.float('Employee ESI Contribution (%)'),
        'employer_esi_con': fields.float('Employer ESI Contribution (%)'),
        'emp_lwf_amt': fields.float('Employee Labor Welfare Fund (LWF) Amt'),
        'employer_lwf_con_amt': fields.float('Employer LWF Contribution Amt'),
    }
arul_hr_payroll_contribution_parameters()
