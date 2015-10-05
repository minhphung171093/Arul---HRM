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

{
    'name': 'VVTi_TPT_HRM',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'Tenth Planet',
    'website' : 'http://www. tenthplanet.in',
    'depends': ['green_erp_arulmani_crm','hr_contract'],
    'data': [
        'security/green_erp_arulmani_hrm_security.xml',
        'security/ir.model.access.csv',
        'wizard/alert_form_view.xml',
        'wizard/print_payslip_view.xml',
        'wizard/time_evaluation_report_view.xml',
        'wizard/leave_balance_for_view.xml', ##
        'wizard/epf_statement_form_view.xml',
        'wizard/esi_statement_view.xml',
        'wizard/time_data_check.xml', ## 
        'wizard/emp_attendance_details.xml', ##
        'wizard/daily_filo_time_view.xml', ##
        'hr_employee_view.xml',
        'hr_department_view.xml',
        'hr_payroll_view.xml',
        'hr_holiday_view.xml',
        'hr_contract_view.xml',
        
        'hr_demo_leave_types.xml',
        'hr_employee_data.xml',
        'emp_leave_status_schedule.xml',
        'emp_time_entry_schedule.xml',
        'hr_payroll_earning_parameters_demo.xml',
        'hr_demo_payroll_deduction_parameters.xml',
        'report/arul_payslip_report.xml',
        'report/print_report.xml',
        'report/gate_pass_view.xml',
        'report/tpt_time_evaluation_report.xml',
        'report/epf_statement_report_view.xml',
        'report/esi_statement_report.xml',
        'report/leave_balance_for_view.xml', ## 
        'report/emp_attendance_details.xml',
        'report/daily_filo_time_for_view.xml',
        'report/DailyInOut_report_view.xml', ##  
        'wizard/DailyInOut_view.xml', ##
#         'data_category.xml', 
        'import_view.xml',
        'green_erp_arulmani_sequence.xml',
        'menu_view.xml',
    ],
    'css' : [
        "static/src/css/base.css",
    ],
    'js' : [
        "static/src/js/view_form.js",
    ],
    'qweb': [
        "static/src/xml/base.xml",
     ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
