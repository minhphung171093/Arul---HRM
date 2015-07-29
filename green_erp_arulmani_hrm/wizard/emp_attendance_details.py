# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_emp_attendance(osv.osv_memory):
    _name = "tpt.emp.attendance"
    _columns = {
        'name': fields.char('Emp Attn No', readonly=True),
        'attn_line_id': fields.one2many('emp.attendance.line', 'header_id', 'Punch'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'employee_id': fields.many2one('hr.employee', 'Employee',ondelete='restrict'),
        'employee_categ_id': fields.many2one('vsis.hr.employee.category', 'Employee Category'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.emp.attendance'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_emp_attn_xls', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.emp.attendance'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_emp_attn', 'datas': datas}
    
tpt_emp_attendance()

class emp_attendance_line(osv.osv_memory):
    _name = "emp.attendance.line"
    _columns = {
        'header_id': fields.many2one('tpt.emp.attendance', 'Emp Attn Header', ondelete='cascade'),
        'employee_id': fields.char('Employee ID', size = 1024),
        'work_date': fields.date('Work Date'), 
        'a_shift_count': fields.float('A'),
        'g1_shift_count': fields.float('G1'),
        'g2_shift_count': fields.float('G2'),
        'b_shift_count': fields.float('B'),
        'c_shift_count': fields.float('C'),
        'total_shift_worked': fields.float('Total'),
        'sub_total': fields.char('', size = 1024),
        
    }

emp_attendance_line()

class emp_attendance_details(osv.osv_memory):
    _name = "emp.attendance.details"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'employee_id': fields.many2one('hr.employee', 'Employee',ondelete='restrict'),
                'employee_categ_id': fields.many2one('vsis.hr.employee.category', 'Employee Category'),
                }
    
    
    def print_report(self, cr, uid, ids, context=None):
        
        def get_move_ids(o):
            account_voucher_obj = self.pool.get('arul.hr.punch.in.out.time')
            move_lines = []
            date_arr = []
            date_from = o.date_from
            date_to = o.date_to
            emp_id = o.employee_id
            emp_categ = o.employee_categ_id
            
            sql = '''
            select emp.employee_id,io.work_date 
                            from arul_hr_punch_in_out_time io
                            inner join hr_employee emp on io.employee_id=emp.id
                            where io.work_date between %s and %s
                            and io.employee_id=%s
            '''%(date_from, date_to, emp_id)
            
            cr.execute(sql)
            res = cr.dictfetchall()
            return res
                    
            #return []    
        ###
        cr.execute('delete from tpt_emp_attendance')
        cb_obj = self.pool.get('tpt.emp.attendance')
        cb = self.browse(cr, uid, ids[0])
        attn_line = []
        attn_line.append((0,0,{
            #'voucher_id': False,
            #'opening_balance': 'Opening Balance:',
            #'debit': get_opening_balance(cb),

        }))
        for seq, line in enumerate(get_move_ids(cb)):
            attn_line.append((0,0,{
            'date': line.move_id and line.move_id.date or '',
                'employee_id': line.employee_id and line.employee_id.employee_id or '',    
                'work_date': line.work_date or '',  
                'a_shift_count': line.a_shift_count1 or '',  
                'g1_shift_count': line.g1_shift_count1 or '',  
                'g2_shift_count': line.g2_shift_count1 or '',  
                'b_shift_count': line.b_shift_count1 or '',  
                'c_shift_count': line.c_shift_count1 or '',  
                'total_shift_worked': line.total_shift_worked1 or '',  
                'sub_total': 'Days Total',
                
            }))
        attn_line.append((0,0,{
            #'voucher_id': False,
            'sub_total': 'Days Total',
            
            'date':False,
            'desc':False,
        }))
        vals = {
            'name': 'Emp Attn Details for the Period: ',
            'attn_line_id': attn_line,
            'date_from': cb.date_from,
            'date_to': cb.date_to,

        }
        attn_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_hrm', 'view_tpt_emp_attn_form')
        
        return {
                    'name': 'Emp Attn Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.emp.attendance',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': attn_id,
                }

emp_attendance_details()