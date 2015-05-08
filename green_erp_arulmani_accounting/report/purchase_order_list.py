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

from openerp import tools
from openerp.osv import fields,osv
from openerp.addons.decimal_precision import decimal_precision as dp

class purchase_order_list(osv.osv_memory):
    _name = "purchase.order.list"
    _columns = {
        'si_no': fields.integer('SI.No', readonly=True),
        'po_id': fields.many2one('purchase.order','PO No', readonly=True),
        'po_date': fields.date('PO Date', readonly=True),
        'po_release_date': fields.date('PO Release Date', readonly=True),
        'supplier_id': fields.many2one('res.partner','Supplier Name', readonly=True),
        'line_no': fields.integer('Line No', readonly=True),
        'product_id': fields.many2one('product.product','Material Code', readonly=True),
        'material_name': fields.text('Material Name', readonly=True),
        'department_id': fields.many2one('hr.department','Department', readonly=True),
        'uom_id': fields.many2one('product.uom','UOM', readonly=True),
        'quantity': fields.float('Ordered Quantity',digits=(16,3), readonly=True),
        'unit_price': fields.float('Unit Price',digits=(16,2), readonly=True),
        'currency_id': fields.many2one('res.currency','UOM', readonly=True),
        'value': fields.float('Value',digits=(16,2), readonly=True),
        'pending_quantity': fields.float('Pending Quantity',digits=(16,3), readonly=True),
    }

purchase_order_list()

class purchase_order_list_wizard(osv.osv_memory):
    _name = "purchase.order.list.wizard"
    _columns = {
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
    }

    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def view_report(self, cr, uid, ids, context=None):
        cr.execute('delete from purchase_order_list')
        purchase_order_list_obj = self.pool.get('purchase.order.list')
        order_line_obj = self.pool.get('purchase.order.line')
        line = self.browse(cr, uid, ids[0])
        date_from = line.date_from
        date_to = line.date_to
        sql = '''
            select id from purchase_order_line where order_id in (select id from purchase_order where date_order between '%s' and '%s')
        '''%(date_from,date_to)
        cr.execute(sql)
        order_line_ids = [r[0] for r in cr.fetchall()]
        for seq,order_line in enumerate(order_line_obj.browse(cr, uid, order_line_ids)):
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                    from stock_move where purchase_line_id=%s and state='done'
            '''%(order_line.id)
            cr.execute(sql)
            grn_qty = cr.fetchone()[0]
            vals = {
                'si_no': seq+1,
                'po_id': order_line.order_id.id,
                'po_date': order_line.order_id.date_order,
                'po_release_date': order_line.order_id.md_approve_date,
                'supplier_id': order_line.partner_id.id,
                'line_no': order_line.line_no,
                'product_id': order_line.product_id.id,
                'material_name': order_line.name,
                'department_id': order_line.po_indent_no.department_id and order_line.po_indent_no.department_id.id or False,
                'uom_id': order_line.product_uom.id,
                'quantity': order_line.product_qty,
                'unit_price': order_line.price_unit,
                'currency_id': order_line.order_id.currency_id.id,
                'value': order_line.product_qty*order_line.price_unit,
                'pending_quantity': order_line.product_qty-grn_qty,
            }
            purchase_order_list_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_purchase_order_list_tree')
        return {
                    'name': 'Purchase Order List',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'purchase.order.list',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                }
    
purchase_order_list_wizard()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
