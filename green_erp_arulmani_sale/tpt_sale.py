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

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val1 = 0.0
            val2 = 0.0
            val3 = 0.0
            for orderline in line.order_line:
                val1 = val1 + orderline.price_subtotal
                res[line.id]['amount_untaxed'] = val1
            val2 = val1 * line.sale_tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
            val3 = val1 + val2
            res[line.id]['amount_total'] = val3
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys() 
    
    _columns = {
#         'name': fields.char('Order Reference', size=64, required=True, readonly=True, select=True),
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True),
        'blanket_id':fields.many2one('tpt.blanket.order','Blanket Order'),
#         'so_date':fields.date('SO Date'),
        'po_date':fields.date('PO Date'),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
        'document_type':fields.selection([('saleorder','Sale Order'),('return','Return Sales Order'),('scrap','Scrap Sales')],'Document Type' ,required=True),
        'po_number':fields.char('PO Number', size = 20),
        'reason':fields.text('Reason'),
        'quotaion_no':fields.char('Quotaion No', size = 40),
        'expected_date':fields.date('Expected delivery Date'),
        'document_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)')],'Document Status'),
        'incoterms_id':fields.many2one('stock.incoterms','Incoterms',required = True),
        'distribution_channel':fields.many2one('crm.case.channel','Distribution Channel',required = True),
        'excise_duty_id': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]", required = True),
        'sale_tax_id': fields.many2one('account.tax', 'Sale Tax', domain="[('type_tax_use','=','sale')]", required = True), 
        'invoice_address': fields.char('Invoice Address', size = 1024),
        'street2': fields.char('', size = 1024),
        'city': fields.char('', size = 1024),
        'country_id': fields.many2one('res.country', ''),
        'state_id': fields.many2one('res.country.state', ''),
        'zip': fields.char('', size = 1024),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order."),
        'sale_consignee_line':fields.one2many('tpt.sale.order.consignee','sale_order_consignee_id','Consignee')
    }
    _defaults = {
#                  'name': lambda obj, cr, uid, context: '/',
        'po_date': time.strftime('%Y-%m-%d'),
        'expected_date': time.strftime('%Y-%m-%d'),
    }
    def onchange_po_date(self, cr, uid, ids, po_date=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if po_date:
            if po_date > current:
                vals = {'po_date':current}
                warning = {
                    'title': _('Warning!'),
                    'message': _('PO Date: Allow back date, not allow future date')
                }
        return {'value':vals,'warning':warning}
    
    def onchange_so_date(self, cr, uid, ids, date_order=False, blanket_id=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if blanket_id:
            blanket = self.pool.get('tpt.blanket.order').browse(cr,uid,blanket_id)
            if date_order < blanket.bo_date:
                vals = {'date_order':current}
                warning = {
                    'title': _('Warning!'),
                    'message': _('PO Date: Allow back date, not allow future date')
                }
        return {'value':vals,'warning':warning}    
    
    def onchange_partner_id(self, cr, uid, ids, partner_id=False, context=None):
        vals = {}
        consignee_lines = []
#         for blanket in self.browse(cr, uid, ids):
#             sql = '''
#                 delete from order_line where blanket_order_id = %s
#             '''%(blanket.id)
#             cr.execute(sql)
        if partner_id :
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            for order in self.browse(cr, uid, ids):
                sql = '''
                    delete from tpt_sale_order_consignee where sale_order_consignee_id = %s
                '''%(order.id)
                cr.execute(sql)
            for line in part.consignee_line:
                rs = {
                        'name_consignee_id': line.id,
                        'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or '') + ' , ' + str(line.state_id.name or '') + ' , ' + str(line.country_id.name or '') + ' , ' +str(line.zip or ''),
                      }
                consignee_lines.append((0,0,rs))
            vals = {'invoice_address':part.street,
                    'street2':part.street2,
                    'city':part.city,
                    'country_id':part.country_id.id,
                    'state_id':part.state_id.id,
                    'zip':part.zip,
                    'payment_term_id':part.property_payment_term.id,
                    'sale_consignee_line': consignee_lines,
                    'incoterms_id':part.inco_terms_id and part.inco_terms_id.id or False,
                    }
        return {'value': vals}    
        
#     def create(self, cr, uid, vals, context=None):
#         if vals.get('name','/')=='/':
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.sale.order.import') or '/'
#         return super(sale_order, self).create(cr, uid, vals, context=context)
    
    def _check_blanket_order_id(self, cr, uid, ids, context=None):
        for blanket in self.browse(cr, uid, ids, context=context):
            if blanket.blanket_id:
                blanket_ids = self.search(cr, uid, [('id','!=',blanket.id),('blanket_id','=',blanket.blanket_id.id)])
                if blanket_ids:
                    raise osv.except_osv(_('Warning!'),_('The data is not suitable!'))  
                    return False
        return True
    _constraints = [
        (_check_blanket_order_id, 'Identical Data', ['blanket_id']),
        ]
    
    def create(self, cr, uid, vals, context=None):
        if 'document_status' in vals:
            vals['document_status'] = 'draft'
        return super(sale_order, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'document_status' in vals:
            vals['document_status'] = 'draft'
        return super(sale_order, self).write(cr, uid,ids, vals, context)
    
    def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
        vals = {}
        blanket_lines = []
        consignee_lines = []
        if blanket_id:
            blanket = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from sale_order_line where order_id = %s
                '''%(line.id)
                cr.execute(sql)
            for blanket_line in blanket.blank_order_line:
                rs_order = {
                      'product_id': blanket_line.product_id and blanket_line.product_id.id or False,
                      'name': blanket_line.description or False,
                      'product_type': blanket_line.product_type or False,
                      'application_id': blanket_line.application_id and blanket_line.application_id.id or False,
                      'product_uom_qty': blanket_line.product_uom_qty or False,
                      'product_uom': blanket_line.uom_po_id and blanket_line.uom_po_id.id or False,
                      'price_unit': blanket_line.price_unit or False,
                      'price_subtotal': blanket_line.sub_total or False,
                      'freight': blanket_line.freight or False,
                      'state': 'draft',
                      }
                blanket_lines.append((0,0,rs_order))
              
            for consignee_line in blanket.blank_consignee_line:
                rs_consignee = {
                      'name_consignee_id': consignee_line.name_consignee_id or False,
                      'location': consignee_line.location or False,
                      'product_id': consignee_line.product_id and consignee_line.product_id.id or False,
                      'product_uom_qty': consignee_line.product_uom_qty or False,
                      'uom_po_id': consignee_line.uom_po_id and consignee_line.uom_po_id.id or False,
                                }
                consignee_lines.append((0,0,rs_consignee))
                
            vals = {'partner_id':blanket.customer_id and blanket.customer_id.id or False,
                    'invoice_address':blanket.invoice_address or False,
                    'street2':blanket.street2 or False,
                    'city':blanket.city or False,
                    'country_id':blanket.country_id and blanket.country_id.id or False,
                    'state_id':blanket.state_id and blanket.state_id.id or False,
                    'zip':blanket.zip or False,
                    'po_date':blanket.po_date or False,
                    'order_type':blanket.order_type or False,
                    'po_number':blanket.po_number or False,
                    'payment_term_id':blanket.payment_term_id and blanket.payment_term_id.id or False,
                    'currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'quotaion_no':blanket.quotaion_no or False,
                    'incoterms_id':blanket.incoterm_id and blanket.incoterm_id.id or False,
                    'distribution_channel':blanket.channel and blanket.channel.id or False,
                    'excise_duty_id':blanket.excise_duty_id and blanket.excise_duty_id.id or False,
                    'sale_tax_id':blanket.sale_tax_id and blanket.sale_tax_id.id or False, 
                    'reason':blanket.reason or False,
                    'amount_untaxed': blanket.amount_untaxed or False,
                    'order_line':blanket_lines or False,
                    'sale_consignee_line':consignee_lines or False,
                        }
        return {'value': vals}    

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        return super(sale_order_line, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'product_uom':product.uom_id.id})
        return super(sale_order_line, self).write(cr, uid,ids, vals, context)
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        subtotal = 0.0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.order_id.excise_duty_id.amount/100)
            res[line.id] = subtotal
        return res
     
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required = True),
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'freight': fields.float('Freight'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    def onchange_product_id(self, cr, uid, ids, product_id = False, context=None):
        vals = {}
        if product_id :
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'product_type':product.type,
                    'product_uom':product.uom_id.id,
                    'price_unit':product.list_price,
                    'name': product.name
                    }
        return {'value': vals}
sale_order_line()

class tpt_sale_order_consignee(osv.osv):
    _name = "tpt.sale.order.consignee"
    
    def quatity_consignee(self, cr, uid, ids, field_name, args, context=None):
        quatity = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            for order_line in line.sale_order_consignee_id.order_line:
                if order_line.product_id.id == line.product_id.id:
                    quatity = order_line.product_uom_qty
            res[line.id] = quatity
        return res
                
            
          
    _columns = {
        'sale_order_consignee_id': fields.many2one('sale.order', 'Consignee'),
        'name_consignee_id': fields.many2one('res.partner', 'Consignee', required = True),
        'location': fields.char('Location', size = 1024),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.function(quatity_consignee, type='float',string='Quatity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
                }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id :
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'uom_po_id':product.uom_id.id,
                    }
        return {'value': vals}
      
tpt_sale_order_consignee()

class tpt_blanket_order(osv.osv):
    _name = "tpt.blanket.order"
    
    def amount_all_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val1 = 0.0
            val2 = 0.0
            val3 = 0.0
            for orderline in line.blank_order_line:
                val1 += orderline.sub_total
            res[line.id]['amount_untaxed'] = val1
            val2 = val1 * line.sale_tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
            val3 = val1 + val2
            res[line.id]['amount_total'] = val3
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.blank.order.line').browse(cr, uid, ids, context=context):
            result[line.blanket_order_id.id] = True
        return result.keys()

    _columns = {
        'name': fields.char('Blanked Order', size = 1024, readonly=True),
        'customer_id': fields.many2one('res.partner', 'Customer', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'invoice_address': fields.char('Invoice Address', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'street2': fields.char('', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'city': fields.char('', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'country_id': fields.many2one('res.country', '', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state_id': fields.many2one('res.country.state', '', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'zip': fields.char('', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'bo_date': fields.date('BO Date', required = True, readonly = True,  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'po_date': fields.date('PO Date', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'po_number': fields.char('PO Number', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'quotaion_no': fields.char('Quotaion No', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'excise_duty_id': fields.many2one('account.tax', 'Excise Duty', domain="[('type_tax_use','=','excise_duty')]", required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'sale_tax_id': fields.many2one('account.tax', 'Sale Tax', domain="[('type_tax_use','=','sale')]", required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}), 
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterms', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'reason': fields.text('Reason', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'exp_delivery_date': fields.date('Expected delivery Date', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'channel': fields.many2one('crm.case.channel', 'Distribution Channel', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'document_type':fields.selection([('blankedorder','Blanked Order')], 'Document Type',required=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'blank_order_line': fields.one2many('tpt.blank.order.line', 'blanket_order_id', 'Sale Order', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_untaxed': fields.function(amount_all_blanket_orderline, multi='sums',string='Untaxed Amount',
                                         store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10),}, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Taxes',
                                      store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_total': fields.function(amount_all_blanket_orderline, multi='sums',string='Total',
                                        store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10), },
             states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        
        'blank_consignee_line': fields.one2many('tpt.consignee', 'blanket_consignee_id', 'Consignee', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}), 
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True),
    }
    
    
    _defaults = {
        'state': 'draft',
        'name': '/',
        'document_type': 'blankedorder',
        'bo_date': time.strftime('%Y-%m-%d'),
    }
    
#     def _check_bo_date(self, cr, uid, ids, context=None):
        
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'done'})
        return True   
    
    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'cancel'})
        return True   
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.blanked.order.import') or '/'
        return super(tpt_blanket_order, self).create(cr, uid, vals, context=context)
    
    def onchange_customer_id(self, cr, uid, ids,customer_id=False, context=None):
        vals = {}
        consignee_lines = []
        if customer_id:
            for blanket in self.browse(cr, uid, ids):
                sql = '''
                    delete from tpt_consignee where blanket_consignee_id = %s
                '''%(blanket.id)
                cr.execute(sql)
            customer = self.pool.get('res.partner').browse(cr, uid, customer_id)
            for line in customer.consignee_line:
                rs = {
                        'name_consignee_id': line.id,
                        'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or '') + ' , ' + str(line.state_id.name or '') + ' , ' + str(line.country_id.name or '') + ' , ' +str(line.zip or ''),
                        
                      }
                consignee_lines.append((0,0,rs))
            
            vals = {'invoice_address': customer.street or False,
                    'street2': customer.street2 or False,
                    'city': customer.city or False,
                    'country_id': customer.country_id and customer.country_id.id or False,
                    'state_id': customer.state_id and customer.state_id.id or False,
                    'zip': customer.zip or False,
                    'payment_term_id':customer.property_payment_term and customer.property_payment_term.id or False,
                    'blank_consignee_line': consignee_lines or False,
                    'incoterm_id':customer.inco_terms_id and customer.inco_terms_id.id or False,
                    }
        return {'value': vals}
    
tpt_blanket_order()

class tpt_blank_order_line(osv.osv):
    _name = "tpt.blank.order.line"
    
    def subtotal_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'sub_total' : 0.0,
               }
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.blanket_order_id.excise_duty_id.amount/100)
            res[line.id]['sub_total'] = subtotal
        return res
    
    _columns = {
        'blanket_order_id': fields.many2one('tpt.blanket.order', 'Blank Order', ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Product', required = True),
        'description': fields.text('Description', required = True),
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'product_uom_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'price_unit': fields.float('Unit Price'),
        'sub_total': fields.function(subtotal_blanket_orderline, store = True, multi='deltas' ,string='SubTotal'),
        'freight': fields.float('Freight'),
                }
    
    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})
        return super(tpt_blank_order_line, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})
        return super(tpt_blank_order_line, self).write(cr, uid,ids, vals, context)
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'product_type':product.type,
                    'uom_po_id':product.uom_id.id,
                    'price_unit':product.list_price,
                    'description': product.name
                    }
        return {'value': vals}
      
tpt_blank_order_line()

class tpt_consignee(osv.osv):
    _name = "tpt.consignee"
    
    def quatity_consignee(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'product_uom_qty' : 0.0,
                }
            quatity = 0.0
            for order_line in line.blanket_consignee_id.blank_order_line:
                if order_line.product_id.id == line.product_id.id:
                    quatity = order_line.product_uom_qty
                         
            res[line.id]['product_uom_qty'] = quatity
        return res
    
#     def quatity_consignee(self, cr, uid, ids, field_name, args, context=None):
#         res = {}
#         for line in self.browse(cr,uid,ids,context=context):
#             res[line.id] = {
#                'product_uom_qty' : 0.0,
#                }
#             for order_line in line.blanket_consignee_id.blank_order_line:
#                 if order_line.product_id.id == line.product_id.id:
#                     quatity = order_line.product_uom_qty
#                         
#             res[line.id]['product_uom_qty'] = quatity
#         return res
    
    
    _columns = {
        'blanket_consignee_id': fields.many2one('tpt.blanket.order', 'Consignee'),
        'name_consignee_id': fields.many2one('res.partner', 'Consignee', required = True),
        'location': fields.char('Location', size = 1024),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.function(quatity_consignee, type = 'float',multi='deltas', string='Quatity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
                }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id :
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'uom_po_id':product.uom_id.id,
                    }
        return {'value': vals}
      
tpt_consignee()

class tpt_test_report(osv.osv):
    _name = "tpt.test.report"
      
    _columns = {
        'name': fields.many2one('product.product', 'Product', required = True),
        'grade':fields.char('Grade', size = 1024),
        'ph':fields.char('pH(5% of Slurry)', size = 1024),
        'moisture':fields.char('Moisture, % by mass', size = 1024),
        'iron':fields.char(' Iron, % by mass', size = 1024),
        'purity':fields.char(' Purity as FSH, % by mass', size = 1024),
        'ferric':fields.char('Ferric Iron, % by mass', size = 1024),
        'acid':fields.char('Free Acid, % by mass', size = 1024),
                }
tpt_test_report()

class tpt_batch_request(osv.osv):
    _name = "tpt.batch.request"
    
    _columns = {
        'name': fields.char('Request No', size = 1024,readonly=True),
        'sale_order_id': fields.many2one('sale.order', 'Sales Order'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'description': fields.text('Description'),
        'request_date': fields.date('Request Date'),
        'product_information_line': fields.one2many('tpt.product.information', 'product_information_id', 'Product Information'), 
                }
    _defaults={
    'name':'/',
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.batch.req.import') or '/'
        return super(tpt_batch_request, self).create(cr, uid, vals, context=context)
    
    
    def _check_sale_order_id(self, cr, uid, ids, context=None):
        for request in self.browse(cr, uid, ids, context=context):
            request_ids = self.search(cr, uid, [('id','!=',request.id),('sale_order_id','=',request.sale_order_id.id)])
            if request_ids:
                raise osv.except_osv(_('Warning!'),_('Sale Order ID already exists!'))
                return False
        return True
    
    def onchange_sale_order_id(self, cr, uid, ids,sale_order_id=False, context=None):
        vals = {}
        product_information_line = []
        if sale_order_id:
            sale = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
            for line in sale.order_line:
                rs = {
                      'product_id': line.product_id and line.product_id.id or False,
                      'product_type': line.product_type or False,
                      'application_id': line.application_id and line.application_id.id or False,
                      'product_uom_qty': line.product_uom_qty or False,
                      'uom_po_id': line.product_uom and line.product_uom.id or False,
                      }
                product_information_line.append((0,0,rs))
            
            vals = {'customer_id': sale.partner_id and sale.partner_id.id or False,
                    'product_information_line':product_information_line
                    }
        return {'value': vals}
    

tpt_batch_request()

class tpt_product_information(osv.osv):
    _name = "tpt.product.information"
     
    _columns = {
        'product_information_id': fields.many2one('tpt.batch.request', 'Batch Request'),          
        'product_id': fields.many2one('product.product', 'Product'),     
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),   
        'application_id': fields.many2one('crm.application', 'Application'),    
        'product_uom_qty': fields.float('Quantity'),   
        'uom_po_id': fields.many2one('product.uom', 'UOM'),     
                }
       
tpt_product_information()

class tpt_batch_number(osv.osv):
    _name = "tpt.batch.number"
     
    _columns = {
        'name': fields.char('System Batch No.', size = 1024,required = True),          
        'phy_batch_no': fields.char('Physical Batch No.', size = 1024,required = True),     
                }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('batch_number_selected'):
            sql = '''
                SELECT sys_batch FROM tpt_batch_allotment_line where sys_batch is not null
            '''
            cr.execute(sql)
            tpt_batch_number_ids = [row[0] for row in cr.fetchall()]
            batch_ids = self.search(cr, uid, [('id','not in',tpt_batch_number_ids)])
            if context.get('sys_batch'):
                batch_ids.append(context.get('sys_batch'))
            args += [('id','in',batch_ids)]
        return super(tpt_batch_number, self).search(cr, uid, args, offset, limit, order, context, count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

tpt_batch_number()

class tpt_batch_allotment(osv.osv):
    _name = "tpt.batch.allotment"
     
    _columns = {
        'batch_request_id':fields.many2one('tpt.batch.request','Batch Request No.',required = True), 
        'name':fields.date('Date Requested',required = True), 
        'sale_order_id':fields.many2one('sale.order','Sale Order'),   
        'customer_id':fields.many2one('res.partner', 'Customer', required = True), 
        'description':fields.text('Description'),
        'state': fields.selection([('to_approve', 'To Approved'), ('refuse', 'Refused'),('confirm', 'Approve'), ('cancel', 'Cancelled')],'Status'),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'batch_allotment_id', 'Product Information'), 
                }
    _defaults = {
              'state': 'to_approve',
    }
    def confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirm'})
        sale_obj = self.pool.get('sale.order')
        for batch_allotment in self.browse(cr,uid,ids,context=context):
            
            # cap nhat cho order line cua sale order giong nhu cua batch allotment
#             picking_out_ids = self.pool.get('stock.picking').search(cr,uid,[('sale_id','=',batch_allotment.sale_order_id.id)],context=context)
#             if not picking_out_ids:
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'sale.order', batch_allotment.sale_order_id.id, 'order_confirm', cr)
        
                # redisplay the record as a sales order
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
            view_id = view_ref and view_ref[1] or False,
    
            #Tim delivery_order cua Sale order do
#             picking_out_ids = self.pool.get('stock.picking').search(cr,uid,[('sale_id','=',batch_allotment.sale_order_id.id)],context=context)
#             sql = '''
#                 delete from stock_move where picking_id = %s
#             '''%(picking_out_ids[0])
#             cr.execute(sql)
#             date_planned = self.pool.get('sale.order')._get_date_planned(cr, uid, batch_allotment.sale_order_id, batch_allotment.sale_order_id.order_line, batch_allotment.sale_order_id.date_order, context=context)
#             location_id = batch_allotment.sale_order_id.shop_id.warehouse_id.lot_stock_id.id
#             output_id = batch_allotment.sale_order_id.shop_id.warehouse_id.lot_output_id.id
#             for line in batch_allotment.batch_allotment_line:
#                 
#                 res = {
#                     'name': line.product_id.name,
#                     'picking_id': picking_out_ids[0],
#                     'product_id': line.product_id.id,
#                     'date': batch_allotment.sale_order_id.expected_date or False,
#                     'date_expected': batch_allotment.sale_order_id.expected_date or False,
#                     'product_qty': line.product_uom_qty,
#                     'product_uom': line.uom_po_id.id,
#                     'product_uos_qty': line.product_uom_qty,
#                     'product_uos': line.uom_po_id.id,
# #                     'product_packaging': line.product_packaging.id,
#                     'partner_id': batch_allotment.sale_order_id.partner_id.id,
#                     'location_id': location_id,
#                     'location_dest_id': output_id,
# #                     'sale_line_id': line.id,
#                     'tracking_id': False,
#                     'state': 'draft',
#                     #'state': 'waiting',
#                     'company_id': batch_allotment.sale_order_id.company_id.id,
#                     'price_unit': 5000 or 0.0
#                 }
#                 self.pool.get('stock.move').create(cr, uid, res)
            #Kiem tra delivery_order lay Id ra roi kiem tra
            #Neu chua done hoac cancel thi xoa stock_move trong picking_out do
            #tao lai stock_move theo batch_allotment_line
            
            return {
                'type': 'ir.actions.act_window',
                'name': _('Sales Order'),
                'res_model': 'sale.order',
                'res_id': batch_allotment.sale_order_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                'nodestroy': True,
            }
    def refuse(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'refuse'})
    def cancelled(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})
    def onchange_batch_request_id(self, cr, uid, ids,batch_request_id=False):
        res = {'value':{
                        'name':False,
                        'sale_order_id':False,
                        'customer_id':False,
                        'description':False,
                        'batch_allotment_line':[],
                      }
               }
        if batch_request_id:
            batch = self.pool.get('tpt.batch.request').browse(cr, uid, batch_request_id)
            batch_allotment_line = []
            for line in batch.product_information_line:
                batch_allotment_line.append({
                          'product_id': line.product_id.id,
                          'product_uom_qty':line.product_uom_qty,
                          'product_type':line.product_type,
                          'uom_po_id': line.uom_po_id.id,
                          'application_id':line.application_id.id,
                    })
        res['value'].update({
                    'name':batch.request_date or False,
                    'sale_order_id':batch.sale_order_id and batch.sale_order_id.id or False,
                    'customer_id':batch.customer_id and batch.customer_id.id or False,
                    'description':batch.description or False,
                    'batch_allotment_line': batch_allotment_line,
        })
        return res
tpt_batch_allotment()

class tpt_form_403(osv.osv):
    _name = "tpt.form.403"
     
    _columns = {
        'from_place':fields.char('From Place', size = 1024),
        'to_place':fields.char('To Place', size = 1024),
        'from_district':fields.char('From District', size = 1024),
        'to_district':fields.char('To District', size = 1024),
        'name':fields.many2one('account.invoice','Invoice No'),
        'date':fields.related('name', 'date_invoice', type='date', string='Date',readonly=True),
        'consignor_name':fields.char('Name', size = 1024),
        'consignor_street': fields.char('Street', size = 1024),
        'consignor_street2': fields.char('', size = 1024),
        'consignor_city': fields.char('', size = 1024),
        'consignor_country_id': fields.many2one('res.country', ''),
        'consignor_state_id': fields.many2one('res.country.state', ''),
        'consignor_zip': fields.char('', size = 1024),
        'consignor_tel':fields.char('Telephone', size = 15),
        'consignor_fax':fields.char('Fax', size = 32),
        'consignor_certi_no':fields.char('Reg. Certificate No', size = 1024),
        'consignor_cst_no':fields.char('CST Reg No', size = 1024),
        'consignor_date_1':fields.date('Date'),
        'consignor_date_2':fields.date('Date'),
        'transporter_name':fields.char('Name', size = 1024),
        'transporter_street': fields.char('Street', size = 1024),
        'transporter_street2': fields.char('', size = 1024),
        'transporter_city': fields.char('', size = 1024),
        'transporter_country_id': fields.many2one('res.country', ''),
        'transporter_state_id': fields.many2one('res.country.state', ''),
        'transporter_zip': fields.char('', size = 1024),
        'transporter_owner':fields.char('Owner Partner Name', size = 1024),
        'transporter_vehicle_no':fields.char('Vehicle No', size = 32),
        'driver_name':fields.char('Name', size = 1024),
        'driver_street': fields.char('Street', size = 1024),
        'driver_street2': fields.char('', size = 1024),
        'driver_city': fields.char('', size = 1024),
        'driver_country_id': fields.many2one('res.country', ''),
        'driver_state_id': fields.many2one('res.country.state', ''),
        'driver_zip': fields.char('', size = 1024),
        'driver_licence':fields.char('Driving Licence Number', size = 1024),
        'driver_issuing':fields.char('Licence Issuing State', size = 1024),
        'good_name':fields.char('Name', size = 1024),
        'good_street': fields.char('Street', size = 1024),
        'good_street2': fields.char('', size = 1024),
        'good_city': fields.char('', size = 1024),
        'good_country_id': fields.many2one('res.country', ''),
        'good_state_id': fields.many2one('res.country.state', ''),
        'good_zip': fields.char('', size = 1024),
        'good_designation':fields.char('Designation', size = 1024),
        'entry_no':fields.char('Entry no', size = 64),
        'reason':fields.char('Reason for abnormal Stoppage', size = 1024),
        'result':fields.char('Result if any', size = 1024, required = True),
        'arrival':fields.datetime('Arrival Time', required = True),
        'departure':fields.datetime('Departure Time', required = True),
        'consignee_street': fields.char('Street', size = 1024),
        'consignee_street2': fields.char('', size = 1024),
        'consignee_city': fields.char('', size = 1024),
        'consignee_country_id': fields.many2one('res.country', ''),
        'consignee_state_id': fields.many2one('res.country.state', ''),
        'consignee_zip': fields.char('', size = 1024),
        'consignee_certi_no':fields.char('Reg. Certificate No', size = 1024),
        'consignee_cst_no':fields.char('CST Reg No', size = 1024),
        'consignee_value':fields.float('Consigned Value'),
        'consignee_line':fields.one2many('tpt.form.403.consignee','form_403_id','Consignee'),
        'inter_state':fields.boolean('Inter State Sale'),
        'tranfer':fields.boolean('Transfer of Documents of Title'),
        'deport_tranfer':fields.boolean('Depot Transfer'),
        'consigment':fields.boolean('Consignment to Branch/Agent'),
        'job_work':fields.boolean('For Job works/ Works contract'),
        'any_other':fields.boolean('Any Other'),
#         'selection_nature':fields.selection([('1','Inter State Sale'),
#                                              ('2','Transfer of Documents of Title'),
#                                              ('3','Depot Transfer'),
#                                              ('4','Consignment to Branch/Agent'),
#                                              ('5','For Job works/ Works contract'),
#                                              ('6','Any Other')],'Nature of Transaction',required=True),
                }
       
tpt_form_403()

class res_partner(osv.osv):
     _inherit = "res.partner"
      
     _columns = {
         'consignee_parent_id': fields.many2one('res.partner', 'Parent', ondelete = 'cascade'),
        'consignee_line': fields.one2many('res.partner', 'consignee_parent_id', 'Consignee'),
        'bill_location': fields.boolean('Is Bill To Location'), 
        'shipping_location': fields.boolean('Is Shipping Location'), 
                 }
     
res_partner()

class tpt_batch_allotment_line(osv.osv):
    _name = "tpt.batch.allotment.line"
    def get_phy_batch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for physical in self.browse(cr, uid, ids, context=context):
            res[physical.id] = {
                'phy_batch': physical.sys_batch and physical.sys_batch.phy_batch_no or False,
            }
        return res
     
    _columns = {
        'pgi_id':fields.many2one('tpt.pgi','PGI',ondelete='cascade'),
#         'delivery_order_id':fields.many2one('tpt.delivery.order','Delivery Order',ondelete='cascade'),
        'batch_allotment_id':fields.many2one('tpt.batch.allotment','Batch Allotment',ondelete='cascade'), 
        'product_id': fields.many2one('product.product','Product'),     
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),   
        'application_id': fields.many2one('crm.application','Application'),    
        'product_uom_qty': fields.float('Quantity'),   
        'uom_po_id': fields.many2one('product.uom','UOM'),   
        'sys_batch':fields.many2one('stock.production.lot','System Serial No.'), 
#         'phy_batch':fields.char('Physical Batch No.', size = 1024)
        'phy_batch':fields.function(get_phy_batch,type='char', size = 1024,string='Physical Serial No.',multi='sum',store=True),
                }
    def onchange_sys_batch(self, cr, uid, ids,sys_batch=False,qty=False,batch_allotment_line=False,context=None):
