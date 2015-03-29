# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'cons_loca':fields.many2one('res.partner','Consignee Location',readonly = True),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'transporter':fields.char('Transporter Name', size = 64),
        'truck':fields.char('Truck Number', size = 64),
        'remarks':fields.text('Remarks'),
        'doc_status':fields.selection([('draft','Drafted'),('waiting','Waiting for Approval'),('completed','Completed'),('cancelled','Cancelled')],'Document Status'),
        'sale_id': fields.many2one('sale.order', 'Sales Order',readonly = True, ondelete='set null', select=True),
        'do_ref_id': fields.many2one('stock.picking.out','DO Reference'),   
        'move_date': fields.date('Movement Date', required = True),
        'reason': fields.text("Reason for Move"),
        'flag_confirm': fields.boolean('Flag', readonly =  True),
        'bag_detail':fields.char('Bag Details', size = 64),
        'tpt_log_line': fields.one2many('tpt.log','delivery_order_id', 'Logs'),
#         'location_sour_id': fields.many2one('stock.location', 'Source Location'),
        'street3':fields.char('Street3',size=128),
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ),
                }
    
    _defaults = {
        'move_date': time.strftime('%Y-%m-%d'),
        'name': '/',
    }
    
#     def create(self, cr, uid, vals, context=None):
#         new_id = super(stock_picking, self).create(cr, uid, vals, context)
#         picking = self.browse(cr, uid, new_id)
#         sql = '''
#                     update stock_move set location_id = %s where picking_id = %s 
#                 '''%(picking.location_id.id, picking.id)
#         cr.execute(sql)
#         return new_id
    
