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
              'code':fields.char('Code',size=1024, required = True),
              'name':fields.char('Name',size=1024, required = True),
              'description':fields.text('Description'),
              'start_time': fields.float('Shift Start Time'),
              'end_time': fields.float('Shift End Time'),
              'time_total': fields.function(_time_total, string='Shift Total Hours', multi='sums', help="The total amount."),
              'allowance': fields.char('Shift Allowance', size=1024),
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
                emp_attendence_obj.create(cr,uid,{'employee_id':line.employee_id.id, 'employee_category_id':line.employee_id.employee_category_id.id, 'sub_category_id':line.employee_id.employee_sub_category_id.id,'designation_id':line.employee_id.department_id.designation_id.id, 'department_id':line.employee_id.department_id.id, 'punch_in_out_line':[(0,0,val1)]}) 
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
            timedelta = (to_dt - from_dt).days+1
            if date.haft_day_leave:
                timedelta = timedelta-0.5
            res[date.id] = {
                'days_total': timedelta
            }
        return res
    
    _columns={
              'employee_id':fields.many2one('hr.employee','Employee'),
              'leave_type_id':fields.many2one('arul.hr.leave.types','Leave Type',required=True),
              'date_from':fields.date('Date From'),
              'date_to': fields.date('To Date'),
              'days_total': fields.function(days_total, string='Leave Total',store=True, multi='sums', help="The total amount.",required=True),
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
            if(non_availability_type_id == 'on_duty'):
                if(line_id.time_total > 8)and(line_id.time_total < 12):
                    val={'permission_onduty_id':emp_attendence_ids[0],'planned_work_shift_id':False,'work_date':date,'in_time':start_time,'out_time':end_time,'approval':1}
                    sql = '''
                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                    '''%(in_time - 1,out_time + 1)
                    cr.execute(sql)
                    work_shift_ids = [row[0] for row in cr.fetchall()]
                    if work_shift_ids :
                        val['planned_work_shift_id']=work_shift_ids[0]
                        details_ids=emp_attendence_obj.search(cr, uid, [('employee_id','=',emp_attendence_ids[0])])
                        if details_ids:
                            val4={'punch_in_out_id':details_ids[0],'planned_work_shift_id':work_shift_ids[0],'employee_id':emp_attendence_ids[0],'work_date':date,'in_time':start_time,'out_time':end_time,'approval':1}
                            detail_obj4.create(cr, uid, val4)
                        else:
                            emp_attendence_obj.create(cr, uid, {'employee_id':employee_ids[0],'punch_in_out_line':[(0,0,val)]})
                    
            val2={'permission_onduty_id':emp_attendence_ids[0], 
                    }
            punch_obj.write(cr,uid,[line_id.id],val2) 
        else:
            
            emp_attendence_id = emp_attendence_obj.create(cr,uid,{'employee_id':line_id.employee_id.id,'employee_category_id':line_id.employee_id.employee_category_id.id,'sub_category_id':line_id.employee_id.employee_sub_category_id.id,'department_id':line_id.employee_id.department_id.id,'designation_id':line_id.employee_id.department_id.designation_id.id}) 
            punch_obj.write(cr,uid,[line_id.id],{'permission_onduty_id':emp_attendence_id}) 
#             self.write(cr, uid, [line.id],{'approval': True})
        return new_id
    
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
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category',readonly=True),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category',readonly=True),
        'designation_id': fields.many2one('arul.hr.designation', 'Designation',readonly=True),
        'department_id':fields.many2one('hr.department', 'Department',readonly=True),
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
        'date_up_load': fields.date('Date Up load', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Upload/View Specification', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)

    }
    
    _defaults = {
        'state':'draft',
        'date_up_load': time.strftime('%Y-%m-%d'),
        
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
              'year': fields.char('Year', size = 1024,required = True, states={'done': [('readonly', True)]}),
              'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True, states={'done': [('readonly', True)]}),
              'monthly_shift_line': fields.one2many('arul.hr.monthly.shift.schedule','monthly_work_id', 'Monthly Work Schedule', states={'done': [('readonly', True)]}),
              'state':fields.selection([('draft', 'Draft'),('load', 'Load'),('done', 'Done')],'Status', readonly=True)
              }
    _defaults = {
        'state':'draft',
        
    }
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
                                           'day_1': work.day_1,
                                           'day_2': work.day_2,
                                           'day_3': work.day_3,
                                           'day_4': work.day_4,
                                           'day_5': work.day_5,
                                           'day_6': work.day_6,
                                           'day_7': work.day_7,
                                           'day_8': work.day_8,
                                           'day_9': work.day_9,
                                           'day_10': work.day_10,
                                           'day_11': work.day_11,
                                           'day_12': work.day_12,
                                           'day_13': work.day_13,
                                           'day_14': work.day_14,
                                           'day_15': work.day_15,
                                           'day_16': work.day_16,
                                           'day_17': work.day_17,
                                           'day_18': work.day_18,
                                           'day_19': work.day_19,
                                           'day_20': work.day_20,
                                           'day_21': work.day_21,
                                           'day_22': work.day_22,
                                           'day_23': work.day_23,
                                           'day_24': work.day_24,
                                           'day_25': work.day_25,
                                           'day_26': work.day_26,
                                           'day_27': work.day_27,
                                           'day_28': work.day_28,
                                           'day_29': work.day_29,
                                           'day_30': work.day_30,
                                           'day_31': work.day_31,
                                           }))
                self.write(cr, uid, [line.id], {'monthly_shift_line':work_vals,'state':'load'})
        return True
    def approve_current_month(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'})
    def onchange_department_id(self, cr, uid, ids,department_id=False, context=None):
        res = {'value':{}}
        section_ids = []
        employee_lines = []
        if department_id:
            dept = self.pool.get('hr.department').browse(cr, uid, department_id)
            section_ids = [x.id for x in dept.section_ids]
            employee_obj=self.pool.get('hr.employee')
            employee_ids = employee_obj.search(cr, uid, [('department_id','=',department_id )])
            for p in self.browse(cr,uid,employee_ids):
                rs = {
                      'employee_id':p.id
                      }
                employee_lines.append((0,0,rs))
        return {'value': {'section_id': False,'monthly_shift_line':employee_lines}, 'domain':{'section_id':[('id','in',section_ids)]}}
        
arul_hr_monthly_work_schedule()

class arul_hr_monthly_shift_schedule(osv.osv):
    _name='arul.hr.monthly.shift.schedule'
    def _num_of_month(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for day in self.browse(cr, uid, ids):
            res[day.id] = {
                'num_of_month': 0,
            }
            num_day = calendar.monthrange(int(day.monthly_work_id.year),int(day.monthly_work_id.month))[1]  
            res[day.id]['num_of_month'] = num_day 
        return res
    _columns={
              'num_of_month': fields.function(_num_of_month, string='Day',store=True, multi='sums', help="The total amount."),
#               'num_of_month': fields.integer('Day'),
              'employee_id':fields.many2one('hr.employee','Employee', required = True),
              'monthly_work_id':fields.many2one('arul.hr.monthly.work.schedule','Monthly Shift Schedule'),
              'day_1': fields.char('1',size=500),
              'day_2': fields.char('2',size=500),
              'day_3': fields.char('3',size=500),
              'day_4': fields.char('4',size=500),
              'day_5': fields.char('5',size=500),
              'day_6': fields.char('6',size=500),
              'day_7': fields.char('7',size=500),
              'day_8': fields.char('8',size=500),
              'day_9': fields.char('9',size=500),
              'day_10': fields.char('10',size=500),
              'day_11': fields.char('11',size=500),
              'day_12': fields.char('12',size=500),
              'day_13': fields.char('13',size=500),
              'day_14': fields.char('14',size=500),
              'day_15': fields.char('15',size=500),
              'day_16': fields.char('16',size=500),
              'day_17': fields.char('17',size=500),
              'day_18': fields.char('18',size=500),
              'day_19': fields.char('19',size=500),
              'day_20': fields.char('20',size=500),
              'day_21': fields.char('21',size=500),
              'day_22': fields.char('22',size=500),
              'day_23': fields.char('23',size=500),
              'day_24': fields.char('24',size=500),
              'day_25': fields.char('25',size=500),
              'day_26': fields.char('26',size=500),
              'day_27': fields.char('27',size=500),
              'day_28': fields.char('28',size=500),
              'day_29': fields.char('29',size=500),
              'day_30': fields.char('30',size=500),
              'day_31': fields.char('31',size=500),
              }
arul_hr_monthly_shift_schedule()

