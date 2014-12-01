# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime



class arul_hr_payroll_area(osv.osv):
    _name = 'arul.hr.payroll.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(arul_hr_payroll_area, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(arul_hr_payroll_area, self).write(cr, uid,ids, vals, context)

    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_hr_payroll_area where id != %s and lower(code) = lower('%s')
            '''%(payroll.id,payroll.code)
            cr.execute(sql)
            payroll_ids = [row[0] for row in cr.fetchall()]
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]

    
arul_hr_payroll_area()

class arul_hr_payroll_sub_area(osv.osv):
    _name = 'arul.hr.payroll.sub.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_hr_payroll_sub_area, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_hr_payroll_sub_area, self).write(cr, uid,ids, vals, context)
    
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_hr_payroll_sub_area where id != %s and lower(code) = lower('%s')
            '''%(payroll.id,payroll.code)
            cr.execute(sql)
            payroll_ids = [row[0] for row in cr.fetchall()]
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
    
arul_hr_payroll_sub_area()

class arul_hr_payroll_earning_parameters(osv.osv):
    _name = 'arul.hr.payroll.earning.parameters'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
         'description':fields.text('Description')
        
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_code_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            payroll_name_ids = self.search(cr, uid, [('id','!=',payroll.id),('name','=',payroll.name)])
            if payroll_code_ids or payroll_name_ids:
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]  

arul_hr_payroll_earning_parameters()

class arul_hr_payroll_deduction_parameters(osv.osv):
    _name = 'arul.hr.payroll.deduction.parameters'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
        'code': fields.char('Code', size=1024, equired = True),
        'description': fields.text('Description'),
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
    
arul_hr_payroll_deduction_parameters()

class arul_hr_payroll_employee_structure(osv.osv):
    _name = 'arul.hr.payroll.employee.structure'
    _columns = {
         'employee_id': fields.many2one('hr.employee','Employee ID',required = True),
         'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Group'),
         'sub_category_id':fields.many2one('hr.employee.sub.category','Employee Sub Group'), 
         'ins_de_period_start':fields.date('Insurance Deduction Period'),
         'ins_de_period_end':fields.date('Insurance Deduction Period'),
         'loan_de_period_start':fields.date('Loan Deductions Period'),
         'loan_de_period_end':fields.date('Loan Deductions Period'),
         'payroll_earning_structure_line':fields.one2many('arul.hr.payroll.earning.structure','earning_structure_id','Structure line' ),
         'payroll_other_deductions_line':fields.one2many('arul.hr.payroll.other.deductions','earning_structure_id','Structure line'),
    }
    def onchange_employee_structure_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        configuration_obj = self.pool.get('arul.hr.payroll.structure.configuration')
        if employee_id:
            earning_obj = self.pool.get('arul.hr.payroll.earning.structure')
            earning_ids = earning_obj.search(cr, uid, [('earning_structure_id','in',ids)])
            earning_obj.unlink(cr, uid, earning_ids)
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            configuration_ids = configuration_obj.search(cr, uid, [('employee_category_id','=',emp.employee_category_id.id),('sub_category_id','=',emp.employee_sub_category_id.id)])
            payroll_earning_structure_line = []
            if configuration_ids:
                configuration = configuration_obj.browse(cr, uid, configuration_ids[0])
                base_amount = 0
                for line in configuration.payroll_structure_configuration_line:
                    if line.earning_parameters_id.code=='BASIC':
                        base_amount = line.value
                        break
                for line in configuration.payroll_structure_configuration_line:
                    if line.fixed_percentage=='fixed':
                        vals={
                              'earning_parameters_id':line.earning_parameters_id.id,
                              'float': line.value,
                        }
                        payroll_earning_structure_line.append((0,0,vals))
                    if line.fixed_percentage=='percentage':
                        vals={
                              'earning_parameters_id':line.earning_parameters_id.id,
                              'float': line.value*base_amount/100,
                        }
                        payroll_earning_structure_line.append((0,0,vals))
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'payroll_earning_structure_line':payroll_earning_structure_line}
        return {'value': vals}

    def _check_employee_id(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('employee_id','=',employee.employee_id.id)])
            if employee_ids:  
                return False
        return True
    _constraints = [
        (_check_employee_id, 'Identical Data', ['employee_id']),
    ]

    def onchange_structure_line(self, cr, uid, ids,payroll_earning_structure_line=False,employee_category_id=False,sub_category_id=False, context=None):
        payroll_earning_structure = []