#     def write(self, cr, uid, ids, vals, context=None):
#         new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
#         for picking in self.browse(cr, uid, ids):
#             sql = '''
#                     update stock_move set location_id = %s where picking_id = %s 
#                 '''%(picking.location_id.id, picking.id)
#             cr.execute(sql)
#         return new_write
    
    def onchange_do_ref_id(self, cr, uid, ids,do_ref_id=False, context=None):
        vals = {}
        move_lines = []
        for stock in self.browse(cr, uid, ids):
            sql = '''
                delete from stock_move where picking_id = %s
            '''%(stock.id)
            cr.execute(sql)
        if do_ref_id:
            de_order = self.pool.get('stock.picking.out').browse(cr, uid, do_ref_id)
            for line in de_order.move_lines:
                rs = {
                      'product_id': line.product_id and line.product_id.id or False,
                      'product_qty': line.product_qty or False,
                      'product_uom': line.product_uom and line.product_uom.id or False,
                      'prodlot_id': line.prodlot_id and line.prodlot_id.id or False,
                      'name': line.product_id and line.product_id.name or False,
                      'location_id': 1,
                      'location_dest_id': 1,
                      }
                move_lines.append((0,0,rs))
            
            vals = {
                    'move_lines':move_lines
                    }
        return {'value': vals}
    
    def onchange_location(self, cr, uid, ids, location_id = False, context=None):
        if location_id:
            return {'value': {'location_dest_id': False}}
        
    def create(self, cr, uid, vals, context=None):
        result = False
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.stock.move.import') or '/'
        new_id = super(stock_picking, self).create(cr, uid, vals, context)
        picking = self.browse(cr, uid, new_id)
        if picking.type == 'internal' and picking.location_id and picking.location_dest_id:
            sql = '''
                        update stock_move set location_id = %s, location_dest_id = %s where picking_id = %s 
                    '''%(picking.location_id.id, picking.location_dest_id.id, picking.id)
            cr.execute(sql)
            
            sql = '''
                    select product_id, prodlot_id, product_uom,sum(product_qty) as product_qty from stock_move where picking_id = %s group by product_id, prodlot_id, product_uom
                '''%(picking.id)
            cr.execute(sql)
            for move_line in cr.dictfetchall():
                if move_line['prodlot_id']:
                    sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id = %s and prodlot_id = %s
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id = %s and prodlot_id = %s
                            )foo
                    '''%(move_line['product_id'],picking.location_id.id,move_line['prodlot_id'] or 'null',move_line['product_id'],picking.location_id.id,move_line['prodlot_id'] or 'null')
                    cr.execute(sql)
                else:
                    sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id = %s
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id = %s
                            )foo
                    '''%(move_line['product_id'],picking.location_id.id,move_line['product_id'],picking.location_id.id)
                    cr.execute(sql)
                ton_sl = cr.dictfetchone()['ton_sl']
                if move_line['product_qty'] > ton_sl:
                    raise osv.except_osv(_('Warning!'),_('You are moving %s but only %s available for this product and serial number.' %(move_line['product_qty'], ton_sl)))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        inventory_obj = self.pool.get('stock.move')
        new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
        for picking in self.browse(cr, uid, ids):
            if picking.type == 'internal' and picking.location_id and picking.location_dest_id:
                sql = '''
                        update stock_move set location_id = %s, location_dest_id = %s where picking_id = %s 
                    '''%(picking.location_id.id, picking.location_dest_id.id, picking.id)
                cr.execute(sql)
                
                sql = '''
                    select product_id, prodlot_id, product_uom,sum(product_qty) as product_qty from stock_move where picking_id = %s group by product_id, prodlot_id, product_uom
                '''%(picking.id)
                cr.execute(sql)
                for move_line in cr.dictfetchall():
                    if move_line['prodlot_id']:
                        sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_dest_id = %s and prodlot_id = %s
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_id = %s and prodlot_id = %s
                                )foo
                        '''%(move_line['product_id'],picking.location_id.id,move_line['prodlot_id'] or 'null',move_line['product_id'],picking.location_id.id,move_line['prodlot_id'] or 'null')
                        cr.execute(sql)
                    else:
                        sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_dest_id = %s
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_id = %s
                                )foo
                        '''%(move_line['product_id'],picking.location_id.id,move_line['product_id'],picking.location_id.id)
                        cr.execute(sql)
                    ton_sl = cr.dictfetchone()['ton_sl']
                    if move_line['product_qty'] > ton_sl:
                        raise osv.except_osv(_('Warning!'),_('You are moving %s but only %s available for this product and serial number.' %(move_line['product_qty'], ton_sl)))
        return new_write
    
    def onchange_move_date(self, cr, uid, ids, move_date=False, context=None):
        vals = {}
        warning = {}
        if move_date:
            sql = '''
                select move_date from stock_picking where type='internal' order by move_date desc
            ''' 
            cr.execute(sql)
            move_dates = [row[0] for row in cr.fetchall()]
            if move_dates and move_date < move_dates[0]:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Not allow to create back Movement Date')
                }
                vals = {'move_date':False}
        return {'value': vals,'warning':warning}
    def print_packing_list(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        do_ids = self.browse(cr, uid, ids[0])
        sql = '''
            select id from account_invoice where delivery_order_id = %s
        '''%(do_ids.id)
        cr.execute(sql)
        invoice_ids = [row[0] for row in cr.fetchall()]
#         if do_ids.invoice_state == 'invoiced':
        if invoice_ids:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_packing_list_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
        else:
            raise osv.except_osv(_('Warning!'),_('This Delivery Order is not created Invoice!'))
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_packing_list_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        invoice_vals = super(stock_picking,self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)
#         if isinstance(partner, int):
#             partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
#         if inv_type in ('out_invoice', 'out_refund'):
#             account_id = partner.property_account_receivable.id
#             payment_term = partner.property_payment_term.id or False
#         else:
#             account_id = partner.property_account_payable.id
#             payment_term = partner.property_supplier_payment_term.id or False
#         comment = self._get_comment_invoice(cr, uid, picking)
        invoice_vals.update({
#             'name': picking.name,
#             'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
#             'type': inv_type,
#             'account_id': account_id,
#             'partner_id': partner.id,
#             'comment': comment,
# #             'payment_term': payment_term,
#             'fiscal_position': partner.property_account_position.id,
#             'date_invoice': context.get('date_inv', False),
#             'company_id': picking.company_id.id,
#             'user_id': uid,
#             
            'sale_id': picking.sale_id and picking.sale_id.id or False,
            'payment_term': picking.sale_id.payment_term_id and picking.sale_id.payment_term_id.id or False,
            'currency_id': picking.sale_id.currency_id and picking.sale_id.currency_id.id or False,
            'excise_duty_id': picking.sale_id.excise_duty_id and picking.sale_id.excise_duty_id.id or False,
            'doc_status': 'draft',
            'cons_loca': picking.cons_loca and picking.cons_loca.id or False,
            'delivery_order_id': picking.id,
            'sale_tax_id': picking.sale_id.sale_tax_id and picking.sale_id.sale_tax_id.id or False,
            'invoice_type': picking.sale_id and picking.sale_id.order_type or False,
        })
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        sql = '''
            select name from stock_production_lot where id in 
            (select prodlot_id from stock_move where picking_id in (select id from stock_picking 
            where id=%s) )
        '''%picking.id 
        cr.execute(sql)
        emp_code='' 
        for p in cr.fetchall(): 
            emp_code = emp_code +' '+ p[0]                               
        invoice_vals['material_info'] = emp_code
        
        return invoice_vals
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        invoice_line_vals = super(stock_picking,self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,invoice_vals, context)
#         if group:
#             name = (picking.name or '') + '-' + move_line.name
#         else:
#             name = move_line.name
#         origin = move_line.picking_id.name or ''
#         if move_line.picking_id.origin:
#             origin += ':' + move_line.picking_id.origin
#  
#         if invoice_vals['type'] in ('out_invoice', 'out_refund'):
#             account_id = move_line.product_id.property_account_income.id
#             if not account_id:
#                 account_id = move_line.product_id.categ_id.\
#                         property_account_income_categ.id
#         else:
#             account_id = move_line.product_id.property_account_expense.id
#             if not account_id:
#                 account_id = move_line.product_id.categ_id.\
#                         property_account_expense_categ.id
#         if invoice_vals['fiscal_position']:
#             fp_obj = self.pool.get('account.fiscal.position')
#             fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
#             account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
#         # set UoS if it's a sale and the picking doesn't have one
#         uos_id = move_line.product_uos and move_line.product_uos.id or False
#         if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
#             uos_id = move_line.product_uom.id
        if picking.type=='out':
            invoice_line_vals.update({
#             'name': name,
#             'origin': origin,
#             'invoice_id': invoice_id,
#             'uos_id': uos_id,
#             'product_id': move_line.product_id.id,
#             'account_id': account_id,
#             'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
#             'discount': self._get_discount_invoice(cr, uid, move_line),
#             'quantity': move_line.product_uos_qty or move_line.product_qty,
#             'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
#             'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
                'product_type':move_line.sale_line_id and move_line.sale_line_id.product_type or False,
                'application_id':move_line.sale_line_id and move_line.sale_line_id.application_id and move_line.sale_line_id.application_id.id or False,
                'freight':move_line.sale_line_id and move_line.sale_line_id.freight or False,
                'invoice_line_tax_id': [(6, 0, [picking.sale_id and picking.sale_id.sale_tax_id and picking.sale_id.sale_tax_id.id])],
            })
        return invoice_line_vals
    
    ### TPT START - By BalamuruganPurushothaman ON 27/03/2015 - TO AVOID CREATING MULTIPLE INVOICE LINE 
    ### SINGLE INVOICE FOR A SET OF MULTIPLE DO
    def action_invoice_create(self, cr, uid, ids, journal_id=False,
            group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        if context is None:
            context = {}

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        invoices_group = {}
        res = {}
        inv_type = type
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
            if isinstance(partner, int):
                partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
            if not partner:
                raise osv.except_osv(_('Error, no partner!'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if group and partner.id in invoices_group:
                invoice_id = invoices_group[partner.id]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                invoices_group[partner.id] = invoice_id
            res[picking.id] = invoice_id
            if len(picking.move_lines)>0:
                move_line = picking.move_lines[0]
                inv_qty_count = 0
                for move_line in picking.move_lines:          
                    if move_line.state == 'cancel':
                        continue
                    if move_line.scrapped:
                    # do no invoice scrapped products
                        continue
                    vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
                                invoice_id, invoice_vals, context=context)                    
                    inv_qty_count = inv_qty_count + move_line.product_qty 
                
                if vals:
                    vals.update({
                            'quantity':inv_qty_count                 
                    })  
                    invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                    #invoice_line_id['product_qty'] = a
                    self._invoice_line_hook(cr, uid, move_line, invoice_line_id)

            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res

    ### TPT END      
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)

                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        product_avail[product.id] = product.qty_available

                    if qty > 0:
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price, round=False)
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})

                        product_avail[product.id] += qty

            # every line of the picking is empty, do not generate anything
            empty_picking = not any(q for q in move_product_qty.values() if q > 0)

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking and not empty_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], 
                               {'name': sequence_obj.get(cr, uid,
                                            'stock.picking.%s'%(pick.type)),
                               })
                    pick.refresh()
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty
                            'prodlot_id': False,
                            'tracking_id': False,
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
                self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (pick.name), context=context)
            elif empty_picking:
                delivered_pack_id = pick.id
            else:
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
            
            cr.execute('''update stock_picking set doc_status='completed' where id=%s''',(delivered_pack_id,))
            
