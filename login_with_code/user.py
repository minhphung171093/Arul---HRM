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

import logging
from openerp.osv import fields, osv
import openerp
from openerp import pooler
import string
import random

_logger = logging.getLogger(__name__)


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'security_code': fields.char('Security Code', size=64),
        'two_way_req': fields.boolean('Two Way Required')
    }

    def id_generator(self, cr, uid, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def route_send_mail(self, cr, uid, ids):
        ir_model_data = self.pool.get('ir.model.data')
        template_obj = self.pool.get('email.template')
        template_id = ir_model_data.get_object_reference(cr, uid, 'login_with_code', 'email_template_edi_security_code')[1]
        template_obj.send_mail(cr, uid, template_id, ids, True, context=None)
        return True

    def authenticate(self, db, login, password, user_agent_env):
        uid = self.login(db, login, password)
        if uid:
            if user_agent_env and user_agent_env.get('base_location'):
                cr = pooler.get_db(db).cursor()
                try:
                    base = user_agent_env['base_location']
                    ICP = self.pool.get('ir.config_parameter')
#                    if not ICP.get_param(cr, uid, 'web.base.url.freeze'):
#                        ICP.set_param(cr, uid, 'web.base.url', base)
                    if self.browse(cr, openerp.SUPERUSER_ID, uid).two_way_req:
                        self.write(cr, openerp.SUPERUSER_ID, uid, {
                            'security_code': self.id_generator(cr, uid)
                        })
                        self.route_send_mail(cr, openerp.SUPERUSER_ID, uid)
                    cr.commit()
                except Exception:
                    _logger.exception("Failed to update web.base.url configuration parameter")
                else:
                    cr.close()
        return uid

res_users()