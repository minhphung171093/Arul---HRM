# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
#     def __init__(self, cr, uid, name, context):
#         super(Parser, self).__init__(cr, uid, name, context=context)
#         self.user_obj = pooler.get_pool(self.cr.dbname).get('res.users')
#         pool = pooler.get_pool(self.cr.dbname)
#         self.cr = cr
#         self.uid = uid
#         self.emp_ids = False
#         self.localcontext.update({
#               
#             'get_emp': self.get_emp,
#         })
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_emp':self.get_emp,
        })
        
    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        active_selection = wizard_data['active_selection']
        res=[]
        resource_obj = self.pool.get('resource.resource')
        emp_obj = self.pool.get('hr.employee')
        if active_selection=='active':
            emp_ids = resource_obj.search(self.cr, self.uid, [('active','=', True)])
        elif active_selection=='inactive':
            emp_ids = resource_obj.search(self.cr, self.uid, [('active','=',False)])
        else:
            emp_ids = resource_obj.search(self.cr, self.uid, [])
            
        for emp in emp_obj.browse(self.cr, self.uid, emp_ids):
            fa = ''
            mobile = ''
            comu_add = (emp.street or '')+', '+(emp.street2 or '')+', '+(emp.city or '')+', '+(emp.state_id and emp.state_id.name or '')+', '+(emp.zip or '')+', '+(emp.country_id and emp.country_id.name or '') 
            permanent_add = (emp.permanent_street or '')+', '+(emp.permanent_street2 or '')+', '+(emp.permanent_city or '')+', '+(emp.permanent_state_id and emp.permanent_state_id.name or '')+', '+(emp.permanent_zip or '')+', '+(emp.permanent_country_id and emp.permanent_country_id.name or '') 
            if emp.family_ids:
                for father in emp.family_ids:
                    if father.relation_type == 'father':
                        fa = father.name or False
                for father in emp.family_ids:                      
                    if father.emergency_contact == 'yes':
                        mobile = father and father.mobile or False
                        break  
                
            if emp.statutory_ids:
                for statutory in emp.statutory_ids:
                    epf_num = statutory and statutory.name or False
                    epf_no = statutory and statutory.epf_nominee or False
                    esi_num = statutory and statutory.esi_no or False
                    esi_no = statutory and statutory.eis_nominee or False
                    gratuity = statutory and statutory.gratuity_no or False
                    gratuity_no = statutory and statutory.gratuity_nominee or False
                    pan_num = statutory and statutory.pan_no or False
            else:
                epf_num = ''
                epf_no = ''
                esi_num = ''
                esi_no = ''
                gratuity = ''
                gratuity_no = ''
                pan_num = ''
                
            payroll_employee_obj = self.pool.get('arul.hr.payroll.employee.structure')
            payroll_employee_ids = payroll_employee_obj.search(self.cr, self.uid, [('employee_id','=', emp.id)])
            gross = 0
            basic = 0
            da = 0
            hra = 0
            conv = 0
            ea = 0
            aa = 0
            la = 0
            spa = 0
            oa = 0
            lta = 0
            sum = 0
            if payroll_employee_ids:
                payroll = payroll_employee_obj.browse(self.cr, self.uid, payroll_employee_ids[0])
                for earning in payroll.payroll_earning_structure_line:
                    if earning.earning_parameters_id.code=='BASIC':
                        basic = earning.float
                    if earning.earning_parameters_id.code=='DA':
                        da = earning.float
                    if earning.earning_parameters_id.code=='HRA':
                        hra = earning.float
                    if earning.earning_parameters_id.code=='C':
                        conv = earning.float
                    if earning.earning_parameters_id.code=='EA':
                        ea = earning.float
                    if earning.earning_parameters_id.code=='LA':
                        la = earning.float
                    if earning.earning_parameters_id.code=='AA':
                        aa = earning.float
                    if earning.earning_parameters_id.code=='SpA':
                        spa = earning.float
                    if earning.earning_parameters_id.code=='OA':
                        oa = earning.float
                    if earning.earning_parameters_id.code=='LTA':
                        lta = earning.float
                sum = basic + da + hra + conv + ea + la + aa + spa + oa + lta
                gross = basic + da + hra + conv + ea + la + aa + spa + oa
            employee_action_obj = self.pool.get('arul.hr.employee.action.history')
            employee_action_ids = employee_action_obj.search(self.cr, self.uid, [('employee_id','=', emp.id),('action_id.name','=', 'Disciplinary')],order='id desc')
            disiciplinary_actions = ''
            if employee_action_ids:
                action = employee_action_obj.browse(self.cr, self.uid, employee_action_ids[0])
                disiciplinary_actions = action.note
            date_of_wedding = ''
            if emp.date_of_wedding:
                date = datetime.strptime(emp.date_of_wedding, "%Y-%m-%d")
                date_of_wedding = date.strftime('%d-%m-%Y')
            date_of_joining = ''
            if emp.date_of_joining:
                date = datetime.strptime(emp.date_of_joining, "%Y-%m-%d")
                date_of_joining = date.strftime('%d-%m-%Y')
                
            birthday = ''
            if emp.birthday:
                date = datetime.strptime(emp.birthday, "%Y-%m-%d")
                birthday = date.strftime('%d-%m-%Y')
            
            date_of_resignation = ''
            if emp.date_of_retirement:
                date = datetime.strptime(emp.date_of_retirement, "%Y-%m-%d")
                date_of_resignation = date.strftime('%d-%m-%Y')
            
            name_last_name =''
            if emp.last_name:
                name_last_name = str(emp.name) + ' ' + str(emp.last_name)
            else:
                name_last_name = emp.name
                
            bank_acct=''
            if emp.bank_account:
                bank_acct =emp.bank_account 
                
            res.append({
                    'code': emp.employee_id,
                    'name': name_last_name,
                    'birthday': birthday,
                    'date_of_wedding': date_of_wedding,
                    'date_of_joining': date_of_joining,
                    'date_of_resignation': date_of_resignation,
                    'designation': emp.job_id.name,
                    'category': emp.employee_category_id.code,
                    'department': emp.department_id.name,
                    'section': emp.section_id.name,
                    'email': emp.work_email,
                    'mobile': emp.work_phone,
                    'communication_address': comu_add,
                    'permanent_address': permanent_add,
                    'blood_group': emp.blood_group,
                    'emergency_contact': mobile,
                    #'bank_acc': str(emp.bank_account_id.acc_number),
                    'bank_acc': bank_acct,
                    'grade': emp.employee_sub_category_id.code,
                    'fa': fa,
                    'disiciplinary_actions': disiciplinary_actions,
    
                    'epf_num': epf_num,
                    'epf_no': epf_no,
                    'esi_num': esi_num,
                    'esi_no': esi_no,
                    'gratuity': gratuity,
                    'gratuity_no': gratuity_no,
                    'pan_num': pan_num,
                    'sum' : sum,
                    'basic': basic,
                    'da': da,
                    'hra': hra,
                    'conv': conv,
                    'ea': ea,
                    'la': la,
                    'aa': aa,
                    'spa': spa,
                    'oa': oa,
                    'gro': gross,
                    'lta': lta,
                     })
        return res
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

