# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar
class hr_employee_category(osv.osv):
    _inherit = "vsis.hr.employee.category"
    _columns = {
        'sub_category_ids' : fields.one2many('hr.employee.sub.category','category_id','Sub Category'),
    }
    def _check_name(self, cr, uid, ids, context=None):
        for emp_cat in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from hr_employee_category where id != %s and lower(name) = lower('%s')
            '''%(emp_cat.id,emp_cat.name)
            cr.execute(sql)
            emp_cat_ids = [row[0] for row in cr.fetchall()]
            if emp_cat_ids:  
                raise osv.except_osv(_('Warning!'),_('This name is duplicated!'))
                return False
        return True
    _constraints = [
        (_check_name, 'Identical Data', ['name']),
    ]
    
hr_employee_category()

class hr_employee_sub_category(osv.osv):
    _inherit = "hr.employee.sub.category"
    
    _columns = {
        'category_id' : fields.many2one('vsis.hr.employee.category','Category',ondelete='cascade'),
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('check_employee_category_id'):
            employee_category_id = context.get('employee_category_id')
            if not employee_category_id:
                args += [('id','=',-1)]
        return super(hr_employee_sub_category, self).search(cr, uid, args, offset, limit, order, context, count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
hr_employee_sub_category()

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
            res.update({'period_to' : '9999-12-31'})
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
        'designation_from_id':fields.many2one('hr.job','Designation From'),
        'designation_to_id':fields.many2one('hr.job','Designation To'),
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
        emp_sub_cat = []
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id}
        if emp.employee_category_id:
                emp_sub_cat = [x.id for x in emp.employee_category_id.sub_category_ids]
        return {'value': vals, 'domain':{'sub_category_id':[('id','in',emp_sub_cat)]}}

    def onchange_promotion_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        emp_sub_cat = []
        designation_ids = []
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'department_from_id':emp.department_id.id,
                    'designation_from_id':emp.job_id.id,
#                     'payroll_area_id':emp.payroll_area_id.id,
                    }
        return {'value': vals}
    
    def onchange_department_from_id(self, cr, uid, ids,department_from_id=False, context=None):
        designation_ids = []
        if department_from_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_from_id)
            for line in department.designation_line:
                designation_ids.append(line.designation_id.id)
        return {'value': {'designation_from_id': False }, 'domain':{'designation_from_id':[('id','in',designation_ids)]}}
    
    def onchange_department_to_id(self, cr, uid, ids,department_to_id=False,designation_from_id=False, context=None):
        designation_ids = []
        if department_to_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_to_id)
            for line in department.designation_line:
                if line.designation_id.id != designation_from_id:
                    designation_ids.append(line.designation_id.id)
            
        return {'value': {'designation_to_id': False }, 'domain':{'designation_to_id':[('id','in',designation_ids)]}}
    
    def onchange_transfer_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'payroll_area_id':emp.payroll_area_id.id,
                    'payroll_sub_area_id':emp.payroll_sub_area_id.id,
                    'department_from_id':emp.department_id.id,
                    }
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

    def onchange_disciplinary_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id}
        return {'value': vals}

    def onchange_compensation_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id}
        return {'value': vals}
    
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False,employee_sub_category_id=False, context=None):
        vals = {}
        if employee_category_id and employee_sub_category_id:
            sql = '''
                select id from hr_employee_sub_category where id = %s and category_id=%s
            '''%(employee_sub_category_id,employee_category_id)
            cr.execute(sql)
            sub_category_ids = [row[0] for row in cr.fetchall()]
            if not sub_category_ids:
                vals['sub_category_id']=False
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
            'default_department_id': hiring.department_from_id.id,
            'default_date_of_joining': hiring.period_from,
            'default_date_of_resignation': hiring.period_to,
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
            self.pool.get('hr.employee').write(cr, uid, [action_history.employee_id.id], {'active': False})
        if context.get('create_promotion_employee'):
            action_history = self.browse(cr, uid, new_id)
            self.pool.get('hr.employee').write(cr, uid, [action_history.employee_id.id], {'employee_category_id': action_history.employee_category_id and action_history.employee_category_id.id or False,
                                                                                          'employee_sub_category_id': action_history.sub_category_id and action_history.sub_category_id.id or False,
                                                                                          'job_id': action_history.designation_to_id.id and action_history.designation_to_id.id or action_history.designation_from_id.id,
                                                                                          'department_id': action_history.department_to_id.id and action_history.department_to_id.id or action_history.department_from_id.id},
                                                                                          )
        if context.get('create_transfer_employee'):
            action_history = self.browse(cr, uid, new_id)
            self.pool.get('hr.employee').write(cr, uid, [action_history.employee_id.id], {'employee_category_id': action_history.employee_category_id and action_history.employee_category_id.id or False,
                                                                                          'employee_sub_category_id': action_history.sub_category_id and action_history.sub_category_id.id or False,
                                                                                          'job_id': action_history.designation_to_id.id and action_history.designation_to_id.id or action_history.designation_from_id.id,
                                                                                          'payroll_area_id':action_history.payroll_area_id and action_history.payroll_area_id.id or False,
#                                                                                           'payroll_sub_area_id':action_history.payroll_sub_area_id and action_history.payroll_sub_area_id.id or False,
                                                                                          'department_id': action_history.department_to_id.id and action_history.department_to_id.id or action_history.department_from_id.id})
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(arul_hr_employee_action_history, self).write(cr, uid,ids, vals, context)
        if 'department_to_id' in vals:
            for line in self.browse(cr, uid, ids):
                self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'department_id': line.department_to_id.id})
        else:
            if 'department_from_id' in vals:
                for line in self.browse(cr, uid, ids):
                    self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'department_id': line.department_from_id.id})
                
        if 'designation_to_id' in vals:
            for line in self.browse(cr, uid, ids):
                self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'job_id': line.designation_to_id.id})
        else:
            if 'designation_from_id' in vals:
                for line in self.browse(cr, uid, ids):
                    self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'job_id': line.designation_from_id.id})
        new = self.browse(cr, uid, ids[0])
        if new.employee_id:
            if 'employee_category_id' in vals:
                for line in self.browse(cr, uid, ids):
                    self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'employee_category_id': line.employee_category_id and line.employee_category_id.id or False})
            if 'sub_category_id' in vals:
                for line in self.browse(cr, uid, ids):
                    self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'employee_sub_category_id': line.sub_category_id and line.sub_category_id.id or False})
            if 'payroll_area_id' in vals:
                for line in self.browse(cr, uid, ids):
                    self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'payroll_area_id': line.payroll_area_id and line.payroll_area_id.id or False})
        return new_write
    
    def approve_employee_rehiring(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.pool.get('hr.employee').write(cr, uid, [line.employee_id.id], {'active': True})
            self.write(cr, uid, [line.id],{'approve_rehiring': True})
        return True

    def _check_date(self, cr, uid, ids, context=None):
        for act in self.browse(cr, uid, ids, context=context):
            if act.period_from and act.period_to:
                if act.period_from > act.period_to:
                    raise osv.except_osv(_('Warning!'),_('The Date is not suitable!'))
                    return False
        return True
    def _check_rehiring_date(self, cr, uid, ids, context=None):
        for act in self.browse(cr, uid, ids, context=context):
            if act.period_from and act.action_date:
                if act.period_from < act.action_date:
                    raise osv.except_osv(_('Warning!'),_('The Valid From Date must be the same as/greater than The Date Of Rehiring!'))
                    return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', ['period_from','period_to']),
        (_check_rehiring_date, 'Identical Data', ['period_from','action_date']),
    ]
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('check_employee_category_id'):
            employee_category_id = context.get('employee_category_id')
            if not employee_category_id:
                args += [('id','=',-1)]
        return super(arul_hr_employee_action_history, self).search(cr, uid, args, offset, limit, order, context, count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
arul_hr_employee_action_history()

class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _order = 'employee_id'
    _columns = {
        'action_history_line': fields.one2many('arul.hr.employee.action.history','employee_id','Action History Line',readonly=True),
        'section_id': fields.many2one('arul.hr.section','Section'),
        'payroll_area_id': fields.many2one('arul.hr.payroll.area','Payroll Area'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area','Payroll Sub Area'),
        'time_record': fields.char('Time Record ID', size=1024, required = True),
        'employee_leave_id': fields.one2many('employee.leave','employee_id','Employee Leave',readonly=False),
        'country_stateofbirth_id': fields.many2one('res.country', 'Country'),
        'date_of_retirement': fields.date('Date Of Retirement'),
        'personal_contact': fields.char('Personal Mobile Number', size=1024),
        'birth_place': fields.char('Birthplace', size=1024),
#         'personal_contact': fields.char('Personal Contact', size=1024),
        'manage_equipment_inventory_line': fields.one2many('tpt.manage.equipment.inventory','employee_id','Manage Equipment Inventory Line'),
    }
    
#     def init(self, cr):
#         try:
#             sql = '''
#                 ALTER TABLE resource_resource DROP COLUMN active;
#             '''
#             cr.execute(sql)
#         except Exception, e:
#             pass
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_contract_employee'):
            sql = '''
                
                select employee_id from arul_hr_employee_action_history where action_id in (select id from arul_employee_actions where name = 'Contracts') group by employee_id
                    
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
                
                select employee_id from arul_hr_employee_action_history where action_id in (select id from arul_employee_actions where name = 'Disciplinary') group by employee_id
                    
            '''%()
            cr.execute(sql)
            exist_employee_ids = [row[0] for row in cr.fetchall()]
            employee_ids = self.search(cr, uid, [('id','not in',exist_employee_ids)])
            if context.get('employee_id'):
                employee_ids.append(context.get('employee_id'))
            args += [('id','in',employee_ids)]
