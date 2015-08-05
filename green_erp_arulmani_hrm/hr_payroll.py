# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from datetime import date
import time
import datetime
import math
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp



class arul_hr_payroll_area(osv.osv):
    _name = 'arul.hr.payroll.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
        
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
                select id from arul_hr_payroll_area where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(payroll.id,payroll.code,payroll.name)
            cr.execute(sql)
            payroll_ids = [row[0] for row in cr.fetchall()]
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]

    
arul_hr_payroll_area()

class arul_hr_payroll_sub_area(osv.osv):
    _name = 'arul.hr.payroll.sub.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
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
                select id from arul_hr_payroll_sub_area where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(payroll.id,payroll.code,payroll.name)
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
        'name': fields.char('Name', size=1024, required = True ),
         'code': fields.char('Code', size=1024, required = True, readonly = True),
         'description':fields.text('Description')
        
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_hr_payroll_earning_parameters where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(payroll.id,payroll.code,payroll.name)
            cr.execute(sql)
            payroll_ids = [row[0] for row in cr.fetchall()]
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(arul_hr_payroll_earning_parameters, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(arul_hr_payroll_earning_parameters, self).write(cr, uid,ids, vals, context)

  

arul_hr_payroll_earning_parameters()

class arul_hr_payroll_deduction_parameters(osv.osv):
    _name = 'arul.hr.payroll.deduction.parameters'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
        'code': fields.char('Code', size=1024, required = True,readonly = True),
        'description': fields.text('Description'),
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_hr_payroll_deduction_parameters where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(payroll.id,payroll.code,payroll.name)
            cr.execute(sql)
            payroll_ids = [row[0] for row in cr.fetchall()]
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(arul_hr_payroll_deduction_parameters, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(arul_hr_payroll_deduction_parameters, self).write(cr, uid,ids, vals, context)
    
arul_hr_payroll_deduction_parameters()
#Start:TPT - By BalamuruganPurushothaman on 22/02/2015 - To Add Loan & Insurance Deatils Tab
class tpt_hr_payroll_loan_deduction_parameters(osv.osv):
    _name = 'arul.hr.payroll.loan.deduction.parameters'
    _columns = {
	'loan_id':fields.many2one('arul.hr.payroll.employee.structure','loan Details', ondelete='cascade'),
        'bank': fields.char('Bank Name', size=1024, required = False),
        'bank_branch': fields.char('Branch', size=1024, required = False),
        'loan_no': fields.char('Loan No', size=1024, required = False),
	'loan_amount': fields.float('Amount', size=1024, required = False),
	'loan_period_start':fields.date('Start Period'),
	'loan_period_end':fields.date('End Period'),
	'loan_id':fields.many2one('arul.hr.payroll.employee.structure','loan Details', ondelete='cascade'),
    }
tpt_hr_payroll_loan_deduction_parameters()

class tpt_hr_payroll_insurance_deduction_parameters(osv.osv):
    _name = 'arul.hr.payroll.insurance.deduction.parameters'
    _columns = {
	'insurance_id':fields.many2one('arul.hr.payroll.employee.structure','insurance details', ondelete='cascade'),
    'insurance_company': fields.char('Insurance Company', size=1024, required = False),
    'insurance_branch': fields.char('Branch', size=1024, required = False),
    'insurance_no': fields.char('Insurance No', size=1024, required = False),
	'insurance_amount': fields.float('Amount', size=1024, required = False),
	'insurance_period_start':fields.date('Start Period'),
	'insurance_period_end':fields.date('End Period'),
	
    }
tpt_hr_payroll_insurance_deduction_parameters()

class arul_hr_payroll_employee_structure(osv.osv):
    _name = 'arul.hr.payroll.employee.structure'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(arul_hr_payroll_employee_structure, self).default_get(cr, uid, fields, context=context)
        '''deductions_ids_vpf = self.pool.get('arul.hr.payroll.deduction.parameters').search(cr, uid, [('code','in',['VPF.D'])])
        deductions_vpf = []
        for line in deductions_ids_vpf:
            deductions_vpf.append((0,0,{'deduction_parameters_id':line}))
        res.update({'payroll_other_deductions_vpf': deductions_vpf})'''
		
	deductions_ids = self.pool.get('arul.hr.payroll.deduction.parameters').search(cr, uid, [('code','in',['VPF.D','I.D','L.D'])])
        deductions = []
        for line in deductions_ids:
            deductions.append((0,0,{'deduction_parameters_id':line}))
	
        res.update({'payroll_other_deductions_line': deductions})
        return res

    def _loan_amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                
                'loan_amount_subtotal': 0.0,
            }
            loanamt =0.0
	    #other_deduction_obj = self.pool.get('arul.hr.payroll.other.deductions')
	    #deduction_obj = self.pool.get('arul.hr.payroll.deduction.parameters')
	    #deduction_ids = deduction_obj.search(cr, uid, [('code','in',['VPF.D','I.D','L.D'])])
            for orderline in line.loan_line:
                loanamt = loanamt + orderline.loan_amount               
                res[line.id]['loan_amount_subtotal'] = loanamt
		
	    '''for deduction in deduction_obj.browse(cr, uid, deduction_ids):
                if deduction.code == 'L.D':
                    other_deduction_obj.append((0,0,{
				'deductions_parameters_id':deduction.id,
				'float':res[line.id]['loan_amount_subtotal'], 
			}))'''
        return res

    def _insurance_amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                
                'insurance_amount_subtotal': 0.0,
            }
            ins_amt =0.0
            for insline in line.insurance_line:
                ins_amt = ins_amt + insline.insurance_amount
		#raise osv.except_osv(_('Warning!%s'),_(ins_amt))               
                res[line.id]['insurance_amount_subtotal'] = ins_amt
        #raise osv.except_osv(_('Warning!%s'),_(res)) 
	return res

    def _get_loan(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('arul.hr.payroll.loan.deduction.parameters').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()

    def _get_insurance(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('arul.hr.payroll.insurance.deduction.parameters').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys() 

    _columns = {
         'employee_id': fields.many2one('hr.employee','Employee ID',required = True),
         'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Group',ondelete='restrict'),
         'sub_category_id':fields.many2one('hr.employee.sub.category','Employee Sub Group',ondelete='restrict'), 
         #'ins_de_period_start':fields.date('Insurance Deduction Period'),
         #'ins_de_period_end':fields.date('Insurance Deduction Period'),
         #'loan_de_period_start':fields.date('Loan Deductions Period'),
         #'loan_de_period_end':fields.date('Loan Deductions Period'),
         'payroll_earning_structure_line':fields.one2many('arul.hr.payroll.earning.structure','earning_structure_id','Earning Structure' ),
         'payroll_other_deductions_line':fields.one2many('arul.hr.payroll.other.deductions','earning_structure_id','Other Deductions'),
         'flag': fields.boolean('Flag'),
    	 'create_date': fields.datetime('Created Date',readonly = True),
    	 'write_date': fields.datetime('Updated Date',readonly = True),
    	 'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
    
    	 'history_line': fields.one2many('arul.hr.payroll.employee.structure','history_id','Histories',readonly = True),
             'history_id': fields.many2one('arul.hr.payroll.employee.structure','Histories Line', ondelete='cascade'),
    	 #'pay_history_line': fields.one2many('arul.hr.payroll.earning.structure','pay_history_line_id',readonly = True),
    	 #'pay_history_line_id': fields.one2many('arul.hr.payroll.earning.structure','pay_history_line_id',ondelete='cascade'),
    	 'loan_line':fields.one2many('arul.hr.payroll.loan.deduction.parameters','loan_id', ondelete='cascade'),
    	 'insurance_line':fields.one2many('arul.hr.payroll.insurance.deduction.parameters','insurance_id', ondelete='cascade'),
    	 #'payroll_other_deductions_vpf':fields.one2many('arul.hr.payroll.other.deductions','earning_structure_id','Structure line'),
    	 #'payroll_other_deductions_line1':fields.one2many('arul.hr.payroll.other.deductions','earning_structure_id','Structure line'),
    	 'loan_amount_subtotal': fields.function(_loan_amount_line, string='Loan Subtotal', digits_compute= dp.get_precision('Account'),
    		store={
                    'arul.hr.payroll.employee.structure': (lambda self, cr, uid, ids, c={}: ids, ['loan_line'], 10),
                    'arul.hr.payroll.loan.deduction.parameters': (_get_loan, ['loan_amount'], 10),
    		},multi='sums', help="The total amount."),
    	 'insurance_amount_subtotal': fields.function(_insurance_amount_line, string='Insurance Subtotal', digits_compute= dp.get_precision('Account'),
    		store={
                    'arul.hr.payroll.employee.structure': (lambda self, cr, uid, ids, c={}: ids, ['insurance_line'], 20),
                    'arul.hr.payroll.insurance.deduction.parameters': (_get_insurance, ['insurance_amount'], 20),
    		},multi='sums', help="The total amount."),
         ##
         'state':fields.selection([('draft', 'Draft'),('approved', 'Approved')],'Status', 
                                 readonly=True, states={'done':[('readonly', True)]}),
         ##
    }
    #Start:TPT By BalamuruganPurushothaman on 23/02/2015 - To  Add update L.D & I.D values from Loan & Insurance tab respectively,while creating the Employee Payroll Strcuture
    def create(self, cr, uid, vals, context=None):
        vals['flag'] = True
        if 'employee_id' in vals:
            emp = self.pool.get('hr.employee').browse(cr, uid, vals['employee_id']) 
 
            vals.update({
                    'employee_category_id':emp.employee_category_id and emp.employee_category_id.id or False,
                    'sub_category_id':emp.employee_sub_category_id and emp.employee_sub_category_id.id or False,
                    })
    	new_id = super(arul_hr_payroll_employee_structure, self).create(cr, uid, vals, context)
    	emp_struct = self.browse(cr,uid,new_id)
    	#raise osv.except_osv(_('Warning!%s'),_(vals))
    	other_deduction_obj = self.pool.get('arul.hr.payroll.other.deductions')
    	deduction_obj = self.pool.get('arul.hr.payroll.deduction.parameters')
    	deduction_ids = deduction_obj.search(cr, uid, [('code','in',['VPF.D','I.D','L.D'])])
    	
        
    	return new_id
    
    def bt_approve(self, cr, uid, ids, context=None):
        sql = '''
        update arul_hr_payroll_employee_structure set state='approved' where id=%s
        '''%ids[0]
        cr.execute(sql)
        return True
    
    #To  Add update L.D & I.D values from Loan & Insurance tab respectively, while editing Employee Payroll Strcuture
    def write(self, cr, uid, ids, vals, context=None):
    	for emp_struct in self.browse(cr,uid,ids): # TO MAINTAIN EMPLOYEE PAYROLL STRUCTURE - 26/02/2015
    	    if 'employee_category_id' in vals: 
                        default ={'history_id': emp_struct.id,'history_line':[]}
                        self.copy(cr, uid, emp_struct.id,default)
    	    if 'sub_category_id' in vals: 
                        default ={'history_id': emp_struct.id,'history_line':[]}
                        self.copy(cr, uid, emp_struct.id,default)
    	    if 'payroll_earning_structure_line' in vals:
                        default ={'history_id': emp_struct.id,'history_line':[]}
                        self.copy(cr, uid, emp_struct.id,default)
    	    if 'payroll_other_deductions_line' in vals:
                        default ={'history_id': emp_struct.id,'history_line':[]}
                        self.copy(cr, uid, emp_struct.id,default)
    	    if 'loan_line' in vals:
                        default ={'history_id': emp_struct.id,'history_line':[]}
                        self.copy(cr, uid, emp_struct.id,default)
    	    if 'insurance_line' in vals:
                        default ={'history_id': emp_struct.id,'history_line':[]}
                        self.copy(cr, uid, emp_struct.id,default)
            ###
            vals.update({'state':'draft'})
            ###
            new_write = super(arul_hr_payroll_employee_structure, self).write(cr, uid,ids, vals, context)
    	for emp_struct in self.browse(cr,uid,ids):
    		other_deduction_obj = self.pool.get('arul.hr.payroll.other.deductions')
    		deduction_obj = self.pool.get('arul.hr.payroll.deduction.parameters')
    		deduction_ids = deduction_obj.search(cr, uid, [('code','in',['VPF.D','I.D','L.D'])])	
            
    
        return new_write

    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['employee_id'], context)
        for line in self.browse(cr,uid,ids):
            for record in reads:
                employee_id = record['employee_id'][1]
                name = employee_id
                res.append((record['id'], name))
            return res  
    
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False,employee_sub_category_id=False, context=None):
        vals = {}
        if employee_category_id and employee_sub_category_id:
            sql = '''
                select id from hr_employee_sub_category where id = %s and category_id=%s
            '''%(employee_sub_category_id,employee_category_id)
            cr.execute(sql)
            sub_category_ids = [row[0] for row in cr.fetchall()]
            if not sub_category_ids:
                vals['sub_category_id']=False
        return {'value': vals}
    
    def onchange_employee_structure_id(self, cr, uid, ids,employee_id=False, context=None):
        vals = {}
        configuration_obj = self.pool.get('arul.hr.payroll.structure.configuration')
        employee_ids = self.search(cr, uid, [('employee_id','=',employee_id)])
        #TPT START
        if employee_ids:  
            raise osv.except_osv(_('Warning!'),_('Already Pay Structure Defined for this Employee!'))
        #TPT END
        if employee_id:
            earning_obj = self.pool.get('arul.hr.payroll.earning.structure')
            earning_ids = earning_obj.search(cr, uid, [('earning_structure_id','in',ids)])
            earning_obj.unlink(cr, uid, earning_ids)
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
#             emp_obj = self.pool.get('hr.employee')
#             emp_ids = emp_obj.search(cr, uid, [('id','=',employee_id)])
#             emp = emp_obj.browse(cr,uid,emp_ids[0])
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

    _defaults = {      
       #'create_date':time.strftime('%Y-%m-%d'),
       #'write_date':time.strftime('%Y-%m-%d'),
       'state':'draft',
    }
    _constraints = [
        #(_check_employee_id, 'Identical Data', ['employee_id']),
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
         'float':fields.float('Amount') ,
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
        'emp_esi_limit': fields.float('Employee ESI Limit'),
        'emp_esi_con': fields.float('Employee ESI Contribution (%)'),
        'employer_esi_con': fields.float('Employer ESI Contribution (%)'),
        'emp_lwf_amt': fields.float('Employee Labor Welfare Fund (LWF) Amt'),
        'employer_lwf_con_amt': fields.float('Employer LWF Contribution Amt'),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
        }
    
    def _check_category(self, cr, uid, ids, context=None):
        for work in self.browse(cr, uid, ids, context=context):
            work_ids = self.search(cr, uid, [('id','!=',work.id),('sub_category_id','=',work.sub_category_id.id),('employee_category_id','=',work.employee_category_id.id)])
            if work_ids:
                raise osv.except_osv(_('Warning!'),_('Employee Group and Employee Sub Group already exist!'))
                return False
        return True
    _constraints = [
        (_check_category, 'Identical Data', ['employee_category_id','sub_category_id']),
    ]
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['employee_category_id', 'sub_category_id'], context)
        for line in self.browse(cr,uid,ids):
            for record in reads:
                sub_category_id = record['sub_category_id'][1]
                employee_category_id = record['employee_category_id'][1]
                name = employee_category_id + ' - ' + sub_category_id
                res.append((record['id'], name))
            return res  
    
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
        emp_sub_cat = []
        if employee_category_id:
            emp_cat = self.pool.get('vsis.hr.employee.category').browse(cr, uid, employee_category_id)
            emp_sub_cat = [x.id for x in emp_cat.sub_category_ids]
        return {'value': {'sub_category_id': False }, 'domain':{'sub_category_id':[('id','in',emp_sub_cat)]}}
         
