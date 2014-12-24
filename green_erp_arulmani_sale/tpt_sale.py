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
#         'name': fields.char('Order Reference', size=64, required=True, readonly=True, select=True),
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
        'sale_consignee_line':fields.one2many('tpt.sale.order.consignee','sale_order_consignee_id','Consignee')
    }
    _defaults = {
#                  'name': lambda obj, cr, uid, context: '/',
#         'so_date': time.strftime('%Y-%m-%d'),
    }
    def onchange_partner_id(self, cr, uid, ids, partner_id=False, context=None):
        vals = {}
        if partner_id :
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            vals = {'invoice_address':part.street,
                    'street2':part.street2,
                    'city':part.city,
                    'country_id':part.country_id.id,
                    'state_id':part.state_id.id,
                    'zip':part.zip,
                    
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
                      'name_consignee': consignee_line.name_consignee,
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
        'name_consignee': fields.char('Consignee Name', size = 1024, required = True),
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
        consignee_lines = []
        if customer_id:
            customer = self.pool.get('res.partner').browse(cr, uid, customer_id)
            for line in customer.consignee_line:
                rs = {
                        'name_consignee': line.name,
                        'location': str(line.street) + str(line.street2) + ' , ' + str(line.city) + ' , ' + str(line.state_id.name) + ' , ' + str(line.country_id.name) + ' , ' +str(line.zip),
                      }
                consignee_lines.append((0,0,rs))
            
            vals = {'invoice_address': customer.street,
                    'street2': customer.street2,
                    'city': customer.city,
                    'country_id': customer.country_id.id,
                    'state_id': customer.state_id.id,
                    'zip': customer.zip,
                    'payment_term_id':customer.property_payment_term.id,
                    'blank_consignee_line': consignee_lines,
#                     'excise_duty_id':customer.excise_duty_id.id,
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
        'name_consignee': fields.char('Consignee', size = 1024),
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

class tpt_form_403(osv.osv):
    _name = "tpt.form.403"
     
    _columns = {
        'name':fields.char('Form 403', size = 1024),
        'from_place':fields.char('From Place', size = 1024),
        'to_place':fields.char('To Place', size = 1024),
        'from_district':fields.char('From District', size = 1024),
        'to_district':fields.char('To District', size = 1024),
        'invoice_no':fields.char('Invoice No', size = 1024),
        'date':fields.date('Date'),
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
        'departure':fields.datetime('Departure Time'),
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
        'selection_nature':fields.selection([('1','Inter State Sale'),
                                             ('2','Transfer of Documents of Title'),
                                             ('3','Depot Transfer'),
                                             ('4','Consignment to Branch/Agent'),
                                             ('5','For Job works/ Works contract'),
                                             ('6','Any Other')],'Nature of Transaction',required=True),
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
        'warehouse_register':fields.char('No in Warehouse Register',size = 1024),
        'good_description':fields.char('Good Description',size = 1024),
        'remarks':fields.char('Remarks',size = 1024),
        'package_description':fields.char('No & Package Description',size = 1024),
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