#         if context.get('search_promotion_employee'):
#             sql = '''
#                   
#                 select employee_id from arul_hr_employee_action_history where action_id in (select id from arul_employee_actions where name = 'Promotion') group by employee_id
#                       
#             '''%()
#             cr.execute(sql)
#             exist_employee_ids = [row[0] for row in cr.fetchall()]
#             employee_ids = self.search(cr, uid, [('id','not in',exist_employee_ids)])
#             employee_ids = self.search(cr, uid,[])
#             if context.get('employee_id'):
#                 employee_ids.append(context.get('employee_id'))
#             args += [('id','in',employee_ids)]
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if name:
            ids = self.search(cr, user, ['|',('name','like',name),('employee_id','like',name)]+args, context=context, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    def onchange_department_id(self, cr, uid, ids,department_id=False, context=None):
#         section_ids = []
#         if department_id:
#             dept = self.pool.get('hr.department').browse(cr, uid, department_id)
#             section_ids = [x.id for x in dept.section_ids]
        return {'value': {'section_id': False}}
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False,employee_sub_category_id=False, context=None):
        vals = {}
        if employee_category_id and employee_sub_category_id:
            sql = '''
                select id from hr_employee_sub_category where id = %s and category_id=%s
            '''%(employee_sub_category_id,employee_category_id)
            cr.execute(sql)
            sub_category_ids = [row[0] for row in cr.fetchall()]
            if not sub_category_ids:
                vals['employee_sub_category_id']=False
        return {'value': vals}

    def onchange_date_of_retirement(self, cr, uid, ids,birthday=False, context=None):
        retirement = ''
        if birthday:
            day = birthday[8:10]
            month = birthday[5:7]
            year = birthday[:4]
            if month == "01" and day=='01':
                year = int(year)+59
                num_of_month = calendar.monthrange(year,12)[1]
                retirement = datetime.datetime(year,12,num_of_month)
            elif month != "01" and day=='01':
                year = int(year)+60
                month = int(month)-1
                num_of_month = calendar.monthrange(year,month)[1]
                retirement = datetime.datetime(year,month,num_of_month)
            else:
                year = int(year)+60
                day = int(day)-1
                month = int(month)
                retirement = datetime.datetime(year,month,day)
        if retirement:
            retirement=retirement.strftime('%Y-%m-%d')
        return {'value': {'date_of_retirement':retirement}}
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if 'time_record' in vals:
            time_record = vals['time_record'].replace(" ","")
            vals['time_record'] = time_record
        new_id = super(hr_employee, self).create(cr, uid, vals, context)
        if context.get('create_hiring_employee'):
            for line_id in context.get('create_hiring_employee'):
                self.pool.get('arul.hr.employee.action.history').write(cr, uid, [line_id], {'employee_id': new_id})
        
        leave_obj = self.pool.get('arul.hr.leave.master')
        emp = self.browse(cr, uid, new_id)
        DATETIME_FORMAT = "%Y-%m-%d"
        now = time.strftime('%Y-%m-%d')
        date_now = datetime.datetime.strptime(now, DATETIME_FORMAT)
        if emp.date_of_joining:
            join_date = datetime.datetime.strptime(emp.date_of_joining, DATETIME_FORMAT)
            timedelta = date_now - join_date
        else:
            timedelta = date_now - date_now
        emp_all_lea_detail = []
        emp_category = emp.employee_category_id and emp.employee_category_id.id or False
        emp_sub = emp.employee_sub_category_id and emp.employee_sub_category_id.id or False
        leave_ids = leave_obj.search(cr, uid, [('employee_category_id','=',emp_category),('employee_sub_category_id','=',emp_sub)])
        for leave in leave_obj.browse(cr, uid, leave_ids):
            day = 0
            if leave.carryforward_nextyear:
                last_year = int(time.strftime('%Y')) - 1
                emp_leave_ids = self.pool.get('employee.leave').search(cr, uid, [('employee_id','=',emp.id),('year','=',str(last_year))])
                if emp_leave_ids:
                    for line in self.pool.get('employee.leave').browse(cr, uid, emp_leave_ids, context=context):
                        for leave_detail in line.emp_leave_details_ids:
                            if leave_detail.leave_type_id.id == leave.id and timedelta.days >= 365 and leave.leave_type_id.code in ['CL','SL','PL']:
                                day = line.total_day - line.taken_day + leave.condition
                            if leave_detail.leave_type_id.id == leave.id and leave.leave_type_id.code not in ['CL','SL','PL']:
                                day = line.total_day - line.taken_day + leave.condition
                else:
                    if timedelta.days < 365 and leave.leave_type_id.code in ['CL','SL','PL']:
                        day = 0
                    else:
                        day = leave.condition
            else:
                if timedelta.days < 365 and leave.leave_type_id.code in ['CL','SL','PL']:
                    day = 0
                else:
                    day = leave.condition
            emp_all_lea_detail.append((0,0,{'leave_type_id':leave.leave_type_id.id, 'total_day':day}))
        self.pool.get('employee.leave').create(cr, uid, {'employee_id':emp.id,'year': time.strftime('%Y'),'emp_leave_details_ids':emp_all_lea_detail})
        
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'time_record' in vals:
            time_record = vals['time_record'].replace(" ","")
            vals['time_record'] = time_record
        return super(hr_employee, self).write(cr, uid,ids, vals, context)
