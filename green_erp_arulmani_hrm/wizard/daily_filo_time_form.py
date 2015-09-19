# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class daily_filo_time(osv.osv_memory):
    _name = "daily.filo.time"
    
    _columns = {
            'name': fields.char('SI.No', readonly=True),            
            'date_to':fields.date('Date To', required=True),            
            'employee_category_id': fields.many2one('vsis.hr.employee.category', 'Employee Category'),
            #'employee_category': fields.one2many('vsis.hr.employee.category', 'Employee Category'),            
            'department_id': fields.many2one('hr.department', 'Department'),
            'dailyfilo_line': fields.one2many('tpt.daily.filo.time.line', 'dailyfilo_id', 'Daily Filo Time Line'),
            'emp_categ_name':fields.char('Employee Category',size=1024),
            'dept_name':fields.char('Employee Category',size=1024),
    }
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'daily.filo.time'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daily_filo_time_pdf', 'datas': datas}
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'daily.filo.time'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daily_filo_time_xls', 'datas': datas}
    
    
    #===========================================================================
    # def print_report(self, cr, uid, ids, context=None):
    #     if context is None:
    #         context = {}
    #     datas = {'ids': context.get('active_ids', [])}
    #     datas['model'] = 'daily.filo.time'
    #     datas['form'] = self.read(cr, uid, ids)[0]
    #     datas['form'].update({'active_id':context.get('active_ids',False)})
    #     return {'type': 'ir.actions.report.xml', 'report_name': 'daily_filo_time', 'datas': datas}
    #===========================================================================
        
daily_filo_time()

class tpt_daily_filo_time_line(osv.osv_memory):
    _name = "tpt.daily.filo.time.line"
    _columns = {
        'dailyfilo_id': fields.many2one('daily.filo.time','Daily Filo Time'),
        'emp_code': fields.char('Employee Code', size = 1024),        
        'emp_name': fields.char('Employee Name', size = 1024),
        'desgn': fields.char('Designation', size = 1024),
        'dept': fields.char('Department', size = 1024),
        'emp_cat': fields.char('Employee Category', size = 1024),
        'in_time': fields.char('In Time', size = 1024),
        'out_time': fields.char('Out Time', size = 1024),
        'work_day': fields.date('Work Date'),  
        'seq_no': fields.float('Seq'), 
 }
tpt_daily_filo_time_line()

class tpt_daily_filo_time(osv.osv_memory):
    _name = "tpt.daily.filo.time"
    _columns = {    
                'employee_category_ids': fields.many2many('vsis.hr.employee.category', 'tpt_template', 'dailyfilo_id', 'employee_category_id', 'Employee Category'),            
                'department_ids': fields.many2many('hr.department', 'tpt_template_new', 'dailyfilo_id', 'department_id', 'Department'),                
                'date_to': fields.date('Date', required=True),
                'dailyfilo_id': fields.many2one('daily.filo.time','Daily Filo Time'),
                }    
   
    
    def print_report(self, cr, uid, ids, context=None):
        
        def get_time_in_out(date,emp_cat,dept,type):
            
            sql = '''
                    select min(hst.in_time) as intime,max(hst.out_time) as outtime from arul_hr_audit_shift_time hst
                    inner join hr_employee hr on (hr.id = hst.employee_id)
                    where hst.work_date = '%s'
                '''%(date)
            if emp_cat:
               qstr = " and hr.employee_category_id in (%s)"%(emp_cat)
               sql = sql+qstr
            if dept:
               qstr = " and hr.department_id in (%s)"%(dept)
               sql = sql+qstr 
            cr.execute(sql)
            for move in cr.dictfetchall():
                if type == 'in_time':
                    in_time = move['intime']
                    return in_time or 0
                if type == 'out_time':
                    out_time = move['outtime']
                    return out_time or 0
        
        def convert_date(date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
            
        def get_invoice(cb):
            res = {}            
            date_to = cb.date_to            
            department_ids = ''
            department_ids = [r.id for r in cb.department_ids]
            department_ids = str(department_ids).replace("[", "")
            department_ids = department_ids.replace("]", "")
                  
            emp_category_ids = ''
            emp_category_ids = [r.id for r in cb.employee_category_ids]
            emp_category_ids = str(emp_category_ids).replace("[", "")
            emp_category_ids = emp_category_ids.replace("]", "")
            
            
            sql = '''
                select distinct hr.employee_id as emp_code,hr.name_related as emp_name,
                j.name as desgn,d.name as dept,hst.work_date as work_date,hr.employee_category_id as emp_categ_id,hr.department_id as dept_id,
                (select name from vsis_hr_employee_category where id=hr.employee_category_id) emp_cat,
                hst.in_time, hst.out_time
                from arul_hr_punch_in_out_time hst
                inner join hr_employee hr on (hr.id = hst.employee_id)
                inner join hr_department d on (d.id = hr.department_id)
                inner join hr_job j on (j.id = hr.job_id)
                where hst.work_date = '%s'
                '''%(date_to)
            if emp_category_ids:
               qstr = " and hr.employee_category_id in (%s)"%(emp_category_ids)
               sql = sql+qstr
            if department_ids:
               qstr = " and hr.department_id in (%s)"%(department_ids)
               sql = sql+qstr        
            sql=sql+" order by hr.employee_id,hr.name_related"
            cr.execute(sql)
            return cr.dictfetchall()
       
        cr.execute('delete from daily_filo_time')
        sls_obj = self.pool.get('daily.filo.time')
        sls = self.browse(cr, uid, ids[0])
        sls_line = []
        seq_no = 1
        for line in get_invoice(sls):
            sls_line.append((0,0,{
                'seq_no': seq_no,     
                'emp_code': line['emp_code'],                  
                'emp_name': line['emp_name'],                
                'desgn': line['desgn'],
                'dept': line['dept'],
                'emp_cat': line['emp_cat'],
                'in_time':  line['in_time'], #get_time_in_out(line['work_date'],line['emp_categ_id'],line['dept_id'],'in_time') or 0,  #line['in_time'],
                'out_time':  line['out_time'], #get_time_in_out(line['work_date'],line['emp_categ_id'],line['dept_id'],'out_time') or 0, #line['out_time'],
                'work_day': line['work_date'],
               
            }))
            seq_no = seq_no + 1
            
        emp_cate_name = ''
        name_ids = [r.name for r in sls.employee_category_ids]
        for name in name_ids:
            emp_cate_name += name + ', '
            
        dept_name = ''
        dept_name_ids = [r.name for r in sls.department_ids]
        for name in dept_name_ids:
            dept_name += name + ', '
        vals = {
                'name': 'Daily First IN and Last OUT Time Report',
                'date_to': sls.date_to,
                #'employee_category_id':  sls.employee_category.id or False,
                'emp_categ_name': sls.employee_category_ids and emp_cate_name or 'All' ,
                #'department': sls.department.id or False, 
                'dept_name': sls.department_ids and dept_name or 'All',                 
                'dailyfilo_line': sls_line,
            }
        
        sls_id = sls_obj.create(cr, uid, vals)               
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_hrm', 'view_daily_filo_time')
        
        return {
                        'name': 'Daily First IN and Last OUT Time Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'daily.filo.time',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': sls_id,
                }
        #
        #cr.execute('delete from daily_filo_time')
        
        
        #new_write = super(tpt_daily_filo_time, self).write(cr, uid, ids, vals, context)
        
        
tpt_daily_filo_time()