#             self.write(cr, uid, [delivered_pack_id], {'doc_status':'completed'}, context)
            if delivered_pack.sale_id:
                sp_ids = self.search(cr, uid, [('id','!=',delivered_pack.id),('state','!=','done'),('sale_id','=',delivered_pack.sale_id.id)])
                if sp_ids:
                    sql = '''
                        update sale_order set document_status='partially' where id = %s
                    '''%(delivered_pack.sale_id.id)
                    cr.execute(sql)
            
        return res
    
    def action_cancel(self, cr, uid, ids, context=None):
        """ Changes picking state to cancel.
        @return: True
        """
        for pick in self.browse(cr, uid, ids, context=context):
            ids2 = [move.id for move in pick.move_lines]
            self.pool.get('stock.move').action_cancel(cr, uid, ids2, context)
        self.write(cr, uid, ids, {'state': 'cancel', 'invoice_state': 'none','doc_status':'cancelled'})
        return True
    
    def has_valuation_moves(self, cr, uid, move):
        return self.pool.get('account.move').search(cr, uid, [
            ('ref', '=', move.picking_id.name),
            ])
    
    def action_revert_done(self, cr, uid, ids, context=None):
        move_ids = []
        invoice_ids = []
        if not len(ids):
            return False
        
        sql ='''
        select count(id) as id from stock_picking where id =%s
        and invoice_state ='invoiced'
        '''%(ids[0])
        cr.execute(sql)
        if cr.dictfetchone()['id']:
            raise osv.except_osv(
                _('Warning'),
                _('You must first cancel all Invoice order(s) attached to this sales order.'))
                
        for picking in self.browse(cr, uid, ids, context):
            for line in picking.move_lines:
                if self.has_valuation_moves(cr, uid, line):
                    raise osv.except_osv(
                        _('Error'),
                        _('Line %s has valuation moves (%s). \
                            Remove them first') % (line.name,
                                                   line.picking_id.name))
                line.write({'state': 'draft'})
            self.write(cr, uid, [picking.id], {'state': 'draft'})
            wf_service = netsvc.LocalService("workflow")
            # Deleting the existing instance of workflow
            wf_service.trg_delete(uid, 'stock.picking', picking.id, cr)
            wf_service.trg_create(uid, 'stock.picking', picking.id, cr)
            self.draft_force_assign(cr, uid, [picking.id])
            sql = '''
                update stock_picking set doc_status='draft' where id = %s
                '''%(picking.id)
            cr.execute(sql)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _(
                "The stock picking '%s' has been set in draft state."
                ) % (name,)
            self.log(cr, uid, id, message)
        return True
    
    def action_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for picking in self.browse(cr, uid, ids, context):
            sale = picking.sale_id and picking.sale_id.amount_total or 0
            limit = picking.partner_id and picking.partner_id.credit_limit_used or 0
            used = picking.partner_id and picking.partner_id.credit or 0
            if not picking.flag_confirm and limit <= (sale + used) and picking.sale_id and picking.sale_id.payment_term_id.name not in ['Immediate Payment','Immediate']:
                sql = '''
                    update stock_picking set doc_status='waiting' where id = %s
                    '''%(picking.id)
                cr.execute(sql)
                context.update({'default_name':'Not able to process DO due to exceed of credit limit. Need management approval to proceed further!'})
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'alert.warning.form',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': context,
                    'nodestroy': True,
                }
            #TPT COMMENTED BY BalamuruganPurushothaman TEMPORARILY ON 29/03/2015
            #====================================================== =============
            # if not picking.flag_confirm and limit == 0 and used == 0:
            #     sql = '''
            #         update stock_picking set doc_status='waiting' where id = %s
            #         '''%(picking.id)
            #     cr.execute(sql)
            #     context.update({'default_name':'Credit limit and Credit used are 0. Need management approval to proceed further!'})
            #     return {
            #         'view_type': 'form',
            #         'view_mode': 'form',
            #         'res_model': 'alert.warning.form',
            #         'type': 'ir.actions.act_window',
            #         'target': 'new',
            #         'context': context,
            #         'nodestroy': True,
            #     }
            #===================================================================
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.partial.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }
    
    def allow_cancel(self, cr, uid, ids, context=None):
        for pick in self.browse(cr, uid, ids, context=context):
            if not pick.move_lines:
                return True
            sql = '''
                    update stock_picking set doc_status='cancelled', flag_confirm = False where id = %s
                '''%(pick.id)
            cr.execute(sql)
            for move in pick.move_lines:
                if move.state == 'done':
                    raise osv.except_osv(_('Error!'), _('You cannot cancel the picking as some moves have been done. You should cancel the picking lines.'))
        return True
    
    def management_confirm(self, cr, uid, ids, context=None):
        for picking in self.browse(cr, uid, ids, context=context):
            if picking.doc_status == 'waiting':
                sql = '''
                    update stock_picking set flag_confirm = True where id = %s
                    '''%(picking.id)
                cr.execute(sql)
        return True
    
