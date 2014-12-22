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

class sale_order(osv.osv):
    _inherit = "sale.order"
    
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
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    _columns = {
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True),
        'blanket_id':fields.many2one('tpt.blanket.order','Blanket Order'),
#         'so_date':fields.date('SO Date'),
        'po_date':fields.date('PO Date'),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term'),
        'document_type':fields.selection([('saleorder','Sale Order'),('return','Return Sales Order'),('scrap','Scrap Sales')],'Document Type' ,required=True),
        'po_number':fields.char('PO Number', size = 1024),
        'reason':fields.text('Reason'),
        'quotaion_no':fields.char('Quotaion No', size = 1024),
        'expected_date':fields.date('Expected delivery Date'),
        'document_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)')],'Document Status' ,required=True),
        'incoterms_id':fields.many2one('stock.incoterms','Incoterms',required = True),
        'distribution_channel':fields.many2one('crm.case.channel','Distribution Channel',required = True),
        'sale_tax':fields.many2one('account.tax','Sales Tax',required = True),
        'excise_duty': fields.many2one('tpt.excise.duty', 'Excise Duty'),
        'invoice_address': fields.char('Invoice Address', size = 1024),
        'street2': fields.char('', size = 1024),
        'city': fields.char('', size = 1024),
        'country_id': fields.many2one('res.country', ''),
        'state_id': fields.many2one('res.country.state', ''),
        'zip': fields.char('', size = 1024),
        'sale_consignee_line':fields.one2many('tpt.sale.order.consignee','sale_order_consignee_id','Consignee')
    }
    _defaults = {
#         'so_date': time.strftime('%Y-%m-%d'),
    }
    def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
        vals = {}
        blanket_lines = []
        consignee_lines = []
        if blanket_id:
            blanket = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
            for blanket_line in blanket.blank_order_line:
                rs_order = {
                      'product_id': blanket_line.product_id.id,
                      'name': blanket_line.description,
                      'product_type': blanket_line.product_type,
                      'application_id': blanket_line.application_id.id,
                      'product_uom_qty': blanket_line.product_uom_qty,
                      'product_uom': blanket_line.uom_po_id.id,
                      'price_unit': blanket_line.price_unit,
#                       'price_subtotal': blanket_line.sub_total,
                      'freight': blanket_line.freight,
                      }
                blanket_lines.append((0,0,rs_order))
              
            for consignee_line in blanket.blank_consignee_line:
                rs_consignee = {
                      'name': consignee_line.name,
                      'location': consignee_line.location,
                      'product_id': consignee_line.product_id.id,
                      'product_uom_qty': consignee_line.product_uom_qty,
                      'uom_po_id': consignee_line.uom_po_id.id,
                                }
                consignee_lines.append((0,0,rs_consignee))
                
            vals = {'partner_id':blanket.customer_id.id,
                    'invoice_address':blanket.invoice_address,
                    'street2':blanket.street2,
                    'city':blanket.city,
                    'country_id':blanket.country_id.id,
                    'state_id':blanket.state_id.id,
                    'zip':blanket.zip,
                    'po_date':blanket.po_date,
                    'order_type':blanket.order_type,
                    'po_number':blanket.po_number,
                    'payment_term_id':blanket.payment_term_id.id,
                    'currency_id':blanket.currency_id.id,
                    'quotaion_no':blanket.quotaion_no,
                    'incoterms_id':blanket.incoterm_id.id,
                    'distribution_channel':blanket.channel.id,
                    'excise_duty':blanket.excise_duty.id,
                    'sale_tax':blanket.sale_tax_id.id,
                    'reason':blanket.reason,
#                     'amount_untaxed': blanket.amount_untaxed,
                    'order_line':blanket_lines,
                    'sale_consignee_line':consignee_lines,
                        
                        }
        return {'value': vals}    

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        subtotal = 0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.order_id.excise_duty.name/100)
            res[line.id] = subtotal
        return res
     
    _columns = {
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'freight': fields.float('Freight'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }
    
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
        'name': fields.char('Consignee Name', size = 1024, required = True),
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
                val1 = val1 + orderline.sub_total
                res[line.id]['amount_untaxed'] = val1
#             val2 = line.amount_untaxed * line.sale_tax_id.amount / 100
            val2 = val1 * line.sale_tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
#             val3 = res[line.id]['amount_untaxed'] + res[line.id]['amount_tax']
            val3 = val1 + val2
            res[line.id]['amount_total'] = val3
        return res
    
#     def amount_total_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
#         amount_total = 0
#         res = {}
#         for line in self.browse(cr,uid,ids,context=context):
#             for orderline in line.blank_order_line:
#                 amount_total = line.amount_untaxed + line.amount_tax + orderline.freight
#             res[line.id] = amount_total
#         return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.blank.order.line').browse(cr, uid, ids, context=context):
            result[line.blanket_order_id.id] = True
        return result.keys()

    _columns = {
        'name': fields.char('Blanked Order', size = 1024, readonly=True),
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
        'amount_untaxed': fields.function(amount_all_blanket_orderline, multi='sums',string='Untaxed Amount',
                                         store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'product_uom_qty'], 10),
            },),
        'amount_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Taxes'),
        'amount_total': fields.function(amount_all_blanket_orderline, multi='sums',string='Total'),
        
        'blank_consignee_line': fields.one2many('tpt.consignee', 'blanket_consignee_id', 'Consignee'), 
    }
    
    
    _defaults = {
        'name': '/',
        'document_type': 'blankedorder',
        'bo_date': time.strftime('%Y-%m-%d'),
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.blanked.order.import') or '/'
        return super(tpt_blanket_order, self).create(cr, uid, vals, context=context)
    
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
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'sub_total' : 0.0,
               }
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.blanket_order_id.excise_duty.name/100)
            res[line.id]['sub_total'] = subtotal
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
        'sub_total': fields.function(subtotal_blanket_orderline, store = True, multi='deltas' ,string='SubTotal'),
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
        'name': fields.char('Consignee Name', size = 1024, required = True),
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
        'product_id': fields.many2one('product.product', 'Product', required = True),
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
