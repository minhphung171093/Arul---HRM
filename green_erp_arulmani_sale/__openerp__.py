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
    'name': 'VVTi_TPT_SALE',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'Tenth Planet',
    'website' : 'http://www. tenthplanet.in',
    'depends': ['green_erp_arulmani_hrm','green_erp_arulmani_crm','sale_stock','stock'],
    'data': [
        'security/green_erp_arulmani_sale_security.xml',
        'security/ir.model.access.csv',
        'data/tpt_sale_data.xml',
        'tpt_sale_view.xml',
        'report/print_form_403_view.xml',
        'report/test_report_view.xml',
        'report/print_form_are_1_view.xml',
        'report/print_form_are_3_view.xml',
        'report/print_dispatch_slip_view.xml',
        'report/export_invoice_report_view.xml',
        'report/domestic_invoice_report_view.xml',
        'report/packing_list_report_view.xml',
        'report/proforma_invoice_report_view.xml',
        'wizard/alert_form_view.xml',
        'wizard/stock_move_view.xml',
        'tpt_stock_view.xml',
        'sale_sequence.xml',
        'tpt_form_are_view.xml',
        'menu_inherit_view.xml',
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
