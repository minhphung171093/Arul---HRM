# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
class hr_department(osv.osv):
    _description = "Department"
    _inherit = 'hr.department'
    _columns = {
        'code': fields.char('Department Code', size=1024, required = True),
        'primary_auditor_id': fields.many2one('hr.employee', 'Primary Time Auditor'),
        'secondary_auditor_id':  fields.many2one('hr.employee', 'Sec. Time Auditor'),
        'section_ids': fields.many2many('arul.hr.section', 'department_section_rel', 'department_id', 'section_id', 'Sections'),
        'resource_budgets_ids': fields.many2many('arul.hr.resource.budgets', 'department_resource_budgets_rel', 'department_id', 'resource_budgets_id', 'Designation & Resource Budgets'),
        'designation_id': fields.many2one('arul.hr.designation', 'Designation'),
        'number': fields.integer('No.of Persons'),
    }
    
    def _check_department_id(self, cr, uid, ids, context=None):
        for department in self.browse(cr, uid, ids, context=context):
            department_ids = self.search(cr, uid, [('id','!=',department.id),('code','=',department.code), ('name','=',department.name)])
            if department_ids:  
                return False
        return True
    _constraints = [
        (_check_department_id, 'Identical Data', ['code', 'name']),
    ]
    
hr_department()

class arul_hr_section(osv.osv):
    _name = 'arul.hr.section'
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
    
arul_hr_section()

# class arul_hr_resource_budgets(osv.osv):
#     _name = 'arul.hr.resource.budgets'
#     _columns = {
#                 
#         'designation_id': fields.many2one('arul.hr.designation', 'Designation'),
#         'number': fields.integer('No.of Persons'),
#         
#     }
#     
#     
# arul_hr_resource_budgets()

class arul_hr_designation(osv.osv):
    _name = 'arul.hr.designation'
    _columns = {
                
        'name': fields.char('Designation', size=1024, required = True),
        
    }
    
    
arul_hr_designation()
