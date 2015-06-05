# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
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