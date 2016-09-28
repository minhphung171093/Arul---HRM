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
    'name': 'VVTi_TPT_REPORTS',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'Tenth Planet',
    'website' : 'http://www. tenthplanet.in',
    'depends': ['green_erp_arulmani_hrm'],
    'data': [
        'security/ir.model.access.csv',
        'report/lwf_deduction_report_view.xml',
        'report/customer_master_report_view.xml',
        'report/monthwise_lop_report_view.xml',
        'report/cost_center_expense_report_view.xml',
        'report/single_source_vendor_report_view.xml',
        'report/new_vendor_list_report_view.xml',
        'wizard/lwf_deduction_report_view.xml',
        'wizard/customer_master_report_view.xml',
        'wizard/monthwise_lop_report_view.xml',
        'wizard/cost_center_expense_report_view.xml',
        'wizard/single_source_vendor_report_view.xml',
        'wizard/new_vendor_list_report_view.xml',
        'hr_payroll_view.xml',
        'menu.xml',
    ],
    'css' : [
    ],
    'js' : [
    ],
    'qweb': [
     ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
