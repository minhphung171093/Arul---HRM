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
              'approval': fields.boolean('Select for Approval'),
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
    def approve_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': True})
        return True
    def reject_shift_time(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, [line.id],{'approval': False})
        return True   
arul_hr_audit_shift_time()

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
        'employee_id':fields.many2one('hr.employee','Employee'),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Category'),
        'sub_category_id':fields.many2one('hr.employee.sub.category','Sub Category'),
        'designation_id': fields.many2one('arul.hr.designation', 'Designation'),
        'department_id':fields.many2one('hr.department', 'Department'),
        'permission_onduty_details_line':fields.one2many('arul.hr.permission.onduty','detail_id','Permission On duty Details',readonly=True),
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
                for i,data1 in enumerate(L):
                    L2 = L[i+1:]
                    employee_code = data1[43:51]
                    employee_ids = employee_obj.search(cr, uid, [('employee_id','=',employee_code)])
                    date = data1[7:11]+'-'+data1[11:13]+'-'+data1[13:15]
                    temp = 0
                    if employee_ids and date:
                        if data1[:3]=='P10':
                            in_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            val1={'employee_id':employee_ids[0],'planned_work_shift_id':False,'work_date':date,'in_time':in_time,'out_time':0,'approval':1}
                            for j,data2 in enumerate(L2):
                                #bat dau vi tri tiep theo cua for 1
                                in_out = data2[:3]
                                employee_code_2=data2[43:51]
                                date_2=data2[7:11]+'-'+data2[11:13]+'-'+data2[13:15]
                                if employee_code_2==employee_code and date==date_2 and in_out=='P20':
                                    out_time=float(data2[15:17])+float(data2[17:19])/60+float(data2[19:21])/3600
                                    val1['out_time']=out_time
                                    #work_shift_ids = detail_obj3.search(cr, uid, [('start_time','>',in_time + 1/6 ),('end_time','<',out_time - 1/6 )])
#                                     planed_work_shift=' '.join(str(x) for x in work_shift_ids)
                                    sql = '''
                                        select id from arul_hr_capture_work_shift where (start_time between %s and start_time+1/6) and (end_time between end_time-1/6 and %s)
                                    '''%(in_time - 1,out_time + 1)
                                    cr.execute(sql)
                                    work_shift_ids = [row[0] for row in cr.fetchall()]
                                    if work_shift_ids :
                                        val1['planned_work_shift_id']=work_shift_ids[0]
                                        detail_obj.create(cr, uid, {'employee_id':employee_ids[0],'punch_in_out_line':[(0,0,val1)]})
                                    else:
                                        val1['approval']=False
                                        detail_obj2.create(cr, uid,val1)
#                                     if 4 <= (out_time - in_time) and (out_time - in_time) < 8:
#                                         val3={'employee_id':employee_ids[0],'planned_work_shift_id':planed_work_shift,'work_date':date,'in_time':in_time,'out_time':out_time,'approval':0}
#                                         detail_obj2.create(cr, uid,val3)
                                   
                                    temp +=1
                                    L.pop(j)
                                    break
                            if temp==0:
                                val={'employee_id':employee_ids[0],'work_date':date,'in_time':in_time,'out_time':0}
                                detail_obj2.create(cr, uid,val)
                        if data1[:3]=='P20':
                            out_time = float(data1[15:17])+float(data1[17:19])/60+float(data1[19:21])/3600
                            val2={'employee_id':employee_ids[0],'work_date':date,'in_time':0,'out_time':out_time}
                            detail_obj2.create(cr, uid,val2)
                            
                self.write(cr, uid, [line.id], {'state':'done'})
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e))


arul_hr_punch_in_out()