#         if employee_category_id and sub_category_id:
#             configuration_obj = self.pool.get('arul.hr.payroll.structure.configuration')
#             base_amount = 0
#             
#             for line in payroll_earning_structure_line:
#                 earning_parameter = self.pool.get('arul.hr.payroll.earning.parameters').browse(cr, uid, line[2]['earning_parameters_id'])
#                 if earning_parameter.code == 'BASIC':
#                     base_amount = line[2]['float']
#                     payroll_earning_structure.append((0,0,{'earning_parameters_id':line[2]['earning_parameters_id'],
#                               'float': base_amount,}))
#                     break
#             if payroll_earning_structure:
#                 for line in payroll_earning_structure_line:
#                     earning_parameters_id = line[2]['earning_parameters_id']
#                     earning_parameter = self.pool.get('arul.hr.payroll.earning.parameters').browse(cr, uid, earning_parameters_id)
#                     if earning_parameter.code != 'BASIC':
#                         configuration_ids = configuration_obj.search(cr, uid, [('employee_category_id','=',employee_category_id),('sub_category_id','=',sub_category_id)])
#                         if configuration_ids:
#                             configuration = configuration_obj.browse(cr, uid, configuration_ids[0])
#                             earning_parameters_id = line[2]['earning_parameters_id']
#                             for line2 in configuration.payroll_structure_configuration_line:
#                                 if line2.earning_parameters_id.id == earning_parameters_id:
#                                     if line2.fixed_percentage=='fixed':
#                                         vals={
#                                               'earning_parameters_id':earning_parameters_id,
#                                               'float': line[2]['float'],
#                                         }
#                                         payroll_earning_structure.append((0,0,vals))
#                                     if line2.fixed_percentage=='percentage':
#                                         vals={
#                                               'earning_parameters_id':earning_parameters_id,
#                                               'float': line2.value*base_amount/100,
#                                         }
#                                         payroll_earning_structure.append((0,0,vals))
#         return {'value':{'payroll_earning_structure_line':payroll_earning_structure}}
        return True
arul_hr_payroll_employee_structure()

class arul_hr_payroll_earning_structure(osv.osv):
    _name = 'arul.hr.payroll.earning.structure'
    _columns = {
         'earning_parameters_id': fields.many2one('arul.hr.payroll.earning.parameters','Earning Parameters', required = True),
         'earning_structure_id':fields.many2one('arul.hr.payroll.employee.structure','Earning Structure', ondelete='cascade'), 
         'float':fields.float('Float') ,
         'executions_details_id':fields.many2one('arul.hr.payroll.executions.details','Execution Details', ondelete='cascade'),
    }
    def onchange_structure_line(self, cr, uid, ids, context=None):
        configuration_obj = self.pool.get('arul.hr.payroll.structure.configuration')
        for line in self.browse(cr, uid, ids):
            if line.earning_parameters_id.code == 'BASIC' and line.earning_structure_id.employee_category_id and line.earning_structure_id.sub_category_id:
                earning_structure_ids = self.search(cr, uid, [('id','!=',line.id),('earning_structure_id','=',line.earning_structure_id.id)])
                configuration_ids = configuration_obj.search(cr, uid, [('employee_category_id','=',line.earning_structure_id.employee_category_id.id),('sub_category_id','=',line.earning_structure_id.sub_category_id.id)])
                if configuration_ids:
                    for earning_structure in self.browse(cr, uid, earning_structure_ids):
                        configuration = configuration_obj.browse(cr, uid, configuration_ids[0])
                        for line2 in configuration.payroll_structure_configuration_line:
                            if line2.earning_parameters_id.id == line.earning_parameters_id.id:
                                if line2.fixed_percentage=='percentage':
                                    self.write(cr, uid, [earning_structure.id],{'float':line.float*line2.value/100})
        return True
