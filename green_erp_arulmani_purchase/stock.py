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
from openerp import netsvc

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'document_type':fields.selection([('raw','VV Raw material PO'),('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'PO Document Type'),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'po_date': fields.datetime('PO Date'),        
        'gate_in_pass_no':fields.many2one('tpt.gate.in.pass','Gate In Pass No'),
        'truck':fields.char('Truck No', size = 64),
        'invoice_no':fields.char('DC/Invoice No', size = 64),
        'header_text':fields.text('Header Text'),#TPT
        'action_taken': fields.related('move_lines', 'action_taken', type='selection',selection=[
            ('direct','Direct Stock Update'),('move','Move to Consumption'),('need','Need Inspection')
            ], string='Action to be Taken'),
        'tpt_create_grn': fields.boolean('Create GRN'),
                }
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_picking, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.type=='in' and line.warehouse:
                sql = '''
                    update stock_move set location_dest_id = %s where picking_id=%s and (action_taken = 'direct' or action_taken is null)
                '''%(line.warehouse.id,line.id)
                cr.execute(sql)
            for move in line.move_lines:
                if 'state' in vals and vals['state']=='cancel' and line.type=='in':
                    sql = '''
                        update tpt_purchase_product set state='po_raised' where pur_product_id=%s and product_id=%s
                    '''%(move.po_indent_id.id,move.product_id.id)
                    cr.execute(sql)
        return new_write

#     def create(self, cr, user, vals, context=None):
#         if ('name' not in vals) or (vals.get('name')=='/'):
#             seq_obj_name =  self._name
#             vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
#         new_id = super(stock_picking, self).create(cr, user, vals, context)
#         grn = self.browse(cr,user,new_id)
#         for grn_line in grn.move_lines:
#             sql = '''
#                 select id from tpt_purchase_product where pur_product_id=%s and product_id=%s
#                 
#                 '''%(grn_line.po_indent_id.id,grn_line.product_id.id)
#             cr.execute(sql)
#             indent_line_ids = [row[0] for row in cr.fetchall()]
#             if indent_line_ids:
#                 self.pool.get('tpt.purchase.product').write(cr, user, indent_line_ids,{'state':'close'})
#         return new_id   
#     def action_invoice_create(self, cr, uid, ids, journal_id=False,
#             group=False, type='out_invoice', context=None):
#         """ Creates invoice based on the invoice state selected for picking.
#         @param journal_id: Id of journal
#         @param group: Whether to create a group invoice or not
#         @param type: Type invoice to be created
#         @return: Ids of created invoices for the pickings
#         """
#         if context is None:
#             context = {}
# 
#         invoice_obj = self.pool.get('account.invoice')
#         invoice_line_obj = self.pool.get('account.invoice.line')
#         partner_obj = self.pool.get('res.partner')
#         invoices_group = {}
#         res = {}
#         inv_type = type
#         for picking in self.browse(cr, uid, ids, context=context):
#             if picking.invoice_state != '2binvoiced':
#                 continue
#             partner = self._get_partner_to_invoice(cr, uid, picking, context=context)
#             if isinstance(partner, int):
#                 partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
#             if not partner:
#                 raise osv.except_osv(_('Error, no partner!'),
#                     _('Please put a partner on the picking list if you want to generate invoice.'))
# 
#             if not inv_type:
#                 inv_type = self._get_invoice_type(picking)
# 
#             if group and partner.id in invoices_group:
#                 invoice_id = invoices_group[partner.id]
#                 invoice = invoice_obj.browse(cr, uid, invoice_id)
#                 invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
#                 invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
#             else:
#                 invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
#                 invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
#                 invoices_group[partner.id] = invoice_id
#             res[picking.id] = invoice_id
#             for move_line in picking.move_lines:
#                 if move_line.state == 'cancel':
#                     continue
#                 if move_line.scrapped:
#                     # do no invoice scrapped products
#                     continue
#                 vals = self._prepare_invoice_line(cr, uid, group, picking, move_line,
#                                 invoice_id, invoice_vals, context=context)
#                 if vals:
#                     invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
#                     self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
# 
#             invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
#                     set_total=(inv_type in ('in_invoice', 'in_refund')))
#             self.write(cr, uid, [picking.id], {
#                 'invoice_state': 'invoiced',
#                 }, context=context)
#             self._invoice_hook(cr, uid, picking, invoice_id)
#         self.write(cr, uid, res.keys(), {
#             'invoice_state': 'invoiced',
#             }, context=context)
#         return res
    
    def onchange_dest_loca_id(self, cr, uid, ids,dest_id=False, context=None):
        vals = {}
        move_lines = []
        if dest_id:
            for stock in self.browse(cr, uid, ids):
                for line in stock.move_lines:
                    if not line.action_taken or line.action_taken not in ['need','move']:
                        rs = {
                              'location_dest_id': dest_id,
                              }
                        move_lines.append((1,line.id,rs))
                        sql = '''
                            update stock_move set location_dest_id = %s where id=%s
                        '''%(dest_id,line.id)
                        cr.execute(sql)
            
#             vals = {
#                     'move_lines':move_lines
#                     }
        return {'value':vals}    
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        invoice_vals = super(stock_picking,self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)
        if picking.type=='in':
            invoice_vals.update({
                                 'grn_no':picking.id,
                                 'purchase_id':picking.purchase_id and picking.purchase_id.id or False,
                                 'currency_id':picking.purchase_id and picking.purchase_id.currency_id and picking.purchase_id.currency_id.id or False,
#                                  'amount_untaxed': picking.purchase_id and picking.purchase_id.amount_untaxed or False,
#                                  'p_f_charge': picking.purchase_id and picking.purchase_id.p_f_charge or False,
#                                  'excise_duty': picking.purchase_id and picking.purchase_id.excise_duty or False,
#                                  'fright': picking.purchase_id and picking.purchase_id.fright or False,
#                                  'amount_tax': picking.purchase_id and picking.purchase_id.amount_tax or False,
#                                  'amount_total': picking.purchase_id and picking.purchase_id.amount_total or False,
                                 
#                                 'sale_tax_id':picking.purchase_id and picking.purchase_id.purchase_tax_id and picking.purchase_id.purchase_tax_id.id or False,
                                 })
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
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin
 
        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
#         tax_id = picking.purchase_id and picking.purchase_id.purchase_tax_id and picking.purchase_id.purchase_tax_id.id or False
#         if tax_id:
                
        if picking.type=='in':
            qty = move_line.product_uos_qty or move_line.product_qty
            invoice_line_vals.update({
                'name': name,
                'origin': origin,
                'invoice_id': invoice_id,
                'uos_id': uos_id,
                'product_id': move_line.product_id.id,
                'account_id': account_id,
                'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
                'discount': self._get_discount_invoice(cr, uid, move_line),
                'quantity':qty ,
                
                'disc': move_line.purchase_line_id and move_line.purchase_line_id.discount or False,
                'p_f': move_line.purchase_line_id and move_line.purchase_line_id.p_f or False,
                'p_f_type': move_line.purchase_line_id and move_line.purchase_line_id.p_f_type or False,
                'ed': move_line.purchase_line_id and move_line.purchase_line_id.ed or False,
                'ed_type': move_line.purchase_line_id and move_line.purchase_line_id.ed_type or False,
                'invoice_line_tax_id': move_line.purchase_line_id and move_line.purchase_line_id.taxes_id or False,
                'fright': move_line.purchase_line_id and move_line.purchase_line_id.fright or False,
                'fright_type': move_line.purchase_line_id and move_line.purchase_line_id.fright_type or False,
                'line_net': move_line.purchase_line_id and move_line.purchase_line_id.line_net or False,
                
    #                 'invoice_line_tax_id': [(6, 0, [tax_id])],
                'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
                'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
    #                 'product_type':move_line.product_type or False,
    #                 'application_id':move_line.application_id or False,
        #                 'freight':move_line.freight or False,
            })
            if move_line.action_taken == 'need' :
                inpec_obj = self.pool.get('tpt.quanlity.inspection')
                inpec_ids = inpec_obj.search(cr, uid, [('need_inspec_id','=',move_line.id)])
                if inpec_ids:
                    qty = inpec_obj.browse(cr, uid, inpec_ids[0]).qty_approve
                    if qty:
                        invoice_line_vals.update({'quantity':qty})
                    else:
                        invoice_line_vals = {}
                else:
                    inpec_ids = inpec_obj.search(cr, uid, [('name','=',move_line.picking_id.id),('product_id','=',move_line.product_id.id),('qty','=',move_line.product_qty)])
                    if inpec_ids:
                        qty = inpec_obj.browse(cr, uid, inpec_ids[0]).qty_approve
                        if qty:
                            invoice_line_vals.update({'quantity':qty})
                        else:
                            invoice_line_vals = {}
                            
                    
#         else:
#             invoice_line_vals.update({
#                 'name': name,
#                 'origin': origin,
#                 'invoice_id': invoice_id,
#                 'uos_id': uos_id,
#                 'product_id': move_line.product_id.id,
#                 'account_id': account_id,
#                 'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
#                 'discount': self._get_discount_invoice(cr, uid, move_line),
#                 'quantity': move_line.product_uos_qty or move_line.product_qty,
# #                 'invoice_line_tax_id': [(6, 0, [picking.purchase_id.purchase_tax_id])],
#     #             'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
#                 'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
# #                 'product_type':move_line.product_type or False,
# #                 'application_id':move_line.application_id or False,
# #                 'freight':move_line.freight or False,
#             })
        return invoice_line_vals
    
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _columns = {
        'document_type':fields.selection([('raw','VV Raw material PO'),('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'PO Document Type',readonly = True),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'po_date': fields.datetime('PO Date', readonly = True),   
        'gate_in_pass_no':fields.many2one('tpt.gate.in.pass','Gate In Pass No'),
        'truck':fields.char('Truck No', size = 64),
        'invoice_no':fields.char('DC/Invoice No', size = 64),
        'header_text':fields.text('Header Text'),#TPT
        'action_taken': fields.related('move_lines', 'action_taken', type='selection',selection=[
            ('direct','Direct Stock Update'),('move','Move to Consumption'),('need','Need Inspection')
            ], string='Action to be Taken'),
        'tpt_create_grn': fields.boolean('Create GRN'),
                }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('tpt_create_grn',False) and vals.get('purchase_id',False):
            wf_service = netsvc.LocalService("workflow")
            purchase_id = vals['purchase_id']
            res = wf_service.trg_validate(uid, 'purchase.order', purchase_id, 'purchase_md_confirmed', cr)
            picking_ids = self.search(cr, uid, [('purchase_id','=',purchase_id)])
            if picking_ids:
                value = {}
                if vals.get('warehouse',False):
                    value['warehouse'] = vals['warehouse']
                if vals.get('gate_in_pass_no',False):
                    value['gate_in_pass_no'] = vals['gate_in_pass_no']
                if vals.get('truck',False):
                    value['truck'] = vals['truck']
                if vals.get('invoice_no',False):
                    value['invoice_no'] = vals['invoice_no']
                if vals.get('header_text',False):
                    value['header_text'] = vals['header_text']
                self.write(cr, uid, [picking_ids[0]],value)
                picking = self.browse(cr, uid, picking_ids[0])
                if vals.get('move_lines',False):
                    for seq,line in enumerate(picking.move_lines):
                        move_value = {}
                        if vals['move_lines'][seq][2].get('item_text',False):
                            move_value['item_text']=vals['move_lines'][seq][2]['item_text']
                        if vals['move_lines'][seq][2].get('action_taken',False):
                            move_value['action_taken']=vals['move_lines'][seq][2]['action_taken']
                        if vals['move_lines'][seq][2].get('bin_location',False):
                            move_value['bin_location']=vals['move_lines'][seq][2]['bin_location']
                        if move_value:
                            self.pool.get('stock.move').write(cr, uid, [line.id], move_value)
                return picking_ids[0]
        return super(stock_picking_in,self).create(cr, uid, vals, context)
    
    def onchange_purchase_id(self, cr, uid, ids,purchase_id=False, context=None):
        vals = {}
        product_line = []
        if purchase_id:
            purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
            for line in purchase.order_line:
                rs = self.pool.get('purchase.order')._prepare_order_line_move(cr, uid,purchase,line,False)
                product_line.append((0,0,rs))
            
            vals = {
                    'partner_id': purchase.partner_id and purchase.partner_id.id or False,
                    'move_lines':product_line,
                    'tpt_create_grn': True,
                    }
        return {'value': vals}
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_default_grn_by_return_req'):
            sql = '''
                select id from stock_picking
                where state != 'draft' and id not in (select grn_id from tpt_gate_out_pass where state != 'cancel')
                and id in (select grn_no_id from tpt_good_return_request where state = 'done')
            '''
            cr.execute(sql)
            request_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',request_ids)]
        return super(stock_picking_in, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def onchange_dest_loca_id(self, cr, uid, ids,dest_id=False, context=None):
        vals = {}
        move_lines = []
        if dest_id:
            for stock in self.browse(cr, uid, ids):
                for line in stock.move_lines:
                    if not line.action_taken or line.action_taken not in ['need','move']:
                        rs = {
                              'location_dest_id': dest_id,
                              }
                        move_lines.append((1,line.id,rs))
                        sql = '''
                            update stock_move set location_dest_id = %s where id=%s
                        '''%(dest_id,line.id)
                        cr.execute(sql)
            
#             vals = {
#                     'move_lines':move_lines
#                     }
        return {'value':vals}
    
stock_picking_in()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    _columns = {
        'action_taken':fields.selection([('direct','Direct Stock Update'),('move','Move to Consumption'),('need','Need Inspection')],'Action to be Taken'),
        'po_indent_id': fields.many2one('tpt.purchase.indent','PO Indent No'),
        'inspec': fields.boolean('Inspec'),  
#         'bin_location':fields.many2one('stock.location','Bin Location'),
        'bin_location':fields.text('Bin Location'),
        'si_no':fields.integer('SI.No',readonly = True),
        'description':fields.char('Description', size = 50, readonly = True),
        'item_text':fields.text('Item Text'),
        'inspec_id': fields.many2one('tpt.quanlity.inspection','Quanlity Inspection'),
        'issue_id': fields.many2one('tpt.material.issue','Material Issue'),
        'grn_no': fields.related('picking_id', 'name', type='char', string='GRN No'),
        'grn_date': fields.related('picking_id', 'date', type='datetime', string='GRN Date'),
        'supplier_id': fields.related('picking_id', 'partner_id',relation='res.partner', type='many2one', string='Supplier'),
        'po_no': fields.related('picking_id', 'purchase_id',relation='purchase.order', type='many2one', string='PO Number'),
        'doc_type': fields.related('picking_id', 'document_type', type='selection',selection=[
            ('raw','VV Raw material PO'),('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')], string='PO Document Type'),
        'invoice_state': fields.related('picking_id', 'invoice_state', type='selection',selection=[
            ("invoiced", "Invoiced"),("2binvoiced", "To Be Invoiced"),("none", "Not Applicable")], string='Inovice State'),
        'tpt_pick_type': fields.related('picking_id', 'type', type='selection',selection=[
            ('out', 'Sending Goods'), ('in', 'Getting Goods'), ('internal', 'Internal')], string='Picking Type'),
        'cost_center_id': fields.many2one('tpt.cost.center','Cost center'),
                }
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False,
                            loc_dest_id=False, partner_id=False, action=False):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param prod_id: Changed Product id
        @param loc_id: Source location id
        @param loc_dest_id: Destination location id
        @param partner_id: Address id of partner
        @return: Dictionary of values
        """
        if not prod_id:
            return {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        lang = user and user.lang or False
        if partner_id:
            addr_rec = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if addr_rec:
                lang = addr_rec and addr_rec.lang or False
        ctx = {'lang': lang}

        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'name': product.partner_ref,
            'product_uom': product.uom_id.id,
            'product_uos': uos_id,
            'product_qty': 1.00,
            'product_uos_qty' : self.pool.get('stock.move').onchange_quantity(cr, uid, ids, prod_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'prodlot_id' : False,
            'bin_location': product.bin_location,
        }
        if loc_id:
            result['location_id'] = loc_id
        if loc_dest_id:
            result['location_dest_id'] = loc_dest_id
        if product.categ_id.cate_name == 'consum':
            result['action_taken'] = 'move'
        if action != 'move':
            if product.categ_id.cate_name == 'consum':
                result['action_taken'] = 'move'
            else:
                result['action_taken'] = False
        else:
            if product.categ_id.cate_name != 'consum':
                result['action_taken'] = False
        return {'value': result}
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(stock_move, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.po_indent_id.document_type == 'consumable':
                if line.action_taken == 'direct' or line.action_taken == 'need':
                    raise osv.except_osv(_('Warning!'),_('Consumable PR type should be processed with Move To Consumption Type only'))
            #TPT-FOLLOWING LINES ARE COMMENTED DUE TO BLOCK THIS MSG WHILE MD APPROVAL BUTTON IS TRIGGERED UP
            #===================================================================
            # if line.po_indent_id.document_type != 'consumable':
            #     if line.action_taken == 'move':
            #         raise osv.except_osv(_('Warning!'),_('Move To Consumption type should be applicable for Consumable PR type only.Please choose other type'))
            #===================================================================
        return new_write
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('picking_id',False):
            vals['si_no'] = len(self.search(cr, uid,[('picking_id', '=', vals['picking_id'])])) + 1
        new_id = super(stock_move, self).create(cr, uid, vals, context)
#         if po_indent_id and po_indent_id.document_type == 'consumable':
#             if action_taken == 'direct' or action_taken == 'need':
#                     raise osv.except_osv(_('Warning!'),_('Document Type of Purchase Indent not allowed select action this'))
#         if po_indent_id and po_indent_id.document_type != 'consumable':
#             if action_taken == 'move':
#                     raise osv.except_osv(_('Warning!'),_('Document Type of Purchase Indent not allowed select action this'))
        return new_id

    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            update_ids = self.search(cr, uid,[('picking_id','=',line.picking_id.id),('si_no','>',line.si_no)])
            if update_ids:
                cr.execute("UPDATE stock_move SET si_no=si_no-1 WHERE id in %s",(tuple(update_ids),))
        return super(stock_move, self).unlink(cr, uid, ids, context=context)
    
    def onchange_action_taken(self, cr, uid, ids,action_taken=False,product_id=False,context=None):
        vals = {}
        if action_taken and product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            cate = product.categ_id and product.categ_id.cate_name or False
            if  action_taken == 'move' and (cate == 'raw' or cate == 'spares' or cate == 'finish'):
                warning = {  
                          'title': _('Warning!'),  
                          'message': _('The action "Move to Consumption" can not be taken for this product!'),  
                          }  
                vals['action_taken']=False
                return {'value': vals,'warning':warning}
            elif cate == 'consum':
#             elif action_taken != 'move' and cate == 'consum':
                vals['action_taken']='move'
#             elif action_taken == 'move' and cate == 'consum':
#                 vals['action_taken']='move'
                location_id = False
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Virtual Locations'),('usage','=','view')])
                if not parent_ids:
                    warning = {  
                          'title': _('Warning!'),  
                          'message': _('System does not have Virtual Locations warehouse, please check it!'),  
                          }  
                    vals['action_taken']=False
                    return {'value': vals,'warning':warning}
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Consumption']),('location_id','=',parent_ids[0])])
                if not locat_ids:
                    warning = {  
                          'title': _('Warning!'),  
                          'message': _('System does not have Consumption location in Virtual Locations warehouse, please check it!'),  
                          }  
                    vals['action_taken']=False
                    return {'value': vals,'warning':warning}
                else:
                    location_id = locat_ids[0]
                vals['location_dest_id'] = location_id
                
            elif action_taken == 'need':
                location_id = False
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
                if not parent_ids:
                    warning = {  
                          'title': _('Warning!'),  
                          'message': _('System does not have Quality Inspection warehouse, please check it!'),  
                          }  
                    vals['action_taken']=False
                    return {'value': vals,'warning':warning}
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
                if not locat_ids:
                    warning = {  
                          'title': _('Warning!'),  
                          'message': _('System does not have Quality Inspection location in Quality Inspection warehouse, please check it!'),  
                          }  
                    vals['action_taken']=False
                    return {'value': vals,'warning':warning}
                else:
                    location_id = locat_ids[0]
                vals['location_dest_id'] = location_id
            elif action_taken == 'direct':   
                for line in self.browse(cr, uid, ids, context=context):
                    if line.picking_id and line.picking_id.warehouse:
                        vals['location_dest_id'] = line.picking_id and line.picking_id.warehouse and line.picking_id.warehouse.id or False
                    vals['action_taken']= action_taken
            else:
                vals['action_taken']= action_taken
        return {'value': vals}
stock_move()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    def amount_all_supplier_invoice_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'p_f_charge': 0.0,
                'excise_duty': 0.0,
                'amount_tax': 0.0,
                'fright': 0.0,
                'amount_total': 0.0,
                'amount_total_inr': 0.0,
                'amount_total_tds': 0.0,
                'amount_tax_debit': 0.0,
                'amount_tax_credit': 0.0,
                'aed': 0.0,
            }
            if line.type == 'out_invoice':
                res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_total_inr': 0.0
                }
                val1 = 0.0
                val2 = 0.0
                val3 = 0.0
                freight = 0.0
                ins = 0.0
                others = 0.0
                voucher_rate = 1
                if context is None:
                    context = {}
                ctx = context.copy()
                ctx.update({'date': line.date_invoice})
#                 ctx.update({'date': time.strftime('%Y-%m-%d')})
                currency = line.currency_id.name or False
                currency_id = line.currency_id.id or False
                #line.invoice_type=='export'
                if currency != 'INR':
                    voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
                for invoiceline in line.invoice_line:           
                    #raise osv.except_osv(_('Warning! Q'),_(invoiceline.freight))             
                    freight_line = invoiceline.quantity * invoiceline.freight #TPT
                    freight_line =freight_line
                    freight += freight_line
                    #freight = round(freight)
                    
                    ins_line = (invoiceline.quantity * invoiceline.insurance) #TPT
                    ins_line = ins_line
                    ins += ins_line
                    #ins = round(ins)
                    
                    others_line = (invoiceline.quantity * invoiceline.others) #TPT
                    others_line = others_line
                    others += others_line
                    #others = round(others)
                    
                    val1_line = invoiceline.price_subtotal
                    val1_line = val1_line
                    val1 += val1_line
                    #val1 = round(val1)
                    
                    val2_line = invoiceline.price_subtotal * (line.sale_tax_id.amount and line.sale_tax_id.amount / 100 or 0)
                    val2_line = val2_line
                    val2 += val2_line
                    #val2 = round(val2)
   
                ##FOR END
                if line.invoice_type=='export':
                   freight = round(freight,2)
                   ins = round(ins,2)
                   others = round(others,2)
                   
                   
                   res[line.id]['amount_untaxed'] = round(val1,2)
                   res[line.id]['amount_tax'] = round(val2,2)
                   res[line.id]['amount_total'] = round(val1+val2+freight+ins+others,2)
                   res[line.id]['amount_total_inr'] = round((val1+val2+freight+ins+others) / voucher_rate,2)
                    
                else:
                   freight = round(freight)
                   ins = round(ins)                 
                   val1 = round(val1)
                   val2 = round(val2)
                    
                   res[line.id]['amount_untaxed'] = round(val1)
                   res[line.id]['amount_tax'] = round(val2)
                   res[line.id]['amount_total'] = round(val1+val2+freight+ins)
                   res[line.id]['amount_total_inr'] = round((val1+val2+freight+ins) / voucher_rate)
                
                for taxline in line.tax_line:
                    sql='''
                        update account_invoice_tax set amount=%s where id=%s
                    '''%(round(val2+freight),taxline.id)
                    cr.execute(sql)#                         amount_total_tax = round(amount_total_tax)
            else:
                if line.purchase_id:
                    amount_untaxed = 0.0
                    p_f_charge=0.0
                    excise_duty=0.0
                    amount_total_tax=0.0
                    total_tax = 0.0
                    total_fright=0.0
                    qty = 0.0
                    aed = 0.0
                    tds_amount = 0.0
                    voucher_rate = 1
                    if context is None:
                        context = {}
                    ctx = context.copy()
                    ctx.update({'date': line.date_invoice})
#                     ctx.update({'date': time.strftime('%Y-%m-%d')})
                    currency = line.currency_id.name or False
                    currency_id = line.currency_id.id or False
                    if currency != 'INR':
                        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
                    for po in line.invoice_line:
                        tax = 0
                        p_f = 0
                        ed = 0
                        fright = 0
                        qty += po.quantity
                        basic = (po.quantity * po.price_unit) - ( (po.quantity * po.price_unit)*po.disc/100)
                        basic = round(basic)
                        amount_untaxed += basic
                        amount_untaxed = round(amount_untaxed)
                        if po.p_f_type == '1' :
                            p_f = basic * po.p_f/100
                            p_f = round(p_f)
                        elif po.p_f_type == '2' :
                            p_f = po.p_f
                            p_f = round(p_f)
                        elif po.p_f_type == '3' :
                            p_f = po.p_f * po.quantity
                            p_f = round(p_f)
                        else:
                            p_f = po.p_f
                            p_f = round(p_f)
                        p_f_charge += p_f
                        p_f_charge = round(p_f_charge)
                        if po.ed_type == '1' :
                            ed = (basic + p_f) * po.ed/100
                            ed = round(ed)
                        elif po.ed_type == '2' :
                            ed = po.ed
                            ed = round(ed)
                        elif po.ed_type == '3' :
                            ed = po.ed *  po.quantity
                            ed = round(ed)
                        else:
                            ed = po.ed
                            ed = round(ed)
                        excise_duty += ed
                        excise_duty = round(excise_duty)
                        tax_amounts = [r.amount for r in po.invoice_line_tax_id]
                        for tax_amount in tax_amounts:
                            tax += tax_amount/100
                        amount_total_tax = (basic + p_f + ed + po.aed_id_1)*(tax)
#                         amount_total_tax = round(amount_total_tax)
                        total_tax += amount_total_tax
#                         total_tax = round(total_tax)
                        if po.fright_type == '1' :
                            fright = (basic + p_f + ed + amount_total_tax) * po.fright/100
                            fright = round(fright)
                        elif po.fright_type == '2' :
                            fright = po.fright
                            fright = round(fright)
                        elif po.fright_type == '3' :
                            fright = po.fright * po.quantity
                            fright = round(fright)
                        else:
                            fright = po.fright
                            fright = round(fright)
                        total_fright += fright
                        total_fright = round(total_fright)
                         
#                         if po.aed_id:
#                             aed += basic*po.aed_id.amount/100
                        aed += po.aed_id_1
                        
                        if po.tds_id:    
                            tds_amount += po.quantity * po.price_unit * po.tds_id.amount/100
                            tds_amount = round(tds_amount,2)
                            
                    res[line.id]['amount_untaxed'] = round(amount_untaxed)
                    res[line.id]['p_f_charge'] = round(p_f_charge)
                    res[line.id]['excise_duty'] = round(excise_duty)
                    res[line.id]['amount_tax'] = round(total_tax)
                    res[line.id]['fright'] = round(total_fright)
                    res[line.id]['aed'] = round(aed)
                    res[line.id]['amount_total_tds'] = round(tds_amount)
                    res[line.id]['amount_total'] = (round(amount_untaxed) + round(p_f_charge) + round(excise_duty) + round(total_tax) + round(total_fright) + round(aed)) - round(tds_amount)
                    res[line.id]['amount_total_inr'] = round(((round(amount_untaxed) + round(p_f_charge) + round(excise_duty) + round(total_tax) + round(total_fright) + round(aed)) - round(tds_amount))/voucher_rate)
                else:
                    amount_untaxed = 0.0
                    p_f_charge=0.0
                    excise_duty=0.0
                    amount_total_tax=0.0
                    total_tax = 0.0
                    total_fright=0.0
                    qty = 0.0
                    tds_amount = 0.0
                    voucher_rate = 1
                    if context is None:
                        context = {}
                    ctx = context.copy()
                    ctx.update({'date': line.date_invoice})
#                     ctx.update({'date': time.strftime('%Y-%m-%d')})
                    currency = line.currency_id.name or False
                    currency_id = line.currency_id.id or False
                    if currency != 'INR':
                        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
                    for po in line.invoice_line:
                        tax = 0
                        p_f = 0
                        ed = 0
                        fright = 0
                        qty += po.quantity
                        basic = (po.quantity * po.price_unit) - ( (po.quantity * po.price_unit)*po.disc/100)
                        basic = round(basic)
                        amount_untaxed += basic
                        amount_untaxed = round(amount_untaxed)
                        if po.p_f_type == '1' :
                            p_f = basic * po.p_f/100
                            p_f = round(p_f)
                        elif po.p_f_type == '2' :
                            p_f = po.p_f
                            p_f = round(p_f)
                        elif po.p_f_type == '3' :
                            p_f = po.p_f * po.quantity
                            p_f = round(p_f)
                        else:
                            p_f = po.p_f
                            p_f = round(p_f)
                        p_f_charge += p_f
                        p_f_charge = round(p_f_charge)
                        if po.ed_type == '1' :
                            ed = (basic + p_f) * po.ed/100
                            ed = round(ed)
                        elif po.ed_type == '2' :
                            ed = po.ed
                            ed = round(ed)
                        elif po.ed_type == '3' :
                            ed = po.ed *  po.quantity
                            ed = round(ed)
                        else:
                            ed = po.ed
                            ed = round(ed)
                        excise_duty += ed
                        excise_duty = round(excise_duty)
                        tax_amounts = [r.amount for r in po.invoice_line_tax_id]
                        for tax_amount in tax_amounts:
                            tax += tax_amount/100
                        amount_total_tax = (basic + p_f + ed)*(tax)
#                         amount_total_tax = round(amount_total_tax)
                        total_tax += amount_total_tax
#                         total_tax = round(total_tax)
                        if po.fright_type == '1' :
                            fright = (basic + p_f + ed + amount_total_tax) * po.fright/100
                            fright = round(fright)
                        elif po.fright_type == '2' :
                            fright = po.fright
                            fright = round(fright)
                        elif po.fright_type == '3' :
                            fright = po.fright * po.quantity
                            fright = round(fright)
                        else:
                            fright = po.fright
                            fright = round(fright)
                        total_fright += fright
                        total_fright = round(total_fright)
                        if po.tds_id:    
                            tds_amount += po.quantity * po.price_unit * po.tds_id.amount/100
                            tds_amount = round(tds_amount)
                    
                    res[line.id]['amount_untaxed'] = round(amount_untaxed)
                    res[line.id]['p_f_charge'] = round(p_f_charge)
                    res[line.id]['excise_duty'] = round(excise_duty)
                    res[line.id]['amount_tax'] = round(total_tax)
                    res[line.id]['fright'] = round(total_fright)
                    res[line.id]['amount_total_tds'] = round(tds_amount)
                    res[line.id]['amount_total'] = round(amount_untaxed) +round(p_f_charge) + round(excise_duty) + round(total_tax) + round(total_fright) - round(tds_amount)
                    res[line.id]['amount_total_inr'] = round((round(amount_untaxed) +round(p_f_charge) + round(excise_duty) + round(total_tax) + round(total_fright) - round(tds_amount))/voucher_rate)
            if line.sup_inv_id and line.type=='in_invoice':
                base = 0
                tax_debit_amount = 0
                tax_credit_amount = 0
                for inv_line in line.invoice_line:
                    if inv_line.fright_fi_type == '2':
                        base_amount = round(inv_line.fright)
                        base+=base_amount
                        tax_debit_amount += round(base_amount*(inv_line.tax_id and inv_line.tax_id.amount/100 or 0))
                        tax_credit_amount += round(base_amount*(inv_line.tax_credit and inv_line.tax_credit.amount/100 or 0))
                    else:
                        base_amount = round(inv_line.fright*inv_line.quantity)
                        base += base_amount
                        tax_debit_amount += round(base_amount*(inv_line.tax_id and inv_line.tax_id.amount/100 or 0))
                        tax_credit_amount += round(base_amount*(inv_line.tax_credit and inv_line.tax_credit.amount/100 or 0))
                res[line.id]['amount_untaxed'] = round(base)
                res[line.id]['amount_tax_debit'] = round(tax_debit_amount)
                res[line.id]['amount_tax_credit'] = round(tax_credit_amount)
                res[line.id]['amount_total'] = res[line.id]['amount_untaxed'] + res[line.id]['amount_tax_debit'] - res[line.id]['amount_tax_credit']
                
                
        return res
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
     
    _columns = {
        'grn_no': fields.many2one('stock.picking.in','GRN No',readonly = True), 
        'create_uid':fields.many2one('res.users','Created By', readonly=True),
        'created_on': fields.datetime('Created On', readonly=True),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order', readonly = True),
        'vendor_ref': fields.char('Vendor Reference', size = 1024, readonly=True, states={'draft':[('readonly',False)]}),
        'is_tds_applicable': fields.boolean('IsTDSApplicable'),
        'tds_id': fields.many2one('account.tax', 'TDS %'),
        'tax_id': fields.many2one('account.tax', 'Taxes'),
        'sup_inv_id': fields.many2one('account.invoice', 'Supplier Invoice', required = True, readonly=True, states={'draft':[('readonly',False)]}),
        'amount_untaxed': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Untaxed Amount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
                
        'p_f_charge': fields.function(amount_all_supplier_invoice_line, multi='sums',string='P & F charges',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'excise_duty': fields.function(amount_all_supplier_invoice_line, multi='sums',string='Excise Duty',
            store={
               'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
               'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                               'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'aed': fields.function(amount_all_supplier_invoice_line, multi='sums',string='AED',
            store={
               'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
               'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                               'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'fright': fields.function(amount_all_supplier_invoice_line, multi='sums',string='Freight',
              store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
                 
        'amount_tax': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Taxes',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'amount_total': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Total',
             store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'amount_total_inr': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Total (INR)',
             store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line','date_invoice'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'amount_total_tds': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Total TDS',
             store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'amount_tax_debit': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Tax (Debit)',
             store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        'amount_tax_credit': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Tax (Credit)',
             store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type', 'tds_id','aed_id_1'], 10)}),
        }
    _defaults = {
        'created_on': time.strftime('%Y-%m-%d %H:%M:%S'),
#         'create_uid':  lambda self,cr,uid,c: uid
        }
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False
        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if (p.property_account_receivable.company_id and (p.property_account_receivable.company_id.id != company_id)) and (p.property_account_payable.company_id and (p.property_account_payable.company_id.id != company_id)):
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
                partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            else:
                acc_id = p.property_account_payable.id
                partner_payment_term = p.property_supplier_payment_term and p.property_supplier_payment_term.id or False
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

        result = {'value': {
            'account_id': acc_id,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position,
            'is_tds_applicable': p.is_tds_applicable,
            'tds_id': p.tds_id and p.tds_id.id or False
            }
        }

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr, uid, ids, partner_payment_term, date_invoice)
                result['value'].update(to_update['value'])
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        return result
    
    def create(self, cr, uid, vals, context=None):
#         if vals.get('type','')=='in_invoice' and 'purchase_id' in vals:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
#         elif vals.get('type','')=='in_invoice' and 'purchase_id' not in vals:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
#         elif 'purchase_id' in vals:
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
        new_id = super(account_invoice, self).create(cr, uid, vals, context)
        return new_id
    
account_invoice()


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def button_reset_taxes(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ait_obj = self.pool.get('account.invoice.tax')
        for id in ids:
            cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
#             partner = self.browse(cr, uid, id, context=ctx).partner_id
#             if partner.lang:
#                 ctx.update({'lang': partner.lang})
#             for taxe in ait_obj.compute(cr, uid, id, context=ctx).values():
#                 ait_obj.create(cr, uid, taxe)
#         # Update the stored value (fields.function), so we write to trigger recompute
        self.pool.get('account.invoice').write(cr, uid, ids, {'invoice_line':[]}, context=ctx)
        return True
    
    def line_net_line_supplier_invo(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        amount_basic = 0.0
        amount_p_f=0.0
        amount_ed=0.0
        amount_fright=0.0
           
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                    'line_net': 0.0,
                }  
            amount_total_tax=0.0
            amount_basic = (line.quantity * line.price_unit)-((line.quantity * line.price_unit)*line.disc/100)
            if line.p_f_type == '1':
               amount_p_f = amount_basic * (line.p_f/100)
            elif line.p_f_type == '2':
                amount_p_f = line.p_f
            elif line.p_f_type == '3':
                amount_p_f = line.p_f * line.quantity
            else:
                amount_p_f = line.p_f
            if line.ed_type == '1':
               amount_ed = (amount_basic + amount_p_f) * (line.ed/100)
            elif line.ed_type == '2':
                amount_ed = line.ed
            elif line.ed_type == '3':
                amount_ed = line.ed * line.quantity
            else:
                amount_ed = line.ed
            if line.fright_type == '1':
               amount_fright = (amount_basic + amount_p_f + amount_ed) * (line.fright/100)
            elif line.fright_type == '2':
                amount_fright = line.fright
            elif line.fright_type == '3':
                amount_fright = line.fright * line.quantity
            else:
                amount_fright = line.fright
            tax_amounts = [r.amount for r in line.invoice_line_tax_id]
            for tax in tax_amounts:
                amount_total_tax += tax/100
            res[line.id]['line_net'] = amount_total_tax+amount_fright+amount_ed+amount_p_f+amount_basic
            
            if line.invoice_id.sup_inv_id and line.invoice_id.type=='in_invoice':
                if line.fright_fi_type == '2':
                    base = line.fright
                    tax_debit_amount = base*(line.tax_id and line.tax_id.amount/100 or 0)
                    tax_credit_amount = base*(line.tax_credit and line.tax_credit.amount/100 or 0)
                else:
                    base = line.fright*line.quantity
                    tax_debit_amount = base*(line.tax_id and line.tax_id.amount/100 or 0)
                    tax_credit_amount = base*(line.tax_credit and line.tax_credit.amount/100 or 0)
                res[line.id]['line_net'] = base+tax_debit_amount-tax_credit_amount
        return res
     
    _columns = {
        'invoice_line_tax_id': fields.many2many('account.tax', 'account_invoice_line_tax', 'invoice_line_id', 'tax_id', 'Taxes', domain=[('parent_id','=',False)]),
        'gl_code_id': fields.many2one('account.account', 'GL Code'),
        'disc': fields.float('DISC'),
        'p_f': fields.float('P&F'),
        'p_f_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('P&F Type')),
        'ed': fields.float('ED'),
        'ed_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('ED Type')),
        'fright': fields.float('Freight'),
        'fright_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('Freight Type')),
        'fright_fi_type':fields.selection([('2','Rs'),('3','Qty')],('Freight Type')),
        'line_net': fields.function(line_net_line_supplier_invo, store = True, multi='deltas' ,string='Line Net'),
        'tax_id': fields.many2one('account.tax', 'Taxes'),
        'tax_credit': fields.many2one('account.tax', 'Tax (Credit)'),
        'tds_id': fields.many2one('account.tax', 'TDS %'),
        'aed_id': fields.many2one('account.tax', 'AED'),
        'aed_id_1': fields.float('AED'),
        'po_line_id': fields.many2one('purchase.order.line', 'purchase order line'),
#         'line_no': fields.integer('SI.No'),
    }
    _defaults = {
        'name': '/',
                 }
    
    def onchange_tax_credit(self, cr, uid, ids, tax_id,tax_credit, context=None):
        vals = {}
        warning = {}
        if tax_id and tax_credit:
            tax_obj = self.pool.get('account.tax')
            temp = 0
            tax_cr = tax_obj.browse(cr, uid, tax_credit)
#             for line in tax_obj.browse(cr, uid, invoice_line_tax_id[0][2]):
#                 if line.amount == tax_cr.amount:
#                     temp+=1
            tax = tax_obj.browse(cr, uid, tax_id)
            if tax.amount!=tax_cr.amount:
                warning = {  
                    'title': _('Warning!'),  
                    'message': _('% defined in Tax (Debit) and Tax (Credit) field should be the same.'),  
                }
                vals={'tax_credit':False}
        return {'value': vals, 'warning':warning}
    
    def onchange_tax_id(self, cr, uid, ids, tax_id=False, context=None):
        vals = {}
        if tax_id:
            vals = {
                'invoice_line_tax_id': [(6,0,[tax_id])],
                    }
        return {'value': vals}
    
    def onchange_gl_code_id(self, cr, uid, ids, gl_code_id=False, context=None):
        vals = {}
        if gl_code_id:
            account = self.pool.get('account.account').browse(cr,uid,gl_code_id)
            vals = {
                'name': account.name
                    }
        return {'value': vals}
account_invoice_line()