#         res = {'value':{
#                         'sys_batch':False
#                         }}
#         if sys_batch and qty:
#             batch = self.pool.get('stock.production.lot').browse(cr, uid, sys_batch)
#             if  batch.stock_available < qty:
#                 warning = {  
#                           'title': _('Warning'),  
#                           'message': _('The quantity product of sale order  is not greater than the quantity product in stock!'),  
#                           }  
#                 res['value'].update({'sys_batch':False,'warning':warning,})
# #                 raise osv.except_osv(_('Warning!'),_('The quantity product of sale order  is not greater than the quantity product in stock !'))
#             else:
#                 res['value'].update({'sys_batch':sys_batch,})
#         return res
        vals = {}
        if sys_batch and qty:
            batch = self.pool.get('stock.production.lot').browse(cr, uid, sys_batch)
            if  batch.stock_available < qty:
                warning = {  
                          'title': _('Warning!'),  
                          'message': _('The quantity product of sale order is not greater than the quantity product in stock!'),  
                          }  
                vals['sys_batch']=False
                return {'value': vals,'warning':warning}
            else:
                vals['sys_batch']= sys_batch
        return {'value': vals}
tpt_batch_allotment_line()

class tpt_pgi(osv.osv):
    _name = "tpt.pgi"
     
    _columns = {
#         'do_id':fields.many2one('tpt.delivery.order','Delivery Order',required = True), 
        'name':fields.date('DO Date',required = True), 
        'customer_id':fields.many2one('res.partner', 'Customer', required = True), 
        'warehouse':fields.char('Warehouse', size = 1024,required = True),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'pgi_id', 'Product'), 
                }