arul_hr_payroll_earning_structure()

class arul_hr_payroll_contribution_parameters(osv.osv):
    _name = 'arul.hr.payroll.contribution.parameters'
    _columns = {
        'sub_category_id':fields.many2one('hr.employee.sub.category','Employee Sub Group', required = True),
        'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Group', required = True),
        'emp_pf_con': fields.float('Employee PF Contribution (%)'),
        'employer_pension_con': fields.float('Employer Pension Contribution (%)'),
        'pension_limit_amt': fields.float('Pension Limit Amt'),
        'emp_esi_limit': fields.float('Employee ESI Limit (%)'),
        'emp_esi_con': fields.float('Employee ESI Contribution (%)'),
        'employer_esi_con': fields.float('Employer ESI Contribution (%)'),
        'emp_lwf_amt': fields.float('Employee Labor Welfare Fund (LWF) Amt'),
        'employer_lwf_con_amt': fields.float('Employer LWF Contribution Amt'),
        }
        
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
        emp_sub_cat = []
        if employee_category_id:
            emp_cat = self.pool.get('vsis.hr.employee.category').browse(cr, uid, employee_category_id)
            emp_sub_cat = [x.id for x in emp_cat.sub_category_ids]
        return {'value': {'sub_category_id': False }, 'domain':{'sub_category_id':[('id','in',emp_sub_cat)]}}
    
arul_hr_payroll_contribution_parameters()

class arul_hr_payroll_structure_configuration(osv.osv):
    _name = 'arul.hr.payroll.structure.configuration'
    _columns = {
         'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Group', required = True),
         'sub_category_id':fields.many2one('hr.employee.sub.category','Employee Sub Group'), 
         'payroll_structure_configuration_line':fields.one2many('arul.hr.payroll.earning.structure.configuration','earning_structure_configuration_id','Structure Configuration') ,   
    }
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
        emp_sub_cat = []
        if employee_category_id:
            emp_cat = self.pool.get('vsis.hr.employee.category').browse(cr, uid, employee_category_id)
            emp_sub_cat = [x.id for x in emp_cat.sub_category_ids]
        return {'value': {'sub_category_id': False }, 'domain':{'sub_category_id':[('id','in',emp_sub_cat)]}}
    
    def _check_category_sub_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_category_ids = self.search(cr, uid, [('id','!=',payroll.id),('employee_category_id','=',payroll.employee_category_id.id)])
            payroll_sub_ids = self.search(cr, uid, [('id','!=',payroll.id),('sub_category_id','=',payroll.sub_category_id.id)])
            if payroll_category_ids or payroll_sub_ids:
                return False
        return True
    _constraints = [
        (_check_category_sub_id, 'Identical Data', ['employee_category_id','sub_category_id']),
    ]  
    
arul_hr_payroll_structure_configuration()

class arul_hr_payroll_earning_structure_configuration(osv.osv):
    _name = 'arul.hr.payroll.earning.structure.configuration'
    _columns = {
         'earning_parameters_id': fields.many2one('arul.hr.payroll.earning.parameters','Earning Parameters',required = True),
         'earning_structure_configuration_id':fields.many2one('arul.hr.payroll.structure.configuration','Earning Structure', ondelete='cascade'), 
         'fixed_percentage':fields.selection([('fixed','Fixed'),('percentage','Percentage')], 'Fixed/Percentage?',required = True) ,
         'value':fields.float('Values'),
    }
    
arul_hr_payroll_earning_structure_configuration()

class arul_hr_payroll_other_deductions(osv.osv):
    _name = 'arul.hr.payroll.other.deductions'
    _columns = {
         
         'deduction_parameters_id': fields.many2one('arul.hr.payroll.deduction.parameters','Deduction Parameters',required = True),
         'earning_structure_id':fields.many2one('arul.hr.payroll.employee.structure','Earning Structure', ondelete='cascade'), 
         'float':fields.float('Float') ,
         'executions_details_id':fields.many2one('arul.hr.payroll.executions.details','Execution Details', ondelete='cascade'),
    }
    
