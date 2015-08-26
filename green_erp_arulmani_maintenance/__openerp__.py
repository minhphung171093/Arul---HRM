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
    "depends" : ['green_erp_arulmani_hrm','green_erp_arulmani_purchase','green_erp_arulmani_accounting'],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    """,
    'update_xml': [
        'mainten_seq.xml',
        'tpt_maintenance_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