stock_picking()

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {        
        'cons_loca':fields.many2one('res.partner','Consignee Location',readonly = True),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'transporter':fields.char('Transporter Name', size = 64),
        'truck':fields.char('Truck Number', size = 64),
        'remarks':fields.text('Remarks'),
        'doc_status':fields.selection([('draft','Drafted'),('waiting','Waiting for Approval'),('completed','Completed'),('cancelled','Cancelled')],'Document Status'),
        'sale_id': fields.many2one('sale.order', 'Sales Order', readonly = True,ondelete='set null', select=True),
        'flag_confirm': fields.boolean('Flag', readonly =  True),
        'bag_detail':fields.char('Bag Details', size = 64),
        'tpt_log_line': fields.one2many('tpt.log','delivery_order_id', 'Logs'),
        #TPT - Added to Hide Print Packing List for Domestic
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type'),
                }
    
    def action_process(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').action_process(
            cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_picking_out, self).write(cr, uid, ids, vals, context)
        for stock in self.browse(cr, uid, ids):
            if stock.sale_id:
                sql = '''
                            select product_id, sum(product_qty) as picking_product_qty from stock_move where picking_id = %s group by product_id
                        '''%(stock.id)
                cr.execute(sql)
                for picking_line in cr.dictfetchall():
                    sql = '''
                            select product_id, sum(product_uom_qty) as sale_product_qty from sale_order_line where order_id = %s group by product_id
                        '''%(stock.sale_id.id)
                    cr.execute(sql)
                    for order_line in cr.dictfetchall():
                        if (picking_line['product_id']==order_line['product_id']):
                            if (picking_line['picking_product_qty'] > order_line['sale_product_qty']):
                                raise osv.except_osv(_('Warning!'),_('You are input %s quantity in delivery order but only %s quantity in sale order for this product.' %(picking_line['picking_product_qty'], order_line['sale_product_qty'])))
        if 'warehouse' in vals:
            location_id = vals['warehouse']
            sql = '''
                UPDATE stock_move
                SET location_id= %s
                WHERE picking_id = %s;
                '''%(location_id,stock.id)
            cr.execute(sql)
        return new_write
    
    def print_dispatch_slip(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'stock.picking.out',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tpt_print_dispatch_slip',
        }
    def print_packing_list(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        do_ids = self.browse(cr, uid, ids[0])
        sql = '''
            select id from account_invoice where delivery_order_id = %s
        '''%(do_ids.id)
        cr.execute(sql)
        invoice_ids = [row[0] for row in cr.fetchall()]
#         if do_ids.invoice_state == 'invoiced':
        if invoice_ids:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_packing_list_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
        else:
            raise osv.except_osv(_('Warning!'),_('This Delivery Order is not created Invoice!'))
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_packing_list_report',
#                 'datas': datas,
#                 'nodestroy' : True
            }
    
    def action_revert_done(self, cr, uid, ids, context=None):
        #override in order to redirect to stock.picking object
        return self.pool.get('stock.picking').action_revert_done(
            cr, uid, ids, context=context)
    
    def management_confirm(self, cr, uid, ids, context=None):
        return self.pool.get('stock.picking').management_confirm(
            cr, uid, ids, context=context)
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    def get_phy_batch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for physical in self.browse(cr, uid, ids, context=context):
            res[physical.id] = {
                'phy_batch': physical.prodlot_id and physical.prodlot_id.phy_batch_no or False,
            }
        return res
    
