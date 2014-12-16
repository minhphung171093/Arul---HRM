# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
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
        'employee_category_id' : fields.many2one('vsis.hr.employee.category', 'Employee Category', required = True),
        'employee_sub_category_id' : fields.many2one('hr.employee.sub.category', 'Employee Sub Category', required = True),
        'maximum_limit': fields.integer('Maximum Limit Applicable'),
        'carryforward_nextyear': fields.boolean('Is Carry Forward for Next Year'),
        'condition': fields.integer('Eligible per Annum'),
    }
    def _check_sub_category_id(self, cr, uid, ids, context=None):
        for sub_cate in self.browse(cr, uid, ids, context=context):
            sub_cate_ids = self.search(cr, uid, [('id','!=',sub_cate.id),('leave_type_id','=',sub_cate.leave_type_id.id),('employee_category_id','=',sub_cate.employee_category_id.id),('employee_sub_category_id','=',sub_cate.employee_sub_category_id.id)])
            if sub_cate_ids:
                raise osv.except_osv(_('Warning!'),_('The data is not suitable!'))  
                return False
        return True
    _constraints = [
        (_check_sub_category_id, 'Identical Data', ['leave_type_id','employee_category_id','employee_sub_category_id']),
        ]
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['leave_type_id'], context)
  
        for record in reads:
            name = record['leave_type_id']
            res.append((record['id'], name))
        return res 
    
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
            
            if time.start_time > time.end_time:
                time_total = 24-time.start_time + time.end_time
            else:
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
            if time.in_time > time.out_time:
                time_total = 24-time.in_time + time.out_time
            else:
                time_total = time.out_time - time.in_time
            res[time.id]['total_hours'] = time_total 
        return res
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee ID', required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'work_date':fields.date('Work Date', required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'employee_category_id':fields.many2one('vsis.hr.employee.category','Work Group', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'planned_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Planned Work Shift', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'actual_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Actual Work Shift', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'in_time': fields.float('In Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'out_time': fields.float('Out Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'total_hours': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'approval': fields.boolean('Select for Approval', readonly =  True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('cancel', 'Reject'),('done', 'Approve')],'Status', readonly=True),
              'type':fields.selection([('permission', 'Permission'),('shift', 'Shift')],'Type', readonly=True),
              'permission_id':fields.many2one('arul.hr.permission.onduty','Permission/On Duty'),
              'time_evaluate_id': fields.many2one('tpt.time.leave.evaluation','Time Evaluation'),
              }
    _defaults = {
        'state':'draft',
    }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['work_date'], context)
  
        for record in reads:
            name = record['work_date']
            res.append((record['id'], name))
        return res 
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
            if line.type != 'permission':
                employee_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line.employee_id.id)])
                if employee_ids:
                    
                    val2={'punch_in_out_id':employee_ids[0], 
                          'employee_id': line.employee_id.id,
                          'work_date':line.work_date, 
                          'planned_work_shift_id':line.planned_work_shift_id.id,
                          'actual_work_shift_id':line.actual_work_shift_id.id,
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
                          'actual_work_shift_id':line.actual_work_shift_id.id,
                          'in_time':line.in_time,
                          'out_time':line.out_time,
                          'approval':1
                          }
                    emp_attendence_obj.create(cr,uid,{'employee_id':line.employee_id.id,
                                                      'employee_category_id':line.employee_id.employee_category_id and line.employee_id.employee_category_id.id or False,
                                                      'sub_category_id':line.employee_id.employee_sub_category_id and line.employee_id.employee_sub_category_id.id or False,
                                                      'department_id':line.employee_id.department_id and line.employee_id.department_id.id or False,
                                                      'designation_id':line.employee_id.job_id and line.employee_id.job_id.id or False,
                                                      'punch_in_out_line':[(0,0,val1)]}) 
            else:
                line_id=line.permission_id
                emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
                punch_obj = self.pool.get('arul.hr.permission.onduty')
                detail_obj4 = self.pool.get('arul.hr.punch.in.out.time')
                emp_attendence_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                if emp_attendence_ids:
                    if(line_id.non_availability_type_id == 'on_duty'):
                        if(line_id.time_total > 8)and(line_id.time_total < 12):
                            val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                             sql = '''
#                                 select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
#                             '''%(line_id.start_time - 1,line_id.end_time + 1)
#                             cr.execute(sql)
#                             work_shift_ids = [row[0] for row in cr.fetchall()]
#                             if work_shift_ids :
#                                 val['planned_work_shift_id']=work_shift_ids[0]
                            details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                            if details_ids:
                                val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                                detail_obj4.create(cr, uid, val4)
                            else:
                                emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,
                                                                    'punch_in_out_line':[(0,0,val)],
                                                                    'employee_category_id':line.employee_id.employee_category_id and line.employee_id.employee_category_id.id or False,
                                                                    'sub_category_id':line.employee_id.employee_sub_category_id and line.employee_id.employee_sub_category_id.id or False,
                                                                    'department_id':line.employee_id.department_id and line.employee_id.department_id.id or False,
                                                                    'designation_id':line.employee_id.job_id and line.employee_id.job_id.id or False})
                        if(line_id.time_total > 12)and(line_id.time_total < 16):
                            val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                             sql = '''
#                                 select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
#                             '''%(line_id.start_time - 1,line_id.end_time + 1)
#                             cr.execute(sql)
#                             work_shift_ids = [row[0] for row in cr.fetchall()]
#                             if work_shift_ids :
#                             val['planned_work_shift_id']=work_shift_ids[0]
                            details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                            if details_ids:
                                val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                                detail_obj4.create(cr, uid, val4)
                            else:
                                emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,
                                                                    'punch_in_out_line':[(0,0,val)],
                                                                    'employee_category_id':line_id.employee_id.employee_category_id and line_id.employee_id.employee_category_id.id or False,
                                                                    'sub_category_id':line_id.employee_id.employee_sub_category_id and line_id.employee_id.employee_sub_category_id.id or False,
                                                                    'department_id':line_id.employee_id.department_id and line_id.employee_id.department_id.id or False,
                                                                    'designation_id':line_id.employee_id.job_id and line_id.employee_id.job_id.id or False})
        
                            
                    val2={'permission_onduty_id':emp_attendence_ids[0], 'approval':1,
                            }
                    punch_obj.write(cr,uid,[line_id.id],val2) 
                else:
                    detail_vals = {'employee_id':line_id.employee_id.id,
                                   'employee_category_id':line_id.employee_id.employee_category_id and line_id.employee_id.employee_category_id.id or False,
                                    'sub_category_id':line_id.employee_id.employee_sub_category_id and line_id.employee_id.employee_sub_category_id.id or False,
                                    'department_id':line_id.employee_id.department_id and line_id.employee_id.department_id.id or False,
                                    'designation_id':line_id.employee_id.job_id and line_id.employee_id.job_id.id or False
#                                    'designation_id':line_id.employee_id.department_id and line_id.employee_id.department_id.designation_id.id or False
                                   }
                    emp_attendence_id = emp_attendence_obj.create(cr,uid,detail_vals)
                    if(line_id.non_availability_type_id == 'on_duty'):
                        if(line_id.time_total > 8)and(line_id.time_total < 12):
                            val={'permission_onduty_id':emp_attendence_id,'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                             sql = '''
#                                 select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
#                             '''%(line_id.start_time - 1,line_id.end_time + 1)
#                             cr.execute(sql)
#                             work_shift_ids = [row[0] for row in cr.fetchall()]
#                             if work_shift_ids :
#                                 val['planned_work_shift_id']=work_shift_ids[0]
                            details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                            if details_ids:
                                val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                                detail_obj4.create(cr, uid, val4)
                            else:
                                emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,
                                                                    'punch_in_out_line':[(0,0,val)],
                                                                    'employee_category_id':line_id.employee_id.employee_category_id and line_id.employee_id.employee_category_id.id or False,
                                                                    'sub_category_id':line_id.employee_id.employee_sub_category_id and line_id.employee_id.employee_sub_category_id.id or False,
                                                                    'department_id':line_id.employee_id.department_id and line_id.employee_id.department_id.id or False,
                                                                    'designation_id':line_id.employee_id.job_id and line_id.employee_id.job_id.id or False})
                        if(line_id.time_total > 12)and(line_id.time_total < 16):
                            val={'permission_onduty_id':emp_attendence_id,'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
#                             sql = '''
#                                 select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
#                             '''%(line_id.start_time - 1,line_id.end_time + 1)
#                             cr.execute(sql)
#                             work_shift_ids = [row[0] for row in cr.fetchall()]
#                             if work_shift_ids :
#                                 val['planned_work_shift_id']=work_shift_ids[0]
                            details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',line_id.employee_id.id)])
                            if details_ids:
                                val4={'punch_in_out_id':details_ids[0],'employee_id':line_id.employee_id.id,'planned_work_shift_id':line.planned_work_shift_id.id,'actual_work_shift_id':line.actual_work_shift_id.id,'work_date':line_id.date,'in_time':line_id.start_time,'out_time':line_id.end_time,'approval':1}
                                detail_obj4.create(cr, uid, val4)
                            else:
                                emp_attendence_obj.create(cr, uid, {'employee_id':line_id.employee_id.id,
                                                                    'punch_in_out_line':[(0,0,val)],
                                                                    'employee_category_id':line_id.employee_id.employee_category_id and line_id.employee_id.employee_category_id.id or False,
                                                                    'sub_category_id':line_id.employee_id.employee_sub_category_id and line_id.employee_id.employee_sub_category_id.id or False,
                                                                    'department_id':line_id.employee_id.department_id and line_id.employee_id.department_id.id or False,
                                                                    'designation_id':line_id.employee_id.job_id and line_id.employee_id.job_id.id or False})
                    punch_obj.write(cr,uid,[line_id.id],{'permission_onduty_id':emp_attendence_id,'approval':1}) 
            self.write(cr, uid, [line.id],{'approval': True, 'state':'done', 'time_evaluate_id':False})
        return True
    def reject_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': False, 'state':'cancel', 'time_evaluate_id':False})
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
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',date.employee_id.id),('year','=',date.date_from[:4])])
            if emp_leave_ids:
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                temp = 0
                for line in emp_leave.emp_leave_details_ids:
                    if line.leave_type_id.id == date.leave_type_id.id:
                        temp += 1
                        day = line.total_day - line.total_taken
                        if timedelta > day and line.leave_type_id.code!='LOP':
                            raise osv.except_osv(_('Warning!'),_('The Taken Day Must Be Less Than The Limit!'))
                if temp == 0:
                    raise osv.except_osv(_('Warning!'),_('Leave Type Is Unlicensed For Employee Category And Employee Sub Category!'))
            else:
                raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Year'))
            res[date.id] = {
                'days_total': timedelta
            }
        return res
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'leave_type_id':fields.many2one('arul.hr.leave.types','Leave Type',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'date_from':fields.date('Date From',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'date_to': fields.date('To Date',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'days_total': fields.function(days_total, string='Leave Total',store=True, multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'haft_day_leave': fields.boolean('Is haft day leave ?', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'reason':fields.text('Reason', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Done')],'Status', readonly=True),
            'leave_evaluate_id': fields.many2one('tpt.time.leave.evaluation','Leave Evaluation'),
              }
    _defaults = {
        'state':'draft',
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['employee_id'], context)
  
        for record in reads:
            name = record['employee_id']
            res.append((record['id'], name))
        return res 
    
    def create(self, cr, uid, vals, context=None):
        new_id1 = False
        new_id2 = False
        if 'date_from' in vals and 'date_to' in vals:
            date_from = vals['date_from']
            date_to = vals['date_to']
            vals1 = vals
            vals2 = vals
            if date_from[5:7] != date_to[5:7]:
                num_of_month = calendar.monthrange(int(date_from[:4]),int(date_from[5:7]))[1]
                vals2['date_from'] = date_from
                vals1['date_to']=date_from[:4]+'-'+date_from[5:7]+'-'+str(num_of_month)
                new_id1 = super(arul_hr_employee_leave_details, self).create(cr, uid, vals1, context)
                vals2['date_from'] = date_to[:4]+'-'+date_to[5:7]+'-01'
                vals2['date_to'] = date_to
                new_id2 = super(arul_hr_employee_leave_details, self).create(cr, uid, vals2, context)
        if new_id1 or new_id2:
            return new_id1
        else:
            return super(arul_hr_employee_leave_details, self).create(cr, uid, vals, context)
    
#     def write(self, cr, uid, ids, vals, context=None):
#         if 'date_from' in vals and 'date_to' in vals:
#             date_from = vals['date_from']
#             date_to = vals['date_to']
#             vals1 = vals
#             vals2 = vals
#             if date_from[5:7] != date_to[5:7]:
#                 num_of_month = calendar.monthrange(int(date_from[:4]),int(date_from[5:7]))[1]
#                 vals2['date_from'] = date_from
#                 vals1['date_to']=date_from[:4]+'-'+date_from[5:7]+'-'+str(num_of_month)
#                 new_id1 = super(arul_hr_employee_leave_details, self).create(cr, uid, vals1, context)
#                 vals2['date_from'] = date_to[:4]+'-'+date_to[5:7]+'-01'
#                 vals2['date_to'] = date_to
#                 new_id2 = super(arul_hr_employee_leave_details, self).create(cr, uid, vals2, context)
#         return super(arul_hr_employee_leave_details, self).write(cr, uid, vals, context)
    
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
                        if timedelta > day and line.leave_type_id.code!='LOP':
                            raise osv.except_osv(_('Warning!'),_('The Taken Day Must Be Less Than The Limit'))
                if temp == 0:
                    raise osv.except_osv(_('Warning!'),_('Leave Type Is Unlicensed For Employee Category And Employee Sub Category!'))
            else:
                raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Current Year'))
        return True
    
    def process_leave_request(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'state':'done','leave_evaluate_id': False})
        return True  
    
    def cancel_leave_request(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            sql = '''
                update arul_hr_employee_leave_details set state='cancel', leave_evaluate_id = null where id = %s
            '''%(line.id)
            cr.execute(sql)
#             self.write(cr, uid, [line.id],{'state':'cancel'})
        return True  
    
    def _check_days(self, cr, uid, ids, context=None): 
        for days in self.browse(cr, uid, ids, context = context):
            date_from = datetime.datetime.strptime(days.date_from, "%Y-%m-%d")
            date_to = datetime.datetime.strptime(days.date_to, "%Y-%m-%d")
            if date_from > date_to:
                raise osv.except_osv(_('Warning!'),_('The start date must be before to the end date.'))
                return False
            return True       
    _constraints = [
        (_check_days, _(''), ['date_from', 'date_to']),
    ]
arul_hr_employee_leave_details()


class arul_hr_permission_onduty(osv.osv):
    _name='arul.hr.permission.onduty'
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(arul_hr_permission_onduty, self).create(cr, uid, vals, context)
        permission = self.browse(cr, uid, new_id)
        sql = '''
            select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
        '''%(permission.start_time - 1,permission.end_time + 1)
        cr.execute(sql)
        work_shift_ids = [row[0] for row in cr.fetchall()]
        
        punch_obj = self.pool.get('arul.hr.punch.in.out')
        day = permission.date[8:10]
        month = permission.date[5:7]
        year = permission.date[:4]
        shift_id = punch_obj.get_work_shift(cr, uid, permission.employee_id.id, int(day), int(month), year)
        
        self.pool.get('arul.hr.audit.shift.time').create(cr, SUPERUSER_ID, {
            'employee_id':permission.employee_id.id,
            'work_date':permission.date,
            'employee_category_id':permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.id or False,
            'planned_work_shift_id': shift_id,
            'actual_work_shift_id': work_shift_ids and work_shift_ids[0] or False,
            'in_time':permission.start_time,
            'out_time':permission.end_time,
            'type': 'permission',
            'permission_id':new_id,
        })
        return new_id
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
        'permission_onduty_id':fields.many2one('arul.hr.employee.attendence.details','Permission/Onduty',ondelete='cascade'),
        'approval': fields.boolean('Select for Approval', readonly =  True),
#         'detail_id':fields.many2one('arul.hr.employee.attendence.details','Detail'),
        
              }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['employee_id'], context)
  
        for record in reads:
            name = record['employee_id']
            res.append((record['id'], name))
        return res
#     def name_get(self, cr, uid, ids, context=None):
#         res = []
#         if not ids:
#             return res
#         reads = self.read(cr, uid, ids, ['non_availability_type_id'], context)
#         for record in reads:
#             name = record['non_availability_type_id']
#             if name=='permission':
#                 name = 'Permission'
#             elif name=='on_duty':
#                 name = 'On duty'
#             res.append((record['id'], name))
#         return res  
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
        'punch_in_out_id':fields.many2one('arul.hr.employee.attendence.details','Punch in/out',ondelete='cascade')
    }
arul_hr_punch_in_out_time()

class arul_hr_employee_attendence_details(osv.osv):
    _name='arul.hr.employee.attendence.details'
    _columns={
        'employee_id':fields.many2one('hr.employee','Employee', required=True),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category',readonly=False,ondelete='restrict'),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category',readonly=False,ondelete='restrict'),
        'designation_id': fields.many2one('hr.job', 'Designation',readonly=False,ondelete='restrict'),
        'department_id':fields.many2one('hr.department', 'Department',readonly=False,ondelete='restrict'),
        'permission_onduty_details_line':fields.one2many('arul.hr.permission.onduty','permission_onduty_id','Permission On duty Details',readonly=True),
        'punch_in_out_line':fields.one2many('arul.hr.punch.in.out.time','punch_in_out_id','Punch in/Punch out Details',readonly=True)
              }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['employee_id'], context)
  
        for record in reads:
            name = record['employee_id']
            res.append((record['id'], name))
        return res 
    
    def onchange_attendence_datails_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'department_id':emp.department_id.id,
                    'designation_id':emp.job_id.id,
                    }
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
    def onchange_department_id(self, cr, uid, ids,department_id=False, context=None):
        designation_ids = []
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            for line in department.designation_line:
                designation_ids.append(line.designation_id.id)
        return {'value': {}}
    
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
    
    def get_work_shift(self,cr,uid,emp,day,month,year,context=None):
        monthly_shift_schedule_obj = self.pool.get('arul.hr.monthly.shift.schedule')
        sql =   '''
                    select ss.id as shift_id
                    from arul_hr_monthly_shift_schedule ss 
                    left join arul_hr_monthly_work_schedule ws on ss.monthly_work_id = ws.id
                    where ss.employee_id = %s and ws.month = '%s' and ws.year = %s and ws.state= 'done'
                '''%(emp,month,year)
        cr.execute(sql)
        kq = cr.fetchall()
        shift_id = False
        if kq:
            for monthly_shift_schedule_id in monthly_shift_schedule_obj.browse(cr,uid,[kq[0][0]],context=context):
                if day == 1:
                    shift_id = monthly_shift_schedule_id.day_1.id
                if day == 2:
                    shift_id = monthly_shift_schedule_id.day_2.id
                if day == 3:
                    shift_id = monthly_shift_schedule_id.day_3.id
                if day == 4:
                    shift_id = monthly_shift_schedule_id.day_4.id
                if day == 5:
                    shift_id = monthly_shift_schedule_id.day_5.id
                if day == 6:
                    shift_id = monthly_shift_schedule_id.day_6.id
                if day == 7:
                    shift_id = monthly_shift_schedule_id.day_7.id
                if day == 8:
                    shift_id = monthly_shift_schedule_id.day_8.id
                if day == 9:
                    shift_id = monthly_shift_schedule_id.day_9.id
                if day == 10:
                    shift_id = monthly_shift_schedule_id.day_10.id
                if day == 11:
                    shift_id = monthly_shift_schedule_id.day_11.id
                if day == 12:
                    shift_id = monthly_shift_schedule_id.day_12.id
                if day == 13:
                    shift_id = monthly_shift_schedule_id.day_13.id
                if day == 14:
                    shift_id = monthly_shift_schedule_id.day_14.id
                if day == 15:
                    shift_id = monthly_shift_schedule_id.day_15.id
                if day == 16:
                    shift_id = monthly_shift_schedule_id.day_16.id
                if day == 17:
                    shift_id = monthly_shift_schedule_id.day_17.id
                if day == 18:
                    shift_id = monthly_shift_schedule_id.day_18.id
                if day == 19:
                    shift_id = monthly_shift_schedule_id.day_19.id
                if day == 20:
                    shift_id = monthly_shift_schedule_id.day_20.id
                if day == 21:
                    shift_id = monthly_shift_schedule_id.day_21.id
                if day == 22:
                    shift_id = monthly_shift_schedule_id.day_22.id
                if day == 23:
                    shift_id = monthly_shift_schedule_id.day_23.id
                if day == 24:
                    shift_id = monthly_shift_schedule_id.day_24.id
                if day == 25:
                    shift_id = monthly_shift_schedule_id.day_25.id
                if day == 26:
                    shift_id = monthly_shift_schedule_id.day_26.id
                if day == 27:
                    shift_id = monthly_shift_schedule_id.day_27.id
                if day == 28:
                    shift_id = monthly_shift_schedule_id.day_28.id
                if day == 29:
                    shift_id = monthly_shift_schedule_id.day_29.id
                if day == 30:
                    shift_id = monthly_shift_schedule_id.day_30.id
                if day == 31:
                    shift_id = monthly_shift_schedule_id.day_31.id
        return shift_id
                
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
                if L:
                    data = L[0]
                    date_old = data[7:11]+'-'+data[11:13]+'-'+data[13:15]
                for i,data1 in enumerate(L):
                    if data1 and (data1[:3]!='P10' and data1[:3]!='P20' or len(data1)!=52):
                        raise osv.except_osv(_('Warning!'),_('Line %s Data Mismatch!')%(i+1))
                    L2 = L[i+1:]
                    employee_code = data1[43:51]
                    employee_ids = employee_obj.search(cr, uid, [('employee_id','=',employee_code)])
                    date = data1[7:11]+'-'+data1[11:13]+'-'+data1[13:15]
                    temp = 0
                    if employee_ids and date:
                        employee = employee_obj.browse(cr, uid, employee_ids[0])
                        day = date[8:10]
                        month = date[5:7]
                        year = date[:4]
                        shift_id = self.get_work_shift(cr, uid, employee_ids[0], int(day), int(month), year)
                        if data1[:3]=='P10':
                            in_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            if date_old == date:
                                val1={'employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':False,'work_date':date,'in_time':in_time,'out_time':0,'approval':1}
                                for j,data2 in enumerate(L2):
                                    #bat dau vi tri tiep theo cua for 1
                                    in_out = data2[:3]
                                    employee_code_2=data2[43:51]
                                    date_2=data2[7:11]+'-'+data2[11:13]+'-'+data2[13:15]
                                    if employee_code_2==employee_code and in_out=='P10':
                                        in_time2 = float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                        val1={'employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':False,'work_date':date,'in_time':in_time2,'out_time':0,'approval':1}
                                    if employee_code_2==employee_code and in_out=='P20':
                                        out_time=float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                        val1['out_time']=out_time
                                        sql = '''
                                            select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                                        '''%(in_time - 1,out_time + 1)
                                        cr.execute(sql)
                                        work_shift_ids = [row[0] for row in cr.fetchall()]
                                        if work_shift_ids and shift_id and shift_id == work_shift_ids[0]:
                                            val1['actual_work_shift_id']=shift_id
                                            details_ids=detail_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                                            if details_ids:
                                                val4={'punch_in_out_id':details_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':shift_id,'employee_id':employee_ids[0],'work_date':date,'in_time':in_time,'out_time':out_time,'approval':1}
                                                detail_obj4.create(cr, uid, val4)
                                            else:
                                                employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
                                                detail_obj.create(cr, uid, {'employee_id':employee_ids[0],
                                                                            'employee_category_id':employee.employee_category_id and employee.employee_category_id.id or False,
                                                                            'sub_category_id':employee.employee_sub_category_id and employee.employee_sub_category_id.id or False,
                                                                            'department_id':employee.department_id and employee.department_id.id or False,
                                                                            'designation_id':employee.job_id and employee.job_id.id or False,
                                                                            'punch_in_out_line':[(0,0,val1)]})
                                        else:
                                            val1['approval']=False  
                                            val1['employee_category_id'] = employee.employee_category_id.id
                                            detail_obj2.create(cr, uid,val1)
                                        temp +=1
                                        L.pop(j)
                                        break
                                if temp==0:
                                    val={'employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'work_date':date,'in_time':in_time,'out_time':0,'employee_category_id':employee.employee_category_id.id}
                                    detail_obj2.create(cr, uid,val)
                            else:
                                detail_obj2.create(cr, uid,{
                                    'employee_id': employee_ids[0],
                                    'planned_work_shift_id':shift_id,
                                    'work_date':date,
                                    'in_time':in_time,
                                    'employee_category_id':employee.employee_category_id.id,
                                    'type':'shift',
                                })
                        if data1[:3]=='P20':
                            out_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            audit_shift_ids = detail_obj2.search(cr, uid, [('type','=','shift'),('work_date','=',date),('employee_id','=', employee_ids[0])])
                            
                            if audit_shift_ids :
                                audit_shift = detail_obj2.browse(cr,uid,audit_shift_ids[0])
                                sql = '''
                                            select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                                        '''%(audit_shift.in_time - 1,out_time + 1)
                                cr.execute(sql)
                                audit_work_shift_ids = [row[0] for row in cr.fetchall()]
                                if audit_work_shift_ids and shift_id and shift_id == audit_work_shift_ids[0]:
                                    detail_obj2.write(cr, uid, [audit_shift.id],{'out_time':out_time,
                                                                                 'actual_work_shift_id':shift_id,})
                                    detail_obj2.approve_shift_time(cr, uid, [audit_shift.id])
                                else:
                                    detail_obj2.write(cr, uid,[audit_shift.id],{
                                    'out_time':out_time,
                                })
                                 
                            else :
                                val2={'employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'work_date':date,'in_time':0,'out_time':out_time,'employee_category_id':employee.employee_category_id.id}
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
              'monthly_shift_line': fields.one2many('arul.hr.monthly.shift.schedule','monthly_work_id', 'Monthly Work Schedule'),
              'state':fields.selection([('draft', 'Draft'),('load', 'Load'),('done', 'Done')],'Status', readonly=True)
              }
    _defaults = {
        'state':'draft',
        'year': int(time.strftime('%Y')),
    }
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'draft'})
    
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
    
    def shift_schedule(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_arul_hr_monthly_shift_schedule_form_vew')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        work = self.browse(cr, uid, ids[0])
        num_of_month = calendar.monthrange(int(work.year),int(work.month))[1]
        context.update({'default_num_of_month':num_of_month,'department_id':work.department_id.id,'section_id':work.section_id.id})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'arul.hr.monthly.shift.schedule',
            'views': [(resource_id,'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
    
    def onchange_department_id(self, cr, uid, ids,department_id=False,section_id=False,month=False,year=False, context=None):
        res = {'value':{}}
        new_section_id = False
        for line in self.browse(cr, uid, ids):
            sql = '''
                delete from arul_hr_monthly_shift_schedule where monthly_work_id = %s
            '''%(line.id)
            cr.execute(sql)
        employee_lines = []
        num_of_month = 0
        if department_id and month and year and section_id: 
            sql = '''
               select id from arul_hr_section where id = %s and department_id=%s 
            '''%(section_id,department_id)
            cr.execute(sql)
            section_ids = [row[0] for row in cr.fetchall()]
            if not section_ids:
                new_section_id = False
            else:
                new_section_id = section_id
            if month and year:
                num_of_month = calendar.monthrange(int(year),int(month))[1]
            dept = self.pool.get('hr.department').browse(cr, uid, department_id)
            employee_obj=self.pool.get('hr.employee')
            employee_ids = employee_obj.search(cr, uid, [('department_id','=',department_id ),('section_id','=',section_id )])
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id,
                      'num_of_month': num_of_month,
                      }
                employee_lines.append((0,0,rs))
        return {'value': {'section_id':new_section_id,'monthly_shift_line':employee_lines}}
    
    def onchange_year_month(self, cr, uid, ids,department_id=False,section_id=False,month=False,year=False, context=None):
        res = {'value':{}}
        for line in self.browse(cr, uid, ids):
            sql = '''
                delete from arul_hr_monthly_shift_schedule where monthly_work_id = %s
            '''%(line.id)
            cr.execute(sql)
        employee_lines = []
        num_of_month = 0
        if department_id and month and year and section_id: 
            if month and year:
                num_of_month = calendar.monthrange(int(year),int(month))[1]
            dept = self.pool.get('hr.department').browse(cr, uid, department_id)
            employee_obj=self.pool.get('hr.employee')
            employee_ids = employee_obj.search(cr, uid, [('department_id','=',department_id ),('section_id','=',section_id )])
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id,
                      'num_of_month': num_of_month,
                      }
                employee_lines.append((0,0,rs))
        return {'value': {'monthly_shift_line':employee_lines}}
        
        
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
              'shift_day_from': fields.many2one('tpt.month','Shift Day From'),
              'shift_day_to': fields.many2one('tpt.month','Shift Day To'),
              'work_shift_id': fields.many2one('arul.hr.capture.work.shift','Work Shift'),
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
    _defaults = {
        'num_of_month': 28,
    }
    
    def load(self, cr, uid, ids, context=None):
        return True
    
    def save_shift_schedule(self, cr, uid, ids, context=None):
        active_id = context.get('active_id')
        for shift_schedule in self.browse(cr, uid, ids):
            shift_schedule_ids = self.search(cr, uid, [('monthly_work_id','=',active_id),('employee_id','=',shift_schedule.employee_id.id)])
            self.write(cr, uid, shift_schedule_ids,{
              'day_1': shift_schedule.day_1.id,
              'day_2': shift_schedule.day_2.id,
              'day_3': shift_schedule.day_3.id,
              'day_4': shift_schedule.day_4.id,
              'day_5': shift_schedule.day_5.id,
              'day_6': shift_schedule.day_6.id,
              'day_7': shift_schedule.day_7.id,
              'day_8': shift_schedule.day_8.id,
              'day_9': shift_schedule.day_9.id,
              'day_10': shift_schedule.day_10.id,
              'day_11': shift_schedule.day_11.id,
              'day_12': shift_schedule.day_12.id,
              'day_13': shift_schedule.day_13.id,
              'day_14': shift_schedule.day_14.id,
              'day_15': shift_schedule.day_15.id,
              'day_16': shift_schedule.day_16.id,
              'day_17': shift_schedule.day_17.id,
              'day_18': shift_schedule.day_18.id,
              'day_19': shift_schedule.day_19.id,
              'day_20': shift_schedule.day_20.id,
              'day_21': shift_schedule.day_21.id,
              'day_22': shift_schedule.day_22.id,
              'day_23': shift_schedule.day_23.id,
              'day_24': shift_schedule.day_24.id,
              'day_25': shift_schedule.day_25.id,
              'day_26': shift_schedule.day_26.id,
              'day_27': shift_schedule.day_27.id,
              'day_28': shift_schedule.day_28.id,
              'day_29': shift_schedule.day_29.id,
              'day_30': shift_schedule.day_30.id,
              'day_31': shift_schedule.day_31.id,
            })
            sql = '''
                delete from arul_hr_monthly_shift_schedule where monthly_work_id is null
            '''
            cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}
    
    def onchange_monthly(self, cr, uid, ids, num_of_month = False, shift_day_from=False,shift_day_to=False, work_shift_id = False, context=None):
        value = {}
        if shift_day_from and shift_day_to and work_shift_id:
            shift_day_f = self.pool.get('tpt.month').browse(cr, uid, shift_day_from)
            shift_day_t = self.pool.get('tpt.month').browse(cr, uid, shift_day_to)
            if shift_day_f.name > shift_day_t.name:
                raise osv.except_osv(_('Warning!'),_('Shift Day Form must less than Shift Day To'))
            if shift_day_t.name > num_of_month:
                raise osv.except_osv(_('Warning!'),_('Range of month is limited'))
            for num in range(shift_day_f.name, shift_day_t.name + 1):
                if num == 1 :
                    value['day_1'] = work_shift_id
                if num == 2:
                    value['day_2'] = work_shift_id
                if num == 3:
                    value['day_3'] = work_shift_id
                if num == 4:
                    value['day_4'] = work_shift_id
                if num == 5:
                    value['day_5'] = work_shift_id
                if num == 6:
                    value['day_6'] = work_shift_id
                if num == 7:
                    value['day_7'] = work_shift_id
                if num == 8:
                    value['day_8'] = work_shift_id
                if num == 9:
                    value['day_9'] = work_shift_id
                if num == 10:
                    value['day_10'] = work_shift_id
                if num == 11:
                    value['day_11'] = work_shift_id
                if num == 12:
                    value['day_12'] = work_shift_id
                if num == 13:
                    value['day_13'] = work_shift_id
                if num == 14:
                    value['day_14'] = work_shift_id
                if num == 15:
                    value['day_15'] = work_shift_id
                if num == 16:
                    value['day_16'] = work_shift_id
                if num == 17:
                    value['day_17'] = work_shift_id
                if num == 18:
                    value['day_18'] = work_shift_id
                if num == 19:
                    value['day_19'] = work_shift_id
                if num == 20:
                    value['day_20'] = work_shift_id
                if num == 21:
                    value['day_21'] = work_shift_id
                if num == 22:
                    value['day_22'] = work_shift_id
                if num == 23:
                    value['day_23'] = work_shift_id
                if num == 24:
                    value['day_24'] = work_shift_id
                if num == 25:
                    value['day_25'] = work_shift_id
                if num == 26:
                    value['day_26'] = work_shift_id
                if num == 27:
                    value['day_27'] = work_shift_id
                if num == 28:
                    value['day_28'] = work_shift_id
                if num == 29:
                    value['day_29'] = work_shift_id
                if num == 30:
                    value['day_30'] = work_shift_id
                if num == 31:
                    value['day_31'] = work_shift_id
            value.update({'shift_day_from': False,'shift_day_to': False, 'work_shift_id':False})
        return {'value': value}          
    
    def _check_employee_id(self, cr, uid, ids, context=None):
        for shift_schedule in self.browse(cr, uid, ids, context=context):
            if shift_schedule.monthly_work_id:
                shift_schedule_ids = self.search(cr, uid, [('id','!=',shift_schedule.id),('employee_id','=',shift_schedule.employee_id.id),('monthly_work_id','=',shift_schedule.monthly_work_id.id)])
                if shift_schedule_ids:  
                    raise osv.except_osv(_('Warning!'),_('This employee: %s is selected!')%(shift_schedule.employee_id.name+' '+(shift_schedule.employee_id.last_name or '')))
                    return False
        return True
    _constraints = [
        (_check_employee_id, 'Identical Data', ['employee_id']),
    ]
