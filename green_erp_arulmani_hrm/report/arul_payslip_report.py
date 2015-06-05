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
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_month':self.get_month,
            'get_year':self.get_year,
            'get_emp':self.get_emp,
            'get_fh_name': self.get_fh_name,
            'get_month_name': self.get_month_name,
            'get_statutory': self.get_statutory,
        })
    
    def get_fh_name(self, employee_id):
        name = ''
        if employee_id:
            employee = self.pool.get('hr.employee').browse(self.cr, self.uid, employee_id)
            for line in employee.family_ids:
                if line.relation_type == 'father':
                    name = line.name
                    break
        return name
    
    def get_statutory(self, employee_id):
        res = {
            'pf_no': '',
            'esi_no': '',
        }
        if employee_id:
            employee = self.pool.get('hr.employee').browse(self.cr, self.uid, employee_id)
            pf_no = ''
            esi_no = ''
            for line in employee.statutory_ids:
                if line.name:
                    pf_no = line.name
                if line.esi_no:
                    esi_no = line.esi_no
                break
            res.update({'pf_no': str(pf_no),'esi_no': str(esi_no)})
        return res
    
    def get_month_name(self, month):
        month = int(month)
        _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
        d = _months[month]
        return d
    
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return self.get_month_name(wizard_data['month'])
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']
    
    def length_month(self,year, month):
        if month == 2 and (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
            value =  29
        else: 
            value =  [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
        return value

    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        emp_ids = wizard_data['employee_ids']
        month=wizard_data['month']
        year=wizard_data['year']
        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
        res = []
        #raise osv.except_osv(_('Warning!'),_('tst'))
        for emp_id in emp_ids :
            payroll_ids = payroll_obj.search(self.cr, self.uid,[('month','=',month),('year','=',year),('employee_id','=',emp_id),('payroll_executions_id.state','in',['confirm','approve'])])
            basic = 0
            da = 0
            hra = 0
            conv = 0
            la = 0
            ea = 0
            aa = 0
            oa = 0
            ma = 0
            gross = 0
            spa = 0
            oa = 0
            shd = 0
            total_erning = 0
            net = 0
            total_ded = 0
            pt = 0
            lop = 0
            vpf = 0
            esi_limit = 0
            esi_con = 0
            loan = 0
            epf = 0
            lwf = 0
            total_fd = 0
            pf_gros = 0
            i_lic_prem = 0
            i_others = 0 
            l_vvti_loan = 0 
            l_lic_hfl = 0 
            l_hdfc = 0 
            l_tmb = 0 
            l_sbt = 0 
            l_others = 0
            md1 = 0
            lic = 0
            
            if payroll_ids:
                payroll = payroll_obj.browse(self.cr, self.uid, payroll_ids[0])
                epf = payroll.emp_pf_con
                esi_limit = payroll.emp_esi_limit
                esi_con = payroll.emp_esi_con
                lwf = payroll.emp_lwf_amt
                
                sql = '''
                        select case when sum(employee_amt)!=0 then sum(employee_amt) else 0 end total_fd from meals_details where emp_id = %s and meals_id in (select id from meals_deduction where meals_for='employees' and EXTRACT(year FROM meals_date) = %s and EXTRACT(month FROM meals_date) = %s)
                    '''%(emp_id,year,int(month))
                self.cr.execute(sql)
                total_fd = self.cr.dictfetchone()['total_fd']
                
                for earning in payroll.earning_structure_line:
                    if earning.earning_parameters_id.code=='BASIC':
                        basic += earning.float
                    if earning.earning_parameters_id.code=='DA':
                        da += earning.float
                    if earning.earning_parameters_id.code=='HRA':
                        hra += earning.float
                    if earning.earning_parameters_id.code=='C':
                        conv += earning.float
                    if earning.earning_parameters_id.code=='SpA':
                        spa += earning.float
                    
                    if earning.earning_parameters_id.code=='LA':
                        la += earning.float
                    if earning.earning_parameters_id.code=='EA':
                        ea += earning.float
                    if earning.earning_parameters_id.code=='AA':
                        aa += earning.float     
                    if earning.earning_parameters_id.code=='OA':
                        oa += earning.float
                    if earning.earning_parameters_id.code=='MA':
                        ma += earning.float
                    if earning.earning_parameters_id.code=='SHD':
                        shd += earning.float
                    
                    if earning.earning_parameters_id.code=='TOTAL_EARNING':
                        total_erning += earning.float
                    if earning.earning_parameters_id.code=='NET':
                        net += earning.float                        
                for deduction in payroll.other_deduction_line:
                    if deduction.deduction_parameters_id.code=='VPF.D':
                        vpf += deduction.float
                    if deduction.deduction_parameters_id.code=='IT': #PT
                        pt += deduction.float
                    if deduction.deduction_parameters_id.code=='L.D':
                        loan += deduction.float
#                     if earning.earning_parameters_id.code=='PF.D':
#                         epf += earning.float
                    if deduction.deduction_parameters_id.code=='TOTAL_DEDUCTION':
                        total_ded += deduction.float
                    if deduction.deduction_parameters_id.code=='LOP':
                        lop += deduction.float
                    if deduction.deduction_parameters_id.code == 'INS_LIC_PREM':
                        i_lic_prem += deduction.float
                    if deduction.deduction_parameters_id.code == 'INS_OTHERS':
                        i_others += deduction.float
                    if deduction.deduction_parameters_id.code == 'LOAN_VVTI':
                        l_vvti_loan += deduction.float
                    if deduction.deduction_parameters_id.code == 'LOAN_LIC_HFL':
                        l_lic_hfl += deduction.float
                    if deduction.deduction_parameters_id.code == 'LOAN_HDFC':
                        l_hdfc += deduction.float
                    if deduction.deduction_parameters_id.code == 'LOAN_TMB':
                        l_tmb += deduction.float
                    if deduction.deduction_parameters_id.code == 'LOAN_SBT':
                        l_sbt += deduction.float
                    if deduction.deduction_parameters_id.code == 'LOAN_OTHERS':
                        l_others += deduction.float
                           
                calendar_days = self.length_month(int(year),int(month))
                
                sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
                SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s 
                AND EXTRACT(month FROM date_from) = %s AND employee_id =%s AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('LOP'))
                '''%(year,month,emp_id)
                self.cr.execute(sql)
                lop_leave =  self.cr.fetchone()
                tpt_lop_leave = lop_leave[0]
                #total_no_of_leave = tpt_lop_leave
                
                sql = '''
                SELECT CASE WHEN SUM(days_total)!=0 THEN 
                SUM(days_total) ELSE 0 END days_total FROM 
                arul_hr_employee_leave_details WHERE EXTRACT(year FROM date_from) = %s 
                AND EXTRACT(month FROM date_from) = %s AND employee_id =%s AND
                leave_type_id in (select id from arul_hr_leave_types where code in ('ESI'))
                '''%(year,month,emp_id)
                self.cr.execute(sql)
                esi_leave =  self.cr.fetchone()
                tpt_esi_leave = esi_leave[0]
                #total_no_of_leave = tpt_lop_esi
                
                special_holiday_worked_count =  0  
                #SELECT COUNT(work_date) AS date_holiday_count                             
                sql = '''
                        SELECT CASE WHEN SUM(total_shift_worked1)!=0 
                            THEN SUM(total_shift_worked1) ELSE 0 END total_shift_worked 
                        FROM arul_hr_punch_in_out_time 
                        WHERE work_date IN (SELECT date FROM arul_hr_holiday_special 
                        WHERE EXTRACT(month from date)=%s AND EXTRACT(year from date)=%s ) AND 
                        EXTRACT(month from work_date)=%s AND EXTRACT(year from work_date)=%s AND
                        punch_in_out_id IN (SELECT id FROM arul_hr_employee_attendence_details WHERE employee_id=%s)
                    '''%(month, year, month, year, emp_id)
                self.cr.execute(sql)
                special_holiday_worked_count = self.cr.dictfetchone()['total_shift_worked']
                
                title=''
                if payroll.employee_id.gender=='male':
                    title='Mr'
                elif payroll.employee_id.gender=='female':
                    if payroll.employee_id.marital=='married':
                        title='Ms'
                    elif payroll.employee_id.marital=='single':
                        title='Miss'
                        
                base_amount = basic + da 
                #vpf = base_amount * vpf / 100
                
                total_working_days = 0
                tdw = 0
                ndw = 0
                if payroll.employee_id.employee_category_id.code=='S3':
                    tdw = 26 
                    ndw = tdw - (tpt_lop_leave + tpt_esi_leave)
                else:
                    tdw = calendar_days
                    ndw = tdw - (tpt_lop_leave + tpt_esi_leave)
                
                sql = '''
                    select extract(day from date_of_joining) doj from hr_employee where extract(year from date_of_joining)= %s and 
                      extract(month from date_of_joining)= %s and id=%s
                    '''%(year,month,emp_id)
                self.cr.execute(sql)
                k = self.cr.fetchone()
                if k:
                    new_emp_day = k[0]    
                    if payroll.employee_id.employee_category_id.code=='S1':
                        tdw = calendar_days          
                        temp = calendar_days - new_emp_day + 1
                        ndw = temp - (tpt_lop_leave + tpt_esi_leave)
                        
                    if payroll.employee_id.employee_category_id.code=='S2':  
                        tdw = calendar_days         
                        temp = calendar_days - new_emp_day + 1
                        ndw = temp - (tpt_lop_leave + tpt_esi_leave)
                        
                    if payroll.employee_id.employee_category_id.code=='S3': 
                        tdw = 26           
                        temp = 26 - new_emp_day - 4 + 1 # 4 is weekly off
                        ndw = temp - (tpt_lop_leave + tpt_esi_leave)
                        
                        
                res.append({
                    'emp_id': emp_id,
                    'emp_name': payroll.employee_id.name + ' ' + (payroll.employee_id.last_name and payroll.employee_id.last_name or ''),
                    'emp_code':payroll.employee_id.employee_id,
                    'emp_designation':payroll.designation_id.name,
                    'emp_title':title,
                    'emp_doj': payroll.employee_id.date_of_joining and (payroll.employee_id.date_of_joining[8:10]+'.'+payroll.employee_id.date_of_joining[5:7]+'.'+payroll.employee_id.date_of_joining[:4]) or '',
                    'basic': format(basic,'.2f'),
                    'da':format(da,'.2f'),
                    'hra': format(hra,'.2f'),
                    'conv': format(conv,'.2f'),
                    'pf_gros': format(basic+da,'.2f'),
                    'gross': format(gross,'.2f'),
                    'spa': format(spa,'.2f'),
                    'oa': format(la + ea + aa + oa,'.2f') ,
                    'ma': format(ma,'.2f'),
                    'shd': format(shd,'.2f'),
                    'total_erning': format(total_erning,'.2f'),
                    'net':format(net,'.2f'),
                    'total_ded':format(total_ded,'.2f'),
                    'pt':pt,
                    #'lop':lop, 
                    'lop':tpt_lop_leave,
                    'esi':tpt_esi_leave,
                    'vpf': format(vpf,'.2f'),
                    'esi_con': format(esi_con,'.2f'),
                    'esi_limit':format(esi_limit,'.2f'),
                    'loan': format(loan,'.2f') ,
                    'epf': epf,
                    'lwf':lwf,
                    'total_fd':format(total_fd,'.2f'),
                   
                    'calendar_days':tdw, 
                    'ndw':ndw,
                    'special_holiday_worked_count':special_holiday_worked_count,
                    'md1':format(l_vvti_loan + l_lic_hfl + l_hdfc + l_tmb + l_sbt + l_others,'.2f'),
                    'lic':format(i_lic_prem + i_others,'.2f'),
                
                })
        return res
                
                
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

