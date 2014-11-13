# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2011 Alistek Ltd (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This module is GPLv3 or newer and incompatible
# with OpenERP SA "AGPL + Private Use License"!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = 'sale.order'  
    def print_quotation(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'sale.order',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        quotation_ids = self.browse(cr, uid, ids[0])
        if quotation_ids.quotation_type == 'domestic':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'quotation_domestic_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'quotation_export_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
sale_order()
