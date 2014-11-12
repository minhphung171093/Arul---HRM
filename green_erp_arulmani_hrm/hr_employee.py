# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class arul_action(osv.osv):
    _name = 'arul.action'
    _columns = {
        'name': fields.char('Name',size=1024, required=True),
    }
    
    def init(self, cr):
        for key in ['Leaving','Promotion','Re Hiring','Compensation Review']:
            arul_ids = self.search(cr, 1, [('name','=',key)])
            if not arul_ids:
                self.create(cr, 1, {'name': key})
    
arul_action()

class arul_action_type(osv.osv):
    _name = 'arul.action.type'
    _columns = {
        'name': fields.char('Name',size=1024, required=True),
    }
    
    def init(self, cr):
        for key in ['Resignation','Termination','Normal Retirement','Volunteer Retirement','Death','Good Performance','Vacancy','New Hire', 'Expansion','Vacancy Fill Up','Change of Pay' ,'Revision of Salary', 'Increment','Promotion']:
            arul_ids = self.search(cr, 1, [('name','=',key)])
            if not arul_ids:
                self.create(cr, 1, {'name': key})
    
arul_action_type()

class arul_reason(osv.osv):
    _name = 'arul.season'
    _columns = {
        'name': fields.char('Name',size=1024, required=True),
    }
    
    def init(self, cr):
        for key in ['Completion of Trainee']:
            arul_ids = self.search(cr, 1, [('name','=',key)])
            if not arul_ids:
                self.create(cr, 1, {'name': key})
    
arul_reason()

class arul_hr_employee_action_history(osv.osv):
    _name = 'arul.hr.employee.action.history'
    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee ID',required = True),
        'action_id': fields.many2one('arul.action','Action', required=True),
        'action_type_id': fields.many2one('arul.action.type','Action type', required=True),
        'action_date': fields.date('Action Date'),
        'created_date': fields.datetime('Created Date'),
        'created_uid': fields.many2one('res.users','Created By'),
        'period_from': fields.date('Period From'),
        'period_to': fields.date('Period to'),
        'reason': fields.many2one('arul.season','Reason'),
        'note': fields.text('Note'),
        'department_from_id': fields.many2one('hr.department','Department From'),
        'department_to_id': fields.many2one('hr.department','Department To'),
        'designation_from_id':fields.many2one('arul.hr.designation','Designation From'),
        'designation_to_id':fields.many2one('arul.hr.designation','Designation To'),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category'),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category'),
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
        'section_id': fields.many2one('arul.hr.section','Section'),
        'payroll_area_id': fields.many2one('arul.hr.payroll.area','Payroll Area'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area','Payroll Sub Area'),
    }
    
hr_employee()

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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