#     def _default_get(self, cr, uid, fields, context=None):
#         res = super(ketqua_xoso, self).default_get(cr, uid, fields, context=context)
#         for location in self.browse(cr, uid, ids):
#             res.update({
#             'location_id':location.picking_id.location_id.id,
#             })
#         return res
    
    def _get_product_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                            'primary_qty': 0.0,
                            }
            if line.product_id and line.product_uom:
                if line.product_uom.id != line.product_id.uom_id.id:
                    if line.product_id.__hasattr__('uom_ids'):
                        res[line.id]['primary_qty'] = uom_obj._compute_qty(cr, uid, line.product_uom.id, line.product_qty, line.product_id.uom_id.id, product_id=line.product_id.id)
                    else:
                        res[line.id]['primary_qty'] = uom_obj._compute_qty(cr, uid, line.product_uom.id, line.product_qty, line.product_id.uom_id.id)
                else:
                    res[line.id]['primary_qty'] = line.product_qty
        return res
    
    _columns = {
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),
        'application_id': fields.many2one('crm.application','Application'),   
        'prodlot_id': fields.many2one('stock.production.lot', 'System Serial No.', states={'done': [('readonly', True)]}, help="Serial number is used to put a serial number on the production", select=True), 
#         'sys_batch':fields.many2one('stock.production.lot','System Serial No.'), 
#         'phy_batch':fields.char('Physical Batch No.', size = 1024)
        'phy_batch':fields.function(get_phy_batch,type='char', size = 1024,string='Physical Serial No.',multi='sum',store=True),
        'primary_qty': fields.function(_get_product_info, string='Primary Qty', digits_compute= dp.get_precision('Product Unit of Measure'), type='float',
            store={
                'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['product_id','product_uom','product_qty'], 10),
            }, readonly=True, multi='pro_info'),

        
                }
    
