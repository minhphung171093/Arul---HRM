# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class hr_employee_category(osv.osv):
    _inherit = "vsis.hr.employee.category"
    _columns = {
        'sub_category_ids' : fields.many2many('hr.employee.sub.category','category_sub_category_ref','category_id','sub_category_id','Sub Category'),
    }
hr_employee_category()

class arul_action(osv.osv):
    _name = 'arul.action'
    _columns = {
        'name': fields.char('Name',size=1024, required=True),
    }
    
    def init(self, cr):

        for key in ['Leaving','Promotion','Re Hiring','Compensation Review','Contracts','Hiring','Transfer']:
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
        for key in ['Resignation','Termination','Normal Retirement','Volunteer Retirement','Death','Good Performance','Vacancy','New Hire', 'Expansion','Vacancy Fill Up','Change of Pay' ,'Revision of Salary', 'Increment','Promotion','Probation', 'Confirmation','Extension of Trainee','Extension of Probation','Performance','Men Power Shortage']:
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
        for key in ['Completion of Trainee','Good Performance', 'Successful completion of Trainee','Successful completion of Probation']:
            arul_ids = self.search(cr, 1, [('name','=',key)])
            if not arul_ids:
                self.create(cr, 1, {'name': key})
    
arul_reason()

class arul_hr_employee_action_history(osv.osv):
    _name = 'arul.hr.employee.action.history'
    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee ID',required = False),
        'action_id': fields.many2one('arul.action','Action', required=True),
        'action_type_id': fields.many2one('arul.action.type','Action type', required=True),
        'action_date': fields.date('Action Date'),
        'create_date': fields.datetime('Created Date'),
        'create_uid': fields.many2one('res.users','Created By'),
        'period_from': fields.date('Period From'),
        'period_to': fields.date('Period to'),
        'reason_id': fields.many2one('arul.season','Reason'),
        'note': fields.text('Note'),
        'department_from_id': fields.many2one('hr.department','Department From'),
        'department_to_id': fields.many2one('hr.department','Department To'),
        'designation_from_id':fields.many2one('arul.hr.designation','Designation From'),
        'designation_to_id':fields.many2one('arul.hr.designation','Designation To'),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category'),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category'),
        'payroll_area_id':fields.many2one('arul.hr.payroll.area','Payroll Area'),
        'payroll_sub_area_id':fields.many2one('arul.hr.payroll.area','Payroll Sub Area'),
#         Document upload
        'current_month_salary': fields.boolean('Current Month Salary (Y/N)'),
        'pl_encashment': fields.boolean('PL Encashment (Y/N)'),
        'c_off': fields.boolean('C-Off (Y/N)'),
        'bonus': fields.boolean('Bonus (Y/N)'),
        'medical_reimbursement': fields.boolean('Medical Reimbursement (Y/N)'),
        'gratuity': fields.boolean('Gratuity (Y/N)'),
        'pf_settlement': fields.boolean('PF Settlement (Y/N)'),
    }
    
    def onchange_rehiring_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id}
        return {'value': vals}



    def onchange_leaving_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'payroll_area_id':emp.payroll_area_id.id,
                    'payroll_sub_area_id':emp.payroll_sub_area_id.id}
        return {'value': vals}
    
    def create_hiring_employee(self, cr, uid, ids, context=None):
        ir_model_data = self.pool.get('ir.model.data')
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'hr', 'view_employee_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'create_hiring_employee': ids,
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.employee',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'current',
            'context': ctx,
        }
        
    def create(self, cr, uid, vals, context=None):
        new_id = super(arul_hr_employee_action_history, self).create(cr, uid, vals, context)
        if context.get('create_leaving_employee'):
            action_history = self.browse(cr, uid, new_id)
            self.pool.get('hr.employee').write(cr, uid, [action_history.employee_id.id], {'employee_active': False})
        return new_id

    
arul_hr_employee_action_history()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'action_history_line': fields.one2many('arul.hr.employee.action.history','employee_id','Action History Line',readonly=True),
        'section_id': fields.many2one('arul.hr.section','Section'),
        'payroll_area_id': fields.many2one('arul.hr.payroll.area','Payroll Area'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area','Payroll Sub Area'),
        'time_record': fields.char('Time Record ID', size=1024),
    }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_contract_employee'):
            
            sql = '''
                
                select employee_id from hr_contract group by employee_id
                    
            '''
            cr.execute(sql)
            employee_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',employee_ids)]
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
<<<<<<< HEAD
    def onchange_department_id(self, cr, uid, ids,department_id=False, context=None):
        section_ids = []
        if department_id:
            dept = self.pool.get('hr.department').browse(cr, uid, department_id)
            section_ids = [x.id for x in dept.section_ids]
        return {'value': {'section_id': False}, 'domain':{'section_id':[('id','in',section_ids)]}}
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
        emp_sub_cat = []
        if employee_category_id:
            emp_cat = self.pool.get('vsis.hr.employee.category').browse(cr, uid, employee_category_id)
            emp_sub_cat = [x.id for x in emp_cat.sub_category_ids]
        return {'value': {'employee_sub_category_id': False }, 'domain':{'employee_sub_category_id':[('id','in',emp_sub_cat)]}}
=======
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(hr_employee, self).create(cr, uid, vals, context)
        if context.get('create_hiring_employee'):
            for line_id in context.get('create_hiring_employee'):
                self.pool.get('arul.hr.employee.action.history').write(cr, uid, [line_id], {'employee_id': new_id})
        return new_id
    
>>>>>>> ed542ccbd29818aded4ed978fd882590f8dd6be0
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