#     
#     def create(self, cr, uid, vals, context=None):
#         if context is None:
#             context = {}
#         new_id = super(hr_employee, self).create(cr, uid, vals, context)
#         if context.get('create_hiring_employee'):
#             for line_id in context.get('create_hiring_employee'):
#                 self.pool.get('arul.hr.employee.action.history').write(cr, uid, [line_id], {'employee_id': new_id})
#         return new_id
    def _check_time_record_id(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record_ids = self.search(cr, uid, [('id','!=',record.id),('time_record','=',record.time_record),('time_record','!=',False)])
            if record_ids:  
                return False
        return True
    
    def _check_date(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            if employee.date_of_joining and employee.date_of_resignation:
                if employee.date_of_joining >= employee.date_of_resignation:
                    raise osv.except_osv(_('Warning!'),_('Date Of Joining must be less than Date Of Resignation!'))
                    return False
        return True
    
    def _check_employee_id(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            record_ids = self.search(cr, uid, [('id','!=',record.id),('employee_id','=',record.employee_id),('employee_id','!=',False)])
            if record_ids:
                raise osv.except_osv(_('Warning!'),_('Employee ID already exists!'))
                return False
        return True
    
    _constraints = [
        (_check_date, 'Identical Data', ['date_of_joining','date_of_resignation']),
        (_check_time_record_id, 'Identical Data', ['time_record']),
    ]
hr_employee()
    
class arul_employee_actions(osv.osv):
    _name="arul.employee.actions"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True,readonly = True),
        'active':fields.boolean('Active'),
        'action_type_ids':fields.many2many('arul.employee.action.type','actions_action_type_ref','actions_id','action_type_id','Action Type'),
              }
    _defaults={
            'active':True,
               }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_employee_actions, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_employee_actions, self).write(cr, uid,ids, vals, context)
    
    def _check_code_id(self, cr, uid, ids, context=None):
        for actions in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_employee_actions where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(actions.id,actions.code,actions.name)
            cr.execute(sql)
            actions_ids = [row[0] for row in cr.fetchall()]
            if actions_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
