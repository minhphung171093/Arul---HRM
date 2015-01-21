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
        if employee_ids:
            val2={'punch_in_out_id':employee_ids[0], 
                  'employee_id': audit.employee_id.id,
                  'work_date':audit.work_date, 
                  'planned_work_shift_id':audit.planned_work_shift_id.id,
                  'actual_work_shift_id':audit.actual_work_shift_id.id,
                  'in_time':audit.in_time,
                  'out_time':audit.out_time,
                  'approval':1
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