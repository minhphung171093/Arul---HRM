# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class lwf_deduction_wizard(osv.osv_memory):
    _name = "lwf.deduction.wizard"
    
    _columns = {
            'year': fields.selection([(num, str(num)) for num in range(2000, 2060)], 'Year'),
            'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month'),
            'category_id': fields.many2one('vsis.hr.employee.category', 'Employee Category'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        report_obj = self.pool.get('lwf.deduction.screen')
        emp_obj = self.pool.get('hr.employee')
        
        this = self.browse(cr, uid, ids[0])
        screen_line = []
        sql = '''
            select
                emp.id as id, emp.employee_id as code, rr.name as name, emp.last_name as last_name
            
            from
                arul_hr_payroll_executions_details ped
                left join arul_hr_payroll_executions pe on ped.payroll_executions_id = pe.id
                left join hr_employee emp on ped.employee_id = emp.id
                left join resource_resource rr on emp.resource_id = rr.id
            where pe.state != 'draft' 
        '''
        if this.month:
            sql += '''
                and pe.month='%s'
            '''%(this.month)
        if this.year:
            sql += '''
                and pe.year=%s
            '''%(this.year)
        if this.category_id:
            sql += '''
                and emp.employee_category_id=%s
            '''%(this.category_id.id)
        sql += '''
            group by emp.id, emp.employee_id, rr.name, emp.last_name
        '''
        cr.execute(sql)
#         for seq,line in enumerate(cr.dictfetchall()):
        for seq,line in enumerate([{'id': 1, 'code': '1234', 'name': 'Admin', 'last_name': 'T'}]):
            emp = emp_obj.browse(cr, uid, line['id'])
            employee_share = 0
            employer_share = 0
            if emp.employee_category_id and emp.employee_sub_category_id:
                sql = '''
                    select id, emp_lwf_amt, employer_lwf_con_amt
                        from arul_hr_payroll_contribution_parameters
                        where employee_category_id=%s and sub_category_id=%s limit 1
                '''%(emp.employee_category_id.id, emp.employee_sub_category_id.id)
                cr.execute(sql)
                contribution_parameters = cr.dictfetchone()
                if contribution_parameters:
                    employee_share = contribution_parameters['emp_lwf_amt']
                    employer_share = contribution_parameters['employer_lwf_con_amt']
                    print 'PHUNG1', employee_share, employer_share
                if this.year:
                    sql = '''
                        select id, emp_lwf_amt, employer_lwf_con_amt
                            from arul_hr_payroll_contribution_parameters_history
                            where contribution_parameters_id in (select id
                                from arul_hr_payroll_contribution_parameters
                                where employee_category_id=%s and sub_category_id=%s limit 1
                            ) and to_char(date, 'YYYY')='%s' 
                    '''%(emp.employee_category_id.id, emp.employee_sub_category_id.id,this.year)
                    if this.month:
                        sql += '''
                             and to_char(date, 'MM')='%s'
                        '''%(this.month)
                    sql += '''
                         order by date desc, id desc limit 1
                    '''
                    cr.execute(sql)
                    contribution_parameters = cr.dictfetchone()
                    if contribution_parameters:
                        employee_share = contribution_parameters['emp_lwf_amt']
                        employer_share = contribution_parameters['employer_lwf_con_amt']
                        print 'PHUNG2', employee_share, employer_share
            screen_line.append((0,0,{
                'sequence': seq+1,
                'emp_code': line['code'],
                'emp_name': line['name']+' '+line['last_name'],
                'employee_share': employee_share,
                'employer_share': employer_share,
            }))
        vals = {
            'name': '',
            'screen_line': screen_line,
            'year': this.year,
        }
        
        report_id = report_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_report', 'view_lwf_deduction_screen')
        return {
            'name': 'LWF Deduction Report',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'lwf.deduction.screen',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'view_id': res and res[1] or False,
            'res_id': report_id,
        }
        
lwf_deduction_wizard()

class lwf_deduction_screen(osv.osv_memory):
    _name = "lwf.deduction.screen"
    
    _columns = {
        'name': fields.char('Name', size=1024),
        'year': fields.selection([(num, str(num)) for num in range(2000, 2060)], 'Year'),
        'screen_line': fields.one2many('lwf.deduction.screen.line', 'screen_id', 'Line'),
    }
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'lwf.deduction.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'lwf_deduction_report_xls', 'datas': datas}
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'lwf.deduction.screen'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'lwf_deduction_report_pdf', 'datas': datas}
        
lwf_deduction_screen()

class lwf_deduction_screen_line(osv.osv_memory):
    _name = "lwf.deduction.screen.line"
    
    _columns = {
        'screen_id': fields.many2one('lwf.deduction.screen', 'Screen', ondelete='cascade'),
        'sequence': fields.integer('SI.No'),
        'emp_code': fields.char('EMP. CODE', size=1024),
        'emp_name': fields.char('NAME', size=1024),
        'employee_share': fields.float("EMPLOYEE'S SHARE"),
        'employer_share': fields.float("EMPLOYER'S SHARE"),
    }
        
lwf_deduction_screen_line()