arul_employee_actions()

class tpt_stream(osv.osv):
    _inherit = 'hr.qualification.attachment'
    _columns={
       'stream_id': fields.many2one('tpt.stream.master','Streams'),
              }
tpt_stream()

class tpt_stream_master(osv.osv):
    _name="tpt.stream.master"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
              }
tpt_stream_master()

class arul_employee_action_type(osv.osv):
    _name="arul.employee.action.type"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
              }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_employee_action_type, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_employee_action_type, self).write(cr, uid,ids, vals, context)
    
    def _check_code_id(self, cr, uid, ids, context=None):
        for type in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_employee_action_type where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(type.id,type.code,type.name)
            cr.execute(sql)
            type_ids = [row[0] for row in cr.fetchall()]
            if type_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]

arul_employee_action_type()

class food_subsidy(osv.osv):
    _name = "food.subsidy"
    
#     def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
#         res = {}
#         for price in self.browse(cr, uid, ids, context=context):
#             res[price.id] = {
#                 'employer_con': price.food_price*0.75,
#                 'employee_con': price.food_price*0.25,
#             }
#         return res

    def onchange_amount_all(self, cr, uid, ids, food_price, context=None):
        res = {}
        res = {
                'employer_con': food_price*0.75,
                'employee_con': food_price*0.25,
            }
        return {'value': res}
    
    _columns = {
        'food_category':fields.selection([('break_fast','Break Fast'),('lunch','Lunch'),('dinner','Dinner'),('midnight_tiffin','Midnight Tiffin')],'Food Category',required=True),
        'food_price': fields.float('Food Price (Rs.)',degits=(16,2)),
        'employer_con': fields.float('Employer Contribution (Rs.)',degits=(16,2)),
        'employee_con': fields.float('Employee Contribution (Rs.)',degits=(16,2)),
        'hotel_name':fields.char('Hotel', size=64, required = True),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'history_line': fields.one2many('food.subsidy','history_id','Histories',readonly = True),
        'history_id': fields.many2one('food.subsidy','Histories Line', ondelete='cascade'),
    }
    def write(self, cr, uid, ids, vals, context=None):
        for line in self.browse(cr,uid,ids):
#             res = {
#                     'food_category': line.food_category or False,
#                     'food_price': line.food_price or False,
#                     'employer_con': line.employer_con or False,
#                     'employee_con': line.employee_con or False,
#                     'hotel_name': line.hotel_name or False,
#                     'street': line.street or False,
#                     'street2': line.street2 or False,
#                     'zip': line.zip or False,
#                     'city': line.city or False,
#                     'state_id': line.state_id and line.state_id.id or False,
#                     'country_id': line.country_id and line.country_id.id or False,
#                     'history_id': line.id,
#                     }
            if 'food_price' in vals:
                default ={'history_id': line.id,'history_line':[]}
                self.copy(cr, uid, line.id,default)
