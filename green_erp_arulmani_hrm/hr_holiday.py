# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import datetime
from datetime import datetime
import base64
import calendar
class arul_hr_holiday_special(osv.osv):
    _name = "arul.hr.holiday.special"
    _columns = {
        'name' : fields.char('Holiday Name', size = 1024, required = True),
        'date' : fields.date('Date', required = True),
    }
arul_hr_holiday_special()


class arul_hr_leave_master(osv.osv):
    _name = "arul.hr.leave.master"
    _columns = {
        'leave_type_id' : fields.many2one('arul.hr.leave.types', 'Leave Type', required = True),
        'employee_category_id' : fields.many2one('vsis.hr.employee.category', 'Employee Category'),
        'employee_sub_category_id' : fields.many2one('hr.employee.sub.category', 'Employee Sub Category'),
        'maximum_limit': fields.integer('Maximum Limit Applicable'),
        'carryforward_nextyear': fields.boolean('Is Carry Forward for Next Year'),
        'condition': fields.char('Eligible per Annum'),
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
#               'code': fields.function(_name_get_fnc, type="char", string='Code',required = True),
              'code':fields.char('Code',size=1024, required = True),
              'name':fields.char('Name',size=1024, required = True),
              'description':fields.text('Description'),
              'start_time': fields.float('Shift Start Time'),
              'end_time': fields.float('Shift End Time'),
              'time_total': fields.function(_time_total, string='Shift Total Hours', multi='sums', help="The total amount."),
              'allowance': fields.float('Shift Allowance'),
              }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['code'], context)
  
        for record in reads:
            name = record['code']
            res.append((record['id'], name))
        return res    
    
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
              'employee_id':fields.many2one('hr.employee','Employee ID', required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'work_date':fields.date('Work Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'employee_category_id':fields.many2one('vsis.hr.employee.category','Work Group', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'planned_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Planned Work Shift', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'in_time': fields.float('In Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'out_time': fields.float('Out Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'total_hours': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'approval': fields.boolean('Select for Approval', readonly =  True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('cancel', 'Reject'),('done', 'Approve')],'Status', readonly=True),
              }
    _defaults = {
        'state':'draft',
    }
    def _check_time(self, cr, uid, ids, context=None): 
        for time in self.browse(cr, uid, ids, context = context):
            if ((time.in_time > 24 or time.in_time < 0) or (time.out_time > 24 or time.out_time < 0)):
                raise osv.except_osv(_('Warning!'),_('Input Wrong Time!'))
                return False
            #if (time.in_time > time.out_time):
              #  raise osv.except_osv(_('Warning!'),_('In Time is earlier than Out Time'))
               # return False
            return True       
    _constraints = [
        (_check_time, _(''), ['in_time', 'out_time']),
    ]
    def onchange_category_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    }
        return {'value': vals}
    def approve_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
#             emp = self.pool.get('hr.employee')
            emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
            punch_obj = self.pool.get('arul.hr.punch.in.out.time')
            employee_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line.employee_id.id)])
            if employee_ids:
                
                val2={'punch_in_out_id':employee_ids[0], 
                      'employee_id': line.employee_id.id,
                      'work_date':line.work_date, 
                      'planned_work_shift_id':line.planned_work_shift_id.id,
                      'in_time':line.in_time,
                      'out_time':line.out_time,
                      'approval':1
                        }
                punch_obj.create(cr,uid,val2) 
            else:
                val1={
                      'employee_id':line.employee_id.id,
                      'work_date':line.work_date,
                      'planned_work_shift_id':line.planned_work_shift_id.id,
                      'in_time':line.in_time,
                      'out_time':line.out_time,
                      'approval':1
                      }
                emp_attendence_obj.create(cr,uid,{'employee_id':line.employee_id.id, 'employee_category_id':line.employee_id.employee_category_id.id, 'sub_category_id':line.employee_id.employee_sub_category_id.id, 'department_id':line.employee_id.department_id.id, 'punch_in_out_line':[(0,0,val1)]}) 
            self.write(cr, uid, [line.id],{'approval': True, 'state':'done'})
        return True
    def reject_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': False, 'state':'cancel'})
        return True   
arul_hr_audit_shift_time()

