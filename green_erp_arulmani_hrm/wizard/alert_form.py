# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
import time
import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class alert_form(osv.osv_memory):
    _name = "alert.form"
    _columns = {    
                'type': fields.selection(WARNING_TYPES, string='Type', readonly=True),
                'title': fields.char(string="Title", size=100, readonly=True),
                'message': fields.text(string="Message ", readonly=True),    
                }
    _req_name = 'title'

    def _get_view_id(self, cr, uid):
        """Get the view id
        @return: view id, or False if no view found
        """
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
            'green_erp_arulmani_hrm', 'alert_form_view')
        return res and res[1] or False
    
    def message(self, cr, uid, id, context):
        message = self.browse(cr, uid, id)
        message_type = [t[1]for t in WARNING_TYPES if message.type == t[0]][0]
        print '%s: %s' % (_(message_type), _(message.title))
        res = {
            'name': '%s: %s' % (_(message_type), _(message.title)),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self._get_view_id(cr, uid),
            'res_model': 'alert.form',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': message.id
        }
        return res
    
    def warning(self, cr, uid, title, message, context=None):
        id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'warning'})
        res = self.message(cr, uid, id, context)
        return res
    
    def info(self, cr, uid, title, message, context=None):
        id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'info'})
        res = self.message(cr, uid, id, context)
        return res
    
    def error(self, cr, uid, title, message, context=None):
        id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'error'})
        res = self.message(cr, uid, id, context)
        return res
    
    def reject(self, cr, uid, ids, context=None):
        payroll_obj = self.pool.get('arul.hr.payroll.executions')
        execution_id = context.get('active_ids')[0]
        line = self.pool.get('tpt.hr.payroll.approve.reject').browse(cr,uid,execution_id)
        executions_obj = self.pool.get('arul.hr.payroll.executions.details')
        payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state', '=', 'confirm')])
        if not payroll_ids:
            raise osv.except_osv(_('Warning !'), _("Do not find the confirmed payroll!"))
        payroll_obj.write(cr, uid, payroll_ids, {'state':'draft'})
        executions_ids = executions_obj.search(cr, uid, [('payroll_executions_id','in',payroll_ids)])
        if not executions_ids:
            raise osv.except_osv(_('Warning !'), _("Can not confirm this payroll!"))
        else:
            executions_obj.unlink(cr, uid, executions_ids, context=context)
        self.pool.get('tpt.hr.payroll.approve.reject').write(cr, uid, [execution_id], {'state':'cancel'})
        return {'type': 'ir.actions.act_window_close'}
    
    def approve_audit(self, cr, uid, ids, context=None):
        audit_ids = context.get('active_ids')
        self.pool.get('arul.hr.audit.shift.time').approve_shift_time_multi(cr, uid, audit_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def reject_audit(self, cr, uid, ids, context=None):
        audit_ids = context.get('active_ids')
        self.pool.get('arul.hr.audit.shift.time').reject_shift_time(cr, uid, audit_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def approve_shift_change(self, cr, uid, ids, context=None):
        shift_change_ids = context.get('active_ids')
        self.pool.get('shift.change').approve(cr, uid, shift_change_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def reject_shift_change(self, cr, uid, ids, context=None):
        shift_change_ids = context.get('active_ids')
        self.pool.get('shift.change').reject(cr, uid, shift_change_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def third_permission_ok(self, cr, uid, ids, context=None):
        emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
        punch_obj = self.pool.get('arul.hr.punch.in.out.time')
        employee_leave_obj = self.pool.get('employee.leave')
        leave_detail_obj = self.pool.get('arul.hr.employee.leave.details')
        audit_id = context.get('audit_id')
        audit = self.pool.get('arul.hr.audit.shift.time').browse(cr, uid, audit_id)
        
        #raise osv.except_osv(_('Warning!'),_(test)) 
        audit_id = context.get('audit_id')
        perm_obj = self.pool.get('arul.hr.permission.onduty').browse(cr, uid, audit_id)
        
        year = perm_obj.date[:4]
        employee_leave_ids = employee_leave_obj.search(cr, uid, [('employee_id','=',perm_obj.employee_id.id),('year','=',year)])
        if employee_leave_ids:
            for detail in employee_leave_obj.browse(cr, uid, employee_leave_ids[0]).emp_leave_details_ids:
                if detail.leave_type_id.code == 'CL' and (detail.total_day-detail.total_taken>=0.5):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': perm_obj.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': perm_obj.date,
                                        'date_to': perm_obj.date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                if detail.leave_type_id.code == 'SL' and (detail.total_day-detail.total_taken>=0.5):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': perm_obj.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': perm_obj.date,
                                        'date_to': perm_obj.date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                #TPT START BalamuruganPurushothaman - TO REDUCE LEAVE COUNT FROM C.OFF ALSO
                if detail.leave_type_id.code == 'C.Off' and (detail.total_day-detail.total_taken>=0.5):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': perm_obj.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': perm_obj.date,
                                        'date_to': perm_obj.date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                #TPT END
                if detail.leave_type_id.code == 'PL' and (detail.total_day-detail.total_taken>=1):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': perm_obj.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': perm_obj.date,
                                        'date_to': perm_obj.date,
                                        'haft_day_leave': False,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                if detail.leave_type_id.code == 'LOP':
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': perm_obj.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': perm_obj.date,
                                        'date_to': perm_obj.date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
        ###
        #line_id=perm_obj.id
        #=======================================================================
        emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
        emp_attendence_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',perm_obj.employee_id.id)])
        # 
        # punch_obj = self.pool.get('arul.hr.punch.in.out.time')
        # val2={'permission_onduty_id':perm_obj.id, 'approval':1,
        # 
        #                         }
        # line_id = emp_attendence_ids[0]
        # punch_obj.write(cr,uid,[line_id],val2)  
        #=======================================================================
        ###
        
        sql = ''' update arul_hr_permission_onduty set approval='t',permission_onduty_id=%s where id=%s  
        '''%(emp_attendence_ids[0], perm_obj.id) 
        cr.execute(sql)
        
        self.pool.get('arul.hr.permission.onduty').write(cr, uid, [audit_id],{'approval': True, 'state':'done'})
        return {'type': 'ir.actions.act_window_close'}
    
    def permission_alert(self, cr, uid, ids, context=None): 
        return {'type': 'ir.actions.act_window_close'}    
    def permission_ok(self, cr, uid, ids, context=None): 
        emp_attendence_obj = self.pool.get('arul.hr.employee.attendence.details')
        punch_obj = self.pool.get('arul.hr.punch.in.out.time')
        employee_leave_obj = self.pool.get('employee.leave')
        leave_detail_obj = self.pool.get('arul.hr.employee.leave.details')
        audit_id = context.get('audit_id')
        audit = self.pool.get('arul.hr.audit.shift.time').browse(cr, uid, audit_id)
        
        year = audit.work_date[:4]
        employee_leave_ids = employee_leave_obj.search(cr, uid, [('employee_id','=',audit.employee_id.id),('year','=',year)])
        if employee_leave_ids:
            for detail in employee_leave_obj.browse(cr, uid, employee_leave_ids[0]).emp_leave_details_ids:
                if detail.leave_type_id.code == 'CL' and (detail.total_day-detail.total_taken>=0.5):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': audit.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': audit.work_date,
                                        'date_to': audit.work_date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                if detail.leave_type_id.code == 'SL' and (detail.total_day-detail.total_taken>=0.5):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': audit.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': audit.work_date,
                                        'date_to': audit.work_date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                #TPT START BalamuruganPurushothaman - TO REDUCE LEAVE COUNT FROM C.OFF ALSO
                if detail.leave_type_id.code == 'C.Off' and (detail.total_day-detail.total_taken>=0.5):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': audit.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': audit.work_date,
                                        'date_to': audit.work_date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                #TPT END
                if detail.leave_type_id.code == 'PL' and (detail.total_day-detail.total_taken>=1):
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': audit.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': audit.work_date,
                                        'date_to': audit.work_date,
                                        'haft_day_leave': False,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
                if detail.leave_type_id.code == 'LOP':
                    leave_detail_id = leave_detail_obj.create(cr, uid, {
                                        'employee_id': audit.employee_id.id,
                                        'leave_type_id': detail.leave_type_id.id,
                                        'date_from': audit.work_date,
                                        'date_to': audit.work_date,
                                        'haft_day_leave': True,
                                        'state': 'draft',
                                    })
                    leave_detail_obj.process_leave_request(cr, uid, [leave_detail_id])
                    break
        employee_ids = emp_attendence_obj.search(cr, uid, [('employee_id','=',audit.employee_id.id)])
        ### TPT START
        if audit.in_time > audit.out_time:
                    time_total = 24-audit.in_time + audit.out_time
        else:
                    time_total = audit.out_time - audit.in_time
        if audit.diff_day and (audit.in_time <= audit.out_time):
                time_total += 24
                    
        permission_count = 0
        onduty_count = 0
        perm_onduty_count = 0
        total_hrs = 0
        a_shift_count = 0
        g1_shift_count = 0
        g2_shift_count = 0
        b_shift_count = 0
        c_shift_count = 0
                
        total_shift_worked = 0
        third_perm_adj_hr = 1 # 1 Hr is added with total shift worked hours. since we could not deduct shift count, since Leave Count has been also deducted.
        
        sql = '''
                SELECT CASE WHEN SUM(time_total)!=0 THEN SUM(time_total) ELSE 0 END time_total FROM arul_hr_permission_onduty WHERE 
                non_availability_type_id='permission' 
                    AND TO_CHAR(date,'YYYY-MM-DD') = ('%s') and employee_id =%s and approval='t'
                    '''%(audit.work_date,audit.employee_id.id)
        cr.execute(sql)
        b =  cr.fetchone()
        permission_count = b[0]
            
                #OnDuty
        sql = '''
                    SELECT CASE WHEN SUM(time_total)!=0 THEN SUM(time_total) ELSE 0 END time_total FROM arul_hr_permission_onduty WHERE non_availability_type_id='on_duty' 
                    AND TO_CHAR(date,'YYYY-MM-DD') = ('%s') and employee_id =%s and approval='t'
                    '''%(audit.work_date,audit.employee_id.id)
        cr.execute(sql)
        c =  cr.fetchone()
        onduty_count = c[0]
                
        perm_onduty_count =   permission_count + onduty_count
        total_hrs = time_total + perm_onduty_count + third_perm_adj_hr
                
        total_hrs = timedelta(hours=total_hrs)
                #Work Shift Taking from Master
        sql = '''
                    SELECT min_start_time,start_time,max_start_time,min_end_time,end_time,max_end_time FROM arul_hr_capture_work_shift WHERE code='A'
                    '''
        cr.execute(sql)
        for k in cr.fetchall():
                    a_min_start_time=k[0]
                    a_start_time=k[1]
                    a_max_start_time=k[2]
                    a_min_end_time=k[3]
                    a_end_time=k[4]
                    a_max_end_time=k[5]
                    
        sql = '''
                    SELECT min_start_time,start_time,max_start_time,min_end_time,end_time,max_end_time FROM arul_hr_capture_work_shift WHERE code='C'
                    '''
        cr.execute(sql)
        for k in cr.fetchall():
                    c_min_start_time=k[0]
                    c_start_time=k[1]
                    c_max_start_time=k[2]
                    c_min_end_time=k[3]
                    c_end_time=k[4]
                    c_max_end_time=k[5]
                    
        sql = '''
                    SELECT min_start_time,start_time,max_start_time,min_end_time,end_time,max_end_time FROM arul_hr_capture_work_shift WHERE code='B'
                    '''
        cr.execute(sql)
        for k in cr.fetchall():
                    b_min_start_time=k[0]
                    b_start_time=k[1]
                    b_max_start_time=k[2]
                    b_min_end_time=k[3]
                    b_end_time=k[4]
                    b_max_end_time=k[5]
        sql = '''
                    SELECT min_start_time,start_time,max_start_time,min_end_time,end_time,max_end_time FROM arul_hr_capture_work_shift WHERE code='G1'
                    '''
        cr.execute(sql)
        for k in cr.fetchall():
                    g1_min_start_time=k[0]
                    g1_start_time=k[1]
                    g1_max_start_time=k[2]
                    g1_min_end_time=k[3]
                    g1_end_time=k[4]
                    g1_max_end_time=k[5]
        sql = '''
                    SELECT min_start_time,start_time,max_start_time,min_end_time,end_time,max_end_time FROM arul_hr_capture_work_shift WHERE code='G2'
                    '''
        cr.execute(sql)
        for k in cr.fetchall():
                    g2_min_start_time=k[0]
                    g2_start_time=k[1]
                    g2_max_start_time=k[2]
                    g2_min_end_time=k[3]
                    g2_end_time=k[4]
                    g2_max_end_time=k[5]
                #raise osv.except_osv(_('Warning!'),_(a_min_start_time))    
                #raise osv.except_osv(_('Warning!'),_(a_start_time))    
        sql = '''
                        SELECT min_start_time FROM arul_hr_capture_work_shift WHERE code='G1'
                        '''
        cr.execute(sql)
        k = cr.fetchone()
        g1_min_start_time=k[0]
                
                ## B Shift
        work_shift_obj = self.pool.get('arul.hr.capture.work.shift') 
        work_shift = work_shift_obj.search(cr, uid, [('code','=','B')])
        work_shift1 = work_shift_obj.browse(cr,uid,work_shift[0])
        b_shift_total_time = work_shift1.time_total   
        b_shift_half_total_time = work_shift1.time_total/2 
                    
        b_min_start_time = timedelta(hours=b_min_start_time)
        b_max_start_time = timedelta(hours=b_max_start_time) 
        b_min_end_time = timedelta(hours=b_min_end_time) 
                    
                ## C Shift                
        c_work_shift = work_shift_obj.search(cr, uid, [('code','=','C')])
        c_work_shift1 = work_shift_obj.browse(cr,uid,work_shift[0])
        c_shift_total_time = c_work_shift1.time_total   
        c_shift_half_total_time = work_shift1.time_total/2 
                    
        c_min_start_time = timedelta(hours=c_min_start_time)
        c_max_start_time = timedelta(hours=c_max_start_time) 
        c_min_end_time = timedelta(hours=c_min_end_time) 
                    
                ## A Shift                
        a_work_shift = work_shift_obj.search(cr, uid, [('code','=','A')])
        a_work_shift1 = work_shift_obj.browse(cr,uid,work_shift[0])
        a_shift_total_time = c_work_shift1.time_total   
        a_shift_half_total_time = work_shift1.time_total/2 
                    
        a_min_start_time = timedelta(hours=a_min_start_time)
        a_max_start_time = timedelta(hours=a_max_start_time) 
        a_min_end_time = timedelta(hours=a_min_end_time) 
                    
        actual_out = timedelta(hours=audit.out_time) 
        actual_in = timedelta(hours=audit.in_time)
                ##
        if audit.actual_work_shift_id.code=='A':
                    #raise osv.except_osv(_('Warning!'),_(line.actual_work_shift_id.min_start_time)) 
                    half_shift_hrs = audit.actual_work_shift_id.time_total / 2   
                    full_shift_hrs = audit.actual_work_shift_id.time_total
                    #full_half_shift_hrs =  full_shift_hrs  + half_shift_hrs   
                    #full_full_shift_hrs = line.actual_work_shift_id.time_total + line.actual_work_shift_id.time_total
                    full_half_shift_hrs =  full_shift_hrs  + b_shift_half_total_time   # A shift + B Shift 0.5 shift
                    full_full_shift_hrs = audit.actual_work_shift_id.time_total + b_shift_total_time # A shift + B Shift 1 shift
                    full_full_half_shift_hrs = full_full_shift_hrs + half_shift_hrs
                    
                    half_shift_hrs = timedelta(hours=half_shift_hrs)
                    full_shift_hrs = timedelta(hours=full_shift_hrs)
                    full_half_shift_hrs = timedelta(hours=full_half_shift_hrs)
                    full_full_shift_hrs = timedelta(hours=full_full_shift_hrs)
                    full_full_half_shift_hrs = timedelta(hours=full_full_half_shift_hrs)
                          
                    if half_shift_hrs <= total_hrs < full_shift_hrs:
                        a_shift_count = 0.5  
                        total_shift_worked = 0.5 
                    if full_shift_hrs <= total_hrs < full_half_shift_hrs:  
                        a_shift_count = 1  
                        total_shift_worked = 1
                    if full_half_shift_hrs <= total_hrs < full_full_shift_hrs:  
                        a_shift_count = 1  
                        b_shift_count = 0.5 
                        total_shift_worked = 1.5
                    if full_full_shift_hrs <= total_hrs < full_full_half_shift_hrs:  
                        a_shift_count = 1  
                        b_shift_count = 1 
                        total_shift_worked = 2

        if audit.actual_work_shift_id.code=='G1':
                    half_shift_hrs = audit.actual_work_shift_id.time_total / 2   
                    full_shift_hrs = audit.actual_work_shift_id.time_total
                    #full_half_shift_hrs =  full_shift_hrs  + half_shift_hrs  
                                 
                    full_half_shift_hrs =  full_shift_hrs  + b_shift_half_total_time   # G1 shift + B Shift 0.5 shift
                    full_full_shift_hrs = audit.actual_work_shift_id.time_total + b_shift_total_time # G1 shift + B Shift 1 shift
                    full_full_half_shift_hrs = full_full_shift_hrs + half_shift_hrs
                    
                    half_shift_hrs = timedelta(hours=half_shift_hrs)
                    full_shift_hrs = timedelta(hours=full_shift_hrs)
                    full_half_shift_hrs = timedelta(hours=full_half_shift_hrs)
                    full_full_shift_hrs = timedelta(hours=full_full_shift_hrs)
                    full_full_half_shift_hrs = timedelta(hours=full_full_half_shift_hrs)
                    
                    g1_min_end_time = timedelta(hours=g1_min_end_time)
                    g1_max_end_time = timedelta(hours=g1_max_end_time)
                    
   
                    if half_shift_hrs <= total_hrs < full_shift_hrs:
                        g1_shift_count = 0.5  
                        total_shift_worked = 0.5 
                    if g1_min_end_time  <= actual_out <  g1_max_end_time: 
                        if full_shift_hrs <= total_hrs:
                            g1_shift_count = 1  
                            total_shift_worked = 1
                    if g1_max_end_time  <= actual_out:   
                        if full_half_shift_hrs <= total_hrs:  
                            if g1_max_end_time  <= actual_out and b_max_start_time <= actual_out:
                                #raise osv.except_osv(_('Warning!%s'),_(g1_max_end_time)) 
                                g1_shift_count = 1  
                                b_shift_count = 0.5 
                                total_shift_worked = 1.5
                    if b_min_end_time  <= actual_out: 
                        if full_full_shift_hrs <= total_hrs:
                            if g1_max_end_time  < actual_out:
                                g1_shift_count = 1  
                                b_shift_count = 1 
                                total_shift_worked = 2
                                
        if audit.actual_work_shift_id.code=='G2':
                    half_shift_hrs = audit.actual_work_shift_id.time_total / 2   
                    full_shift_hrs = audit.actual_work_shift_id.time_total
                    
                    #full_half_shift_hrs =  full_shift_hrs  + half_shift_hrs  
                    work_shift_obj = self.pool.get('arul.hr.capture.work.shift') 
                    work_shift = work_shift_obj.search(cr, uid, [('code','=','B')])
                    work_shift1 = work_shift_obj.browse(cr,uid,work_shift[0])
                    b_shift_total_time = work_shift1.time_total   
                    b_shift_half_total_time = work_shift1.time_total/2            
                    full_half_shift_hrs =  full_shift_hrs  + b_shift_half_total_time  
                      
                    full_full_shift_hrs = audit.actual_work_shift_id.time_total + b_shift_total_time
                    full_full_half_shift_hrs = full_full_shift_hrs + half_shift_hrs
                    
                    half_shift_hrs = timedelta(hours=half_shift_hrs)
                    full_shift_hrs = timedelta(hours=full_shift_hrs)
                    full_half_shift_hrs = timedelta(hours=full_half_shift_hrs)
                    full_full_shift_hrs = timedelta(hours=full_full_shift_hrs)
                    full_full_half_shift_hrs = timedelta(hours=full_full_half_shift_hrs)
                    
                    g2_min_end_time = timedelta(hours=g2_min_end_time)
                    g2_max_end_time = timedelta(hours=g2_max_end_time)
       
                    if half_shift_hrs <= total_hrs < full_shift_hrs:
                        g2_shift_count = 0.5  
                        total_shift_worked = 0.5 
                    if g2_min_end_time  <= actual_out <  g2_max_end_time: 
                        if full_shift_hrs <= total_hrs:
                            g2_shift_count = 1  
                            total_shift_worked = 1
                    if g2_max_end_time  <= actual_out: 
                        if full_half_shift_hrs <= total_hrs:
                            if g2_max_end_time  <= actual_out and b_min_start_time <= actual_out:
                                g2_shift_count = 1  
                                b_shift_count = 0.5 
                                total_shift_worked = 1.5
                    if b_min_end_time  <= actual_out: 
                        if full_half_shift_hrs <= total_hrs:
                            if g2_max_end_time  < actual_out:
                                g2_shift_count = 1  
                                b_shift_count = 1 
                                total_shift_worked = 2
                        
        if audit.actual_work_shift_id.code=='B':
                    half_shift_hrs = audit.actual_work_shift_id.time_total / 2   
                    full_shift_hrs = audit.actual_work_shift_id.time_total
                    full_half_shift_hrs =  full_shift_hrs  + c_shift_half_total_time   
                    full_full_shift_hrs = audit.actual_work_shift_id.time_total + c_shift_total_time
                    full_full_half_shift_hrs = full_full_shift_hrs + half_shift_hrs
                    
                    half_shift_hrs = timedelta(hours=half_shift_hrs)
                    full_shift_hrs = timedelta(hours=full_shift_hrs)
                    full_half_shift_hrs = timedelta(hours=full_half_shift_hrs)
                    full_full_shift_hrs = timedelta(hours=full_full_shift_hrs)
                    full_full_half_shift_hrs = timedelta(hours=full_full_half_shift_hrs)
                          
                    if half_shift_hrs <= total_hrs < full_shift_hrs:
                        b_shift_count = 0.5  
                        total_shift_worked = 0.5 
                    if full_shift_hrs <= total_hrs < full_half_shift_hrs:  
                        b_shift_count = 1  
                        total_shift_worked = 1
                    if full_half_shift_hrs <= total_hrs < full_full_shift_hrs:  
                        if actual_in<=a_min_start_time:
                            b_shift_count = 1  
                            a_shift_count = 0.5 
                        else:
                            b_shift_count = 1  
                            c_shift_count = 0.5 
                        total_shift_worked = 1.5
                            
                    if full_full_shift_hrs <= total_hrs < full_full_half_shift_hrs:  
                        if actual_in<=a_min_start_time:
                            b_shift_count = 1  
                            a_shift_count = 1 
                        else:
                            b_shift_count = 1  
                            c_shift_count = 1 
                        total_shift_worked = 2
                        
                        
        if audit.actual_work_shift_id.code=='C':
                    half_shift_hrs = audit.actual_work_shift_id.time_total / 2   
                    full_shift_hrs = audit.actual_work_shift_id.time_total
                    full_half_shift_hrs =  full_shift_hrs  + a_shift_half_total_time   
                    full_full_shift_hrs = audit.actual_work_shift_id.time_total + a_shift_total_time
                    full_full_half_shift_hrs = full_full_shift_hrs + half_shift_hrs
                    
                    half_shift_hrs = timedelta(hours=half_shift_hrs)
                    full_shift_hrs = timedelta(hours=full_shift_hrs)
                    full_half_shift_hrs = timedelta(hours=full_half_shift_hrs)
                    full_full_shift_hrs = timedelta(hours=full_full_shift_hrs)
                    full_full_half_shift_hrs = timedelta(hours=full_full_half_shift_hrs)
                          
                    if half_shift_hrs <= total_hrs < full_shift_hrs:
                        c_shift_count = 0.5  
                        total_shift_worked = 0.5 
                    if full_shift_hrs <= total_hrs < full_half_shift_hrs:  
                        c_shift_count = 1  
                        total_shift_worked = 1
                    if full_half_shift_hrs <= total_hrs < full_full_shift_hrs:  
                        if actual_in<=b_min_start_time:
                            c_shift_count = 1  
                            b_shift_count = 0.5 
                        else:
                            c_shift_count = 1  
                            a_shift_count = 0.5 
                        total_shift_worked = 1.5
                            
                    if full_full_shift_hrs <= total_hrs < full_full_half_shift_hrs:  
                        if actual_in<=b_min_start_time:
                            c_shift_count = 1  
                            b_shift_count = 1 
                        else:
                            c_shift_count = 1  
                            a_shift_count = 1 
                        total_shift_worked = 2
        if employee_ids:
            
            val2={'punch_in_out_id':employee_ids[0], 
                  'employee_id': audit.employee_id.id,
                  'work_date':audit.work_date, 
                  'planned_work_shift_id':audit.planned_work_shift_id.id,
                  'actual_work_shift_id':audit.actual_work_shift_id.id,
                  'in_time':audit.in_time,
                  'out_time':audit.out_time,
                  'approval':1,
                  
                  'a_shift_count':a_shift_count,
                  'g1_shift_count':g1_shift_count,
                  'g2_shift_count':g2_shift_count,
                  'b_shift_count':b_shift_count,
                  'c_shift_count':c_shift_count,
                  'total_shift_worked':total_shift_worked,
                              
                  'a_shift_count1':a_shift_count,
                  'g1_shift_count1':g1_shift_count,
                  'g2_shift_count1':g2_shift_count,
                  'b_shift_count1':b_shift_count,
                  'c_shift_count1':c_shift_count,
                  'total_shift_worked1':total_shift_worked,
                          
                    }
            punch_obj.create(cr,uid,val2) 
        else:
            val1={
                  'employee_id':audit.employee_id.id,
                  'work_date':audit.work_date,
                  'planned_work_shift_id':audit.planned_work_shift_id.id,
                  'actual_work_shift_id':audit.actual_work_shift_id.id,
                  'in_time':audit.in_time,
                  'out_time':audit.out_time,
                  'approval':1
                  }
            emp_attendence_obj.create(cr,uid,{'employee_id':audit.employee_id.id,
                                              'employee_category_id':audit.employee_id.employee_category_id and audit.employee_id.employee_category_id.id or False,
                                              'sub_category_id':audit.employee_id.employee_sub_category_id and audit.employee_id.employee_sub_category_id.id or False,
                                              'department_id':audit.employee_id.department_id and audit.employee_id.department_id.id or False,
                                              'designation_id':audit.employee_id.job_id and audit.employee_id.job_id.id or False,
                                              'punch_in_out_audit':[(0,0,val1)]})
        self.pool.get('arul.hr.audit.shift.time').write(cr, uid, [audit_id],{'approval': True, 'state':'done', 'time_evaluate_id':False})
        return {'type': 'ir.actions.act_window_close'}
alert_form()

class time_leave_evalv(osv.osv_memory):
    _name = "time.leave.evalv" 
    _columns = {    
                #'type': fields.selection(WARNING_TYPES, string='Type', readonly=True),
                #'title': fields.char(string="Title", size=100, readonly=True),
                #'message': fields.text(string="Message ", readonly=True),    
                'from_date':fields.date('From Date', ),
                'to_date':fields.date('To Date', ),
                }
    #===========================================================================
    # def submit_btn(self, cr, uid, ids, context=None):
    #     shift_change_ids = context.get('active_ids')
    #     #self.pool.get('tpt.time.leave.evaluation').approve(cr, uid, shift_change_ids)
    #     return {'type': 'ir.actions.act_window_close'}
    #===========================================================================
    def submit_btn(self, cr, uid, ids, context=None):
        monthly_shift_obj = self.pool.get('arul.hr.monthly.shift.schedule')
        non_availability_obj = self.pool.get('tpt.non.availability')
        sub_id = context.get('time_id')
        time_evalv_obj = self.pool.get('time.leave.evalv')
        tl = self.browse(cr, uid, ids[0])
        from_date = tl.from_date
        to_date = tl.to_date 
        #raise osv.except_osv(_('Warning !'), _(to_date))
        from_day = int(from_date[8:10])
        to_day = int(to_date[8:10])
        
        #time_ids = self.pool.get('tpt.time.leave.evaluation').browse(cr, uid, sub_id)
        #time_obj = self.pool.get('tpt.time.leave.evaluation').browse(cr, uid, context=context)
        
        #year = audit.work_date[:4]
        #time_ids = time_obj.search(cr, uid, [('id','=',sub_id)])
        #for sub in self.pool.get('tpt.time.leave.evaluation').browse(cr, uid, sub_id,context=context):#time_ids: #self.browse(cr, uid, ids, context=context):
        sub = self.pool.get('tpt.time.leave.evaluation').browse(cr, uid, sub_id,context=context)
        ###
        sql = '''
                update arul_hr_audit_shift_time set time_evaluate_id = null where EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s and state = 'draft'
                and employee_id in (select id from hr_employee where payroll_area_id = %s)
                
            '''%(sub.year,sub.month,sub.payroll_area_id.id)
        cr.execute(sql)
        sql = '''
                update arul_hr_employee_leave_details set leave_evaluate_id = null where EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s and state = 'draft'
                and employee_id in (select id from hr_employee where payroll_area_id = %s)
                
            '''%(sub.year,sub.month,sub.payroll_area_id.id)
        cr.execute(sql)
            
        ###
        sql = '''
                update arul_hr_audit_shift_time set time_evaluate_id = %s where EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s and state = 'draft'
                and employee_id in (select id from hr_employee where payroll_area_id = %s)
                and EXTRACT(day FROM work_date) between %s and %s
            '''%(sub.id,sub.year,sub.month,sub.payroll_area_id.id,from_day,to_day)
        cr.execute(sql)
        sql = '''
                update arul_hr_employee_leave_details set leave_evaluate_id = %s where EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s and state = 'draft'
                and employee_id in (select id from hr_employee where payroll_area_id = %s)
                and EXTRACT(day FROM date_from) between %s and %s
            '''%(sub.id,sub.year,sub.month,sub.payroll_area_id.id,from_day,to_day)
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
                
                day_now = 31
                month_now = int(time.strftime('%m'))
                year_now = int(time.strftime('%Y'))
                if year_now == sub.year and month_now == int(sub.month):
                    day_now = int(time.strftime('%d'))
                if year_now >= sub.year: 
                    ###
                    d1 = datetime.date(int(sub.year), int(sub.month), from_day)
                    d2 = datetime.date(int(sub.year), int(sub.month), to_day)
                    
                    delta = d2 - d1
                    
                    time_var1 = False
                    time_var2 = False
                    time_var3 = False
                    time_var4 = False
                    time_var5 = False
                    time_var6 = False
                    time_var7 = False
                    time_var8 = False
                    time_var9 = False
                    time_var10 = False
                    time_var11 = False
                    time_var12 = False
                    time_var13 = False
                    time_var14 = False
                    time_var15 = False
                    time_var16 = False
                    time_var17 = False
                    time_var18 = False
                    time_var19 = False
                    time_var20 = False
                    time_var21 = False
                    time_var22 = False
                    time_var23 = False
                    time_var24 = False
                    time_var25 = False
                    time_var26 = False
                    time_var27 = False
                    time_var28 = False
                    time_var29 = False
                    time_var30 = False
                    time_var31 = False
                    
                    for i in range(delta.days + 1):
                        temp_day = d1 + timedelta(days=i) 
                        day = str(temp_day)[8:10]  
                        day = int(day)
                        if day==1:
                            time_var1 = True
                        if day==2:
                            time_var2 = True
                        if day==3:
                            time_var3 = True
                        if day==4:
                            time_var4 = True
                        if day==5:
                            time_var5 = True
                        if day==6:
                            time_var6 = True
                        if day==7:
                            time_var7 = True
                        if day==8:
                            time_var8 = True
                        if day==9:
                            time_var9 = True
                        if day==10:
                            time_var10 = True
                        if day==11:
                            time_var11 = True
                        if day==12:
                            time_var12 = True
                        if day==13:
                            time_var13 = True
                        if day==14:
                            time_var14 = True
                        if day==15:
                            time_var15 = True
                        if day==16:
                            time_var16 = True
                        if day==17:
                            time_var17 = True
                        if day==18:
                            time_var18 = True
                        if day==19:
                            time_var19 = True
                        if day==20:
                            time_var20 = True
                        if day==21:
                            time_var21 = True
                        if day==22:
                            time_var22 = True
                        if day==23:
                            time_var23 = True
                        if day==24:
                            time_var24 = True
                        if day==25:
                            time_var25 = True
                        if day==26:
                            time_var26 = True
                        if day==27:
                            time_var27 = True
                        if day==28:
                            time_var28 = True
                        if day==29:
                            time_var29 = True
                        if day==30:
                            time_var30 = True
                        if day==31:
                            time_var31 = True
                    ###     
                    ### ###TPT-By BalamuruganPurushothaman  on 29/09/2015 - to handle DOJ in Time Leave Evaluation
                    sql = '''
                    select extract(day from date_of_joining) doj from hr_employee where extract(year from date_of_joining)= %s and 
                      extract(month from date_of_joining)= %s and id=%s
                    '''%(sub.year,sub.month,emp_id)
                    cr.execute(sql)
                    new_doj = cr.fetchone()
                    if new_doj:
                        day = new_doj[0]
                        day -=  1
                        day = int(day)
                        for i in range(day):
                            day = i
                            if day==0:
                                time_var1 = False
                            if day==1:
                                time_var2 = False
                            if day==2:
                                time_var3 = False
                            if day==3:
                                time_var4 = False
                            if day==4:
                                time_var5 = False
                            if day==5:
                                time_var6 = False
                            if day==6:
                                time_var7 = False
                            if day==7:
                                time_var8 = False
                            if day==8:
                                time_var9 = False
                            if day==9:
                                time_var10 = False
                            if day==10:
                                time_var11 = False
                            if day==11:
                                time_var12 = False
                            if day==12:
                                time_var13 = False
                            if day==13:
                                time_var14 = False
                            if day==14:
                                time_var15 = False
                            if day==15:
                                time_var16 = False
                            if day==16:
                                time_var17 = False
                            if day==17:
                                time_var18 = False
                            if day==18:
                                time_var19 = False
                            if day==19:
                                time_var20 = False
                            if day==20:
                                time_var21 = False
                            if day==21:
                                time_var22 = False
                            if day==22:
                                time_var23 = False
                            if day==23:
                                time_var24 = False
                            if day==24:
                                time_var25 = False
                            if day==25:
                                time_var26 = False
                            if day==26:
                                time_var27 = False
                            if day==27:
                                time_var28 = False
                            if day==28:
                                time_var29 = False
                            if day==29:
                                time_var30 = False
                            if day==30:
                                time_var31 = False
                    ###    
                    if shift.day_1 and shift.day_1.code != 'W' and day_now>=1 and 1.0 not in holiday_days and time_var1 is True:
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
                    if shift.day_2 and shift.day_2.code != 'W' and day_now>=2 and 2.0 not in holiday_days and time_var2 is True:
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
                    if shift.day_3 and shift.day_3.code != 'W' and day_now>=3 and 3.0 not in holiday_days and time_var3 is True:
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
                    if shift.day_4 and shift.day_4.code != 'W' and day_now>=4 and 4.0 not in holiday_days and time_var4 is True:
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
                    if shift.day_5 and shift.day_5.code != 'W' and day_now>=5 and 5.0 not in holiday_days and time_var5 is True:
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
                    if shift.day_6 and shift.day_6.code != 'W' and day_now>=6 and 6.0 not in holiday_days and time_var6 is True:
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
                    if shift.day_7 and shift.day_7.code != 'W' and day_now>=7 and 7.0 not in holiday_days and time_var7 is True:
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
                    if shift.day_8 and shift.day_8.code != 'W' and day_now>=8 and 8.0 not in holiday_days and time_var8 is True:
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
                    if shift.day_9 and shift.day_9.code != 'W' and day_now>=9 and 9.0 not in holiday_days and time_var9 is True:
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
                    if shift.day_10 and shift.day_10.code != 'W' and day_now>=10 and 10.0 not in holiday_days and time_var10:
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
                    if shift.day_11 and shift.day_11.code != 'W' and day_now>=11 and 11.0 not in holiday_days and time_var11:
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
                    if shift.day_12 and shift.day_12.code != 'W' and day_now>=12 and 12.0 not in holiday_days and time_var12:
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
                    if shift.day_13 and shift.day_13.code != 'W' and day_now>=13 and 13.0 not in holiday_days and time_var13:
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
                    if shift.day_14 and shift.day_14.code != 'W' and day_now>=14 and 14.0 not in holiday_days and time_var14:
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
                    if shift.day_15 and shift.day_15.code != 'W' and day_now>=15 and 15.0 not in holiday_days and time_var15:
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
                    if shift.day_16 and shift.day_16.code != 'W' and day_now>=16 and 16.0 not in holiday_days and time_var16:
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
                    if shift.day_17 and shift.day_17.code != 'W' and day_now>=17 and 17.0 not in holiday_days and time_var17:
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
                    if shift.day_18 and shift.day_18.code != 'W' and day_now>=18 and 18.0 not in holiday_days and time_var18:
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
                    if shift.day_19 and shift.day_19.code != 'W' and day_now>=19 and 19.0 not in holiday_days and time_var19:
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
                    if shift.day_20 and shift.day_20.code != 'W' and day_now>=20 and 20.0 not in holiday_days and time_var20:
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
                    if shift.day_21 and shift.day_21.code != 'W' and day_now>=21 and 21.0 not in holiday_days and time_var21:
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
                    if shift.day_22 and shift.day_22.code != 'W' and day_now>=22 and 22.0 not in holiday_days and time_var22:
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
                    if shift.day_23 and shift.day_23.code != 'W' and day_now>=23 and 23.0 not in holiday_days and time_var23:
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
                    if shift.day_24 and shift.day_24.code != 'W' and day_now>=24 and 24.0 not in holiday_days and time_var24:
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
                    if shift.day_25 and shift.day_25.code != 'W' and day_now>=25 and 25.0 not in holiday_days and time_var25:
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
                    if shift.day_26 and shift.day_26.code != 'W' and day_now>=26 and 26.0 not in holiday_days and time_var26:
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
                    if shift.day_27 and shift.day_27.code != 'W' and day_now>=27 and 27.0 not in holiday_days and time_var27:
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
                    if shift.day_28 and shift.day_28.code != 'W' and day_now>=28 and 28.0 not in holiday_days and time_var28:
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
                    if shift.day_29 and shift.day_29.code != 'W' and shift.num_of_month>=29 and day_now>=29 and 29.0 not in holiday_days and time_var29:
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
                    if shift.day_30 and shift.day_30.code != 'W' and shift.num_of_month>=30 and day_now>=30 and 30.0 not in holiday_days and time_var30:
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
                    if shift.day_31 and shift.day_31.code != 'W' and shift.num_of_month>=31 and day_now>=31 and 31.0 not in holiday_days and time_var31:
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
    
    
time_leave_evalv() 