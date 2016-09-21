# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################


{
    "name" : "VVTI TPT Maintenance Management",
    "version" : "6.1",
    "author" : "Tien",
    'category': 'GreenERP',
    'sequence': 14,
    "depends" : ['green_erp_arulmani_hrm','green_erp_arulmani_production','green_erp_arulmani_accounting'],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    """,
    'update_xml': [
        'security/green_erp_arulmani_maintenance_security.xml',
        'security/ir.model.access.csv',
        'wizard/alert_form_view.xml',
        'mainten_seq.xml',
        'tpt_maintenance_view.xml',       
        'report/print_gpass_req_view.xml', 
        'report/print_service_gpass_out_view.xml',
        'material_return_request_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