#     def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
#         employee_sub_ids = []
#         if employee_category_id:
#             employee = self.pool.get('vsis.hr.employee.category').browse(cr, uid, employee_category_id)
#             for emp in employee.sub_category_ids:
#                 employee_sub_ids.append(emp.code)
#         return {'value': {'sub_category_id': False }, 'domain':{'sub_category_id':[('char','in',employee_sub_ids)]}}
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('check_employee_category_id'):
            employee_category_id = context.get('employee_category_id')
            if not employee_category_id:
                args += [('id','=',-1)]
        return super(arul_hr_payroll_contribution_parameters, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    
arul_hr_payroll_contribution_parameters()

class arul_hr_payroll_structure_configuration(osv.osv):
    _name = 'arul.hr.payroll.structure.configuration'
    _columns = {
         'employee_category_id':fields.many2one('vsis.hr.employee.category','Employee Group', required = True),
         'sub_category_id':fields.many2one('hr.employee.sub.category','Employee Sub Group',required = True), 
         'create_date': fields.datetime('Created Date',readonly = True),
         'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
         'payroll_structure_configuration_line':fields.one2many('arul.hr.payroll.earning.structure.configuration','earning_structure_configuration_id','Structure Configuration') ,   
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['employee_category_id', 'sub_category_id'], context)
        for line in self.browse(cr,uid,ids):
            for record in reads:
                sub_category_id = record['sub_category_id'][1]
                employee_category_id = record['employee_category_id'][1]
                name = employee_category_id + ' - ' + sub_category_id
                res.append((record['id'], name))
            return res  
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('check_employee_category_id'):
            employee_category_id = context.get('employee_category_id')
            if not employee_category_id:
                args += [('id','=',-1)]
        return super(arul_hr_payroll_structure_configuration, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    def onchange_employee_category_id(self, cr, uid, ids,employee_category_id=False, context=None):
        return {'value': {'sub_category_id': False }}
    
    def _check_category_sub_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_category_ids = self.search(cr, uid, [('id','!=',payroll.id),('employee_category_id','=',payroll.employee_category_id.id)])
            payroll_sub_ids = self.search(cr, uid, [('id','!=',payroll.id),('sub_category_id','=',payroll.sub_category_id.id)])
            if payroll_category_ids and payroll_sub_ids:
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
    def _check_earning_parameters_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_category_ids = self.search(cr, uid, [('id','!=',payroll.id),('earning_parameters_id','=',payroll.earning_parameters_id.id),('earning_structure_configuration_id','=',payroll.earning_structure_configuration_id.id)])
            if payroll_category_ids :
                return False
        return True
    _constraints = [
        (_check_earning_parameters_id, 'Identical Data', ['earning_parameters_id']),
    ]  
arul_hr_payroll_earning_structure_configuration()

class arul_hr_payroll_other_deductions(osv.osv):
    _name = 'arul.hr.payroll.other.deductions'
    _columns = {
         
         'deduction_parameters_id': fields.many2one('arul.hr.payroll.deduction.parameters','Deduction Parameters',required = True),
         'earning_structure_id':fields.many2one('arul.hr.payroll.employee.structure','Earning Structure', ondelete='cascade'), 
         'float':fields.float('Amount') ,
         'executions_details_id':fields.many2one('arul.hr.payroll.executions.details','Execution Details', ondelete='cascade'),
    }
    
arul_hr_payroll_other_deductions()

class tpt_hr_payroll_approve_reject(osv.osv):
    _name = 'tpt.hr.payroll.approve.reject'
    _columns = {
         'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year', required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
         'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
         'state':fields.selection([('draft', 'New'),('cancel', 'Reject'),('done', 'Approved')],'Status', readonly=True),
         'post_date': fields.date('Posting Date',required=True),
         'create_date': fields.datetime('Created Date',readonly = True),
         'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
    }
    _defaults = {
        'state':'draft',
       'year':int(time.strftime('%Y')),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['year', 'month'], context)
        for line in self.browse(cr,uid,ids):
            for record in reads:
                year = str(line.year)
                month = str(line.month)
                name = month + ' - ' + year
                res.append((record['id'], name))
            return res     

    def approve_payroll(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            payroll_obj = self.pool.get('arul.hr.payroll.executions')
            payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state','=','confirm')])
            for payroll in payroll_obj.browse(cr,uid,payroll_ids):
                payroll_obj.write(cr, uid, payroll.id, {'state':'approve'})
        return self.write(cr, uid, line.id, {'state':'done'})
    
    def reject_payroll(self, cr, uid, ids, context=None):
#         for line in self.browse(cr,uid,ids):
#             payroll_obj = self.pool.get('arul.hr.payroll.executions')
#             executions_obj = self.pool.get('arul.hr.payroll.executions.details')
#             payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state', '=', 'confirm')])
#             if not payroll_ids:
#                 raise osv.except_osv(_('Warning !'), _("Do not find the confirmed payroll!"))
#             payroll_obj.write(cr, uid, payroll_ids, {'state':'draft'})
#             executions_ids = executions_obj.search(cr, uid, [('payroll_executions_id','in',payroll_ids)])
#             if not executions_ids:
#                 raise osv.except_osv(_('Warning !'), _("Can not confirm this payroll!"))
#             else:
#                 executions_obj.unlink(cr, uid, executions_ids, context=context)
#         return self.write(cr, uid, ids, {'state':'cancel'})
        line = self.browse(cr,uid,ids[0])
        return self.pool.get('alert.form').info(cr, uid, title='Alert', message="Do you need to roll back the Payroll for the Period: %s?"%(str(line.month)+'-'+str(line.year)))
tpt_hr_payroll_approve_reject()


class arul_hr_payroll_executions(osv.osv):
    _name = 'arul.hr.payroll.executions'
    _columns = {
         'payroll_area_id': fields.many2one('arul.hr.payroll.area','Payroll Area',required = True, states={'confirm': [('readonly', True)], 'approve': [('readonly', True)]}),
         'state': fields.selection([('draft', 'New'),('confirm', 'Confirmed'),('approve', 'Approved')],'Status'),
         'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year', required = True, states={'confirm': [('readonly', True)], 'approve': [('readonly', True)]}),
         'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True, states={'confirm': [('readonly', True)], 'approve': [('readonly', True)]}),
         'create_date': fields.datetime('Created Date',readonly = True),
         'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
         'payroll_executions_details_line': fields.one2many('arul.hr.payroll.executions.details','payroll_executions_id','Details Line', states={'confirm': [('readonly', True)], 'approve': [('readonly', True)]}),
    }
    _defaults = {
        'state':'draft',
        'year':int(time.strftime('%Y')),
    }
    
    def _check(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        for line in self.browse(cr,uid,ids):
            execution_ids = self.search(cr, uid, [('id','!=',line.id),('payroll_area_id','=',line.payroll_area_id.id),('month','=',line.month),('year','=',line.year)])
            if execution_ids:
                raise osv.except_osv(_('Warning!'),_('Payroll Executions for Payroll area %s, month %s, year %s already exist!')%(line.payroll_area_id.id,line.month,line.year))
                return False
        return True
    _constraints = [
        (_check, _(''), ['name', 'date']),
    ]
    
    def print_payslip(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'arul.hr.payroll.executions',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'arul_print_report',
        }
    
    def length_month(self,year, month):
        if month == 2 and (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
            value =  29
        else: 
            value =  [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
        return value
    
    def get_timesheet(self,cr,uid,emp,month,year,context=None):
        monthly_shift_schedule_obj = self.pool.get('arul.hr.monthly.shift.schedule')
        sql =   '''
                    select ss.id as shift_id
                    from arul_hr_monthly_shift_schedule ss 
                    left join arul_hr_monthly_work_schedule ws on ss.monthly_work_id = ws.id
                    where ss.employee_id = %s and ws.month = '%s' and ws.year = %s and ws.state= 'done'
                '''%(emp,month,year)
        cr.execute(sql)
        kq = cr.fetchall()
        total_days = 0
        total_shift_allowance = 0
        total_lop = 0
        total_esi = 0
        total_week_off = 0
        special_holidays = 0
        if kq:
            leave_detail_obj = self.pool.get('arul.hr.employee.leave.details')
            sql = '''
                select id from arul_hr_employee_leave_details where EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s and employee_id = %s and 
                leave_type_id in (select id from arul_hr_leave_types where code = 'LOP')
                and state='done'
            '''%(year,int(month),emp)
            cr.execute(sql)
            leave_detail_ids = [row[0] for row in cr.fetchall()]
            for leave_detail in leave_detail_obj.browse(cr, uid, leave_detail_ids):
                day_from = leave_detail.date_from[8:10]
                day_to = leave_detail.date_to[8:10]
                for day in range(int(day_from),int(day_to)+1):
                    total_lop += 1
            shift_ids = self.pool.get('arul.hr.audit.shift.time').search(cr, uid, [('work_date','like',str(year)),('employee_id','=',emp),('state','=','cancel'),('additional_shifts','=',False)])
            #total_lop += len(shift_ids)

	    #Start:TPT To calculate Total no of ESI Leaves
            sql = '''
                select id from arul_hr_employee_leave_details where EXTRACT(year FROM date_from) = %s and 
                EXTRACT(month FROM date_from) = %s and employee_id = %s and 
                leave_type_id in (select id from arul_hr_leave_types where code = 'ESI')
                and state='done'
            '''%(year,int(month),emp)
            cr.execute(sql)
            leave_detail_ids = [row[0] for row in cr.fetchall()]
            for leave_detail in leave_detail_obj.browse(cr, uid, leave_detail_ids):
                day_from = leave_detail.date_from[8:10]
                day_to = leave_detail.date_to[8:10]
                for day in range(int(day_from),int(day_to)+1):
                    total_esi += 1
            shift_ids = self.pool.get('arul.hr.audit.shift.time').search(cr, uid, [('work_date','like',str(year)),('employee_id','=',emp),('state','=','cancel'),('additional_shifts','=',False)])
            #total_esi += len(shift_ids) #TPT CHECK POINT FOR GEN_PAYROLL

	    # Special Holiday Calculation
            sql2 = '''
                    select count(*) from arul_hr_holiday_special where EXTRACT(year FROM date) = %s and EXTRACT(month FROM date) = %s and is_local_holiday='f'
                '''%(year, int(month))
            cr.execute(sql2)
            a =  cr.fetchone()
            special_holidays = a[0]
	    #END:TPT
            for monthly_shift_schedule_id in monthly_shift_schedule_obj.browse(cr,uid,[kq[0][0]],context=context):
                if monthly_shift_schedule_id.day_1:
                    if monthly_shift_schedule_id.day_1.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_1.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_2:
                    if monthly_shift_schedule_id.day_2.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_2.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_3:
                    if monthly_shift_schedule_id.day_3.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_3.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_4:
                    if monthly_shift_schedule_id.day_4.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_4.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_5:
                    if monthly_shift_schedule_id.day_5.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_5.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_6:
                    if monthly_shift_schedule_id.day_6.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_6.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_7:
                    if monthly_shift_schedule_id.day_7.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_7.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_8:
                    if monthly_shift_schedule_id.day_8.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_8.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_9:
                    if monthly_shift_schedule_id.day_9.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_9.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_10:
                    if monthly_shift_schedule_id.day_10.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_10.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_11:
                    if monthly_shift_schedule_id.day_11.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_11.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_12:
                    if monthly_shift_schedule_id.day_12.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_12.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_13:
                    if monthly_shift_schedule_id.day_13.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_13.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_14:
                    if monthly_shift_schedule_id.day_14.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_14.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_15:
                    if monthly_shift_schedule_id.day_15.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_15.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_16:
                    if monthly_shift_schedule_id.day_16.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_16.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_17:
                    if monthly_shift_schedule_id.day_17.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_17.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_18:
                    if monthly_shift_schedule_id.day_18.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_18.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_19:
                    if monthly_shift_schedule_id.day_19.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_19.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_20:
                    if monthly_shift_schedule_id.day_20.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_20.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_21:
                    if monthly_shift_schedule_id.day_21.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_21.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_22:
                    if monthly_shift_schedule_id.day_22.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_22.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_23:
                    if monthly_shift_schedule_id.day_23.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_23.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_24:
                    if monthly_shift_schedule_id.day_24.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_24.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_25:
                    if monthly_shift_schedule_id.day_25.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_25.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_26:
                    if monthly_shift_schedule_id.day_26.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_26.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_27:
                    if monthly_shift_schedule_id.day_27.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_27.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_28:
                    if monthly_shift_schedule_id.day_28.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_28.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_29 and monthly_shift_schedule_id.num_of_month>=29:
                    if monthly_shift_schedule_id.day_29.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_29.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_30 and monthly_shift_schedule_id.num_of_month>=30:
                    if monthly_shift_schedule_id.day_30.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_30.time_total
                    else:
                        total_week_off += 1
                if monthly_shift_schedule_id.day_31 and monthly_shift_schedule_id.num_of_month>=31:
                    if monthly_shift_schedule_id.day_31.code != 'W':
                        total_days += 1
                        total_shift_allowance += monthly_shift_schedule_id.day_31.time_total
                    else:
                        total_week_off += 1
        return total_days,total_shift_allowance,total_lop,total_esi,total_week_off #,special_holidays
    
    def generate_payroll(self, cr, uid, ids, context=None):
        details_line = []
        
        for line in self.browse(cr,uid,ids):
            time_leav_obj = self.pool.get('tpt.time.leave.evaluation')
            time_leav_ids = time_leav_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('year','=',line.year),('month','=',line.month),('state','=','done')])
            if not time_leav_ids:
                raise osv.except_osv(_('Warning!'),_('Time/Leave Evaluation is not made or confirm!'))
            for ti_le in time_leav_obj.browse(cr,uid,time_leav_ids):
                if len(ti_le.shift_time_id)!=0 or len(ti_le.leave_request_id)!=0 or len(ti_le.non_availability_id)!=0:
                    raise osv.except_osv(_('Warning!'),_('Time/Leave Evaluation is not completed!'))

            emp_obj = self.pool.get('hr.employee')
            payroll_emp_struc_obj = self.pool.get('arul.hr.payroll.employee.structure')
            executions_details_obj = self.pool.get('arul.hr.payroll.executions.details')
            earning_structure_obj = self.pool.get('arul.hr.payroll.earning.structure')
            other_deductions_obj = self.pool.get('arul.hr.payroll.other.deductions')
            contribution_obj = self.pool.get('arul.hr.payroll.contribution.parameters')
            earning_obj = self.pool.get('arul.hr.payroll.earning.parameters')
            deduction_obj = self.pool.get('arul.hr.payroll.deduction.parameters')
 
            ##    
            sql = '''
                select employee_id from arul_hr_monthly_shift_schedule where 
                    monthly_work_id in (select id from arul_hr_monthly_work_schedule where "month"='%s' and "year"=%s and state='done')
            '''%(line.month,line.year)
            cr.execute(sql)
            monthly_shift_emp_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select employee_id from arul_hr_payroll_employee_structure
            '''
            cr.execute(sql)
            employee_structure_emp_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select employee_id from arul_hr_punch_in_out_time where EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s
            '''%(line.year,line.month)
            cr.execute(sql)
            punch_in_out_emp_ids = [row[0] for row in cr.fetchall()]     
            ##TPT
            sql = '''
                SELECT employee_id FROM 
                arul_hr_permission_onduty WHERE non_availability_type_id='on_duty' 
                AND EXTRACT(year FROM date) = %s AND EXTRACT(month FROM date) = %s and total_shift_worked>=1
            '''%(line.year,line.month)
            cr.execute(sql)
            onduty_emps = [row[0] for row in cr.fetchall()] 
            punch_onduty_emps = punch_in_out_emp_ids+onduty_emps
            
            #TPT     
            #TPT COMMENTED BY BalamuruganPurushothaman ON 24/03/2015 - TO GENERATE THE PAYROLL FOR EMPLOYEES ARE NOT IN MONTHLY WORK SCHEDULE
            #SINCE NEW EMPLOYEE CAN HAVE ONLY ATTENDANCE DETAILS
            #employee_ids = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('id','in',monthly_shift_emp_ids),('id','in',employee_structure_emp_ids),('id','in',punch_in_out_emp_ids)])
            
            #employee_ids = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('id','in',employee_structure_emp_ids),('id','in',punch_in_out_emp_ids)])
            #employee_ids_no_emp_pay_struct = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('id','not in',employee_structure_emp_ids),('id','in',punch_in_out_emp_ids)])
            employee_ids = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('id','in',employee_structure_emp_ids),('id','in',punch_onduty_emps)])
            employee_ids_no_emp_pay_struct = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('id','not in',employee_structure_emp_ids),('id','in',punch_onduty_emps)])
            if employee_ids_no_emp_pay_struct:  
                emp_code='' 
                for p in emp_obj.browse(cr,uid,employee_ids_no_emp_pay_struct): 
                    emp_code = emp_code +'\n'+ p.employee_id                               
                raise osv.except_osv(_('No Pay Structure Defined for the following Employees'),_(emp_code))
            ###   
            ##
            sql = '''
                select employee_id from arul_hr_payroll_employee_structure where state='draft' and history_id is null
            '''
            cr.execute(sql)
            employee_draft_structure_emp_ids = [row[0] for row in cr.fetchall()]
            ##        
            employee_ids_draft_emp_pay_struct = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id),('id','in',employee_draft_structure_emp_ids),('id','in',punch_onduty_emps)])
            if employee_ids_draft_emp_pay_struct:  
                emp_code='' 
                for p in emp_obj.browse(cr,uid,employee_ids_draft_emp_pay_struct): 
                    emp_code = emp_code +'\n'+ p.employee_id                               
                raise osv.except_osv(_('Pay Structure not Approved for the following Employees'),_(emp_code))
            ###
            for p in emp_obj.browse(cr,uid,employee_ids):
                payroll_executions_details_ids = executions_details_obj.search(cr, uid, [('payroll_executions_id', '=', line.id), ('employee_id', '=', p.id)], context=context)
                
                #TPT START - By BalamurganPurushothaman - ON 13/03/2015-TO CALCULATE TOTAL NO.OF SHIFT WORKED FOR SPECIAL ALLOWANCE CALCULATION
                #PUNCH IN OUT
                #TPT - Attendance Total Shift Count for Payroll Month
                
                sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
                SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s 
                AND EXTRACT(month FROM date_from) = %s AND employee_id =%s AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('LOP','ESI'))
                and state='done'
                '''%(line.year,line.month,p.id)
                cr.execute(sql)
                lop_esi =  cr.fetchone()
                tpt_lop_esi = lop_esi[0]
                total_no_of_leave = tpt_lop_esi

                #TPT BalamuruganPurushothaman ON 19/05/2015 - TO DEFINE RULES FOR NEWLY JOINED EMPLOYEES IN BETWEEN A PAYROLL MONTH
                # If Date Of Joining is 15/04/2015 Then  
                # Day of Joining = 15, Calendar Days for this Month = 30
                # The Total No.Of Days Before DOJ = 30 - 15 - 1 = 14 Days
                # So these 14 Days are Considered as LOP for Internal Process Only, Since there is no Pay for these Days
                # Then this "Total No.Of Days Before DOJ" count is added with Real LOP/ESI Count (this count is taken from arul_hr_employee_leave_details table)
                s3_working_days = 26
                sql = '''
                    select extract(day from date_of_joining) doj from hr_employee where extract(year from date_of_joining)= %s and 
                      extract(month from date_of_joining)= %s and id=%s
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                k = cr.fetchone()
                if k:
                    new_emp_day = k[0]    
                    if p.employee_category_id and p.employee_category_id.code == 'S1':           
                        #before_doj = calendar_days - new_emp_day - 1
                        before_doj =  new_emp_day - 1
                        total_no_of_leave = total_no_of_leave + before_doj
                    if p.employee_category_id and p.employee_category_id.code == 'S2':           
                        #before_doj = calendar_days - new_emp_day - 1
                        before_doj =  new_emp_day - 1
                        total_no_of_leave = total_no_of_leave + before_doj
                    if p.employee_category_id and p.employee_category_id.code == 'S3':
                        #before_doj = s3_working_days - new_emp_day - 1
                        before_doj =  new_emp_day - 1
                        total_no_of_leave = total_no_of_leave + before_doj
                    
                ##TPT END
                sql = '''
                SELECT CASE WHEN SUM(total_shift_worked1)!=0 THEN SUM(total_shift_worked1) ELSE 0 END total_shift_worked FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                '''%(line.year,line.month,p.id)
                cr.execute(sql)
                a =  cr.fetchone()
                shift_count = a[0]
                
                #Permission
                sql = '''
                SELECT SUM(total_shift_worked) FROM arul_hr_permission_onduty WHERE non_availability_type_id='permission' 
                AND EXTRACT(year FROM date) = %s AND EXTRACT(month FROM date) = %s and employee_id =%s
                '''%(line.year,line.month,p.id)
                cr.execute(sql)
                b =  cr.fetchone()
                permission_count = b[0]
                
                #OnDuty
                #===============================================================
                # sql = '''
                # SELECT CASE WHEN SUM(total_shift_worked)!=0 THEN SUM(total_shift_worked) ELSE 0 END total_shift_worked 
                # FROM arul_hr_permission_onduty WHERE non_availability_type_id='on_duty' 
                # AND EXTRACT(year FROM date) = %s AND EXTRACT(month FROM date) = %s and employee_id =%s and total_shift_worked>=1 and approval='t'
                # '''%(line.year,line.month,p.id)
                #===============================================================
                sql = '''
                    select case when sum(total_shift_worked)!=0 then sum(total_shift_worked) else 0 end total_shift_worked from arul_hr_permission_onduty where shift_type='G2' and 
                    EXTRACT(year FROM date) = %s AND EXTRACT(month FROM date) = %s and employee_id=%s
                    and approval='t'
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                c =  cr.fetchone()
                onduty_count = c[0]
                
                #TOTAL SHIFT WORKED
                total_shift_worked = 0.0    
                total_shift_worked = shift_count + onduty_count
                
                total_g1_shift_allowance = 0
                total_g2_shift_allowance = 0
                total_a_shift_allowance = 0
                total_b_shift_allowance = 0
                total_c_shift_allowance = 0
                              
                sql = '''
                    SELECT CASE WHEN SUM(a_shift_count1)!=0 THEN SUM(a_shift_count1) ELSE 0 END a_shift_count FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                    AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                a_c =  cr.fetchone()
                a_shift_count = a_c[0]
                
                sql = '''
                    SELECT CASE WHEN SUM(b_shift_count1)!=0 THEN SUM(b_shift_count1) ELSE 0 END b_shift_count FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                    AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                b_c =  cr.fetchone()
                b_shift_count = b_c[0]
                
                sql = '''
                    SELECT CASE WHEN SUM(c_shift_count1)!=0 THEN SUM(c_shift_count1) ELSE 0 END c_shift_count FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                    AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                c_c =  cr.fetchone()
                c_shift_count = c_c[0]
                
                sql = '''
                    SELECT CASE WHEN SUM(g1_shift_count1)!=0 THEN SUM(g1_shift_count1) ELSE 0 END g1_shift_count FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                    AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                g1_c =  cr.fetchone()
                g1_shift_count = g1_c[0]
                
                sql = '''
                    SELECT CASE WHEN SUM(g2_shift_count1)!=0 THEN SUM(g2_shift_count1) ELSE 0 END g2_shift_count FROM arul_hr_punch_in_out_time WHERE EXTRACT(year FROM work_date) = %s 
                    AND EXTRACT(month FROM work_date) = %s AND employee_id =%s
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                g2_c =  cr.fetchone()
                g2_shift_count = g2_c[0]
                
                sql = '''
                    select allowance from arul_hr_capture_work_shift where code='G1'
                    '''
                cr.execute(sql)
                g1_all =  cr.fetchone()
                g1_shift_allowance = g1_all[0]
                
                sql = '''
                    select allowance from arul_hr_capture_work_shift where code='G2'
                    '''
                cr.execute(sql)
                g2_all =  cr.fetchone()
                g2_shift_allowance = g2_all[0]
                
                sql = '''
                    select allowance from arul_hr_capture_work_shift where code='A'
                    '''
                cr.execute(sql)
                a_all =  cr.fetchone()
                a_shift_allowance = a_all[0]
                
                sql = '''
                    select allowance from arul_hr_capture_work_shift where code='B'
                    '''
                cr.execute(sql)
                b_all =  cr.fetchone()
                b_shift_allowance = b_all[0]
                
                sql = '''
                    select allowance from arul_hr_capture_work_shift where code='C'
                    '''
                cr.execute(sql)
                c_all =  cr.fetchone()
                c_shift_allowance = c_all[0]
                ###TPT
                total_onduty_g2_alLowance = 0 
                sql = '''
                    select case when sum(total_shift_worked)!=0 then sum(total_shift_worked) else 0 end total_shift_worked from arul_hr_permission_onduty where shift_type='G2' and 
                    EXTRACT(year FROM date) = %s AND EXTRACT(month FROM date) = %s and employee_id=%s
                    and approval='t'
                    '''%(line.year,line.month,p.id)
                cr.execute(sql)
                onduty_shift =  cr.fetchone()
                onduty_shift_count = onduty_shift[0]
                total_onduty_g2_allowance = onduty_shift_count * g2_shift_allowance
                ##
                sql = '''
                    select EXTRACT(day FROM work_date) from arul_hr_punch_in_out_time where employee_id = %s and EXTRACT(year FROM work_date) = %s and EXTRACT(month FROM work_date) = %s
                '''%(p.id, line.year, line.month)
                cr.execute(sql)
                punch_days = [row[0] for row in cr.fetchall()]
                ##
                ###TPT

                total_g1_shift_allowance = g1_shift_count * g1_shift_allowance
                total_g2_shift_allowance = g2_shift_count * g2_shift_allowance
                total_a_shift_allowance = a_shift_count * a_shift_allowance
                total_b_shift_allowance = b_shift_count * b_shift_allowance
                total_c_shift_allowance = c_shift_count * c_shift_allowance
                
                total_all_shift_allowance =  total_g1_shift_allowance + total_g2_shift_allowance + total_a_shift_allowance + total_b_shift_allowance + total_c_shift_allowance
                total_all_shift_allowance = total_all_shift_allowance + total_onduty_g2_allowance
                #TPT
                
                special_holiday_worked_count =  0  
                #SELECT COUNT(work_date) AS date_holiday_count                             
                sql = '''
                        SELECT CASE WHEN SUM(total_shift_worked)!=0 
                            THEN SUM(total_shift_worked) ELSE 0 END total_shift_worked 
                        FROM arul_hr_punch_in_out_time 
                        WHERE work_date IN (SELECT date FROM arul_hr_holiday_special 
                        WHERE EXTRACT(month from date)=%s AND EXTRACT(year from date)=%s ) AND 
                        EXTRACT(month from work_date)=%s AND EXTRACT(year from work_date)=%s AND
                        punch_in_out_id IN (SELECT id FROM arul_hr_employee_attendence_details WHERE employee_id=%s)
                    '''%(line.month, line.year, line.month, line.year, p.id)
                cr.execute(sql)
                special_holiday_worked_count = cr.dictfetchone()['total_shift_worked']
                
                #TPT-TAKING SHD HOLIDAY COUNT FOR PAYROLL MONTH
                special_holidays = 0
                sql = '''
                        select count(*) from arul_hr_holiday_special where EXTRACT(year FROM date) = %s and EXTRACT(month FROM date) = %s and is_local_holiday='f'
                    '''%(line.year,line.month)
                cr.execute(sql)
                spl =  cr.fetchone()
                special_holidays = spl[0]
                        
                #TPT END
                        
                if payroll_executions_details_ids:
                    executions_details_obj.unlink(cr, uid, payroll_executions_details_ids, context=context) 
                vals_earning_struc = []
                vals_other_deductions = []
                emp_struc_ids = payroll_emp_struc_obj.search(cr,uid,[('employee_id','=',p.id),('state','=','approved')]) 
                emp_esi_limit = 0
                emp_esi_con = 0
                emp_pf_con = 0
                emp_lwf_amt = 0
                emp_esi_con_amount = 0
                emp_pf_con_amount = 0
                vpfd_amount = 0
                gross_sal = 0
                total_earning = 0
                da = 0
                lop = 0
                
                pfd = 0.0
                pd = 0.0
                vpfd = 0.0
                esid = 0.0
                fd = 0.0
                ld = 0.0 
                ind = 0.0
                pt = 0.0
                lwf = 0.0
                total_deduction = 0
                
                basic = 0.0
                da = 0.0
                c = 0.0
                hra = 0.0
                fa = 0.0
                pc = 0.0
                cre = 0.0
                ea = 0.0
                spa = 0.0
                la = 0.0
                aa = 0.0
                sha = 0.0
                oa = 0.0
                ma = 0.0
                lta = 0.0
                med = 0.0
                net_sala = 0.0
                
                net_basic = 0.0
                net_da = 0.0 
                net_c = 0.0
                net_hra = 0.0
                net_ea = 0.0
                net_aa = 0.0
                net_la = 0.0
                net_oa = 0.0

                if emp_struc_ids:
                    payroll_emp_struc = payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0])
                    contribution_ids = contribution_obj.search(cr, uid, [('employee_category_id','=',p.employee_category_id.id),('sub_category_id','=',p.employee_sub_category_id.id)])
                    if contribution_ids:
                        contribution = contribution_obj.browse(cr, uid, contribution_ids[0])
                        emp_esi_limit = contribution.emp_esi_limit
                        ##TPT
                        sql = '''
                        select extract(day from date_of_joining) doj from hr_employee where extract(year from date_of_joining)= %s and 
                          extract(month from date_of_joining)= %s and id=%s
                        '''%(line.year,line.month,p.id)
                        cr.execute(sql)
                        k = cr.fetchone()
                        if k:
                            new_emp_day = k[0]  
                            emp_lwf_amt = contribution.emp_lwf_amt 
                        ##TPT
                        if line.month=='12':
                            sql = '''
                            select extract(day from date_of_joining) doj from hr_employee where extract(year from date_of_joining)= %s and id=%s
                            '''%(line.year,p.id)
                            cr.execute(sql)
                            k = cr.fetchone()
                            if not k:
                                emp_lwf_amt = contribution.emp_lwf_amt
                                
                        emp_esi_con = contribution.emp_esi_con
                        emp_pf_con = contribution.emp_pf_con
                    total_days,total_shift_allowance,total_lop,total_esi,total_week_off = self.get_timesheet(cr,uid,p.id,line.month,line.year,context=context)
                    calendar_days = self.length_month(int(line.year),int(line.month))

                    sql = '''
                        select case when sum(employee_amt)!=0 then sum(employee_amt) else 0 end total_fd from meals_details where emp_id = %s and meals_id in (select id from meals_deduction where meals_for='employees' and EXTRACT(year FROM meals_date) = %s and EXTRACT(month FROM meals_date) = %s)
                    '''%(p.id,line.year,int(line.month))
                    cr.execute(sql)
                    total_fd = cr.dictfetchone()['total_fd']
                    
                    if p.employee_category_id and p.employee_category_id.code == 'S1':
                        pfd = 0.0
                        pd = 0.0
                        vpfd = 0.0
                        esid = 0.0
                        fd = 0.0
                        ld = 0.0 
                        ind = 0.0
                        pt = 0.0
                        lwf = 0.0
                        total_deduction = 0
                        
                        i_lic_prem = 0
                        i_others = 0 
                        l_vvti_loan = 0 
                        l_lic_hfl = 0 
                        l_hdfc = 0 
                        l_tmb = 0 
                        l_sbt = 0 
                        l_others = 0
                        it_deduction = 0
    
                        for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if other_deductions_id.deduction_parameters_id.code == 'P.D':
                                pd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vpfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'F.D':
                                fd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'L.D':
                                ld = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'I.D':
                                ind = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'PT':
                                pt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'INS_LIC_PREM':
                                i_lic_prem = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'INS_OTHERS':
                                i_others = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_VVTI':
                                l_vvti_loan = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_LIC_HFL':
                                l_lic_hfl = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_HDFC':
                                l_hdfc = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_TMB':
                                l_tmb = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_SBT':
                                l_sbt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_OTHERS':
                                l_others = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'IT':
                                it_deduction = other_deductions_id.float

                        fd += total_fd
                        fd = round(fd,0)
                        #pt += total_ptax			
                        total_deduction = pd  + esid + fd + ld + ind +  pt + lwf + i_lic_prem + i_others + l_vvti_loan + l_lic_hfl + l_hdfc + l_tmb + l_sbt + l_others + it_deduction
                        
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'P.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'L.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': ld,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'I.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': ind,
                                    }))

                        basic = 0.0
                        da = 0.0
                        c = 0.0
                        hra = 0.0
                        fa = 0.0
                        pc = 0.0
                        cre = 0.0
                        ea = 0.0
                        spa = 0.0
                        la = 0.0
                        aa = 0.0
                        sha = 0.0
                        oa = 0.0
                        lta = 0.0
                        med = 0.0
                        gross_sal = 0.0
                        total_earning = 0.0
                        net_sala = 0.0

                        net_basic = 0.0
                        net_da = 0.0 
                        net_c = 0.0
                        net_hra = 0.0
                        net_ea = 0.0
                        net_aa = 0.0
                        net_la = 0.0
                        net_oa = 0.0
                        vpfd_amount = 0.0
                        ma = 0.0
                        spa = 0.0
                        esi_check = 0.0

                        for earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if earning_struc_id.earning_parameters_id.code == 'BASIC':
                                basic = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'DA':
                                da = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'C':
                                c = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'HRA':
                                hra = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'FA':
                                fa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'PC':
                                pc = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'CR':
                                cre = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'EA':
                                ea = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'SpA':
                                spa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'LA':
                                la = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'AA':
                                aa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'ShA':
                                sha = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'OA':
                                oa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MA':
                                ma = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'LTA':
                                lta = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MED':
                                med = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'ESI_CHECK':
                                esi_check = earning_struc_id.float

                        sql = '''
                        select extract(day from date_of_joining) doj from hr_employee where extract(year from date_of_joining)= %s and 
                          extract(month from date_of_joining)= %s and id=%s
                        '''%(line.year,line.month,p.id)
                        cr.execute(sql)
                        k = cr.fetchone()
                        if k:
                            new_emp_day = k[0] 
                            total_working_days_s1 = 0    
                            if p.employee_category_id and p.employee_category_id.code == 'S1':           
                                total_working_days_s1 = calendar_days - new_emp_day + 1    
                                #spa = spa / (calendar_days - 4 - special_holidays) * total_working_days_s1 
                                spa = spa / calendar_days  * total_working_days_s1   
                                spa  = round(spa,0)                     
                        
            
            ##TPT-New Joinee
            
            
            
			net_basic = round(basic - (basic / calendar_days) * total_no_of_leave,0)
			net_da = round(da - (da / calendar_days) * total_no_of_leave, 0)
			net_c = round(c - (c / calendar_days) * total_no_of_leave, 0)
			net_hra = round(hra - (hra / calendar_days) * total_no_of_leave, 0)
			net_ea = round(ea - (ea / calendar_days) * total_no_of_leave, 0)
			net_aa = round(aa - (aa / calendar_days) * total_no_of_leave, 0)
			net_la = round(la - (la / calendar_days) * total_no_of_leave, 0)
			net_oa = round(oa - (oa / calendar_days) * total_no_of_leave, 0)
            
            

			total_earning =  net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa + fa + spa + pc + cre + sha + lta + med
			gross_sal =  net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa + fa + spa + pc + cre + sha + lta + med

			if gross_sal + esi_check >= emp_esi_limit:
                            emp_esi_con_amount = 0
                        else:
                            emp_esi_con_amount = math.ceil(total_earning*emp_esi_con/100)# round=math.ceil

                        base_amount = net_basic + net_da 
                        emp_pf_con_amount = round(base_amount*emp_pf_con/100)
                        #raise osv.except_osv(_('Warning !'), _(round(21.5)))
                        vpfd_amount = round(base_amount * vpfd / 100) 	
			total_deduction += (emp_pf_con_amount + emp_esi_con_amount + emp_lwf_amt + vpfd_amount)            
			net_sala = gross_sal - total_deduction
            


                        for _earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if _earning_struc_id.earning_parameters_id.code == 'BASIC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_basic,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'DA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_da,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'C':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_c,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'HRA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_hra,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'FA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': fa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'PC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': pc,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'CR':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': cre,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'EA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_ea,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SpA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': spa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_la,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'AA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_aa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'ShA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': sha,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'OA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_oa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LTA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': lta,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'MED':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': med,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'MA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': ma,
                                    }))
                            
                        earning_ids = earning_obj.search(cr, uid, [('code','in',['TOTAL_EARNING','GROSS_SALARY','NET'])])
                        for earning in earning_obj.browse(cr, uid, earning_ids):
                            if earning.code == 'TOTAL_EARNING':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': total_earning,
                                }))
                            if earning.code == 'GROSS_SALARY':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': gross_sal,
                                }))
                            if earning.code == 'NET':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': net_sala,
                                }))
                        ## TPT START - PTAX CALCULATION
                        from_date = ''
                        to_date =''
                        sql = '''
                        select from_date,to_date from tpt_hr_ptax where extract(month from to_date)=%s and extract(year from to_date)=%s
                        '''%(line.month,line.year)
                        cr.execute(sql)
                        for k in cr.fetchall():
                            from_date=k[0]
                            to_date=k[1]
                        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
                        
                        total_ptax = 0
                        prev_total_earning = 0
                        if from_date and to_date:
                            sql = '''
                            SELECT * FROM generate_series('%s'::timestamp,
                                  '%s', '1 Months')
                            '''%(from_date, to_date)
                            cr.execute(sql)
                            temp_list = [r[0] for r in cr.fetchall()]
                            month_list = []
                            for k in temp_list:
                                month_list.append(str(int(k[5:7])))
                                      
                            payroll_ids = payroll_obj.search(cr, uid,[('month','in',month_list),('year','=',line.year),('employee_id','=',p.id),('payroll_executions_id.state','in',['confirm','approve'])])
                            if payroll_ids:
                                for pay in payroll_ids:
                                    payroll = payroll_obj.browse(cr, uid, pay)
                                   
                                    for earning in payroll.earning_structure_line:
                                        if earning.earning_parameters_id.code=='TOTAL_EARNING':
                                            prev_total_earning +=   earning.float
                            #raise osv.except_osv(_('Warning !'), _(prev_total_earning))
                            ptax_total_earning = prev_total_earning + total_earning 
                            sql = '''
                                    select  pl.ptax_amt ptax_amt from tpt_hr_ptax_line pl
                                        inner join tpt_hr_ptax_slab sl on pl.slab_id=sl.id
                                        where %s between sl.from_range and sl.to_range
                                        and ptax_id = 
                                        (select id from tpt_hr_ptax where extract(month from to_date)=%s 
                                        and extract(year from to_date)=%s)
                                    '''%(ptax_total_earning, line.month,line.year)
                            cr.execute(sql)
                            total_ptax = cr.dictfetchone()['ptax_amt'] 
                            pt = total_ptax
                            total_deduction = total_deduction + pt
                        ### TPT END PTAX 
                        deduction_ids = deduction_obj.search(cr, uid, [('code','in',['TOTAL_DEDUCTION','VPF.D','PF.D','ESI.D','LWF','F.D','LOP',
                                    'INS_LIC_PREM','INS_OTHERS','LOAN_VVTI','LOAN_LIC_HFL','LOAN_HDFC','LOAN_TMB', 'LOAN_SBT','LOAN_OTHERS','IT','PT'               
                                                                                     ])])
                        for deduction in deduction_obj.browse(cr, uid, deduction_ids):
                            if deduction.code == 'TOTAL_DEDUCTION':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': total_deduction,
                                    }))
                            if deduction.code == 'VPF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': vpfd_amount,
                                    }))
                            if deduction.code == 'PF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_pf_con_amount,
                                    }))
                            if deduction.code == 'ESI.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_esi_con_amount,
                                    }))
                            if deduction.code == 'LWF':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_lwf_amt,
                                    }))
                            if deduction.code == 'F.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': fd,
                                    }))
                            if deduction.code == 'INS_LIC_PREM':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': i_lic_prem,
                                    }))
                            if deduction.code == 'INS_OTHERS':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': i_others,
                                    }))
                            if deduction.code == 'LOAN_VVTI':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_vvti_loan,
                                    }))
                            if deduction.code == 'LOAN_LIC_HFL':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_lic_hfl,
                                    }))
                            if deduction.code == 'LOAN_HDFC':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_hdfc,
                                    }))
                            if deduction.code == 'LOAN_TMB':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_tmb,
                                    }))
                            if deduction.code == 'LOAN_SBT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_sbt,
                                    }))
                            if deduction.code == 'LOAN_OTHERS':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_others,
                                    }))
                            if deduction.code == 'IT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': it_deduction,
                                    }))
                            if deduction.code == 'PT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': pt,
                                    }))

		    # Handling Pay Structure for S2 Category
                    if p.employee_category_id and p.employee_category_id.code == 'S2':
                        pfd = 0.0
                        pd = 0.0
                        vpfd = 0.0
                        esid = 0.0
                        fd = 0.0
                        ld = 0.0 
                        ind = 0.0
                        pt = 0.0
                        lwf = 0.0
                        total_deduction = 0
                        
                        i_lic_prem = 0
                        i_others = 0 
                        l_vvti_loan = 0 
                        l_lic_hfl = 0 
                        l_hdfc = 0 
                        l_tmb = 0 
                        l_sbt = 0 
                        l_others = 0
                        it_deduction = 0
                        
                        for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:

                            if other_deductions_id.deduction_parameters_id.code == 'P.D':
                                pd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vpfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'F.D':
                                fd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'L.D':
                                ld = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'I.D':
                                ind = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'PT':
                                pt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'INS_LIC_PREM':
                                i_lic_prem = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'INS_OTHERS':
                                i_others = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_VVTI':
                                l_vvti_loan = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_LIC_HFL':
                                l_lic_hfl = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_HDFC':
                                l_hdfc = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_TMB':
                                l_tmb = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_SBT':
                                l_sbt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_OTHERS':
                                l_others = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'IT':
                                it_deduction = other_deductions_id.float
                                
                        fd += total_fd     
                        fd = round(fd,0)     
                        
                        total_deduction = pfd + pd  + esid + fd + ld + ind +  pt + lwf + i_lic_prem + i_others + l_vvti_loan + l_lic_hfl + l_hdfc + l_tmb + l_sbt + l_others + it_deduction

                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'P.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'L.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': ld,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'I.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': ind,
                                    }))

                        basic = 0.0
                        da = 0.0
                        c = 0.0
                        hra = 0.0
                        fa = 0.0
                        pc = 0.0
                        cre = 0.0
                        ea = 0.0
                        spa = 0.0
                        la = 0.0
                        aa = 0.0
                        sha = 0.0
                        oa = 0.0
                        lta = 0.0
                        med = 0.0
                        gross_sal = 0.0
                        total_earning = 0.0
                        net_sala = 0.0
			
			            #Start:TPT
                        net_basic = 0.0
                        net_da = 0.0 
                        net_c = 0.0
                        net_hra = 0.0
                        net_ea = 0.0
                        net_aa = 0.0
                        net_la = 0.0
                        net_oa = 0.0
                        vpfd_amount = 0.0
                        ma = 0.0
                        shd = 0.0
                        esi_check = 0.0

                        for earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if earning_struc_id.earning_parameters_id.code == 'BASIC':
                                basic = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'DA':
                                da = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'C':
                                c = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'HRA':
                                hra = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'FA':
                                fa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'PC':
                                pc = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'CR':
                                cre = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'EA':
                                ea = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'SpA':
                                spa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'LA':
                                la = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'AA':
                                aa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'ShA':
                                sha = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'OA':
                                oa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MA':
                                ma = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'LTA':
                                lta = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MED':
                                med = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'SHD':
                                shd = earning_struc_id.float	
                            if earning_struc_id.earning_parameters_id.code == 'ESI_CHECK':
                                esi_check = earning_struc_id.float		
                        
                        
                        for_esi_base_spa = spa
                        spa = spa / (calendar_days - 4 - special_holidays) * total_shift_worked # TPT total_days <-> total_shift_worked
                        spa  = round(spa,0)  
                        
			
                        net_basic = round(basic - (basic / calendar_days) * total_no_of_leave, 0)
                        net_da = round(da - (da / calendar_days) * total_no_of_leave, 0)
                        net_c = round(c - (c / calendar_days) * total_no_of_leave, 0)
                        net_hra = round(hra - (hra / calendar_days) * total_no_of_leave, 0)
                        net_ea = round(ea - (ea / calendar_days) * total_no_of_leave, 0)
                        net_aa = round(aa - (aa / calendar_days) * total_no_of_leave, 0)
                        net_la = round(la - (la / calendar_days) * total_no_of_leave, 0)
                        net_oa = round(oa - (oa / calendar_days) * total_no_of_leave, 0)
            
            
                        total_earning =  net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa + fa + spa + pc + cre + sha + lta + med
                        gross_sal =  net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa + fa + spa + pc + cre + sha + lta + med
                        for_esi_base_gross_sal =  basic + da + c + hra + ea + aa + la + oa + fa + for_esi_base_spa + pc + cre + sha + lta + med
                        
                        gross_shd_calc = net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa
                        if p.employee_sub_category_id.code=='T1':
                            shd = 0
                        else:
                            shd = (gross_shd_calc / calendar_days) * special_holiday_worked_count
                        total_earning = total_earning + shd
                        gross_sal = gross_sal + shd
                        

                        if for_esi_base_gross_sal + esi_check >= emp_esi_limit:#S2
                            emp_esi_con_amount = 0
                        else:
                            emp_esi_con_amount = math.ceil(total_earning*emp_esi_con/100)

                        base_amount = net_basic + net_da 
                        emp_pf_con_amount = round(base_amount*emp_pf_con/100)
                        vpfd_amount = round(base_amount * vpfd / 100) 	
                        total_deduction += (emp_pf_con_amount + emp_esi_con_amount + emp_lwf_amt + vpfd_amount)
                        net_sala = gross_sal - total_deduction
  
                        for _earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if _earning_struc_id.earning_parameters_id.code == 'BASIC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_basic,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'DA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_da,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'C':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_c,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'HRA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_hra,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'FA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': fa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'PC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': pc,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'CR':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': cre,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'EA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_ea,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SpA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': spa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_la,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'AA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_aa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'ShA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': sha,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'OA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_oa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LTA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': lta,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'MED':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': med,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SHD':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': shd,
                                    }))
                            
                           
                        earning_ids = earning_obj.search(cr, uid, [('code','in',['TOTAL_EARNING','GROSS_SALARY','NET'])])
                        for earning in earning_obj.browse(cr, uid, earning_ids):
                            if earning.code == 'TOTAL_EARNING':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': total_earning,
                                }))
                            if earning.code == 'GROSS_SALARY':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': gross_sal,
                                }))
                            if earning.code == 'NET':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': net_sala,
                                }))
                       
                        ## TPT START - PTAX CALCULATION
                        from_date = ''
                        to_date =''
                        sql = '''
                        select from_date,to_date from tpt_hr_ptax where extract(month from to_date)=%s and extract(year from to_date)=%s
                        '''%(line.month,line.year)
                        cr.execute(sql)
                        for k in cr.fetchall():
                            from_date=k[0]
                            to_date=k[1]
                        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
                        
                        total_ptax = 0
                        prev_total_earning = 0
                        if from_date and to_date:
                            sql = '''
                            SELECT * FROM generate_series('%s'::timestamp,
                                  '%s', '1 Months')
                            '''%(from_date, to_date)
                            cr.execute(sql)
                            temp_list = [r[0] for r in cr.fetchall()]
                            month_list = []
                            for k in temp_list:
                                month_list.append(str(int(k[5:7])))
                                      
                            payroll_ids = payroll_obj.search(cr, uid,[('month','in',month_list),('year','=',line.year),('employee_id','=',p.id),('payroll_executions_id.state','in',['confirm','approve'])])
                            if payroll_ids:
                                for pay in payroll_ids:
                                    payroll = payroll_obj.browse(cr, uid, pay)
                                    for earning in payroll.earning_structure_line:
                                        if earning.earning_parameters_id.code=='TOTAL_EARNING':
                                            prev_total_earning += earning.float
                            ptax_total_earning = prev_total_earning + total_earning
                            sql = '''
                                    select  pl.ptax_amt ptax_amt from tpt_hr_ptax_line pl
                                        inner join tpt_hr_ptax_slab sl on pl.slab_id=sl.id
                                        where %s between sl.from_range and sl.to_range
                                        and ptax_id = 
                                        (select id from tpt_hr_ptax where extract(month from to_date)=%s 
                                        and extract(year from to_date)=%s)
                                    '''%(ptax_total_earning, line.month,line.year)
                            cr.execute(sql)
                            total_ptax = cr.dictfetchone()['ptax_amt'] 
                            pt = total_ptax
                            total_deduction = total_deduction + pt
                        ### TPT END PTAX 
                        
                        deduction_ids = deduction_obj.search(cr, uid, [('code','in',['TOTAL_DEDUCTION','VPF.D','PF.D','ESI.D','LWF','F.D','LOP',
                                        'INS_LIC_PREM','INS_OTHERS','LOAN_VVTI','LOAN_LIC_HFL','LOAN_HDFC','LOAN_TMB', 'LOAN_SBT','LOAN_OTHERS','IT','PT'                                               
                                                                                     ])])
                        for deduction in deduction_obj.browse(cr, uid, deduction_ids):
                            if deduction.code == 'TOTAL_DEDUCTION':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': total_deduction,
                                    }))
                            if deduction.code == 'VPF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': vpfd_amount,
                                    }))
                            if deduction.code == 'PF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_pf_con_amount,
                                    }))
                            if deduction.code == 'ESI.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_esi_con_amount,
                                    }))
                            if deduction.code == 'LWF':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_lwf_amt,
                                    }))
                            if deduction.code == 'F.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': fd,
                                    }))
                            if deduction.code == 'INS_LIC_PREM':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': i_lic_prem,
                                    }))
                            if deduction.code == 'INS_OTHERS':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': i_others,
                                    }))
                            if deduction.code == 'LOAN_VVTI':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_vvti_loan,
                                    }))
                            if deduction.code == 'LOAN_LIC_HFL':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_lic_hfl,
                                    }))
                            if deduction.code == 'LOAN_HDFC':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_hdfc,
                                    }))
                            if deduction.code == 'LOAN_TMB':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_tmb,
                                    }))
                            if deduction.code == 'LOAN_SBT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_sbt,
                                    }))
                            if deduction.code == 'LOAN_OTHERS':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_others,
                                    }))
                            if deduction.code == 'IT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': it_deduction,
                                    }))
                            if deduction.code == 'PT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': pt,
                                    }))
                                

		    #Start:TPT hadling Workers - S3 category
                    if p.employee_category_id and p.employee_category_id.code == 'S3':
                        pfd = 0.0
                        pd = 0.0
                        vpfd = 0.0
                        esid = 0.0
                        fd = 0.0
                        ld = 0.0 
                        ind = 0.0
                        pt = 0.0
                        lwf = 0.0
                        total_deduction = 0
                        
                        i_lic_prem = 0
                        i_others = 0 
                        l_vvti_loan = 0 
                        l_lic_hfl = 0 
                        l_hdfc = 0 
                        l_tmb = 0 
                        l_sbt = 0 
                        l_others = 0
                        it_deduction = 0
                        
                        for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if other_deductions_id.deduction_parameters_id.code == 'P.D':
                                pd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vpfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'F.D':
                                fd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'L.D':
                                ld = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'I.D':
                                ind = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'PT':
                                pt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'INS_LIC_PREM':
                                i_lic_prem = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'INS_OTHERS':
                                i_others = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_VVTI':
                                l_vvti_loan = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_LIC_HFL':
                                l_lic_hfl = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_HDFC':
                                l_hdfc = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_TMB':
                                l_tmb = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_SBT':
                                l_sbt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LOAN_OTHERS':
                                l_others = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'IT':
                                it_deduction = other_deductions_id.float
                        
                        fd += total_fd        
                        fd = round(fd,0)

                        total_deduction = pfd + pd + esid + fd + ld + ind +  pt + lwf + i_lic_prem + i_others + l_vvti_loan + l_lic_hfl + l_hdfc + l_tmb + l_sbt + l_others + it_deduction
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'P.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pd,
                                    }))

                            if _other_deductions_id.deduction_parameters_id.code == 'L.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': ld,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'I.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': ind,
                                    }))

                        basic = 0.0
                        da = 0.0
                        c = 0.0
                        hra = 0.0
                        fa = 0.0
                        pc = 0.0
                        cre = 0.0
                        ea = 0.0
                        spa = 0.0
                        la = 0.0
                        aa = 0.0
                        sha = 0.0
                        oa = 0.0
                        lta = 0.0
                        med = 0.0
                        gross_sal = 0.0
                        total_earning = 0.0
                        net_sala = 0.0
                        wa = 0.0
                        ma = 0.0
                        shd = 0.0
                        esi_check = 0.0

                        #Start:TPT - Variable Declarations
                        net_basic = 0.0
                        net_da = 0.0 
                        net_c = 0.0
                        net_hra = 0.0
                        net_ea = 0.0
                        net_aa = 0.0
                        net_la = 0.0
                        net_oa = 0.0
                        vpfd_amount = 0.0
                        #End:TPT - Variable Declarations

                        for earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if earning_struc_id.earning_parameters_id.code == 'BASIC':
                                basic = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'DA':
                                da = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'C':
                                c = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'HRA':
                                hra = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'FA':
                                fa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'PC':
                                pc = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'CR':
                                cre = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'EA':
                                ea = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'SpA':
                                spa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'LA':
                                la = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'AA':
                                aa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'ShA':
                                sha = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'OA':
                                oa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MA':
                                ma = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'WA':
                                wa = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'LTA':
                                lta = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MED':
                                med = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'ESI_CHECK':
                                esi_check = earning_struc_id.float                      
                        for_esi_base_spa = spa
                        spa = spa/(calendar_days - 4 - special_holidays) * total_shift_worked #TPT total_days <->total_shift_worked 
                        spa  = round(spa,0)  

                        lunch_allowance = 5 # Rs.5 is Fixed as Lunch Allowance as per VVTi Rules
                        washing_allowane = 4 # Rs.4 is Fixed as per VVTi Rules
                        #TPT-MISCELLANEOUS AMOUNT NOT CALCULATE FOR TRAINEES
                        if p.employee_sub_category_id.code=='T2':
                            ma = 0
                        else:
                            ma = (total_shift_worked * ( lunch_allowance + washing_allowane )) + total_all_shift_allowance
                            ma = round(ma,0) 
			            
                        net_basic = round(basic - (basic / s3_working_days) * total_no_of_leave, 0)
                        net_da = round(da - (da / s3_working_days) * total_no_of_leave, 0)
                        net_c = round(c - (c / s3_working_days) * total_no_of_leave, 0)
                        net_hra = round(hra - (hra / s3_working_days) * total_no_of_leave, 0)
                        net_ea = round(ea - (ea / s3_working_days) * total_no_of_leave,0)
                        net_aa = round(aa - (aa / s3_working_days) * total_no_of_leave, 0)
                        net_la = round(la - (la / s3_working_days) * total_no_of_leave, 0)
                        net_oa = round(oa - (oa / s3_working_days) * total_no_of_leave, 0)

                        total_earning =  net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa + fa + spa + pc + cre + sha + lta + med + ma
                        gross_sal =  net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa + fa + spa + pc + cre + sha + lta + med + ma
                        for_esi_base_gross_sal =  basic + da + c + hra + ea + aa + la + oa + fa + for_esi_base_spa + pc + cre + sha + lta + med
                        #S3
                        gross_shd_calc = net_basic + net_da + net_c + net_hra + net_ea + net_aa + net_la + net_oa
                        # SYSTEM COULD NOT CALCULATE SHD ALLOWANCE FOR ALL TRAINEES - 03/06/2015
                        if p.employee_sub_category_id.code=='T2':
                            shd = 0
                        else:
                            shd = (gross_shd_calc / s3_working_days) * special_holiday_worked_count
                        total_earning = total_earning + shd
                        gross_sal = gross_sal + shd
                        
                        if for_esi_base_gross_sal + esi_check >= emp_esi_limit:
                            emp_esi_con_amount = 0
                        else:
                            emp_esi_con_amount = math.ceil(total_earning*emp_esi_con/100)

                        base_amount = net_basic + net_da 
                        emp_pf_con_amount = round(base_amount*emp_pf_con/100) #math.ceil(base_amount*emp_pf_con/100)
                        vpfd_amount = round(base_amount * vpfd / 100) 	
                        total_deduction += (emp_pf_con_amount + emp_esi_con_amount + emp_lwf_amt + vpfd_amount)
                        net_sala = gross_sal - total_deduction

                        for _earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if _earning_struc_id.earning_parameters_id.code == 'BASIC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_basic,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'DA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_da,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'C':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_c,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'HRA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_hra,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'FA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': fa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'PC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': pc,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'CR':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': cre,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'EA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_ea,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SpA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': spa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_la,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'AA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_aa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'ShA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': sha,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'OA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_oa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'MA': #TPT
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': ma,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LTA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': lta,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'MED':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': med,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SHD': #TPT
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': shd,
                                    }))
			   
                        earning_ids = earning_obj.search(cr, uid, [('code','in',['TOTAL_EARNING','GROSS_SALARY','NET'])])
                        for earning in earning_obj.browse(cr, uid, earning_ids):
                            if earning.code == 'TOTAL_EARNING':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': total_earning,
                                }))
                            if earning.code == 'GROSS_SALARY':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': gross_sal,
                                }))
                            if earning.code == 'NET':
                                vals_earning_struc.append((0,0, {
                                      'earning_parameters_id':earning.id,
                                      'float': net_sala,
                                }))
                        
                        ## TPT START - PTAX CALCULATION
                        from_date = ''
                        to_date =''
                        sql = '''
                        select from_date,to_date from tpt_hr_ptax where extract(month from to_date)=%s and extract(year from to_date)=%s
                        '''%(line.month,line.year)
                        cr.execute(sql)
                        for k in cr.fetchall():
                            from_date=k[0]
                            to_date=k[1]
                        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
                        
                        total_ptax = 0
                        prev_total_earning = 0
                        if from_date and to_date:
                            sql = '''
                            SELECT * FROM generate_series('%s'::timestamp,
                                  '%s', '1 Months')
                            '''%(from_date, to_date)
                            cr.execute(sql)
                            temp_list = [r[0] for r in cr.fetchall()]
                            month_list = []
                            for k in temp_list:
                                month_list.append(str(int(k[5:7])))
                                      
                            payroll_ids = payroll_obj.search(cr, uid,[('month','in',month_list),('year','=',line.year),('employee_id','=',p.id),('payroll_executions_id.state','in',['confirm','approve'])])
                            if payroll_ids:
                                for pay in payroll_ids:
                                    payroll = payroll_obj.browse(cr, uid, pay)
                                    for earning in payroll.earning_structure_line:
                                        if earning.earning_parameters_id.code=='TOTAL_EARNING':
                                            prev_total_earning += earning.float
                            ptax_total_earning = prev_total_earning + total_earning
                            sql = '''
                                    select  pl.ptax_amt ptax_amt from tpt_hr_ptax_line pl
                                        inner join tpt_hr_ptax_slab sl on pl.slab_id=sl.id
                                        where %s between sl.from_range and sl.to_range
                                        and ptax_id = 
                                        (select id from tpt_hr_ptax where extract(month from to_date)=%s 
                                        and extract(year from to_date)=%s)
                                    '''%(ptax_total_earning, line.month,line.year)
                            cr.execute(sql)
                            total_ptax = cr.dictfetchone()['ptax_amt'] 
                            pt = total_ptax
                            total_deduction = total_deduction + pt
                        ### TPT END PTAX 
                        deduction_ids = deduction_obj.search(cr, uid, [('code','in',['TOTAL_DEDUCTION','VPF.D','PF.D','ESI.D','LWF','F.D','LOP',
                                    'INS_LIC_PREM','INS_OTHERS','LOAN_VVTI','LOAN_LIC_HFL','LOAN_HDFC','LOAN_TMB', 'LOAN_SBT','LOAN_OTHERS','IT','PT'                                                   
                                                                                     ])])
                        for deduction in deduction_obj.browse(cr, uid, deduction_ids):
                            if deduction.code == 'TOTAL_DEDUCTION':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': total_deduction,
                                    }))
                            if deduction.code == 'VPF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': vpfd_amount,
                                    }))
                            if deduction.code == 'PF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_pf_con_amount,
                                    }))
                            if deduction.code == 'ESI.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_esi_con_amount,
                                    }))
                            if deduction.code == 'LWF':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': emp_lwf_amt,
                                    }))
                            if deduction.code == 'F.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': fd,
                                    }))
                            if deduction.code == 'INS_LIC_PREM':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': i_lic_prem,
                                    }))
                            if deduction.code == 'INS_OTHERS':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': i_others,
                                    }))
                            if deduction.code == 'LOAN_VVTI':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_vvti_loan,
                                    }))
                            if deduction.code == 'LOAN_LIC_HFL':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_lic_hfl,
                                    }))
                            if deduction.code == 'LOAN_HDFC':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_hdfc,
                                    }))
                            if deduction.code == 'LOAN_TMB':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_tmb,
                                    }))
                            if deduction.code == 'LOAN_SBT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_sbt,
                                    }))
                            if deduction.code == 'LOAN_OTHERS':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': l_others,
                                    }))
                            if deduction.code == 'IT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': it_deduction,
                                    }))
                            if deduction.code == 'PT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':deduction.id,
                                          'float': pt,
                                    }))

                rs = {
                        'payroll_executions_id': line.id,
                        'employee_id': p.id,
                        'department_id':p.department_id and p.department_id.id or False,
                        'designation_id':p.job_id and p.job_id.id or False,
                        'year':line.year,
                        'month':line.month,
                        'company_id': p.company_id and p.company_id.id or False,
                        'payroll_area_id': line.payroll_area_id.id,
                        'payroll_sub_area_id': p.payroll_sub_area_id.id,
                        'earning_structure_line':vals_earning_struc,
                        'other_deduction_line':vals_other_deductions,
                        'emp_esi_limit': emp_esi_limit,
                        'emp_esi_con': emp_esi_con_amount,
                        'emp_pf_con': emp_pf_con_amount,
                        'emp_lwf_amt': emp_lwf_amt,
                      }
                executions_details_id = executions_details_obj.create(cr,uid,rs)
                
        datas = {
             'ids': ids,
             'model': 'arul.hr.payroll.executions',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'arul_print_report',
        }
                   
    def confirm_payroll(self, cr, uid, ids, context=None):
        executions_obj = self.pool.get('arul.hr.payroll.executions.details')
        executions_ids = executions_obj.search(cr, uid, [('payroll_executions_id','in',ids)])
        if executions_ids:
            return self.write(cr, uid, ids, {'state': 'confirm'})
        else:
            raise osv.except_osv(_('Warning !'), _("Can not confirm this payroll!"))

    def rollback_payroll(self, cr, uid, ids, context=None):
        executions_obj = self.pool.get('arul.hr.payroll.executions.details')
        executions_ids = executions_obj.search(cr, uid, [('payroll_executions_id','in',ids)])
        if executions_ids:
            return  executions_obj.unlink(cr, uid, executions_ids, context=context)
        else:
            raise osv.except_osv(_('Warning !'), _("This payroll has not been generated yet!"))
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['payroll_area_id' ,'year', 'month'], context)
        for line in self.browse(cr,uid,ids):
            for record in reads:
                year = str(line.year)
                month = str(line.month)
                payroll = record['payroll_area_id'][1]
                name = payroll  + ' - ' + month + ' - ' + year
                res.append((record['id'], name))
            return res  
        