class arul_hr_employee_leave_details(osv.osv):
    _name='arul.hr.employee.leave.details'

    def days_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for date in self.browse(cr, uid, ids, context=context):
            DATETIME_FORMAT = "%Y-%m-%d"
            from_dt = datetime.datetime.strptime(date.date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date.date_to, DATETIME_FORMAT)
#             timedelta = to_dt - from_dt
            timedelta = (to_dt - from_dt).days+1
            if date.haft_day_leave:
                timedelta = timedelta-0.5
             
            leave_details_obj = self.pool.get('employee.leave.detail')
            emp_leave_obj = self.pool.get('employee.leave')
            year_now = time.strftime('%Y')
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',date.employee_id.id),('year','=',year_now)])
            if emp_leave_ids:
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                temp = 0
                for line in emp_leave.emp_leave_details_ids:
                    if line.leave_type_id.id == date.leave_type_id.id:
                        temp += 1
                        day = line.total_day - line.total_taken
                        if timedelta > day:
                            raise osv.except_osv(_('Warning!'),_('Exceeds Holiday Lets'))
                if temp == 0:
                    raise osv.except_osv(_('Warning!'),_('Leave Type Unlicensed'))
            else:
                raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Current Year'))
            res[date.id] = {
                'days_total': timedelta
            }
        return res
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'leave_type_id':fields.many2one('arul.hr.leave.types','Leave Type',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'date_from':fields.date('Date From', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'date_to': fields.date('To Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'days_total': fields.function(days_total, string='Leave Total',store=True, multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'haft_day_leave': fields.boolean('Is haft day leave ?', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'reason':fields.text('Reason', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Done')],'Status', readonly=True),
              }
    _defaults = {
        'state':'draft',
    }
    def onchange_date(self, cr, uid, ids, date_from=False, date_to=False,employee_id=False,leave_type_id=False,haft_day_leave=False, context=None):
        DATETIME_FORMAT = "%Y-%m-%d"
        if date_from and date_to and employee_id and leave_type_id:
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            timedelta = (to_dt - from_dt).days+1
            if haft_day_leave:
                timedelta = timedelta-0.5
            leave_details_obj = self.pool.get('employee.leave.detail')
            emp_leave_obj = self.pool.get('employee.leave')
            year_now = time.strftime('%Y')
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',employee_id),('year','=',year_now)])
            if emp_leave_ids:
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                temp = 0
                for line in emp_leave.emp_leave_details_ids:
                    if line.leave_type_id.id == leave_type_id:
                        temp += 1
                        day = line.total_day - line.total_taken
                        if timedelta > day:
                            raise osv.except_osv(_('Warning!'),_('Exceeds Holiday Lets'))
                if temp == 0:
                    raise osv.except_osv(_('Warning!'),_('Leave Type Unlicensed'))
            else:
                raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Current Year'))
        return True
    
    def process_leave_request(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'state':'done'})
        return True  
    
    def cancel_leave_request(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'state':'cancel'})
        return True  
    
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


class arul_hr_permission_onduty(osv.osv):
    _name='arul.hr.permission.onduty'
    
    def create(self, cr, uid, vals, context=None):
