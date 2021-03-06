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
        'report/pr_history_report_view.xml',
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
        'wizard/purchase_indent_line_view.xml',
        'wizard/pr_history_view.xml',
        'wizard/slow_moving_items_report_view.xml',
        'wizard/idle_stock_list_report_view.xml',
        'wizard/cop_report_view.xml',
        'report/purchase_indent_line_report_view.xml', 
        'report/print_gate_out_pass_view.xml',
        'report/slow_moving_items_report_view.xml',
        'report/idle_stock_list_report_view.xml',
        'report/cop_report_view.xml',

        'purchase_view.xml',
        'stock_view.xml',
        'tpt_purchase_view.xml',
        'tpt_user_view.xml',
        'purchase_workflow.xml',
        'menu_inherit_view.xml',
        'import_view.xml',
        'purchase_stock_data.xml',
        'wizard/stock_pur_view.xml',
        'wizard/mateiral_purchase_value_month_view.xml',
        'report/report_mateiral_purchase_value_month_view.xml',
        'report/tpt_material_issue.xml',
        'wizard/po_above10lacs.xml',
        'report/po_above10lacs_view.xml',
        'wizard/purchase_vat_wizard.xml',
        'report/purchase_vat_report.xml',
        'wizard/purchase_cst_wizard.xml',
        'report/purchase_cst_report.xml',
        'wizard/rawmaterial_stock.xml',
        'report/rawmaterial_stock_report.xml',
        
        'wizard/stock_movement_analysis_finished_view.xml',
        'report/report_stock_movement_analysis_finished_view.xml',
        
        
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