arul_hr_payroll_other_deductions()


class arul_hr_payroll_executions(osv.osv):
    _name = 'arul.hr.payroll.executions'
    _columns = {
         'payroll_area_id': fields.many2one('arul.hr.payroll.area','Payroll Area',required = True),
         'year': fields.char('Year', size = 1024,required = True),
         'state': fields.selection([('draft', 'New'),('confirm', 'Confirmed'),('approve', 'Approved')],'Status'),
         'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
         'payroll_executions_details_line': fields.one2many('arul.hr.payroll.executions.details','payroll_executions_id','Details Line'),
    }
    def generate_payroll(self, cr, uid, ids, context=None):
        details_line = []
        for line in self.browse(cr,uid,ids):
            emp_obj = self.pool.get('hr.employee')
            payroll_emp_struc_obj = self.pool.get('arul.hr.payroll.employee.structure')
            executions_details_obj = self.pool.get('arul.hr.payroll.executions.details')
            earning_structure_obj = self.pool.get('arul.hr.payroll.earning.structure')
            other_deductions_obj = self.pool.get('arul.hr.payroll.other.deductions')
            employee_ids = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id)])
            for p in emp_obj.browse(cr,uid,employee_ids):
                payroll_executions_details_ids = executions_details_obj.search(cr, uid, [('payroll_executions_id', '=', line.id), ('employee_id', '<=', p.id)], context=context)
                if payroll_executions_details_ids:
                    executions_details_obj.unlink(cr, uid, payroll_executions_details_ids, context=context) 
                vals_earning_struc = []
                vals_other_deductions = []
                
                emp_struc_ids = payroll_emp_struc_obj.search(cr,uid,[('employee_id','=',p.id)])
                if emp_struc_ids:
                    for earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                        vals_earning_struc.append((0,0, {
#                                   'executions_details_id':executions_details_id,               
                                  'earning_parameters_id':earning_struc_id.earning_parameters_id.id,
                                  'float': earning_struc_id.float,
                            }))
#                         earning_structure_obj.create(cr,uid,vals_earning_struc)
                    
                    for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                        vals_other_deductions.append((0,0, {
#                                   'executions_details_id':executions_details_id,                    
                                  'deduction_parameters_id':other_deductions_id.deduction_parameters_id.id,
                                  'float': other_deductions_id.float,
                            }))
#                         other_deductions_obj.create(cr,uid,vals_other_deductions)
                rs = {
                        'payroll_executions_id': line.id,
                        'employee_id': p.id,
                        'department_id':p.department_id and p.department_id.id or False,
#                         'designation_id':p.department_id and (p.department_id.designation_id and p.department_id.designation_id.id or False) or False,
                        'year':line.year,
                        'month':line.month,
                        'company_id': p.company_id and p.company_id.id or False,
                        'payroll_area_id': line.payroll_area_id.id,
                        'payroll_sub_area_id': p.payroll_sub_area_id.id,
                        'earning_structure_line':vals_earning_struc,
                        'other_deduction_line':vals_other_deductions,
                      }
                executions_details_id = executions_details_obj.create(cr,uid,rs)
                
        return True
                    
    def confirm_payroll(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'})

    def rollback_payroll(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})
    
arul_hr_payroll_executions()

class arul_hr_payroll_executions_details(osv.osv):
    _name = 'arul.hr.payroll.executions.details'
    _columns = {
        'company_id': fields.many2one('res.company','Company'),
        'payroll_area_id': fields.many2one('arul.hr.payroll.area', 'Payroll Area'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area', 'Payroll Sub Area'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'designation_id': fields.many2one('hr.job', 'Designation'),
        'year': fields.char('Year', size = 1024),
        'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month'),
        'payroll_executions_id':fields.many2one('arul.hr.payroll.executions', 'Payroll Executions', ondelete='cascade'),
        'earning_structure_line':fields.one2many('arul.hr.payroll.earning.structure','executions_details_id', 'Earing Structure'),
        'other_deduction_line':fields.one2many('arul.hr.payroll.other.deductions','executions_details_id', 'Other Deduction'),
    }
    
arul_hr_payroll_executions_details()