arul_hr_monthly_shift_schedule()

class tpt_non_availability(osv.osv):
    _name = 'tpt.non.availability'
    _columns={
          'employee_id':fields.many2one('hr.employee','Employee',required=True),
          'date':fields.date('Date'),
          'state':fields.selection([('draft', 'No Leave Request Raised'),('done', 'Done')],'Status', readonly=True),
          'leave_evaluate_id': fields.many2one('tpt.time.leave.evaluation','Leave Evaluation'),
      }
    _defaults = {
        'state':'draft',
    }
tpt_non_availability()

class tpt_time_leave_evaluation(osv.osv):
    _name = 'tpt.time.leave.evaluation'
    _columns = {
         'payroll_area_id':fields.many2one('arul.hr.payroll.area','Payroll Area',required = True),
         'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year',required = True),
         'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
         'shift_time_id': fields.one2many('arul.hr.audit.shift.time','time_evaluate_id','Time Evaluation Report',readonly = True),
         'leave_request_id': fields.one2many('arul.hr.employee.leave.details','leave_evaluate_id','Not Approved Section',readonly = True),
         'non_availability_id': fields.one2many('tpt.non.availability','leave_evaluate_id','Non Availability Report',readonly = True),
    }
    _defaults = {
       'year':int(time.strftime('%Y')),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['month','year'], context)
  
        for record in reads:
            name = record['month'] + ' - ' + str(record['year'])
            res.append((record['id'], name))
        return res   
     
    def submit_evaluate(self, cr, uid, ids, context=None):
        monthly_shift_obj = self.pool.get('arul.hr.monthly.shift.schedule')
        non_availability_obj = self.pool.get('tpt.non.availability')
        for sub in self.browse(cr, uid, ids, context=context):
            sql = '''
                update arul_hr_audit_shift_time set time_evaluate_id = %s where EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s and state = 'draft'
                and employee_id in (select id from hr_employee where payroll_area_id = %s)
            '''%(sub.id,sub.year,sub.month,sub.payroll_area_id.id)
            cr.execute(sql)
            sql = '''
                update arul_hr_employee_leave_details set leave_evaluate_id = %s where EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s and state = 'draft'
                and employee_id in (select id from hr_employee where payroll_area_id = %s)
            '''%(sub.id,sub.year,sub.month,sub.payroll_area_id.id)
            cr.execute(sql)
            
            sql = '''
                delete from tpt_non_availability where leave_evaluate_id = %s
            '''%(sub.id)
            cr.execute(sql)
            monthly_shift_ids = monthly_shift_obj.search(cr, uid, [('employee_id.payroll_area_id','=',sub.payroll_area_id.id),('monthly_work_id.year','=',sub.year),('monthly_work_id.month','=',sub.month)])
            for shift in monthly_shift_obj.browse(cr, uid, monthly_shift_ids):
                emp_id = shift.employee_id.id
                sql = '''
                    select EXTRACT(day FROM work_date) from arul_hr_audit_shift_time where employee_id = %s and EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s
                '''%(emp_id, sub.year, sub.month)
                cr.execute(sql)
                audit_days = [row[0] for row in cr.fetchall()]
                
                sql = '''
                    select EXTRACT(day FROM work_date) from arul_hr_punch_in_out_time where employee_id = %s and EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s
                '''%(emp_id, sub.year, sub.month)
                cr.execute(sql)
                punch_days = [row[0] for row in cr.fetchall()]
                
                sql = '''
                    select EXTRACT(day FROM date_from) from arul_hr_employee_leave_details where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                '''%(emp_id, sub.year, sub.month)
                cr.execute(sql)
                leave_days = [row[0] for row in cr.fetchall()]
                
                sql = '''
                    select EXTRACT(day FROM date) from arul_hr_holiday_special where EXTRACT(year FROM date) = %s and EXTRACT(month FROM date) = %s
                '''%(sub.year, sub.month)
                cr.execute(sql)
                holiday_days = [row[0] for row in cr.fetchall()]
                
                day_now = int(time.strftime('%d'))
                month_now = int(time.strftime('%d'))
                year_now = int(time.strftime('%Y'))
                if month_now >= int(sub.month):
                    day_now = 31
                if year_now >= sub.year:
                    if shift.day_1 and shift.day_1.code != 'W' and day_now>=1 and 1.0 not in holiday_days:
                        if 1.0 not in audit_days and 1.0 not in punch_days and 1.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),1)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_2 and shift.day_2.code != 'W' and day_now>=2 and 2.0 not in holiday_days:
                        if 2.0 not in audit_days and 2.0 not in punch_days and 2.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),2)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_3 and shift.day_3.code != 'W' and day_now>=3 and 3.0 not in holiday_days:
                        if 3.0 not in audit_days and 3.0 not in punch_days and 3.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),3)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_4 and shift.day_4.code != 'W' and day_now>=4 and 4.0 not in holiday_days:
                        if 4.0 not in audit_days and 4.0 not in punch_days and 4.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),4)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_5 and shift.day_5.code != 'W' and day_now>=5 and 5.0 not in holiday_days:
                        if 5.0 not in audit_days and 5.0 not in punch_days and 5.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),5)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_6 and shift.day_6.code != 'W' and day_now>=6 and 6.0 not in holiday_days:
                        if 6.0 not in audit_days and 6.0 not in punch_days and 6.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),6)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_7 and shift.day_7.code != 'W' and day_now>=7 and 7.0 not in holiday_days:
                        if 7.0 not in audit_days and 7.0 not in punch_days and 7.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),7)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_8 and shift.day_8.code != 'W' and day_now>=8 and 8.0 not in holiday_days:
                        if 8.0 not in audit_days and 8.0 not in punch_days and 8.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),8)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_9 and shift.day_9.code != 'W' and day_now>=9 and 9.0 not in holiday_days:
                        if 9.0 not in audit_days and 9.0 not in punch_days and 9.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),9)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_10 and shift.day_10.code != 'W' and day_now>=10 and 10.0 not in holiday_days:
                        if 10.0 not in audit_days and 10.0 not in punch_days and 10.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),10)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_11 and shift.day_11.code != 'W' and day_now>=11 and 11.0 not in holiday_days:
                        if 11.0 not in audit_days and 11.0 not in punch_days and 11.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),11)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_12 and shift.day_12.code != 'W' and day_now>=12 and 12.0 not in holiday_days:
                        if 12.0 not in audit_days and 12.0 not in punch_days and 12.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),12)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_13 and shift.day_13.code != 'W' and day_now>=13 and 13.0 not in holiday_days:
                        if 13.0 not in audit_days and 13.0 not in punch_days and 13.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),13)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_14 and shift.day_14.code != 'W' and day_now>=14 and 14.0 not in holiday_days:
                        if 14.0 not in audit_days and 14.0 not in punch_days and 14.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),14)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_15 and shift.day_15.code != 'W' and day_now>=15 and 15.0 not in holiday_days:
                        if 15.0 not in audit_days and 15.0 not in punch_days and 15.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),15)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_16 and shift.day_16.code != 'W' and day_now>=16 and 16.0 not in holiday_days:
                        if 16.0 not in audit_days and 16.0 not in punch_days and 16.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),16)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_17 and shift.day_17.code != 'W' and day_now>=17 and 17.0 not in holiday_days:
                        if 17.0 not in audit_days and 17.0 not in punch_days and 17.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),17)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_18 and shift.day_18.code != 'W' and day_now>=18 and 18.0 not in holiday_days:
                        if 18.0 not in audit_days and 18.0 not in punch_days and 18.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),18)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_19 and shift.day_19.code != 'W' and day_now>=19 and 19.0 not in holiday_days:
                        if 19.0 not in audit_days and 19.0 not in punch_days and 19.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),19)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_20 and shift.day_20.code != 'W' and day_now>=20 and 20.0 not in holiday_days:
                        if 20.0 not in audit_days and 20.0 not in punch_days and 20.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),20)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_21 and shift.day_21.code != 'W' and day_now>=21 and 21.0 not in holiday_days:
                        if 21.0 not in audit_days and 21.0 not in punch_days and 21.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),21)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_22 and shift.day_22.code != 'W' and day_now>=22 and 22.0 not in holiday_days:
                        if 22.0 not in audit_days and 22.0 not in punch_days and 22.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),22)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_23 and shift.day_23.code != 'W' and day_now>=23 and 23.0 not in holiday_days:
                        if 23.0 not in audit_days and 23.0 not in punch_days and 23.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),23)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_24 and shift.day_24.code != 'W' and day_now>=24 and 24.0 not in holiday_days:
                        if 24.0 not in audit_days and 24.0 not in punch_days and 24.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),24)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_25 and shift.day_25.code != 'W' and day_now>=25 and 25.0 not in holiday_days:
                        if 25.0 not in audit_days and 25.0 not in punch_days and 25.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),25)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_26 and shift.day_26.code != 'W' and day_now>=26 and 26.0 not in holiday_days:
                        if 26.0 not in audit_days and 26.0 not in punch_days and 26.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),26)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_27 and shift.day_27.code != 'W' and day_now>=27 and 27.0 not in holiday_days:
                        if 27.0 not in audit_days and 27.0 not in punch_days and 27.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),27)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_28 and shift.day_28.code != 'W' and day_now>=28 and 28.0 not in holiday_days:
                        if 28.0 not in audit_days and 28.0 not in punch_days and 28.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),28)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_29 and shift.day_29.code != 'W' and shift.num_of_month>=29 and day_now>=29 and 29.0 not in holiday_days:
                        if 29.0 not in audit_days and 29.0 not in punch_days and 29.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),29)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_30 and shift.day_30.code != 'W' and shift.num_of_month>=30 and day_now>=30 and 30.0 not in holiday_days:
                        if 30.0 not in audit_days and 30.0 not in punch_days and 30.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),30)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_31 and shift.day_31.code != 'W' and shift.num_of_month>=31 and day_now>=31 and 31.0 not in holiday_days:
                        if 31.0 not in audit_days and 31.0 not in punch_days and 31.0 not in leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),31)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
        return True
     