arul_hr_payroll_executions()

class arul_hr_payroll_executions_details(osv.osv):
    _name = 'arul.hr.payroll.executions.details'
    _columns = {
        'company_id': fields.many2one('res.company','Company',ondelete='restrict'),
        'payroll_area_id': fields.many2one('arul.hr.payroll.area', 'Payroll Area',ondelete='restrict'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area', 'Payroll Sub Area',ondelete='restrict'),
        'employee_id': fields.many2one('hr.employee', 'Employee',ondelete='restrict'),
        'department_id': fields.many2one('hr.department', 'Department',ondelete='restrict'),
        'designation_id': fields.many2one('hr.job', 'Designation',ondelete='restrict'),
        'year': fields.char('Year', size = 1024),
        'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month'),
        'payroll_executions_id':fields.many2one('arul.hr.payroll.executions', 'Payroll Executions', ondelete='cascade'),
        'earning_structure_line':fields.one2many('arul.hr.payroll.earning.structure','executions_details_id', 'Earing Structure'),
        'other_deduction_line':fields.one2many('arul.hr.payroll.other.deductions','executions_details_id', 'Other Deduction'),
        
        'emp_pf_con': fields.float('Employee PF Contribution'),
        'emp_esi_limit': fields.float('Employee ESI Limit'),
        'emp_esi_con': fields.float('Employee ESI Contribution'),
        'emp_lwf_amt': fields.float('Employee Labor Welfare Fund (LWF) Amt'),
    }
    
    def onchange_department_from_id(self, cr, uid, ids,department_id=False, context=None):
        designation_ids = []
        if department_id:
            department = self.pool.get('hr.department').browse(cr, uid, department_id)
            for line in department.designation_line:
                designation_ids.append(line.designation_id.id)
        return {'value': {'designation_id': False }, 'domain':{'designation_id':[('id','in',designation_ids)]}}
    