#         for line in self.browse(cr,uid,ids):
        new_id = super(arul_hr_permission_onduty, self).create(cr, uid, vals, context)
        line_id=self.browse(cr,uid,new_id)
        emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
        punch_obj = self.pool.get('arul.hr.permission.onduty')
        detail_obj4 = self.pool.get('arul.hr.punch.in.out.time')
        emp_attendence_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
        if emp_attendence_ids:
            if(line_id.non_availability_type_id == 'on_duty'):
                if(line_id.time_total > 8)and(line_id.time_total < 12):
                    val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':False,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                    sql = '''
                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                    '''%(line_id.start_time - 1,line_id.end_time + 1)
                    cr.execute(sql)
                    work_shift_ids = [row[0] for row in cr.fetchall()]
                    if work_shift_ids :
                        val['planned_work_shift_id']=work_shift_ids[0]
                        details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                        if details_ids:
                            val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':work_shift_ids[0],'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                            detail_obj4.create(cr, uid, val4)
                        else:
                            emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,'punch_in_out_line':[(0,0,val)]})
                if(line_id.time_total > 12)and(line_id.time_total < 16):
                    val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':False,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                    sql = '''
                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                    '''%(line_id.start_time - 1,line_id.end_time + 1)
                    cr.execute(sql)
                    work_shift_ids = [row[0] for row in cr.fetchall()]
                    if work_shift_ids :
                        val['planned_work_shift_id']=work_shift_ids[0]
                        details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                        if details_ids:
                            val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':work_shift_ids[0],'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                            detail_obj4.create(cr, uid, val4)
                        else:
                            emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,'punch_in_out_line':[(0,0,val)]})

                    
            val2={'permission_onduty_id':emp_attendence_ids[0], 
                    }
            punch_obj.write(cr,uid,[line_id.id],val2) 
        else:
            detail_vals = {'employee_id':line_id.employee_id.id,
                           'employee_category_id':line_id.employee_id.employee_category_id.id,
                           'sub_category_id':line_id.employee_id.employee_sub_category_id.id,
                           'department_id':line_id.employee_id.department_id.id,
                           'designation_id':line_id.employee_id.department_id and line_id.employee_id.department_id.designation_id.id or False}
            emp_attendence_id = emp_attendence_obj.create(cr,uid,detail_vals)
            if(line_id.non_availability_type_id == 'on_duty'):
                if(line_id.time_total > 8)and(line_id.time_total < 12):
                    val={'permission_onduty_id':emp_attendence_id,'planned_work_shift_id':False,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                    sql = '''
                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                    '''%(line_id.start_time - 1,line_id.end_time + 1)
                    cr.execute(sql)
                    work_shift_ids = [row[0] for row in cr.fetchall()]
                    if work_shift_ids :
                        val['planned_work_shift_id']=work_shift_ids[0]
                        details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                        if details_ids:
                            val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':work_shift_ids[0],'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                            detail_obj4.create(cr, uid, val4)
                        else:
                            emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,'punch_in_out_line':[(0,0,val)]})
                if(line_id.time_total > 12)and(line_id.time_total < 16):
                    val={'permission_onduty_id':emp_attendence_id,'planned_work_shift_id':False,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                    sql = '''
                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                    '''%(line_id.start_time - 1,line_id.end_time + 1)
                    cr.execute(sql)
                    work_shift_ids = [row[0] for row in cr.fetchall()]
                    if work_shift_ids :
                        val['planned_work_shift_id']=work_shift_ids[0]
                        details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                        if details_ids:
                            val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':work_shift_ids[0],'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                            detail_obj4.create(cr, uid, val4)
                        else:
                            emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,'punch_in_out_line':[(0,0,val)]})
            punch_obj.write(cr,uid,[line_id.id],{'permission_onduty_id':emp_attendence_id}) 
#             self.write(cr, uid, [line.id],{'approval': True})
        return new_id
#     def write(self, cr, uid, ids, vals, context=None):
#         new_id = super(arul_hr_permission_onduty, self).write(cr, uid, ids, vals, context=context)
#         for line_id in self.browse(cr,uid,ids):
#             emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
#             punch_obj = self.pool.get('arul.hr.permission.onduty')
#             detail_obj4 = self.pool.get('arul.hr.punch.in.out.time')
#             emp_attendence_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
#             if emp_attendence_ids:
#                 if(line_id.non_availability_type_id == 'on_duty'):
#                     if(line_id.time_total > 8)and(line_id.time_total < 12):
#                         val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':False,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                         sql = '''
#                             select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
#                         '''%(line_id.start_time - 1,line_id.end_time + 1)
#                         cr.execute(sql)
#                         work_shift_ids = [row[0] for row in cr.fetchall()]
#                         if work_shift_ids :
#                             val['planned_work_shift_id']=work_shift_ids[0]
#                             details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
#                             if details_ids:
#                                 val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':work_shift_ids[0],'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                                 detail_obj4.create(cr, uid, val4)
#                             else:
#                                 emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,'punch_in_out_line':[(0,0,val)]})
#                     if(line_id.time_total > 12)and(line_id.time_total < 16):
#                         val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':False,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                         sql = '''
#                             select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
#                         '''%(line_id.start_time - 1,line_id.end_time + 1)
#                         cr.execute(sql)
#                         work_shift_ids = [row[0] for row in cr.fetchall()]
#                         if work_shift_ids :
#                             val['planned_work_shift_id']=work_shift_ids[0]
#                             details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
#                             if details_ids:
#                                 val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':work_shift_ids[0],'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                                 detail_obj4.create(cr, uid, val4)
#                             else:
#                                 emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,'punch_in_out_line':[(0,0,val)]})
#     
#                         
#                 val2={'permission_onduty_id':emp_attendence_ids[0], 
#                         }
#                 sql = '''
#                     update arul_hr_permission_onduty set permission_onduty_id=%s where id = %s
#                 '''%(emp_attendence_ids[0],line_id.id)
#                 cr.execute(sql)
#             else:
#                 detail_vals = {'employee_id':line_id.employee_id.id,
#                                'employee_category_id':line_id.employee_id.employee_category_id.id,
#                                'sub_category_id':line_id.employee_id.employee_sub_category_id.id,
#                                'department_id':line_id.employee_id.department_id.id,
#                                'designation_id':line_id.employee_id.department_id and line_id.employee_id.department_id.designation_id.id or False}
#                 emp_attendence_id = emp_attendence_obj.create(cr,uid,detail_vals)
#                 sql = '''
#                     update arul_hr_permission_onduty set permission_onduty_id=%s where id = %s
#                 '''%(emp_attendence_id,line_id.id)
#                 cr.execute(sql)
#         return new_id
#     
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
        'employee_id':fields.many2one('hr.employee','Employee',required=True),
        'non_availability_type_id':fields.selection([('permission','Permission'),('on_duty','On duty')],'Non Availability Type',required = True),
        'date':fields.date('Date'),
        'duty_location':fields.char('On Duty Location', size = 1024),
        'start_time': fields.float('Start Time'),
        'end_time': fields.float('End Time'),
        'time_total': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount."),
        'reason':fields.text('Reason'),
        'permission_onduty_id':fields.many2one('arul.hr.employee.attendence.details','Permission/Onduty'),
