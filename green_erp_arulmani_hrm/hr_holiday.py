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
	    'is_local_holiday': fields.boolean('Is Local Holiday?'),
    }
    def _check(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            date = self.search(cr, uid, [('date','=',obj.date)])
            if (name and len(name) > 1) or (date and len(date) > 1):
                raise osv.except_osv(_('Warning!'),_('This Holiday has already existed!'))
        return True
    _constraints = [
        (_check, _(''), ['name', 'date']),
    ]
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
    def _check_limit_day(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids[0])
        if obj:
            if obj.maximum_limit < obj.condition:
                raise osv.except_osv(_('Warning!'),_('Eligible per Annum must be less than/as same as Maximum Limit Applicable!'))
        return True
    _constraints = [
        (_check_sub_category_id, 'Identical Data', ['leave_type_id','employee_category_id','employee_sub_category_id']),
        (_check_limit_day, 'Identical Data', ['maximum_limit','condition']),
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
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_hr_leave_types, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_hr_leave_types, self).write(cr, uid,ids, vals, context)
    
    def _check_code(self, cr, uid, ids, context=None):
        for leave in self.browse(cr, uid, ids, context=context):
            leave_ids = self.search(cr, uid, [('id','!=',leave.id),('code','=',leave.code)])
            if leave_ids:  
                raise osv.except_osv(_('Warning!'),_('The Code is unique!'))
        return True
    
    def _check_name(self, cr, uid, ids, context=None):
        for leave in self.browse(cr, uid, ids, context=context):
            leave_ids = self.search(cr, uid, [('id','!=',leave.id),('name','=',leave.name)])
            if leave_ids:  
                raise osv.except_osv(_('Warning!'),_('The Name is unique!'))
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
        (_check_name, 'Identical Data', ['name']),
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
	      #Start:TPT - BalamuruganPurushothaman on 18/02/2015 - To give grace period time for a Shift
	      'min_start_time': fields.float('Minimum Shift Start Time'),
	      'max_start_time': fields.float('Maximum Shift Start Time'),
	      'min_end_time': fields.float('Minimum Shift End Time'),
	      'max_end_time': fields.float('Maximum Shift End Time'),	
	      'half_day_shift_hr': fields.float('Half Day Shift Hour'),
	      #End:TPT	
              }
    
