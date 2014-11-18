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

class arul_hr_employee_leave_details(osv.osv):
    _name='arul.hr.employee.leave.details'

    def days_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for date in self.browse(cr, uid, ids, context=context):
            DATETIME_FORMAT = "%Y-%m-%d"
            from_dt = datetime.strptime(date.date_from, DATETIME_FORMAT)
            to_dt = datetime.strptime(date.date_to, DATETIME_FORMAT)
            timedelta = to_dt - from_dt
            res[date.id] = {
                'days_total': timedelta.days
            }
        return res
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee'),
              'leave_type_id':fields.many2one('arul.hr.leave.types','Leave Type',required=True),
              'date_from':fields.date('Date From'),
              'date_to': fields.date('To Date'),
              'days_total': fields.function(days_total, string='Leave Total', multi='sums', help="The total amount.",required=True),
              'haft_day_leave': fields.boolean('Is haft day leave ?'),
              'reason':fields.text('Reason')
              }
    def _check_days(self, cr, uid, ids, context=None): 
        for days in self.browse(cr, uid, ids, context = context):
            if ((days.date_from > days.date_to)):
                raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))
                return False
            return True       
    _constraints = [
        (_check_days, _(''), ['date_from', 'date_to']),
    ]
arul_hr_employee_leave_details()

class arul_permission_onduty(osv.osv):
    _name = 'arul.permission.onduty'
    _columns = {
        'name': fields.char('Name',size=1024, required=True),
    }
    
    def init(self, cr):
        for key in ['Permission','On Duty']:
            arul_ids = self.search(cr, 1, [('name','=',key)])
            if not arul_ids:
                self.create(cr, 1, {'name': key})
    
arul_permission_onduty()

class arul_hr_permission_onduty(osv.osv):
    _name='arul.hr.permission.onduty'
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
        'employee_id':fields.many2one('hr.employee','Employee'),
        'non_availability_type_id':fields.many2one('arul.permission.onduty','Non Availability Type',required = True),
        'date':fields.date('Date'),
        'duty_location':fields.char('On Duty Location', size = 1024),
        'start_time': fields.float('Start Time'),
        'end_time': fields.float('End Time'),
        'time_total': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount."),
        'reason':fields.text('Reason'),
        'detail_id':fields.many2one('arul.hr.employee.attendence.details','Detail'),
              }
    def _check_time(self, cr, uid, ids, context=None): 
        for time in self.browse(cr, uid, ids, context = context):
            if ((time.start_time > 24 or time.start_time < 0) or (time.end_time > 24 or time.end_time < 0)):
                raise osv.except_osv(_('Warning!'),_('Input Wrong Time!'))
                return False
            if (time.start_time > time.end_time):
                raise osv.except_osv(_('Warning!'),_('Start Time is earlier than End Time'))
                return False
            return True       
    _constraints = [
        (_check_time, _(''), ['start_time', 'end_time']),
        ]
   
arul_hr_permission_onduty()

class arul_hr_employee_attendence_details(osv.osv):
    _name='arul.hr.employee.attendence.details'
    _columns={
        'employee_id':fields.many2one('hr.employee','Employee'),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category'),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category'),
        'designation_id': fields.many2one('arul.hr.designation', 'Designation'),
        'department_id':fields.many2one('hr.department', 'Department'),
        'permission_onduty_details_line':fields.one2many('arul.hr.permission.onduty','detail_id','Permission On duty Details',readonly=True)
              }
    def onchange_attendence_datails_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'department_id':emp.department_id.id,
                    }
        return {'value': vals}
    def onchange_designation_id(self, cr, uid, ids,department_id=False, context=None):
        vals = {}
        if department_id:
            emp = self.pool.get('hr.department').browse(cr, uid, department_id)
            vals = {'designation_id':emp.designation_id.id,
                   }
        return {'value': vals}
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_employee_id'):
#             
#             sql = '''
#                 
#                 select employee_id from arul.hr.permission.onduty
#                     
#             '''
#             cr.execute(sql)
#             employee_id_ids = [row[0] for row in cr.fetchall()]
#             args += [('id','in',employee_id_ids)]
#         return super(hr.employee, self).search(cr, uid, args, offset, limit, order, context, count)

arul_hr_employee_attendence_details()



