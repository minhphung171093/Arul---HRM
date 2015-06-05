# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
from datetime import date
import calendar
import openerp.addons.decimal_precision as dp

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_partial_picking, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            if picking.type != 'in':
                moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done','cancel')]
            else:
                moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done','cancel') and m.action_taken in ['direct','need','move']]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
    def do_partial(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Partial picking processing may only be done one at a time.'
        quanlity_vals = []
        quality_inspec = self.pool.get('tpt.quanlity.inspection')
        product_obj = self.pool.get('product.product')
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        picking_type = partial.picking_id.type
        for wizard_line in partial.move_ids:
            
            if picking_type=='in':
                if wizard_line.move_id.purchase_line_id and wizard_line.product_id.tolerance_qty:
                    po_qty = wizard_line.move_id.purchase_line_id.product_qty
                    tolerance_qty = po_qty*wizard_line.product_id.tolerance_qty/100
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move
                            where product_id=%s
                                and picking_id in (select id from stock_picking where state='done' and type='in' and purchase_id=%s)
                    '''%(wizard_line.product_id.id,wizard_line.move_id.picking_id.purchase_id.id)
                    cr.execute(sql)
                    received_qty = cr.fetchone()[0]
                    if (received_qty+wizard_line.quantity)>po_qty+tolerance_qty:
                        raise osv.except_osv(_('Warning!'),_('Tolerance Limit reached for the product %s!'%(wizard_line.product_id.name)))
            
            line_uom = wizard_line.product_uom
            move_id = wizard_line.move_id.id

            #Quantiny must be Positive
            if wizard_line.quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Please provide proper Quantity.'))

            #Compute the quantity for respective wizard_line in the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, line_uom.id)

#             if line_uom.factor and line_uom.factor <> 0:
#                 if float_compare(qty_in_line_uom, wizard_line.quantity, precision_rounding=line_uom.rounding) != 0:
#                     raise osv.except_osv(_('Warning!'), _('The unit of measure rounding does not allow you to ship "%s %s", only rounding of "%s %s" is accepted by the Unit of Measure.') % (wizard_line.quantity, line_uom.name, line_uom.rounding, line_uom.name))
            if move_id:
                #Check rounding Quantity.ex.
                #picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                #partial delivery: 253g
                #=> result= refused, as the qty left on picking would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.move_id.product_uom
                #Compute the quantity for respective wizard_line in the initial uom
                qty_in_initial_uom = uom_obj._compute_qty(cr, uid, line_uom.id, wizard_line.quantity, initial_uom.id)
                without_rounding_qty = (wizard_line.quantity / line_uom.factor) * initial_uom.factor
#                 if float_compare(qty_in_initial_uom, without_rounding_qty, precision_rounding=initial_uom.rounding) != 0:
#                     raise osv.except_osv(_('Warning!'), _('The rounding of the initial uom does not allow you to ship "%s %s", as it would let a quantity of "%s %s" to ship and only rounding of "%s %s" is accepted by the uom.') % (wizard_line.quantity, line_uom.name, wizard_line.move_id.product_qty - without_rounding_qty, initial_uom.name, initial_uom.rounding, initial_uom.name))
            else:
                seq_obj_name =  'stock.picking.' + picking_type
                move_id = stock_move.cremove_idate(cr,uid,{'name' : self.pool.get('ir.sequence').get(cr, uid, seq_obj_name),
                                                    'product_id': wizard_line.product_id.id,
                                                    'product_qty': wizard_line.quantity,
                                                    'product_uom': wizard_line.product_uom.id,
                                                    'prodlot_id': wizard_line.prodlot_id.id,
                                                    'location_id' : wizard_line.location_id.id,
                                                    'location_dest_id' : wizard_line.location_dest_id.id,
                                                    'picking_id': partial.picking_id.id
                                                    },context=context)
                stock_move.action_confirm(cr, uid, [move_id], context)
            partial_data['move%s' % (move_id)] = {
                'product_id': wizard_line.product_id.id,
                'product_qty': wizard_line.quantity,
                'product_uom': wizard_line.product_uom.id,
                'prodlot_id': wizard_line.prodlot_id.id,
            }
            if (picking_type == 'in') and (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.move_id.id)].update(product_price=wizard_line.cost,
                                                                  product_currency=wizard_line.currency.id)
            
#             if wizard_line.action_taken=='need':
#                 product_line = []
#                 if wizard_line.product_id.categ_id.cate_name=='raw':
#                     for para in wizard_line.product_id.spec_parameter_line: 
#                         product_line.append((0,0,{
#                                             'name':para.name and para.name.id or False,
#                                            'value':para.required_spec,
#                                            'uom_id':para.uom_po_id and para.uom_po_id.id or False,
#                                            }))
#                 qty_approve += wizard_line.quantity
#                 quanlity_vals.append({
#                         'product_id':wizard_line.product_id.id,
#                         'qty':wizard_line.quantity,
#                         'remaining_qty':wizard_line.quantity,
# #                         'qty_approve':qty_approve,
#                         'name':partial.picking_id.id,
#                         'supplier_id':partial.picking_id.partner_id.id,
#                         'date':partial.picking_id.date,
#                         'specification_line':product_line,
#                         'need_inspec_id':move_id,
#                         })
                
#                 quality_inspec.create(cr, SUPERUSER_ID, vals)
        res = stock_picking.do_partial(cr, uid, [partial.picking_id.id], partial_data, context=context)
        new_picking_id = res[partial.picking_id.id]['delivered_picking']
        if new_picking_id:
            
            for move in stock_picking.browse(cr, SUPERUSER_ID,new_picking_id).move_lines:
#                 if move.picking_id.action_taken=='need':
                if move.action_taken=='need':
                    product_line = []
                    if move.product_id.categ_id.cate_name=='raw':
                        for para in move.product_id.spec_parameter_line: 
                            product_line.append((0,0,{
                                                'name':para.name and para.name.id or False,
                                               'value':para.required_spec,
                                               'uom_id':para.uom_po_id and para.uom_po_id.id or False,
                                               }))
                    vals={
                            'product_id':move.product_id.id,
                            'qty':move.product_qty,
                            'remaining_qty':move.product_qty,
    #                         'qty_approve':qty_approve,
                            'name':new_picking_id,
                            'supplier_id':move.picking_id.partner_id.id,
                            'date':move.picking_id.date,
                            'specification_line':product_line,
                            'need_inspec_id':move.id,
                            }
                    quality_inspec.create(cr, SUPERUSER_ID, vals)
#         a_ids = stock_move.search(cr, uid,[('picking_id','=',[partial.picking_id.id]),('action_taken','=','need'),('state','not in',['done','cancel']),('inspec','=',False)])
#         for line in stock_move.browse(cr,uid,a_ids):
#             product_line = []
#             if line.product_id.categ_id.cate_name=='raw':
#                 for para in line.product_id.spec_parameter_line: 
#                     product_line.append((0,0,{
#                                         'name':para.name,
#                                        'value':para.required_spec,
#                                        }))
# 
#                 
#             vals = {
#                     'product_id':line.product_id.id,
#                     'qty':line.product_qty,
#                     'name':line.picking_id.id,
#                     'supplier_id':line.picking_id.partner_id.id,
#                     'date':line.picking_id.date,
#                     'need_inspec_id':line.id,
#                     'specification_line':product_line,
#                     }
#             
#             quality_inspec.create(cr, SUPERUSER_ID, vals)
#             sql = '''
#                 update stock_move set inspec='t' where id =%s
#             '''%(line.id)
#             cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}
    
    def _partial_move_for(self, cr, uid, move):
#         partial_move = {
#             'product_id' : move.product_id.id,
#             'quantity' : move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0,
#             'product_uom' : move.product_uom.id,
#             'prodlot_id' : move.prodlot_id.id,
#             'move_id' : move.id,
#             'location_id' : move.location_id.id,
#             'location_dest_id' : move.location_dest_id.id,
#             'currency': move.picking_id and move.picking_id.company_id.currency_id.id or False,
#             'action_taken': move.action_taken or False,
#         }
#         if move.picking_id.type == 'in' and move.product_id.cost_method == 'average':
#             partial_move.update(update_cost=True, **self._product_cost_for_average_update(cr, uid, move))
        partial_move = super(stock_partial_picking,self)._partial_move_for(cr, uid, move)
        if move.picking_id.type == 'in':
            partial_move.update({
                                 'action_taken': move.action_taken or False,
                                 })
        return partial_move
stock_partial_picking()

class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_invoice_onshipping, self).default_get(cr, uid, fields, context=context)
        res_ids = context and context.get('active_ids', [])
        model = context.get('active_model')
        if not model or 'stock.picking' not in model:
            return res

        model_pool = self.pool.get(model)
        browse_picking = model_pool.browse(cr, uid, res_ids, context=context)
        for pick in browse_picking:
            if pick.type == 'in':
                sql = '''
                    select case when count(id)>0 then 1 else 0 end abc from tpt_quanlity_inspection where state in ('draft','remaining') and name=%s
                '''%(pick.id)
                cr.execute(sql)
                abc = cr.fetchone()[0]
                if abc:
                    raise osv.except_osv(_('Warning!'),_('You should check Quality Inspection before the Create Invoice !'))
                
        return res
    def open_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_ids = []
        data_pool = self.pool.get('ir.model.data')
        
        picking_id = context and context.get('active_id', False)
        currency_id = False
        currency_name = False
        for wiz in self.browse(cr, uid, ids, context=context):
            if picking_id:
                pick_id = self.pool.get('stock.picking').browse(cr, uid, picking_id)
                if pick_id.type == 'in':
                    currency_id = pick_id.purchase_id and pick_id.purchase_id.currency_id and pick_id.purchase_id.currency_id.id or False
                    currency_name = pick_id.purchase_id and pick_id.purchase_id.currency_id and pick_id.purchase_id.currency_id.name or False
                if pick_id.type == 'out': 
                    currency_id = pick_id.sale_id and pick_id.sale_id.currency_id and pick_id.sale_id.currency_id.id or False
                    currency_name = pick_id.sale_id and pick_id.sale_id.currency_id and pick_id.sale_id.currency_id.name or False
                if currency_id:
                    if currency_name != 'INR':
                        if not wiz.invoice_date:
                            raise osv.except_osv(_('Warning!'),_('Please choose date of invoice!')) 
                        cur_rate_obj =self.pool.get('res.currency.rate')
                        cur_rate_ids = cur_rate_obj.search(cr, uid, [('currency_id','=',currency_id),('name','=',wiz.invoice_date)])
                        if not cur_rate_ids:
                            raise osv.except_osv(_('Warning!'),_('Rate of currency is not defined on %s!'%wiz.invoice_date)) 
                else:
                    raise osv.except_osv(_('Warning!'),_('Please check again! Do not have currency for this Picking order!')) 
        res = self.create_invoice(cr, uid, ids, context=context)
        invoice_ids += res.values()
        inv_type = context.get('inv_type', False)
        action_model = False
        action = {}
        if not invoice_ids:
            raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
        if inv_type == "out_invoice":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
        elif inv_type == "in_invoice":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
        elif inv_type == "out_refund":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree3")
        elif inv_type == "in_refund":
            action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree4")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
        return action
    
stock_invoice_onshipping()

class stock_partial_picking_line(osv.osv_memory):
    _inherit = "stock.partial.picking.line"
    _columns = {
        'action_taken':fields.selection([('direct','Direct Stock Update'),('move','Move to Consumption'),('need','Need Inspection')],'Action to be Taken'),
    }
stock_partial_picking_line()
    