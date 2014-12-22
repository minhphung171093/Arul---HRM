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
        'blanket_id':fields.many2one('tpt.blanket.order','Blanket Order'),
#         'so_date':fields.date('SO Date'),
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
        
    def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
        vals = {}
        if blanket_id:
            emp = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
            vals = {'partner_id':emp.customer_id.name,
                    'invoice_address':emp.invoice_address,
                    'street2':emp.street2,
                    'city':emp.city,
                    'country_id':emp.country_id,
                    'state_id':emp.state_id,
                    'zip':emp.zip,
                    'po_date':emp.po_date,
                    'order_type':emp.order_type,
                    'po_number':emp.po_number,
                    'payment_term':emp.payment_term_id.id,
                    'currency_id':emp.currency_id.id,
                    'quotaion_no':emp.quotaion_no,
                    'incoterms_id':emp.incoterm_id.id,
                    'distribution_chanel':emp.po_number,
                    'excise_duty':emp.excise_duty,
                    'sale_tax':emp.sale_tax_id.id,
                    'reason':emp.reason,
                    }
        return {'value': vals}    

sale_order()

class tpt_sale_order_consignee(osv.osv):
    _name = "tpt.sale.order.consignee"
    
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
        'sale_order_consignee_id': fields.many2one('sale.order', 'Consignee'),
        'name': fields.char('Consignee Name', size = 1024, required = True),
        'location': fields.char('Location', size = 1024),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.function(quatity_consignee, store = True, type='float',string='Quatity'),
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
        'amount_untaxed': fields.function(amount_untaxed_blanket_orderline, type='float',string='Untaxed Amount'),
        'amount_tax': fields.function(amount_tax_blanket_orderline, type='float',string='Taxes'),
        'amount_total': fields.function(amount_total_blanket_orderline, type='float',string='Total'),
        'blank_order_line': fields.one2many('tpt.blank.order.line', 'blanket_order_id', 'Sale Order'), 
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

class tpt_form_403(osv.osv):
    _name = "tpt.form.403"
     
    _columns = {
        'name':fields.char('Form 403', size = 1024),
        'from_place':fields.char('From Place', size = 1024),
        'to_place':fields.char('To Place', size = 1024),
        'from_district':fields.char('From District', size = 1024),
        'to_district':fields.char('From District', size = 1024),
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
        'result':fields.char('Result if any', size = 1024),
        'arrival':fields.datetime('Arrival Time'),
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