#     _defaults = {
#         'location_id': 1,
#         'location_dest_id': 1,
#     }




    def onchange_sys_batch(self, cr, uid, ids,sys_batch=False,qty=False,context=None):
        vals = {}
        if context is None:
            context={}
        if sys_batch and qty:
            if context.get('search_prodlot_by_batch_alot'):
                sale_id = context.get('sale_id', False)
                if sale_id:
                    batch_obj = self.pool.get('tpt.batch.allotment')
                    batch_ids = batch_obj.search(cr, uid, [('sale_order_id','=',sale_id)])
                    batch_id = batch_obj.browse(cr, uid, batch_ids)
                    if batch_id:
                        for batch in batch_id:
                            if batch.batch_allotment_line:
                                for line in batch.batch_allotment_line:
                                    if line.sys_batch != sys_batch:
                                        if line.product_uom_qty < qty:
                                            warning = {  
                                                      'title': _('Warning!'),  
                                                      'message': _('The product quantity on Delivery Order is not greater than the product quantity on the Batch Allotment!\n Need to split it, please click on Split button on Product Line'),  
                                                      }  
                                            vals['prodlot_id']=False
                                            return {'value': vals,'warning':warning}
                                        else:
                                            vals['prodlot_id']= sys_batch
        return {'value': vals}
    