#         'detail_id':fields.many2one('arul.hr.employee.attendence.details','Detail'),
        
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

class arul_hr_punch_in_out_time(osv.osv):
    _inherit='arul.hr.audit.shift.time'
    _name='arul.hr.punch.in.out.time'
    _columns = {
        'punch_in_out_id':fields.many2one('arul.hr.employee.attendence.details','Punch in/out')
    }
arul_hr_punch_in_out_time()

class arul_hr_employee_attendence_details(osv.osv):
    _name='arul.hr.employee.attendence.details'
    _columns={
        'employee_id':fields.many2one('hr.employee','Employee', required=True),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category',readonly=False),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category',readonly=False),
        'designation_id': fields.many2one('hr.job', 'Designation',readonly=False),
        'department_id':fields.many2one('hr.department', 'Department',readonly=False),
        'permission_onduty_details_line':fields.one2many('arul.hr.permission.onduty','permission_onduty_id','Permission On duty Details',readonly=True),
        'punch_in_out_line':fields.one2many('arul.hr.punch.in.out.time','punch_in_out_id','Punch in/Punch out Details',readonly=True)
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
    def onchange_department_id(self, cr, uid, ids,department_id=False, context=None):
        designation_ids = []
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            for line in department.designation_line:
                designation_ids.append(line.designation_id.id)
        return {'value': {'designation_id': False }, 'domain':{'designation_id':[('id','in',designation_ids)]}}
    
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

