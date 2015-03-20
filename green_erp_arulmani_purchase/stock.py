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
        'document_type':fields.selection([('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'PO Document Type'),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'po_date': fields.datetime('PO Date'),        
        'gate_in_pass_no':fields.many2one('tpt.gate.in.pass','Gate In Pass No'),
        'truck':fields.char('Truck No', size = 64),
        'delivery_no':fields.char('Delivery Challan No', size = 64),
        'invoice_no':fields.char('Invoice No & Date', size = 64),
                }

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
            invoice_line_vals.update({
                'name': name,
                'origin': origin,
                'invoice_id': invoice_id,
                'uos_id': uos_id,
                'product_id': move_line.product_id.id,
                'account_id': account_id,
                'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
                'discount': self._get_discount_invoice(cr, uid, move_line),
                'quantity': move_line.product_uos_qty or move_line.product_qty,
                
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
        'document_type':fields.selection([('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'PO Document Type',readonly = True),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'po_date': fields.datetime('PO Date', readonly = True),   
        'gate_in_pass_no':fields.many2one('tpt.gate.in.pass','Gate In Pass No'),
        'truck':fields.char('Truck No', size = 64),
        'delivery_no':fields.char('Delivery Challan No', size = 64),
        'invoice_no':fields.char('Invoice No & Date', size = 64),
                }
    
    def onchange_purchase_id(self, cr, uid, ids,purchase_id=False, context=None):
        vals = {}
        product_line = []
        for picking in self.browse(cr, uid, ids):
            sql = '''
                delete from stock_move where picking_id = %s
            '''%(picking.id)
            cr.execute(sql)
        if purchase_id:
            purchase = self.pool.get('purchase.order').browse(cr, uid, purchase_id)
            for line in purchase.order_line:
                rs = {
                      'po_indent_id': line.po_indent_no and line.po_indent_no.id or False,
                      'product_id': line.product_id and line.product_id.id or False,
                      'product_qty': line.product_qty or False,
                      'product_uom': line.product_uom and line.product_uom.id or False,
                      }
                product_line.append((0,0,rs))
            
            vals = {
                    'partner_id': purchase.partner_id and purchase.partner_id.id or False,
                    'move_lines':product_line,
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
   

    
stock_picking_in()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    _columns = {
        'action_taken':fields.selection([('direct','Direct Stock Update'),('move','Move to Consumption'),('need','Need Inspection')],'Action to be Taken'),
        'po_indent_id': fields.many2one('tpt.purchase.indent','PO Indent No'),
        'inspec': fields.boolean('Inspec'),  
        'bin_location':fields.many2one('stock.location','Bin Location'),
        'si_no':fields.integer('SI.No',readonly = True),
                }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('picking_id',False):
            vals['si_no'] = len(self.search(cr, uid,[('picking_id', '=', vals['picking_id'])])) + 1
        return super(stock_move, self).create(cr, uid, vals, context)

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
            if  action_taken == 'move' and (cate == 'raw' or cate == 'spares'):
                warning = {  
                          'title': _('Warning!'),  
                          'message': _('The action "Move to Consumption" can not be taken for this product!'),  
                          }  
                vals['action_taken']=False
                return {'value': vals,'warning':warning}
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
                'amount_total': 0.0
            }
            if line.type == 'out_invoice':
                res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                }
                val1 = 0.0
                val2 = 0.0
                val3 = 0.0
                freight = 0.0
                for invoiceline in line.invoice_line:
                    freight += invoiceline.freight
                    val1 += invoiceline.price_subtotal
                    val2 += invoiceline.price_subtotal * (line.sale_tax_id.amount and line.sale_tax_id.amount / 100 or 0)
    #                 val3 = val1 + val2 + freight
                res[line.id]['amount_untaxed'] = val1
                res[line.id]['amount_tax'] = val2
                res[line.id]['amount_total'] = val1+val2+freight
                for taxline in line.tax_line:
                    sql='''
                        update account_invoice_tax set amount=%s where id=%s
                    '''%(val2+freight,taxline.id)
                    cr.execute(sql)
            else:
                amount_untaxed = 0.0
                p_f_charge=0.0
                excise_duty=0.0
                amount_total_tax=0.0
                total_tax = 0.0
                fright=0.0
                qty = 0.0
                for po in line.invoice_line:
                    tax = 0
                    qty += po.quantity
                    basic = (po.quantity * po.price_unit) - ( (po.quantity * po.price_unit)*po.disc/100)
                    amount_untaxed += basic
                    if po.p_f_type == '1' :
                        p_f = basic * po.p_f/100
                    else:
                        p_f = po.p_f
                    p_f_charge += p_f
                    if po.ed_type == '1' :
                        ed = (basic + p_f) * po.ed/100
                    else:
                        ed = po.ed
                    excise_duty += ed
                    tax_amounts = [r.amount for r in po.invoice_line_tax_id]
                    for tax_amount in tax_amounts:
                        tax += tax_amount/100
                    amount_total_tax = (basic + p_f + ed)*(tax)
                    total_tax += amount_total_tax
                    if po.fright_type == '1' :
                        fright += (basic + p_f + ed + amount_total_tax) * po.fright/100
                    else:
                        fright += po.fright
                res[line.id]['amount_untaxed'] = amount_untaxed
                res[line.id]['p_f_charge'] = p_f_charge
                res[line.id]['excise_duty'] = excise_duty
                res[line.id]['amount_tax'] = total_tax
                res[line.id]['fright'] = fright
                res[line.id]['amount_total'] = amount_untaxed+p_f_charge+excise_duty+total_tax+fright
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
        
        'amount_untaxed': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Untaxed Amount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type'], 10)}),
                
        'p_f_charge': fields.function(amount_all_supplier_invoice_line, multi='sums',string='P & F charges',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type'], 10)}),
        'excise_duty': fields.function(amount_all_supplier_invoice_line, multi='sums',string='Excise Duty',
            store={
               'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
               'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                               'ed', 'ed_type','invoice_line_tax_id','fright','fright_type'], 10)}),
        'fright': fields.function(amount_all_supplier_invoice_line, multi='sums',string='Freight',
              store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type'], 10)}),
                 
        'amount_tax': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Taxes',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type'], 10)}),
        'amount_total': fields.function(amount_all_supplier_invoice_line, multi='sums', string='Total',
             store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),   
                'account.invoice.line': (_get_invoice_line, ['quantity', 'uos_id', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','invoice_line_tax_id','fright','fright_type'], 10)}),
        }
    _defaults = {
        'created_on': time.strftime('%Y-%m-%d %H:%M:%S'),
#         'create_uid':  lambda self,cr,uid,c: uid
        }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('type','')=='in_invoice':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
        new_id = super(account_invoice, self).create(cr, uid, vals, context)
        return new_id
    
account_invoice()


class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
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
            else:
                amount_p_f = line.p_f
            if line.ed_type == '1':
               amount_ed = (amount_basic + amount_p_f) * (line.ed/100)
            else:
                amount_ed = line.ed
            if line.fright_type == '1':
               amount_fright = (amount_basic + amount_p_f + amount_ed) * (line.fright/100)
            else:
                amount_fright = line.fright
            tax_amounts = [r.amount for r in line.invoice_line_tax_id]
            for tax in tax_amounts:
                amount_total_tax += tax/100
            res[line.id]['line_net'] = amount_total_tax+amount_fright+amount_ed+amount_p_f+amount_basic
        return res
     
    _columns = {
        'invoice_line_tax_id': fields.many2many('account.tax', 'account_invoice_line_tax', 'invoice_line_id', 'tax_id', 'Taxes', domain=[('parent_id','=',False)]),
        'gl_code_id': fields.many2one('account.account', 'GL Code'),
        'disc': fields.float('DISC'),
        'p_f': fields.float('P&F'),
        'p_f_type':fields.selection([('1','%'),('2','Rs')],('P&F Type')),
        'ed': fields.float('ED'),
        'ed_type':fields.selection([('1','%'),('2','Rs')],('ED Type')),
        'fright': fields.float('Freight'),
        'fright_type':fields.selection([('1','%'),('2','Rs')],('Freight Type')),
        'line_net': fields.function(line_net_line_supplier_invo, store = True, multi='deltas' ,string='Line Net'),
    }
    def onchange_gl_code_id(self, cr, uid, ids, gl_code_id=False, context=None):
        vals = {}
        if gl_code_id:
            account = self.pool.get('account.account').browse(cr,uid,gl_code_id)
            vals = {
                'name': account.name
                    }
        return {'value': vals}
account_invoice_line()
