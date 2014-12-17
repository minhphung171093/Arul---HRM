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
    def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
        vals = {}
        if blanket_id:
            emp = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
            vals = {'partner_id':emp.customer_id.name,
                    'partner_invoice_id':emp.invoice_address,
#                     'payment_term_id':emp.payment_term_id.id,
                    'po_date':emp.po_date,
                    'order_type':emp.order_type,
                    'po_number':emp.po_number,
                    'currency_id':emp.currency_id.id,
                    'quotaion_no':emp.quotaion_no,
#                     'incoterms_id':emp.currency_id.id,
                    'distribution_chanel':emp.po_number,
                    'currency_id':emp.currency_id.id,
                    'quotaion_no':emp.quotaion_no,
                    }
        return {'value': vals}    

sale_order()



class tpt_blanket_order(osv.osv):
    _name = "tpt.blanket.order"
    _columns = {
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
        'blank_order_line': fields.one2many('tpt.blank.order.line', 'blanket_order_id', 'Sale Order'), 
        'blank_consignee_line': fields.one2many('tpt.consignee', 'blanket_consignee_id', 'Consignee'), 
    }
    
    _defaults = {
        'document_type': 'blankedorder',
        'bo_date': time.strftime('%Y-%m-%d'),
        
    }
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['customer_id'], context)
  
        for record in reads:
            name = record['customer_id']
            res.append((record['id'], name))
        return res 
    
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
        'name': fields.char('Excise Duty', size = 1024, required = True),
                }
tpt_excise_duty()

class tpt_blank_order_line(osv.osv):
    _name = "tpt.blank.order.line"
      
    _columns = {
        'blanket_order_id': fields.many2one('tpt.blanket.order', 'Blank Order', ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Product'),
        'description': fields.text('Description'),
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'product_uom_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
        'price_unit': fields.float('Unit Price'),
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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
