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
        'sale_consignee_line':fields.one2many('tpt.sale.order.consignee','sale_order_consignee_id','Consignee')
    }
    _defaults = {
#         'so_date': time.strftime('%Y-%m-%d'),
    }
    
    def _check_blanket_order_id(self, cr, uid, ids, context=None):
        for blanket in self.browse(cr, uid, ids, context=context):
            blanket_ids = self.search(cr, uid, [('id','!=',blanket.id),('blanket_id','=',blanket.blanket_id.id)])
            if blanket_ids:
                raise osv.except_osv(_('Warning!'),_('The data is not suitable!'))  
                return False
        return True
    _constraints = [
        (_check_blanket_order_id, 'Identical Data', ['blanket_id']),
        ]
    
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
                      'price_subtotal': blanket_line.sub_total,
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
                    'excise_duty_id':blanket.excise_duty_id.id,
                    'sale_tax_id':blanket.sale_tax_id.id,
                    'reason':blanket.reason,
                    'amount_untaxed': blanket.amount_untaxed,
                    'order_line':blanket_lines,
                    'sale_consignee_line':consignee_lines,
                        
                        }
        return {'value': vals}    

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        subtotal = 0.0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.order_id.excise_duty_id.amount/100)
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
            val2 = val1 * line.sale_tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
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
        'customer_id': fields.many2one('res.partner', 'Customer', required = True, states={'cancel': [('readonly', True)]}),
        'invoice_address': fields.char('Invoice Address', size = 1024, states={'cancel': [('readonly', True)]}),
        'street2': fields.char('', size = 1024, states={'cancel': [('readonly', True)]}),
        'city': fields.char('', size = 1024, states={'cancel': [('readonly', True)]}),
        'country_id': fields.many2one('res.country', '', states={'cancel': [('readonly', True)]}),
        'state_id': fields.many2one('res.country.state', '', states={'cancel': [('readonly', True)]}),
        'zip': fields.char('', size = 1024, states={'cancel': [('readonly', True)]}),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', states={'cancel': [('readonly', True)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', states={'cancel': [('readonly', True)]}),
        'bo_date': fields.date('BO Date', required = True, states={'cancel': [('readonly', True)]}),
        'po_date': fields.date('PO Date', required = True, states={'cancel': [('readonly', True)]}),
        'po_number': fields.char('PO Number', size = 1024, states={'cancel': [('readonly', True)]}),
        'quotaion_no': fields.char('Quotaion No', size = 1024, states={'cancel': [('readonly', True)]}),
        'excise_duty_id': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]", required = True, states={'cancel': [('readonly', True)]}),
        'sale_tax_id': fields.many2one('account.tax', 'Sale Tax', domain="[('type_tax_use','=','sale')]", required = True, states={'cancel': [('readonly', True)]}), 
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterms', required = True, states={'cancel': [('readonly', True)]}),
        'reason': fields.text('Reason', states={'cancel': [('readonly', True)]}),
        'exp_delivery_date': fields.date('Expected delivery Date', required = True, states={'cancel': [('readonly', True)]}),
        'channel': fields.many2one('crm.case.channel', 'Distribution Channel', states={'cancel': [('readonly', True)]}),
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True, states={'cancel': [('readonly', True)]}),
        'document_type':fields.selection([('blankedorder','Blanked Order')], 'Document Type',required=True, states={'cancel': [('readonly', True)]}),
        'blank_order_line': fields.one2many('tpt.blank.order.line', 'blanket_order_id', 'Sale Order', states={'cancel': [('readonly', True)]}),
        'amount_untaxed': fields.function(amount_all_blanket_orderline, multi='sums',string='Untaxed Amount',
                                         store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10),
            }, states={'cancel': [('readonly', True)]}),
        'amount_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Taxes'
#                                       store={
#                 'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
#                 'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10), },
            , states={'cancel': [('readonly', True)]}),
        'amount_total': fields.function(amount_all_blanket_orderline, multi='sums',string='Total',
#                                         store={
#                 'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line'], 10),
#                 'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10), },
             states={'cancel': [('readonly', True)]}),
        
        'blank_consignee_line': fields.one2many('tpt.consignee', 'blanket_consignee_id', 'Consignee', states={'cancel': [('readonly', True)]}), 
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel')],'Status', readonly=True),
    }
    
    
    _defaults = {
        'state': 'draft',
        'name': '/',
        'document_type': 'blankedorder',
        'bo_date': time.strftime('%Y-%m-%d'),
    }
    
#     def _check_bo_date(self, cr, uid, ids, context=None):
        
    
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
        if customer_id:
            customer = self.pool.get('res.partner').browse(cr, uid, customer_id)
            vals = {'invoice_address': customer.street,
                    'street2': customer.street2,
                    'city': customer.city,
                    'country_id': customer.country_id.id,
                    'state_id': customer.state_id.id,
                    'zip': customer.zip,
                    'payment_term_id':customer.property_payment_term.id,
#                     'excise_duty_id':customer.excise_duty_id.id,
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

class tpt_batch_number(osv.osv):
    _name = "tpt.batch.number"
     
    _columns = {
        'name': fields.char('System Batch No.', size = 1024),          
        'phy_batch_no': fields.char('Physical Batch No.', size = 1024),     
                }

tpt_batch_number()

class tpt_batch_allotment(osv.osv):
    _name = "tpt.batch.allotment"
     
    _columns = {
        'batch_request_id':fields.many2one('tpt.batch.request', 'Batch Request No.',required = True), 
        'name':fields.date('Date Requested',required = True), 
        'sale_order_id':fields.many2one('sale.order', 'Sale Order'),   
        'customer_id':fields.many2one('res.partner', 'Customer', required = True), 
        'description':fields.text('Description'),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'product_information_id', 'Product Information'), 
                }
tpt_batch_allotment()

class tpt_batch_allotment_line(osv.osv):
    _name = "tpt.batch.allotment.line"
     
    _columns = {
        'batch_allotment_id':fields.many2one('tpt.batch.allotment', 'Batch Allotment',ondelete='cascade'), 
        'product_id': fields.many2one('product.product', 'Product'),     
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),   
        'application_id': fields.many2one('crm.application', 'Application'),    
        'product_uom_qty': fields.float('Quantity'),   
        'uom_po_id': fields.many2one('product.uom', 'UOM'),   
        'sys_batch':fields.many2one('tpt.batch.number', 'System Batch No.'), 
        'phy_batch':fields.float('Physical Batch No.'),  
                }
tpt_batch_allotment_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