#             self.create(cr,uid,res)
        return super(food_subsidy, self).write(cr, uid,ids, vals, context)
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['food_category'], context)
        for record in reads:
            name = record['food_category']
            if name=='break_fast':
                name = 'Break Fast'
            elif name=='lunch':
                name = 'Lunch'
            elif name=='dinner':
                name = 'Dinner'
            else:
                name = 'Midnight Tiffin'
            res.append((record['id'], name))
        return res  
    
    def _check_food_category(self, cr, uid, ids, context=None):
        for food in self.browse(cr, uid, ids, context=context):
            if not food.history_id:
                food_ids = self.search(cr, uid, [('id','!=',food.id),('food_category','=',food.food_category),('history_id','=',False)])
                if food_ids:  
                    return False
        return True

    _constraints = [
        (_check_food_category, 'Identical Data', ['food_category']),
    ]
    
food_subsidy()

class meals_deduction(osv.osv):
    _name = "meals.deduction"

    def onchange_date(self, cr, uid, ids, date, meals_for, context=None):
        vals = {}
        punch_obj = self.pool.get('arul.hr.punch.in.out.time')
        punch_ids = punch_obj.search(cr, uid, [('work_date','=',date)])
        emp_vals = []
        details_obj = self.pool.get('meals.details')
        details_ids = details_obj.search(cr, uid, [('meals_id','in',ids)])
        details_obj.unlink(cr, uid, details_ids)
        if meals_for == 'employees':
            for punch in punch_obj.browse(cr, uid, punch_ids):
                emp_vals.append((0,0,{'emp_id':punch.employee_id.id}))
        vals = {'meals_details_emp_ids':emp_vals,'meals_details_order_ids':[]}
        return {'value': vals}
   
    _columns = {
        'meals_date':fields.date('Meals Arrangement Date'),
        'meals_for':fields.selection([('employees','Employees'),('others','Others')],'Meals Arrangement For',required=True),
        'meals_details_emp_ids': fields.one2many('meals.details','meals_id','Meals Deduction Details'),
        'meals_details_order_ids': fields.one2many('meals.details','meals_id','Meals Deduction Details'),
    }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['meals_date'], context)
  
        for record in reads:
            name = record['meals_date']
            res.append((record['id'], name))
        return res  
meals_deduction()

class meals_details(osv.osv):
    _name = "meals.details"
    _description = "Meals Deduction"
    def evaluate_amt(self, cr, uid, ids, name, args, context=None):
        employer_amount = 0.0
        employee_amount = 0.0
        res = {}
        dict = {}
        food_subsidy_obj = self.pool.get('food.subsidy')
        for meal_de in self.browse(cr, uid, ids, context=context):
            if meal_de.meals_id.meals_for == "others":
                if meal_de.break_fast: 
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','break_fast'),('history_id','=',False)])
                    for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += (free1.employer_con + free1.employee_con)
                        employee_amount = 0.0
                if meal_de.lunch:
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','lunch'),('history_id','=',False)])
                    for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += (free1.employer_con + free1.employee_con)
                        employee_amount = 0.0
                if meal_de.dinner:
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','dinner'),('history_id','=',False)])
                    for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += (free1.employer_con + free1.employee_con)
                        employee_amount = 0.0
                if meal_de.midnight_tiffin:        
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','midnight_tiffin'),('history_id','=',False)])
                    for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += (free1.employer_con + free1.employee_con)
                        employee_amount = 0.0
            else:
                if meal_de.break_fast : 
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','break_fast'),('history_id','=',False)])
                    for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += meal.employer_con
                        employee_amount += meal.employee_con
                if meal_de .lunch: 
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','lunch'),('history_id','=',False)])
                    for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += meal.employer_con
                        employee_amount += meal.employee_con
                if meal_de.dinner : 
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','dinner'),('history_id','=',False)])
                    for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += meal.employer_con
                        employee_amount += meal.employee_con
                if meal_de.midnight_tiffin : 
                    food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','midnight_tiffin'),('history_id','=',False)])
                    for meal in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                        employer_amount += meal.employer_con
                        employee_amount += meal.employee_con
                if meal_de.free_cost_1 : 
                    if meal_de.break_fast and (meal_de.free_cost_1.food_category == "break_fast"): 
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','break_fast'),('history_id','=',False)])
                        for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free1.employee_con
                            employee_amount -= free1.employee_con
                    if meal_de.lunch and (meal_de.free_cost_1.food_category == "lunch"):
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','lunch'),('history_id','=',False)])
                        for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free1.employee_con
                            employee_amount -= free1.employee_con
                    if meal_de.dinner and (meal_de.free_cost_1.food_category == "dinner"):
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','dinner'),('history_id','=',False)])
                        for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free1.employee_con
                            employee_amount -= free1.employee_con
                    if meal_de.midnight_tiffin and (meal_de.free_cost_1.food_category == "midnight_tiffin"):        
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','midnight_tiffin'),('history_id','=',False)])
                        for free1 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free1.employee_con
                            employee_amount -= free1.employee_con  
                if meal_de.free_cost_2 : 
                    if meal_de.break_fast and (meal_de.free_cost_2.food_category == "break_fast"): 
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','break_fast'),('history_id','=',False)])
                        for free2 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free2.employee_con
                            employee_amount -= free2.employee_con
                    if meal_de.lunch and (meal_de.free_cost_2.food_category == "lunch"):
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','lunch'),('history_id','=',False)])
                        for free2 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free2.employee_con
                            employee_amount -= free2.employee_con
                    if meal_de.dinner and (meal_de.free_cost_2.food_category == "dinner"):
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','dinner'),('history_id','=',False)])
                        for free2 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free2.employee_con
                            employee_amount -= free2.employee_con
                    if meal_de.midnight_tiffin and (meal_de.free_cost_2.food_category == "midnight_tiffin"):        
                        food_subsidy_ids = food_subsidy_obj.search(cr, uid, [('food_category','=','midnight_tiffin'),('history_id','=',False)])
                        for free2 in food_subsidy_obj.browse(cr, uid, food_subsidy_ids):
                            employer_amount += free2.employee_con
                            employee_amount -= free2.employee_con  
            dict = {
                    'employer_amt': employer_amount,
                    'employee_amt': employee_amount,
                    }  
            res[meal_de.id] = dict
        return res
    _columns = {
#         'emp_code' : fields.char('Emp. Code', size=128),
        'emp_name' : fields.char('Name', size=128),
        'emp_id': fields.many2one('hr.employee', 'Emp. Code', select="1"),
        'break_fast' : fields.boolean('Break Fast'),
        'lunch' : fields.boolean('Lunch'),
        'dinner' : fields.boolean('Dinner'),
        'midnight_tiffin' : fields.boolean('Midnight Tiffin'),
        'employer_amt' : fields.function(evaluate_amt,digits=(16,2),type='float',string='Employer Amt',multi='sum',store=True),  
        'employee_amt' : fields.function(evaluate_amt,digits=(16,2),type='float',string='Employee Amt',multi='sum',store=True), 
        'free_cost_1' : fields.many2one('food.subsidy', 'Free Cost 1'),
        'free_cost_2' : fields.many2one('food.subsidy', 'Free Cost 2'),
        'meals_id': fields.many2one('meals.deduction','Meal Deduction'),
    }
    
