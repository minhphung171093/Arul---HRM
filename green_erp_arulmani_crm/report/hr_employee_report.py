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
        emp_obj = self.pool.get('hr.employee')
        if active_selection=='active':
            emp_ids = emp_obj.search(self.cr, self.uid, [('employee_active','=', True)])
        elif active_selection=='inactive':
            emp_ids = emp_obj.search(self.cr, self.uid, [('employee_active','=',False)])
        else:
            emp_ids = emp_obj.search(self.cr, self.uid, [])
            
        for emp in emp_obj.browse(self.cr, self.uid, emp_ids):
            payroll_employee_obj = self.pool.get('arul.hr.payroll.employee.structure')
            payroll_employee_ids = payroll_employee_obj.search(self.cr, self.uid, [('employee_id','=', emp.id)])
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
                    if earning.earning_parameters_id.code=='GROSS_SALARY':
                        gross = earning.float
                    if earning.earning_parameters_id.code=='LTA':
                        lta = earning.float    
                res.append({
                    'code': emp.employee_id,
                    'name': emp.name,
                    'birthday': emp.birthday,
                    'date_of_wedding': emp.date_of_wedding,
                    'date_of_joining': emp.date_of_joining,
                    'date_of_resignation': emp.date_of_resignation,
                    'designation': emp.job_id.name,
                    'category': emp.employee_category_id.name,
                    'department': emp.department_id.name,
                    'email': emp.work_email,
                    'mobile': emp.work_phone,
                    'communication_address': emp.address_id.name,
                    'permanent_address': emp.street,
                    'blood_group': emp.blood_group,
                    'emergency_contact': emp.personal_contact,
                    'bank_acc': emp.bank_account_id.name,
                    'grade': emp.employee_grade_id.name,
#                      
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
            
#     def get_emp(self):
#         wizard_data = self.localcontext['data']['form']
#         active_selection = wizard_data['active_selection']
#         res=[]
#         emp_obj = self.pool.get('hr.employee')
#         if active_selection=='active':
#             emp_ids = emp_obj.search(self.cr, self.uid, [('employee_active','=', True)])
#             if emp_ids:
#                 payroll_employee_obj = self.pool.get('arul.hr.payroll.employee.structure')
#             emp = emp_obj.browse(self.cr, self.uid, emp_ids[0])
#                 payroll_employee_ids = payroll_employee_obj.search(self.cr, self.uid, [('employee_id','=', emp.id)])
#                 payroll = payroll_employee_obj.browse(self.cr, self.uid, payroll_employee_ids[0])
#                 for earning in payroll.payroll_earning_structure_line:
#                     if earning.earning_parameters_id.code=='BASIC':
#                         basic = earning.float
#                     if earning.earning_parameters_id.code=='DA':
#                         da = earning.float
#                     if earning.earning_parameters_id.code=='HRA':
#                         hra = earning.float
#                     if earning.earning_parameters_id.code=='C':
#                         conv = earning.float
#                     if earning.earning_parameters_id.code=='EA':
#                         ea = earning.float
#                     if earning.earning_parameters_id.code=='LA':
#                         la = earning.float
#                     if earning.earning_parameters_id.code=='AA':
#                         aa = earning.float
#                     if earning.earning_parameters_id.code=='SpA':
#                         spa = earning.float
#                     if earning.earning_parameters_id.code=='OA':
#                         oa = earning.float
#                     if earning.earning_parameters_id.code=='GROSS_SALARY':
#                         gross = earning.float
#                     if earning.earning_parameters_id.code=='LTA':
#                         lta = earning.float
#             res.append({
#                     'code': emp.employee_id,
#                     'name': emp.name,
#                     'birthday': emp.birthday,
#                     'date_of_wedding': emp.date_of_wedding,
#                     'date_of_joining': emp.date_of_joining,
#                     'date_of_resignation': emp.date_of_resignation,
#                     'designation': emp.job_id.name,
#                     'category': emp.employee_category_id.name,
#                     'department': emp.department_id.name,
#                     'email': emp.work_mail,
#                     'mobile': emp.work_phone,
#                     'communication_address': emp.address_id,
#                     'permanent_address': emp.street,
#                     'blood_group': emp.blood_group,
#                     'emergency_contact': emp.personal_contact,
#                     'bank_acc': emp.bank_account_id.name,
#                     
#                     'basic': basic,
#                     'da': da,
#                     'hra': hra,
#                     'conv': conv,
#                     'ea': ea,
#                     'la': la,
#                     'aa': aa,
#                     'spa': spa,
#                     'oa': oa,
#                     'gross': gross,
#                     'lta': lta,
                    
#                 })
#         elif active_selection=='inactive':
#             emp_ids = emp_obj.search(self.cr, self.uid, [('employee_active','=',False)])
#             payroll_employee_obj = self.pool.get('arul.hr.payroll.employee.structure')
#             emp = emp_obj.browse(self.cr, self.uid, self.emp_ids[0])
#                 payroll_employee_ids = payroll_employee_obj.search(self.cr, self.uid, [('employee_id','=', emp.id)])
#                 payroll = payroll_employee_obj.browse(self.cr, self.uid, self.payroll_employee_ids[0])
#                 for earning in payroll.payroll_earning_structure_line:
#                     if earning.earning_parameters_id.code=='BASIC':
#                         basic = earning.float
#                     if earning.earning_parameters_id.code=='DA':
#                         da = earning.float
#                     if earning.earning_parameters_id.code=='HRA':
#                         hra = earning.float
#                     if earning.earning_parameters_id.code=='C':
#                         conv = earning.float
#                     if earning.earning_parameters_id.code=='EA':
#                         ea = earning.float
#                     if earning.earning_parameters_id.code=='LA':
#                         la = earning.float
#                     if earning.earning_parameters_id.code=='AA':
#                         aa = earning.float
#                     if earning.earning_parameters_id.code=='SpA':
#                         spa = earning.float
#                     if earning.earning_parameters_id.code=='OA':
#                         oa = earning.float
#                     if earning.earning_parameters_id.code=='GROSS_SALARY':
#                         gross = earning.float
#                     if earning.earning_parameters_id.code=='LTA':
#                         lta = earning.float
#             res.append({
#                     'code': emp.employee_id,
#                     'name': emp.name,
#                     'birthday': emp.birthday,
#                     'date_of_wedding': emp.date_of_wedding,
#                     'date_of_joining': emp.date_of_joining,
#                     'date_of_resignation': emp.date_of_resignation,
#                     'designation': emp.job_id.name,
#                     'category': emp.employee_category_id.name,
#                     'department': emp.department_id.name,
#                     'email': emp.work_mail,
#                     'mobile': emp.work_phone,
#                     'communication_address': emp.address_id,
#                     'permanent_address': emp.street,
#                     'blood_group': emp.blood_group,
#                     'emergency_contact': emp.personal_contact,
#                     'bank_acc': emp.bank_account_id.name,

#                     'basic': basic,
#                     'da': da,
#                     'hra': hra,
#                     'conv': conv,
#                     'ea': ea,
#                     'la': la,
#                     'aa': aa,
#                     'spa': spa,
#                     'oa': oa,
#                     'gross': gross,
#                     'lta': lta,
#                 })
#         else:
#             emp_ids = emp_obj.search(self.cr, self.uid, [])
#                 payroll_employee_obj = self.pool.get('arul.hr.payroll.employee.structure')
#             emp = emp_obj.browse(self.cr, self.uid, self.emp_ids[0])
#                 payroll_employee_ids = payroll_employee_obj.search(self.cr, self.uid, [('employee_id','=', emp.id)])
#                 payroll = payroll_employee_obj.browse(self.cr, self.uid, self.payroll_employee_ids[0])
#                 for earning in payroll.payroll_earning_structure_line:
#                     if earning.earning_parameters_id.code=='BASIC':
#                         basic = earning.float
#                     if earning.earning_parameters_id.code=='DA':
#                         da = earning.float
#                     if earning.earning_parameters_id.code=='HRA':
#                         hra = earning.float
#                     if earning.earning_parameters_id.code=='C':
#                         conv = earning.float
#                     if earning.earning_parameters_id.code=='EA':
#                         ea = earning.float
#                     if earning.earning_parameters_id.code=='LA':
#                         la = earning.float
#                     if earning.earning_parameters_id.code=='AA':
#                         aa = earning.float
#                     if earning.earning_parameters_id.code=='SpA':
#                         spa = earning.float
#                     if earning.earning_parameters_id.code=='OA':
#                         oa = earning.float
#                     if earning.earning_parameters_id.code=='GROSS_SALARY':
#                         gross = earning.float
#                     if earning.earning_parameters_id.code=='LTA':
#                         lta = earning.float
#             res.append({
#                     'code': emp.employee_id,
#                     'name': emp.name,
#                     'birthday': emp.birthday,
#                     'date_of_wedding': emp.date_of_wedding,
#                     'date_of_joining': emp.date_of_joining,
#                     'date_of_resignation': emp.date_of_resignation,
#                     'designation': emp.job_id.name,
#                     'category': emp.employee_category_id.name,
#                     'department': emp.department_id.name,
#                     'email': emp.work_mail,
#                     'mobile': emp.work_phone,
#                     'communication_address': emp.address_id,
#                     'permanent_address': emp.street,
#                     'blood_group': emp.blood_group,
#                     'emergency_contact': emp.personal_contact,
#                     'bank_acc': emp.bank_account_id.name,

#                     'basic': basic,
#                     'da': da,
#                     'hra': hra,
#                     'conv': conv,
#                     'ea': ea,
#                     'la': la,
#                     'aa': aa,
#                     'spa': spa,
#                     'oa': oa,
#                     'gross': gross,
#                     'lta': lta,
#                 })
#         
#         return res
#         stt = 0
#         if not self.emp_ids:
#             self.get_header();
#         result = []
#         list_emp = str(self.emp_ids).replace("[","(")
#         list_emp = list_emp.replace("]",")")
#         sql = ''' 
#                 select hr.employee_id, hr.name_related as first_name, hr.last_name, hr.date_of_joining, hj.name as designation,
#                     emc.name as employeegroup, emsc.name as employeesubgroup, case when hr.employee_active = true then 'Active' else 'Withdrawn' end as employmentstatus,
#                     hd.name as organizationalunit, hr.street ||', '|| hr.street2 ||', '|| hr.city ||', '|| recs.name ||', '|| rec.name as personalarea, hr.basic, hr.conveyance, hr.lunch_allowance,hr.special_allowance,hr.gross,hr.mra,
#                     hr.ctc,hr.hra,hr.education_allowance,hr.admin_allowance,hr.other_allowance,hr.lta,hr.bonus
#                 from hr_employee hr
#                 left join hr_job hj on hr.job_id = hj.id
#                 left join vsis_hr_employee_category emc on hr.employee_category_id = emc.id
#                 left join hr_employee_sub_category emsc on hr.employee_sub_category_id = emsc.id
#                 left join hr_department hd on hr.department_id = hd.id
#                 left join res_country_state recs on hr.state_id = recs.id 
#                 left join res_country rec on hr.country_id = rec.id
#                 where hr.id in %s
#               '''%(list_emp)
#         self.cr.execute(sql)
#         for line in self.cr.dictfetchall():
#             stt += 1
#             dic = {
#                    'stt': stt,
#                    'employee_id': line['employee_id'],
#                    'first_name': line['first_name'],
#                    'last_name': line['last_name'],
#                    'date_of_joining': line['date_of_joining'],
#                    'designation': line['designation'],
#                    'employeegroup': line['employeegroup'] ,
#                    'employeesubgroup': line['employeesubgroup'] ,
#                    'employmentstatus': line['employmentstatus'] ,
#                    'organizationalunit': line['organizationalunit'] ,
#                    'personalarea': line['personalarea'] ,
#                    'basic': line['basic'] and line['basic'] or 0 ,
#                    'conveyance': line['conveyance'] ,
#                    'lunch_allowance': line['lunch_allowance'] ,
#                    'special_allowance': line['special_allowance'] ,
#                    'gross': line['gross'] ,
#                    'mra': line['mra'] ,
#                    'ctc': line['ctc'] ,
#                    'hra': line['hra'] ,
#                    'education_allowance': line['education_allowance'] ,
#                    'admin_allowance': line['admin_allowance'] ,
#                    'other_allowance': line['other_allowance'] ,
#                    'lta': line['lta'] ,
#                    'bonus': line['bonus'] ,
#             }
#             result.append(dic)
#         return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

