# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class crm_sale_order(osv.osv):
    _name = 'crm.sale.order'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.sale.order') or '/'
        return super(crm_sale_order, self).create(cr, uid, vals, context=context)
    #TPT
    #def write(self, cr, uid, ids, vals, context=None):
    #   new_write = super(crm_sales_order, self).write(cr, uid,ids, vals, context)       
    #   return new_write
    
    def onchange_quotation_type(self, cr, uid, ids,quotation_type=False, context=None):
        vals = {}
        if quotation_type and quotation_type == 'domestic':
            vals = {'description':'*The above price is on ex-works basis. Freight charges will be to your account. (Transporter to be nominated by yourselves) \n*Insurance and statuary levies should be arranged at your end.'}
        elif quotation_type and quotation_type == 'export':
            vals = {'description':'*Freight charges will be to your account. (Liner to be nominated by yourselves). \n*Insurance and statuary levies should be arranged at your end.'}
        else:
            vals = {'description':''}
        return {'value': vals}
    
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('crm.sale.order.line')
        for sale in self.browse(cr, uid, ids, context=context):
            sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line], {'state': 'cancel'})
            if sale.lead_id:
                self.pool.get('crm.lead').write(cr, uid, [sale.lead_id.id], {'status':'cancelled'}, context=context)
                self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':sale.lead_id.id,'status':'cancelled'}, context=context)
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state': 'draft',
            'name': self.pool.get('ir.sequence').get(cr, uid, 'crm.sale.order'),
        })
        return super(crm_sale_order, self).copy(cr, uid, id, default, context=context)
    
    def copy_quotation(self, cr, uid, ids, default=None, context=None):
        id = self.copy(cr, uid, ids[0],default=None, context=None)
        for sale in self.browse(cr, uid, ids, context=context):
            if sale.lead_id:
                self.pool.get('crm.lead').write(cr, uid, [sale.lead_id.id], {'status':'quotation'}, context=context)
                self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':sale.lead_id.id,'status':'quotation'}, context=context)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'green_erp_arulmani_crm', 'crm_sale_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quotation'),
            'res_model': 'crm.sale.order',
            'res_id': id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }
    def action_button_view_partner(self, cr, uid, ids, context=None):
        for sale in self.browse(cr, uid, ids, context=context):
            self.pool.get('crm.sale.order').write(cr, uid, [sale.id], {'state':'done'}, context=context)
            if sale.lead_id and sale.lead_id.partner_id:
                partner_id = sale.lead_id.partner_id.id
                self.pool.get('res.partner').write(cr, uid, [partner_id], {'is_company':True}, context=context)
                view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'view_partner_form')
                view_id = view_ref and view_ref[1] or False,
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Customer'),
                    'res_model': 'res.partner',
                    'res_id': partner_id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'current',
                    'nodestroy': True,
                }
            else:
                return True
        
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += line.tax_amt
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] - order.commission_amount
        return res
    def _commission_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = order.commission_rate and order.commission_rate or 0.0
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('crm.sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    def onchange_lead_id(self, cr, uid, ids,lead_id=False, context=None):
        res = {'value':{
                        'quotation_type':False,
                        'currency_id':False,
                        'partner_id':False,
                      }
               }
        if lead_id:
            lead = self.pool.get('crm.lead').browse(cr, uid, lead_id)
            res['value'].update({
                                'quotation_type':lead.lead_group,
                                'currency_id':lead.currency_id.id,
                                'partner_id':lead.partner_id.id,
                                })
        return res
    
    def _get_default_shop(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        shop_ids = self.pool.get('sale.shop').search(cr, uid, [('company_id','=',company_id)], context=context)
        if not shop_ids:
            raise osv.except_osv(_('Error!'), _('There is no default shop for the current user\'s company!'))
        return shop_ids[0]
        
    _columns = {
                'partner_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
                'name': fields.char('Order Reference', size=64, required=True,
            readonly=True, states={'draft': [('readonly', False)]}, select=True),
                'lead_id': fields.many2one('crm.lead','Lead',domain="[('type','=','opportunity')]" ,readonly=True),
                'quotation_type':fields.selection([('domestic','Domestic'),('export','Export')],'Quotation Type' ,readonly=True),
                'commission_type_id': fields.selection([('percentage','Percentage'),('quantity_wise','Quantity Wise')],'Commission Type',readonly=True, states={'draft': [('readonly', False)]}),
                'commission_rate': fields.float('Commission Rate',readonly=True, states={'draft': [('readonly', False)]}),
                'commission_amount': fields.function(_commission_amount, string='Commission Amount', digits_compute= dp.get_precision('Account')),
                'currency_id': fields.many2one('res.currency','Currency',required=True,readonly=True),
                'date_order': fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
                'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
                    store={
                        'crm.sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                        'crm.sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                    },
                    multi='sums', help="The amount without tax.", track_visibility='always'),
                'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
                    store={
                        'crm.sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                        'crm.sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                    },
                    multi='sums', help="The tax amount."),
                'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
                    store={
                        'crm.sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','commission_rate'], 10),
                        'crm.sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                    },
                    multi='sums', help="The total amount."),
                'client_order_ref': fields.char('Customer Reference', size=64,readonly=True, states={'draft': [('readonly', False)]}),
                'user_id': fields.many2one('res.users', 'Salesperson', readonly=True, states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange'),
                'section_id': fields.many2one('crm.case.section', 'Sales Team',readonly=True, states={'draft': [('readonly', False)]}),
                'categ_ids': fields.many2many('crm.case.categ', 'sale_order_category_rel', 'order_id', 'category_id', 'Categories', \
            domain="['|',('section_id','=',section_id),('section_id','=',False), ('object_id.model', '=', 'crm.lead')]",readonly=True, states={'draft': [('readonly', False)]}, context="{'object_name': 'crm.lead'}"),
                'origin': fields.char('Source Document', size=64,readonly=True, states={'draft': [('readonly', False)]}, help="Reference of the document that generated this sales order request."),
                'payment_term': fields.many2one('account.payment.term', 'Payment Term',readonly=True, states={'draft': [('readonly', False)]},   ),
                
                #'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
                
                
                'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position',readonly=True, states={'draft': [('readonly', False)]}),
                'company_id': fields.related('shop_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True, states={'draft': [('readonly', False)]}),
                'bank_account_id': fields.many2one('res.partner.bank', 'Customer Bank Account', readonly=True, states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange'),
                
                'bank_account': fields.many2one('res.bank', 'Bank Account', readonly=True, states={'draft': [('readonly', False)]}, select=True, track_visibility='onchange'),
                
                
                'note': fields.text('Terms and conditions'),
                'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Pricelist for current sales order."),
                'incoterm': fields.many2one('stock.incoterms', 'Incoterm',readonly=True, states={'draft': [('readonly', False)]}, help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
                'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=True, states={'draft': [('readonly', False)]}),
                'picking_details':fields.char('Packing Details',size=255,readonly=True, states={'draft': [('readonly', False)]}),
                'packing_details': fields.selection([
                                        ('25 KG HDPE With Lines', '25 KG HDPE With Lines'),
                                        ('50 KG HDPE With Lines', '50 KG HDPE With Lines'),
                                        ('50 KG HDPE Bag', '50 KG HDPE Bag'),
                                        ('500 KG Jumbo Bag', '500 KG Jumbo Bag'),
                                        ('1000 KG Jumbo Bag', '1000 KG Jumbo Bag'),
                                        ], 'Packing Details'),
                'transport_details': fields.selection([
                                        ('Arranged at your End', 'Arranged at your End'),
                                        ('Arranged By VVTi', 'Arranged By VVTi'),                                        
                                        ], 'Transport Details'),
                'insurance_details': fields.selection([
                                        ('Arranged at your End', 'Arranged at your End'),
                                        ('Arranged By VVTi', 'Arranged By VVTi'),                                        
                                        ], 'Insurance Details'),
                'description':fields.text('Description',readonly=True, states={'draft': [('readonly', False)]}),
                'order_line': fields.one2many('crm.sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)]}),
                'state': fields.selection([
                                        ('draft', 'Draft Quotation'),
                                        ('cancel', 'Cancelled'),
                                        ('done', 'Done'),
                                        ], 'Status', readonly=True, track_visibility='onchange',
                                        help="Gives the status of the quotation or sales order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked to the sales order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date.", select=True),
                }
    _defaults = {
                 'commission_amount':0.0,
                 'shop_id': _get_default_shop,
                 'name': lambda obj, cr, uid, context: '/',
                 'state':'draft',
                 }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            if name and len(name) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Name must be unique !', ['name']),
    ]
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None):
        v = {}
        if shop_id:
            shop = self.pool.get('sale.shop').browse(cr, uid, shop_id, context=context)
            if shop.project_id.id:
                v['project_id'] = shop.project_id.id
            if shop.pricelist_id.id:
                v['pricelist_id'] = shop.pricelist_id.id
        return {'value': v}
    
    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        value = {
            'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        }
        if not order_lines:
            return {'value': value}
        warning = {
            'title': _('Pricelist Warning!'),
            'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
        }
        return {'warning': warning, 'value': value}
    
crm_sale_order()

class crm_sale_order_line(osv.osv):
    _name = "crm.sale.order.line"
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price_subtotal = 0.0
            ex_duty = 0.0
            if line.ex_duty:
                ex_duty = line.ex_duty.amount
            price_subtotal = line.product_uom_qty*line.price_unit * (1 - (line.discount or 0.0) / 100.0) + (line.product_uom_qty*line.price_unit * (1 - (line.discount or 0.0) / 100.0))*(ex_duty/100.0)
            res[line.id] = price_subtotal
        return res
    
    def _amount_tax(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price_subtotal = 0.0
            tax = 0.0
            ex_duty = 0.0
            if line.ex_duty:
                ex_duty = line.ex_duty.amount
            price_subtotal = line.product_uom_qty*line.price_unit * (1 - (line.discount or 0.0) / 100.0) + (line.product_uom_qty*line.price_unit * (1 - (line.discount or 0.0) / 100.0))*(ex_duty/100.0)
            if line.sub_tax:
                tax = line.sub_tax.amount
            res[line.id] = tax*price_subtotal/100.0
        return res

    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        context = context or {}
        lang = lang or ('lang' in context and context['lang'])
        if not uom:
            return {'value': {'price_unit': 0.0, 'product_uom' : uom or False}}
        return self.product_id_change(cursor, user, ids, pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order, context=context)
        
    _columns = {
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'order_id': fields.many2one('crm.sale.order', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True),
        'name': fields.text('Description', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'application_id': fields.many2one('crm.application','Application'),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),
        'ex_duty': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]"),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'sub_tax':fields.many2one('account.tax', 'S.Tax', domain="[('type_tax_use','=','sale')]"),
        'tax': fields.related('sub_tax','amount',type='float',relation='account.tax',string='Tax %',store=True,readonly=True,),
        'tax_amt': fields.function(_amount_tax, string='Tax Amt', digits_compute= dp.get_precision('Account')),
        'state': fields.selection([('cancel', 'Cancelled'),('draft', 'Draft'),('confirmed', 'Confirmed'),('exception', 'Exception'),('done', 'Done')], 'Status', required=True, readonly=True,
                help='* The \'Draft\' status is set when the related sales order in draft status. \
                    \n* The \'Confirmed\' status is set when the related sales order is confirmed. \
                    \n* The \'Exception\' status is set when the related sales order is set as exception. \
                    \n* The \'Done\' status is set when the sales order line has been picked. \
                    \n* The \'Cancelled\' status is set when a user cancel the sales order related.'),
        'product_uos_qty': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'product_uos': fields.many2one('product.uom', 'Product UoS'),
        'type': fields.selection([('make_to_stock', 'from stock'), ('make_to_order', 'on order')], 'Procurement Method', required=True, readonly=True, states={'draft': [('readonly', False)]},
         help="From stock: When needed, the product is taken from the stock or we wait for replenishment.\nOn order: When needed, the product is purchased or produced."),
        'th_weight': fields.float('Weight', readonly=True, states={'draft': [('readonly', False)]}),
        'address_allotment_id': fields.many2one('res.partner', 'Allotment Partner',help="A partner to whom the particular product needs to be allotted."),
        'discount': fields.float('Discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
    }
    
    # Hung sua lai Description la hien product name
    
#     def onchange_line(self, cr, uid, ids,product_uom_qty = False,price_unit = False,ex_duty = False,discount =False,sub_tax = False, context=None):
#         vals = {}
#         if product_uom_qty and price_unit and ex_duty and sub_tax:
#             ex_duty = self.pool.get('account.tax').browse(cr, uid, ex_duty).amount
#             tax = self.pool.get('account.tax').browse(cr, uid, sub_tax).amount
#             price_subtotal = product_uom_qty*price_unit * (1 - (discount or 0.0) / 100.0) + (product_uom_qty*price_unit * (1 - (discount or 0.0) / 100.0))*(ex_duty/100.0)
#             tax_amt = (tax or 0.0)*(price_subtotal or 0.0)/100.0
#             vals = {'price_subtotal':price_subtotal,'tax_amt':tax_amt}
#             return {'value': vals} 
#         if product_uom_qty and price_unit and sub_tax:
#             tax = self.pool.get('account.tax').browse(cr, uid, sub_tax).amount
#             price_subtotal = product_uom_qty*price_unit * (1 - (discount or 0.0) / 100.0)
#             tax_amt = (tax or 0.0)*(price_subtotal or 0.0)/100.0
#             vals = {'price_subtotal':price_subtotal,'tax_amt':tax_amt}
#             return {'value': vals}
#         if product_uom_qty and price_unit and ex_duty:
#             ex_duty = self.pool.get('account.tax').browse(cr, uid, ex_duty).amount
#             price_subtotal = product_uom_qty*price_unit * (1 - (discount or 0.0) / 100.0) + (product_uom_qty*price_unit * (1 - (discount or 0.0) / 100.0))*(ex_duty/100.0)
#             tax_amt = 0.0
#             vals = {'price_subtotal':price_subtotal,'tax_amt':tax_amt}
#             return {'value': vals}
#         if product_uom_qty and price_unit:
#             price_subtotal = product_uom_qty*price_unit * (1 - (discount or 0.0) / 100.0)
#             tax_amt = 0.0
#             vals = {'price_subtotal':price_subtotal,'tax_amt':tax_amt}
#             return {'value': vals}
#         return {'value': vals}
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
#         if not  partner_id:
#             raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
#             result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
#             if product_obj.description_sale:
#                 result['name'] += '\n'+product_obj.description_sale
            result['name'] = product_obj.name
            
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price
        # Hung sua lai khong default unit price

#         if not pricelist:
#             warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
#                     'Please set one before choosing a product.')
#             warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
#         else:
#             price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
#                     product, qty or 1.0, partner_id, {
#                         'uom': uom or result.get('product_uom'),
#                         'date': date_order,
#                         })[pricelist]
#             if price is False:
#                 warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
#                         "You have to change either the product, the quantity or the pricelist.")
# 
#                 warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
#             else:
#                 result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}
    
    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False
        
    _defaults = {
        'product_uom' : _get_uom_id,
        'discount': 0.0,
        'product_uom_qty': 0,
        'product_uos_qty': 0,
        'sequence': 10,
        'state': 'draft',
        'type': 'make_to_stock',
        'price_unit': 0.0,
        'ex_duty':False,
        'tax':0.0,
        'price_subtotal':0.0,
        'tax_amt':0.0
    }
    
crm_sale_order_line()
