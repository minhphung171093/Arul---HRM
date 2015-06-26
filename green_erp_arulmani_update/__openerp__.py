# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################


{
    "name" : "Update for report",
    "version" : "6.1",
    "author" : "Tien",
    'category': 'GreenERP',
    "depends" : ['green_erp_arulmani_accounting','green_erp_arulmani_purchase'],
    "init_xml" : [],
    "demo_xml" : [],
    "description": """
    """,
    'update_xml': [
        'update_view.xml',
        'update_stock_move_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'certificate': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
