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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class crm_make_cancel(osv.osv_memory):
    _name = "crm.make.cancel"
    
    def makecancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        lead_obj = self.pool.get('crm.lead')
        data = context and context.get('active_ids', []) or []
        for make in lead_obj.browse(cr, uid, data, context=context):
            self.pool.get('crm.lead').case_cancel(cr, uid, [make.id], context=context)
            self.pool.get('crm.lead').write(cr, uid, make.id, {'probability' : 0.0,'status':'cancelled','type':'lead'}, context=context)
            self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':make.id,'status':'cancelled'}, context=context)
        return True    
crm_make_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
