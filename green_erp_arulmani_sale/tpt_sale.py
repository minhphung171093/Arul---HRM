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

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True),
        'blanket_id':fields.many2one('tpt.blanket.order','Blanket Order',required = True),
        'so_date':fields.date('SO Date'),
        'po_date':fields.date('PO Date'),
        'document_type':fields.selection([('saleorder','Sale Order'),('return','Return Sales Order'),('scrap','Scrap Sales')],'Document Type' ,required=True),
        'po_number':fields.char('PO Number', size = 1024),
        'reason':fields.text('Reason'),
        'quotaion_no':fields.char('Quotaion No', size = 1024),
        'expected_date':fields.date('Expected delivery Date'),
        'document_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)')],'Document Status' ,required=True),
        'incoterms_id':fields.many2one('stock.incoterms','Incoterms',required = True),
        'distribution_chanel':fields.many2one('crm.case.channel','Distribution Chanel',required = True),
        'sale_tax':fields.many2one('account.tax','Sales Tax',required = True),
        'excise_duty':fields.char('Excise Duty',size = 1024),
    }
    _defaults = {
        'so_date': time.strftime('%Y-%m-%d'),
    }
#     def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
#         vals = {}
#         if blanket_id:
#             emp = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
#             vals = {'partner_id':emp.customer_id.id,
#                     'partner_invoice_id':emp.invoice_address,
#                     'payment_term':emp.payment_term_id.id,
#                     'po_date':emp.po_date,
#                     'order_type':emp.order_type,
#                     'po_number':emp.po_number,
#                     'currency_id':emp.currency_id.id,
#                     'quotaion_no':emp.quotaion_no,
#                     'incoterms_id':emp.incoterm_id.id,
#                     'distribution_chanel':emp.po_number,
#                     'currency_id':emp.currency_id.id,
#                     'quotaion_no':emp.quotaion_no,
#                     'excise_duty':emp.excise_duty,
#                     'sale_tax':emp.sale_tax_id.id,
#                     'reason':emp.reason,
#                     }
#         return {'value': vals}

sale_order()



class tpt_blanket_order(osv.osv):
    _name = "tpt.blanket.order"
    
    def amount_untaxed_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        amount_untaxed = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            for orderline in line.blank_order_line:
                amount_untaxed = orderline.sub_total
            res[line.id] = amount_untaxed
        return res
    
    def amount_tax_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        amount_tax = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            amount_tax = line.amount_untaxed * line.sale_tax_id.amount / 100
            res[line.id] = amount_tax
        return res
    
    def amount_total_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        amount_total = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            for orderline in line.blank_order_line:
                amount_total = line.amount_untaxed + line.amount_tax + orderline.freight
            res[line.id] = amount_total
        return res
    
    _columns = {
        'name': fields.char('Blanked Order', size = 1024, required = True),
        'customer_id': fields.many2one('res.partner', 'Customer', required = True),
        'invoice_address': fields.char('Invoice Address', size = 1024),
        'street2': fields.char('', size = 1024),
        'city': fields.char('', size = 1024),
        'country_id': fields.many2one('res.country', ''),
        'state_id': fields.many2one('res.country.state', ''),
        'zip': fields.char('', size = 1024),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
        'bo_date': fields.date('BO Date', required = True),
        'po_date': fields.date('PO Date', required = True),
        'po_number': fields.char('PO Number', size = 1024),
        'quotaion_no': fields.char('Quotaion No', size = 1024),
        'excise_duty': fields.many2one('tpt.excise.duty', 'Excise Duty', required = True), 
        'sale_tax_id': fields.many2one('account.tax', 'Sale Tax', required = True), 
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterms', required = True),
        'reason': fields.text('Reason'),
        'exp_delivery_date': fields.date('Expected delivery Date', required = True),
        'channel': fields.many2one('crm.case.channel', 'Distribution Channel'),
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True),
        'document_type':fields.selection([('blankedorder','Blanked Order')], 'Document Type',required=True),
        'amount_untaxed': fields.function(amount_untaxed_blanket_orderline, type='float',string='Untaxed Amount'),
        'amount_tax': fields.function(amount_tax_blanket_orderline, type='float',string='Taxes'),
        'amount_total': fields.function(amount_total_blanket_orderline, type='float',string='Total'),
        'blank_order_line': fields.one2many('tpt.blank.order.line', 'blanket_order_id', 'Sale Order'), 
        'blank_consignee_line': fields.one2many('tpt.consignee', 'blanket_consignee_id', 'Consignee'), 
    }
    
    
    _defaults = {
        'name': lambda self,cr,uid,ctx=None: self.pool.get('ir.sequence').get(cr, uid, 'tpt.blanked.import'),        
        'document_type': 'blankedorder',
        'bo_date': time.strftime('%Y-%m-%d'),
        
    }
    
    def onchange_customer_id(self, cr, uid, ids,customer_id=False, context=None):
        vals = {}
        if customer_id:
            customer = self.pool.get('res.partner').browse(cr, uid, customer_id)
            vals = {'invoice_address': customer.street,
                    'street2': customer.street2,
                    'city': customer.city,
                    'country_id': customer.country_id.id,
                    'state_id': customer.state_id.id,
                    'zip': customer.zip,
                    'payment_term_id':customer.property_payment_term.id,
                    'excise_duty':customer.excise_duty,
                    }
        return {'value': vals}
    
