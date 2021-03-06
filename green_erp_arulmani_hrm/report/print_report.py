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
            'get_sub_basic': self.get_sub_basic,
            'get_sub_da': self.get_sub_da,
            'get_sub_hra': self.get_sub_hra,
            'get_sub_conv': self.get_sub_conv,
            'get_sub_spa': self.get_sub_spa,
            'get_sub_oa': self.get_sub_oa,
            'get_sub_ma': self.get_sub_ma,
            'get_sub_la': self.get_sub_la,
            'get_sub_aa': self.get_sub_aa,
            'get_sub_ea': self.get_sub_ea,
            'get_sub_shd': self.get_sub_shd,#
            'get_sub_pfd': self.get_sub_pfd,
            'get_sub_vpf': self.get_sub_vpf,
            'get_sub_esi_con': self.get_sub_esi_con,
            'get_sub_fd': self.get_sub_fd,
            'get_sub_cd': self.get_sub_cd,
            'get_sub_loan': self.get_sub_loan,
            'get_sub_id': self.get_sub_id,
            'get_sub_pt': self.get_sub_pt,
            'get_sub_lwf': self.get_sub_lwf,
            'get_sub_lop': self.get_sub_lop,
            'get_sub_total_ear': self.get_sub_total_ear,
            'get_sub_total_ded': self.get_sub_total_ded,
            'get_sub_net': self.get_sub_net,     
            'get_vpf_amt': self.get_vpf_amt,
            
            'get_sub_i_lic_prem': self.get_sub_i_lic_prem,   
            'get_sub_i_others': self.get_sub_i_others,             
            'get_sub_l_vvti_loan': self.get_sub_l_vvti_loan, 
            'get_sub_l_lic_hfl': self.get_sub_l_lic_hfl, 
            'get_sub_l_hdfc': self.get_sub_l_hdfc, 
            'get_sub_l_tmb': self.get_sub_l_tmb, 
            'get_sub_l_sbt': self.get_sub_l_sbt, 
            'get_sub_l_others': self.get_sub_l_others, 
            'get_sub_it_deduction': self.get_sub_it_deduction,
            'get_date_from': self.get_date_from,
                                           
        })
        
    
    def get_date_from(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')  
    
    def get_vpf_amt(self,net_basic,net_da,vpf_in_percent):               
        #return round(net_basic+net_da*vpf_in_percent/100, 2)
        basic_da = 0.0
        vpf = 0.0
        vpf_in_amt = 0.0
        basic_da = net_basic + net_da
        vpf = vpf_in_percent / 100
        vpf_in_amt = basic_da * vpf
        return round(vpf_in_percent)
    
    def get_sub_basic(self):
        subtotal_basic = 0
        for line in self.get_payslip():
            subtotal_basic += line['basic']          
        return round(subtotal_basic, 2)
    
    def get_sub_da(self):
        subtotal_da = 0
        for line in self.get_payslip():
            subtotal_da += line['da']          
        return round(subtotal_da, 2)
    
    def get_sub_hra(self):
        subtotal_hra = 0
        for line in self.get_payslip():
            subtotal_hra += line['hra']          
        return subtotal_hra
    
    def get_sub_conv(self):
        subtotal_conv = 0
        for line in self.get_payslip():
            subtotal_conv += line['conv']          
        return round(subtotal_conv, 2)
    
    def get_sub_spa(self):
        subtotal_spa = 0
        for line in self.get_payslip():
            subtotal_spa += line['spa']          
        return round(subtotal_spa,2)
    
    def get_sub_oa(self):
        subtotal_oa = 0
        for line in self.get_payslip():
            subtotal_oa += line['oa']          
        return round(subtotal_oa,2)
    
    def get_sub_ma(self):
        subtotal_ma = 0
        for line in self.get_payslip():
            subtotal_ma += line['ma']          
        return round(subtotal_ma, 2)
    
    def get_sub_la(self):
        subtotal_la = 0
        for line in self.get_payslip():
            subtotal_la += line['la']                      
        return round(subtotal_la, 2)
    
    def get_sub_ea(self):
        subtotal_ea = 0
        for line in self.get_payslip():
            subtotal_ea += line['ea']                      
        return round(subtotal_ea, 2)
    
    def get_sub_shd(self):
        subtotal_shd = 0
        for line in self.get_payslip():
            subtotal_shd += line['shd']                      
        return round(subtotal_shd, 2)
    
    def get_sub_aa(self):
        subtotal_aa = 0
        for line in self.get_payslip():
            subtotal_aa += line['aa']          
        return round(subtotal_aa, 2)
    
    def get_sub_pfd(self):
        subtotal_pfd = 0
        for line in self.get_payslip():
            subtotal_pfd += line['pfd']          
        return round(subtotal_pfd, 2)
    
    def get_sub_vpf(self):
        subtotal_vpf = 0
        for line in self.get_payslip():
#             v1 = line['basic'] + line['da']
#             v2 = line['vpf'] / 100
#             v3 = v1 * v2
            vpfd_amt = line['vpf']
            subtotal_vpf += vpfd_amt   
                  
        return round(subtotal_vpf)
    
    def get_sub_esi_con(self):
        subtotal_esi_con = 0
        for line in self.get_payslip():
            subtotal_esi_con += line['esi_con']          
        return round(subtotal_esi_con,2)
    
    def get_sub_fd(self):
        subtotal_fd = 0
        for line in self.get_payslip():
            subtotal_fd += line['fd']          
        return round(subtotal_fd,2)
    def get_sub_cd(self):
        subtotal_fd = 0
        for line in self.get_payslip():
            subtotal_fd += line['cd']          
        return round(subtotal_fd,2)
    
    def get_sub_loan(self):
        subtotal_loan = 0
        for line in self.get_payslip():
            subtotal_loan += line['loan']          
        return round(subtotal_loan,2)
    
    def get_sub_id(self):
        subtotal_id = 0
        for line in self.get_payslip():
            subtotal_id += line['id']          
        return round(subtotal_id,2)
    
    def get_sub_pt(self):
        subtotal_pt = 0
        for line in self.get_payslip():
            subtotal_pt += line['pt']          
        return round(subtotal_pt,2)
    
    def get_sub_lwf(self):
        subtotal_lwf = 0
        for line in self.get_payslip():
            subtotal_lwf += line['lwf']          
        return round(subtotal_lwf,2)
    
    def get_sub_lop(self):
        subtotal_lop = 0
        for line in self.get_payslip():
            subtotal_lop += line['lop']          
        return round(subtotal_lop,2)
    
    def get_sub_total_ear(self):
        subtotal_total_ear = 0
        for line in self.get_payslip():
            subtotal_total_ear += line['total_ear']          
        return round(subtotal_total_ear)
    
    
    def get_sub_total_ded(self):
        subtotal_total_ded = 0
        for line in self.get_payslip():
            subtotal_total_ded += line['total_ded']          
        return round(subtotal_total_ded)
    
    def get_sub_net(self):
        subtotal_net = 0
        for line in self.get_payslip():
            subtotal_net += line['net']          
        return round(subtotal_net,2)
    #TPT
    def get_sub_i_lic_prem(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['i_lic_prem']          
        return round(subtotal_i_lic_prem,2)
    def get_sub_i_others(self):
        subtotal_i_others = 0
        for line in self.get_payslip():
            subtotal_i_others += line['i_others']          
        return round(subtotal_i_others,2)
    def get_sub_l_vvti_loan(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['l_vvti_loan']          
        return round(subtotal_i_lic_prem,2)
    def get_sub_l_lic_hfl(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['l_lic_hfl']          
        return round(subtotal_i_lic_prem,2)
    def get_sub_l_hdfc(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['l_hdfc']          
        return round(subtotal_i_lic_prem,2)
    def get_sub_l_tmb(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['l_tmb']          
        return round(subtotal_i_lic_prem,2)
    def get_sub_l_sbt(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['l_sbt']          
        return round(subtotal_i_lic_prem,2)
    def get_sub_l_others(self):
        subtotal_i_lic_prem = 0
        for line in self.get_payslip():
            subtotal_i_lic_prem += line['l_others']          
        return round(subtotal_i_lic_prem,2)
    
    def get_sub_it_deduction(self):
        subtotal_it = 0
        for line in self.get_payslip():
            subtotal_it += line['it_deduction']          
        return round(subtotal_it,2)
     #TPT END       
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
            shd = 0 #
            pfd = 0
            vpf = 0
            esi_con = 0
            fd = 0
            cd = 0
            loan = 0
            id = 0
            pt = 0
            lwf = 0
            lop = 0
            total_ear = 0
            total_ded = 0
            net = 0
            ma = 0
            
            i_lic_prem = 0
            i_others = 0 
            l_vvti_loan = 0 
            l_lic_hfl = 0 
            l_hdfc = 0 
            l_tmb = 0 
            l_sbt = 0 
            l_others = 0 
            it_deduction = 0
            

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
                if earning.earning_parameters_id.code=='MA': #TPT
                    ma += earning.float
                if earning.earning_parameters_id.code=='LA':
                    la += earning.float
                if earning.earning_parameters_id.code=='AA':
                    aa += earning.float
                if earning.earning_parameters_id.code=='EA':
                    ea += earning.float
                if earning.earning_parameters_id.code=='SHD': #TPT
                    shd += earning.float
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
                if deduction.deduction_parameters_id.code=='C.D': # ON 27/10/2015
                    cd += deduction.float
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
                if deduction.deduction_parameters_id.code == 'IT':
                    it_deduction += deduction.float
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
                'cd': cd,
                'loan': loan,
                'id': id,
                'pt': pt,
                'lwf': lwf,
                'lop': lop,
                'total_ear': total_ear,
                'total_ded': total_ded,
                'net': round(net),
                'ma': ma,
                'shd': shd,#
                'i_lic_prem' : i_lic_prem,
                'i_others' : i_others,
                'l_vvti_loan' : l_vvti_loan,
                'l_lic_hfl' : l_lic_hfl, 
                'l_hdfc' : l_hdfc, 
                'l_tmb' : l_tmb, 
                'l_sbt' : l_sbt, 
                'l_others' : l_others, 
                'it_deduction' : it_deduction,
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