tpt_time_leave_evaluation()

class tpt_month(osv.osv):
    _name = 'tpt.month'
    _columns = {
        'name': fields.integer('Name'),     
    }
    
    def init(self, cr):
        for num in range(1,32):
            month_ids = self.search(cr, 1, [('name','=',num)])
            if not month_ids:
                self.create(cr, 1, {'name':num})
        return True
tpt_month()

class tpt_work_center(osv.osv):
    _name = 'tpt.work.center'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_work_center, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_work_center, self).write(cr, uid,ids, vals, context)

    def _check_code_id(self, cr, uid, ids, context=None):
        for work in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_work_center where id != %s and lower(code) = lower('%s') 
            '''%(work.id,work.code)
            cr.execute(sql)
            work_ids = [row[0] for row in cr.fetchall()]
            if work_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]

    
tpt_work_center()

class tpt_cost_center(osv.osv):
    _name = 'tpt.cost.center'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_cost_center, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_cost_center, self).write(cr, uid,ids, vals, context)

    def _check_code_id(self, cr, uid, ids, context=None):
        for cost in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_cost_center where id != %s and lower(code) = lower('%s')
            '''%(cost.id,cost.code)
            cr.execute(sql)
            cost_ids = [row[0] for row in cr.fetchall()]
            if cost_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]

    
