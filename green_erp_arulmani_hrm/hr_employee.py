# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class hr_employee_category(osv.osv):
    _inherit = "vsis.hr.employee.category"
    _columns = {
        'sub_category_ids' : fields.many2many('hr.employee.sub.category','category_sub_category_ref','category_id','sub_category_id','Sub Category'),
    }
hr_employee_category()

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
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(arul_hr_employee_action_history, self).default_get(cr, uid, fields, context=context)
        if context.get('action_default_disciplinary'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Disciplinary')])
        elif context.get('action_default_leaving'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Leaving')])
        elif context.get('action_default_hiring'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Hiring')])
        elif context.get('action_default_contracts'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Contracts')])
        elif context.get('action_default_compensation_review'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Compensation Review')])
        elif context.get('action_default_rehiring'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Re Hiring')])
        elif context.get('action_default_promotion'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Promotion')])
        elif context.get('action_default_transfer'):
            action_ids = self.pool.get('arul.employee.actions').search(cr, uid, [('name','=','Transfer')])
        else:
            action_ids = []
        if action_ids:
            res.update({'action_id': action_ids[0]})
        
        return res
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(arul_hr_employee_action_history, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(arul_hr_employee_action_history, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    _columns = {
        'employee_id': fields.many2one('hr.employee','Employee ID',required = False),
        'action_id': fields.many2one('arul.employee.actions','Action', required=True),
        'action_type_id': fields.many2one('arul.employee.action.type','Action type', required=True),
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
        'payroll_sub_area_id':fields.many2one('arul.hr.payroll.sub.area','Payroll Sub Area'),
        'approve_rehiring': fields.boolean('Approve Rehiring'),
#         Document upload
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Upload/View Specification', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'current_month_salary': fields.boolean('Current Month Salary (Y/N)'),
        'pl_encashment': fields.boolean('PL Encashment (Y/N)'),
        'c_off': fields.boolean('C-Off (Y/N)'),
        'bonus': fields.boolean('Bonus (Y/N)'),
        'medical_reimbursement': fields.boolean('Medical Reimbursement (Y/N)'),
        'gratuity': fields.boolean('Gratuity (Y/N)'),
        'pf_settlement': fields.boolean('PF Settlement (Y/N)'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['action_id','employee_id'], context)
  
        for record in reads:
            if record['action_id'][1] != 'Hiring':
                name = record['action_id'][1] + '-' + record['employee_id'][1]
            else:
                name = record['action_id'][1]
            res.append((record['id'], name))
        return res
    
    def onchange_action_id(self, cr, uid, ids,action_id=False, context=None):
        action_type_ids = []
        if action_id:
            action = self.pool.get('arul.employee.actions').browse(cr, uid, action_id)
            action_type_ids = [x.id for x in action.action_type_ids]
        return {'value': {'action_type_id': False}, 'domain':{'action_type_id':[('id','in',action_type_ids)]}}
    
    def onchange_rehiring_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id}
        return {'value': vals}

    def onchange_promotion_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'department_from_id':emp.department_id.id,
                    'designation_from_id':emp.department_id.designation_id.id,}
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
        hiring = self.browse(cr, uid, ids[0])
        ctx.update({
            'create_hiring_employee': ids,
            'default_employee_category_id': hiring.employee_category_id.id,
            'default_employee_sub_category_id': hiring.sub_category_id.id,
            'default_payroll_area_id': hiring.payroll_area_id.id,
            'default_payroll_sub_area_id': hiring.payroll_sub_area_id.id,
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
    def approve_employee_rehiring(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'employee_active': True})
            self.write(cr, uid, [line.id],{'approve_rehiring': True})
        return True
    
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
                
                select employee_id from arul_hr_employee_action_history where action_id in (select id from arul_action where name = 'Contracts') group by employee_id
                    
            '''%()
            cr.execute(sql)
            exist_employee_ids = [row[0] for row in cr.fetchall()]
            if exist_employee_ids:
                sql = '''
                    select employee_id from hr_contract where employee_id not in (%s) group by employee_id
                '''%(','.join(map(str,exist_employee_ids)))
            else:
                sql = '''
                    select employee_id from hr_contract group by employee_id
                '''
            cr.execute(sql)
            employee_ids = [row[0] for row in cr.fetchall()]
            if context.get('employee_id'):
                employee_ids.append(context.get('employee_id'))
            args += [('id','in',employee_ids)]
        if context.get('search_disciplinary_employee'):
            sql = '''
                
                select employee_id from arul_hr_employee_action_history where action_id in (select id from arul_action where name = 'Disciplinary') group by employee_id
                    
            '''%()
            cr.execute(sql)
            exist_employee_ids = [row[0] for row in cr.fetchall()]
            employee_ids = self.search(cr, uid, [('id','not in',exist_employee_ids)])
            if context.get('employee_id'):
                employee_ids.append(context.get('employee_id'))
            args += [('id','in',employee_ids)]
        if context.get('search_promotion_employee'):
            sql = '''
                
                select employee_id from arul_hr_employee_action_history where action_id in (select id from arul_action where name = 'Promotion') group by employee_id
                    
            '''%()
            cr.execute(sql)
            exist_employee_ids = [row[0] for row in cr.fetchall()]
            employee_ids = self.search(cr, uid, [('id','not in',exist_employee_ids)])
            if context.get('employee_id'):
                employee_ids.append(context.get('employee_id'))
            args += [('id','in',employee_ids)]
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
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
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        new_id = super(hr_employee, self).create(cr, uid, vals, context)
        if context.get('create_hiring_employee'):
            for line_id in context.get('create_hiring_employee'):
                self.pool.get('arul.hr.employee.action.history').write(cr, uid, [line_id], {'employee_id': new_id})
        return new_id
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
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('code','=',employee.code)])
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
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('code','=',employee.code)])
            if employee_ids:  
                return False
        return True
    
    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]

arul_employee_action_type()

class food_subsidy(osv.osv):
    _name = "food.subsidy"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for price in self.browse(cr, uid, ids, context=context):
            res[price.id] = {
                'employer_con': price.food_price*0.75,
                'employee_con': price.food_price*0.25,
            }
        return res
    
    _columns = {
        'food_category':fields.selection([('break_fast','Break Fast'),('lunch','Lunch'),('dinner','Dinner'),('midnight_tiffin','Midnight Tiffin')],'Food Category',required=True),
        'food_price': fields.float('Food Price (Rs.)',degits=(16,2)),
        'employer_con': fields.function(_amount_all,degits=(16,2), string='Employer Contribution (Rs.)',
            store={
                'food.subsidy': (lambda self, cr, uid, ids, c={}: ids, ['food_price'], 10),
            },
            multi='sums'),
        'employee_con': fields.function(_amount_all,degits=(16,2), string='Employee Contribution (Rs.)',
            store={
                'food.subsidy': (lambda self, cr, uid, ids, c={}: ids, ['food_price'], 10),
            },
            multi='sums'),
    }
food_subsidy()

class meals_deduction(osv.osv):
    _name = "meals.deduction"
    
#     def load_food_sub(self, cr, uid, ids, meal_code = False, context=None):
#         employer_amount = 0
#         employee_amount = 0
#         food_subsidy_obj = self.pool.get('food.subsidy')
#         food_subsidy_ids = food_subsidy_obj.search(self.cr, self.uid, [('food_category','=',meal_code)])
#         res = {
#                 'employer_amount': food_subsidy_ids.employer_con,
#                 'employee_amount': food_subsidy_ids.employee_con,
#             }
#         return res
    
    _columns = {
        'meals_date':fields.date('Meals Arrangement Date'),
        'meals_for':fields.selection([('employees','Employees'),('others','Others')],'Meals Arrangement For',required=True),
        'meals_details_emp_ids': fields.one2many('meals.details','meals_id','Meals Deduction Details'),
        'meals_details_order_ids': fields.one2many('meals.details','meals_id','Meals Deduction Details'),
    }
meals_deduction()

class meals_details(osv.osv):
    _name = "meals.details"
    _description = "Meals Deduction"
    _columns = {
        'emp_code' : fields.char('Emp. Code', size=128),
        'emp_name' : fields.char('Name', size=128),
        'break_fast' : fields.boolean('Break Fast'),
        'lunch' : fields.boolean('Lunch'),
        'dinner' : fields.boolean('Dinner'),
        'midnight_tiffin' : fields.boolean('Midnight Tiffin'),
        'employer_amt': fields.float('Employer Amt',degits=(16,2)),
        'employee_amt': fields.float('Employee Amt',degits=(16,2)),
        'free_cost' : fields.boolean('Free Of Cost'),
        'meals_id': fields.many2one('hr.employee','Employee'),
    }
    
    def onchange_checkbox(self, cr, uid, ids, bre, lun, din, mid, free, context=None):
        employer_amount = 0
        employee_amount = 0
        food_subsidy_obj = self.pool.get('food.subsidy')
        if bre : 
            food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','break_fast')])
            for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                employer_amount += meal.employer_con
                employee_amount += meal.employee_con
        if lun : 
            food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','lunch')])
            for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                employer_amount += meal.employer_con
                employee_amount += meal.employee_con
        if din : 
            food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','dinner')])
            for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                employer_amount += meal.employer_con
                employee_amount += meal.employee_con
        if mid : 
            food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','midnight_tiffin')])
            for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                employer_amount += meal.employer_con
                employee_amount += meal.employee_con
        if free : 
            employer_amount += employee_amount
            employee_amount = 0
            
        res = {
            'employer_amt': employer_amount,
            'employee_amt': employee_amount,
        }        
        return {'value':res}
    
meals_details()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

