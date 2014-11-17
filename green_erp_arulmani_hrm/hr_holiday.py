# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class arul_hr_holiday_special(osv.osv):
    _name = "arul.hr.holiday.special"
    _columns = {
        'name' : fields.char('Holiday Name', size = 1024),
        'date' : fields.date('Date'),
    }
arul_hr_holiday_special()


class arul_hr_leave_master(osv.osv):
    _name = "arul.hr.leave.master"
    _columns = {
        'leave_type_id' : fields.many2one('arul.hr.leave.types', 'Leave Type'),
        'employee_category_id' : fields.many2one('vsis.hr.employee.category', 'Employee Category'),
        'employee_sub_category_id' : fields.many2one('hr.employee.sub.category', 'Employee Sub Category'),
        'maximum_limit': fields.integer('Maximum Limit Applicable'),
        'carryforward_nextyear': fields.boolean('Is Carry Forward for Next Year'),
        'condition': fields.text('Eligible per Annum'),
    }
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
        emp_sub_cat = []
        if employee_category_id:
            emp_cat = self.pool.get('vsis.hr.employee.category').browse(cr, uid, employee_category_id)
            emp_sub_cat = [x.id for x in emp_cat.sub_category_ids]
        return {'value': {'employee_sub_category_id': False }, 'domain':{'employee_sub_category_id':[('id','in',emp_sub_cat)]}}
    
arul_hr_leave_master()

class arul_hr_leave_types(osv.osv):
    _name='arul.hr.leave.types'
    _columns={
              'code':fields.char('Code',size=256,required = True),
              'name':fields.char('Name',size=256,required =True)
              }
    def _check_code(self, cr, uid, ids, context=None):
        for leave in self.browse(cr, uid, ids, context=context):
            leave_ids = self.search(cr, uid, [('id','!=',leave.id),('code','=',leave.code)])
            if leave_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_hr_leave_types()

class arul_hr_capture_work_shift(osv.osv):
    _name='arul.hr.capture.work.shift'
    
    def _time_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for time in self.browse(cr, uid, ids, context=context):
            res[time.id] = {
                'time_total': 0.0,
            }
            time_total = time.end_time - time.start_time
            res[time.id]['time_total'] = time_total 
        return res
    
    _columns={
              'code':fields.char('Code',size=1024, required = True),
              'name':fields.char('Name',size=1024, required = True),
              'description':fields.text('Description'),
              'start_time': fields.float('Shift Start Time'),
              'end_time': fields.float('Shift End Time'),
              'time_total': fields.function(_time_total, string='Shift Total Hours', multi='sums', help="The total amount."),
              'allowance': fields.text('Shift Allowance'),
              }
    def _check_code(self, cr, uid, ids, context=None):
        for shift in self.browse(cr, uid, ids, context=context):
            shift_ids = self.search(cr, uid, [('id','!=',shift.id),('code','=',shift.code)])
            if shift_ids:  
                return False
        return True
    
    def _check_time(self, cr, uid, ids, context=None): 
        for time in self.browse(cr, uid, ids, context = context):
            if ((time.start_time > 24 or time.start_time < 0) or (time.end_time > 24 or time.end_time < 0)):
                raise osv.except_osv(_('Warning!'),_('Input Wrong Time!'))
                return False
            if (time.start_time > time.end_time):
                raise osv.except_osv(_('Warning!'),_('Shift Start Time is earlier than Shift End Time'))
                return False
            return True       
    _constraints = [
        (_check_time, _(''), ['start_time', 'end_time']),
    ]   

arul_hr_capture_work_shift()

class arul_hr_audit_shift_time(osv.osv):
    _name='arul.hr.audit.shift.time'
    
    def _time_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for time in self.browse(cr, uid, ids, context=context):
            res[time.id] = {
                'total_hours': 0.0,
            }
            time_total = time.out_time - time.in_time
            res[time.id]['total_hours'] = time_total 
        return res
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee ID', required = True),
              'work_date':fields.date('Work Date'),
              'planned_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Planned Work Shift'),
              'actual_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Actual Work Shift'),
              'in_time': fields.float('In Time'),
              'out_time': fields.float('Out Time'),
              'total_hours': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount."),
              'approval': fields.boolean('Select for Approval', readonly = True),
              }
    def _check_time(self, cr, uid, ids, context=None): 
        for time in self.browse(cr, uid, ids, context = context):
            if ((time.in_time > 24 or time.in_time < 0) or (time.out_time > 24 or time.out_time < 0)):
                raise osv.except_osv(_('Warning!'),_('Input Wrong Time!'))
                return False
            if (time.in_time > time.out_time):
                raise osv.except_osv(_('Warning!'),_('In Time is earlier than Out Time'))
                return False
            return True       
    _constraints = [
        (_check_time, _(''), ['in_time', 'out_time']),
    ]
    def approve_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': True})
        return True
    def reject_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': False})
        return True   
arul_hr_audit_shift_time()



