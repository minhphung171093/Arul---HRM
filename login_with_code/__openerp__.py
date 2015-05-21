# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
{
    'name': 'GreenERP Two way verification',
    'version': '1.0',
    'category': 'GreenERP',
    'description': """
This module is used to enter security code sent by mail.
""",
    'author': "Tenth Planet",
    'website': "http://www. tenthplanet.in",
    'depends': ['base', 'web', 'mail', 'email_template'],
    'data': [
        'data/email_data.xml',
        'user_view.xml',
    ],
    'demo': [],
    'test': [],
    'js': ['static/src/js/coresetup.js'],
    'qweb': ['static/src/xml/web.xml'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: