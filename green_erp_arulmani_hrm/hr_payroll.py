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
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_code_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            payroll_name_ids = self.search(cr, uid, [('id','!=',payroll.id),('name','=',payroll.name)])
            if payroll_code_ids or payroll_name_ids:  
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
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
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
        'code': fields.char('Code', size=1024, required = True),
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
         'payroll_earning_structure_line':fields.one2many('arul.hr.payroll.earning.structure','earning_structure_id','Structure line'),
         'payroll_other_deductions_line':fields.one2many('arul.hr.payroll.other.deductions','earning_structure_id','Structure line'),
    }
    def onchange_employee_structure_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        configuration_obj = self.pool.get('arul.hr.payroll.structure.configuration')
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            configuration_ids = configuration_obj.search(cr, uid, [('employee_category_id','=',emp.employee_category_id.id),('sub_category_id','=',emp.employee_sub_category_id.id)])
            payroll_earning_structure_line = []
            if configuration_ids:
                configuration = configuration_obj.browse(cr, uid, configuration_ids[0])
                for line in configuration.payroll_structure_configuration_line:
                    
                    vals={
                          'earning_parameters_id':line.earning_parameters_id.id,
                          'float': line.value,
                    }
                    payroll_earning_structure_line.append((0,0,vals))
            vals = {'employee_category_id':emp.employee_category_id.id,
                    'sub_category_id':emp.employee_sub_category_id.id,
                    'payroll_earning_structure_line':payroll_earning_structure_line}
        return {'value': vals}

    
arul_hr_payroll_employee_structure()

class arul_hr_payroll_earning_structure(osv.osv):
    _name = 'arul.hr.payroll.earning.structure'
    _columns = {
         'earning_parameters_id': fields.many2one('arul.hr.payroll.earning.parameters','Earning Parameters',required = False),
         'earning_structure_id':fields.many2one('arul.hr.payroll.employee.structure','Earning Structure'), 
         'float':fields.float('Float') ,
         'executions_details_id':fields.many2one('arul.hr.payroll.executions.details','Execution Details'),
    }
    
arul_hr_payroll_earning_structure()

class arul_hr_payroll_contribution_parameters(osv.osv):
    _name = 'arul.hr.payroll.contribution.parameters'
    _columns = {
        'emp_pf_con': fields.float('Employee PF Contribution (%)'),
        'employer_pension_con': fields.float('Employer Pension Contribution (%)'),
        'pension_limit_amt': fields.float('Pension Limit Amt'),
        'emp_esi_limit': fields.float('Employee ESI Limit (%)'),
        'emp_esi_con': fields.float('Employee ESI Contribution (%)'),
        'employer_esi_con': fields.float('Employer ESI Contribution (%)'),
        'emp_lwf_amt': fields.float('Employee Labor Welfare Fund (LWF) Amt'),
        'employer_lwf_con_amt': fields.float('Employer LWF Contribution Amt'),
    }
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
    
arul_hr_payroll_structure_configuration()

class arul_hr_payroll_earning_structure_configuration(osv.osv):
    _name = 'arul.hr.payroll.earning.structure.configuration'
    _columns = {
         'earning_parameters_id': fields.many2one('arul.hr.payroll.earning.parameters','Earning Parameters',required = True),
         'earning_structure_configuration_id':fields.many2one('arul.hr.payroll.structure.configuration','Earning Structure'), 
         'fixed_percentage':fields.selection([('fixed','Fixed'),('percentage','Percentage')], 'Fixed/Percentage?',required = True) ,
         'value':fields.float('Values'),
    }
    
arul_hr_payroll_earning_structure_configuration()

class arul_hr_payroll_other_deductions(osv.osv):
    _name = 'arul.hr.payroll.other.deductions'
    _columns = {
         'deduction_parameters_id': fields.many2one('arul.hr.payroll.deduction.parameters','Deduction Parameters',required = True),
         'earning_structure_id':fields.many2one('arul.hr.payroll.employee.structure','Earning Structure'), 
         'float':fields.float('Float') ,
    }
    
arul_hr_payroll_other_deductions()


class arul_hr_payroll_executions(osv.osv):
    _name = 'arul.hr.payroll.executions'
    _columns = {
         'payroll_area_id': fields.many2one('arul.hr.payroll.area','Payroll Area',required = True),
         'year': fields.char('Year', size = 1024,required = True),
         'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
         'payroll_executions_details_line': fields.one2many('arul.hr.payroll.executions.details','payroll_executions_id','Details Line'),
    }
    
arul_hr_payroll_executions()

class arul_hr_payroll_executions_details(osv.osv):
    _name = 'arul.hr.payroll.executions.details'
    _columns = {
        'company_id': fields.many2one('res.company','Company'),
        'payroll_area_id': fields.many2one('arul.hr.payroll.area', 'Payroll Area'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area', 'Payroll Sub Area'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'designation_id': fields.many2one('arul.hr.designation', 'Designation'),
        'year': fields.char('Year', size = 1024),
        'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month'),
        'payroll_executions_id':fields.many2one('arul.hr.payroll.executions', 'Payroll Executions'),
        'earning_structure_line':fields.one2many('arul.hr.payroll.earning.structure','executions_details_id', 'Earing Structure'),
    }
    
arul_hr_payroll_executions_details()