arul_hr_payroll_executions_details()

#TPT For Employee Payroll Structure
class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('pay_structured_emp'):
            sql = '''
                select id from hr_employee where id not in (select distinct employee_id from arul_hr_payroll_employee_structure 
                where history_id is null) and resource_id in (select id from resource_resource where active='t');
            '''
            cr.execute(sql)
            qc_test_request_ids = [row[0] for row in cr.fetchall()]
            request_ids = self.search(cr, uid, [('id','in',qc_test_request_ids)])
            if context.get('name'):
                request_ids.append(context.get('name'))
            args += [('id','in',request_ids)]
        return super(hr_employee, self).search(cr, uid, args, offset, limit, order, context, count)
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#         ids = self.search(cr, user, args, context=context, limit=limit)
#         return self.name_get(cr, user, ids, context=context)

hr_employee()

class resource_resource(osv.osv):
    _inherit = "resource.resource"
    _columns = {   
        'rfid': fields.char('RFID', size=1024, required = False),   
    }
resource_resource()

class tpt_hr_ptax(osv.osv):
    _name = "tpt.hr.ptax"
    _columns = {   
        'name': fields.char('Name'), 
        'ptax_line': fields.one2many('tpt.hr.ptax.line', 'ptax_id', 'PTax Slab'),
        'from_date': fields.date('From Date'),
        'to_date': fields.date('To Date'),    
    }
    def create(self, cr, uid, vals, context=None):
        vals.update({'name':'From '+str(vals['from_date'])+ ' to '+str(vals['to_date']),
                        })
        return super(tpt_hr_ptax, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        ptax_obj = self.pool.get('tpt.hr.ptax') 
        ptax_obj_id = ptax_obj.browse(cr,uid,ids[0])
        if 'from_date' in vals :
            vals.update({'name':'From '+str(vals['from_date'])+ ' to '+str(ptax_obj_id.to_date),
                         })
        if 'to_date' in vals :
            vals.update({'name':'From '+str(ptax_obj_id.from_date)+ ' to '+str(vals['to_date']),
                         })
        new_write = super(tpt_hr_ptax, self).write(cr, uid,ids, vals, context)
        return new_write
tpt_hr_ptax()

class tpt_hr_ptax_line(osv.osv):
    _name = "tpt.hr.ptax.line"
    _order = "ptax_amt asc"
    _columns = {   
        'ptax_id': fields.many2one('tpt.hr.ptax', 'PTax'),
        'slab_id':fields.many2one('tpt.hr.ptax.slab','Gross Salary'),
        'from_range': fields.float('Salary Amt From'),
        'to_range': fields.float('Salary Amt To'),   
        'ptax_amt': fields.float('PTax Amount'),  
    }
tpt_hr_ptax_line()

class tpt_hr_ptax_slab(osv.osv):
    _name = "tpt.hr.ptax.slab"
    _columns = {  
        'name': fields.char('Name'), 
        'from_range': fields.float('Salary Amt From'),
        'to_range': fields.float('Salary Amt To'),   
    }
    def create(self, cr, uid, vals, context=None):
        vals.update({'name':'Between Rs.'+str(vals['from_range'])+ ' to Rs.'+str(vals['to_range']),
                        })
        return super(tpt_hr_ptax_slab, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        ptax_obj = self.pool.get('tpt.hr.ptax.slab') 
        ptax_obj_id = ptax_obj.browse(cr,uid,ids[0])
        if 'from_range' in vals:
            
            vals.update({'name':'Between Rs.'+str(vals['from_range'])+ ' to Rs.'+str(ptax_obj_id.to_range),
                         })
        if 'to_range' in vals:
            vals.update({'name':'Between Rs.'+str(ptax_obj_id.from_range)+ ' to Rs.'+str(vals['to_range']),
                         })
        new_write = super(tpt_hr_ptax_slab, self).write(cr, uid,ids, vals, context)
        return new_write
tpt_hr_ptax_slab()
