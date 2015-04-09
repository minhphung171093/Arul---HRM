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
    'name': 'VVTi_TPT_ACCOUNTING',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'Tenth Planet',
    'website' : 'http://www. tenthplanet.in',
    'depends': ['green_erp_arulmani_crm','green_erp_arulmani_purchase','account','purchase','green_erp_arulmani_production','account_cancel'],
    'data': [
        'security/green_erp_arulmani_accounting_security.xml',
        'security/ir.model.access.csv',
        'wizard/daily_sale_form_view.xml',
        'wizard/cash_book_report_view.xml',
        'wizard/bank_book_report_view.xml',
        'tpt_accounting_sequence.xml',
        'tpt_accounting_view.xml',
        'report/daily_sale_report_view.xml',
        'report/report_cash_book_view.xml',
        'import_view.xml',
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