class arul_hr_punch_in_out(osv.osv):
    _name = 'arul.hr.punch.in.out'
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
            super(arul_hr_punch_in_out, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(arul_hr_punch_in_out, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Up load', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Upload/View Specification', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)

    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    def upload_punch_in_out(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            try:
                recordlist = base64.decodestring(line.db_datas)
                L = recordlist.split('\n')
                employee_obj = self.pool.get('hr.employee')
                detail_obj = self.pool.get('arul.hr.employee.attendence.details')
                detail_obj2 = self.pool.get('arul.hr.audit.shift.time')
                detail_obj3 = self.pool.get('arul.hr.capture.work.shift')
                detail_obj4 = self.pool.get('arul.hr.punch.in.out.time')
                for i,data1 in enumerate(L):
                    if data1 and data1[:3]!='P10' and data1[:3]!='P20':
                        raise osv.except_osv(_('Warning!'),_('Line %s Data Mismatch!')%(i+1))
                    L2 = L[i+1:]
                    employee_code = data1[43:51]
                    employee_ids = employee_obj.search(cr, uid, [('employee_id','=',employee_code)])
                    date = data1[7:11]+'-'+data1[11:13]+'-'+data1[13:15]
                    temp = 0
                    if employee_ids and date:
                        employee = employee_obj.browse(cr, uid, employee_ids[0])
                        if data1[:3]=='P10':
                            in_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            val1={'employee_id':employee_ids[0],'planned_work_shift_id':False,'work_date':date,'in_time':in_time,'out_time':0,'approval':1}
                            for j,data2 in enumerate(L2):
                                #bat dau vi tri tiep theo cua for 1
                                in_out = data2[:3]
                                employee_code_2=data2[43:51]
                                date_2=data2[7:11]+'-'+data2[11:13]+'-'+data2[13:15]
                                if employee_code_2==employee_code and date==date_2 and in_out=='P10':
                                    in_time2 = float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                    val1={'employee_id':employee_ids[0],'planned_work_shift_id':False,'work_date':date,'in_time':in_time2,'out_time':0,'approval':1}
                                if employee_code_2==employee_code and date==date_2 and in_out=='P20':
                                    out_time=float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                    val1['out_time']=out_time
                                    sql = '''
                                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                                    '''%(in_time - 1,out_time + 1)
                                    cr.execute(sql)
                                    work_shift_ids = [row[0] for row in cr.fetchall()]
                                    if work_shift_ids :
                                        val1['planned_work_shift_id']=work_shift_ids[0]
                                        details_ids=detail_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                                        if details_ids:
                                            val4={'punch_in_out_id':details_ids[0],'planned_work_shift_id':work_shift_ids[0],'employee_id':employee_ids[0],'work_date':date,'in_time':in_time,'out_time':out_time,'approval':1}
                                            detail_obj4.create(cr, uid, val4)
                                        else:
                                            detail_obj.create(cr, uid, {'employee_id':employee_ids[0],'punch_in_out_line':[(0,0,val1)]})
                                    else:
                                        val1['approval']=False
                                        val1['employee_category_id'] = employee.employee_category_id.id
                                        detail_obj2.create(cr, uid,val1)
                                    temp +=1
                                    L.pop(j)
                                    break
                            if temp==0:
                                val={'employee_id':employee_ids[0],'work_date':date,'in_time':in_time,'out_time':0,'employee_category_id':employee.employee_category_id.id}
                                detail_obj2.create(cr, uid,val)
                        if data1[:3]=='P20':
                            out_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            val2={'employee_id':employee_ids[0],'work_date':date,'in_time':0,'out_time':out_time,'employee_category_id':employee.employee_category_id.id}
                            detail_obj2.create(cr, uid,val2)
                            
                self.write(cr, uid, [line.id], {'state':'done'})
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))


arul_hr_punch_in_out()