meals_details()

class employee_leave(osv.osv):
    _name = "employee.leave"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=False,ondelete='cascade'),        
        'year': fields.char('Year',size=128, readonly=False),
        'emp_leave_details_ids': fields.one2many('employee.leave.detail','emp_leave_id','Employee Leave Details',readonly=False),
    }
    def get_employee_leave(self, cr, uid, context=None):
        day = 0
        vals = {}
        DATETIME_FORMAT = "%Y-%m-%d"
        
        emp_obj = self.pool.get('hr.employee') 
        leave_obj = self.pool.get('arul.hr.leave.master')
        leave_detail_obj = self.pool.get('employee.leave.detail')
        emp_ids = emp_obj.search(cr, uid, [])
        for emp in emp_obj.browse(cr, uid, emp_ids):
            year_now = time.strftime('%Y')
            employee_leave_ids = self.search(cr, uid, [('year','=',year_now),('employee_id','=',emp.id)])
            if not employee_leave_ids:
                if emp.date_of_joining:
                    join_date = datetime.datetime.strptime(emp.date_of_joining, DATETIME_FORMAT)
                    now = time.strftime('%Y-%m-%d')
                    date_now = datetime.datetime.strptime(now, DATETIME_FORMAT)
                    timedelta = date_now - join_date
                emp_all_lea_detail = []
                emp_category = emp.employee_category_id and emp.employee_category_id.id or False
                emp_sub = emp.employee_sub_category_id and emp.employee_sub_category_id.id or False
                leave_ids = leave_obj.search(cr, uid, [('employee_category_id','=',emp_category),('employee_sub_category_id','=',emp_sub)])
                for leave in leave_obj.browse(cr, uid, leave_ids):
                    day = 0
                    if leave.carryforward_nextyear:
                        last_year = int(time.strftime('%Y')) - 1
                        emp_leave_ids = self.search(cr, uid, [('employee_id','=',emp.id),('year','=',str(last_year))])
                        if emp_leave_ids:
                            for line in self.browse(cr, uid, emp_leave_ids, context=context):
                                for leave_detail in line.emp_leave_details_ids:
                                    if leave_detail.leave_type_id.id == leave.id and timedelta.days >= 365:
                                        day = line.total_day - line.taken_day + leave.condition
                        else:
                            if timedelta.days >= 365: 
                                day = leave.condition
                    else:
                        if timedelta.days >= 365: 
                            day = leave.condition
                    emp_all_lea_detail.append((0,0,{'leave_type_id':leave.leave_type_id.id, 'total_day':day}))
                self.pool.get('employee.leave').create(cr, uid, {'employee_id':emp.id,'year': time.strftime('%Y'),'emp_leave_details_ids':emp_all_lea_detail})
        return vals
    
    def get_employee_leave_daily(self, cr, uid, context=None):
        day = 0
        vals = {}
        emp_all_lea_detail = []
        DATETIME_FORMAT = "%Y-%m-%d"
        now = time.strftime('%Y-%m-%d')
        date_now = datetime.datetime.strptime(now, DATETIME_FORMAT)
        curr_year = time.strftime('%Y')
        emp_obj = self.pool.get('hr.employee')
        leave_obj = self.pool.get('arul.hr.leave.master')
        emp_ids = emp_obj.search(cr, uid, [])
        for emp in emp_obj.browse(cr, uid, emp_ids):
            emp_all_lea_detail = []
            emp_leave_ids = self.pool.get('employee.leave').search(cr, uid, [('employee_id','=',emp.id),('year','=',curr_year)])
            emp_category = emp.employee_category_id and emp.employee_category_id.id or False
            emp_sub = emp.employee_sub_category_id and emp.employee_sub_category_id.id or False
            if emp.date_of_joining:
                join_date = datetime.datetime.strptime(emp.date_of_joining, DATETIME_FORMAT)
                timedelta = date_now - join_date
            else:
                timedelta = date_now - date_now
            if emp_leave_ids and timedelta.days > 365:
                for line in self.pool.get('employee.leave').browse(cr, uid, emp_leave_ids, context=context):
                    master_leave_ids = leave_obj.search(cr, uid, [('employee_category_id','=',emp_category),('employee_sub_category_id','=',emp_sub)])
                    for master in leave_obj.browse(cr, uid, father_leave_ids):
                        for leave_detail in line.emp_leave_details_ids:
                            if master.leave_type_id.id == leave_detail.leave_type_id.id:
                                if leave_detail.total_day == 0 and leave_detail.leave_type_id.code in ['CL','SL','PL']:
                                    leave_type = leave_detail.leave_type_id and leave_detail.leave_type_id.id or False
                                    leave_ids = leave_obj.search(cr, uid, [('leave_type_id','=',leave_type),('employee_category_id','=',emp_category),('employee_sub_category_id','=',emp_sub)])
                                    for le in leave_obj.browse(cr, uid, leave_ids):
                                        day = le.condition
                                    self.pool.get('employee.leave.detail').write(cr, uid, [leave_detail.id] ,{'total_day':day})
                            else:
                                if master.carryforward_nextyear:
                                    last_year = int(time.strftime('%Y')) - 1
                                    emp_leave_ids = self.pool.get('employee.leave').search(cr, uid, [('employee_id','=',emp.id),('year','=',str(last_year))])
                                    if emp_leave_ids:
                                        for line in self.pool.get('employee.leave').browse(cr, uid, emp_leave_ids, context=context):
                                            for leave_detail in line.emp_leave_details_ids:
                                                if leave_detail.leave_type_id.id == master.id and timedelta.days > 365 and master.leave_type_id.code in ['CL','SL','PL']:
                                                    day = line.total_day - line.taken_day + master.condition
                                                if leave_detail.leave_type_id.id == master.id and master.leave_type_id.code not in ['CL','SL','PL']:
                                                    day = line.total_day - line.taken_day + master.condition
                                    else:
                                        if timedelta.days < 365 and master.leave_type_id.code in ['CL','SL','PL']:
                                            day = 0
                                        else:
                                            day = leave.condition
                                else:
                                    if timedelta.days < 365 and master.leave_type_id.code in ['CL','SL','PL']:
                                        day = 0
                                    else:
                                        day = leave.condition
                            self.pool.get('employee.leave.detail').create(cr, uid, {'emp_leave_id':line.id,'leave_type_id':master.leave_type_id.id, 'total_day':day})
                        
            if not emp_leave_ids:
                leave_ids = leave_obj.search(cr, uid, [('employee_category_id','=',emp_category),('employee_sub_category_id','=',emp_sub)])
                for leave in leave_obj.browse(cr, uid, leave_ids):
                    if leave.carryforward_nextyear:
                        last_year = int(time.strftime('%Y')) - 1
                        emp_leave_ids = self.pool.get('employee.leave').search(cr, uid, [('employee_id','=',emp.id),('year','=',str(last_year))])
                        if emp_leave_ids:
                            for line in self.pool.get('employee.leave').browse(cr, uid, emp_leave_ids, context=context):
                                for leave_detail in line.emp_leave_details_ids:
                                    if leave_detail.leave_type_id.id == leave.id and timedelta.days > 365 and leave.leave_type_id.code in ['CL','SL','PL']:
                                        day = line.total_day - line.taken_day + leave.condition
                                    if leave_detail.leave_type_id.id == leave.id and leave.leave_type_id.code not in ['CL','SL','PL']:
                                        day = line.total_day - line.taken_day + leave.condition
                        else:
                            if timedelta.days < 365 and leave.leave_type_id.code in ['CL','SL','PL']:
                                day = 0
                            else:
                                day = leave.condition
                    else:
                        if timedelta.days < 365 and leave.leave_type_id.code in ['CL','SL','PL']:
                            day = 0
                        else:
                            day = leave.condition
                    emp_all_lea_detail.append((0,0,{'leave_type_id':leave.leave_type_id.id, 'total_day':day}))
                self.pool.get('employee.leave').create(cr, uid, {'employee_id':emp.id,'year': time.strftime('%Y'),'emp_leave_details_ids':emp_all_lea_detail})
        return True                   
    
