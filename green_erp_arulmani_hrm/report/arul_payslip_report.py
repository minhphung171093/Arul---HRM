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
        })
        
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['month']

    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year']

    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        emp_ids = wizard_data['employee_ids']
        month=wizard_data['month']
        year=wizard_data['year']
        payroll_obj = self.pool.get('arul.hr.payroll.executions.details')
        res = []
        for emp_id in emp_ids :
            payroll_ids = payroll_obj.search(self.cr, self.uid,[('month','=',month),('year','=',year),('employee_id','=',emp_id),('payroll_executions_id.state','=','approve')])
            basic = 0
            hra = 0
            conv = 0
            gross = 0
            spa = 0
            oa = 0
            tatal_erning = 0
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
            if payroll_ids:
                payroll = payroll_obj.browse(self.cr, self.uid, payroll_ids[0])
                epf = payroll.emp_pf_con
                esi_limit = payroll.emp_esi_limit
                esi_con = payroll.emp_esi_con
                lwf = payroll.emp_lwf_amt
                for earning in payroll.earning_structure_line:
                    if earning.earning_parameters_id.code=='BASIC':
                        basic += earning.float
                    if earning.earning_parameters_id.code=='HRA':
                        hra += earning.float
                    if earning.earning_parameters_id.code=='C':
                        conv += earning.float
                    if earning.earning_parameters_id.code=='GROSS_SALARY':
                        gross += earning.float
                    if earning.earning_parameters_id.code=='SpA':
                        spa += earning.float
                    if earning.earning_parameters_id.code=='OA':
                        oa += earning.float
                    if earning.earning_parameters_id.code=='TOTAL_EARNING':
                        tatal_erning += earning.float
                    if earning.earning_parameters_id.code=='NET':
                        net += earning.float                        
                for deduction in payroll.other_deduction_line:
                    if deduction.deduction_parameters_id.code=='VPF.D':
                        vpf += earning.float
                    if deduction.deduction_parameters_id.code=='PT':
                        pt += earning.float
                    if deduction.deduction_parameters_id.code=='L.D':
                        loan += earning.float
#                     if earning.earning_parameters_id.code=='PF.D':
#                         epf += earning.float
                    if deduction.deduction_parameters_id.code=='TOTAL_DEDUCTION':
                        total_ded += earning.float
                    if deduction.deduction_parameters_id.code=='LOP':
                        lop += earning.float
                           

                res.append({
                    'emp_name': payroll.employee_id.name + ' ' + (payroll.employee_id.last_name and payroll.employee_id.last_name or ''),
                    'emp_code':payroll.employee_id.employee_id,
                    'emp_designation':payroll.designation_id.name,
                    'emp_doj': payroll.employee_id.date_of_joining,
                    'basic': basic,
                    'hra': hra,
                    'conv': conv,
                    'gross': gross,
                    'spa': spa,
                    'oa': oa,
                    'tatal_erning': tatal_erning,
                    'net':net,
                    'total_ded':total_ded,
                    'pt':pt,
                    'lop':lop,
                    'vpf': vpf,
                    'esi_con': esi_con,
                    'esi_limit':esi_limit,
                    'loan': loan ,
                    'epf': epf,
                    'lwf':lwf,
                
                })
        return res
                
                
                    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