class arul_hr_monthly_work_schedule(osv.osv):
    _name='arul.hr.monthly.work.schedule'
    
    _columns={
              'department_id':fields.many2one('hr.department','Department', required = True, states={'done': [('readonly', True)]}),
              'section_id': fields.many2one('arul.hr.section','Section', required = True, states={'done': [('readonly', True)]}),
              'year': fields.selection([(num, str(num)) for num in range(1950, 2026)], 'Year', required = True, states={'done': [('readonly', True)]}),
              'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True, states={'done': [('readonly', True)]}),
              'monthly_shift_line': fields.one2many('arul.hr.monthly.shift.schedule','monthly_work_id', 'Monthly Work Schedule', states={'done': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('load', 'Load'),('done', 'Done')],'Status', readonly=True)
              }
    _defaults = {
        'state':'draft',
        
    }
    
    def _check_month_year(self, cr, uid, ids, context=None):
        for work in self.browse(cr, uid, ids, context=context):
            work_ids = self.search(cr, uid, [('id','!=',work.id),('year','=',work.year),('month','=',work.month),('department_id','=',work.department_id.id),('section_id','=',work.section_id.id)])
            if work_ids:
                raise osv.except_osv(_('Warning!'),_('The monthly work schedule has already existed!'))
                return False
        return True
    _constraints = [
        (_check_month_year, 'Identical Data', ['month','year']),
    ]
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['year', 'month'], context)
        for line in self.browse(cr,uid,ids):
            for record in reads:
                year = str(line.year)
                month = str(line.month)
                name = month + ' - ' + year
                res.append((record['id'], name))
            return res  
    
    def load_previous_month(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if line.month=='1':
                year = int(line.year)-1
                month = 12
            else:
                month = int(line.month)-1
                year = line.year
            work_schedule_pre_ids = self.search(cr, uid, [('year','=',str(year)),('month','=',str(month)),('department_id','=',line.department_id.id)])
            if work_schedule_pre_ids:
                work_vals = []
                work_schedule_pre = self.browse(cr, uid, work_schedule_pre_ids[0])
                sql = '''
                    delete from arul_hr_monthly_shift_schedule where monthly_work_id = %s
                '''%(line.id)
                cr.execute(sql)
                for work in work_schedule_pre.monthly_shift_line:
                    work_vals.append((0,0,{
                                           'employee_id': work.employee_id.id,
                                           'day_1': work.day_1.id,
                                           'day_2': work.day_2.id,
                                           'day_3': work.day_3.id,
                                           'day_4': work.day_4.id,
                                           'day_5': work.day_5.id,
                                           'day_6': work.day_6.id,
                                           'day_7': work.day_7.id,
                                           'day_8': work.day_8.id,
                                           'day_9': work.day_9.id,
                                           'day_10': work.day_10.id,
                                           'day_11': work.day_11.id,
                                           'day_12': work.day_12.id,
                                           'day_13': work.day_13.id,
                                           'day_14': work.day_14.id,
                                           'day_15': work.day_15.id,
                                           'day_16': work.day_16.id,
                                           'day_17': work.day_17.id,
                                           'day_18': work.day_18.id,
                                           'day_19': work.day_19.id,
                                           'day_20': work.day_20.id,
                                           'day_21': work.day_21.id,
                                           'day_22': work.day_22.id,
                                           'day_23': work.day_23.id,
                                           'day_24': work.day_24.id,
                                           'day_25': work.day_25.id,
                                           'day_26': work.day_26.id,
                                           'day_27': work.day_27.id,
                                           'day_28': work.day_28.id,
                                           'day_29': work.day_29.id,
                                           'day_30': work.day_30.id,
                                           'day_31': work.day_31.id,
                                           }))
                self.write(cr, uid, [line.id], {'monthly_shift_line':work_vals,'state':'load'})
        return True
    def approve_current_month(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'})
    def onchange_department_id(self, cr, uid, ids,department_id=False,month=False,year=False, context=None):
        res = {'value':{}}
        for line in self.browse(cr, uid, ids):
            sql = '''
                delete from arul_hr_monthly_shift_schedule where monthly_work_id = %s
            '''%(line.id)
            cr.execute(sql)
        section_ids = []
        employee_lines = []
        num_of_month = 0
        if department_id: 
            if month and year:
                num_of_month = calendar.monthrange(int(year),int(month))[1]
            dept = self.pool.get('hr.department').browse(cr, uid, department_id)
            section_ids = [x.id for x in dept.section_ids]
            employee_obj=self.pool.get('hr.employee')
            employee_ids = employee_obj.search(cr, uid, [('department_id','=',department_id )])
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id,
                      'num_of_month': num_of_month,
                      }
                employee_lines.append((0,0,rs))
        return {'value': {'section_id':False,'monthly_shift_line':employee_lines}, 'domain':{'section_id':[('id','in',section_ids)]}}
    
    def onchange_year_month(self, cr, uid, ids,department_id=False,month=False,year=False, context=None):
        res = {'value':{}}
        for line in self.browse(cr, uid, ids):
            sql = '''
                delete from arul_hr_monthly_shift_schedule where monthly_work_id = %s
            '''%(line.id)
            cr.execute(sql)
        section_ids = []
        employee_lines = []
        num_of_month = 0
        if department_id: 
            if month and year:
                num_of_month = calendar.monthrange(int(year),int(month))[1]
            dept = self.pool.get('hr.department').browse(cr, uid, department_id)
            section_ids = [x.id for x in dept.section_ids]
            employee_obj=self.pool.get('hr.employee')
            employee_ids = employee_obj.search(cr, uid, [('department_id','=',department_id )])
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id,
                      'num_of_month': num_of_month,
                      }
                employee_lines.append((0,0,rs))
        return {'value': {'monthly_shift_line':employee_lines}, 'domain':{'section_id':[('id','in',section_ids)]}}
        
        