#     def name_get(self, cr, uid, ids, context=None):
#         res = []
#         if not ids:
#             return res
#         reads = self.read(cr, uid, ids, ['code'], context)
#   
#         for record in reads:
#             name = record['code']
#             res.append((record['id'], name))
#         return res    
    
    def _check_code(self, cr, uid, ids, context=None):
        for shift in self.browse(cr, uid, ids, context=context):
            shift_ids = self.search(cr, uid, [('id','!=',shift.id),('code','=',shift.code)])
            if shift_ids:  
                raise osv.except_osv(_('Warning!'),_('The Code is unique!'))
        return True
    
    def _check_time(self, cr, uid, ids, context=None): 
        time = self.browse(cr,uid,ids[0])
        shift_ids = self.search(cr, uid, [('start_time','=',time.start_time),('end_time','=',time.end_time)])
        if shift_ids and len(shift_ids) > 1:  
            raise osv.except_osv(_('Warning!'),_('The Time is duplicated!'))
        if ((time.start_time > 24 or time.start_time < 0) or (time.end_time > 24 or time.end_time < 0)):
            raise osv.except_osv(_('Warning!'),_('Input Wrong Time!'))
        if time.start_time == 0 and time.end_time == 0:
            raise osv.except_osv(_('Warning!'),_('Input Wrong Time!'))
        return True       
    _constraints = [
        (_check_time, _(''), ['start_time', 'end_time']),
        (_check_code, _(''), ['code']),
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
            if time.in_time != 0 and time.out_time!=0:
                if time.in_time > time.out_time:
                    time_total = 24-time.in_time + time.out_time
                else:
                    time_total = time.out_time - time.in_time
                if time.diff_day and (time.in_time <= time.out_time):
                    time_total += 24
            else:
                time_total=0
            res[time.id]['total_hours'] = time_total            
        return res
    #AST
    def _shift_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for time in self.browse(cr, uid, ids, context=context):
            res[time.id] = {
                'total_shift_worked': 0.0,
            }
            if time.total_hours <= 1.0:            
                res[time.id]['total_shift_worked'] = 0.125
            if time.total_hours >= 1.1 and time.total_hours <= 2.0:            
                res[time.id]['total_shift_worked'] = 0.25
            if time.total_hours >= 2.1 and time.total_hours <= 3.0:            
                res[time.id]['total_shift_worked'] = 0.375            
            if time.total_hours >= 4.0 and time.total_hours <= 7.44:            
                res[time.id]['total_shift_worked'] = 0.5    
            if time.total_hours >= 7.45 and time.total_hours <= 8.30:            
                res[time.id]['total_shift_worked'] = 1.0
            if time.total_hours >8.30  and time.total_hours <= 11.44:            
                res[time.id]['total_shift_worked'] = 1.0
            if time.total_hours >=11.45  and time.total_hours <= 15.44:            
                res[time.id]['total_shift_worked'] = 1.5
            if time.total_hours >=15.45  and time.total_hours <= 15.45:            
                res[time.id]['total_shift_worked'] = 1.5
            if time.total_hours >=15.45:            
                res[time.id]['total_shift_worked'] = 2.0
        return res
    
    def _check_additional_shift(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        additional_shifts = False
        for audit in self.browse(cr, uid, ids, context=context):
            time_ids = self.pool.get('arul.hr.punch.in.out.time').search(cr, uid, [('employee_id','=',audit.employee_id.id),('work_date','=',audit.work_date)])
            if time_ids:
                additional_shifts = True
            res[audit.id] = additional_shifts 
        return res
        
    def _get_audit(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('arul.hr.punch.in.out.time').browse(cr, uid, ids, context=context):
            audit_ids = self.pool.get('arul.hr.audit.shift.time').search(cr, uid, [('employee_id','=',line.employee_id.id),('work_date','=',line.work_date)])
            for audit_id in audit_ids:
                result[audit_id] = True
        return result.keys()
        
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee ID', required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'work_date':fields.date('Work Date', required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'employee_category_id':fields.many2one('vsis.hr.employee.category','Work Group', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'planned_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Planned Work Shift', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'actual_work_shift_id':fields.many2one('arul.hr.capture.work.shift','Actual Work Shift', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'in_time': fields.float('In Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'out_time': fields.float('Out Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'total_hours': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'additional_shifts': fields.function(_check_additional_shift, string='Additional Shifts', type='boolean', store={
                   'arul.hr.audit.shift.time': (lambda self, cr, uid, ids, c={}: ids, ['employee_id','work_date'], 10),
                   'arul.hr.punch.in.out.time': (_get_audit, ['employee_id', 'work_date'], 10),
                   }),
              'approval': fields.boolean('Select for Approval', readonly =  True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('cancel', 'Reject'),('done', 'Approve')],'Status', readonly=True),
              'type':fields.selection([('permission', 'Permission'),('on_duty', 'On Duty'),('shift', 'Waiting'),('punch', 'Punch In/Out'),
                                       ('punch_edited', 'Punch In/Out-Edited'),
                                       ('permission_edited', 'Permission-Edited'),
                                       ('on_duty_edited', 'On Duty-Edited'),
                                       ('manual_edited', 'Manual Entry-Edited'),
                                       ('manual','Manual Entry')],'Type'),#TPT Onduty, Manual Entry type is added in Audit Shift Time Screen.
              'permission_id':fields.many2one('arul.hr.permission.onduty','Permission/On Duty'),
              'time_evaluate_id': fields.many2one('tpt.time.leave.evaluation','Time Evaluation'),
              'diff_day': fields.boolean('Difference Day', readonly = True),
              #TPT
              'punch_in_date':fields.date('Punch In Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'punch_out_date':fields.date('Punch Out Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'reason_for_edit': fields.text('Reason',states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'time_change_flag': fields.boolean('If In/Out Changed'), 
              #TPT - Audit Shift Times
              'total_shift_worked': fields.function(_shift_total, string='No.Of Shift Worked', multi='shiftsums', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              #'total_shift_worked': fields.float('No.Of Shift Worked', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'a_shift_count': fields.float('A', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'g1_shift_count': fields.float('G1', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'g2_shift_count': fields.float('G2', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'b_shift_count': fields.float('B', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'c_shift_count': fields.float('C', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'create_date': fields.datetime('Created Date',readonly = True),
              'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
              
              }
    _defaults = {
        'state':'draft',
	    'type':'manual',
        
    }
    def onchange_in_time(self, cr, uid, ids, in_out_time=False, type=False,context=None):
        vals = {}
        vals.update({'time_change_flag':True})
        if type=='manual':
            vals.update({'type':'manual_edited'})
        if type=='punch':
            vals.update({'type':'punch_edited'})
        if type=='permission':
            vals.update({'type':'permission_edited'})
        if type=='on_duty':
            vals.update({'type':'on_duty_edited'})
        return {'value':vals}

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
    def approve_shift_time_multi(self, cr, uid, ids, context=None):
        employee_leave_obj = self.pool.get('employee.leave')
        employee_leave_detail_obj = self.pool.get('employee.leave.detail')
        leave_type_obj = self.pool.get('arul.hr.leave.types')
        for line in self.browse(cr, uid, ids):
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                continue
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
        for line in self.browse(cr,uid,ids):
#             emp = self.pool.get('hr.employee')
            emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
            punch_obj = self.pool.get('arul.hr.punch.in.out.time')
            if line.type != 'permission' and line.type != 'on_duty':
                extra_hours = 0.0
		#TPT: To throw warning if Actual Work Shift is not selected
		if not line.actual_work_shift_id :
		    raise osv.except_osv(_('Warning!'),_('Please Select Actual Work Shift'))
                if line.in_time > line.out_time:
                    extra_hours = 24-line.in_time + line.out_time
                else:
                    extra_hours = line.out_time - line.in_time
                if line.diff_day and (line.in_time <= line.out_time):
                    extra_hours += 24
                    
                if line.actual_work_shift_id:
                    if line.actual_work_shift_id.start_time > line.actual_work_shift_id.end_time:
                        shift_hours = 24-line.actual_work_shift_id.start_time + line.actual_work_shift_id.end_time
                    else:
                        shift_hours = line.actual_work_shift_id.end_time - line.actual_work_shift_id.start_time
                elif line.planned_work_shift_id:
                    if line.planned_work_shift_id.start_time > line.planned_work_shift_id.end_time:
                        shift_hours = 24-line.planned_work_shift_id.start_time + line.planned_work_shift_id.end_time
                    else:
                        shift_hours = line.planned_work_shift_id.end_time - line.planned_work_shift_id.start_time
                else:
                    shift_hours = 8
                
                flag = 0
		#Start:TPT 
                #if line.planned_work_shift_id and line.planned_work_shift_id.code=='W':
                #    flag = 1
                #    shift_hours = 0
                #End:TPT
	
		#Start:TPT By BalamuruganPurushothaman on 21/02/2015
		if line.total_hours >= 4 and line.planned_work_shift_id.code=='W':	
		    flag = 1
                    shift_hours = 0
		    
		elif line.total_hours < 3.7 and line.planned_work_shift_id.code=='W':
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }

		#Adding C.Off count if an Employee worked on Special Holiday. And allow to approve if total worked hour meets 4 hrs
		
		sql=''' SELECT date FROM arul_hr_holiday_special WHERE TO_CHAR(date,'YYYY-MM-DD') = ('%s') and is_local_holiday='f' '''%line.work_date
                cr.execute(sql)                
                spl_date=cr.fetchall()
		
		if spl_date and line.total_hours >= 4:
		    flag = 1
                    shift_hours = 0
		if spl_date and line.total_hours < 3.7:
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
		

		# Handling Local Holiday. And allow to approve if total worked hour meets 4 hrs - RULE WILL BE IMPLEMENTED AS PER USER REQUIREMENTS
		
		sql=''' SELECT date FROM arul_hr_holiday_special WHERE TO_CHAR(date,'YYYY-MM-DD') = ('%s') and is_local_holiday='t' '''%line.work_date
                cr.execute(sql)                
                local_date=cr.fetchall()
		
		if local_date and line.total_hours >= 4:
		    flag = 1
                    shift_hours = 0
		if local_date and line.total_hours < 3.7:
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
                # A+C Shift Handling
		
		sql=''' SELECT work_date FROM arul_hr_punch_in_out_time WHERE TO_CHAR(work_date,'YYYY-MM-DD') = ('%s') and employee_id=%s '''%(line.work_date,line.employee_id.id)
                cr.execute(sql)                
                same_work_date=cr.fetchone()
		
		if same_work_date and line.total_hours >= 4:
		    flag = 1
                    shift_hours = 0
		    
		if same_work_date and line.total_hours < 3.7:
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
		
		if line.total_hours<shift_hours and line.planned_work_shift_id.code!='W':
                    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
                
		#End:TPT						

		# TPT: The system should block approval if total working time is not match with shit time - For Emp Categ S1
		#if extra_hours<shift_hours and line.employee_id.employee_category_id and line.employee_id.employee_category_id.code!='S1':
                if extra_hours<shift_hours and line.employee_id.employee_category_id :
                    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        continue
                
                #if flag==1 or line.additional_shifts or (extra_hours>8 and line.employee_id.employee_category_id and line.employee_id.employee_category_id.code!='S1'): # Commented By BalamuruganPurushothaman - TO do not calculate COFF for S1 categ
		if flag==1 and line.employee_id.employee_category_id and line.employee_id.employee_category_id.code!='S1':
                    c_off_day = 0.0
		    #raise osv.except_osv(_('Warning!'),_('inside c.off'))
                    if line.additional_shifts:
                        if extra_hours >= 3.7 and extra_hours < 7.39:
                            c_off_day = 0.5
                        if extra_hours >= 7.4 and extra_hours < 12:
                            c_off_day = 1
                        if extra_hours >= 12 and extra_hours < 16:
                            c_off_day = 1.5
                        if extra_hours >= 16:
                            c_off_day = 2
                    else:
                        extra_hours = extra_hours-shift_hours
                        if extra_hours >= 3.7 and extra_hours < 7.39:
                            c_off_day = 0.5
                        if extra_hours >= 7.4 and extra_hours < 12:
                            c_off_day = 1
                        if extra_hours >= 12 and extra_hours < 16:
                            c_off_day = 1.5
                        if extra_hours >= 16:
                            c_off_day = 2
                    employee_leave_ids = employee_leave_obj.search(cr, uid, [('year','=',line.work_date[:4]),('employee_id','=',line.employee_id.id)])
                    leave_type_ids = leave_type_obj.search(cr, uid, [('code','=','C.Off')])
                    if not leave_type_ids:
                        raise osv.except_osv(_('Warning!'),_('Can not find Leave Type C.Off. Please Create Leave Type C.Off before'))
                    if employee_leave_ids:
                        employee_leave_detail_ids = employee_leave_detail_obj.search(cr, uid, [('emp_leave_id','in',employee_leave_ids),('leave_type_id','=',leave_type_ids[0])])
                        if employee_leave_detail_ids:
                            sql = '''
                                update employee_leave_detail set total_day = total_day+%s where id = %s
                            '''%(c_off_day,employee_leave_detail_ids[0])
                            cr.execute(sql)
                        else:
                            employee_leave_detail_obj.create(cr, uid, {
                                                                       'leave_type_id': leave_type_ids[0],
                                                                       'emp_leave_id': employee_leave_ids[0],
                                                                       'total_day': c_off_day,
                                                                       })
                    else:
                        employee_leave_detail_obj.create(cr, uid, {
                                                                   'employee_id': employee_ids[0],
                                                                   'year': data1[7:11],
                                                                   'emp_leave_details_ids': [(0,0,{
                                                                                               'leave_type_id': leave_type_ids[0],
                                                                                               'emp_leave_id': employee_leave_ids[0],
                                                                                               'total_day': c_off_day,
                                                                                                   })],
                                                                   })
                
                employee_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line.employee_id.id)])
                if employee_ids:
                    
                    val2={'punch_in_out_id':employee_ids[0], 
                          'employee_id': line.employee_id.id,
                          'work_date':line.work_date, 
                          'planned_work_shift_id':line.planned_work_shift_id.id,
                          'actual_work_shift_id':line.actual_work_shift_id.id,
                          'in_time':line.in_time,
                          'out_time':line.out_time,
                          'approval':1,
                          'diff_day': line.diff_day,
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
                          'approval':1,
                          'diff_day': line.diff_day,
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
    
    def approve_shift_time(self, cr, uid, ids, context=None):
        employee_leave_obj = self.pool.get('employee.leave')
        employee_leave_detail_obj = self.pool.get('employee.leave.detail')
        leave_type_obj = self.pool.get('arul.hr.leave.types')
	#raise osv.except_osv(_('Warning!%s'),leave_type_obj)	
        for line in self.browse(cr, uid, ids):
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                continue
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
        for line in self.browse(cr,uid,ids):
#             emp = self.pool.get('hr.employee')
            emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
            punch_obj = self.pool.get('arul.hr.punch.in.out.time')
            if line.type != 'permission'  and line.type != 'on_duty':
                extra_hours = 0.0
		#TPT: To throw warning if Actual Work Shift is not selected
		if not line.actual_work_shift_id:
		    raise osv.except_osv(_('Warning!'),_('Please Select Actual Work Shift'))
                if line.in_time > line.out_time:
                    extra_hours = 24-line.in_time + line.out_time
                else:
                    extra_hours = line.out_time - line.in_time
                if line.diff_day and (line.in_time <= line.out_time):
                    extra_hours += 24
                    
                if line.actual_work_shift_id:
                    if line.actual_work_shift_id.start_time > line.actual_work_shift_id.end_time:
                        shift_hours = 24-line.actual_work_shift_id.start_time + line.actual_work_shift_id.end_time
                    else:
                        shift_hours = line.actual_work_shift_id.end_time - line.actual_work_shift_id.start_time
                elif line.planned_work_shift_id:
                    if line.planned_work_shift_id.start_time > line.planned_work_shift_id.end_time:
                        shift_hours = 24-line.planned_work_shift_id.start_time + line.planned_work_shift_id.end_time
                    else:
                        shift_hours = line.planned_work_shift_id.end_time - line.planned_work_shift_id.start_time
                else:
                    shift_hours = 8
                
                flag = 0
		#Start:TPT - By BalamuruganPurushothaman on 20/02/2015 - To allow approve Audit Shift Time record, if Emp worked on Week Off when it reached max of 4 hrs
                #if line.planned_work_shift_id and line.planned_work_shift_id.code=='W':
                #    flag = 1
                #    shift_hours = 0                
		#
		if line.total_hours >= 3.7 and line.planned_work_shift_id.code=='W':	
		    flag = 1
                    shift_hours = 0
		    #raise osv.except_osv(_('Warning!%s%s'),(line.total_hours,line.planned_work_shift_id))
		elif line.total_hours < 3.7 and line.planned_work_shift_id.code=='W':
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }

		#Adding C.Off count if an Employee worked on Special Holiday. And allow to approve if total worked hour meets 4 hrs
		
		sql=''' SELECT date FROM arul_hr_holiday_special WHERE TO_CHAR(date,'YYYY-MM-DD') = ('%s') and is_local_holiday='f' '''%line.work_date
                cr.execute(sql)                
                spl_date=cr.fetchall()
		
		if spl_date and line.total_hours >= 3.7:
		    flag = 1
                    shift_hours = 0
		if spl_date and line.total_hours < 3.7:
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
		
		# Handling Local Holiday. And allow to approve if total worked hour meets 4 hrs - RULE WILL BE IMPLEMENTED AS PER USER REQUIREMENTS
		
		sql=''' SELECT date FROM arul_hr_holiday_special WHERE TO_CHAR(date,'YYYY-MM-DD') = ('%s') and is_local_holiday='t' '''%line.work_date
                cr.execute(sql)                
                local_date=cr.fetchall()
		
		if local_date and line.total_hours >= 3.7: # MIN of SHIFT 7.45 / 2 = 3.7
		    #flag = 1
                    shift_hours = 0
		if local_date and line.total_hours < 3.7:
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }

                # A+C Shift Handling - COff will be applicable for S1,S3 if attendance entry is created twice the day
		
		sql=''' SELECT work_date FROM arul_hr_punch_in_out_time WHERE TO_CHAR(work_date,'YYYY-MM-DD') = ('%s') and employee_id=%s '''%(line.work_date,line.employee_id.id)
                cr.execute(sql)                
                same_work_date=cr.fetchone()
		
		if same_work_date and line.total_hours >= 4:
		    flag = 1
                    shift_hours = 0
		    
		if same_work_date and line.total_hours < 4:
		    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
		#
		# C+A Shift Handling 
		
		sql=''' SELECT work_date FROM arul_hr_punch_in_out_time WHERE TO_CHAR(work_date,'YYYY-MM-DD') = ('%s') and employee_id=%s '''%(line.work_date,line.employee_id.id)
                cr.execute(sql)                
                #same_work_date=cr.fetchone()


		if line.total_hours<shift_hours and line.planned_work_shift_id.code!='W':
                    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    	
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
                
		#End:TPT
		# TPT: The system should block approval if total working time is not match with shit time - For Emp Categ S1
               	#if extra_hours<shift_hours and line.employee_id.employee_category_id and line.employee_id.employee_category_id.code!='S1':
		if extra_hours<shift_hours and line.employee_id.employee_category_id :
                    permission_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','permission'),('date','=',line.work_date),('employee_id','=',line.employee_id.id)])
                    on_duty_ids = self.pool.get('arul.hr.permission.onduty').search(cr, uid, [('non_availability_type_id','=','on_duty'),('from_date','<=',line.work_date),('to_date','>=',line.work_date),('employee_id','=',line.employee_id.id)])
                    leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [('date_from','<=',line.work_date),('date_to','>=',line.work_date),('employee_id','=',line.employee_id.id),('state','=','done')])
		    
                    if not permission_ids and not on_duty_ids and not leave_detail_ids:
                        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'alert_permission_form_view')
                        return {
                                'name': 'Alert Permission',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': res[1],
                                'res_model': 'alert.form',
                                'domain': [],
                                'context': {'default_message':'No Permission / On Duty Entry is made for Pending Hours. Do you want to reduce it from Leave Credits (CL/SL/C.Off/PL/LOP) ?','audit_id':line.id},
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
                
                #if flag==1 or line.additional_shifts or (extra_hours>8 and line.employee_id.employee_category_id and line.employee_id.employee_category_id.code!='S1'): # Commented By BalamuruganPurushothaman - TO do not calculate COFF for S1 categ
		if flag==1 and line.employee_id.employee_category_id and line.employee_id.employee_category_id.code!='S1':
                    c_off_day = 0.0
		    #raise osv.except_osv(_('Warning!%s%s%s%s%s'),(flag,extra_hours,line.employee_id.employee_category_id,line.employee_id.employee_category_id.code,line.additional_shifts))
                    if line.additional_shifts:
                        if extra_hours >= 3.7 and extra_hours < 7.39:
                            c_off_day = 0.5
                        if extra_hours >= 7.4 and extra_hours < 12:
                            c_off_day = 1
                        if extra_hours >= 12 and extra_hours < 16:
                            c_off_day = 1.5
                        if extra_hours >= 16:
                            c_off_day = 2
                    else:
                        extra_hours = extra_hours-shift_hours
                        if extra_hours >= 3.7 and extra_hours < 7.39:
                            c_off_day = 0.5
                        if extra_hours >= 7.4 and extra_hours < 12:
                            c_off_day = 1
                        if extra_hours >= 12 and extra_hours < 16:
                            c_off_day = 1.5
                        if extra_hours >= 16:
                            c_off_day = 2
                    employee_leave_ids = employee_leave_obj.search(cr, uid, [('year','=',line.work_date[:4]),('employee_id','=',line.employee_id.id)])
                    leave_type_ids = leave_type_obj.search(cr, uid, [('code','=','C.Off')])
                    if not leave_type_ids:
                        raise osv.except_osv(_('Warning!'),_('Can not find Leave Type C.Off. Please Create Leave Type C.Off before'))
                    if employee_leave_ids:
                        employee_leave_detail_ids = employee_leave_detail_obj.search(cr, uid, [('emp_leave_id','in',employee_leave_ids),('leave_type_id','=',leave_type_ids[0])])
                        if employee_leave_detail_ids:
                            sql = '''
                                update employee_leave_detail set total_day = total_day+%s where id = %s
                            '''%(c_off_day,employee_leave_detail_ids[0])
                            cr.execute(sql)
                        else:
                            employee_leave_detail_obj.create(cr, uid, {
                                                                       'leave_type_id': leave_type_ids[0],
                                                                       'emp_leave_id': employee_leave_ids[0],
                                                                       'total_day': c_off_day,
                                                                       })
                    else:
                        employee_leave_detail_obj.create(cr, uid, {
                                                                   'employee_id': employee_ids[0],
                                                                   'year': data1[7:11],
                                                                   'emp_leave_details_ids': [(0,0,{
                                                                                               'leave_type_id': leave_type_ids[0],
                                                                                               'emp_leave_id': employee_leave_ids[0],
                                                                                               'total_day': c_off_day,
                                                                                                   })],
                                                                   })
                
                employee_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',line.employee_id.id)])
                if employee_ids:
                    
                    val2={'punch_in_out_id':employee_ids[0], 
                          'employee_id': line.employee_id.id,
                          'work_date':line.work_date, 
                          'planned_work_shift_id':line.planned_work_shift_id.id,
                          'actual_work_shift_id':line.actual_work_shift_id.id,
                          'in_time':line.in_time,
                          'out_time':line.out_time,
                          'approval':1,
                          'diff_day': line.diff_day,
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
                          'approval':1,
                          'diff_day': line.diff_day,
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
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                continue
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
            self.write(cr, uid, [line.id],{'approval': False, 'state':'cancel', 'time_evaluate_id':False})
        return True
    #TPT
    def rollback_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': False, 'state':'draft'})
        return True
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_for_audit_shift_pri_auditor'):
            primary_auditor_ids = self.pool.get('hr.department').search(cr, uid, [('primary_auditor_id','=',uid)])
            if primary_auditor_ids:
                sql = '''
                    select id from arul_hr_audit_shift_time where
                        employee_id in (select id from hr_employee
                            where department_id in (select id from hr_department where primary_auditor_id =%s))
                '''%(uid)
                cr.execute(sql)
                leave_details_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',leave_details_ids)]
        return super(arul_hr_audit_shift_time, self).search(cr, uid, args, offset, limit, order, context, count)

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
            #APPEND HERE        
            leave_details_obj = self.pool.get('employee.leave.detail')
            emp_leave_obj = self.pool.get('employee.leave')
            year_now = time.strftime('%Y')
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',date.employee_id.id),('year','=',date.date_from[:4])])
            if emp_leave_ids:
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                temp = 0
                for line in emp_leave.emp_leave_details_ids:
                    if line.leave_type_id.id == date.leave_type_id.id and date.leave_type_id.code != 'LOP' and date.leave_type_id.code != 'ESI': #TPT BalamuruganPurushothaman on 17/02/2015 - To treat ESI as same as LOP
                        temp += 1
                        day = line.total_day - line.total_taken
                        if timedelta > day and line.leave_type_id.code!='LOP' and line.leave_type_id.code != 'ESI': # To treat ESI as same as LOP
                            raise osv.except_osv(_('Warning!'),_('The Taken Day Must Be Less Than The Limit!'))
                    if date.leave_type_id.code == 'LOP' or date.leave_type_id.code == 'ESI': # To treat ESI as same as LOP
                        temp += 1
                        leave = leave_details_obj.search(cr, uid, [('emp_leave_id','=',emp_leave.id),('leave_type_id','=',date.leave_type_id.id)])
                        if not leave:
                            leave_details_obj.create(cr,uid,{'emp_leave_id':emp_leave.id,
                                                      'leave_type_id':date.leave_type_id.id,}) 
                if temp == 0:
                    raise osv.except_osv(_('Warning!'),_('Leave Type Is Unlicensed For Employee Category And Employee Sub Category!'))
            else:
                raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Year'))
            res[date.id] = {
                'days_total': timedelta
            }
        return res
    
    def _available_leave(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        DATETIME_FORMAT = "%Y-%m-%d"
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            day = 0
            from_dt = datetime.datetime.strptime(line.date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(line.date_to, DATETIME_FORMAT)
            timedelta = (to_dt - from_dt).days+1
            if line.haft_day_leave:
                timedelta = timedelta-0.5
            leave_details_obj = self.pool.get('employee.leave.detail')
            emp_leave_obj = self.pool.get('employee.leave')
            year_now = line.date_from[0:4]
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',line.employee_id.id),('year','=',year_now)])
            if emp_leave_ids:
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                temp = 0
                for line_leave in emp_leave.emp_leave_details_ids:
                    if line_leave.leave_type_id.id == line.leave_type_id.id:
                        temp += 1
                        day = line_leave.total_day - line_leave.total_taken
            res[line.id] = day
        return res
    
    def _get_line(self, cr, uid, ids, context=None):
        result = {}
        leave_detail_ids = self.pool.get('arul.hr.employee.leave.details').search(cr, uid, [])
        for line in leave_detail_ids:
            result[line] = True
        return result.keys()
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'leave_type_id':fields.many2one('arul.hr.leave.types','Leave Type',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'date_from':fields.date('Date From',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'date_to': fields.date('To Date',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'days_total': fields.function(days_total, string='Total Leaves',store=True, multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'haft_day_leave': fields.boolean('Is Half Day Leave ?', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'check_leave_type_pl': fields.boolean('Check Leave Type PL'),
#               'available_leave': fields.float('Available Leave',readonly=True),
                'available_leave': fields.function(_available_leave, string='Available Leave',store={
                    'arul.hr.employee.leave.details': (_get_line, ['date_from','date_to','employee_id','leave_type_id','haft_day_leave'], 10),
                    'arul.hr.employee.leave.details': (_get_line, ['state'], 20),                                                                                 
                    }, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'reason':fields.char('Reason for Leave', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('reject', 'Rejected'),('done', 'Done')],'Status', readonly=True),
              'leave_evaluate_id': fields.many2one('tpt.time.leave.evaluation','Leave Evaluation'),
              'check_leave_type_lop_esi': fields.boolean('Check Leave Type LOP_ESI'),
              'reason_for_reject':fields.text('Reason for Rejection', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              'check_reject_flag': fields.boolean('Check Reject Option'),
              'type_half': fields.selection([('first_half','First Half'),('second_half','Second Half')],'Type Half'),
              'day': fields.many2one('tpt.month','Day'),
              }
    _defaults = {
        'state':'draft',
        'type_half': 'first_half',
    }
    
    def _check_date_holiday(self, cr, uid, ids, context=None):
        for leave in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_hr_permission_onduty where employee_id = %s and non_availability_type_id ='permission' and date between '%s' and '%s' and approval = 't'
            '''%(leave.employee_id.id, leave.date_from, leave.date_to)   
            cr.execute(sql)
            employee_dates = [r[0] for r in cr.fetchall()]
            if employee_dates:
                raise osv.except_osv(_('Warning!'),_('The Leave Day do not suitable'))
                return False
              
            sql = '''
                select id from arul_hr_audit_shift_time where employee_id = %s and work_date between '%s' and '%s' and approval = 't'
            '''%(leave.employee_id.id, leave.date_from, leave.date_to)   
            cr.execute(sql)
            employee_work_dates = [r[0] for r in cr.fetchall()]
            if employee_work_dates:
                raise osv.except_osv(_('Warning!'),_('The Leave Day do not suitable'))
                return False
            
            sql = '''
                select id from arul_hr_permission_onduty where employee_id = %s and non_availability_type_id ='on_duty' and (from_date between '%s' and '%s' or to_date between '%s' and '%s' or '%s' between from_date and to_date or '%s' between from_date and to_date)  and approval = 't'
            '''%(leave.employee_id.id, leave.date_from, leave.date_to,leave.date_from, leave.date_to,leave.date_from, leave.date_to)
            cr.execute(sql)
            employee_dates = [r[0] for r in cr.fetchall()]
            if employee_dates:
                raise osv.except_osv(_('Warning!'),_('The Leave Day do not suitable'))
                return False
        return True
         
    
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
        
#         per_onduty_obj = self.pool.get('arul.hr.permission.onduty')  
#         sql = '''
#             select * from arul_hr_permission_onduty where employee_id = %s and date between '%s' and '%s' and approval = True
#         '''%(vals['employee_id'], vals['date_from'], vals['date_to'])   
#         cr.execute(sql)
#         employee_dates = [r[0] for r in cr.fetchall()]
#         if employee_dates:
#             raise osv.except_osv(_('Warning!'),_('The Leave Day do not suitable'))
#          
#         sql = '''
#             select * from arul_hr_audit_shift_time where employee_id = %s and work_date between '%s' and '%s'
#         '''%(vals['employee_id'], vals['date_from'], vals['date_to'])   
#         cr.execute(sql)
#         employee_work_dates = [r[0] for r in cr.fetchall()]
#         if employee_work_dates:
#             raise osv.except_osv(_('Warning!'),_('The Leave Day do not suitable'))
        
                
                   
        #TPT START-By BalamuruganPurushothaman ON 14/03/2015-If CL/SL/C.OFF is taken a Half Day,
        #then system would not allow the same for next Half a day Except ESI/LOP
        if vals['haft_day_leave']:
            if vals['date_from'] == vals['date_to']:
                emp_leave_count = 0
                sql = '''
                        select COUNT(id)  from arul_hr_employee_leave_details where employee_id = %s 
                        and date_to = '%s' and haft_day_leave = True and days_total=0.5 and leave_type_id in 
                        (select id from arul_hr_leave_types where code in ('CL','SL','C.Off'))
                    '''%(vals['employee_id'],vals['date_to'])
                cr.execute(sql)
                    
                a1 = cr.fetchone()
                emp_leave_count = a1[0]
                
                sql = '''   select id from arul_hr_leave_types where code ='CL'  '''
                cr.execute(sql)                    
                cl1 = cr.fetchone()
                cl = cl1[0]                
                
                sql = '''   select id from arul_hr_leave_types where code ='SL' '''
                cr.execute(sql)                    
                sl1 = cr.fetchone()
                sl = sl1[0]               
                
                sql = '''   select id from arul_hr_leave_types where code ='C.Off' '''
                cr.execute(sql)                    
                coff1 = cr.fetchone()
                coff = coff1[0]
                    
                if emp_leave_count == 1 and vals['leave_type_id']==cl:                                         
                    raise osv.except_osv(_('Warning!'),_('Only LOP/ESI is possible for another Half a Day Leave'))
                if emp_leave_count == 1 and vals['leave_type_id']==sl:                                         
                    raise osv.except_osv(_('Warning!'),_('Only LOP/ESI is possible for another Half a Day Leave'))
                if emp_leave_count == 1 and vals['leave_type_id']==coff:                                         
                    raise osv.except_osv(_('Warning!'),_('Only LOP/ESI is possible for another Half a Day Leave'))
            #TPT END  
        new_id1 = False
        new_id2 = False       
        vals.update({'check_reject_flag':True}) #TPT-BalamurugaPurushothaman on 12/03/2015
        
        if 'date_from' in vals and 'date_to' in vals:
            day_obj = self.pool.get('tpt.month')
            date_from = vals['date_from']
            date_to = vals['date_to']
            vals1 = vals
            vals2 = vals
            vals13={}
            vals23={}
            if date_from[5:7] != date_to[5:7]:
                if vals['haft_day_leave']:
                    if 'day' in vals:
                        vals13={'day':vals['day'],'haft_day_leave':vals['haft_day_leave'],'type_half':vals['type_half']}
                        vals23={'day':vals['day'],'haft_day_leave':vals['haft_day_leave'],'type_half':vals['type_half']}
                        day = day_obj.browse(cr, uid, vals['day'])
                        if day.name>=int(date_from[8:10]):
                            vals23.update({'day':False})
                            vals23.update({'haft_day_leave':False})
                            vals23.update({'type_half':False})
                        if day.name<=int(date_to[8:10]):
                            vals13.update({'day':False})
                            vals13.update({'haft_day_leave':False})
                            vals13.update({'type_half':False})
                num_of_month = calendar.monthrange(int(date_from[:4]),int(date_from[5:7]))[1]
                vals1['date_from'] = date_from
                vals1['date_to']=date_from[:4]+'-'+date_from[5:7]+'-'+str(num_of_month)
                vals1.update(vals13)
                new_id1 = super(arul_hr_employee_leave_details, self).create(cr, uid, vals1, context)
                vals2.update(vals23)
                vals2['date_from'] = date_to[:4]+'-'+date_to[5:7]+'-01'
                vals2['date_to'] = date_to
                new_id2 = super(arul_hr_employee_leave_details, self).create(cr, uid, vals2, context)
        if new_id1:
            return new_id1
        elif new_id2:
            return new_id2
        else:
            return super(arul_hr_employee_leave_details, self).create(cr, uid, vals, context)
    
    def unlink(self, cr, uid, ids, context=None):
        leave_details = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for ld in leave_details:
            if ld['state'] in ['draft', 'cancel']:
                unlink_ids.append(ld['id'])
            else:
                raise osv.except_osv(_('Warning!'), _('In employee leave details to delete a confirmed employee leave details, You can not delete it!'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
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
        vals = {}
        vals = {'available_leave':0.0}
        if leave_type_id:
            leave_type_obj = self.pool.get('arul.hr.leave.types')
            leave_type = leave_type_obj.browse(cr, uid, leave_type_id)
            if leave_type.code == "PL":
                vals.update({'check_leave_type_pl':True,'haft_day_leave':False})
            else:
                vals.update({'check_leave_type_pl':False})
                
            #TPT - To Hide Leave Balance for ESI,LOP Leaves
            if leave_type.code == "LOP" or leave_type.code == "ESI":
                vals.update({'check_leave_type_lop_esi':True})
            else:
                vals.update({'check_leave_type_lop_esi':False})
                                         
        if employee_id and leave_type_id and date_from:
            leave_details_obj = self.pool.get('employee.leave.detail')
            emp_leave_obj = self.pool.get('employee.leave')
            year_now = date_from[:4]
#             year_now = time.strftime('%Y')
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',employee_id),('year','=',year_now)])
            if emp_leave_ids:
                available_leave = 0.0
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                for line in emp_leave.emp_leave_details_ids:
                    if line.leave_type_id.id == leave_type_id:
                        available_leave = line.total_day - line.total_taken
#                 vals['available_leave'] = available_leave
        if date_from and date_to and employee_id and leave_type_id:
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            timedelta = (to_dt - from_dt).days+1
            if haft_day_leave:
                timedelta = timedelta-0.5
            leave_details_obj = self.pool.get('employee.leave.detail')
            emp_leave_obj = self.pool.get('employee.leave')
            year_now = date_from[0:4]
            leave_lop_ids = leave_type_obj.search(cr, uid, [('code','=','LOP')])
            leave_lop_id = leave_type_obj.browse(cr, uid, leave_lop_ids[0])
	    #Start:TPT - BalamuruganPurushothaman on 17/02/2015 - To treat ESI same as LOP
	    leave_esi_ids = leave_type_obj.search(cr, uid, [('code','=','ESI')])
            leave_esi_id = leave_type_obj.browse(cr, uid, leave_esi_ids[0])
	    #End:TPT - BalamuruganPurushothaman - To treat ESI same as LOP
#             year_now = time.strftime('%Y')
            emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',employee_id),('year','=',year_now)])
            if emp_leave_ids:
                emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                temp = 0
                for line in emp_leave.emp_leave_details_ids:
                    if line.leave_type_id.id == leave_type_id:
                        temp += 1
                        day = line.total_day - line.total_taken
                        if timedelta > day and line.leave_type_id.code!='LOP' and line.leave_type_id.code!='ESI': #To treat ESI same as LOP
                            raise osv.except_osv(_('Warning!'),_('The Taken Day Must Be Less Than The Limit'))
                if temp == 0 and leave_lop_id.id != leave_type_id and leave_esi_id.id != leave_type_id: #To treat ESI same as LOP
                    raise osv.except_osv(_('Warning!'),_('Leave Type Is Unlicensed For Employee Category And Employee Sub Category!'))
            else:
                raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Current Year'))
        return {'value':vals}
    
    def process_leave_request(self, cr, uid, ids, context=None):
        DATETIME_FORMAT = "%Y-%m-%d"
        for line in self.browse(cr, uid, ids):
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                from_dt = datetime.datetime.strptime(line.date_from, DATETIME_FORMAT)
                to_dt = datetime.datetime.strptime(line.date_to, DATETIME_FORMAT)
                timedelta = (to_dt - from_dt).days+1
                if line.haft_day_leave:
                    timedelta = timedelta-0.5
                leave_details_obj = self.pool.get('employee.leave.detail')
                emp_leave_obj = self.pool.get('employee.leave')
                year_now = line.date_from[0:4]
        #             year_now = time.strftime('%Y')
                emp_leave_ids = emp_leave_obj.search(cr, uid, [('employee_id','=',line.employee_id.id),('year','=',year_now)])
                if emp_leave_ids:
                    emp_leave = emp_leave_obj.browse(cr, uid, emp_leave_ids[0])
                    temp = 0
                    for line_leave in emp_leave.emp_leave_details_ids:
                        if line_leave.leave_type_id.id == line.leave_type_id.id:
                            temp += 1
                            day = line_leave.total_day - line_leave.total_taken
                            if timedelta > day and line_leave.leave_type_id.code!='LOP' and line_leave.leave_type_id.code!='ESI':#TPT BalamuruganPurushothaman on 17/02/2015 - To treat ESI as same as LOP
                                raise osv.except_osv(_('Warning!'),_('The Taken Day Must Be Less Than The Limit'))
                    if temp == 0:
                        raise osv.except_osv(_('Warning!'),_('Leave Type Is Unlicensed For Employee Category And Employee Sub Category!'))
                else:
                    raise osv.except_osv(_('Warning!'),_('Employee Has Not Been Licensed Holidays For The Current Year'))
                self.write(cr, uid, [line.id],{'state':'done','leave_evaluate_id': False,'check_reject_flag':False}) #TPT check_reject_flag is marked as false after approve
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
        return True  
    #TPT:START 
    def reject_leave_request(self, cr, uid, ids, context=None):  
        for line in self.browse(cr, uid, ids): 
            #vals = {}
            #vals.update({'check_reject_flag':True})
            if line.reason_for_reject:    
                self.write(cr, uid, [line.id],{'state':'reject','leave_evaluate_id':False,'check_reject_flag':True})
            else:
                raise osv.except_osv(_('Warning!'),_('Please Edit & Provide Reason for Rejection!'))
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
        return True  
    #TPT:E
    def cancel_leave_request(self, cr, uid, ids, context=None):
        date_now = time.strftime('%Y-%m-%d')
        for line in self.browse(cr, uid, ids):
            if line.date_from < date_now:
                raise osv.except_osv(_('Warning!'),_('Can not Cancel for past day!'))
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
#             sql = '''
#                 update arul_hr_employee_leave_details set state='cancel', leave_evaluate_id = null where id = %s
#             '''%(line.id)
#             cr.execute(sql)
            self.write(cr, uid, [line.id],{'state':'cancel','leave_evaluate_id':False})
        return True  
    
    def _check_days(self, cr, uid, ids, context=None): 
        for days in self.browse(cr, uid, ids, context = context):
            date_from = datetime.datetime.strptime(days.date_from, "%Y-%m-%d")
            date_to = datetime.datetime.strptime(days.date_to, "%Y-%m-%d")
            if date_from > date_to:
                raise osv.except_osv(_('Warning!'),_('The start date must be before to the end date.'))
                return False
            return True       
    def _check_days_2(self, cr, uid, ids, context=None): 
        day = self.browse(cr, uid, ids[0])
        if day and day.employee_id and day.date_from and day.date_to:
            date_from = datetime.datetime.strptime(day.date_from, "%Y-%m-%d")
            date_to = datetime.datetime.strptime(day.date_to, "%Y-%m-%d")
            #TPT: SQL IS MODIFIED FOR LEAVE RE-GENERATION IF LEAVE IS IN CANCEL STATE
            sql = '''
                select id from arul_hr_employee_leave_details where id != %s and employee_id = %s and (('%s' between date_from and date_to) or ('%s' between date_from and date_to)) and state != 'cancel'
            '''%(day.id,day.employee_id.id,date_from.strftime('%Y-%m-%d'),date_to.strftime('%Y-%m-%d'))
            cr.execute(sql)
            leave_ids = [row[0] for row in cr.fetchall()]
#                 leave_ids.remove(day.id)
            sql = '''
                select id from arul_hr_employee_leave_details where id != %s and employee_id = %s and ((date_from between '%s' and '%s') and (date_to between '%s' and '%s')) and state != 'cancel'
            '''%(day.id,day.employee_id.id,date_from.strftime('%Y-%m-%d'),date_to.strftime('%Y-%m-%d'),date_from.strftime('%Y-%m-%d'),date_to.strftime('%Y-%m-%d'))
            cr.execute(sql)
            leave_1_ids = [row[0] for row in cr.fetchall()]
            if not day.haft_day_leave:
                if leave_ids or leave_1_ids:  
                    raise osv.except_osv(_('Warning!'),_('The Employee requested leave day for these date!'))
            else:
                if date_from == date_to:
                    sql2 = '''
                        select id from arul_hr_employee_leave_details where id != %s and employee_id = %s and date_to = '%s' and haft_day_leave = True and type_half='%s'
                    '''%(day.id,day.employee_id.id,date_to.strftime('%Y-%m-%d'),day.type_half)
                    cr.execute(sql2)
                    leave_t_ids = [row[0] for row in cr.fetchall()]
                    if leave_t_ids:  
                        raise osv.except_osv(_('Warning!'),_('The Employee requested leave day for these date!'))
                else:
                    if leave_ids or leave_1_ids:  
                        raise osv.except_osv(_('Warning!'),_('The Employee requested leave day for these date!'))
        return True   
    _constraints = [
        (_check_days, _(''), ['date_from', 'date_to']),
        (_check_days_2, _(''), ['employee_id','date_from', 'date_to']),
        (_check_date_holiday, _(''), ['employee_id','date_from', 'date_to']),
    ]
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_for_primary_auditor'):
            primary_auditor_ids = self.pool.get('hr.department').search(cr, uid, [('primary_auditor_id','=',uid)])
            if primary_auditor_ids:
                sql = '''
                    select id from arul_hr_employee_leave_details where
                        employee_id in (select id from hr_employee
                            where department_id in (select id from hr_department where primary_auditor_id =%s))
                '''%(uid)
                cr.execute(sql)
                leave_details_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',leave_details_ids)]
        return super(arul_hr_employee_leave_details, self).search(cr, uid, args, offset, limit, order, context, count)

arul_hr_employee_leave_details()


class arul_hr_permission_onduty(osv.osv):
    _name='arul.hr.permission.onduty'
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(arul_hr_permission_onduty, self).create(cr, uid, vals, context)
        permission = self.browse(cr, uid, new_id)
        sql = '''
            select id from arul_hr_capture_work_shift where (%s between start_time - 0.5 and start_time + 0.25) and (%s >= end_time-0.25)
        '''%(permission.start_time,permission.end_time)
        cr.execute(sql)
        work_shift_ids = [row[0] for row in cr.fetchall()]
        
        punch_obj = self.pool.get('arul.hr.punch.in.out')
        
        if permission.non_availability_type_id == 'on_duty' and not permission.date:
            date_from = datetime.datetime.strptime(permission.from_date,'%Y-%m-%d')
            date_to = datetime.datetime.strptime(permission.to_date,'%Y-%m-%d')
            while (date_from<=date_to):
                day = date_from.day
                month = date_from.month
                year = date_from.year
                shift_id = punch_obj.get_work_shift(cr, uid, permission.employee_id.id, int(day), int(month), year)
                self.create(cr, uid, {
                                        'employee_id': permission.employee_id.id,
                                        'non_availability_type_id': 'on_duty',
                                        'date': date_from,
                                        'duty_location': permission.duty_location,
                                        'start_time': permission.start_time,
                                        'end_time': permission.end_time,
                                        'reason':permission.reason,
                                        'parent_id': permission.id,
                                        }, context)
                
#                 self.pool.get('arul.hr.audit.shift.time').create(cr, SUPERUSER_ID, {
#                     'employee_id':permission.employee_id.id,
#                     'work_date':date_from,
#                     'employee_category_id':permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.id or False,
#                     'planned_work_shift_id': shift_id,
#                     'actual_work_shift_id': work_shift_ids and work_shift_ids[0] or False,
#                     'in_time':permission.start_time,
#                     'out_time':permission.end_time,
#                     'type': 'permission',
#                     'permission_id':new_id,
#                 })
                date_from += datetime.timedelta(days=1)
        else:
            day = permission.date[8:10]
            month = permission.date[5:7]
            year = permission.date[:4]
	    # TPT - The following if condition is commented to check permission for emp categ "S1"also
            #if permission.non_availability_type_id=='permission' and permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.code != 'S1':
	    if permission.non_availability_type_id=='permission' and permission.employee_id.employee_category_id:
                sql = '''
                    select count(id) as num_of_permission from arul_hr_permission_onduty where non_availability_type_id='permission' and employee_id=%s
                        and id!=%s and EXTRACT(year from date)='%s' and EXTRACT(month from date)='%s'
                '''%(permission.employee_id.id,permission.id,year,month)
                cr.execute(sql)
                p = cr.dictfetchone()		
                if p and p['num_of_permission']==2:
                    raise osv.except_osv(_('Warning!'),_('Employee %s have 2 permission for this month!')%(permission.employee_id.name+' '+(permission.employee_id.last_name or '')))
                #TPT SATRT
                sql = '''
                    select count(id) as num_of_permission from arul_hr_permission_onduty where non_availability_type_id='permission' and employee_id=%s
                        and id!=%s and EXTRACT(year from date)='%s'
                '''%(permission.employee_id.id,permission.id,year)
                cr.execute(sql)
                p = cr.dictfetchone()        
                if p and p['num_of_permission']>=11:
                    raise osv.except_osv(_('Warning!'),_('NO MORE PERMISSION PERMITTED.\n Employee %s have already taken 10 permission for this year!')%(permission.employee_id.name+' '+(permission.employee_id.last_name or '')))
                #TPT ENDs
            shift_id = punch_obj.get_work_shift(cr, uid, permission.employee_id.id, int(day), int(month), year)
#             self.pool.get('arul.hr.audit.shift.time').create(cr, SUPERUSER_ID, {
#                  'employee_id':permission.employee_id.id,
#                  'work_date':permission.date,
#                  'employee_category_id':permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.id or False,
#                  'planned_work_shift_id': shift_id,
#                  'actual_work_shift_id': work_shift_ids and work_shift_ids[0] or False,
#                  'in_time':permission.start_time,
#                  'out_time':permission.end_time,
#                  #'type': 'permission', #TPT Changes - Commented
#  		        'type': permission.non_availability_type_id,#TPT Changes - By BalamuruganPurushothaman on 21/02/2015 - To Update NonAvailability Status in Audit Shift Screen.
#                  'permission_id':new_id,
#              })
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
    #TPT - Permission On Duty
    def _shift_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for time in self.browse(cr, uid, ids, context=context):
            res[time.id] = {
                'total_shift_worked': 0.0,
            }
            if time.time_total <= 1.0:            
                res[time.id]['total_shift_worked'] = 0.125
            if time.time_total >= 1.1 and time.time_total <= 2.0:            
                res[time.id]['total_shift_worked'] = 0.25
            if time.time_total >= 2.1 and time.time_total <= 3.0:            
                res[time.id]['total_shift_worked'] = 0.375             
            if time.time_total >= 4.0 and time.time_total <= 7.44:            
                res[time.id]['total_shift_worked'] = 0.5    
            if time.time_total >= 7.45 and time.time_total <= 8.30:            
                res[time.id]['total_shift_worked'] = 1.0
            if time.time_total >8.30  and time.time_total <= 11.44:            
                res[time.id]['total_shift_worked'] = 1.0
            if time.time_total >=11.45  and time.time_total <= 15.44:            
                res[time.id]['total_shift_worked'] = 1.5
            if time.time_total >=15.45  and time.time_total <= 15.45:            
                res[time.id]['total_shift_worked'] = 1.5
            if time.time_total >=15.45:            
                res[time.id]['total_shift_worked'] = 2.0
        return res
    #TPT
    _columns={
        'employee_id':fields.many2one('hr.employee','Employee',required=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'non_availability_type_id':fields.selection([('permission','Permission'),('on_duty','On duty')],'Non Availability Type',required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'date':fields.date('Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'from_date':fields.date('From Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'to_date':fields.date('To Date', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'duty_location':fields.char('On Duty Location', size = 1024, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'start_time': fields.float('Start Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'end_time': fields.float('End Time', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'time_total': fields.function(_time_total, string='Total Hours', multi='sums', help="The total amount.", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'reason':fields.text('Reason', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        'permission_onduty_id':fields.many2one('arul.hr.employee.attendence.details','Permission/Onduty',ondelete='cascade'),
        'approval': fields.boolean('Is Approved?', readonly =  True),
        'parent_id':fields.many2one('arul.hr.permission.onduty','Permission/Onduty',ondelete='cascade'),
        'permission_onduty_line':fields.one2many('arul.hr.permission.onduty','parent_id','Onduty Line',readonly=True),
#         'detail_id':fields.many2one('arul.hr.employee.attendence.details','Detail'),
        #TPT-Permission On Duty
        'total_shift_worked': fields.function(_shift_total, store=True, string='No.Of Shift Worked', multi='shift_sums', help="The total amount."),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Reject'),('done', 'Approve')],'Status', readonly=True),
              }
    _defaults = {
           'state': 'draft',  
                 }
    
    def approve_permission_onduty(self, cr, uid, ids, context=None):
        permission = self.browse(cr, uid, ids[0])
        sql = '''
            select id from arul_hr_capture_work_shift where (%s between start_time - 0.5 and start_time + 0.25) and (%s >= end_time-0.25)
        '''%(permission.start_time,permission.end_time)
        cr.execute(sql)
        work_shift_ids = [row[0] for row in cr.fetchall()]
        
        punch_obj = self.pool.get('arul.hr.punch.in.out')
        audit_obj = self.pool.get('arul.hr.audit.shift.time')
        if permission.non_availability_type_id == 'on_duty' and not permission.date:
            date_from = datetime.datetime.strptime(permission.from_date,'%Y-%m-%d')
            date_to = datetime.datetime.strptime(permission.to_date,'%Y-%m-%d')
            while (date_from<=date_to):
                day = date_from.day
                month = date_from.month
                year = date_from.year
                shift_id = punch_obj.get_work_shift(cr, uid, permission.employee_id.id, int(day), int(month), year)
                self.create(cr, uid, {
                                        'employee_id': permission.employee_id.id,
                                        'non_availability_type_id': 'on_duty',
                                        'date': date_from,
                                        'duty_location': permission.duty_location,
                                        'start_time': permission.start_time,
                                        'end_time': permission.end_time,
                                        'reason':permission.reason,
                                        'parent_id': permission.id,
                                        }, context)
                
                audit_id = audit_obj.create(cr, SUPERUSER_ID, {
                    'employee_id':permission.employee_id.id,
                    'work_date':date_from,
                    'employee_category_id':permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.id or False,
                    'planned_work_shift_id': shift_id,
                    'actual_work_shift_id': work_shift_ids and work_shift_ids[0] or False,
                    'in_time':permission.start_time,
                    'out_time':permission.end_time,
                    'type': 'permission',
                    'permission_id':ids[0],
                })
                audit_obj.approve_shift_time(cr, SUPERUSER_ID,[audit_id])
                date_from += datetime.timedelta(days=1)
        else:
            day = permission.date[8:10]
            month = permission.date[5:7]
            year = permission.date[:4]
        # TPT - The following if condition is commented to check permission for emp categ "S1"also
            #if permission.non_availability_type_id=='permission' and permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.code != 'S1':
        if permission.non_availability_type_id=='permission' and permission.employee_id.employee_category_id:
                sql = '''
                    select count(id) as num_of_permission from arul_hr_permission_onduty where non_availability_type_id='permission' and employee_id=%s
                        and id!=%s and EXTRACT(year from date)='%s' and EXTRACT(month from date)='%s'
                '''%(permission.employee_id.id,permission.id,year,month)
                cr.execute(sql)
                p = cr.dictfetchone()        
                if p and p['num_of_permission']==2:
                    raise osv.except_osv(_('Warning!'),_('Employee %s have 2 permission for this month!')%(permission.employee_id.name+' '+(permission.employee_id.last_name or '')))
                #TPT SATRT
                sql = '''
                    select count(id) as num_of_permission from arul_hr_permission_onduty where non_availability_type_id='permission' and employee_id=%s
                        and id!=%s and EXTRACT(year from date)='%s'
                '''%(permission.employee_id.id,permission.id,year)
                cr.execute(sql)
                p = cr.dictfetchone()        
                if p and p['num_of_permission']>=11:
                    raise osv.except_osv(_('Warning!'),_('NO MORE PERMISSION PERMITTED.\n Employee %s have already taken 10 permission for this year!')%(permission.employee_id.name+' '+(permission.employee_id.last_name or '')))
                #TPT ENDs
                shift_id = punch_obj.get_work_shift(cr, uid, permission.employee_id.id, int(day), int(month), year)
                audit_id = audit_obj.create(cr, SUPERUSER_ID, {
                 'employee_id':permission.employee_id.id,
                 'work_date':permission.date,
                 'employee_category_id':permission.employee_id.employee_category_id and permission.employee_id.employee_category_id.id or False,
                 'planned_work_shift_id': shift_id,
                 'actual_work_shift_id': work_shift_ids and work_shift_ids[0] or False,
                 'in_time':permission.start_time,
                 'out_time':permission.end_time,
                 #'type': 'permission', #TPT Changes - Commented
                 'type': permission.non_availability_type_id,#TPT Changes - By BalamuruganPurushothaman on 21/02/2015 - To Update NonAvailability Status in Audit Shift Screen.
                 'permission_id':ids[0],
             })
                audit_obj.approve_shift_time(cr, SUPERUSER_ID,[audit_id])
        return self.write(cr,uid,ids,{'state': 'done'}) 
    
    def reject_permission_onduty(self, cr, uid, ids, context=None):
        return self.write(cr,uid,ids,{'state': 'cancel'}) 
        
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
            if time.start_time == 0.0 and time.end_time == 0.0:
                raise osv.except_osv(_('Warning!'),_('Input Wrong Time'))
                return False
            #TPT - BalamuruganPurushothaman on 10/03/2014 - To throw warning when onduty entered for same time for same date
            if time.non_availability_type_id=='on_duty':                
                sql = '''
                    SELECT COUNT(*) FROM arul_hr_permission_onduty WHERE 
                    start_time <='%s' AND end_time >= '%s' and employee_id=%s 
                    AND to_char(from_date,'YYYY-MM-DD')=('%s') AND to_char(to_date,'YYYY-MM-DD')=('%s')        
                    ''' %(time.start_time,time.end_time,time.employee_id.id,time.from_date,time.to_date)
                cr.execute(sql)
                p = cr.fetchone()   
                #raise osv.except_osv(_('Warning!%s'),_(p[0]))           
                if p[0]-1>0:
                    raise osv.except_osv(_('Warning!'),_('OnDuty Already Entered for this Time Period'))  
  
            #TPT - BalamuruganPurushothaman on 10/03/2014 - To throw warning when permission entered for same date    
            if time.non_availability_type_id=='permission':
                sql = '''
                    SELECT COUNT(*) FROM arul_hr_permission_onduty WHERE 
                    employee_id=%s 
                    AND to_char(date,'YYYY-MM-DD')=('%s')        
                    ''' %(time.employee_id.id,time.date)
                cr.execute(sql)
                p = cr.fetchone()   
                #raise osv.except_osv(_('Warning!%s'),_(p[0]))           
                if p[0]-1>0:
                    raise osv.except_osv(_('Warning!'),_('Permission Entry Already Exist for this Employee'))   
                if time.end_time - time.start_time > 1:
                    raise osv.except_osv(_('Warning!'),_('Permission should not exceed an Hour for a day')) 
        return True
    
    def print_gate_pass(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'arul.hr.permission.onduty',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'gate_pass_report',
            }
    
    def _check_date_from_to(self, cr, uid, ids, context=None): 
        for permission_onduty in self.browse(cr, uid, ids, context = context):
            if permission_onduty.non_availability_type_id and permission_onduty.to_date < permission_onduty.from_date:
                raise osv.except_osv(_('Warning!'),_('From Date is earlier than To Date'))
                return False
        return True    
    _constraints = [
        (_check_time, _(''), ['start_time', 'end_time']),
        (_check_date_from_to, _(''), ['from_date', 'to_date']),
        ]
    
   
arul_hr_permission_onduty()

class arul_hr_punch_in_out_time(osv.osv):
    _name='arul.hr.punch.in.out.time'
     
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
            if time.diff_day and (time.in_time <= time.out_time):
                time_total += 24
                    
            res[time.id]['total_hours'] = time_total 
        return res
    #TPT - Punch InOut
    def _shift_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for time in self.browse(cr, uid, ids, context=context):
            res[time.id] = {
                'total_shift_worked': 0.0,
            }
            #raise osv.except_osv(_('Warning!%s'),time.actual_work_shift_id.code)
            sql = '''
            select start_time,end_time from arul_hr_capture_work_shift where code = '%s'

            '''%(time.actual_work_shift_id.code)
            cr.execute(sql)
            a = cr.fetchall()
            #TPT SHIFT
            if time.in_time != 0 and time.out_time!=0: 
                if time.actual_work_shift_id.code=='A':
                    res[time.id]['a_shift_count'] = 1.0
                if time.actual_work_shift_id.code=='B':
                    res[time.id]['b_shift_count'] = 1.0
                if time.actual_work_shift_id.code=='C':
                    res[time.id]['c_shift_count'] = 1.0
                if time.actual_work_shift_id.code=='G1':
                    res[time.id]['g1_shift_count'] = 1.0
                if time.actual_work_shift_id.code=='G2':
                    res[time.id]['g2_shift_count'] = 1.0
                '''    
                if time.in_time >= 6.00:
                    if time.out_time <= 14.30:         
                        res[time.id]['a_shift_count'] = 1.0
                if 13.45 >=time.in_time and 23.55 <= time.out_time:         
                    res[time.id]['b_shift_count'] = 1.0
                #if 21.30 >=time.in_time and 9.55 <= time.out_time:         
                #    res[time.id]['c_shift_count'] = 1.0
                #if 8.00 >=time.in_time and 16.45 <= time.out_time:
                if 8.00 >=time.in_time and 16.45 <= time.out_time:          
                    res[time.id]['g1_shift_count'] = 1.0
                if 9.00 >=time.in_time and 17.45 <= time.out_time:         
                    res[time.id]['g2_shift_count'] = 1.0
                '''  
            #Permission
            permission_count = 0
            onduty_count = 0
            perm_onduty_count = 0
            sql = '''
            SELECT SUM(total_shift_worked) FROM arul_hr_permission_onduty WHERE 
            non_availability_type_id='permission' 
                AND TO_CHAR(date,'YYYY-MM-DD') = ('%s') and employee_id =%s
                '''%(time.work_date,time.employee_id.id)
            cr.execute(sql)
            b =  cr.fetchone()
            if b[0]:
                permission_count = b[0]
                
            #OnDuty
            sql = '''
                SELECT SUM(total_shift_worked) FROM arul_hr_permission_onduty WHERE non_availability_type_id='on_duty' 
                AND TO_CHAR(to_date,'YYYY-MM-DD') = ('%s') and employee_id =%s
                '''%(time.work_date,time.employee_id.id)
            cr.execute(sql)
            c =  cr.fetchone()
            if c[0]:
                onduty_count = c[0]
            
            perm_onduty_count =   permission_count + onduty_count
            
            if time.total_hours <= 1.0:            
                res[time.id]['total_shift_worked'] = 0.125 + perm_onduty_count
            if time.total_hours >= 1.1 and time.total_hours <= 2.0:            
                res[time.id]['total_shift_worked'] = 0.25 + perm_onduty_count
            if time.total_hours >= 2.1 and time.total_hours <= 3.0:            
                res[time.id]['total_shift_worked'] = 0.375 + perm_onduty_count        
            if time.total_hours >= 4.0 and time.total_hours <= 7.44:            
                res[time.id]['total_shift_worked'] = 0.5 + perm_onduty_count 
            if time.total_hours >= 7.45 and time.total_hours <= 8.30:            
                res[time.id]['total_shift_worked'] = 1.0 + perm_onduty_count
            if time.total_hours >8.30  and time.total_hours <= 11.44:            
                res[time.id]['total_shift_worked'] = 1.0 + perm_onduty_count
            if time.total_hours >=11.45  and time.total_hours <= 15.44:            
                res[time.id]['total_shift_worked'] = 1.5 + perm_onduty_count
            if time.total_hours >=15.45  and time.total_hours <= 15.45:            
                res[time.id]['total_shift_worked'] = 1.5 + perm_onduty_count
            if time.total_hours >=15.45:            
                res[time.id]['total_shift_worked'] = 2.0 + perm_onduty_count
            if time.total_hours >=23.45:            
                res[time.id]['total_shift_worked'] = 3.0 + perm_onduty_count
            
            #res[time.id]['shift_count']=res[time.id]['total_shift_worked']
            #res.update({'shift_count': res[time.id]['total_shift_worked']})
            
        return res
    #TPT 
    _columns = {
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
        'type':fields.selection([('permission', 'Permission'),('shift', 'Waiting'),('punch', 'Punch In/Out')],'Type', readonly=True),
        'permission_id':fields.many2one('arul.hr.permission.onduty','Permission/On Duty'),
        'time_evaluate_id': fields.many2one('tpt.time.leave.evaluation','Time Evaluation'),
        'punch_in_out_id':fields.many2one('arul.hr.employee.attendence.details','Punch in/out',ondelete='cascade'),
        'emp_id': fields.related('punch_in_out_id','employee_id',string="Employee",relation='hr.employee',type='many2one',readonly=True,store=True),
        'diff_day': fields.boolean('Difference Day', readonly = True),
        #TPT
        #TPT-Punch InOut - THIS COLUMN IS STORE IN DB TO GET THIS COUNT DURING PAYROLL PROCESS
        'total_shift_worked': fields.function(_shift_total, store=True, string='No.Of Shift Worked', multi='shift_punchinout_sums', help="The total amount."),
        #'shift_count': fields.function(_shift_total, store=True,string='Shift Count', multi='shift_punchinout2_sums', help="The total amount."),
        'a_shift_count': fields.function(_shift_total, string='A', multi='a_shift'),
        'b_shift_count': fields.function(_shift_total, string='B', multi='b_shift'),
        'c_shift_count': fields.function(_shift_total, string='C', multi='c_shift'),
        'g1_shift_count': fields.function(_shift_total, string='G1', multi='g1_shift'),
        'g2_shift_count': fields.function(_shift_total, string='G2', multi='g2_shift'),
        
        #'g1_shift_count': fields.float('G1', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        #'g2_shift_count': fields.float('G2', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        #'b_shift_count': fields.float('B', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        #'c_shift_count': fields.float('C', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
              
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
        'punch_in_out_line':fields.one2many('arul.hr.punch.in.out.time','punch_in_out_id','Punch in/Punch out Details',readonly=False)
              }
    #Start:TPT BalamuruganPurushothaman
    '''def print_empleave_details(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'arul.hr.employee.attendence.details',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'print_emp_leave_details',
        }'''
	#Start:TPT BalamuruganPurushothaman
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
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Upload/View Specification', type="binary", nodrop=True,states={'done': [('readonly', True)]}, required=True),
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
                shift_obj = self.pool.get('arul.hr.capture.work.shift')
                employee_leave_obj = self.pool.get('employee.leave')
                employee_leave_detail_obj = self.pool.get('employee.leave.detail')
                leave_type_obj = self.pool.get('arul.hr.leave.types')
                if L:
                    data = L[0]
                    date_old = data[7:11]+'-'+data[11:13]+'-'+data[13:15]
                for i,data1 in enumerate(L):
                    if data1 and (data1[:3]!='P10' and data1[:3]!='P20' or len(data1)<51):
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
#                             if date_old == date:
                            val1={'employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':False,'work_date':date,'punch_in_date':date,'in_time':in_time,'out_time':0,'approval':1}
                            for j,data2 in enumerate(L2):
                                #bat dau vi tri tiep theo cua for 1
                                in_out = data2[:3]
                                employee_code_2=data2[43:51]
                                date_2=data2[7:11]+'-'+data2[11:13]+'-'+data2[13:15]
                                out_date = data2[7:11]+'-'+data2[11:13]+'-'+data2[13:15]
                                if employee_code_2==employee_code and in_out=='P10':
                                    in_time2 = float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                    val1={'employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':False,'work_date':date,'punch_in_date':date,'in_time':in_time2,'out_time':0,'approval':1}
                                if employee_code_2==employee_code and in_out=='P20':
                                    out_time=float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                    out_date = data2[7:11]+'-'+data2[11:13]+'-'+data2[13:15]
                                    val1['out_time']=out_time
                                    val1['punch_out_date']=out_date
                                # cho phep di lam som nua tieng hoac di tre 15 phut va ve som 15 phut
				# TPT Changes - BalamuruganPurushothaman on 18/02/2015 - SQL Query is modified to check Grace Time for shift
                                    sql = '''
                                        select id from arul_hr_capture_work_shift where 
					(%s between 
					case when min_start_time>0.00 then (start_time-(start_time-min_start_time)) else start_time end
					and 
					case when max_start_time>0.00 then (start_time+(max_start_time-start_time)) else start_time end
					)
					and
					(%s between
					case when min_end_time>0.00 then (end_time-(end_time-min_end_time)) else end_time end
					and 
					case when max_end_time>0.00 then (end_time+(max_end_time-end_time)) else end_time end
					)
                                    '''%(in_time,out_time)
                                    cr.execute(sql)
                                    work_shift_ids = [row[0] for row in cr.fetchall()]
				    #raise osv.except_osv(_('Warning!%s'),sql)
                                    if work_shift_ids and shift_id:
                                        if shift_id == work_shift_ids[0]:
                                            
                                            extra_hours = 0.0
                                            c_off_day = 0.0
                                            shift = shift_obj.browse(cr, uid, shift_id)
                                            extra_hours = out_time - shift.end_time
                                            if extra_hours >= 4 and extra_hours < 8:
                                                c_off_day = 0.5
                                            if extra_hours >= 8 and extra_hours < 12:
                                                c_off_day = 1
                                            if extra_hours >= 12 and extra_hours < 16:
                                                c_off_day = 1.5
                                            if extra_hours >= 16:
                                                c_off_day = 2
                                            employee_leave_ids = employee_leave_obj.search(cr, uid, [('year','=',data1[7:11]),('employee_id','=',employee_ids[0])])
                                            leave_type_ids = leave_type_obj.search(cr, uid, [('code','=','C.Off')])
                                            if not leave_type_ids:
                                                raise osv.except_osv(_('Warning!'),_('Can not find Leave Type C.Off. Please Create Leave Type C.Off before'))
                                            if employee_leave_ids:
                                                employee_leave_detail_ids = employee_leave_detail_obj.search(cr, uid, [('emp_leave_id','in',employee_leave_ids),('leave_type_id','=',leave_type_ids[0])])
                                                if employee_leave_detail_ids:
                                                    sql = '''
                                                        update employee_leave_detail set total_day = total_day+%s where id = %s
                                                    '''%(c_off_day,employee_leave_detail_ids[0])
                                                    cr.execute(sql)
                                                else:
                                                    employee_leave_detail_obj.create(cr, uid, {
                                                                                               'leave_type_id': leave_type_ids[0],
                                                                                               'emp_leave_id': employee_leave_ids[0],
                                                                                               'total_day': c_off_day,
                                                                                               })
                                            else:
                                                employee_leave_obj.create(cr, uid, {
                                                                                           'employee_id': employee_ids[0],
                                                                                           'year': data1[7:11],
                                                                                           'emp_leave_details_ids': [(0,0,{
                                                                                                                       'leave_type_id': leave_type_ids[0],
                                                                                                                       'total_day': c_off_day,
                                                                                                                           })],
                                                                                           })
                                                    
                                            val1['actual_work_shift_id']=shift_id
                                            details_ids=detail_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
                                            if details_ids:
                                                val4={'punch_in_out_id':details_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':shift_id,'employee_id':employee_ids[0],'work_date':date,'in_time':in_time,'out_time':out_time,'approval':1}
                                                if date_2!=date:
                                                    val4.update({'diff_day':True})
                                                    val1.update({'diff_day':True})
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
                                            if date_2!=date:
                                                val1.update({'diff_day':True})
                                            val1['actual_work_shift_id']=work_shift_ids[0]
                                            val1['approval']=False  
                                            val1['employee_category_id'] = employee.employee_category_id.id
                                            val1['type']='punch'
                                            detail_obj2.create(cr, uid,val1)
#                                         if work_shift_ids and shift_id and shift_id == work_shift_ids[0]:
#                                             val1['actual_work_shift_id']=shift_id
#                                             details_ids=detail_obj.search(cr, uid, [('employee_id','=',employee_ids[0])])
#                                             if details_ids:
#                                                 val4={'punch_in_out_id':details_ids[0],'planned_work_shift_id':shift_id,'actual_work_shift_id':shift_id,'employee_id':employee_ids[0],'work_date':date,'in_time':in_time,'out_time':out_time,'approval':1}
#                                                 detail_obj4.create(cr, uid, val4)
#                                             else:
#                                                 employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids[0])
#                                                 detail_obj.create(cr, uid, {'employee_id':employee_ids[0],
#                                                                             'employee_category_id':employee.employee_category_id and employee.employee_category_id.id or False,
#                                                                             'sub_category_id':employee.employee_sub_category_id and employee.employee_sub_category_id.id or False,
#                                                                             'department_id':employee.department_id and employee.department_id.id or False,
#                                                                             'designation_id':employee.job_id and employee.job_id.id or False,
#                                                                             'punch_in_out_line':[(0,0,val1)]})
                                    else:
                                        if date_2!=date:
                                            val1.update({'diff_day':True})
                                        val1['approval']=False  
                                        val1['employee_category_id'] = employee.employee_category_id.id
                                        val1['type']='punch'
                                        detail_obj2.create(cr, uid,val1)
                                    temp +=1
                                    test =  L.pop(i+j+1)
                                    break
                            if temp==0:
                                val={'employee_id':employee_ids[0],
                                     'planned_work_shift_id':shift_id,
                                     'work_date':date,
                                     'punch_in_date':date,
                                     'in_time':in_time,
                                     'out_time':0,
                                     'employee_category_id':employee.employee_category_id.id,
                                     'type':'shift',}
                                detail_obj2.create(cr, uid,val)
#                             else:
#                                 detail_obj2.create(cr, uid,{
#                                     'employee_id': employee_ids[0],
#                                     'planned_work_shift_id':shift_id,
#                                     'work_date':date,
#                                     'in_time':in_time,
#                                     'employee_category_id':employee.employee_category_id.id,
#                                     'type':'shift',
#                                 })
                        if data1[:3]=='P20':
                            out_date = data1[7:11]+'-'+data1[11:13]+'-'+data1[13:15]
                            out_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            audit_shift_ids = detail_obj2.search(cr, uid, [('type','=','shift'),('employee_id','=', employee_ids[0]),('state','=','draft')],order='id desc')
                            
                            if audit_shift_ids :
                                audit_shift = detail_obj2.browse(cr,uid,audit_shift_ids[0])
				# TPT Changes - BalamuruganPurushothaman on 18/02/2015 - SQL Query is modified to check Grace Time for shift
                                sql = '''
                                      	select id from arul_hr_capture_work_shift where 
					(%s between 
					case when min_start_time>0.00 then (start_time-(start_time-min_start_time)) else start_time end
					and 
					case when max_start_time>0.00 then (start_time+(max_start_time-start_time)) else start_time end
					)
					and
					(%s between
					case when min_end_time>0.00 then (end_time-(end_time-min_end_time)) else end_time end
					and 
					case when max_end_time>0.00 then (end_time+(max_end_time-end_time)) else end_time end
					)
                                        '''%(audit_shift.in_time,out_time)
                                cr.execute(sql)
                                audit_work_shift_ids = [row[0] for row in cr.fetchall()]
                                if audit_work_shift_ids and shift_id:
                                    if shift_id == audit_work_shift_ids[0]:
                                        
                                        extra_hours = 0.0
                                        c_off_day = 0.0
                                        shift = shift_obj.browse(cr, uid, shift_id)
                                        extra_hours = out_time - shift.end_time
                                        if extra_hours >= 4 and extra_hours < 8:
                                            c_off_day = 0.5
                                        if extra_hours >= 8 and extra_hours < 12:
                                            c_off_day = 1
                                        if extra_hours >= 12 and extra_hours < 16:
                                            c_off_day = 1.5
                                        if extra_hours >= 16:
                                            c_off_day = 2
                                        employee_leave_ids = employee_leave_obj.search(cr, uid, [('year','=',audit_shift.work_date[:4]),('employee_id','=',audit_shift.employee_id.id)])
                                        leave_type_ids = leave_type_obj.search(cr, uid, [('code','=','C.Off')])
                                        if not leave_type_ids:
                                            raise osv.except_osv(_('Warning!'),_('Can not find Leave Type C.Off. Please Create Leave Type C.Off before'))
                                        if employee_leave_ids:
                                            employee_leave_detail_ids = employee_leave_detail_obj.search(cr, uid, [('emp_leave_id','in',employee_leave_ids),('leave_type_id','=',leave_type_ids[0])])
                                            if employee_leave_detail_ids:
                                                sql = '''
                                                    update employee_leave_detail set total_day = total_day+%s where id = %s
                                                '''%(c_off_day,employee_leave_detail_ids[0])
                                                cr.execute(sql)
                                            else:
                                                employee_leave_detail_obj.create(cr, uid, {
                                                                                           'leave_type_id': leave_type_ids[0],
                                                                                           'emp_leave_id': employee_leave_ids[0],
                                                                                           'total_day': c_off_day,
                                                                                           })
                                        else:
                                            employee_leave_obj.create(cr, uid, {
                                                                                       'employee_id': employee_ids[0],
                                                                                       'year': data1[7:11],
                                                                                       'emp_leave_details_ids': [(0,0,{
                                                                                                                   'leave_type_id': leave_type_ids[0],
                                                                                                                   'total_day': c_off_day,
                                                                                                                       })],
                                                                                       })
                                        
                                        if audit_shift.work_date!=date:
                                            detail_obj2.write(cr, uid, [audit_shift.id],{'out_time':out_time,
                                                                                'punch_out_date':out_date,
                                                                                'actual_work_shift_id':shift_id,
                                                                                'diff_day':True})
                                        else:
                                            detail_obj2.write(cr, uid, [audit_shift.id],{'out_time':out_time,'punch_out_date':out_date,
                                                                                'actual_work_shift_id':shift_id,})
                                        detail_obj2.approve_shift_time(cr, uid, [audit_shift.id])
                                    else:
                                        if audit_shift.work_date!=date:
                                            detail_obj2.write(cr, uid, [audit_shift.id],{'type':'punch',
                                                                        'out_time':out_time,'punch_out_date':out_date,
                                                                        'actual_work_shift_id':audit_work_shift_ids[0],
                                                                                'diff_day':True})
                                        else:
                                            detail_obj2.write(cr, uid,[audit_shift.id],{
                                            'type':'punch',
                                            'out_time':out_time,'punch_out_date':out_date,
                                            'actual_work_shift_id':audit_work_shift_ids[0],
                                    })
                                    
#                                 if audit_work_shift_ids and shift_id and shift_id == audit_work_shift_ids[0]:
#                                     detail_obj2.write(cr, uid, [audit_shift.id],{'out_time':out_time,
#                                                                                  'actual_work_shift_id':shift_id,})
#                                     detail_obj2.approve_shift_time(cr, uid, [audit_shift.id])
                                else:
                                    if audit_shift.work_date!=date:
                                        detail_obj2.write(cr, uid, [audit_shift.id],{'out_time':out_time,
                                                                                    'type':'punch','punch_out_date':out_date,
                                                                                    'diff_day':True})
                                    else:
                                        detail_obj2.write(cr, uid,[audit_shift.id],{
                                                                                'out_time':out_time,'punch_out_date':out_date,
                                                                                'type':'punch',
                                                                                })
                                 
                            else :
                                val2={'type':'punch','employee_id':employee_ids[0],'planned_work_shift_id':shift_id,'work_date':date,'punch_in_date':date,'punch_out_date':out_date,'in_time':0,'out_time':out_time,'employee_category_id':employee.employee_category_id.id}
                                detail_obj2.create(cr, uid,val2)
                            
                self.write(cr, uid, [line.id], {'state':'done'})
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))

    def _check_db_datas(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            punch_in_out_ids = self.search(cr, uid, [('id','!=',line.id),('db_datas','=',line.db_datas)])
            name_file_ids = self.search(cr, uid, [('id','!=',line.id),('datas_fname','=',line.datas_fname)])
            if punch_in_out_ids or name_file_ids:
                raise osv.except_osv(_('Warning!'),_('The file to import already existed!'))
                return False
        return True
    _constraints = [
        (_check_db_datas, 'Identical Data', ['db_datas']),
    ]
    
arul_hr_punch_in_out()

class arul_hr_monthly_work_schedule(osv.osv):
    _name='arul.hr.monthly.work.schedule'
    
    _columns={
              'department_id':fields.many2one('hr.department','Department', required = True, states={'done': [('readonly', True)]}),
              'section_id': fields.many2one('arul.hr.section','Section', required = True, states={'done': [('readonly', True)]}),
              'year': fields.selection([(num, str(num)) for num in range(1950, 2026)], 'Year', required = True, states={'done': [('readonly', True)]}),
              'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True, states={'done': [('readonly', True)]}),
              'monthly_shift_line': fields.one2many('arul.hr.monthly.shift.schedule','monthly_work_id', 'Monthly Work Schedule', states={'done': [('readonly', True)]}),
              'create_date': fields.datetime('Created Date',readonly = True),
              'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
              'state':fields.selection([('draft', 'Draft'),('load', 'Load'),('done', 'Done')],'Status', readonly=True),
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
                                           'year': line.year,
                                           'month': line.month,
                                           'num_of_month': calendar.monthrange(int(line.year),int(line.month))[1],
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
        for line in self.browse(cr, uid, ids):           
            #TPT
            monthly_shift_schedule_obj = self.pool.get('arul.hr.monthly.shift.schedule')           
            sql = '''
            select count(id) from arul_hr_monthly_shift_schedule where monthly_work_id='%s' and day_28 is null'''%(line.id)
            cr.execute(sql)
            p = cr.fetchone()            
            if p[0]>0:
                 raise osv.except_osv(_('Warning!'),_('Shift needs to be assigned to all the employees before Approving Work Schedule'))     
            #TPT
            if line.department_id and line.department_id.primary_auditor_id and line.department_id.primary_auditor_id.id==uid \
            or line.department_id and line.department_id.secondary_auditor_id and line.department_id.secondary_auditor_id.id==uid:
                self.write(cr, uid, ids, {'state':'done'})
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
            
        return self.write(cr, uid, ids, {'state':'done'})
    
    def shift_schedule(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_arul_hr_monthly_shift_schedule_form_vew')])
        resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
        work = self.browse(cr, uid, ids[0])
        num_of_month = calendar.monthrange(int(work.year),int(work.month))[1]
        for num in range(1,num_of_month+1):
            if num == 1:
                date = datetime.date (int(work.year), int(work.month), 1)
                context.update({'default_name_of_day_1': date.strftime("%A")})
            if num == 2:
                date = datetime.date (int(work.year), int(work.month), 2)
                context.update({'default_name_of_day_2': date.strftime("%A")})
            if num == 3:
                date = datetime.date (int(work.year), int(work.month), 3)
                context.update({'default_name_of_day_3': date.strftime("%A")})
            if num == 4:
                date = datetime.date (int(work.year), int(work.month), 4)
                context.update({'default_name_of_day_4': date.strftime("%A")})
            if num == 5:
                date = datetime.date (int(work.year), int(work.month), 5)
                context.update({'default_name_of_day_5': date.strftime("%A")})
            if num == 6:
                date = datetime.date (int(work.year), int(work.month), 6)
                context.update({'default_name_of_day_6': date.strftime("%A")})
            if num == 7:
                date = datetime.date (int(work.year), int(work.month), 7)
                context.update({'default_name_of_day_7': date.strftime("%A")})
            if num == 8:
                date = datetime.date (int(work.year), int(work.month), 8)
                context.update({'default_name_of_day_8': date.strftime("%A")})
            if num == 9:
                date = datetime.date (int(work.year), int(work.month), 9)
                context.update({'default_name_of_day_9': date.strftime("%A")})
            if num == 10:
                date = datetime.date (int(work.year), int(work.month), 10)
                context.update({'default_name_of_day_10': date.strftime("%A")})
            if num == 11:
                date = datetime.date (int(work.year), int(work.month), 11)
                context.update({'default_name_of_day_11': date.strftime("%A")})
            if num == 12:
                date = datetime.date (int(work.year), int(work.month), 12)
                context.update({'default_name_of_day_12': date.strftime("%A")})
            if num == 13:
                date = datetime.date (int(work.year), int(work.month), 13)
                context.update({'default_name_of_day_13': date.strftime("%A")})
            if num == 14:
                date = datetime.date (int(work.year), int(work.month), 14)
                context.update({'default_name_of_day_14': date.strftime("%A")})
            if num == 15:
                date = datetime.date (int(work.year), int(work.month), 15)
                context.update({'default_name_of_day_15': date.strftime("%A")})
            if num == 16:
                date = datetime.date (int(work.year), int(work.month), 16)
                context.update({'default_name_of_day_16': date.strftime("%A")})
            if num == 17:
                date = datetime.date (int(work.year), int(work.month), 17)
                context.update({'default_name_of_day_17': date.strftime("%A")})
            if num == 18:
                date = datetime.date (int(work.year), int(work.month), 18)
                context.update({'default_name_of_day_18': date.strftime("%A")})
            if num == 19:
                date = datetime.date (int(work.year), int(work.month), 19)
                context.update({'default_name_of_day_19': date.strftime("%A")})
            if num == 20:
                date = datetime.date (int(work.year), int(work.month), 20)
                context.update({'default_name_of_day_20': date.strftime("%A")})
            if num == 21:
                date = datetime.date (int(work.year), int(work.month), 21)
                context.update({'default_name_of_day_21': date.strftime("%A")})
            if num == 22:
                date = datetime.date (int(work.year), int(work.month), 22)
                context.update({'default_name_of_day_22': date.strftime("%A")})
            if num == 23:
                date = datetime.date (int(work.year), int(work.month), 23)
                context.update({'default_name_of_day_23': date.strftime("%A")})
            if num == 24:
                date = datetime.date (int(work.year), int(work.month), 24)
                context.update({'default_name_of_day_24': date.strftime("%A")})
            if num == 25:
                date = datetime.date (int(work.year), int(work.month), 25)
                context.update({'default_name_of_day_25': date.strftime("%A")})
            if num == 26:
                date = datetime.date (int(work.year), int(work.month), 26)
                context.update({'default_name_of_day_26': date.strftime("%A")})
            if num == 27:
                date = datetime.date (int(work.year), int(work.month), 27)
                context.update({'default_name_of_day_27': date.strftime("%A")})
            if num == 28:
                date = datetime.date (int(work.year), int(work.month), 28)
                context.update({'default_name_of_day_28': date.strftime("%A")})
            if num == 29:
                date = datetime.date (int(work.year), int(work.month), 29)
                context.update({'default_name_of_day_29': date.strftime("%A")})
            if num == 30:
                date = datetime.date (int(work.year), int(work.month), 30)
                context.update({'default_name_of_day_30': date.strftime("%A")})
            if num == 31:
                date = datetime.date (int(work.year), int(work.month), 31)
                context.update({'default_name_of_day_31': date.strftime("%A")})
        context.update({'default_year':work.year,'default_month':work.month,'default_num_of_month':num_of_month,'department_id':work.department_id.id,'section_id':work.section_id.id,'default_monthly_work':work.id})
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
            employee_ids = employee_obj.search(cr, uid, [('active','=',True ),('department_id','=',department_id ),('section_id','=',section_id )])
            name_of_day_1 = False
            name_of_day_2 = False
            name_of_day_3 = False
            name_of_day_4 = False
            name_of_day_5 = False
            name_of_day_6 = False
            name_of_day_7 = False
            name_of_day_8 = False
            name_of_day_9 = False
            name_of_day_10 = False
            name_of_day_11 = False
            name_of_day_12 = False
            name_of_day_13 = False
            name_of_day_14 = False
            name_of_day_15 = False
            name_of_day_16 = False
            name_of_day_17 = False
            name_of_day_18 = False
            name_of_day_19 = False
            name_of_day_20 = False
            name_of_day_21 = False
            name_of_day_22 = False
            name_of_day_23 = False
            name_of_day_24 = False
            name_of_day_25 = False
            name_of_day_26 = False
            name_of_day_27 = False
            name_of_day_28 = False
            name_of_day_29 = False
            name_of_day_30 = False
            name_of_day_31 = False
            for num in range(1,num_of_month+1):
                if num == 1:
                    date = datetime.date (year, int(month), 1)
                    name_of_day_1 = date.strftime("%A")
                if num == 2:
                    date = datetime.date (year, int(month), 2)
                    name_of_day_2 = date.strftime("%A")
                if num == 3:
                    date = datetime.date (year, int(month), 3)
                    name_of_day_3 = date.strftime("%A")
                if num == 4:
                    date = datetime.date (year, int(month), 4)
                    name_of_day_4 = date.strftime("%A")
                if num == 5:
                    date = datetime.date (year, int(month), 5)
                    name_of_day_5 = date.strftime("%A")
                if num == 6:
                    date = datetime.date (year, int(month), 6)
                    name_of_day_6 = date.strftime("%A")
                if num == 7:
                    date = datetime.date (year, int(month), 7)
                    name_of_day_7 = date.strftime("%A")
                if num == 8:
                    date = datetime.date (year, int(month), 8)
                    name_of_day_8 = date.strftime("%A")
                if num == 9:
                    date = datetime.date (year, int(month), 9)
                    name_of_day_9 = date.strftime("%A")
                if num == 10:
                    date = datetime.date (year, int(month), 10)
                    name_of_day_10 = date.strftime("%A")
                if num == 11:
                    date = datetime.date (year, int(month), 11)
                    name_of_day_11 = date.strftime("%A")
                if num == 12:
                    date = datetime.date (year, int(month), 12)
                    name_of_day_12 = date.strftime("%A")
                if num == 13:
                    date = datetime.date (year, int(month), 13)
                    name_of_day_13 = date.strftime("%A")
                if num == 14:
                    date = datetime.date (year, int(month), 14)
                    name_of_day_14 = date.strftime("%A")
                if num == 15:
                    date = datetime.date (year, int(month), 15)
                    name_of_day_15 = date.strftime("%A")
                if num == 16:
                    date = datetime.date (year, int(month), 16)
                    name_of_day_16 = date.strftime("%A")
                if num == 17:
                    date = datetime.date (year, int(month), 17)
                    name_of_day_17 = date.strftime("%A")
                if num == 18:
                    date = datetime.date (year, int(month), 18)
                    name_of_day_18 = date.strftime("%A")
                if num == 19:
                    date = datetime.date (year, int(month), 19)
                    name_of_day_19 = date.strftime("%A")
                if num == 20:
                    date = datetime.date (year, int(month), 20)
                    name_of_day_20 = date.strftime("%A")
                if num == 21:
                    date = datetime.date (year, int(month), 21)
                    name_of_day_21 = date.strftime("%A")
                if num == 22:
                    date = datetime.date (year, int(month), 22)
                    name_of_day_22 = date.strftime("%A")
                if num == 23:
                    date = datetime.date (year, int(month), 23)
                    name_of_day_23 = date.strftime("%A")
                if num == 24:
                    date = datetime.date (year, int(month), 24)
                    name_of_day_24 = date.strftime("%A")
                if num == 25:
                    date = datetime.date (year, int(month), 25)
                    name_of_day_25 = date.strftime("%A")
                if num == 26:
                    date = datetime.date (year, int(month), 26)
                    name_of_day_26 = date.strftime("%A")
                if num == 27:
                    date = datetime.date (year, int(month), 27)
                    name_of_day_27 = date.strftime("%A")
                if num == 28:
                    date = datetime.date (year, int(month), 28)
                    name_of_day_28 = date.strftime("%A")
                if num == 29:
                    date = datetime.date (year, int(month), 29)
                    name_of_day_29 = date.strftime("%A")
                if num == 30:
                    date = datetime.date (year, int(month), 30)
                    name_of_day_30 = date.strftime("%A")
                if num == 31:
                    date = datetime.date (year, int(month), 31)
                    name_of_day_31 = date.strftime("%A")
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id,
                      'num_of_month': num_of_month,
                      'month':month,
                      'year': year,
                      'name_of_day_1': name_of_day_1,
                      'name_of_day_2': name_of_day_2,
                      'name_of_day_3': name_of_day_3,
                      'name_of_day_4': name_of_day_4,
                      'name_of_day_5': name_of_day_5,
                      'name_of_day_6': name_of_day_6,
                      'name_of_day_7': name_of_day_7,
                      'name_of_day_8': name_of_day_8,
                      'name_of_day_9': name_of_day_9,
                      'name_of_day_10': name_of_day_10,
                      'name_of_day_11': name_of_day_11,
                      'name_of_day_12': name_of_day_12,
                      'name_of_day_13': name_of_day_13,
                      'name_of_day_14': name_of_day_14,
                      'name_of_day_15': name_of_day_15,
                      'name_of_day_16': name_of_day_16,
                      'name_of_day_17': name_of_day_17,
                      'name_of_day_18': name_of_day_18,
                      'name_of_day_19': name_of_day_19,
                      'name_of_day_20': name_of_day_20,
                      'name_of_day_21': name_of_day_21,
                      'name_of_day_22': name_of_day_22,
                      'name_of_day_23': name_of_day_23,
                      'name_of_day_24': name_of_day_24,
                      'name_of_day_25': name_of_day_25,
                      'name_of_day_26': name_of_day_26,
                      'name_of_day_27': name_of_day_27,
                      'name_of_day_28': name_of_day_28,
                      'name_of_day_29': name_of_day_29,
                      'name_of_day_30': name_of_day_30,
                      'name_of_day_31': name_of_day_31,
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
            employee_ids = employee_obj.search(cr, uid, [('active','=',True ),('department_id','=',department_id ),('section_id','=',section_id )])
            name_of_day_1 = False
            name_of_day_2 = False
            name_of_day_3 = False
            name_of_day_4 = False
            name_of_day_5 = False
            name_of_day_6 = False
            name_of_day_7 = False
            name_of_day_8 = False
            name_of_day_9 = False
            name_of_day_10 = False
            name_of_day_11 = False
            name_of_day_12 = False
            name_of_day_13 = False
            name_of_day_14 = False
            name_of_day_15 = False
            name_of_day_16 = False
            name_of_day_17 = False
            name_of_day_18 = False
            name_of_day_19 = False
            name_of_day_20 = False
            name_of_day_21 = False
            name_of_day_22 = False
            name_of_day_23 = False
            name_of_day_24 = False
            name_of_day_25 = False
            name_of_day_26 = False
            name_of_day_27 = False
            name_of_day_28 = False
            name_of_day_29 = False
            name_of_day_30 = False
            name_of_day_31 = False
            for num in range(1,num_of_month+1):
                if num == 1:
                    date = datetime.date (year, int(month), 1)
                    name_of_day_1 = date.strftime("%A")
                if num == 2:
                    date = datetime.date (year, int(month), 2)
                    name_of_day_2 = date.strftime("%A")
                if num == 3:
                    date = datetime.date (year, int(month), 3)
                    name_of_day_3 = date.strftime("%A")
                if num == 4:
                    date = datetime.date (year, int(month), 4)
                    name_of_day_4 = date.strftime("%A")
                if num == 5:
                    date = datetime.date (year, int(month), 5)
                    name_of_day_5 = date.strftime("%A")
                if num == 6:
                    date = datetime.date (year, int(month), 6)
                    name_of_day_6 = date.strftime("%A")
                if num == 7:
                    date = datetime.date (year, int(month), 7)
                    name_of_day_7 = date.strftime("%A")
                if num == 8:
                    date = datetime.date (year, int(month), 8)
                    name_of_day_8 = date.strftime("%A")
                if num == 9:
                    date = datetime.date (year, int(month), 9)
                    name_of_day_9 = date.strftime("%A")
                if num == 10:
                    date = datetime.date (year, int(month), 10)
                    name_of_day_10 = date.strftime("%A")
                if num == 11:
                    date = datetime.date (year, int(month), 11)
                    name_of_day_11 = date.strftime("%A")
                if num == 12:
                    date = datetime.date (year, int(month), 12)
                    name_of_day_12 = date.strftime("%A")
                if num == 13:
                    date = datetime.date (year, int(month), 13)
                    name_of_day_13 = date.strftime("%A")
                if num == 14:
                    date = datetime.date (year, int(month), 14)
                    name_of_day_14 = date.strftime("%A")
                if num == 15:
                    date = datetime.date (year, int(month), 15)
                    name_of_day_15 = date.strftime("%A")
                if num == 16:
                    date = datetime.date (year, int(month), 16)
                    name_of_day_16 = date.strftime("%A")
                if num == 17:
                    date = datetime.date (year, int(month), 17)
                    name_of_day_17 = date.strftime("%A")
                if num == 18:
                    date = datetime.date (year, int(month), 18)
                    name_of_day_18 = date.strftime("%A")
                if num == 19:
                    date = datetime.date (year, int(month), 19)
                    name_of_day_19 = date.strftime("%A")
                if num == 20:
                    date = datetime.date (year, int(month), 20)
                    name_of_day_20 = date.strftime("%A")
                if num == 21:
                    date = datetime.date (year, int(month), 21)
                    name_of_day_21 = date.strftime("%A")
                if num == 22:
                    date = datetime.date (year, int(month), 22)
                    name_of_day_22 = date.strftime("%A")
                if num == 23:
                    date = datetime.date (year, int(month), 23)
                    name_of_day_23 = date.strftime("%A")
                if num == 24:
                    date = datetime.date (year, int(month), 24)
                    name_of_day_24 = date.strftime("%A")
                if num == 25:
                    date = datetime.date (year, int(month), 25)
                    name_of_day_25 = date.strftime("%A")
                if num == 26:
                    date = datetime.date (year, int(month), 26)
                    name_of_day_26 = date.strftime("%A")
                if num == 27:
                    date = datetime.date (year, int(month), 27)
                    name_of_day_27 = date.strftime("%A")
                if num == 28:
                    date = datetime.date (year, int(month), 28)
                    name_of_day_28 = date.strftime("%A")
                if num == 29:
                    date = datetime.date (year, int(month), 29)
                    name_of_day_29 = date.strftime("%A")
                if num == 30:
                    date = datetime.date (year, int(month), 30)
                    name_of_day_30 = date.strftime("%A")
                if num == 31:
                    date = datetime.date (year, int(month), 31)
                    name_of_day_31 = date.strftime("%A")
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id,
                      'num_of_month': num_of_month,
                      'month':month,
                      'year': year,
                      'name_of_day_1': name_of_day_1,
                        'name_of_day_2': name_of_day_2,
                        'name_of_day_3': name_of_day_3,
                        'name_of_day_4': name_of_day_4,
                        'name_of_day_5': name_of_day_5,
                        'name_of_day_6': name_of_day_6,
                        'name_of_day_7': name_of_day_7,
                        'name_of_day_8': name_of_day_8,
                        'name_of_day_9': name_of_day_9,
                        'name_of_day_10': name_of_day_10,
                        'name_of_day_11': name_of_day_11,
                      'name_of_day_12': name_of_day_12,
                      'name_of_day_13': name_of_day_13,
                      'name_of_day_14': name_of_day_14,
                      'name_of_day_15': name_of_day_15,
                      'name_of_day_16': name_of_day_16,
                      'name_of_day_17': name_of_day_17,
                      'name_of_day_18': name_of_day_18,
                      'name_of_day_19': name_of_day_19,
                      'name_of_day_20': name_of_day_20,
                      'name_of_day_21': name_of_day_21,
                      'name_of_day_22': name_of_day_22,
                      'name_of_day_23': name_of_day_23,
                      'name_of_day_24': name_of_day_24,
                      'name_of_day_25': name_of_day_25,
                      'name_of_day_26': name_of_day_26,
                      'name_of_day_27': name_of_day_27,
                      'name_of_day_28': name_of_day_28,
                      'name_of_day_29': name_of_day_29,
                      'name_of_day_30': name_of_day_30,
                      'name_of_day_31': name_of_day_31,
                      }
                employee_lines.append((0,0,rs))
        return {'value': {'monthly_shift_line':employee_lines}}
        
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_for_monthly_work_sche_pri_auditor'):
            primary_auditor_ids = self.pool.get('hr.department').search(cr, uid, [('primary_auditor_id','=',uid)])
            if primary_auditor_ids:
                sql = '''
                    select id from arul_hr_monthly_work_schedule where
                        department_id in (select id from hr_department where primary_auditor_id =%s)
                '''%(uid)
                cr.execute(sql)
                leave_details_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',leave_details_ids)]
        return super(arul_hr_monthly_work_schedule, self).search(cr, uid, args, offset, limit, order, context, count)
        
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
    
    def _get_name_of_day(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            name_of_day_1 = False
            name_of_day_2 = False
            name_of_day_3 = False
            name_of_day_4 = False
            name_of_day_5 = False
            name_of_day_6 = False
            name_of_day_7 = False
            name_of_day_8 = False
            name_of_day_9 = False
            name_of_day_10 = False
            name_of_day_11 = False
            name_of_day_12 = False
            name_of_day_13 = False
            name_of_day_14 = False
            name_of_day_15 = False
            name_of_day_16 = False
            name_of_day_17 = False
            name_of_day_18 = False
            name_of_day_19 = False
            name_of_day_20 = False
            name_of_day_21 = False
            name_of_day_22 = False
            name_of_day_23 = False
            name_of_day_24 = False
            name_of_day_25 = False
            name_of_day_26 = False
            name_of_day_27 = False
            name_of_day_28 = False
            name_of_day_29 = False
            name_of_day_30 = False
            name_of_day_31 = False
            for num in range(1,line.num_of_month+1):
                if num == 1:
                    date = datetime.date (line.year, int(line.month), 1)
                    name_of_day_1 = date.strftime("%A")
                if num == 2:
                    date = datetime.date (line.year, int(line.month), 2)
                    name_of_day_2 = date.strftime("%A")
                if num == 3:
                    date = datetime.date (line.year, int(line.month), 3)
                    name_of_day_3 = date.strftime("%A")
                if num == 4:
                    date = datetime.date (line.year, int(line.month), 4)
                    name_of_day_4 = date.strftime("%A")
                if num == 5:
                    date = datetime.date (line.year, int(line.month), 5)
                    name_of_day_5 = date.strftime("%A")
                if num == 6:
                    date = datetime.date (line.year, int(line.month), 6)
                    name_of_day_6 = date.strftime("%A")
                if num == 7:
                    date = datetime.date (line.year, int(line.month), 7)
                    name_of_day_7 = date.strftime("%A")
                if num == 8:
                    date = datetime.date (line.year, int(line.month), 8)
                    name_of_day_8 = date.strftime("%A")
                if num == 9:
                    date = datetime.date (line.year, int(line.month), 9)
                    name_of_day_9 = date.strftime("%A")
                if num == 10:
                    date = datetime.date (line.year, int(line.month), 10)
                    name_of_day_10 = date.strftime("%A")
                if num == 11:
                    date = datetime.date (line.year, int(line.month), 11)
                    name_of_day_11 = date.strftime("%A")
                if num == 12:
                    date = datetime.date (line.year, int(line.month), 12)
                    name_of_day_12 = date.strftime("%A")
                if num == 13:
                    date = datetime.date (line.year, int(line.month), 13)
                    name_of_day_13 = date.strftime("%A")
                if num == 14:
                    date = datetime.date (line.year, int(line.month), 14)
                    name_of_day_14 = date.strftime("%A")
                if num == 15:
                    date = datetime.date (line.year, int(line.month), 15)
                    name_of_day_15 = date.strftime("%A")
                if num == 16:
                    date = datetime.date (line.year, int(line.month), 16)
                    name_of_day_16 = date.strftime("%A")
                if num == 17:
                    date = datetime.date (line.year, int(line.month), 17)
                    name_of_day_17 = date.strftime("%A")
                if num == 18:
                    date = datetime.date (line.year, int(line.month), 18)
                    name_of_day_18 = date.strftime("%A")
                if num == 19:
                    date = datetime.date (line.year, int(line.month), 19)
                    name_of_day_19 = date.strftime("%A")
                if num == 20:
                    date = datetime.date (line.year, int(line.month), 20)
                    name_of_day_20 = date.strftime("%A")
                if num == 21:
                    date = datetime.date (line.year, int(line.month), 21)
                    name_of_day_21 = date.strftime("%A")
                if num == 22:
                    date = datetime.date (line.year, int(line.month), 22)
                    name_of_day_22 = date.strftime("%A")
                if num == 23:
                    date = datetime.date (line.year, int(line.month), 23)
                    name_of_day_23 = date.strftime("%A")
                if num == 24:
                    date = datetime.date (line.year, int(line.month), 24)
                    name_of_day_24 = date.strftime("%A")
                if num == 25:
                    date = datetime.date (line.year, int(line.month), 25)
                    name_of_day_25 = date.strftime("%A")
                if num == 26:
                    date = datetime.date (line.year, int(line.month), 26)
                    name_of_day_26 = date.strftime("%A")
                if num == 27:
                    date = datetime.date (line.year, int(line.month), 27)
                    name_of_day_27 = date.strftime("%A")
                if num == 28:
                    date = datetime.date (line.year, int(line.month), 28)
                    name_of_day_28 = date.strftime("%A")
                if num == 29:
                    date = datetime.date (line.year, int(line.month), 29)
                    name_of_day_29 = date.strftime("%A")
                if num == 30:
                    date = datetime.date (line.year, int(line.month), 30)
                    name_of_day_30 = date.strftime("%A")
                if num == 31:
                    date = datetime.date (line.year, int(line.month), 31)
                    name_of_day_31 = date.strftime("%A")
            res[line.id] = {
                'name_of_day_1': name_of_day_1,
                'name_of_day_2': name_of_day_2,
                'name_of_day_3': name_of_day_3,
                'name_of_day_4': name_of_day_4,
                'name_of_day_5': name_of_day_5,
                'name_of_day_6': name_of_day_6,
                'name_of_day_7': name_of_day_7,
                'name_of_day_8': name_of_day_8,
                'name_of_day_9': name_of_day_9,
                'name_of_day_10': name_of_day_10,
                'name_of_day_11': name_of_day_11,
                'name_of_day_12': name_of_day_12,
                'name_of_day_13': name_of_day_13,
                'name_of_day_14': name_of_day_14,
                'name_of_day_15': name_of_day_15,
                'name_of_day_16': name_of_day_16,
                'name_of_day_17': name_of_day_17,
                'name_of_day_18': name_of_day_18,
                'name_of_day_19': name_of_day_19,
                'name_of_day_20': name_of_day_20,
                'name_of_day_21': name_of_day_21,
                'name_of_day_22': name_of_day_22,
                'name_of_day_23': name_of_day_23,
                'name_of_day_24': name_of_day_24,
                'name_of_day_25': name_of_day_25,
                'name_of_day_26': name_of_day_26,
                'name_of_day_27': name_of_day_27,
                'name_of_day_28': name_of_day_28,
                'name_of_day_29': name_of_day_29,
                'name_of_day_30': name_of_day_30,
                'name_of_day_31': name_of_day_31,
            }
        return res
    _columns={
#               'num_of_month': fields.function(_num_of_month, string='Day',store=True, multi='sums', help="The total amount."),
              'num_of_month': fields.integer('Day'),
              'name_of_day_1': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_2': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_3': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_4': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_5': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_6': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_7': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_8': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_9': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_10': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_11': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_12': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_13': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_14': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_15': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_16': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_17': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_18': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_19': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_20': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_21': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_22': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_23': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_24': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_25': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_26': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_27': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_28': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_29': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_30': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'name_of_day_31': fields.function(_get_name_of_day,string='Name Of Day', type='char',multi='days'),
              'year': fields.selection([(num, str(num)) for num in range(1950, 2026)], 'Year'),
              'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month'),
              'monthly_work': fields.integer('monthly work'),
              'shift_day_from': fields.many2one('tpt.month','Shift Day From'),
              'shift_day_to': fields.many2one('tpt.month','Shift Day To'),
              'work_shift_id': fields.many2one('arul.hr.capture.work.shift','Work Shift'),
              'shift_group_id': fields.many2one('shift.group','Shift Group'),
              'employee_id':fields.many2one('hr.employee','Employee', required = True),
              'monthly_work_id':fields.many2one('arul.hr.monthly.work.schedule','Monthly Shift Schedule'),
              'day_1': fields.many2one('arul.hr.capture.work.shift','1',required = True),
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
            if shift_schedule_ids:
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
            else:
                self.write(cr, uid, [shift_schedule.id],{
                  'monthly_work_id': active_id,
                })
            sql = '''
                delete from arul_hr_monthly_shift_schedule where monthly_work_id is null
            '''
            cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}
    
    def onchange_employee_id(self, cr, uid, ids, employee_id = False,monthly_work=False, context=None):
        value = {}
        if employee_id and monthly_work:
            shift_schedule_ids = self.search(cr, uid, [('monthly_work_id','=',monthly_work),('employee_id','=',employee_id)])
            if shift_schedule_ids:
                shift_schedule = self.browse(cr, uid, shift_schedule_ids[0])
                value = {
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
                    }
        return {'value': value}
    
    def onchange_monthly(self, cr, uid, ids, num_of_month = False, shift_day_from=False,shift_day_to=False, work_shift_id = False,shift_group_id=False,month=False,year=False, context=None):
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
        if shift_day_from and shift_day_to and shift_group_id and month and year:
            shift_group = self.pool.get('shift.group').browse(cr, uid, shift_group_id)
            month = int(month)
            shift_day_f = self.pool.get('tpt.month').browse(cr, uid, shift_day_from)
            shift_day_t = self.pool.get('tpt.month').browse(cr, uid, shift_day_to)
            if shift_day_f.name > shift_day_t.name:
                raise osv.except_osv(_('Warning!'),_('Shift Day Form must less than Shift Day To'))
            if shift_day_t.name > num_of_month:
                raise osv.except_osv(_('Warning!'),_('Range of month is limited'))
            for num in range(shift_day_f.name, shift_day_t.name + 1):
                if num == 1:
                    date = datetime.date (year, month, 1)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_1'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_1'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_1'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_1'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_1'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_1'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_1'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 2:
                    date = datetime.date (year, month, 2)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_2'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_2'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_2'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_2'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_2'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_2'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_2'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 3:
                    date = datetime.date (year, month, 3)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_3'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_3'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_3'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_3'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_3'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_3'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_3'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 4:
                    date = datetime.date (year, month, 4)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_4'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_4'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_4'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_4'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_4'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_4'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_4'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 5:
                    date = datetime.date (year, month, 5)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_5'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_5'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_5'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_5'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_5'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_5'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_5'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 6:
                    date = datetime.date (year, month, 6)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_6'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_6'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_6'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_6'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_6'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_6'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_6'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 7:
                    date = datetime.date (year, month, 7)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_7'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_7'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_7'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_7'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_7'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_7'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_7'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 8:
                    date = datetime.date (year, month, 8)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_8'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_8'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_8'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_8'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_8'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_8'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_8'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 9:
                    date = datetime.date (year, month, 9)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_9'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_9'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_9'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_9'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_9'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_9'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_9'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 10:
                    date = datetime.date (year, month, 10)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_10'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_10'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_10'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_10'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_10'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_10'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_10'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 11:
                    date = datetime.date (year, month, 11)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_11'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_11'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_11'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_11'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_11'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_11'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_11'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 12:
                    date = datetime.date (year, month, 12)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_12'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_12'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_12'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_12'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_12'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_12'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_12'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 13:
                    date = datetime.date (year, month, 13)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_13'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_13'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_13'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_13'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_13'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_13'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_13'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 14:
                    date = datetime.date (year, month, 14)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_14'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_14'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_14'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_14'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_14'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_14'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_14'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 15:
                    date = datetime.date (year, month, 15)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_15'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_15'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_15'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_15'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_15'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_15'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_15'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 16:
                    date = datetime.date (year, month, 16)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_16'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_16'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_16'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_16'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_16'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_16'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_16'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 17:
                    date = datetime.date (year, month, 17)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_17'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_17'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_17'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_17'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_17'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_17'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_17'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 18:
                    date = datetime.date (year, month, 18)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_18'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_18'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_18'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_18'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_18'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_18'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_18'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 19:
                    date = datetime.date (year, month, 19)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_19'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_19'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_19'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_19'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_19'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_19'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_19'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 20:
                    date = datetime.date (year, month, 20)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_20'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_20'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_20'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_20'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_20'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_20'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_20'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 21:
                    date = datetime.date (year, month, 21)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_21'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_21'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_21'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_21'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_21'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_21'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_21'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 22:
                    date = datetime.date (year, month, 22)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_22'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_22'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_22'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_22'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_22'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_22'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_22'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 23:
                    date = datetime.date (year, month, 23)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_23'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_23'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_23'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_23'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_23'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_23'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_23'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 24:
                    date = datetime.date (year, month, 24)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_24'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_24'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_24'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_24'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_24'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_24'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_24'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 25:
                    date = datetime.date (year, month, 25)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_25'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_25'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_25'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_25'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_25'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_25'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_25'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 26:
                    date = datetime.date (year, month, 26)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_26'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_26'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_26'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_26'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_26'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_26'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_26'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 27:
                    date = datetime.date (year, month, 27)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_27'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_27'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_27'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_27'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_27'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_27'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_27'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 28:
                    date = datetime.date (year, month, 28)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_28'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_28'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_28'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_28'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_28'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_28'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_28'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 29:
                    date = datetime.date (year, month, 29)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_29'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_29'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_29'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_29'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_29'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_29'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_29'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 30:
                    date = datetime.date (year, month, 30)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_30'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_30'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_30'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_30'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_30'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_30'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_30'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                if num == 31:
                    date = datetime.date (year, month, 31)
                    name_day = date.strftime("%A")
                    if name_day == 'Sunday':
                        value['day_31'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                    elif name_day == 'Monday':
                        value['day_31'] = shift_group.monday_id and shift_group.monday_id.id or False
                    elif name_day == 'Tuesday':
                        value['day_31'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                    elif name_day == 'Wednesday':
                        value['day_31'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                    elif name_day == 'Thursday':
                        value['day_31'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                    elif name_day == 'Friday':
                        value['day_31'] = shift_group.friday_id and shift_group.friday_id.id or False
                    else:
                        value['day_31'] = shift_group.saturday_id and shift_group.saturday_id.id or False
            value.update({'shift_day_from': False,'shift_day_to': False, 'shift_group_id':False})
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
    def _check(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj:
            time_leave = self.search(cr, uid, [('payroll_area_id','=',obj.payroll_area_id.id),('year','=',obj.year),('month','=',obj.month)])
            if time_leave and len(time_leave) > 1:
                raise osv.except_osv(_('Warning!'),_('This Time Leave Evaluation has already existed!'))
        return True
    _constraints = [
        (_check, _(''), ['payroll_area_id', 'year', 'month']),
    ]
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
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (1.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 1.0 not in audit_days and 1.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),1)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_2 and shift.day_2.code != 'W' and day_now>=2 and 2.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (2.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 2.0 not in audit_days and 2.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),2)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_3 and shift.day_3.code != 'W' and day_now>=3 and 3.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (3.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 3.0 not in audit_days and 3.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),3)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_4 and shift.day_4.code != 'W' and day_now>=4 and 4.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (4.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 4.0 not in audit_days and 4.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),4)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_5 and shift.day_5.code != 'W' and day_now>=5 and 5.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (5.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 5.0 not in audit_days and 5.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),5)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_6 and shift.day_6.code != 'W' and day_now>=6 and 6.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (6.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 6.0 not in audit_days and 6.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),6)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_7 and shift.day_7.code != 'W' and day_now>=7 and 7.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (7.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 7.0 not in audit_days and 7.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),7)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_8 and shift.day_8.code != 'W' and day_now>=8 and 8.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (8.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 8.0 not in audit_days and 8.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),8)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_9 and shift.day_9.code != 'W' and day_now>=9 and 9.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (9.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 9.0 not in audit_days and 9.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),9)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_10 and shift.day_10.code != 'W' and day_now>=10 and 10.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (10.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 10.0 not in audit_days and 10.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),10)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_11 and shift.day_11.code != 'W' and day_now>=11 and 11.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (11.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 11.0 not in audit_days and 11.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),11)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_12 and shift.day_12.code != 'W' and day_now>=12 and 12.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (12.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 12.0 not in audit_days and 12.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),12)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_13 and shift.day_13.code != 'W' and day_now>=13 and 13.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (13.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 13.0 not in audit_days and 13.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),13)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_14 and shift.day_14.code != 'W' and day_now>=14 and 14.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (14.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 14.0 not in audit_days and 14.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),14)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_15 and shift.day_15.code != 'W' and day_now>=15 and 15.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (15.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 15.0 not in audit_days and 15.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),15)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_16 and shift.day_16.code != 'W' and day_now>=16 and 16.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (16.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 16.0 not in audit_days and 16.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),16)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_17 and shift.day_17.code != 'W' and day_now>=17 and 17.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (17.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 17.0 not in audit_days and 17.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),17)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_18 and shift.day_18.code != 'W' and day_now>=18 and 18.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (18.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 18.0 not in audit_days and 18.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),18)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_19 and shift.day_19.code != 'W' and day_now>=19 and 19.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (19.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 19.0 not in audit_days and 19.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),19)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_20 and shift.day_20.code != 'W' and day_now>=20 and 20.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (20.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 20.0 not in audit_days and 20.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),20)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_21 and shift.day_21.code != 'W' and day_now>=21 and 21.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (21.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 21.0 not in audit_days and 21.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),21)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_22 and shift.day_22.code != 'W' and day_now>=22 and 22.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (22.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 22.0 not in audit_days and 22.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),22)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_23 and shift.day_23.code != 'W' and day_now>=23 and 23.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (23.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 23.0 not in audit_days and 23.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),23)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_24 and shift.day_24.code != 'W' and day_now>=24 and 24.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (24.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 24.0 not in audit_days and 24.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),24)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_25 and shift.day_25.code != 'W' and day_now>=25 and 25.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (25.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 25.0 not in audit_days and 25.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),25)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_26 and shift.day_26.code != 'W' and day_now>=26 and 26.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (26.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 26.0 not in audit_days and 26.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),26)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_27 and shift.day_27.code != 'W' and day_now>=27 and 27.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (27.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 27.0 not in audit_days and 27.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),27)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_28 and shift.day_28.code != 'W' and day_now>=28 and 28.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (28.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 28.0 not in audit_days and 28.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),28)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_29 and shift.day_29.code != 'W' and shift.num_of_month>=29 and day_now>=29 and 29.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (29.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 29.0 not in audit_days and 29.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),29)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_30 and shift.day_30.code != 'W' and shift.num_of_month>=30 and day_now>=30 and 30.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (30.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 30.0 not in audit_days and 30.0 not in punch_days and not leave_days:
                            date = datetime.datetime(sub.year,int(sub.month),30)
                            non_availability_obj.create(cr, uid, {'employee_id':emp_id,'state':'draft','date':date,'leave_evaluate_id':sub.id})
                    if shift.day_31 and shift.day_31.code != 'W' and shift.num_of_month>=31 and day_now>=31 and 31.0 not in holiday_days:
                        sql = '''
                            select id from arul_hr_employee_leave_details
                                where employee_id = %s and EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s
                                    and (31.0 between EXTRACT(day FROM date_from) and EXTRACT(day FROM date_to))
                        '''%(emp_id, sub.year, sub.month)
                        cr.execute(sql)
                        leave_days = [row[0] for row in cr.fetchall()]
                        if 31.0 not in audit_days and 31.0 not in punch_days and not leave_days:
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
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_day_for_leave', False):
            if context.get('date_from', False) and context.get('date_to', False):
                date_from = context.get('date_from', False)
                date_to = context.get('date_to', False)
                day_names = []
                if date_from[5:7] == date_to[5:7]:
                    for day in range(int(date_from[8:10]),int(date_to[8:10])+1): 
                        day_names.append(day)
                else:
                    num_of_month = calendar.monthrange(int(date_from[:4]),int(date_from[5:7]))[1]
                    for day in range(int(date_from[8:10]),num_of_month+1): 
                        day_names.append(day)
                    for day in range(1,int(date_to[8:10])+1): 
                        day_names.append(day)
                day_ids = self.search(cr, uid, [('name','in',day_names)])
                args += [('id','in',day_ids)]
            else:
                args = [('id','=',0)]
        return super(tpt_month, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
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
                select id from tpt_equipment_master where id != %s and lower(code) = lower('%s')
            '''%(cost.id,cost.code)
            cr.execute(sql)
            cost_ids = [row[0] for row in cr.fetchall()]
            if cost_ids:  
                raise osv.except_osv(_('Warning!'),_('The Code is unique!'))
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
    
    def onchange_allocated_qty(self, cr, uid, ids, allocated_qty=False, returned_qty=False, context=None):
        vals = {}
        warning = {}
        if allocated_qty and returned_qty:
            if  allocated_qty < returned_qty:
                vals = {'returned_qty':0}
                warning = {
                    'title': _('Warning!'),
                    'message': _('Return quantity should not be greater than allocated qty')
                }
        return {'value':vals,'warning':warning}
tpt_manage_equipment_inventory()
    
class shift_group(osv.osv):
    _name='shift.group'
    
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
              'name':fields.char('Name',size=1024, required = True),
              'sunday_id': fields.many2one('arul.hr.capture.work.shift', 'Sunday'),
              'monday_id': fields.many2one('arul.hr.capture.work.shift', 'Monday'),
              'tuesday_id': fields.many2one('arul.hr.capture.work.shift', 'Tuesday'),
              'wednesday_id': fields.many2one('arul.hr.capture.work.shift', 'Wednesday'),
              'thursday_id': fields.many2one('arul.hr.capture.work.shift', 'Thursday'),
              'friday_id': fields.many2one('arul.hr.capture.work.shift', 'Friday'),
              'saturday_id': fields.many2one('arul.hr.capture.work.shift', 'Saturday'),
              }
    

shift_group()

class shift_change(osv.osv):
    _name='shift.change'
    _columns={
              'num_of_month': fields.integer('Num Of Month'),
              'date_from': fields.many2one('tpt.month','Change Requested From', required = True, states={'approved': [('readonly', True)]}),
              'date_to': fields.many2one('tpt.month','Change Requested To', required = True, states={'approved': [('readonly', True)]}),
              'department_id':fields.many2one('hr.department','Department', required = True, states={'approved': [('readonly', True)]}),
              'section_id': fields.many2one('arul.hr.section','Section', required = True, states={'approved': [('readonly', True)]}),
              'employee_id': fields.many2one('hr.employee','Employee', required = True, states={'approved': [('readonly', True)]}),
              'year': fields.selection([(num, str(num)) for num in range(1950, 2026)], 'Work Schedule Year', required = True, states={'approved': [('readonly', True)]}),
              'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Work Schedule Month',required = True, states={'approved': [('readonly', True)]}),
              'shift_id': fields.many2one('arul.hr.capture.work.shift','Shift to be Changed', states={'approved': [('readonly', True)]}),
              'shift_group_id': fields.many2one('shift.group','Shift Group to be Changed', states={'approved': [('readonly', True)]}),
              'apply_weekly_off': fields.boolean('Apply schedule change to weekly off days?', states={'done': [('readonly', True)]}),
              'create_date': fields.datetime('Created Date',readonly = True),
              'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
              'state':fields.selection([('draft', 'Draft'),('submitted', 'Submitted'),('rejected', 'Rejected'),('approved', 'Approved')],'Status', readonly=True),
              'type': fields.selection([('single_shift', 'Single Shift'),('shift_group', 'Shift Group')],'Type',required=True, states={'approved': [('readonly', True)]}),
              }
    _defaults = {
        'type':'single_shift',
        'state':'draft',
        'year': int(time.strftime('%Y')),
    }
    
    def submit(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            sql = '''
                select id from arul_hr_monthly_shift_schedule where employee_id=%s
                    and monthly_work_id in (select id from arul_hr_monthly_work_schedule where department_id = %s and section_id = %s and year=%s and month='%s' and state='done')
            '''%(line.employee_id.id,line.department_id.id,line.section_id.id,line.year,line.month)
            cr.execute(sql)
            monthly_shift_ids = [row[0] for row in cr.fetchall()]
            if not monthly_shift_ids:
                raise osv.except_osv(_('Warning!'),_('Please Approve Monthly Work Schedule before Approve!!'))
        return self.write(cr, uid, ids, {'state': 'submitted'})
    
    def approve(self, cr, uid, ids, context=None):
        monthly_shift_obj = self.pool.get('arul.hr.monthly.shift.schedule')
        for line in self.browse(cr, uid, ids):
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                continue
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
            if line.state != 'submitted':
                raise osv.except_osv(_('Warning!'),_('Please Submit request before Approve!'))
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                continue
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
            sql = '''
                select id from arul_hr_monthly_shift_schedule where employee_id=%s
                    and monthly_work_id in (select id from arul_hr_monthly_work_schedule where department_id = %s and section_id = %s and year=%s and month='%s' and state='done')
            '''%(line.employee_id.id,line.department_id.id,line.section_id.id,line.year,line.month)
            cr.execute(sql)
            date_now = time.strftime('%Y-%m-%d')
            monthly_shift_ids = [row[0] for row in cr.fetchall()]
            for monthly_shift in monthly_shift_obj.browse(cr, uid, monthly_shift_ids):
                #if line.apply_weekly_off: #TPT: IF-ELSE COMMENTED By BalamuruganPurushothaman on 02_03_2015 - TO DO NOT TREAT SUNDAYS AS WEEK OFF FOREVER, 
                if line.type=='shift_group':
                    value={}
                    for num in range(line.date_from.name, line.date_to.name + 1):
                        shift_group = line.shift_group_id
                        year = int(line.year)
                        month = int(line.month)
                        if num == 1:
                            date = datetime.date (year, month, 1)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_1'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_1'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_1'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_1'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_1'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_1'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_1'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 2:
                            date = datetime.date (year, month, 2)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_2'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_2'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_2'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_2'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_2'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_2'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_2'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 3:
                            date = datetime.date (year, month, 3)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_3'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_3'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_3'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_3'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_3'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_3'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_3'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 4:
                            date = datetime.date (year, month, 4)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_4'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_4'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_4'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_4'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_4'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_4'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_4'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 5:
                            date = datetime.date (year, month, 5)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_5'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_5'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_5'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_5'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_5'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_5'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_5'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 6:
                            date = datetime.date (year, month, 6)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_6'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_6'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_6'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_6'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_6'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_6'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_6'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 7:
                            date = datetime.date (year, month, 7)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_7'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_7'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_7'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_7'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_7'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_7'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_7'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 8:
                            date = datetime.date (year, month, 8)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_8'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_8'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_8'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_8'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_8'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_8'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_8'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 9:
                            date = datetime.date (year, month, 9)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_9'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_9'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_9'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_9'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_9'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_9'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_9'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 10:
                            date = datetime.date (year, month, 10)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_10'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_10'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_10'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_10'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_10'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_10'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_10'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 11:
                            date = datetime.date (year, month, 11)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_11'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_11'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_11'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_11'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_11'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_11'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_11'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 12:
                            date = datetime.date (year, month, 12)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_12'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_12'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_12'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_12'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_12'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_12'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_12'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 13:
                            date = datetime.date (year, month, 13)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_13'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_13'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_13'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_13'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_13'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_13'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_13'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 14:
                            date = datetime.date (year, month, 14)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_14'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_14'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_14'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_14'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_14'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_14'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_14'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 15:
                            date = datetime.date (year, month, 15)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_15'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_15'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_15'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_15'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_15'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_15'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_15'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 16:
                            date = datetime.date (year, month, 16)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_16'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_16'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_16'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_16'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_16'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_16'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_16'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 17:
                            date = datetime.date (year, month, 17)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_17'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_17'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_17'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_17'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_17'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_17'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_17'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 18:
                            date = datetime.date (year, month, 18)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_18'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_18'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_18'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_18'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_18'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_18'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_18'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 19:
                            date = datetime.date (year, month, 19)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_19'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_19'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_19'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_19'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_19'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_19'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_19'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 20:
                            date = datetime.date (year, month, 20)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_20'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_20'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_20'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_20'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_20'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_20'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_20'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 21:
                            date = datetime.date (year, month, 21)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_21'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_21'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_21'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_21'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_21'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_21'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_21'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 22:
                            date = datetime.date (year, month, 22)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_22'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_22'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_22'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_22'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_22'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_22'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_22'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 23:
                            date = datetime.date (year, month, 23)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_23'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_23'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_23'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_23'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_23'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_23'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_23'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 24:
                            date = datetime.date (year, month, 24)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_24'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_24'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_24'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_24'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_24'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_24'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_24'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 25:
                            date = datetime.date (year, month, 25)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_25'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_25'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_25'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_25'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_25'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_25'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_25'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 26:
                            date = datetime.date (year, month, 26)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_26'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_26'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_26'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_26'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_26'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_26'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_26'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 27:
                            date = datetime.date (year, month, 27)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_27'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_27'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_27'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_27'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_27'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_27'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_27'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 28:
                            date = datetime.date (year, month, 28)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_28'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_28'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_28'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_28'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_28'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_28'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_28'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 29:
                            date = datetime.date (year, month, 29)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_29'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_29'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_29'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_29'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_29'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_29'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_29'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 30:
                            date = datetime.date (year, month, 30)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_30'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_30'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_30'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_30'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_30'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_30'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_30'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                        if num == 31:
                            date = datetime.date (year, month, 31)
                            name_day = date.strftime("%A")
                            if name_day == 'Sunday':
                                value['day_31'] = shift_group.sunday_id and shift_group.sunday_id.id or False
                            elif name_day == 'Monday':
                                value['day_31'] = shift_group.monday_id and shift_group.monday_id.id or False
                            elif name_day == 'Tuesday':
                                value['day_31'] = shift_group.tuesday_id and shift_group.tuesday_id.id or False
                            elif name_day == 'Wednesday':
                                value['day_31'] = shift_group.wednesday_id and shift_group.wednesday_id.id or False
                            elif name_day == 'Thursday':
                                value['day_31'] = shift_group.thursday_id and shift_group.thursday_id.id or False
                            elif name_day == 'Friday':
                                value['day_31'] = shift_group.friday_id and shift_group.friday_id.id or False
                            else:
                                value['day_31'] = shift_group.saturday_id and shift_group.saturday_id.id or False
                    monthly_shift_obj.write(cr, uid, [monthly_shift.id], value)
                else:
                    for num in range(line.date_from.name,line.date_to.name+1):
                            if num==1:
                                date = datetime.datetime(int(line.year),int(line.month),1)
                                ### An trong vong 2 thang sau do mo ra lai 31-01-2015
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_1':line.shift_id.id})
                            if num==2:
                                date = datetime.datetime(int(line.year),int(line.month),2)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_2':line.shift_id.id})
                            if num==3:
                                date = datetime.datetime(int(line.year),int(line.month),3)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_3':line.shift_id.id})
                            if num==4:
                                date = datetime.datetime(int(line.year),int(line.month),4)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_4':line.shift_id.id})
                            if num==5:
                                date = datetime.datetime(int(line.year),int(line.month),5)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_5':line.shift_id.id})
                            if num==6:
                                date = datetime.datetime(int(line.year),int(line.month),6)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_6':line.shift_id.id})
                            if num==7:
                                date = datetime.datetime(int(line.year),int(line.month),7)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_7':line.shift_id.id})
                            if num==8:
                                date = datetime.datetime(int(line.year),int(line.month),8)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_8':line.shift_id.id})
                            if num==9:
                                date = datetime.datetime(int(line.year),int(line.month),9)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_9':line.shift_id.id})
                            if num==10:
                                date = datetime.datetime(int(line.year),int(line.month),10)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_10':line.shift_id.id})
                            if num==11:
                                date = datetime.datetime(int(line.year),int(line.month),11)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_11':line.shift_id.id})
                            if num==12:
                                date = datetime.datetime(int(line.year),int(line.month),12)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_12':line.shift_id.id})
                            if num==13:
                                date = datetime.datetime(int(line.year),int(line.month),13)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_13':line.shift_id.id})
                            if num==14:
                                date = datetime.datetime(int(line.year),int(line.month),14)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_14':line.shift_id.id})
                            if num==15:
                                date = datetime.datetime(int(line.year),int(line.month),15)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_15':line.shift_id.id})
                            if num==16:
                                date = datetime.datetime(int(line.year),int(line.month),16)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_16':line.shift_id.id})
                            if num==17:
                                date = datetime.datetime(int(line.year),int(line.month),17)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_17':line.shift_id.id})
                            if num==18:
                                date = datetime.datetime(int(line.year),int(line.month),18)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_18':line.shift_id.id})
                            if num==19:
                                date = datetime.datetime(int(line.year),int(line.month),19)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_19':line.shift_id.id})
                            if num==20:
                                date = datetime.datetime(int(line.year),int(line.month),20)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_20':line.shift_id.id})
                            if num==21:
                                date = datetime.datetime(int(line.year),int(line.month),21)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_21':line.shift_id.id})
                            if num==22:
                                date = datetime.datetime(int(line.year),int(line.month),22)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_22':line.shift_id.id})
                            if num==23:
                                date = datetime.datetime(int(line.year),int(line.month),23)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_23':line.shift_id.id})
                            if num==24:
                                date = datetime.datetime(int(line.year),int(line.month),24)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_24':line.shift_id.id})
                            if num==25:
                                date = datetime.datetime(int(line.year),int(line.month),25)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_25':line.shift_id.id})
                            if num==26:
                                date = datetime.datetime(int(line.year),int(line.month),26)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_26':line.shift_id.id})
                            if num==27:
                                date = datetime.datetime(int(line.year),int(line.month),27)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_27':line.shift_id.id})
                            if num==28:
                                date = datetime.datetime(int(line.year),int(line.month),28)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_28':line.shift_id.id})
                            if num==29:
                                date = datetime.datetime(int(line.year),int(line.month),29)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_29':line.shift_id.id})
                            if num==30:
                                date = datetime.datetime(int(line.year),int(line.month),30)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_30':line.shift_id.id})
                            if num==31:
                                date = datetime.datetime(int(line.year),int(line.month),31)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_31':line.shift_id.id})
                    '''else:
                        for num in range(line.date_from.name,line.date_to.name+1):
                            if num==1 and monthly_shift.name_of_day_1 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),1)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_1':line.shift_id.id})
                            if num==2 and monthly_shift.name_of_day_2 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),2)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_2':line.shift_id.id})
                            if num==3 and monthly_shift.name_of_day_3 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),3)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_3':line.shift_id.id})
                            if num==4 and monthly_shift.name_of_day_4 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),4)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_4':line.shift_id.id})
                            if num==5 and monthly_shift.name_of_day_5 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),5)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_5':line.shift_id.id})
                            if num==6 and monthly_shift.name_of_day_6 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),6)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_6':line.shift_id.id})
                            if num==7 and monthly_shift.name_of_day_7 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),7)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_7':line.shift_id.id})
                            if num==8 and monthly_shift.name_of_day_8 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),8)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_8':line.shift_id.id})
                            if num==9 and monthly_shift.name_of_day_9 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),9)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_9':line.shift_id.id})
                            if num==10 and monthly_shift.name_of_day_10 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),10)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_10':line.shift_id.id})
                            if num==11 and monthly_shift.name_of_day_11 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),11)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_11':line.shift_id.id})
                            if num==12 and monthly_shift.name_of_day_12 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),12)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_12':line.shift_id.id})
                            if num==13 and monthly_shift.name_of_day_13 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),13)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_13':line.shift_id.id})
                            if num==14 and monthly_shift.name_of_day_14 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),14)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_14':line.shift_id.id})
                            if num==15 and monthly_shift.name_of_day_15 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),15)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_15':line.shift_id.id})
                            if num==16 and monthly_shift.name_of_day_16 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),16)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_16':line.shift_id.id})
                            if num==17 and monthly_shift.name_of_day_17 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),17)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_17':line.shift_id.id})
                            if num==18 and monthly_shift.name_of_day_18 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),18)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_18':line.shift_id.id})
                            if num==19 and monthly_shift.name_of_day_19 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),19)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_19':line.shift_id.id})
                            if num==20 and monthly_shift.name_of_day_20 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),20)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_20':line.shift_id.id})
                            if num==21 and monthly_shift.name_of_day_21 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),21)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_21':line.shift_id.id})
                            if num==22 and monthly_shift.name_of_day_22 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),22)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_22':line.shift_id.id})
                            if num==23 and monthly_shift.name_of_day_23 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),23)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_23':line.shift_id.id})
                            if num==24 and monthly_shift.name_of_day_24 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),24)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_24':line.shift_id.id})
                            if num==25 and monthly_shift.name_of_day_25 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),25)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_25':line.shift_id.id})
                            if num==26 and monthly_shift.name_of_day_26 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),26)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_26':line.shift_id.id})
                            if num==27 and monthly_shift.name_of_day_27 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),27)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_27':line.shift_id.id})
                            if num==28 and monthly_shift.name_of_day_28 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),28)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_28':line.shift_id.id})
                            if num==29 and monthly_shift.name_of_day_29 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),29)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_29':line.shift_id.id})
                            if num==30 and monthly_shift.name_of_day_30 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),30)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_30':line.shift_id.id})
                            if num==31 and monthly_shift.name_of_day_31 != 'Sunday':
                                date = datetime.datetime(int(line.year),int(line.month),31)
    #                             if date_now >= datetime.datetime.strftime(date, '%Y-%m-%d'):
    #                                 raise osv.except_osv(_('Warning!'),_('Can not change Work Monthly Schedule for past day!'))
                                monthly_shift_obj.write(cr, uid, [monthly_shift.id], {'day_31':line.shift_id.id})'''
        return self.write(cr, uid, ids, {'state': 'approved'})
    
    def reject(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if line.state != 'submitted':
                raise osv.except_osv(_('Warning!'),_('Please Submit request before Reject!'))
            if line.employee_id.department_id and line.employee_id.department_id.primary_auditor_id and line.employee_id.department_id.primary_auditor_id.id==uid \
            or line.employee_id.department_id and line.employee_id.department_id.secondary_auditor_id and line.employee_id.department_id.secondary_auditor_id.id==uid:
                continue
            else:
                raise osv.except_osv(_('Warning!'),_('User does not have permission to approve for this employee department!'))
        return self.write(cr, uid, ids, {'state': 'rejected'})
    
    def onchange_employee(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {
                'department_id': employee.department_id and employee.department_id.id or False,
                'section_id': employee.section_id and employee.section_id.id or False,
            }
        return {'value':vals}
    
    def onchange_department(self, cr, uid, ids,department_id=False,section_id=False, context=None):
        domain = {}
        vals = {'employee_id':False}
        if department_id and section_id:
            section_ids = self.pool.get('arul.hr.section').search(cr, uid, [('id','=',section_id),('department_id','=',department_id)])
            if not section_ids:
                vals.update({'section_id': False})
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('department_id','=',department_id),('section_id','=',section_id)])
            domain = {'employee_id':[('id','in',employee_ids)]}
        return {'value':vals,'domain':domain}
    
    def onchange_year_month(self, cr, uid, ids,month=False,year=False, context=None):
        num_of_month = 0
        if month and year:
            num_of_month = calendar.monthrange(int(year),int(month))[1]
        return {'value': {'num_of_month':num_of_month}}
    
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
        
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_for_shift_change_pri_auditor'):
            primary_auditor_ids = self.pool.get('hr.department').search(cr, uid, [('primary_auditor_id','=',uid)])
            if primary_auditor_ids:
                sql = '''
                    select id from shift_change where
                        department_id in (select id from hr_department where primary_auditor_id =%s)
                '''%(uid)
                cr.execute(sql)
                leave_details_ids = [r[0] for r in cr.fetchall()]
                args += [('id','in',leave_details_ids)]
        return super(shift_change, self).search(cr, uid, args, offset, limit, order, context, count)
shift_change()
