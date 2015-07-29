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
            account_voucher_obj = self.pool.get('account.voucher')
            move_lines = []
            date_arr = []
            date_from = o.date_from
            date_to = o.date_to
            emp = o.employee_id
            emp_categ = o.employee_categ_id
            return []    
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
                
                
            }))
        attn_line.append((0,0,{
            'voucher_id': False,
            'opening_balance': 'Days Total',
            
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