arul_hr_monthly_work_schedule()

class arul_hr_monthly_shift_schedule(osv.osv):
    _name='arul.hr.monthly.shift.schedule'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(arul_hr_monthly_shift_schedule, self).default_get(cr, uid, fields, context=context)
        if 'num_of_month' in fields and context.get('month') and context.get('year'):
            num_of_month = calendar.monthrange(int(context.get('year')),int(context.get('month')))[1]
            res.update({'num_of_month': num_of_month})
        return res
    
#     def _num_of_month(self, cr, uid, ids, field_name, arg, context=None):
#         res = {}
#         for day in self.browse(cr, uid, ids):
#             res[day.id] = {
#                 'num_of_month': 0,
#             }
#             num_day = calendar.monthrange(int(day.monthly_work_id.year),int(day.monthly_work_id.month))[1]  
#             res[day.id]['num_of_month'] = num_day 
#         return res
    _columns={
#               'num_of_month': fields.function(_num_of_month, string='Day',store=True, multi='sums', help="The total amount."),
              'num_of_month': fields.integer('Day'),
              'employee_id':fields.many2one('hr.employee','Employee', required = True),
              'monthly_work_id':fields.many2one('arul.hr.monthly.work.schedule','Monthly Shift Schedule'),
              'day_1': fields.many2one('arul.hr.capture.work.shift','1'),
              'day_2': fields.many2one('arul.hr.capture.work.shift','2'),
              'day_3': fields.many2one('arul.hr.capture.work.shift','3'),
              'day_4': fields.many2one('arul.hr.capture.work.shift','4'),
              'day_5': fields.many2one('arul.hr.capture.work.shift','5'),
              'day_6': fields.many2one('arul.hr.capture.work.shift','6'),
              'day_7': fields.many2one('arul.hr.capture.work.shift','7'),
              'day_8': fields.many2one('arul.hr.capture.work.shift','8'),
              'day_9': fields.many2one('arul.hr.capture.work.shift','9'),
              'day_10': fields.many2one('arul.hr.capture.work.shift','10'),
              'day_11': fields.many2one('arul.hr.capture.work.shift','11'),
              'day_12': fields.many2one('arul.hr.capture.work.shift','12'),
              'day_13': fields.many2one('arul.hr.capture.work.shift','13'),
              'day_14': fields.many2one('arul.hr.capture.work.shift','14'),
              'day_15': fields.many2one('arul.hr.capture.work.shift','15'),
              'day_16': fields.many2one('arul.hr.capture.work.shift','16'),
              'day_17': fields.many2one('arul.hr.capture.work.shift','17'),
              'day_18': fields.many2one('arul.hr.capture.work.shift','18'),
              'day_19': fields.many2one('arul.hr.capture.work.shift','19'),
              'day_20': fields.many2one('arul.hr.capture.work.shift','20'),
              'day_21': fields.many2one('arul.hr.capture.work.shift','21'),
              'day_22': fields.many2one('arul.hr.capture.work.shift','22'),
              'day_23': fields.many2one('arul.hr.capture.work.shift','23'),
              'day_24': fields.many2one('arul.hr.capture.work.shift','24'),
              'day_25': fields.many2one('arul.hr.capture.work.shift','25'),
              'day_26': fields.many2one('arul.hr.capture.work.shift','26'),
              'day_27': fields.many2one('arul.hr.capture.work.shift','27'),
              'day_28': fields.many2one('arul.hr.capture.work.shift','28'),
              'day_29': fields.many2one('arul.hr.capture.work.shift','29'),
              'day_30': fields.many2one('arul.hr.capture.work.shift','30'),
              'day_31': fields.many2one('arul.hr.capture.work.shift','31'),
              }
arul_hr_monthly_shift_schedule()
