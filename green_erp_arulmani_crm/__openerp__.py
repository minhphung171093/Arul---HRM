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
    'name': 'VVTi_TPT_CRM',
    'version': '1.0',
    'category': 'VVTi_TPT_CRM',
    'sequence': 14,
    'author': 'Tenth Planet',
    'website' : 'http://www. tenthplanet.in',
    'depends': ['base','crm','sale','hr','hr_contract','sale_crm','account','stock','sale_stock','web_m2x_options','report_aeroo','report_aeroo_ooo','web_widget_radio'],
    'data': [
        'security/green_erp_arulmani_crm_security.xml',
        'security/ir.model.access.csv',
        'wizard/crm_make_cancel_view.xml',
        'green_erp_arulmani_crm_view.xml',
        'green_erp_arulmani_hr_view.xml',
        'green_erp_arulmani_sequence.xml',
        'hr_qualification_attachment_view.xml',
        'hr_identities_attachment_view.xml',
        'crm_sequence.xml',
        'crm_specification_view.xml',
        'crm_qc_test_view.xml',
        'crm_sample_invoice_view.xml',
        'green_erp_arulmani_sale_view.xml',
        'crm_configuration_view.xml',
        'report/sample_sending_report_view.xml',
        'report/sample_invoice_report_view.xml',
        'report/hr_employee_report_view.xml',
        'report/quotation_report_view.xml',
        'report/customer_export_template_view.xml',
        'wizard/hr_employee_report.xml',
        'menu_inherit_view.xml',
    ],
    'css' : [
        "static/src/css/base.css",
    ],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