tpt_pgi()

class tpt_form_403_consignee(osv.osv):
    _name = "tpt.form.403.consignee"
      
    _columns = {
        'number': fields.char('SI.No',size = 32, readonly = True),
        'description': fields.char('Description of Goods',size =1024),
        'commodity': fields.char('Commodity Code',size = 1024),
        'unity_code': fields.char('Unity Code',size = 1024),
        'rate_of_tax': fields.char('Rate of Tax',size = 1024),
        'value': fields.char('Value',size = 1024, required = True),
        'form_403_id':fields.many2one('tpt.form.403','Consignee'),
                
                }
    _defaults = {
        'number': ' ',
    }
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('form_403_id','=',line.form_403_id.id),('number','>',line.number)])
            if update_ids:
                cr.execute("UPDATE tpt_form_403_consignee SET number=number-1 WHERE id in %s",(tuple(update_ids),))
        return super(tpt_form_403_consignee, self).unlink(cr, uid, ids, context)  
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('form_403_id',False):
            vals['number'] = len(self.search(cr, uid,[('form_403_id', '=', vals['form_403_id'])])) + 1
        return super(tpt_form_403_consignee, self).create(cr, uid, vals, context)
tpt_form_403_consignee()

class tpt_form_are_3(osv.osv):
    _name = "tpt.form.are.3"
      
    _columns = {
        'name': fields.char('SI.No',size = 32, required = True),
        'range_from': fields.char('From Range',size =1024),
        'range_to': fields.char('To Range',size = 1024),
        'reg_no_from': fields.char('From CE Reg No',size =1024),
        'reg_no_to': fields.char('To CE Reg No',size = 1024),
        'division_from': fields.char('From Division',size =1024, required = True),
        'division_to': fields.char('To Division',size = 1024,  required = True),
        'warehouse_from': fields.char('From Warehouse',size =1024,  required = True),
        'warehouse_to': fields.char('To Warehouse',size = 1024,  required = True),
        'to_mr_mess': fields.char('To Mr./Messrs.',size = 1024),
        'invoice_no_id': fields.many2one('account.invoice','Invoice No'),
        'date': fields.date('Date', required = True),
        'warehouse_register':fields.char('No. in Warehouse Register',size = 1024),
        'good_description':fields.char('Good Description',size = 1024),
        'remarks':fields.char('Remarks',size = 1024),
        'package_description':fields.char('No. & Package Description',size = 1024),
        'tranport':fields.char('Tranport Manner',size = 1024),
        'gross_weight':fields.float('Package gross weight'),
        'good_qty':fields.float('Good Qty'),
        'value':fields.float('Value'),
        'marks_package':fields.float('Marks & No on Packages'),
        'warehouse_date': fields.date('Warehouse Date of Entry', required = True),
        'invoiced_date': fields.date('Invoiced Date', required = True),
        'warehousing_date': fields.date('1st Warehousing Date', required = True),
        'duty_rate_line':fields.one2many('tpt.form.are.3.duty.rate','form_are_3_id','Duty Rate'),       
                }
tpt_form_are_3()

class tpt_form_are_3_duty_rate(osv.osv):
    _name = "tpt.form.are.3.duty.rate"
      
    _columns = {
        'duty_rate': fields.float('Duty Rate in %', required = True),
        'amount_usd': fields.float('Amount(in USD)', required = True),
        'amount_inr': fields.float('Amount(in INR)', required = True),
        'form_are_3_id': fields.many2one('tpt.form.are.3', 'Duty Rate'),
                }
tpt_form_are_3_duty_rate()

class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    _columns = {
        'phy_batch_no': fields.char('Physical Serial No.', size = 1024,required = True), 
                }
stock_production_lot()  


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
