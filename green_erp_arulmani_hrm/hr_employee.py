# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class arul_hr_employee_action_history(osv.osv):
    _name = 'arul.hr.employee.action.history'
    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee ID',required = True),
        'action': fields.selection([('leaving','Leaving'),('promotion','Promotion')],'Action',required = True ),
        'action_type': fields.selection([('resignation','Resignation'),('termination','Termination'),('normal_retirement','Normal Retirement'),('volunteer_retirement','Volunteer Retirement'),('death','Death'),('good_performance','Good Performance'),('vacancy','Vacancy')],'Action type',required = True),
        'action_date': fields.date('Action Date'),
        'created_date': fields.datetime('Created Date'),
        'created_uid': fields.many2one('res.users','Created By'),
        'period_from': fields.date('Period From'),
        'period_to': fields.date('Period to'),
        'reason': fields.char('Reason',size=1024),
        'note': fields.text('Note'),
        'department_from': fields.many2one('hr.department','Department From'),
        'department_to': fields.many2one('hr.department','Department To'),
        'designation_from':fields.many2one('arul.hr.designation','Designation From'),
        'designation_to':fields.many2one('arul.hr.designation','Designation To'),
        'employee_category':fields.many2one('arul.employee.category','Employee Category'),
        'sub_category':fields.many2one('arul.employee.sub.category','Sub Category'),
#         Document upload
        'current_month_salary': fields.boolean('Current Month Salary (Y/N)'),
        'pl_encashment': fields.boolean('PL Encashment (Y/N)'),
        'c_off': fields.boolean('C-Off (Y/N)'),
        'bonus': fields.boolean('Bonus (Y/N)'),
        'medical_reimbursement': fields.boolean('Medical Reimbursement (Y/N)'),
        'gratuity': fields.boolean('Gratuity (Y/N)'),
        'pf_settlement': fields.boolean('PF Settlement (Y/N)'),
    }
    
arul_hr_employee_action_history()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'action_history_line': fields.one2many('arul.hr.employee.action.history','employee_id','Action History Line',readonly=True),
    }
    
hr_employee()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class arul_employee_category(osv.osv):
    _name="arul.employee.category"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
        'active':fields.boolean('Active'),
        'sub_category_ids':fields.many2many('arul.employee.sub.category','catagory_subcategory_ref','category_id','sub_category_id','Sub Category'),
              }
    _defaults={
            'active':True,
               }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_category()

class arul_employee_sub_category(osv.osv):
    _name="arul.employee.sub.category"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
              }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_sub_category()

class arul_employee_actions(osv.osv):
    _name="arul.employee.actions"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
        'active':fields.boolean('Active'),
        'action_type_ids':fields.many2many('arul.employee.action.type','actions_action_type_ref','actions_id','action_type_id','Action Type'),
              }
    _defaults={
            'active':True,
               }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_actions()

class arul_employee_action_type(osv.osv):
    _name="arul.employee.action.type"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
              }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]

arul_employee_action_type()