tpt_blanket_order()

class tpt_excise_duty(osv.osv):
    _name = "tpt.excise.duty"
      
    _columns = {
        'name': fields.float('Excise Duty', required = True),
                }
tpt_excise_duty()

class tpt_blank_order_line(osv.osv):
    _name = "tpt.blank.order.line"
    
    def subtotal_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        subtotal = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.blanket_order_id.excise_duty.name/100)
            res[line.id] = subtotal
        return res
    
    _columns = {
        'blanket_order_id': fields.many2one('tpt.blanket.order', 'Blank Order', ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Product'),
        'description': fields.text('Description'),
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'product_uom_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
        'price_unit': fields.float('Unit Price'),
        'sub_total': fields.function(subtotal_blanket_orderline, type='float',string='SubTotal'),
        'freight': fields.float('Freight'),
                }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'product_type':product.type,
                    'uom_po_id':product.uom_id.id,
                    'price_unit':product.list_price,
                    'description': product.description_purchase
                    }
        return {'value': vals}
      
tpt_blank_order_line()

class tpt_consignee(osv.osv):
    _name = "tpt.consignee"
    
    def quatity_consignee(self, cr, uid, ids, field_name, args, context=None):
        quatity = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            for order_line in line.blanket_consignee_id.blank_order_line:
                if order_line.product_id.id == line.product_id.id:
                    quatity = order_line.product_uom_qty
                        
            res[line.id] = quatity
        return res
    
    
    _columns = {
        'blanket_consignee_id': fields.many2one('tpt.blanket.order', 'Consignee'),
        'name': fields.char('Consignee Name', size = 1024, required = True),
        'location': fields.char('Location', size = 1024),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.function(quatity_consignee, type='float',string='Quatity'),
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

class tpt_batch_request(osv.osv):
    _name = "tpt.batch.request"
     
    _columns = {
        'name': fields.char('Request No', size = 1024, required = True),
        'sale_order_id': fields.many2one('sale.order', 'Sales Order'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'description': fields.text('Description'),
        'product_information_line': fields.one2many('tpt.product.information', 'product_information_id', 'Product Information'), 
                }
    
#     _defaults = {
#         'name': lambda self,cr,uid,ctx=None: self.pool.get('ir.sequence').get(cr, uid, 'tpt.batch.request.import'),        
#     }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.batch.request.import') or '/'
        return super(tpt_batch_request, self).create(cr, uid, vals, context=context)
    
    def _check_sale_order_id(self, cr, uid, ids, context=None):
        for request in self.browse(cr, uid, ids, context=context):
            request_ids = self.search(cr, uid, [('id','!=',request.id),('sale_order_id','=',request.sale_order_id.id)])
            if request_ids:
                raise osv.except_osv(_('Warning!'),_('Sale Order ID already exists!'))
                return False
        return True

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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