stock_move()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
#     def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
#         res = {}
#         for line in self.browse(cr,uid,ids,context=context):
#             res[line.id] = {
#                 'amount_untaxed': 0.0,
#                 'amount_tax': 0.0,
#                 'amount_total': 0.0,
#             }
#             val1 = 0.0
#             val2 = 0.0
#             val3 = 0.0
#             freight = 0.0
#             for invoiceline in line.invoice_line:
#                 freight += invoiceline.freight
#                 val1 += invoiceline.price_subtotal
#                 val2 += invoiceline.price_subtotal * (line.sale_tax_id.amount and line.sale_tax_id.amount / 100 or 0)
# #                 val3 = val1 + val2 + freight
#             res[line.id]['amount_untaxed'] = val1
#             res[line.id]['amount_tax'] = val2
#             res[line.id]['amount_total'] = val1+val2+freight
#             for taxline in line.tax_line:
#                 sql='''
#                     update account_invoice_tax set amount=%s where id=%s
#                 '''%(val2+freight,taxline.id)
#                 cr.execute(sql)
#         return res
#     
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    _columns = {
        'vvt_number': fields.char('Number', size=1024),
        'delivery_order_id': fields.many2one('stock.picking.out','Delivery Order', readonly=True),
        'cons_loca': fields.many2one('res.partner','Consignee Location', readonly=False, states={'draft':[('readonly',False)]}),
        'sale_id':  fields.many2one('sale.order','Sale Order', readonly=True, states={'draft':[('readonly',False)]}), 
        'excise_duty_id': fields.many2one('account.tax','Excise Duty', required = False, readonly=True, states={'draft':[('readonly',False)]}),
        'sale_tax_id': fields.many2one('account.tax','Sale Tax', required = False, readonly=True, states={'draft':[('readonly',False)]}),
        'doc_status':fields.selection([('draft','Drafted'),('waiting','Waiting for Approval'),('completed','Completed'),('cancelled','Cancelled')],'Document Status'),
        'invoice_type':fields.selection([ ('domestic','Domestic/Indirect Export'), ('export','Export'), ],'Invoice Type', readonly=True, states={'draft':[('readonly',False)]}),
        'vessel_flight_no': fields.char('Vessel/Flight No.', size = 1024, readonly=True, states={'draft':[('readonly',False)]}),
        'port_of_loading_id': fields.many2one('res.country','Port Of Loading', readonly=True, states={'draft':[('readonly',False)]}),
        'port_of_discharge_id': fields.many2one('res.country','Port Of Discharge', readonly=True, states={'draft':[('readonly',False)]}),
        'mark_container_no': fields.char('Marks & No Container No.', size = 1024, readonly=True, states={'draft':[('readonly',False)]}),
        'insurance': fields.float('Insurance', readonly=True, states={'draft':[('readonly',False)]}),
        'pre_carriage_by': fields.selection([('sea','Sea')],'Pre Carriage By', readonly=True, states={'draft':[('readonly',False)]}),
        
        #TPT - By BalamuruganPurushothaman on 28/02/2015- The following are used for Domestic Invoice Print
        'booked_to': fields.char('Booked To', size = 1024, readonly=True, states={'draft':[('readonly',False)]}),
        'lr_no': fields.char('LR Number', size = 1024, readonly=True, states={'draft':[('readonly',False)]}),
        'rem_date':fields.datetime('Date & Time of Rem.Of Goods', readonly=True, states={'draft':[('readonly',False)]}),
        'inv_date_as_char':fields.char('Date & Time of Invoice',readonly=True, states={'draft':[('readonly',False)]}),
        'rem_date_as_char':fields.char('Date & Time of Rem.Of Goods',readonly=True, states={'draft':[('readonly',False)]}),
        'material_info': fields.text('Material Additional Info',readonly=True, states={'draft':[('readonly',False)]}),
        'other_info': fields.text('Other Info', readonly=True, states={'draft':[('readonly',False)]}),
        #TPT
        'street3':fields.char('Street3',size=128)
#         'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
#             store={
#                 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#             },
#             multi='sums', help="The amount without tax.", track_visibility='always'),
#         'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
#             store={
#                 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#             },
#             multi='sums', help="The tax amount."),
#         'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
#             store={
#                 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#             },
#             multi='sums', help="The total amount."),
                }
    _defaults = {
        'vvt_number': '/',
    }
    
    def onchange_date_invoice(self, cr, uid, ids, date_invoice=False, context=None):
        vals = {}
        warning = {}
        if date_invoice:
            sql = '''
                select date_invoice from account_invoice where type='out_invoice' order by date_invoice desc
            ''' 
            cr.execute(sql)
            date_invoices = [row[0] for row in cr.fetchall()]
            if date_invoices and date_invoice < date_invoices[0]:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Not allow to create back date invoices')
                }
                vals = {'date_invoice':False}
        return {'value': vals,'warning':warning}
    
    def onchange_delivery_order_id(self, cr, uid, ids, delivery_order_id=False, context=None):
        vals = {}
        invoice_lines = []
        if delivery_order_id :
            delivery = self.pool.get('stock.picking.out').browse(cr, uid, delivery_order_id)
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql)
            for invoice_line in delivery.move_lines:
                rs_invoice = {
                      'product_id': invoice_line.product_id and invoice_line.product_id.id or False,
                      'product_type': invoice_line.product_type or False,
                      'application_id': invoice_line.application_id and invoice_line.application_id.id or False,
                      'quantity': invoice_line.product_qty or False,
                      'uos_id': invoice_line.product_uom and invoice_line.product_uom.id or False,
                      }
                invoice_lines.append((0,0,rs_invoice))
            vals = {'partner_id':delivery.partner_id and delivery.partner_id.id or False,
                    'cons_loca':delivery.partner_id and delivery.cons_loca.id or False,
                    'sale_id': delivery.sale_id and delivery.sale_id.id or False,
                    'doc_status':delivery.doc_status or False,
                    'invoice_line': invoice_lines or False
                    }
        return {'value': vals}
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('vvt_number','/')=='/':
            vals['vvt_number'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.customer.invoice.import') or '/'
        return super(account_invoice, self).create(cr, uid, vals, context=context)
    
    def invoice_print(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        invoice_ids = self.browse(cr, uid, ids[0])
        if invoice_ids.invoice_type == 'export':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_export_account_invoice',
#                 'datas': datas,
#                 'nodestroy' : True
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_domestic_account_invoice',
#                 'datas': datas,
#                 'nodestroy' : True
            }
    
    def write(self, cr, uid, ids, vals, context=None):
        for id in ids:
            if 'state' in vals:
                if (vals['state'] == 'draft'):
                    sql = '''
                        update account_invoice set doc_status='draft' where id=%s
                    '''%(id)
                    cr.execute(sql)
                if (vals['state'] == 'cancel'):
                    sql = '''
                        update account_invoice set doc_status='cancelled' where id=%s
                    '''%(id)
                    cr.execute(sql)
                if (vals['state'] == 'open'):
                    sql = '''
                        update account_invoice set doc_status='completed' where id=%s
                    '''%(id)
                    cr.execute(sql)
                if (vals['state'] == 'paid'):
                    sql = '''
                        update account_invoice set doc_status='completed' where id=%s
                    '''%(id)
                    cr.execute(sql)
        return super(account_invoice, self).write(cr, uid,ids, vals, context)
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        subtotal = 0.0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.quantity * line.price_unit) + (line.quantity * line.price_unit) * (line.invoice_id.excise_duty_id.amount and line.invoice_id.excise_duty_id.amount/100 or 1)          
            res[line.id] = subtotal
        return res
    
    _columns = {
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'freight': fields.float('FreightAmt'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
       } 
    
account_invoice_line()

class product_product(osv.osv):
    _inherit = "product.product"
    
    _defaults={
               'type':'product',
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_do_ref_id'):
            if context.get('do_ref_id'):
                sql = '''
                    select product_id from stock_move where picking_id in(select id from stock_picking where id = %s)
                '''%(context.get('do_ref_id'))
                cr.execute(sql)
                picking_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',picking_ids)]
        if context.get('search_pro_by_so'): 
            if context.get('sale_id'):
                sql = '''
                    select product_id from sale_order_line where order_id  = %s
                '''%(context.get('sale_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
product_product()

