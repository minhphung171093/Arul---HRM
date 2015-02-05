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
import openerp.addons.decimal_precision as dp


class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    _description = "Split in Serial Numbers"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        if context.get('search_prodlot_by_batch_alot'):
            move_id = context.get('active_id', False)
            if move_id:
                move = self.pool.get('stock.move').browse(cr,uid,move_id)
                sale_id = move.picking_id.sale_id and move.picking_id.sale_id.id or False
                if sale_id:
                    sql = '''
                        select sys_batch,product_uom_qty from tpt_batch_allotment_line line, tpt_batch_allotment mast
                        where mast.id = line.batch_allotment_id and batch_allotment_id in (select id from tpt_batch_allotment where sale_order_id = %s and state != 'cancel')
                    '''%(sale_id)
                    cr.execute(sql)
                    line_exist_line = []
                    for line in cr.dictfetchall():
                        line_exist_line.append((0,0,{'prodlot_id':line['sys_batch'],'quantity':line['product_uom_qty']}))
                    res.update({'line_exist_ids':line_exist_line})
        return res

split_in_production_lot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
