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
            'get_emp':self.get_emp,
            'get_payslip': self.get_payslip,
        })
        
    def get_month(self):
        return self.ids

    def get_emp(self):
        payroll_obj = self.pool.get('arul.hr.payroll.executions')
        return payroll_obj.browse(self.cr, self.uid, self.ids[0]).payroll_executions_details_line
    
    def get_payslip(self):
        res = []
        payroll_obj = self.pool.get('arul.hr.payroll.executions')
        for line in payroll_obj.browse(self.cr, self.uid, self.ids[0]).payroll_executions_details_line:
            basic = 0
            ea = 0
            da = 0
            hra = 0
            conv = 0
            spa = 0
            oa = 0
            la = 0
            aa = 0
            pfd = 0
            vpf = 0
            esi_con = 0
            fd = 0
            loan = 0
            id = 0
            pt = 0
            lwf = 0
            lop = 0
            total_ear = 0
            total_ded = 0
            net = 0
            for earning in line.earning_structure_line:
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
                if earning.earning_parameters_id.code=='OA':
                    oa += earning.float
                if earning.earning_parameters_id.code=='LA':
                    la += earning.float
                if earning.earning_parameters_id.code=='AA':
                    aa += earning.float
                if earning.earning_parameters_id.code=='EA':
                    ea += earning.float
                if earning.earning_parameters_id.code=='TOTAL_EARNING':
                    total_ear += earning.float
                if earning.earning_parameters_id.code=='NET':
                    net += earning.float                        
            for deduction in line.other_deduction_line:
                if deduction.deduction_parameters_id.code=='PF.D':
                    pfd += deduction.float
                if deduction.deduction_parameters_id.code=='ESI.D':
                    esi_con += deduction.float
                if deduction.deduction_parameters_id.code=='LWF':
                    lwf += deduction.float
                if deduction.deduction_parameters_id.code=='VPF.D':
                    vpf += deduction.float
                if deduction.deduction_parameters_id.code=='F.D':
                    fd += deduction.float
                if deduction.deduction_parameters_id.code=='PT':
                    pt += deduction.float
                if deduction.deduction_parameters_id.code=='L.D':
                    loan += deduction.float
                if deduction.deduction_parameters_id.code=='I.D':
                    id += deduction.float
                if deduction.deduction_parameters_id.code=='TOTAL_DEDUCTION':
                    total_ded += deduction.float
                if deduction.deduction_parameters_id.code=='LOP':
                    lop += deduction.float
            res.append({
                'payslip': line,
                'basic': basic,
                'da': da,
                'hra': hra,
                'conv': conv,
                'spa': spa,
                'oa': oa,
                'la': la,
                'aa': aa,
                'ea': ea,
                'pfd': pfd,
                'vpf': vpf,
                'esi_con': esi_con,
                'fd': fd,
                'loan': loan,
                'id': id,
                'pt': pt,
                'lwf': lwf,
                'lop': lop,
                'total_ear': total_ear,
                'total_ded': total_ded,
                'net': net,
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