employee_leave()

class employee_leave_detail(osv.osv):
    _name = "employee.leave.detail"
    _description = "Employee Leave Details"
    
    def get_taken_day(self, cr, uid, ids, field_name, arg, context=None):
        taken_day = 0
        res = {}
        DATETIME_FORMAT = "%Y-%m-%d"
        timedelta = 0
        for line in self.browse(cr, uid, ids, context=context):
            emp = line.emp_leave_id and line.emp_leave_id.employee_id.id or False
            year = line.emp_leave_id and line.emp_leave_id.year or False
            leave_type = line.leave_type_id and line.leave_type_id.id or False
            leave_detail_obj = self.pool.get('arul.hr.employee.leave.details')
            emp_obj = self.pool.get('hr.employee')
            emp_ids = emp_obj.search(cr, uid, [('id','=', emp)])
            for ee in emp_obj.browse(cr, uid, emp_ids):
                if ee.date_of_joining:
                    join_date = datetime.datetime.strptime(ee.date_of_joining, DATETIME_FORMAT)
                    now = time.strftime('%Y-%m-%d')
                    date_now = datetime.datetime.strptime(now, DATETIME_FORMAT)
                    timedelta = date_now - join_date
            if line.leave_type_id.code=='LOP':
                shift_ids = self.pool.get('arul.hr.audit.shift.time').search(cr, uid, [('work_date','like',line.emp_leave_id.year),('employee_id','=',emp),('state','=','cancel')])
                taken_day += len(shift_ids)
            leave_detail_ids = leave_detail_obj.search(cr, uid, [('date_from','like',line.emp_leave_id.year),('employee_id','=',emp),('leave_type_id','=',leave_type),('state','!=','cancel')])
            for detail in leave_detail_obj.browse(cr, uid, leave_detail_ids, context=context):
                if not timedelta and (detail.leave_type_id.code=='CL' or detail.leave_type_id.code=='SL' or detail.leave_type_id.code=='PL'):
                    raise osv.except_osv(_('Warning!'),_('The Selected Employee does not reach 1 year from The Date of Joining'))
                elif timedelta and detail.date_from[0:4] == year and timedelta.days >= 365 and line.total_day != 0 and (detail.leave_type_id.code=='CL' or detail.leave_type_id.code=='SL' or detail.leave_type_id.code=='PL'):
                    taken_day += detail.days_total
                else:
                    taken_day += detail.days_total
            res[line.id] = taken_day
        return res
    
    def _get_leave_detail(self, cr, uid, ids, context=None):
        result = {}
        for leave_detail in self.pool.get('arul.hr.employee.leave.details').browse(cr, uid, ids):
            year_leave = leave_detail.date_from[:4]
            emp_leave_ids = self.pool.get('employee.leave').search(cr, uid, [('employee_id','=',leave_detail.employee_id.id),('year','=',year_leave)])
            emp_leave_dt_ids = self.pool.get('employee.leave.detail').search(cr, uid, [('emp_leave_id','in',emp_leave_ids),('leave_type_id','=',leave_detail.leave_type_id.id)])
            for line in emp_leave_dt_ids:
                result[line] = True
        return result.keys()
    
    def _get_audit(self, cr, uid, ids, context=None):
        result = {}
        for audit in self.pool.get('arul.hr.audit.shift.time').browse(cr, uid, ids):
            year_audit = audit.work_date[:4]
            emp_leave_ids = self.pool.get('employee.leave').search(cr, uid, [('employee_id','=',audit.employee_id.id),('year','=',year_audit)])
            leave_type_ids = self.pool.get('arul.hr.leave.types').search(cr, uid, [('code','=','LOP')])
            emp_leave_dt_ids = self.pool.get('employee.leave.detail').search(cr, uid, [('emp_leave_id','in',emp_leave_ids),('leave_type_id','in',leave_type_ids)])
            for line in emp_leave_dt_ids:
                result[line] = True
        return result.keys()
    
    _columns = {
        'emp_leave_id': fields.many2one('employee.leave', 'Employee Leave', readonly=True,ondelete='cascade'),
        'leave_type_id' : fields.many2one('arul.hr.leave.types', 'Leave Types', readonly=False),
        'total_day': fields.float('Total Day',degits=(16,2), readonly=False),
#         'total_taken': fields.float('Total Day',degits=(16,2)),
        'total_taken': fields.function(get_taken_day,degits=(16,2),store={
            'employee.leave.detail': (lambda self, cr, uid, ids, c={}: ids, ['total_day','leave_type_id','emp_leave_id'], 10),
            'arul.hr.employee.leave.details': (_get_leave_detail, ['employee_id','leave_type_id','date_from','date_to','haft_day_leave','state'], 10),
            'arul.hr.audit.shift.time': (_get_audit, ['employee_id','work_date','state'], 20),                                          
        }, type='float',string='Taken Day'),
#         'total_taken': fields.function(get_taken_day,degits=(16,2), type='float',string='Taken Day')
    }
    
employee_leave_detail()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

