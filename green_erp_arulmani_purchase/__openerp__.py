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
    'name': 'VVTi_TPT_PURCHASE',
    'version': '1.0',
    'category': 'GreenERP',
    'sequence': 14,
    'author': 'Tenth Planet',
    'website' : 'http://www. tenthplanet.in',
    'depends': ['purchase','stock','green_erp_arulmani_sale'],
    'data': [
        'security/green_erp_arulmani_purchase_security.xml',
        'security/ir.model.access.csv',
        'purchase_sequence.xml',
        'report/print_rfq_view.xml',
        'report/comparison_chart_view.xml',
        'report/purchase_order_report.xml',
        'report/report_stock_on_hand_view.xml',
        'report/grn_report_view.xml',
        'report/report_stock_inward_outward_view.xml',
        'report/report_stock_movement_analysis_view.xml',
        'report/tpt_raw_stock_statement_report_view.xml',
        'report/material_request_consumption_report_view.xml',
        'report/grn_line_details_report_view.xml',
        'wizard/tick_purchase_chart_view.xml',
        'wizard/alert_form_purchase_view.xml',
        'wizard/alert_form_line_view.xml',
        'wizard/stock_on_hand_report_view.xml',
        'wizard/load_line_from_norm_form_view.xml',
        'wizard/stock_movement_analysis_view.xml',
        'wizard/load_line_from_indent_form_view.xml',
        'wizard/stock_inward_outward_report_view.xml',
        'wizard/raw_material_stock_statement_report_view.xml',
        'wizard/material_request_line_view.xml',
        'wizard/grn_line_view.xml',

        'purchase_view.xml',
        'stock_view.xml',
        'tpt_purchase_view.xml',
        'tpt_user_view.xml',
        'purchase_workflow.xml',
        'menu_inherit_view.xml',
        'import_view.xml',
        'purchase_stock_data.xml',
        'wizard/stock_pur_view.xml',
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