tpt_cost_center()

class tpt_equipment_master(osv.osv):
    _name = 'tpt.equipment.master'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_equipment_master, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_equipment_master, self).write(cr, uid,ids, vals, context)

    def _check_code_id(self, cr, uid, ids, context=None):
        for cost in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_cost_center where id != %s and lower(code) = lower('%s')
            '''%(cost.id,cost.code)
            cr.execute(sql)
            cost_ids = [row[0] for row in cr.fetchall()]
            if cost_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
tpt_cost_center()

class tpt_manage_equipment_inventory(osv.osv):
    _name = 'tpt.manage.equipment.inventory'
    
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for quatity in self.browse(cr, uid, ids, context = context):
            res[quatity.id] = {
               'total_qty' : 0.0,
               }
            total = quatity.allocated_qty - quatity.returned_qty
            res[quatity.id]['total_qty'] = total
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['equipment_id','employee_id'], context)
  
        for record in reads:
            name = record['employee_id'][1] + ' - ' + record['equipment_id'][1]
            res.append((record['id'], name))
        return res    
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required = True, ondelete = 'cascade'),  
        'equipment_id': fields.many2one('tpt.equipment.master', 'Equipment Name', required = True),
        'allocated_qty': fields.float('Allocated Qty'),
        'returned_qty': fields.float('Returned Qty'),
        'total_qty': fields.function(_amount_total, string='Total Qty', multi='deltas', store = True),
    }
