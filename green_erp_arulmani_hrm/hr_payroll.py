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

class arul_hr_payroll_employee_structure(osv.osv):
    _name = 'arul.hr.payroll.employee.structure'
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(arul_hr_payroll_employee_structure, self).default_get(cr, uid, fields, context=context)
        deductions_ids = self.pool.get('arul.hr.payroll.deduction.parameters').search(cr, uid, [('code','in',['I.D','L.D','VPF.D'])])
        deductions = []
        for line in deductions_ids:
            deductions.append((0,0,{'deduction_parameters_id':line}))
        res.update({'payroll_other_deductions_line': deductions})
        return res
    
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
         'flag': fields.boolean('Flag'),
    }
    
    def create(self, cr, uid, vals, context=None):
        vals['flag'] = True
        return super(arul_hr_payroll_employee_structure, self).create(cr, uid, vals, context)
    
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
#                 employee_sub_ids.append(emp.id)
#         return {'value': {'sub_category_id': False }, 'domain':{'sub_category_id':[('id','in',employee_sub_ids)]}}
    
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
            payroll_category_ids = self.search(cr, uid, [('id','!=',payroll.id),('earning_parameters_id','=',payroll.earning_parameters_id.id)])
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
            payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month)])
#             executions_obj = self.pool.get('arul.hr.payroll.executions.details')
#         executions_ids = executions_obj.search(cr, uid, [('payroll_executions_id','in',ids)])
#         if executions_ids:
            for payroll in payroll_obj.browse(cr,uid,payroll_ids):
                if payroll.state == "confirm":
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
         'payroll_executions_details_line': fields.one2many('arul.hr.payroll.executions.details','payroll_executions_id','Details Line', states={'confirm': [('readonly', True)], 'approve': [('readonly', True)]}),
    }
    _defaults = {
        'state':'draft',
        'year':int(time.strftime('%Y')),
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
                    where ss.employee_id = %s and ws.month = '%s' and ws.year = '%s' and ws.state= 'done'
                '''%(emp,month,year)
        cr.execute(sql)
        kq = cr.fetchall()
        total_days = 0
        total_a = 0
        total_b = 0
        total_c = 0
        shift_allowance_a = 0
        shift_allowance_b = 0
        shift_allowance_c = 0
        total_shift_allowance = 0
        total_lop = 0
        if kq:
            leave_detail_obj = self.pool.get('arul.hr.employee.leave.details')
            sql = '''
                select * from arul_hr_employee_leave_details where EXTRACT(year FROM date_from) = %s and EXTRACT(month FROM date_from) = %s and employee_id = %s and leave_type_id in (select id from arul_hr_leave_types where code = 'LOP')
            '''%(year,int(month),emp)
            cr.execute(sql)
            leave_detail_ids = [row[0] for row in cr.fetchall()]
            for leave_detail in leave_detail_obj.browse(cr, uid, leave_detail_ids):
                day_from = leave_detail.date_from[8:10]
                day_to = leave_detail.date_to[8:10]
                for day in range(day_from,day_to+1):
                    total_lop += 1
            for monthly_shift_schedule_id in monthly_shift_schedule_obj.browse(cr,uid,[kq[0][0]],context=context):
                if monthly_shift_schedule_id.day_1:
                    if monthly_shift_schedule_id.day_1.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_1.time_total
                    if monthly_shift_schedule_id.day_1.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_1.time_total
                    if monthly_shift_schedule_id.day_1.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_1.time_total
                if monthly_shift_schedule_id.day_2:
                    if monthly_shift_schedule_id.day_2.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_2.time_total
                    if monthly_shift_schedule_id.day_2.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_2.time_total
                    if monthly_shift_schedule_id.day_2.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_2.time_total
                if monthly_shift_schedule_id.day_3:
                    if monthly_shift_schedule_id.day_3.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_3.time_total
                    if monthly_shift_schedule_id.day_3.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_3.time_total
                    if monthly_shift_schedule_id.day_3.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_3.time_total
                if monthly_shift_schedule_id.day_4:
                    if monthly_shift_schedule_id.day_4.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_4.time_total
                    if monthly_shift_schedule_id.day_4.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_4.time_total
                    if monthly_shift_schedule_id.day_4.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_4.time_total
                if monthly_shift_schedule_id.day_5:
                    if monthly_shift_schedule_id.day_5.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_5.time_total
                    if monthly_shift_schedule_id.day_5.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_5.time_total
                    if monthly_shift_schedule_id.day_5.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_5.time_total
                if monthly_shift_schedule_id.day_6:
                    if monthly_shift_schedule_id.day_6.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_6.time_total
                    if monthly_shift_schedule_id.day_6.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_6.time_total
                    if monthly_shift_schedule_id.day_6.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_6.time_total
                if monthly_shift_schedule_id.day_7:
                    if monthly_shift_schedule_id.day_7.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_7.time_total
                    if monthly_shift_schedule_id.day_7.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_7.time_total
                    if monthly_shift_schedule_id.day_7.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_7.time_total
                if monthly_shift_schedule_id.day_8:
                    if monthly_shift_schedule_id.day_8.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_8.time_total
                    if monthly_shift_schedule_id.day_8.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_8.time_total
                    if monthly_shift_schedule_id.day_8.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_8.time_total
                if monthly_shift_schedule_id.day_9:
                    if monthly_shift_schedule_id.day_9.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_9.time_total
                    if monthly_shift_schedule_id.day_9.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_9.time_total
                    if monthly_shift_schedule_id.day_9.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_9.time_total
                if monthly_shift_schedule_id.day_10:
                    if monthly_shift_schedule_id.day_10.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_10.time_total
                    if monthly_shift_schedule_id.day_10.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_10.time_total
                    if monthly_shift_schedule_id.day_10.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_10.time_total
                if monthly_shift_schedule_id.day_11:
                    if monthly_shift_schedule_id.day_11.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_11.time_total
                    if monthly_shift_schedule_id.day_11.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_11.time_total
                    if monthly_shift_schedule_id.day_11.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_11.time_total
                if monthly_shift_schedule_id.day_12:
                    if monthly_shift_schedule_id.day_12.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_12.time_total
                    if monthly_shift_schedule_id.day_12.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_12.time_total
                    if monthly_shift_schedule_id.day_12.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_12.time_total
                if monthly_shift_schedule_id.day_13:
                    if monthly_shift_schedule_id.day_13.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_13.time_total
                    if monthly_shift_schedule_id.day_13.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_13.time_total
                    if monthly_shift_schedule_id.day_13.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_13.time_total
                if monthly_shift_schedule_id.day_14:
                    if monthly_shift_schedule_id.day_14.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_14.time_total
                    if monthly_shift_schedule_id.day_14.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_14.time_total
                    if monthly_shift_schedule_id.day_14.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_14.time_total
                if monthly_shift_schedule_id.day_15:
                    if monthly_shift_schedule_id.day_15.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_15.time_total
                    if monthly_shift_schedule_id.day_15.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_15.time_total
                    if monthly_shift_schedule_id.day_15.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_15.time_total
                if monthly_shift_schedule_id.day_16:
                    if monthly_shift_schedule_id.day_16.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_16.time_total
                    if monthly_shift_schedule_id.day_16.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_16.time_total
                    if monthly_shift_schedule_id.day_16.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_16.time_total
                if monthly_shift_schedule_id.day_17:
                    if monthly_shift_schedule_id.day_17.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_17.time_total
                    if monthly_shift_schedule_id.day_17.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_17.time_total
                    if monthly_shift_schedule_id.day_17.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_17.time_total
                if monthly_shift_schedule_id.day_18:
                    if monthly_shift_schedule_id.day_18.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_18.time_total
                    if monthly_shift_schedule_id.day_18.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_18.time_total
                    if monthly_shift_schedule_id.day_18.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_18.time_total
                if monthly_shift_schedule_id.day_19:
                    if monthly_shift_schedule_id.day_19.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_19.time_total
                    if monthly_shift_schedule_id.day_19.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_19.time_total
                    if monthly_shift_schedule_id.day_19.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_19.time_total
                if monthly_shift_schedule_id.day_20:
                    if monthly_shift_schedule_id.day_20.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_20.time_total
                    if monthly_shift_schedule_id.day_20.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_20.time_total
                    if monthly_shift_schedule_id.day_20.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_20.time_total
                if monthly_shift_schedule_id.day_21:
                    if monthly_shift_schedule_id.day_21.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_21.time_total
                    if monthly_shift_schedule_id.day_21.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_21.time_total
                    if monthly_shift_schedule_id.day_21.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_21.time_total
                if monthly_shift_schedule_id.day_22:
                    if monthly_shift_schedule_id.day_22.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_22.time_total
                    if monthly_shift_schedule_id.day_22.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_22.time_total
                    if monthly_shift_schedule_id.day_22.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_22.time_total
                if monthly_shift_schedule_id.day_23:
                    if monthly_shift_schedule_id.day_23.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_23.time_total
                    if monthly_shift_schedule_id.day_23.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_23.time_total
                    if monthly_shift_schedule_id.day_23.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_23.time_total
                if monthly_shift_schedule_id.day_24:
                    if monthly_shift_schedule_id.day_24.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_24.time_total
                    if monthly_shift_schedule_id.day_24.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_24.time_total
                    if monthly_shift_schedule_id.day_24.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_24.time_total
                if monthly_shift_schedule_id.day_25:
                    if monthly_shift_schedule_id.day_25.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_25.time_total
                    if monthly_shift_schedule_id.day_25.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_25.time_total
                    if monthly_shift_schedule_id.day_25.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_25.time_total
                if monthly_shift_schedule_id.day_26:
                    if monthly_shift_schedule_id.day_26.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_26.time_total
                    if monthly_shift_schedule_id.day_26.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_26.time_total
                    if monthly_shift_schedule_id.day_26.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_26.time_total
                if monthly_shift_schedule_id.day_27:
                    if monthly_shift_schedule_id.day_27.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_27.time_total
                    if monthly_shift_schedule_id.day_27.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_27.time_total
                    if monthly_shift_schedule_id.day_27.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_27.time_total
                if monthly_shift_schedule_id.day_28:
                    if monthly_shift_schedule_id.day_28.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_28.time_total
                    if monthly_shift_schedule_id.day_28.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_28.time_total
                    if monthly_shift_schedule_id.day_28.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_28.time_total
                if monthly_shift_schedule_id.num_of_month >=29 and monthly_shift_schedule_id.day_29:
                    if monthly_shift_schedule_id.day_29.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_29.time_total
                    if monthly_shift_schedule_id.day_29.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_29.time_total
                    if monthly_shift_schedule_id.day_29.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_29.time_total
                if monthly_shift_schedule_id.num_of_month >=30 and monthly_shift_schedule_id.day_30:
                    if monthly_shift_schedule_id.day_30.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_30.time_total
                    if monthly_shift_schedule_id.day_30.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_30.time_total
                    if monthly_shift_schedule_id.day_30.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_30.time_total
                if monthly_shift_schedule_id.num_of_month >=31 and monthly_shift_schedule_id.day_31:
                    if monthly_shift_schedule_id.day_31.code == 'A':
                        total_a +=1
                        shift_allowance_a += monthly_shift_schedule_id.day_31.time_total
                    if monthly_shift_schedule_id.day_31.code == 'B':
                        total_b +=1
                        shift_allowance_b += monthly_shift_schedule_id.day_31.time_total
                    if monthly_shift_schedule_id.day_31.code == 'C':
                        total_c +=1
                        shift_allowance_c += monthly_shift_schedule_id.day_31.time_total
            total_days = total_a + total_b + total_c
            total_shift_allowance = shift_allowance_a + shift_allowance_b + shift_allowance_c    
        return total_days,total_shift_allowance,total_lop
    
    def generate_payroll(self, cr, uid, ids, context=None):
        details_line = []
        for line in self.browse(cr,uid,ids):
            emp_obj = self.pool.get('hr.employee')
            payroll_emp_struc_obj = self.pool.get('arul.hr.payroll.employee.structure')
            executions_details_obj = self.pool.get('arul.hr.payroll.executions.details')
            earning_structure_obj = self.pool.get('arul.hr.payroll.earning.structure')
            other_deductions_obj = self.pool.get('arul.hr.payroll.other.deductions')
            contribution_obj = self.pool.get('arul.hr.payroll.contribution.parameters')
            employee_ids = emp_obj.search(cr, uid, [('payroll_area_id','=',line.payroll_area_id.id)])
            for p in emp_obj.browse(cr,uid,employee_ids):
                payroll_executions_details_ids = executions_details_obj.search(cr, uid, [('payroll_executions_id', '=', line.id), ('employee_id', '=', p.id)], context=context)
                if payroll_executions_details_ids:
                    executions_details_obj.unlink(cr, uid, payroll_executions_details_ids, context=context) 
                vals_earning_struc = []
                vals_other_deductions = []
                emp_struc_ids = payroll_emp_struc_obj.search(cr,uid,[('employee_id','=',p.id)]) 
                emp_esi_limit = 0
                emp_esi_con = 0
                emp_pf_con = 0
                emp_lwf_amt = 0
                emp_esi_con_amount = 0
                emp_pf_con_amount = 0
                if emp_struc_ids:
                    payroll_emp_struc = payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0])
                    contribution_ids = contribution_obj.search(cr, uid, [('employee_category_id','=',payroll_emp_struc.employee_category_id.id),('sub_category_id','=',payroll_emp_struc.sub_category_id.id)])
                    if contribution_ids:
                        contribution = contribution_obj.browse(cr, uid, contribution_ids[0])
                        emp_esi_limit = contribution.emp_esi_limit
                        if line.month=='12':
                            emp_lwf_amt = contribution.emp_lwf_amt
                        emp_esi_con = contribution.emp_esi_con
                        emp_pf_con = contribution.emp_pf_con
                    total_days,total_shift_allowance,total_lop = self.get_timesheet(cr,uid,p.id,line.month,line.year,context=context)
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
                        for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if other_deductions_id.deduction_parameters_id.code == 'PF.D':
                                pfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'P.D':
                                pd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vpfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'ESI.D':
                                esid = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'F.D':
                                fd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'L.D':
                                ld = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'I.D':
                                ind = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'PT':
                                pt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LWF':
                                lwf = other_deductions_id.float

                        fd += total_fd
                        
                        total_deduction = pfd + pd + vpfd + esid + fd + ld + ind +  pt + lwf    
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'PF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pfd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'P.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': vpfd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'ESI.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': esid,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'F.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': fd,
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
                            if _other_deductions_id.deduction_parameters_id.code == 'PT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pt,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'LWF':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': lwf,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'TOTAL_DEDUCTION':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': total_deduction,
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
                            if earning_struc_id.earning_parameters_id.code == 'LTA':
                                lta = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MED':
                                med = earning_struc_id.float
                                
                        total_earning = basic + da + c + hra + fa + pc + cre + ea +spa + la + aa + sha + oa + lta + med
                        gross_before = basic + c + hra  +spa + ea + oa
                        if total_lop:
                            gross_sal = gross_before/calendar_days*(total_days-total_lop)
                            lop = gross_before - gross_sal
                        else:
                            gross_sal = gross_before
                            lop = 0
                        total_deduction += lop
                        net_sala = gross_sal - total_deduction
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'LOP':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': lop,
                                    }))
                        for _earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if _earning_struc_id.earning_parameters_id.code == 'BASIC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': basic,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'DA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': da,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'C':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': c,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'HRA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': hra,
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
                                          'float': ea,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SpA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': spa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': la,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'AA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': aa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'ShA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': sha,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'OA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': oa,
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
                            if _earning_struc_id.earning_parameters_id.code == 'TOTAL_EARNING':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': total_earning,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'GROSS_SALARY':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': gross_sal,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'NET':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_sala,
                                    }))
                    
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
                        for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if other_deductions_id.deduction_parameters_id.code == 'PF.D':
                                pfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'P.D':
                                pd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vpfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'ESI.D':
                                esid = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'F.D':
                                fd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'L.D':
                                ld = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'I.D':
                                ind = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'PT':
                                pt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LWF':
                                lwf = other_deductions_id.float
                                
                        fd += total_fd
                        
                        total_deduction = pfd + pd + vpfd + esid + fd + ld + ind +  pt + lwf    
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'PF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pfd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'P.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': vpfd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'ESI.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': esid,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'F.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': fd,
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
                            if _other_deductions_id.deduction_parameters_id.code == 'PT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pt,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'LWF':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': lwf,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'TOTAL_DEDUCTION':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': total_deduction,
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
                            if earning_struc_id.earning_parameters_id.code == 'LTA':
                                lta = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MED':
                                med = earning_struc_id.float
                        spa = spa/(calendar_days - 4)*total_days  
                        total_earning = basic + da + c + hra + fa + pc + cre + ea +spa + la + aa + sha + oa + lta + med
                        gross_before = basic + c + hra  +spa + ea + oa + da + la + aa
                        if total_lop:
                            gross_sal = gross_before/calendar_days*(total_days-total_lop)
                            lop = gross_before - gross_sal
                        else:
                            gross_sal = gross_before
                            lop = 0
                        lop = gross_before - gross_sal
                        total_deduction += lop
                        net_sala = gross_sal - total_deduction
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'LOP':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': lop,
                                    }))
                        for _earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if _earning_struc_id.earning_parameters_id.code == 'BASIC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': basic,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'DA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': da,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'C':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': c,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'HRA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': hra,
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
                                          'float': ea,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SpA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': spa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': la,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'AA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': aa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'ShA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': sha,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'OA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': oa,
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
                            if _earning_struc_id.earning_parameters_id.code == 'TOTAL_EARNING':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': total_earning,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'GROSS_SALARY':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': gross_sal,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'NET':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_sala,
                                    }))  
                    
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
                        for other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if other_deductions_id.deduction_parameters_id.code == 'PF.D':
                                pfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'P.D':
                                pd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vpfd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'ESI.D':
                                esid = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'F.D':
                                fd = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'L.D':
                                ld = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'I.D':
                                ind = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'PT':
                                pt = other_deductions_id.float
                            if other_deductions_id.deduction_parameters_id.code == 'LWF':
                                lwf = other_deductions_id.float
                        
                        fd += total_fd        
                        
                        total_deduction = pfd + pd + vpfd + esid + fd + ld + ind +  pt + lwf    
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'PF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pfd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'P.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'VPF.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': vpfd,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'ESI.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': esid,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'F.D':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': fd,
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
                            if _other_deductions_id.deduction_parameters_id.code == 'PT':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': pt,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'LWF':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': lwf,
                                    }))
                            if _other_deductions_id.deduction_parameters_id.code == 'TOTAL_DEDUCTION':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': total_deduction,
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
                            if earning_struc_id.earning_parameters_id.code == 'LTA':
                                lta = earning_struc_id.float
                            if earning_struc_id.earning_parameters_id.code == 'MED':
                                med = earning_struc_id.float
                        spa = spa/(26 - 4)*total_days 
                        oa = total_shift_allowance + total_days*4 + la  
                        total_earning = basic + da + c + hra + fa + pc + cre + ea +spa + la + aa + sha + oa + lta + med
                        gross_before = basic + c + hra  +spa + oa + da + ea
                        if total_lop:
                            gross_sal = gross_before/26*(total_days-total_lop)
                            lop = gross_before - gross_sal
                        else:
                            gross_sal = gross_before
                            lop = 0
                        lop = gross_before - gross_sal
                        total_deduction += lop
                        net_sala = gross_sal - total_deduction
                        for _other_deductions_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_other_deductions_line:
                            if _other_deductions_id.deduction_parameters_id.code == 'LOP':
                                vals_other_deductions.append((0,0, {
                                          'deduction_parameters_id':_other_deductions_id.deduction_parameters_id.id,
                                          'float': lop,
                                    }))
                        for _earning_struc_id in payroll_emp_struc_obj.browse(cr,uid,emp_struc_ids[0]).payroll_earning_structure_line:
                            if _earning_struc_id.earning_parameters_id.code == 'BASIC':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': basic,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'DA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': da,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'C':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': c,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'HRA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': hra,
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
                                          'float': ea,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'SpA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': spa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'LA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': la,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'AA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': aa,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'ShA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': sha,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'OA':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': oa,
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
                            if _earning_struc_id.earning_parameters_id.code == 'TOTAL_EARNING':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': total_earning,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'GROSS_SALARY':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': gross_sal,
                                    }))
                            if _earning_struc_id.earning_parameters_id.code == 'NET':
                                vals_earning_struc.append((0,0, {
                                          'earning_parameters_id':_earning_struc_id.earning_parameters_id.id,
                                          'float': net_sala,
                                    }))
                    if gross_sal >= emp_esi_limit:
                        emp_esi_con_amount = 0
                    else:
                        emp_esi_con_amount = total_earning*emp_esi_con/100
                    base_amount = basic + da - lop
                    emp_pf_con_amount = base_amount*emp_pf_con/100
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
                        'emp_esi_limit': emp_esi_limit,
                        'emp_esi_con': emp_esi_con_amount,
                        'emp_pf_con': emp_pf_con_amount,
                        'emp_lwf_amt': emp_lwf_amt,
                      }
                executions_details_id = executions_details_obj.create(cr,uid,rs)
                
        return True           
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
