# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime, date
import datetime
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
                'cate_name': fields.char('Cate Name',size=64),    
                'warehouse_id':fields.many2one('stock.location', 'Sale Warehouse'),   ###TPT-BM-28/11/2015-TO OVERWRITE DUMMY FUNCTION OF THIS WAREHOUSE ID
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context and context.get('search_default_categ_id', False):
            args.append((('categ_id', 'child_of', context['search_default_categ_id'])))
        if context.get('search_blanket_id'):
            if context.get('blanket_id'):
                sql = '''
                    select product_id from tpt_blank_order_line where blanket_order_id in(select id from tpt_blanket_order where id = %s)
                '''%(context.get('blanket_id'))
                cr.execute(sql)
                blanket_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',blanket_ids)]
        if context.get('search_batch_request'):
            if context.get('batch_request_id'):
                sql = '''
                    select product_id from tpt_product_information where product_information_id in(select id from tpt_batch_request where id = %s)
                '''%(context.get('batch_request_id'))
                cr.execute(sql)
                request_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',request_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
#     def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
#         if not args:
#             args = []
#         if name:
#             ids = self.search(cr, user, [('default_code','=',name)]+ args, limit=limit, context=context)
#             if not ids:
#                 ids = self.search(cr, user, [('ean13','=',name)]+ args, limit=limit, context=context)
#             if not ids:
#                 # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
#                 # on a database with thousands of matching products, due to the huge merge+unique needed for the
#                 # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
#                 # Performing a quick memory merge of ids in Python will give much better performance
#                 ids = set()
#                 ids.update(self.search(cr, user, args + [('default_code',operator,name)], limit=limit, context=context))
#                 if not limit or len(ids) < limit:
#                     # we may underrun the limit because of dupes in the results, that's fine
#                     ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
#                 ids = list(ids)
#             if not ids:
#                 ptrn = re.compile('(\[(.*?)\])')
#                 res = ptrn.search(name)
#                 if res:
#                     ids = self.search(cr, user, [('default_code','=', res.group(2))] + args, limit=limit, context=context)
#         else:
#             ids = self.search(cr, user, args, limit=limit, context=context)
#         result = self.name_get(cr, user, ids, context=context)
#         return result

product_product()

class sale_order(osv.osv):
    _inherit = "sale.order"    
    _order = "date_order desc" #"blanket_id"
    
    def init(self, cr):
        sql = '''
            update sale_order set currency_id=tpt_currency_id
        '''
        cr.execute(sql)
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        order_line_obj = self.pool.get('sale.order.line')
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_total_cgst_tax': 0.0,
                'amount_total_sgst_tax': 0.0,
                'amount_total_igst_tax': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val1 = 0.0
            amount_total_cgst_tax = 0.0
            amount_total_sgst_tax = 0.0
            amount_total_igst_tax = 0.0
            total_tax = 0.0
            val2 = 0.0
            val3 = 0.0
            freight = 0.0
            for orderline in line.order_line:
                freight = freight + (orderline.product_uom_qty * orderline.freight)
                
                line_value = order_line_obj._get_tax_gst_amount(cr, uid, [orderline.id], None, None, None)[orderline.id]
                
                total_tax += line_value['tax_cgst_amount']+line_value['tax_sgst_amount']+line_value['tax_igst_amount']#(basic + p_f + ed)*(quotation.tax_id and quotation.tax_id.amount or 0) / 100
                amount_total_cgst_tax += line_value['tax_cgst_amount']
                amount_total_sgst_tax += line_value['tax_sgst_amount']
                amount_total_igst_tax += line_value['tax_igst_amount']
                
#                 total_tax += orderline.tax_cgst_amount+orderline.tax_sgst_amount+orderline.tax_igst_amount
#                 amount_total_cgst_tax += orderline.tax_cgst_amount
#                 amount_total_sgst_tax += orderline.tax_sgst_amount
#                 amount_total_igst_tax += orderline.tax_igst_amount
                
                val1 = val1 + orderline.price_subtotal
                val1 += freight #TPT-BM-01/07/2017-GST
                res[line.id]['amount_untaxed'] = round(val1)
                val2 = val1 * line.sale_tax_id.amount / 100
                
                
            amount_total_cgst_tax = round(amount_total_cgst_tax)
            amount_total_sgst_tax = round(amount_total_sgst_tax)
            amount_total_igst_tax = round(amount_total_igst_tax)
            total_tax = amount_total_cgst_tax+amount_total_sgst_tax+amount_total_igst_tax
            res[line.id]['amount_total_cgst_tax'] = amount_total_cgst_tax
            res[line.id]['amount_total_sgst_tax'] = amount_total_sgst_tax
            res[line.id]['amount_total_igst_tax'] = amount_total_igst_tax
            res[line.id]['amount_tax'] = total_tax
            #val3 = val1 + total_tax + freight
            val3 = val1 + total_tax 
            res[line.id]['amount_total'] = round(val3)
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys() 
    
    _columns = {
#         'name': fields.char('Order Reference', size=64, required=True, readonly=True, select=True),
        'order_type':fields.selection([('domestic','Domestic'),('export','Export')],'Order Type' ,required=True,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'blanket_id':fields.many2one('tpt.blanket.order','Blanket Order',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
#         'so_date':fields.date('SO Date'),
        'po_date':fields.date('PO Date',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term',required = True,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'document_type':fields.selection([('saleorder','Sale Order'),('return','Return Sales Order'),('scrap','Scrap Sales')],'Document Type' ,required=True,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'po_number':fields.char('PO Number', size = 50,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'reason':fields.text('Reason',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'quotaion_no':fields.char('Quotaion No', size = 40,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'expected_date':fields.date('Expected delivery Date',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'dispatch_date':fields.date('Scheduled Dispatch Date'), #TPT
        'document_status':fields.selection([('draft','Draft'),
                                            ('waiting','Waiting for Approval'),
                                            ('batch_allotted','Batch Allotted'),
                                            ('completed','Completed(Ready to Process)'),
                                            ('partially','Partially Delivered'),
                                            ('close','Closed(Delivered)'),
                                            ('cancelled','Cancelled')],'Document Status', readonly = True),
        'incoterms_id':fields.many2one('stock.incoterms','Incoterms',required = True,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'distribution_channel':fields.many2one('crm.case.channel','Distribution Channel',required = True,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'excise_duty_id': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]", required = False,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'sale_tax_id': fields.many2one('account.tax', 'Sale Tax', domain="[('type_tax_use','=','sale')]", required = True,states={'progress':[('readonly',True)],'done':[('readonly',True)]}), 
        'invoice_address': fields.char('Invoice Address', size = 1024,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'street2': fields.char('', size = 1024,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'street3': fields.char('', size = 1024,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'city': fields.char('', size = 1024,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'country_id': fields.many2one('res.country', '',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'state_id': fields.many2one('res.country.state', '',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'zip': fields.char('', size = 1024,states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','sale_tax_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','sale_tax_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total_cgst_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total CGSTAmt',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','sale_tax_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total_sgst_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total SGSTAmt',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','sale_tax_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total_igst_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total IGSTAmt',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','sale_tax_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','sale_tax_id'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, required=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order."),
        'sale_consignee_line':fields.one2many('tpt.sale.order.consignee','sale_order_consignee_id','Consignee',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'tpt_log_line': fields.one2many('tpt.log','sale_order_id', 'Logs'),
        'flag_t':fields.boolean('Flag',readonly =True,states={'progress':[('readonly',True)],'done':[('readonly',True)]} ),
        'flag_p':fields.boolean('Flag',readonly =True,states={'progress':[('readonly',True)],'done':[('readonly',True)]} ),
        'blanket_line_id':fields.many2one('tpt.blank.order.line','Blanket Order Line',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),#TPT
        'tpt_currency_id': fields.many2one('res.currency', 'Currency'),#TPT
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),       
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True), 
        ##
        'return_so_id':fields.many2one('sale.order','Base Sale Order',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'return_do_id':fields.many2one('stock.picking','Base DO',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'return_invoice_id':fields.many2one('account.invoice','Base Invoice',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        'return_date_order':fields.date('Return SO Date',states={'progress':[('readonly',True)],'done':[('readonly',True)]}),
        ##    
    }
    _defaults = {
#                  'name': lambda obj, cr, uid, context: '/',
        'po_date': time.strftime('%Y-%m-%d'),
        'expected_date': time.strftime('%Y-%m-%d'),
        'order_policy': 'picking',
        'document_status':'draft',
        'flag_t':False,
        'flag_p':False,
        'document_type':'saleorder',#TPT
    }
    
    def onchange_currency(self, cr, uid, ids, currency_id=False, context=None):
        return {'value':{'tpt_currency_id':currency_id}}
    
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

#     def onchange_doc_status(self, cr, uid, ids, payment_term_id=False, context=None):
#         vals = {}
#         if payment_term_id==1:
#              vals = {'document_status':'waiting'}
#         else:
#             vals = {'document_status':'completed'}
#         return {'value':vals}

  
#     def onchange_so_date(self, cr, uid, ids, date_order=False, blanket_id=False, context=None):
#         vals = {}
#         current = time.strftime('%Y-%m-%d')
#         warning = {}
#         if blanket_id:
#             blanket = self.pool.get('tpt.blanket.order').browse(cr,uid,blanket_id)
#             if date_order < blanket.bo_date:
#                 vals = {'date_order':current}
#                 warning = {
#                     'title': _('Warning!'),
#                     'message': _('PO Date: Allow back date, not allow future date')
#                 }
#         return {'value':vals,'warning':warning}    
    
    def onchange_partner_id(self, cr, uid, ids, part=False, blanket_id=False, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
            
        consignee_lines = []
#         for blanket in self.browse(cr, uid, ids):
#             sql = '''
#                 delete from order_line where blanket_order_id = %s
#             '''%(blanket.id)
#             cr.execute(sql)
        if part and not blanket_id:
            part = self.pool.get('res.partner').browse(cr, uid, part)
            val.update({'invoice_address':part.street,
                    'street2':part.street2,
                    'street3':part.street3,
                    'city':part.city,
                    'country_id':part.country_id and part.country_id.id or False,
                    'state_id':part.state_id and part.state_id.id or False,
                    'zip':part.zip,
                    'payment_term_id':part.property_payment_term and part.property_payment_term.id or False,
                    'incoterms_id':part.inco_terms_id and part.inco_terms_id.id or False,
                    'order_line':False,
                    }) 
        
        return {'value': val}
    ###
    def onchange_return_so_id(self, cr, uid, ids, return_so_id=False, context=None):
        vals = {}
        if return_so_id:
            sale_order = self.pool.get('sale.order').browse(cr, uid, return_so_id)
            for base_so_line in sale_order.order_line:
                rs_order = {
                       'product_id': base_so_line.product_id and base_so_line.product_id.id or False,
                       'name': base_so_line.name or False,
                       'product_type': base_so_line.product_type or False,
                       'application_id': base_so_line.application_id and base_so_line.application_id.id or False,
                       'product_uom_qty': base_so_line.product_uom_qty or False, #-product_uom_qty or False,
                       'product_uom': base_so_line.product_uom and base_so_line.product_uom.id or False,
                       'price_unit': base_so_line.price_unit or False,
                       'price_subtotal': base_so_line.price_subtotal or False,
                       'freight': base_so_line.freight or False,
                       'state': 'draft',
                       'type': 'make_to_stock',
                       #'name_consignee_id' : blanket_line.name_consignee_id.id,
                       'name_consignee_id' : base_so_line.name_consignee_id and base_so_line.name_consignee_id.id or False,#TPT Consignee Part blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False
                       'location':base_so_line.location,
                }
            #
            inv_obj = self.pool.get('account.invoice')
            inv_obj_ids = inv_obj.search(cr, uid, [('sale_id','=',sale_order.id)])
            if inv_obj_ids:
                inv_obj_id = inv_obj.browse(cr,uid,inv_obj_ids[0])
            #
                vals = {
                        'order_line':  [(0,0,rs_order)],
                        'order_policy': 'picking',
                        'partner_id':sale_order.partner_id.id or False,
                        'return_invoice_id':inv_obj_id.id or False,
                        'return_do_id': inv_obj_id.delivery_order_id.id or False,
                        
                        'invoice_address':sale_order.invoice_address or False,
                        'street2':sale_order.street2 or False,
                        'street3':sale_order.street3 or False,
                        'city':sale_order.city or False,
                        'country_id':sale_order.country_id and sale_order.country_id.id or False,
                        'state_id':sale_order.state_id and sale_order.state_id.id or False,
                        'zip':sale_order.zip or False,
                        
                        'po_date':sale_order.po_date or False,
                        'order_type':sale_order.order_type or False,
                        'po_number':sale_order.po_number or False,
                        'payment_term_id':sale_order.payment_term_id and sale_order.payment_term_id.id or False,
                        'currency_id':sale_order.currency_id and sale_order.currency_id.id or False,
                        'tpt_currency_id':sale_order.tpt_currency_id and sale_order.tpt_currency_id.id or False,
                        'quotaion_no':sale_order.quotaion_no or '',
                        'incoterms_id':sale_order.incoterms_id and sale_order.incoterms_id.id or False,
                        'distribution_channel':sale_order.distribution_channel and sale_order.distribution_channel.id or False,
                        'excise_duty_id':sale_order.excise_duty_id and sale_order.excise_duty_id.id or False,
                        'sale_tax_id':sale_order.sale_tax_id and sale_order.sale_tax_id.id or False, 
                        
                            }
        return {'value': vals}   
    ###
    def onchange_blanketorderline_id(self, cr, uid, ids, blanket_line_id=False, context=None):
        vals = {}
        for id in ids:
            sql = '''
                delete from sale_order_line where order_id = %s
            '''%(id)
            cr.execute(sql)
        if blanket_line_id:
            blanket_line = self.pool.get('tpt.blank.order.line').browse(cr, uid, blanket_line_id)
            sql = '''
                select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line where order_id in (select id from sale_order where blanket_line_id=%s and state!='cancel')
            '''%(blanket_line.id)
            cr.execute(sql)
            product_uom_qty = cr.dictfetchone()['product_uom_qty']
            rs_order = {
                  'product_id': blanket_line.product_id and blanket_line.product_id.id or False,
                  'name': blanket_line.description or False,
                  'product_type': blanket_line.product_type or False,
                  'application_id': blanket_line.application_id and blanket_line.application_id.id or False,
                  'product_uom_qty': blanket_line.product_uom_qty-product_uom_qty or False,
                  'product_uom': blanket_line.uom_po_id and blanket_line.uom_po_id.id or False,
                  'price_unit': blanket_line.price_unit or False,
                  'price_subtotal': blanket_line.sub_total or False,
                  'freight': blanket_line.freight or False,
                  'state': 'draft',
                  'type': 'make_to_stock',
                  #'name_consignee_id' : blanket_line.name_consignee_id.id,
                  'name_consignee_id' : blanket_line.tpt_name_consignee_id and blanket_line.tpt_name_consignee_id.tpt_consignee_id and blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False,#TPT Consignee Part blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False
                  'location':blanket_line.location,
                            }
            vals = {
                    'order_line': [(0,0,rs_order)],
                    'order_policy': 'picking',
                    'expected_date': blanket_line.expected_date,
                        }
        return {'value': vals}   
#     def onchange_partner_id(self, cr, uid, ids, partner_id=False, blanket_id=False, context=None):
#         vals = {}
#         consignee_lines = []
# #         for blanket in self.browse(cr, uid, ids):
# #             sql = '''
# #                 delete from order_line where blanket_order_id = %s
# #             '''%(blanket.id)
# #             cr.execute(sql)
#         if partner_id and not blanket_id:
#             part = self.pool.get('res.partner').browse(cr, uid, partner_id)
#             vals = {'invoice_address':part.street,
#                     'street2':part.street2,
#                     'city':part.city,
#                     'country_id':part.country_id.id,
#                     'state_id':part.state_id.id,
#                     'zip':part.zip,
#                     'payment_term_id':part.property_payment_term.id,
#                     'incoterms_id':part.inco_terms_id and part.inco_terms_id.id or False,
#                     }
#         return {'value': vals}    
        
   
    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        for sale in self.browse(cr, uid, ids, context=context):
            for inv in sale.invoice_ids:
                if inv.state not in ('draft', 'cancel'):
                    raise osv.except_osv(
                        _('Cannot cancel this sales order!'),
                        _('First cancel all invoices attached to this sales order.'))
            for r in self.read(cr, uid, ids, ['invoice_ids']):
                for inv in r['invoice_ids']:
                    wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_cancel', cr)
            sale_order_line_obj.write(cr, uid, [l.id for l in  sale.order_line],
                    {'state': 'cancel'})
            sale_order_ids = self.pool.get('tpt.batch.request').search(cr,uid,[('sale_order_id', '=',sale.id ),('state','!=','cancel')])
            if sale_order_ids:
                raise osv.except_osv(_('Warning!'),_('Sale Order has already existed on Batch Request'))
        self.write(cr, uid, ids, {'state': 'cancel'})
        sql = '''
             update sale_order set document_status='cancelled' where id = %s
            '''%(sale.id)
        cr.execute(sql)
        #TPT-BM Enabled on 27/07/2016
        sql = '''
              update tpt_blanket_order set state='approve' where id = %s
               '''%(sale.blanket_id.id)
        cr.execute(sql)
        #TPT-END
        return True
    
    def create(self, cr, uid, vals, context=None):
        #if vals.get('name','/')=='/':
            #vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.sale.order.import') or '/'
        #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
        if 'document_type' in vals:
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            if vals.get('name','/')=='/':
                if vals['document_type']=='saleorder':
                    sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.sale.order.import') or '/'
                    vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                elif vals['document_type']=='return': #TPT-BM-ON 15/06/2016
                   sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.return.sale.order.import') or '/' 
                   vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                
                    
          #TPT END    
        ###TPT
        if 'blanket_id' in vals and vals['blanket_id']:
            blanket = self.pool.get('tpt.blanket.order').browse(cr, uid, vals['blanket_id'])
            addr = self.pool.get('res.partner').address_get(cr, uid, [blanket.customer_id.id], ['delivery', 'invoice', 'contact'])
            ###
            if 'blanket_line_id' in vals:
                blanket_line = self.pool.get('tpt.blank.order.line').browse(cr, uid, vals['blanket_line_id'])
                sql = '''
                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line where order_id in (select id from sale_order where blanket_line_id=%s and state!='cancel')
                '''%(vals['blanket_line_id'])
                cr.execute(sql)
                product_uom_qty = cr.dictfetchone()['product_uom_qty']
                rs_order = {
                      'product_id': blanket_line.product_id and blanket_line.product_id.id or False,
                      'name': blanket_line.description or False,
                      'product_type': blanket_line.product_type or False,
                      'application_id': blanket_line.application_id and blanket_line.application_id.id or False,
                      'product_uom_qty': blanket_line.product_uom_qty-product_uom_qty or False,
                      'product_uom': blanket_line.uom_po_id and blanket_line.uom_po_id.id or False,
                      'price_unit': blanket_line.price_unit or False,
                      'price_subtotal': blanket_line.sub_total or False,
                      'freight': blanket_line.freight or False,
                      'state': 'draft',
                      'type': 'make_to_stock',
                      #'name_consignee_id' : blanket_line.name_consignee_id.id,
                      'name_consignee_id' : blanket_line.tpt_name_consignee_id and blanket_line.tpt_name_consignee_id.tpt_consignee_id and blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False,#TPT Consignee Part blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False
                      'location':blanket_line.location,
                                }
            ###
            vals.update({
                        'partner_id':blanket.customer_id and blanket.customer_id.id or False,
                    'invoice_address':blanket.invoice_address or False,
                    'street2':blanket.street2 or False,
                    'street3':blanket.street3 or False,
                    'city':blanket.city or False,
                    'country_id':blanket.country_id and blanket.country_id.id or False,
                    'state_id':blanket.state_id and blanket.state_id.id or False,
                    'zip':blanket.zip or False,
                    'po_date':blanket.po_date or False,
                    'order_type':blanket.order_type or False,
                    'po_number':blanket.po_number or False,
                    'payment_term_id':blanket.payment_term_id and blanket.payment_term_id.id or False,
                    'currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'tpt_currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'quotaion_no':blanket.quotaion_no or False,
                    'incoterms_id':blanket.incoterm_id and blanket.incoterm_id.id or False,
                    'distribution_channel':blanket.channel and blanket.channel.id or False,
                    'excise_duty_id':blanket.excise_duty_id and blanket.excise_duty_id.id or False,
                    'sale_tax_id':blanket.sale_tax_id and blanket.sale_tax_id.id or False, 
                    'reason':blanket.reason or False,
                    'amount_untaxed': blanket.amount_untaxed or False,
                    'order_line':[],
                    #'blanket_line_id': False,
                    'order_policy': 'picking',
                    'partner_invoice_id': addr['invoice'],
                    'order_line': [(0,0,rs_order)],
                         })
        ###TPT
        #TPT-BM-14/06/2016
        if 'return_so_id' in vals and vals['return_so_id']:
            base_so = self.pool.get('sale.order').browse(cr, uid, vals['return_so_id'])
            for base_so_line in base_so.order_line:
                rs_order = {
                       'product_id': base_so_line.product_id and base_so_line.product_id.id or False,
                       'name': base_so_line.name or False,
                       'product_type': base_so_line.product_type or False,
                       'application_id': base_so_line.application_id and base_so_line.application_id.id or False,
                       'product_uom_qty': base_so_line.product_uom_qty or False, #-product_uom_qty or False,
                       'product_uom': base_so_line.product_uom and base_so_line.product_uom.id or False,
                       'price_unit': base_so_line.price_unit or False,
                       'price_subtotal': base_so_line.price_subtotal or False,
                       'freight': base_so_line.freight or False,
                       'state': 'draft',
                       'type': 'make_to_stock',
                       #'name_consignee_id' : blanket_line.name_consignee_id.id,
                       'name_consignee_id' : base_so_line.name_consignee_id and base_so_line.name_consignee_id.id or False,#TPT Consignee Part blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False
                       'location':base_so_line.location,
                }
            #
            inv_obj = self.pool.get('account.invoice')
            inv_obj_ids = inv_obj.search(cr, uid, [('sale_id','=',base_so.id)])
            inv_obj_id = inv_obj.browse(cr,uid,inv_obj_ids[0])
            #
            vals.update( {
                    'order_line':  [(0,0,rs_order)],
                    'order_policy': 'picking',
                    'partner_id':base_so.partner_id.id or False,
                    'return_invoice_id':inv_obj_id.id or False,
                    'return_do_id': inv_obj_id.delivery_order_id.id or False,
                    
                    'invoice_address':base_so.invoice_address or False,
                    'street2':base_so.street2 or False,
                    'street3':base_so.street3 or False,
                    'city':base_so.city or False,
                    'country_id':base_so.country_id and base_so.country_id.id or False,
                    'state_id':base_so.state_id and base_so.state_id.id or False,
                    'zip':base_so.zip or False,
                    
                    'po_date':base_so.po_date or False,
                    'order_type':base_so.order_type or False,
                    'po_number':base_so.po_number or False,
                    'payment_term_id':base_so.payment_term_id and base_so.payment_term_id.id or False,
                    'currency_id':base_so.currency_id and base_so.currency_id.id or False,
                    'tpt_currency_id':base_so.tpt_currency_id and base_so.tpt_currency_id.id or False,
                    'quotaion_no':base_so.quotaion_no or '',
                    'incoterms_id':base_so.incoterms_id and base_so.incoterms_id.id or False,
                    'distribution_channel':base_so.distribution_channel and base_so.distribution_channel.id or False,
                    'excise_duty_id':base_so.excise_duty_id and base_so.excise_duty_id.id or False,
                    'sale_tax_id':base_so.sale_tax_id and base_so.sale_tax_id.id or False, 
                    
                        }
                        )
        #
        #print vals
        new_id = super(sale_order, self).create(cr, uid, vals, context)
        #TPT-BM-ON 29/06/2016 - The following snippet moved into Confirm Sale Button
        #=======================================================================
        # if 'blanket_id' in vals and vals['blanket_id']:
        #     sale = self.browse(cr, uid, new_id)
        #     
        #     sql = '''
        #         select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line where order_id in (select id from sale_order where blanket_line_id=%s and id!=%s and state!='cancel')
        #     '''%(sale.blanket_line_id.id,sale.id)
        #     cr.execute(sql)
        #     product_uom_qty = cr.dictfetchone()['product_uom_qty']
        #     
        #     for line in sale.order_line:
        #         if round(line.product_uom_qty,3) > round(sale.blanket_line_id.product_uom_qty-product_uom_qty,3): #TPT-By BalamuruganPurushothaman - ON 23/11/2015
        #             raise osv.except_osv(_('Warning!'),_('Quantity must be less than blanket order line quantity!'))
        #     
        #     sql = '''
        #         select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
        #             from sale_order_line where order_id in (select id from sale_order where blanket_id=%s and state!='cancel')
        #     '''%(sale.blanket_id.id)
        #     cr.execute(sql)
        #     product_uom_qty_sale = cr.dictfetchone()['product_uom_qty']
        #     sql = '''
        #         select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
        #             from tpt_blank_order_line where blanket_order_id = %s
        #     '''%(sale.blanket_id.id)
        #     cr.execute(sql)
        #     product_uom_qty_bk = cr.dictfetchone()['product_uom_qty']
        #     if product_uom_qty_bk==product_uom_qty_sale:
        #         sql = '''
        #             update tpt_blanket_order set state = 'done' where id=%s 
        #         '''%(sale.blanket_id.id)
        #         cr.execute(sql)
        #     if sale.blanket_id.state=='done' and product_uom_qty_sale<product_uom_qty_bk:
        #         sql = '''
        #             update tpt_blanket_order set state = 'approve' where id=%s 
        #         '''%(sale.blanket_id.id)
        #         cr.execute(sql)
        #=======================================================================
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        ###TPT
        if 'blanket_id' in vals and vals['blanket_id']:
            blanket = self.pool.get('tpt.blanket.order').browse(cr, uid, vals['blanket_id'])
            addr = self.pool.get('res.partner').address_get(cr, uid, [blanket.customer_id.id], ['delivery', 'invoice', 'contact'])
            #
            if 'blanket_line_id' in vals:
                blanket_line = self.pool.get('tpt.blank.order.line').browse(cr, uid, vals['blanket_line_id'])
                sql = '''
                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line where order_id in (select id from sale_order where blanket_line_id=%s and state!='cancel')
                '''%(vals['blanket_line_id'])
                cr.execute(sql)
                product_uom_qty = cr.dictfetchone()['product_uom_qty']
                rs_order = {
                      'product_id': blanket_line.product_id and blanket_line.product_id.id or False,
                      'name': blanket_line.description or False,
                      'product_type': blanket_line.product_type or False,
                      'application_id': blanket_line.application_id and blanket_line.application_id.id or False,
                      'product_uom_qty': blanket_line.product_uom_qty-product_uom_qty or False,
                      'product_uom': blanket_line.uom_po_id and blanket_line.uom_po_id.id or False,
                      'price_unit': blanket_line.price_unit or False,
                      'price_subtotal': blanket_line.sub_total or False,
                      'freight': blanket_line.freight or False,
                      'state': 'draft',
                      'type': 'make_to_stock',
                      #'name_consignee_id' : blanket_line.name_consignee_id.id,
                      'name_consignee_id' : blanket_line.tpt_name_consignee_id and blanket_line.tpt_name_consignee_id.tpt_consignee_id and blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False,#TPT Consignee Part blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False
                      'location':blanket_line.location,
                                }
            ###    
            vals.update({
                        'partner_id':blanket.customer_id and blanket.customer_id.id or False,
                    'invoice_address':blanket.invoice_address or False,
                    'street2':blanket.street2 or False,
                    'street3':blanket.street3 or False,
                    'city':blanket.city or False,
                    'country_id':blanket.country_id and blanket.country_id.id or False,
                    'state_id':blanket.state_id and blanket.state_id.id or False,
                    'zip':blanket.zip or False,
                    'po_date':blanket.po_date or False,
                    'order_type':blanket.order_type or False,
                    'po_number':blanket.po_number or False,
                    'payment_term_id':blanket.payment_term_id and blanket.payment_term_id.id or False,
                    'currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'tpt_currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'quotaion_no':blanket.quotaion_no or False,
                    'incoterms_id':blanket.incoterm_id and blanket.incoterm_id.id or False,
                    'distribution_channel':blanket.channel and blanket.channel.id or False,
                    'excise_duty_id':blanket.excise_duty_id and blanket.excise_duty_id.id or False,
                    'sale_tax_id':blanket.sale_tax_id and blanket.sale_tax_id.id or False, 
                    'reason':blanket.reason or False,
                    'amount_untaxed': blanket.amount_untaxed or False,
                    'order_line':[],
                    #'blanket_line_id': False,
                    'order_policy': 'picking',
                    'partner_invoice_id': addr['invoice'],
                    'order_line': [(0,0,rs_order)],
                         })
        ###TPT
        #
        if 'return_so_id' in vals and vals['return_so_id']:
            base_so = self.pool.get('sale.order').browse(cr, uid, vals['return_so_id'])
            for base_so_line in base_so.order_line:
                rs_order = {
                       'product_id': base_so_line.product_id and base_so_line.product_id.id or False,
                       'name': base_so_line.name or False,
                       'product_type': base_so_line.product_type or False,
                       'application_id': base_so_line.application_id and base_so_line.application_id.id or False,
                       'product_uom_qty': base_so_line.product_uom_qty or False, #-product_uom_qty or False,
                       'product_uom': base_so_line.product_uom and base_so_line.product_uom.id or False,
                       'price_unit': base_so_line.price_unit or False,
                       'price_subtotal': base_so_line.price_subtotal or False,
                       'freight': base_so_line.freight or False,
                       'state': 'draft',
                       'type': 'make_to_stock',
                       #'name_consignee_id' : blanket_line.name_consignee_id.id,
                       'name_consignee_id' : base_so_line.name_consignee_id and base_so_line.name_consignee_id.id or False,#TPT Consignee Part blanket_line.tpt_name_consignee_id.tpt_consignee_id.id or False
                       'location':base_so_line.location,
                }
            #
            inv_obj = self.pool.get('account.invoice')
            inv_obj_ids = inv_obj.search(cr, uid, [('sale_id','=',base_so.id)])
            inv_obj_id = inv_obj.browse(cr,uid,inv_obj_ids[0])
            #
            vals.update( {
                    'order_line':  [(0,0,rs_order)],
                    'order_policy': 'picking',
                    'partner_id':base_so.partner_id.id or False,
                    'return_invoice_id':inv_obj_id.id or False,
                    'return_do_id': inv_obj_id.delivery_order_id.id or False,
                    
                    'invoice_address':base_so.invoice_address or False,
                    'street2':base_so.street2 or False,
                    'street3':base_so.street3 or False,
                    'city':base_so.city or False,
                    'country_id':base_so.country_id and base_so.country_id.id or False,
                    'state_id':base_so.state_id and base_so.state_id.id or False,
                    'zip':base_so.zip or False,
                    
                    'po_date':base_so.po_date or False,
                    'order_type':base_so.order_type or False,
                    'po_number':base_so.po_number or False,
                    'payment_term_id':base_so.payment_term_id and base_so.payment_term_id.id or False,
                    'currency_id':base_so.currency_id and base_so.currency_id.id or False,
                    'tpt_currency_id':base_so.tpt_currency_id and base_so.tpt_currency_id.id or False,
                    'quotaion_no':base_so.quotaion_no or '',
                    'incoterms_id':base_so.incoterms_id and base_so.incoterms_id.id or False,
                    'distribution_channel':base_so.distribution_channel and base_so.distribution_channel.id or False,
                    'excise_duty_id':base_so.excise_duty_id and base_so.excise_duty_id.id or False,
                    'sale_tax_id':base_so.sale_tax_id and base_so.sale_tax_id.id or False, 
                    
                        }
                        )
        #
        new_write = super(sale_order, self).write(cr, uid,ids, vals, context)
        #TPT-BM-ON 29/06/2016 - The following snippet moved into Confirm Sale Button
        #=======================================================================
        # if 'blanket_id' in vals and vals['blanket_id']:
        #     for sale in self.browse(cr, uid, ids):
        #         if 'shipped' in vals:
        #             if (vals['shipped'] == True):
        #                 sql = '''
        #                      update sale_order set document_status='close' where id = %s
        #                 '''%(sale.id)
        #                 cr.execute(sql)
        #         sql = '''
        #             select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line
        #                 where order_id in (select id from sale_order where blanket_line_id=%s and id!=%s and state!='cancel')
        #         '''%(sale.blanket_line_id.id,sale.id)
        #         cr.execute(sql)
        #         product_uom_qty = cr.dictfetchone()['product_uom_qty']
        #         for line in sale.order_line:
        #             if round(line.product_uom_qty,3) > round(sale.blanket_line_id.product_uom_qty-product_uom_qty, 3): #TPT-BM-19/04/2016
        #                 raise osv.except_osv(_('Warning!'),_('Quantity must be less than blanket order line quantity!'))
        #         
        #         sql = '''
        #             select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
        #                 from sale_order_line where order_id in (select id from sale_order where blanket_id=%s and state!='cancel')
        #         '''%(sale.blanket_id.id)
        #         cr.execute(sql)
        #         product_uom_qty_sale = cr.dictfetchone()['product_uom_qty']
        #         sql = '''
        #             select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
        #                 from tpt_blank_order_line where blanket_order_id = %s
        #         '''%(sale.blanket_id.id)
        #         cr.execute(sql)
        #         product_uom_qty_bk = cr.dictfetchone()['product_uom_qty']
        #         if product_uom_qty_bk==product_uom_qty_sale:
        #             sql = '''
        #                 update tpt_blanket_order set state = 'done' where id=%s 
        #             '''%(sale.blanket_id.id)
        #             cr.execute(sql)
        #         if sale.blanket_id.state=='done' and product_uom_qty_sale<product_uom_qty_bk:
        #             sql = '''
        #                 update tpt_blanket_order set state = 'approve' where id=%s 
        #             '''%(sale.blanket_id.id)
        #             cr.execute(sql)
        #=======================================================================
        return new_write

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
                sql_so = '''
                    select id from sale_order where blanket_id = %s and state!='cancel'
                '''%(blanket_id)
                cr.execute(sql_so)
                kq = cr.fetchall()
                so_ids = []
                if kq:
                    for i in kq:
                        so_ids.append(i[0])
                    so_ids = str(so_ids).replace("[","(")
                    so_ids = so_ids.replace("]",")")
                    sql_product = '''
                        select sol.product_id, sum(sol.product_uom_qty) as qty
                        from sale_order_line sol
                        inner join sale_order so on so.id = sol.order_id
                        where sol.order_id in %s and sol.product_id = %s
                        group by sol.product_id
                    '''%(so_ids,blanket_line.product_id.id)
                    cr.execute(sql_product)
                    kq = cr.fetchall()
                    for data in kq:
                        if blanket_line.product_uom_qty > data[1]:
                            rs_order = {
                                  'product_id': blanket_line.product_id and blanket_line.product_id.id or False,
                                  'name': blanket_line.description or False,
                                  'product_type': blanket_line.product_type or False,
                                  'application_id': blanket_line.application_id and blanket_line.application_id.id or False,
                                  'product_uom_qty': blanket_line.product_uom_qty - data[1] or False,
                                  'product_uom': blanket_line.uom_po_id and blanket_line.uom_po_id.id or False,
                                  'price_unit': blanket_line.price_unit or False,
                                  'price_subtotal': blanket_line.sub_total or False,
                                  'freight': blanket_line.freight or False,
                                  'state': 'draft',
                                  'type': 'make_to_stock',
                                  }
                            blanket_lines.append((0,0,rs_order))
                else:
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
                                  'type': 'make_to_stock',
                                  }
                    blanket_lines.append((0,0,rs_order))
              
            addr = self.pool.get('res.partner').address_get(cr, uid, [blanket.customer_id.id], ['delivery', 'invoice', 'contact'])
            
            vals = {'partner_id':blanket.customer_id and blanket.customer_id.id or False,
                    'invoice_address':blanket.invoice_address or False,
                    'street2':blanket.street2 or False,
                    'street3':blanket.street3 or False,
                    'city':blanket.city or False,
                    'country_id':blanket.country_id and blanket.country_id.id or False,
                    'state_id':blanket.state_id and blanket.state_id.id or False,
                    'zip':blanket.zip or False,
                    'po_date':blanket.po_date or False,
                    'order_type':blanket.order_type or False,
                    'po_number':blanket.po_number or False,
                    'payment_term_id':blanket.payment_term_id and blanket.payment_term_id.id or False,
                    'currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'tpt_currency_id':blanket.currency_id and blanket.currency_id.id or False,
                    'quotaion_no':blanket.quotaion_no or False,
                    'incoterms_id':blanket.incoterm_id and blanket.incoterm_id.id or False,
                    'distribution_channel':blanket.channel and blanket.channel.id or False,
                    'excise_duty_id':blanket.excise_duty_id and blanket.excise_duty_id.id or False,
                    'sale_tax_id':blanket.sale_tax_id and blanket.sale_tax_id.id or False, 
                    'reason':blanket.reason or False,
                    'amount_untaxed': blanket.amount_untaxed or False,
                    'order_line':[],
                    'blanket_line_id': False,
                    'order_policy': 'picking',
                    'partner_invoice_id': addr['invoice'],
#                     'document_status':'close',
#                     'sale_consignee_line':consignee_lines or False,
                        }
        return {'value': vals}    
    
#     def onchange_blanket_id(self, cr, uid, ids,blanket_id=False, context=None):
#         vals = {}
#         blanket_lines = []
#         consignee_lines = []
#         if blanket_id:
#             blanket = self.pool.get('tpt.blanket.order').browse(cr, uid, blanket_id)
#             for line in self.browse(cr, uid, ids):
#                 sql = '''
#                     delete from sale_order_line where order_id = %s
#                 '''%(line.id)
#                 cr.execute(sql)
#             for blanket_line in blanket.blank_order_line:
#                 rs_order = {
#                       'product_id': blanket_line.product_id and blanket_line.product_id.id or False,
#                       'name': blanket_line.description or False,
#                       'product_type': blanket_line.product_type or False,
#                       'application_id': blanket_line.application_id and blanket_line.application_id.id or False,
#                       'product_uom_qty': blanket_line.product_uom_qty or False,
#                       'product_uom': blanket_line.uom_po_id and blanket_line.uom_po_id.id or False,
#                       'price_unit': blanket_line.price_unit or False,
#                       'price_subtotal': blanket_line.sub_total or False,
#                       'freight': blanket_line.freight or False,
#                       'state': 'draft',
#                       'type': 'make_to_stock',
#                       }
#                 blanket_lines.append((0,0,rs_order))
#               
# #             for consignee_line in blanket.blank_consignee_line:
# #                 rs_consignee = {
# #                       'name_consignee_id': consignee_line.name_consignee_id or False,
# #                       'location': consignee_line.location or False,
# #                       'product_id': consignee_line.product_id and consignee_line.product_id.id or False,
# #                       'product_uom_qty': consignee_line.product_uom_qty or False,
# #                       'uom_po_id': consignee_line.uom_po_id and consignee_line.uom_po_id.id or False,
# #                                 }
# #                 consignee_lines.append((0,0,rs_consignee))
#             
#             addr = self.pool.get('res.partner').address_get(cr, uid, [blanket.customer_id.id], ['delivery', 'invoice', 'contact'])
#             
#             vals = {'partner_id':blanket.customer_id and blanket.customer_id.id or False,
#                     'invoice_address':blanket.invoice_address or False,
#                     'street2':blanket.street2 or False,
#                     'city':blanket.city or False,
#                     'country_id':blanket.country_id and blanket.country_id.id or False,
#                     'state_id':blanket.state_id and blanket.state_id.id or False,
#                     'zip':blanket.zip or False,
#                     'po_date':blanket.po_date or False,
#                     'order_type':blanket.order_type or False,
#                     'po_number':blanket.po_number or False,
#                     'payment_term_id':blanket.payment_term_id and blanket.payment_term_id.id or False,
#                     'currency_id':blanket.currency_id and blanket.currency_id.id or False,
#                     'quotaion_no':blanket.quotaion_no or False,
#                     'incoterms_id':blanket.incoterm_id and blanket.incoterm_id.id or False,
#                     'distribution_channel':blanket.channel and blanket.channel.id or False,
#                     'excise_duty_id':blanket.excise_duty_id and blanket.excise_duty_id.id or False,
#                     'sale_tax_id':blanket.sale_tax_id and blanket.sale_tax_id.id or False, 
#                     'reason':blanket.reason or False,
#                     'amount_untaxed': blanket.amount_untaxed or False,
#                     'order_line':blanket_lines or False,
#                     'order_policy': 'picking',
#                     'partner_invoice_id': addr['invoice'],
# #                     'sale_consignee_line':consignee_lines or False,
#                         }
#         return {'value': vals}    
 
    def action_button_confirm_approve(self, cr, uid, ids, context=None):
        sale = self.browse(cr, uid, ids[0])
        if (sale.payment_term_id.name == 'Immediate Payment' or sale.payment_term_id.name == 'Immediate') and sale.shipped == True and sale.invoiced == True:
            sql = '''
                update sale_order set document_status='completed',flag_t='t' where id=%s
            '''%(sale.id)
            cr.execute(sql)
        sql = '''
            update sale_order set flag_t='t' where id=%s
        '''%(sale.id)
        cr.execute(sql)
        return True
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        
        sale = self.browse(cr, uid, ids[0])
#         for line in sale.order_line:
#             if (line.product_id.track_production==True and line.product_id.track_incoming==True and line.product_id.track_outgoing==True):
#                 sql = '''
#                         select product_id, sum(product_uom_qty) as product_qty from sale_order_line where order_id = %s group by product_id
#                         '''%(sale.id)
#                 cr.execute(sql)
#                 for order_line in cr.dictfetchall():
#                     sql = '''
#                     SELECT sum(onhand_qty) onhand_qty
#                     From
#                     (SELECT
#                            
#                         case when loc1.usage != 'internal' and loc2.usage = 'internal'
#                         then stm.primary_qty
#                         else
#                         case when loc1.usage = 'internal' and loc2.usage != 'internal'
#                         then -1*stm.primary_qty 
#                         else 0.0 end
#                         end onhand_qty
#                                 
#                     FROM stock_move stm 
#                         join stock_location loc1 on stm.location_id=loc1.id
#                         join stock_location loc2 on stm.location_dest_id=loc2.id
#                     WHERE stm.state= 'done' and product_id=%s)foo
#                     '''%(order_line['product_id'])
#                     cr.execute(sql)
#                     onhand_qty = cr.dictfetchone()['onhand_qty']
#                     if (order_line['product_qty'] > onhand_qty):
#                         raise osv.except_osv(_('Warning!'),_('You are confirm %s but only %s available for this product in stock.' %(order_line['product_qty'], onhand_qty)))
        
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
#         if sale.payment_term_id:
#             sql = '''
#                 update sale_order set document_status='waiting' where id=%s
#             '''%(sale.id)
#             cr.execute(sql)
        if ids:
            if (sale.payment_term_id.name == 'Immediate Payment' or sale.payment_term_id.name == 'Immediate'):
                sql = '''
                    update sale_order set document_status='waiting' where id=%s
                '''%(sale.id)
                cr.execute(sql)
            else:
                sql = '''
                    update sale_order set document_status='completed',flag_p='t' where id=%s
                '''%(sale.id)
                cr.execute(sql)
            picking_out_obj = self.pool.get('stock.picking.out')
            stock_move_obj = self.pool.get('stock.move')
            doc_status = 'draft'  
            picking_out_ids = picking_out_obj.search(cr,uid,[('sale_id','=',ids[0])],context=context)
            if picking_out_ids:
                sql = '''
                    select name_consignee_id from sale_order_line where order_id = %s group by name_consignee_id
                '''%(ids[0])
                cr.execute(sql)
                consignee_ids = [row[0] for row in cr.fetchall()]
                picking_id = picking_out_ids[0]
                limit = sale.partner_id and sale.partner_id.credit_limit_used or False
                amount = sale.amount_total or False
                if (limit > 0 or limit == 0) and amount and amount >= limit:
                    doc_status = 'waiting'
                first_picking_id = False
                #
                if sale.document_type=='return':
                    document_type = 'return_do'
                else:
                    document_type = 'do'
                #
                for i,consignee_id in enumerate(consignee_ids):
                    if i==0:
                        first_picking_id = picking_id
                        picking = picking_out_obj.browse(cr, uid, picking_id)
                        picking_out_obj.write(cr, uid, [picking_id], {'cons_loca': consignee_id,'backorder_id':picking_id,'origin':picking.origin,
                                                                      'sale_id':ids[0],'partner_id':sale.partner_id.id,'doc_status':'draft',
                                                                      'order_type':sale.order_type, 'document_type':document_type})
                    else:
                        sql = '''
                            select id from sale_order_line where name_consignee_id = %s and order_id = %s
                        '''%(consignee_id,sale.id)
                        cr.execute(sql)
                        order_line_ids = [row[0] for row in cr.fetchall()]
                        default = {'backorder_id':picking_id,'move_lines':[],'cons_loca': consignee_id}
                        picking = picking_out_obj.browse(cr, uid, picking_id)
                        new_picking_id = picking_out_obj.copy(cr, uid, picking_id, default)
                        picking_out_obj.write(cr, uid, [new_picking_id], {'cons_loca': consignee_id,'backorder_id':picking_id,'origin':picking.origin,'sale_id':ids[0],'partner_id':sale.partner_id.id,'doc_status':'draft'})
                        stock_move_ids = stock_move_obj.search(cr, uid, [('sale_line_id','in',order_line_ids)])
                        stock_move = stock_move_obj.browse(cr,uid,stock_move_ids[0])
                        stock_move_obj.write(cr, uid, stock_move_ids, {'picking_id':new_picking_id,'product_type':stock_move.sale_line_id.product_type,
                                                                       'application_id':stock_move.sale_line_id.application_id and stock_move.sale_line_id.application_id.id or False})
        #                 wf_service.trg_validate(uid, 'stock.picking', new_picking_id, 'button_confirm', cr)
                        picking_out_obj.draft_force_assign(cr, uid, [new_picking_id])
                        picking_id = new_picking_id
                if first_picking_id:
                    for line in picking_out_obj.browse(cr, uid, first_picking_id).move_lines:
                        ###TPT START - By BalamuruganPurushothaman ON 4/4/2015 - TO SET SYSTEM BATCH NO BY DEFAULT
                        ### FOR FSH PRODUCT
                        if line.sale_line_id.application_id.id:
                            sql = '''
                            select id from stock_production_lot where product_id = (select id from product_product where default_code = 'M0501010002')
                            and application_id = %s
                        '''%(line.sale_line_id.application_id.id)
                            cr.execute(sql)
                            fsh_prod_lot = cr.fetchone()
                        else:
                            fsh_prod_lot = False    
                        if fsh_prod_lot:
                            stock_move_obj.write(cr, uid, [line.id], {'product_type':line.sale_line_id.product_type,
                                                                      'application_id':line.sale_line_id.application_id and line.sale_line_id.application_id.id or False, 
                                                                      'prodlot_id':fsh_prod_lot})
                        else:
                            stock_move_obj.write(cr, uid, [line.id], {'product_type':line.sale_line_id.product_type,'application_id':line.sale_line_id.application_id and line.sale_line_id.application_id.id or False})
                        ###TPT END
                        #stock_move_obj.write(cr, uid, [line.id], {'product_type':line.sale_line_id.product_type,'application_id':line.sale_line_id.application_id and line.sale_line_id.application_id.id or False})
            #
            #TPT START-BM-ON 29/06/2016 - the following snippet moved from create,write method - BO tured to Done state even its partial qty ordered
            sale = self.browse(cr, uid, ids[0])
            if sale.blanket_id:
                sql = '''
                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line where order_id in (select id from sale_order where blanket_line_id=%s and id!=%s and state!='cancel')
                '''%(sale.blanket_line_id.id,sale.id)
                cr.execute(sql)
                product_uom_qty = cr.dictfetchone()['product_uom_qty']
                
                for line in sale.order_line:
                    if round(line.product_uom_qty,3) > round(sale.blanket_line_id.product_uom_qty-product_uom_qty,3): #TPT-By BalamuruganPurushothaman - ON 23/11/2015
                        raise osv.except_osv(_('Warning!'),_('Quantity must be less than blanket order line quantity!'))
                
                sql = '''
                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
                        from sale_order_line where order_id in (select id from sale_order where blanket_id=%s and state!='cancel')
                '''%(sale.blanket_id.id)
                cr.execute(sql)
                product_uom_qty_sale = cr.dictfetchone()['product_uom_qty']
                sql = '''
                    select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
                        from tpt_blank_order_line where blanket_order_id = %s
                '''%(sale.blanket_id.id)
                cr.execute(sql)
                product_uom_qty_bk = cr.dictfetchone()['product_uom_qty']
                if product_uom_qty_bk==product_uom_qty_sale:
                    sql = '''
                        update tpt_blanket_order set state = 'done' where id=%s 
                    '''%(sale.blanket_id.id)
                    cr.execute(sql)
                if sale.blanket_id.state=='done' and product_uom_qty_sale<product_uom_qty_bk:
                    sql = '''
                        update tpt_blanket_order set state = 'approve' where id=%s 
                    '''%(sale.blanket_id.id)
                    cr.execute(sql)
            #TPT START
        return True
    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0
        }

    def _prepare_order_picking(self,cr,uid,order,context=None):
        #pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            #sequence = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out') or '/'
            #pick_name =  sequence and sequence+'/'+fiscalyear['code'] or '/'
            #TPT END
            product_obj = self.pool.get('product.product')
            #TPT-BM-16/06/2016 - FOR SALES RETURN PROCESS
            if order.document_type=='saleorder':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out') or '/'
            elif order.document_type=='return':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.return.do.import') or '/'
            pick_name = sequence and sequence+'/'+fiscalyear['code'] or '/'    
            #           
            for line in order.order_line:
                if line.product_id and not line.product_id.warehouse_id.id:
#                 product = product_obj.search(cr,uid,line.product_id.id)
#                 if product and not product.warehouse_id.id:
                    raise osv.except_osv(_('Warning!'),_('Sale Warehouse is not null, please configure it in Product Master!'))
                else:
                    warehouse = line.product_id.warehouse_id.id
            return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
            'warehouse':warehouse,
            #'document_type':'do',#TPT-BM-16/06/2016
        }
        
    def onchange_date_order(self, cr, uid, ids, date_order=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if date_order and date_order > current:
            vals = {'date_order':current}
            warning = {
                'title': _('Warning!'),
                'message': _('SO Date: Not allow future date!')
            }
        return {'value':vals,'warning':warning}
    
sale_order()

class tpt_log(osv.osv):
    _name='tpt.log'
    _columns = {
        'name': fields.text('Remarks',required=True),
        'current_date': fields.date('Current Date',required=True),
        'sale_order_id': fields.many2one('sale.order', 'Sale Order',ondelete='cascade'),
        'delivery_order_id': fields.many2one('stock.picking', 'Delivery Order',ondelete='cascade'),
    }
    _defaults = {
        'current_date': time.strftime('%Y-%m-%d'),
    }
tpt_log()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
#     def create(self, cr, uid, vals, context=None):
#         if 'product_id' in vals:
#             product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
#             vals.update({'product_uom':product.uom_id.id})
#         if 'product_uom_qty' in vals:
#             order = self.pool.get('sale.order').browse(cr,uid,vals['order_id'])
#             blanket = self.pool.get('tpt.blanket.order').browse(cr,uid,order.blanket_id.id )
#             for line in blanket.blank_order_line:
#                 if (vals['product_id'] == line.product_id.id):
#                     if (vals['product_uom_qty'] > line.product_uom_qty):
#                         raise osv.except_osv(_('Warning!'),_('Quatity must be less than quatity of Blanket Order'))
#         return super(sale_order_line, self).create(cr, uid, vals, context)
#     
#     def write(self, cr, uid, ids, vals, context=None):
#         if 'product_id' in vals:
#             product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
#             vals.update({'product_uom':product.uom_id.id})
# #         if 'product_uom_qty' in vals:
# #             order = self.pool.get('sale.order').browse(cr,uid,vals['order_id'])
# #             blanket = self.pool.get('tpt.blanket.order').browse(cr,uid,order.blanket_id.id )
# #             for line in blanket.blank_order_line:
# #                 if (vals['product_id'] == line.product_id.id):
# #                     if (vals['product_uom_qty'] > line.product_uom_qty):
# #                         raise osv.except_osv(_('Warning!'),_('sdfghj'))
#         return super(sale_order_line, self).write(cr, uid,ids, vals, context)
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        subtotal = 0.0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.product_uom_qty * line.price_unit)# + (line.product_uom_qty * line.price_unit) * (line.order_id.excise_duty_id.amount/100)
            res[line.id] = subtotal
        return res
    def basic_amt_calc(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'amount_basic' : 0.0,
               }
            subtotal = (line.product_uom_qty * line.price_unit) 
            res[line.id]['amount_basic'] = subtotal
        return res
    def ed_amt_calc(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'amount_ed' : 0.0,
               }
            subtotal = (line.product_uom_qty * line.price_unit) * (line.order_id.excise_duty_id and line.order_id.excise_duty_id.amount/100 or 0)
            res[line.id]['amount_ed'] = subtotal
        return res
    
    def _get_tax_gst_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            tax_cgst_amount = 0.0
            tax_sgst_amount = 0.0
            tax_igst_amount = 0.0
            res[line.id] = {
                'tax_cgst_amount': 0.0,
                'tax_sgst_amount': 0.0,
                'tax_igst_amount': 0.0,
            }
            
            if line.order_id.sale_tax_id:
                amount_untaxed = line.price_subtotal
                amount_untaxed += (line.product_uom_qty * line.freight) #TPT-BM-01/07/2017 - GST
                if line.order_id.sale_tax_id.child_depend:
                    for tax_child in line.order_id.sale_tax_id.child_ids:
                        if 'CGST' in tax_child.description.upper():
                            tax_cgst_amount += (amount_untaxed)*(tax_child.amount or 0) / 100
                        if 'SGST' in tax_child.description.upper():
                            tax_sgst_amount += (amount_untaxed)*(tax_child.amount or 0) / 100
                else:
                    if 'IGST' in line.order_id.sale_tax_id.description.upper():
                        tax_igst_amount += (amount_untaxed)*(line.order_id.sale_tax_id.amount or 0) / 100
                
            res[line.id]['tax_cgst_amount'] = tax_cgst_amount
            res[line.id]['tax_sgst_amount'] = tax_sgst_amount
            res[line.id]['tax_igst_amount'] = tax_igst_amount
        return res
      
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required = True),
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Prod Type'),
        'application_id': fields.many2one('crm.application', 'Application', ondelete='restrict'),
        'freight': fields.float('Frt/Qty'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'name_consignee_id': fields.many2one('res.partner', 'Consignee', required = False), #TPT - modified required true to false
        'location': fields.char('Location', size = 1024),   
        'product_uom_qty': fields.float('Qty', digits=(16,3), required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'amount_basic': fields.function(basic_amt_calc, store = True, multi='deltas3' ,string='Basic'),
        'amount_ed': fields.function(ed_amt_calc, store = True, multi='deltas4' ,string='ED'),
        'tax_cgst_amount': fields.function(_get_tax_gst_amount, store = True, multi='gst_tax' ,digits=(16,3),string='CGSTAmt'),
        'tax_sgst_amount': fields.function(_get_tax_gst_amount, store = True, multi='gst_tax' ,digits=(16,3),string='SGSTAmt'),
        'tax_igst_amount': fields.function(_get_tax_gst_amount, store = True, multi='gst_tax' ,digits=(16,3),string='IGSTAmt'),
    }
    _defaults ={
      'product_uom_qty':0,
     }
    def create(self, cr, uid, vals, context=None):
        if ('freight'and 'product_uom_qty') in vals:
            if (vals['freight'] < 0 and vals['product_uom_qty'] < 0 ):
                raise osv.except_osv(_('Warning!'),_('Freight and Quantity is not negative value'))
        if 'freight' in vals:
            if (vals['freight'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not negative value'))
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
        if 'price_unit' in vals:
            if (vals['price_unit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Unit Price is not allowed as negative values'))
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(sale_order_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            
            if (line.freight < 0 and line.product_uom_qty < 0 ):
                    raise osv.except_osv(_('Warning!'),_('Freight and Quantity is not negative value'))
            if (line.freight < 0):
                    raise osv.except_osv(_('Warning!'),_('Freight is not negative value'))
            if (line.product_uom_qty < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
            if (line.price_unit < 0):
                raise osv.except_osv(_('Warning!'),_('Unit Price is not allowed as negative values'))
        return new_write

    def onchange_consignee_id(self, cr, uid, ids, name_consignee_id = False, context=None):
        vals = {}
        if name_consignee_id :
            line = self.pool.get('res.partner').browse(cr, uid, name_consignee_id)
            vals = {
                    'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or ''),    
                    }
        return {'value': vals}
#     def onchange_tpt_product_id(self, cr, uid, ids,product_id=False, order_id=False, context=None):
#         product_ids = []
#         if product_id:
#             sale = self.pool.get('sale.order').browse(cr, uid, order_id)
#             blanket = self.pool.get('tpt.blanket.order').browse(cr, uid, sale.blanket_id.id)
#             for line in blanket.blank_order_line:
#                 product_ids.append(line.product_id.id)
#         return {'value': {'designation_id': False }, 'domain':{'product_id':[('id','in',product_ids)]}}

#     def onchange_product_id(self, cr, uid, ids, product_id = False, context=None):
#         vals = {}
#         if product_id :
#             product = self.pool.get('product.product').browse(cr, uid, product_id)
#             vals = {
#                     'product_uom':product.uom_id.id,
#                     'price_unit':product.list_price,
#                     'name': product.name
#                     }
#         return {'value': vals}
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
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
            result['name'] = self.pool.get('product.product').browse(cr, uid, product_obj.id).name
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
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

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                result.update({'price_unit': price})
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}
sale_order_line()


class tpt_blanket_order(osv.osv):
    _name = "tpt.blanket.order"
    _order = "bo_date desc"
    
    def amount_all_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        blanket_line_obj = self.pool.get('tpt.blank.order.line')
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_total_cgst_tax': 0.0,
                'amount_total_sgst_tax': 0.0,
                'amount_total_igst_tax': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val1 = 0.0
            amount_total_cgst_tax = 0.0
            amount_total_sgst_tax = 0.0
            amount_total_igst_tax = 0.0
            total_tax = 0.0
            val2 = 0.0
            val3 = 0.0
            freight = 0.0
            for orderline in line.blank_order_line:
                freight = freight + (orderline.product_uom_qty * orderline.freight)
                val1 += orderline.sub_total
#                 total_tax += orderline.tax_cgst_amount+orderline.tax_sgst_amount+orderline.tax_igst_amount
#                 amount_total_cgst_tax += orderline.tax_cgst_amount
#                 amount_total_sgst_tax += orderline.tax_sgst_amount
#                 amount_total_igst_tax += orderline.tax_igst_amount
                line_value = blanket_line_obj._get_tax_gst_amount(cr, uid, [orderline.id], None, None, None)[orderline.id]
                
                total_tax = line_value['tax_cgst_amount']+line_value['tax_sgst_amount']+line_value['tax_igst_amount']#(basic + p_f + ed)*(quotation.tax_id and quotation.tax_id.amount or 0) / 100
                amount_total_cgst_tax += line_value['tax_cgst_amount']
                amount_total_sgst_tax += line_value['tax_sgst_amount']
                amount_total_igst_tax += line_value['tax_igst_amount']
            val1 += freight
            amount_total_cgst_tax = round(amount_total_cgst_tax)
            amount_total_sgst_tax = round(amount_total_sgst_tax)
            amount_total_igst_tax = round(amount_total_igst_tax)
            total_tax = amount_total_cgst_tax+amount_total_sgst_tax+amount_total_igst_tax
            res[line.id]['amount_untaxed'] = round(val1) #TPT-BM-Freight is addeded - This is Taxable Amount
            val2 = val1 * line.sale_tax_id.amount / 100
            res[line.id]['amount_total_cgst_tax'] = amount_total_cgst_tax
            res[line.id]['amount_total_sgst_tax'] = amount_total_sgst_tax
            res[line.id]['amount_total_igst_tax'] = amount_total_igst_tax
            res[line.id]['amount_tax'] = total_tax
            #val3 = val1 + total_tax + freight
            val3 = val1 + total_tax # GST-Freight Removed
            res[line.id]['amount_total'] = round(val3)
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.blank.order.line').browse(cr, uid, ids, context=context):
            result[line.blanket_order_id.id] = True
        return result.keys()

    _columns = {
        'name': fields.char('Blanket Order', size = 1024, readonly=True),
        'customer_id': fields.many2one('res.partner', 'Customer', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'invoice_address': fields.char('Invoice Address', size = 1024, readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'street2': fields.char('', size = 1024, readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'street3': fields.char('', size = 1024, readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),#TPT
        'city': fields.char('', size = 1024, readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'country_id': fields.many2one('res.country', '', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'state_id': fields.many2one('res.country.state', '', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'zip': fields.char('', size = 1024, readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'currency_id': fields.many2one('res.currency', 'Currency', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'bo_date': fields.date('BO Date', required = True,   states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'po_date': fields.date('PO Date', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'po_number': fields.char('PO Number', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'quotaion_no': fields.char('Quotation No', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'excise_duty_id': fields.many2one('account.tax', 'Excise Duty', domain="[('type_tax_use','=','excise_duty')]", required = False, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'sale_tax_id': fields.many2one('account.tax', 'Sale Tax', domain="[('type_tax_use','=','sale')]", required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}), 
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterms', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'reason': fields.text('Reason', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'exp_delivery_date': fields.date('Expected delivery Date', required = False, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'dispatch_date':fields.date('Scheduled Dispatch Date'),
        'channel': fields.many2one('crm.case.channel', 'Distribution Channel', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'order_type':fields.selection([('domestic','Domestic/Indirect Export'),('export','Export')],'Order Type' ,required=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'document_type':fields.selection([('blankedorder','Blanket Order')], 'Document Type',required=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'blank_order_line': fields.one2many('tpt.blank.order.line', 'blanket_order_id', 'Sale Order', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'amount_untaxed': fields.function(amount_all_blanket_orderline, multi='sums',string='Untaxed Amount',
                                         store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line','sale_tax_id','excise_duty_id'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10),}, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'amount_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Taxes',
                                      store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line', 'sale_tax_id','excise_duty_id'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'amount_total_cgst_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Total CGSTAmt',
                                      store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line', 'sale_tax_id','excise_duty_id'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'amount_total_sgst_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Total SGSTAmt',
                                      store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line', 'sale_tax_id','excise_duty_id'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'amount_total_igst_tax': fields.function(amount_all_blanket_orderline, multi='sums',string='Total IGSTAmt',
                                      store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line', 'sale_tax_id','excise_duty_id'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        'amount_total': fields.function(amount_all_blanket_orderline, multi='sums',string='Total',
                                        store={
                'tpt.blanket.order': (lambda self, cr, uid, ids, c={}: ids, ['blank_order_line', 'sale_tax_id','excise_duty_id'], 10),
                'tpt.blank.order.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty', 'freight'], 10), },
             states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}),
        
        'blank_consignee_line': fields.one2many('tpt.consignee', 'blanket_consignee_id', 'Consignee', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'approve':[('readonly', True)]}), 
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Done'), ('approve', 'Confirmed'), ('close', 'Closed')],'Status', readonly=True),
        'flag2':fields.boolean(''),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),       
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True),
        'amendment_reason': fields.char('Reason for Amendment', size = 1024, ),
        'amendment_flag':fields.boolean('Is Amended'),
    }
    
    
    _defaults = {
        'state': 'draft',
        'name': '/',
        'document_type': 'blankedorder',
        #'bo_date': time.strftime('%Y-%m-%d'),
        #'bo_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        #'bo_date':date.today().strftime('%Y-%m-%d'),
        'flag2':False,
        'amendment_flag':False,
    }
    #TPT START - BY BM -ON 30/05/2016 - FOR MOBILE APP
    def update_bo(self, cr, uid, ids, name, context=None):
        res_return = "False"   
        res = self.search(cr, SUPERUSER_ID, [('name','=',name[:18])])
        if res:
            sql = '''
            update tpt_blanket_order set state='approve' where id=%s
            '''%res[0]
            cr.execute(sql)
            res_return = "True"   
        return res_return
    
    def cancel_bo(self, cr, uid, ids, name, context=None):
        res_return = "False"   
        res = self.search(cr, SUPERUSER_ID, [('name','=',name[:18])])
        if res:
            sql = '''
            update tpt_blanket_order set state='cancel' where id=%s
            '''%res[0]
            cr.execute(sql)
            res_return = "True"   
        return res_return  
    #TPT END
    def onchange_exp_delivery_date(self, cr, uid, ids, exp_delivery_date=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if exp_delivery_date:
            if exp_delivery_date < current:
                vals = {'exp_delivery_date':current}
                warning = {
                    'title': _('Warning!'),
                    'message': _('Expected delivery Date: Allow future date, not allow back date')
                }
        return {'value':vals,'warning':warning}
    def onchange_sche_dispatch_date(self, cr, uid, ids, sche_dispatch_date=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if sche_dispatch_date:
            if sche_dispatch_date < current:
                vals = {'dispatch_date':current}
                warning = {
                    'title': _('Warning!'),
                    'message': _('Scheduled Dispatch Date: Allow future date, not allow back date')
                }
        return {'value':vals,'warning':warning}
    
    #TPT- By BalamuruganPurushothaman on 01_03-2015 - To have Total(update) option
    def button_dummy(self, cr, uid, ids, context=None):
        return True
            
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if not line.blank_order_line:
                raise osv.except_osv(_('Warning!'),_('You can not approve a blanket order without blanket order lines!'))
            self.write(cr, uid, ids,{'state':'approve'})
        return True   
    
    ###TPT- By BalamuruganPurushothaman on 16/10/2015 - TO CLOSE THE BO, IF CUSTOMER STOP RECEIVEING SERVICE EVENTHOUGHT IT HAS PARTIAL QTY SHIPPED
    def bt_cancel(self, cr, uid, ids, context=None):
        
                    
                    
        for line in self.browse(cr, uid, ids):
            sale_order_ids = self.pool.get('sale.order').search(cr,uid,[('blanket_id', '=',line.id ),('state', '!=','cancel')])
            
            #===================================================================
            # sql = ''' select count(id) from sale_order where blanket_id=%s
            # '''%line.id
            # cr.execute(sql)
            # count = cr.fetchone()
            # count = count[0]
            # if count>1:
            #===================================================================
            if len(sale_order_ids)==1:
                raise osv.except_osv(_('Warning!'),_('Blanket Order has one Sale Order'))
            elif len(sale_order_ids)>1:
                raise osv.except_osv(_('Warning!'),_('Blanket Order has already existed in more than one Sale Order'))
            
            cl_sale_order_ids = self.pool.get('sale.order').search(cr,uid,[('blanket_id', '=',line.id ), ('state', '=','cancel')])
            so_qty = 0
            bo_line_ids = self.pool.get('tpt.blank.order.line').search(cr,uid,[ ('blanket_order_id', '=',line.id)]) 
            bo_line = self.pool.get('tpt.blank.order.line').browse(cr,uid,bo_line_ids[0])
            if cl_sale_order_ids:
                for so_id in cl_sale_order_ids:
                    so_line_ids = self.pool.get('sale.order.line').search(cr,uid,[ ('order_id', '=',so_id)])               
                    so_line = self.pool.get('sale.order.line').browse(cr,uid,so_line_ids[0])
                    so_qty += so_line.product_uom_qty                
                if so_qty!=bo_line.product_uom_qty:
                    raise osv.except_osv(_('Warning!'),_('Blanket Order has already existed on Sale Order'))
            confirm_sale_order_ids = self.pool.get('sale.order').search(cr,uid,[('blanket_id', '=',line.id ), ('state', 'in',('draft', 'progress','done'))])
            if confirm_sale_order_ids:
                for so_id in cl_sale_order_ids:
                    so_line_ids = self.pool.get('sale.order.line').search(cr,uid,[ ('order_id', '=',confirm_sale_order_ids[0])])               
                    so_line = self.pool.get('sale.order.line').browse(cr,uid,so_line_ids[0])
                    so_qty += so_line.product_uom_qty                
                if so_qty!=bo_line.product_uom_qty:
                    raise osv.except_osv(_('Warning!'),_('Blanket Order has already existed on Sale Order'))
            #TPT-BM-31/10/2015 - TO GIVE ALERT WHEN BO IS CANCELLED 
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_sale', 'alert_bo_cancel_form_view')
            return {
                    'name': 'Alert for BO Cancel',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.bo.cancel',
                    'domain': [],
                    'context': {'default_message':'Do You Really want to Cancel this BO?','bo_id':line.id},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
            }
            self.write(cr, uid, ids,{'state':'cancel'})
        return True  
    ###
    def bt_close(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            sale_order_ids = self.pool.get('sale.order').search(cr,uid,[('blanket_id', '=',line.id )])
            if len(sale_order_ids)==0:
                raise osv.except_osv(_('Warning!'),_('Sales Order not raised for this BO'))
            self.write(cr, uid, ids,{'state':'close'})
        return True   
    ###TPT-
    def bt_draft(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):           
            self.write(cr, uid, ids,{'state':'draft', 'amendment_flag':True})
        return True 
    #TPT
    def create(self, cr, uid, vals, context=None):
        #if vals.get('name','/')=='/':
            #vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.blanked.order.import') or '/'
        #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
        #if 'document_type' in vals:
        sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        if vals.get('name','/')=='/':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.blanked.order.import') or '/'
            vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        #TPT END    
        if 'customer_id' in vals:
            customer = self.pool.get('res.partner').browse(cr, uid, vals['customer_id'])
            ###TPT
            if customer.arulmani_type:
                if customer.arulmani_type=='domestic':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','10')])                  
                if customer.arulmani_type=='export':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','20')])
                if customer.arulmani_type=='indirect_export':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','30')]) 
            ###TPT
            vals.update({
                        'invoice_address': customer.street or False,
                        'street2': customer.street2 or False,
                        'street3': customer.street3 or False,
                        'city': customer.city or False,
                        'country_id': customer.country_id and customer.country_id.id or False,
                        'state_id': customer.state_id and customer.state_id.id or False,
                        'zip': customer.zip or False,
                        ###TPT
                        'channel':channel_id[0] or False,
                        'incoterm_id':customer.inco_terms_id and customer.inco_terms_id.id or False,
                        'currency_id':customer.currency_id and customer.currency_id.id or False,
                        ###TPT
                         })
        new_id = super(tpt_blanket_order, self).create(cr, uid, vals, context=context)
        blanket = self.browse(cr, uid, new_id)
#         if not blanket.blank_order_line:
#             raise osv.except_osv(_('Warning!'),_('You can not create a blanket order without blanket order lines!'))
        con_ids = []
        for con_line in blanket.customer_id.consignee_line:
            con_ids.append(con_line.id)
        #TPT - Commented By BalamuruganPurushothaman on 01/03/2015 - To make Consignee mandatory      
        #for blanket_line in blanket.blank_order_line:
        #    if blanket_line.name_consignee_id.id not in con_ids:
        #       raise osv.except_osv(_('Warning!'),_('This consignee "%s" does not belong to the selected customer "%s"!')%(blanket_line.name_consignee_id.name,blanket.customer_id.name))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'customer_id' in vals:
            customer = self.pool.get('res.partner').browse(cr, uid, vals['customer_id'])
            ###TPT
            if customer.arulmani_type:
                if customer.arulmani_type=='domestic':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','10')])                  
                if customer.arulmani_type=='export':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','20')])
                if customer.arulmani_type=='indirect_export':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','30')])  
            ###TPT
            vals.update({
                        'invoice_address': customer.street or False,
                        'street2': customer.street2 or False,
                        'street3': customer.street3 or False,
                        'city': customer.city or False,
                        'country_id': customer.country_id and customer.country_id.id or False,
                        'state_id': customer.state_id and customer.state_id.id or False,
                        'zip': customer.zip or False,
                        ###TPT
                        'channel':channel_id[0] or False,
                        'incoterm_id':customer.inco_terms_id and customer.inco_terms_id.id or False,
                        'currency_id':customer.currency_id and customer.currency_id.id or False,
                        ###TPT
                         })
        new_write = super(tpt_blanket_order, self).write(cr, uid, ids, vals, context=context) 
        for blanket in self.browse(cr, uid, ids):
            con_ids = []
            if not blanket.blank_order_line:
                raise osv.except_osv(_('Warning!'),_('You can not write a blanket order without blanket order lines!'))
            for con_line in blanket.customer_id.consignee_line:
                con_ids.append(con_line.id)
            #TPT - Commented By BalamuruganPurushothaman on 01/03/2015 - To manke COnsignee mandatory on     
            #for blanket_line in blanket.blank_order_line:
            #    if blanket_line.name_consignee_id.id not in con_ids:
            #        raise osv.except_osv(_('Warning!'),_('This consignee "%s" does not belong to the selected customer "%s"!')%(blanket_line.name_consignee_id.name,blanket.customer_id.name))
        return new_write
    
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
                        'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or ''),
                        
                      }
                consignee_lines.append((0,0,rs))
            if customer.arulmani_type:
                if customer.arulmani_type=='domestic':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','10')])                  
                if customer.arulmani_type=='export':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','20')])
                if customer.arulmani_type=='indirect_export':
                    channel_obj = self.pool.get('crm.case.channel') 
                    channel_id = channel_obj.search(cr, uid, [('code','=','30')])   
            vals = {'invoice_address': customer.street or False,
                    'street2': customer.street2 or False,
                    'street3': customer.street3 or False,
                    'city': customer.city or False,
                    'country_id': customer.country_id and customer.country_id.id or False,
                    'state_id': customer.state_id and customer.state_id.id or False,
                    'zip': customer.zip or False,
                    'payment_term_id':customer.property_payment_term and customer.property_payment_term.id or False,
                    'blank_consignee_line': consignee_lines or False,
                    'incoterm_id':customer.inco_terms_id and customer.inco_terms_id.id or False,
                    'currency_id':customer.currency_id and customer.currency_id.id or False,
                    'bo_date': fields.date.context_today(self,cr,uid,context=context)
                    }
        return {'value': vals}
    
    def onchange_bo_date(self, cr, uid, ids, bo_date=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if bo_date and bo_date > current:
            vals = {'bo_date':current}
            warning = {
                'title': _('Warning!'),
                'message': _('BO Date: Not allow future date!')
            }
        return {'value':vals,'warning':warning}
    
    def onchange_po_date(self, cr, uid, ids, po_date=False, context=None):
        vals = {}
        current = time.strftime('%Y-%m-%d')
        warning = {}
        if po_date and po_date > current:
            vals = {'po_date':current}
            warning = {
                'title': _('Warning!'),
                'message': _('PO Date: Not allow future date!')
            }
        return {'value':vals,'warning':warning}
    
tpt_blanket_order()

class tpt_blank_order_line(osv.osv):
    _name = "tpt.blank.order.line"
    
    def subtotal_blanket_orderline(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'sub_total' : 0.0,
               }
            subtotal = (line.product_uom_qty * line.price_unit)# + (line.product_uom_qty * line.price_unit) * (line.blanket_order_id.excise_duty_id.amount/100)
            res[line.id]['sub_total'] = subtotal
        return res
    def basic_amt_calc(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'amount_basic' : 0.0,
               }
            basic = (line.product_uom_qty * line.price_unit) 
            res[line.id]['amount_basic'] = basic
        return res
    def ed_amt_calc(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'amount_ed' : 0.0,
               }
            ed = (line.product_uom_qty * line.price_unit) * (line.blanket_order_id.excise_duty_id and line.blanket_order_id.excise_duty_id.amount/100 or 0)
            res[line.id]['amount_ed'] = ed
        return res
    
    def _get_tax_gst_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            tax_cgst_amount = 0.0
            tax_sgst_amount = 0.0
            tax_igst_amount = 0.0
            res[line.id] = {
                'tax_cgst_amount': 0.0,
                'tax_sgst_amount': 0.0,
                'tax_igst_amount': 0.0,
            }
            
            if line.blanket_order_id.sale_tax_id:
                amount_untaxed = line.sub_total
                amount_untaxed += (line.product_uom_qty * line.freight) #TPT-BM-01/07/2017 - For GST Freight Should be Included
                if line.blanket_order_id.sale_tax_id.child_depend:
                    for tax_child in line.blanket_order_id.sale_tax_id.child_ids:
                        if 'CGST' in tax_child.description.upper():
                            tax_cgst_amount += (amount_untaxed)*(tax_child.amount or 0) / 100
                        if 'SGST' in tax_child.description.upper():
                            tax_sgst_amount += (amount_untaxed)*(tax_child.amount or 0) / 100
                else:
                    if 'IGST' in line.blanket_order_id.sale_tax_id.description.upper():
                        tax_igst_amount += (amount_untaxed)*(line.blanket_order_id.sale_tax_id.amount or 0) / 100
                
            res[line.id]['tax_cgst_amount'] = tax_cgst_amount
            res[line.id]['tax_sgst_amount'] = tax_sgst_amount
            res[line.id]['tax_igst_amount'] = tax_igst_amount
        return res
    
    _columns = {
        'blanket_order_id': fields.many2one('tpt.blanket.order', 'Blank Order', ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Product', required = True),
        'description': fields.text('Description', required = True),
        'product_type': fields.selection([('rutile', 'Rutile'),('anatase', 'Anatase')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application', ondelete='restrict'),
        'product_uom_qty': fields.float('Quantity', digits=(16,3)),
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = False, ondelete='restrict'),
        'price_unit': fields.float('Unit Price'),
        'sub_total': fields.function(subtotal_blanket_orderline, multi='deltas' ,string='SubTotal'),
        'freight': fields.float('Frt/Qty'),
        #Effective Consignee
        'tpt_name_consignee_id': fields.many2one('tpt.cus.consignee', 'Consignee' ),
        
        'name_consignee_id': fields.many2one('res.partner', 'Consignee', required = False),
        'location': fields.char('Location', size = 1024,readonly = True),
        'expected_date':fields.date('Expected delivery Date'),
        
        'amount_basic': fields.function(basic_amt_calc, multi='deltas1' ,string='Basic'),
        'amount_ed': fields.function(ed_amt_calc, multi='deltas2' ,string='ED'),
                
        'is_fsh_tio2': fields.boolean('Is TiO2 or FSH'),
        'dispatch_date':fields.date('Scheduled Dispatch Date'),
        'tax_cgst_amount': fields.function(_get_tax_gst_amount, store = True, multi='gst_tax' ,digits=(16,3),string='CGSTAmt'),
        'tax_sgst_amount': fields.function(_get_tax_gst_amount, store = True, multi='gst_tax' ,digits=(16,3),string='SGSTAmt'),
        'tax_igst_amount': fields.function(_get_tax_gst_amount, store = True, multi='gst_tax' ,digits=(16,3),string='IGSTAmt'),
                }
    _defaults = {
        'expected_date': time.strftime('%Y-%m-%d'),
        'product_uom_qty': 1,
    }
    def _check_product(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            product_ids = self.search(cr, uid, [('id','!=',product.id),('product_id','!=',product.product_id.id),('blanket_order_id', '=',product.blanket_order_id.id)])
            if product_ids:
                raise osv.except_osv(_('Warning!'),_('Different Products are not allowed in same Blanket Order!'))           
                return False
            return True
        
    _constraints = [
        (_check_product, 'Identical Data', ['blanket_order_id', 'product_id']),
    ]       
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name_consignee_id','product_id','product_uom_qty'], context)
        for record in reads:
            name = ''
            if record['name_consignee_id']:
                name += record['name_consignee_id'][1]+'_'
            if record['product_id']:
                name += record['product_id'][1]+'_'
            name += str(record['product_uom_qty'])
            res.append((record['id'], name))
        return res
    
    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id,
                         'description':product.name,
                         'product_type':product.tpt_product_type,})
        if ('freight'and 'product_uom_qty') in vals:
            if (vals['freight'] < 0 and vals['product_uom_qty'] < 0 ):
                raise osv.except_osv(_('Warning!'),_('Freight and Quantity is not negative value'))
        if 'freight' in vals:
            if (vals['freight'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not negative value'))
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity field should not have negative value'))
        if 'price_unit' in vals:
            if (vals['price_unit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Unit Price is not allowed as negative values'))
        return super(tpt_blank_order_line, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id,
                         'description':product.name,
                         'product_type':product.tpt_product_type,})
        new_write = super(tpt_blank_order_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if (line.freight < 0 and line.product_uom_qty < 0 ):
                    raise osv.except_osv(_('Warning!'),_('Freight and Quantity is not negative value'))
            if (line.freight < 0):
                    raise osv.except_osv(_('Warning!'),_('Freight is not negative value'))
            if (line.product_uom_qty < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not negative value'))
            if (line.price_unit < 0):
                raise osv.except_osv(_('Warning!'),_('Unit Price is not allowed as negative values'))
        return new_write
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_blanket_line'):
            blanket_id = context.get('blanket_id')
            blanket_line_ids = []
            if blanket_id:
                blanketline_ids = self.pool.get('tpt.blank.order.line').search(cr, uid, [('blanket_order_id','=',blanket_id)])
                for blanketline in self.pool.get('tpt.blank.order.line').browse(cr, uid, blanketline_ids):
                    sql = '''
                        select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty from sale_order_line where order_id in (select id from sale_order where blanket_line_id=%s and state!='cancel')
                    '''%(blanketline.id)
                    cr.execute(sql)
                    product_uom_qty = cr.dictfetchone()['product_uom_qty']
                    if blanketline.product_uom_qty>product_uom_qty:
                        blanket_line_ids.append(blanketline.id)
                args += [('id','in',blanket_line_ids)]
        return super(tpt_blank_order_line, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        res = {'value':{
                    'product_type':False,# TPT - BalamuruganPurushothaman
                    'uom_po_id':False,
                    'price_unit':False,
                    'description': False,
                    }}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            res['value'].update({
                    'product_type':product.tpt_product_type,# TPT - BalamuruganPurushothaman
                    'uom_po_id':product.uom_id.id,
                    'price_unit':product.list_price,
                    'description': product.name,
                    })
            #TPT  START - By BalamuruganPurushothaman - 5/4/2015 TO MAKE APPLICATION FIELD 
            #AS MANDATORY WHEN TIO2 , FSH IS SELECTED                  
            if product.name == 'FERROUS SULPHATE' or product.default_code == 'FSH':                
                #res.update({'is_fsh': True}) 
                res['value'].update({
                     'is_fsh_tio2': True,                   
                    })
            if product.name == 'TITANIUM DIOXIDE-ANATASE' or product.default_code == 'TiO2':                               
                res['value'].update({
                    'is_fsh_tio2': True,                                
                    })
            if product.name != 'FERROUS SULPHATE' and product.name != 'TITANIUM DIOXIDE-ANATASE':                
                res['value'].update({
                    'is_fsh_tio2': False,                     
                    })
            #TPT END
        return res
    
    def onchange_consignee_id(self, cr, uid, ids, name_consignee_id = False, context=None):
        vals = {}
        if name_consignee_id :
            line = self.pool.get('res.partner').browse(cr, uid, name_consignee_id)
            vals = {
                    'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or ''),    
                    }
        return {'value': vals}
    
tpt_blank_order_line()




class tpt_consignee(osv.osv):
    _name = "tpt.consignee"
    
#     def quatity_consignee(self, cr, uid, ids, field_name, args, context=None):
#         res = {}
#         for line in self.browse(cr,uid,ids,context=context):
#             res[line.id] = {
#                 'total_qty' : 0.0,
#                 }
#             quatity = 0.0
#             for order_line in line.blanket_consignee_id.blank_order_line:
#                 if order_line.product_id.id == line.product_id.id:
#                     quatity = quatity + line.product_uom_qty
#                           
#             res[line.id]['total_qty'] = quatity
#         return res
    
    
    _columns = {
        'blanket_consignee_id': fields.many2one('tpt.blanket.order', 'Consignee'),
        'name_consignee_id': fields.many2one('res.partner', 'Consignee', required = True),
        'location': fields.char('Location', size = 1024),
        'product_id': fields.many2one('product.product', 'Product'),
#         'total_qty': fields.function(quatity_consignee, store = True, type = 'float',multi='deltas', string='Quatity'),
        'product_uom_qty': fields.float('Quatity'),
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
        'report_line': fields.one2many('tpt.test.report.line', 'report_id', 'Line'),
        'date_of_manufacture': fields.date('Date of Manufacture'),
        'date_of_expiry': fields.date('Date of Expiry'),
        'is_tio2': fields.boolean('Is TiO2'),
        'date': fields.date('Date'),
        'customer_id': fields.many2one('res.partner', 'Customer', required = True),
                }
    
    def onchange_product(self, cr, uid, ids,product_id=False, context=None):
        vals = {'report_line':[],'is_tio2':False}
        report_line = []
        if product_id:
            for id in ids:
                sql = '''
                    delete from tpt_test_report_line where report_id = %s
                '''%(id)
                cr.execute(sql)
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            if product.name == 'TITANIUM DIOXIDE-ANATASE' or product.default_code == 'TiO2': 
                for line in ['Texture','pH of Pigments Slurry','Bulk Density gm/ml (Tapped)','Residue on 45 micron IS sieve, % by mass','Iron, ppm by mass','Solubility, % by mass',
                             'Purity as TiO2 % by mass','LOI @ B00^C % by mass','Phosphate, % by mass','Volatile Matter, % by mass','FTIR Correlation Coefficient %','L*','a*','b*',
                             '457 Brightness',
                             ]:
                    rs = {
                          'name': line,
                          }
                    report_line.append((0,0,rs))
                vals.update({'is_tio2': True})
            if product.name == 'FERROUS SULPHATE' or product.default_code == 'FSH': 
                for line in ['Grade of the product','pH value with 5% of Slurry','Content of Moisture, % by mass','Content of Iron, % by mass',
                             'Purity as FSH, % by mass','Content of Ferric Iron, % by mass','Free Acid value, % by mass'
                             ]:
                    rs = {
                          'name': line,
                          }
                    report_line.append((0,0,rs))
                vals.update({'is_tio2': False})
            vals.update({
                    'report_line':report_line,
                    })
        return {'value': vals}
    
    def test_report_print(self, cr, uid, ids, context=None):
        test = self.browse(cr, uid, ids[0])
        if test.name.name == 'TITANIUM DIOXIDE-ANATASE' or test.name.default_code == 'TiO2':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'test_report_tio2',
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'test_report',
            }
    
tpt_test_report()

class tpt_test_report_line(osv.osv):
    _name = "tpt.test.report.line"
      
    _columns = {
        'report_id': fields.many2one('tpt.test.report', 'Test Report', ondelete='cascade'),
        'name':fields.char('Name', size = 1024,required=True),
        'value':fields.char('Value', size = 1024),
                }
tpt_test_report_line()

class tpt_batch_request(osv.osv):
    _name = "tpt.batch.request"
    _order = 'create_date desc'
    
    _columns = {
        'name': fields.char('Request No', size = 1024,readonly=True, required = True , states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'sale_order_id': fields.many2one('sale.order', 'Sales Order', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'customer_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'description': fields.text('Description', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'request_date': fields.date('Request Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'product_information_line': fields.one2many('tpt.product.information', 'product_information_id', 'Product Information', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancelled'),('done', 'Approved')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),       
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True),  
                }
    _defaults={
               'name':'/',
               'state': 'draft',
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'sale_order_id' in vals:
            sale = self.pool.get('sale.order').browse(cr, uid, vals['sale_order_id'])
            product_lines = []
            for line in sale.order_line:
                if line.product_id.track_production and line.product_id.track_incoming and line.product_id.track_outgoing:
                    rs = {
                            'product_id': line.product_id.id,
                            'product_type': line.product_type,
                            'application_id': line.application_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'uom_po_id': line.product_uom.id,
                          }
                    product_lines.append((0,0,rs))
            vals.update({'customer_id':sale.partner_id.id, 'product_information_line': product_lines})
        return super(tpt_batch_request, self).write(cr, uid,ids, vals, context)
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            batch_allotment_ids = self.pool.get('tpt.batch.allotment').search(cr,uid,[('batch_request_id','=',line.id),('state','!=','cancel')])
            if batch_allotment_ids:
                raise osv.except_osv(_('Warning!'),_('Batch Request has already existed on Batch Allotment'))
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def _check_sale_order_id(self, cr, uid, ids, context=None):
        for request in self.browse(cr, uid, ids, context=context):
            request_ids = self.search(cr, uid, [('id','!=',request.id),('sale_order_id','=',request.sale_order_id.id),('state', '!=', 'cancel')])
            if request_ids:
                raise osv.except_osv(_('Warning!'),_('Sale Order ID already exists!'))
                return False
            return True

    _constraints = [
        (_check_sale_order_id, 'Identical Data', ['sale_order_id']),
    ]
    
#     def onchange_sale_order_id(self, cr, uid, ids,sale_order_id=False, context=None):
#         vals = {}
#         product_lines = []
#         if sale_order_id :
#             sale = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
#             for line in sale.order_line:
#                 rs = {
#                         'product_id': line.product_id.id,
#                         'product_type': line.product_type,
#                         'application_id': line.application_id.id,
#                         'product_uom_qty': line.product_uom_qty,
#                         'uom_po_id': line.product_uom.id,
#                       }
#                 product_lines.append((0,0,rs))
#             vals = {
#                     'customer_id':sale.partner_id.id,
#                     'product_information_line': product_lines,
#                     }
#         return {'value': vals}
    
    def create(self, cr, uid, vals, context=None):
        #if vals.get('name','/')=='/':
            #vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.batch.req.import') or '/'
    #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)        
        if 'sale_order_id' in vals:
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            if vals.get('name','/')=='/':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.batch.req.import') or '/'
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
          #TPT END    
        #if 'sale_order_id' in vals:
            sale = self.pool.get('sale.order').browse(cr, uid, vals['sale_order_id'])
            product_lines = []
            for line in sale.order_line:
                if line.product_id.track_production and line.product_id.track_incoming and line.product_id.track_outgoing:
                    rs = {
                            'product_id': line.product_id.id,
                            'product_type': line.product_type,
                            'application_id': line.application_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'uom_po_id': line.product_uom.id,
                          }
                    product_lines.append((0,0,rs))
            vals.update({'customer_id':sale.partner_id.id, 'product_information_line': product_lines})
        return super(tpt_batch_request, self).create(cr, uid, vals, context=context)
    
    def onchange_sale_order_id(self, cr, uid, ids,sale_order_id=False, context=None):
        vals = {}
        product_information_line = []
        for request in self.browse(cr, uid, ids):
            sql = '''
                delete from tpt_product_information where product_information_id = %s
            '''%(request.id)
            cr.execute(sql)
        if sale_order_id:
            sale = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
            for line in sale.order_line:
                if line.product_id.track_production and line.product_id.track_incoming and line.product_id.track_outgoing:
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
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_default_batch_request_by_allot'):
            sql = '''
                select id from tpt_batch_request
                where state != 'cancel' and id not in (select batch_request_id from tpt_batch_allotment al,tpt_batch_request re where al.batch_request_id = re.id and al.state != 'cancel')
            '''
            cr.execute(sql)
            request_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',request_ids)]
        return super(tpt_batch_request, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
    
tpt_batch_request()

class tpt_product_information(osv.osv):
    _name = "tpt.product.information"
     
    _columns = {
        'product_information_id': fields.many2one('tpt.batch.request', 'Batch Request'),          
        'product_id': fields.many2one('product.product', 'Product',required = True),     
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),   
        'application_id': fields.many2one('crm.application', 'Application', ondelete='restrict'),    
        'product_uom_qty': fields.float('Quantity', digits=(16,3)),   
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
    _order = 'batch_request_id desc' 
     
    def init(self, cr):
        batch_line_obj = self.pool.get('tpt.batch.allotment.line')
        batch_line_ids = batch_line_obj.search(cr, 1, [])
        if batch_line_ids:
            for line in batch_line_obj.browse(cr,1,batch_line_ids):
                sale_id = line.batch_allotment_id and line.batch_allotment_id.sale_order_id and line.batch_allotment_id.sale_order_id.id or False
                lot_id = line.sys_batch.id or False
                if sale_id and lot_id:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end qty from stock_move where state = 'done' and prodlot_id = %s 
                            and sale_line_id in (select id from sale_order_line where order_id = %s)
                    '''%(lot_id,sale_id)
                    cr.execute(sql)
                    qty = cr.dictfetchone()['qty']
                    
                    sql ='''
                        update tpt_batch_allotment_line set used_qty = %s where id = %s
                    '''%(qty,line.id)
                    cr.execute(sql)
                    if line.used_qty and line.used_qty==line.product_uom_qty:
                        sql ='''
                            update tpt_batch_allotment_line set is_deliver = 't' where id = %s
                        '''%(line.id)
                        cr.execute(sql)
                    
    _columns = {
        'batch_request_id':fields.many2one('tpt.batch.request','Batch Request No.',required = True), 
        'name':fields.date('Date Requested',required = True), 
        'sale_order_id':fields.many2one('sale.order','Sale Order',required = True),   
        'customer_id':fields.many2one('res.partner', 'Customer', required = True), 
        'description':fields.text('Description'),
        'state': fields.selection([('to_approve', 'Draft'), ('refuse', 'Refused'),('confirm', 'Allotted'), ('cancel', 'Cancelled')],'Status'),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'batch_allotment_id', 'Product Information'), 
        'requested_qty': fields.float('Requested Quantity', digits=(16,3),readonly = True),   
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),       
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True),
                }
    _defaults = {
              'state': 'to_approve',
    }
    
    def unlink(self, cr, uid, ids, context=None):
        stat = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for t in stat:
            if t['state'] in ('cancel','to_approve'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Warning!'), _('This Batch Allotment can not be deleted!'))
        return super(tpt_batch_allotment, self).unlink(cr, uid, ids, context=context)
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(tpt_batch_allotment, self).create(cr, uid, vals, context)
        batch = self.browse(cr, uid, new_id)
        requested_qty = 0
        for line in batch.batch_allotment_line:
            allot_qty = 0
            requested_qty += line.product_uom_qty
            sql = '''
                    select id from tpt_batch_allotment_line where sys_batch = %s and is_deliver is not True 
                    and batch_allotment_id not in (select id from tpt_batch_allotment where state in ('cancel','refuse'))
            '''%(line.sys_batch.id)
            cr.execute(sql)
            for ba_line in cr.dictfetchall():
                line_id = self.pool.get('tpt.batch.allotment.line').browse(cr, uid, ba_line['id']) 
                qty = line_id.product_uom_qty or 0
                used =line_id.used_qty or 0
                allot_qty += qty - used
            lot_id = self.pool.get('stock.production.lot').browse(cr, uid, line.sys_batch.id) 
            ##TPT COMMENTED BY BalamuruganPurushothaman on 23/07/2015 - temporarily
            #if allot_qty > lot_id.stock_available:
                #raise osv.except_osv(_('Warning!'),_('Batch number %s: Allotted quantity should not be greater than Available Quantity!'%line.sys_batch.name))
        if requested_qty:
            sql = '''
                    update tpt_batch_allotment set requested_qty = %s where id = %s
                '''%(requested_qty,new_id)
            cr.execute(sql)
            
        sql = '''
                    select product_id, sum(product_uom_qty) as allot_product_qty from tpt_batch_allotment_line where batch_allotment_id = %s group by product_id
                '''%(batch.id)
        cr.execute(sql)
        
        for allot_line in cr.dictfetchall():
            sql = '''
                    select product_id, sum(product_uom_qty) as request_product_qty from tpt_product_information where product_information_id = %s group by product_id
                '''%(batch.batch_request_id.id)
            cr.execute(sql)
            for request_line in cr.dictfetchall():
                if (allot_line['product_id']==request_line['product_id']):
                    if (allot_line['allot_product_qty'] != request_line['request_product_qty']):
                        raise osv.except_osv(_('Warning!'),_('The product quantity in batch allotment must be as same as the product quantity in batch request!'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(tpt_batch_allotment, self).write(cr, uid, ids, vals, context)
        requested_qty = 0
        for batch in self.browse(cr, uid, ids):
            for line in batch.batch_allotment_line:
                allot_qty = 0
                requested_qty += line.product_uom_qty
                sql = '''
                    select id from tpt_batch_allotment_line where sys_batch = %s and is_deliver is not True
                    and batch_allotment_id not in (select id from tpt_batch_allotment where state in ('cancel','refuse'))
                '''%(line.sys_batch.id)
                cr.execute(sql)
                for ba_line in cr.dictfetchall():
                    line_id = self.pool.get('tpt.batch.allotment.line').browse(cr, uid, ba_line['id']) 
                    qty = line_id.product_uom_qty or 0
                    used =line_id.used_qty or 0
                    allot_qty += qty - used
                lot_id = self.pool.get('stock.production.lot').browse(cr, uid, line.sys_batch.id) 
                #TPT-BalamuruganPurushothaman on 23/07/2015
                #if allot_qty > lot_id.stock_available:
                    #raise osv.except_osv(_('Warning!'),_('Allotted quantity should not be greater than available stock Quantity in Batch no %s!'%line.sys_batch.name))
                    
            if requested_qty:
                sql = '''
                        update tpt_batch_allotment set requested_qty = %s where id = %s
                    '''%(requested_qty,batch.id)
                cr.execute(sql)
            sql = '''
                    select product_id, sum(product_uom_qty) as allot_product_qty from tpt_batch_allotment_line where batch_allotment_id = %s group by product_id
                '''%(batch.id)
            cr.execute(sql)
            for allot_line in cr.dictfetchall():
                sql = '''
                        select product_id, sum(product_uom_qty) as request_product_qty from tpt_product_information where product_information_id = %s group by product_id
                    '''%(batch.batch_request_id.id)
                cr.execute(sql)
                for request_line in cr.dictfetchall():
                    if (allot_line['product_id']==request_line['product_id']):
                        if (allot_line['allot_product_qty'] != request_line['request_product_qty']):
                            raise osv.except_osv(_('Warning!'),_('The product quantity in batch allotment must be as same as the product quantity in batch request!'))
                        
                
        return new_write
    def confirm(self, cr, uid, ids, context=None):
        new_write =  self.write(cr, uid, ids, {'state': 'confirm'})
        #TPT - By BalamuruganPurushothaman on 03/03/2015 - TO CHANGE 'SO' STATUS TO 'BATCH ALLOTTED' 
        sale_obj = self.pool.get('sale.order')
        batch_allot_obj = self.browse(cr,uid,ids[0])       
        sale_id = batch_allot_obj.sale_order_id.id
        sql = '''
                update sale_order set document_status='batch_allotted' where id=%s
            '''%(sale_id)
        cr.execute(sql)
            
        return new_write
#         sale_obj = self.pool.get('sale.order')
#         for batch_allotment in self.browse(cr,uid,ids,context=context):
#             
#             # cap nhat cho order line cua sale order giong nhu cua batch allotment
# #             picking_out_ids = self.pool.get('stock.picking').search(cr,uid,[('sale_id','=',batch_allotment.sale_order_id.id)],context=context)
# #             if not picking_out_ids:
#             wf_service = netsvc.LocalService('workflow')
#             wf_service.trg_validate(uid, 'sale.order', batch_allotment.sale_order_id.id, 'order_confirm', cr)
#         
#                 # redisplay the record as a sales order
#             view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
#             view_id = view_ref and view_ref[1] or False,
    
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
            
#             return {
#                 'type': 'ir.actions.act_window',
#                 'name': _('Sales Order'),
#                 'res_model': 'sale.order',
#                 'res_id': batch_allotment.sale_order_id.id,
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'view_id': view_id,
#                 'target': 'current',
#                 'nodestroy': True,
#             }
    def refuse(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'refuse'})
    def cancelled(self, cr, uid, ids, context=None):
        for batch in self.browse(cr, uid, ids):
            if batch.sale_order_id:
                sql='''
                    select id from stock_picking where sale_id = %s
                '''%(batch.sale_order_id.id)
                cr.execute(sql)
                do_ids = cr.fetchall()
                if len(do_ids)>1:
                    raise osv.except_osv(_('Warning!'),_('Delivery Order of this Batch Allotment is delivered. Can not cancel!'))
                elif len(do_ids)==1:
                    sql='''
                        select case when count(*)=1 then count(*) else 0 end num_re from stock_picking where id = %s and state='done'
                    '''%(do_ids[0])
                    cr.execute(sql)
                    num_re = cr.dictfetchone()['num_re']
                    if num_re==1:
                        raise osv.except_osv(_('Warning!'),_('Delivery Order of this Batch Allotment is delivered. Can not cancel!'))
                    else:
                        write_id = self.write(cr, uid, ids, {'state': 'cancel'})
                else:
                    write_id = self.write(cr, uid, ids, {'state': 'cancel'})
        return write_id
    def onchange_batch_request_id(self, cr, uid, ids,batch_request_id=False):
        res = {'value':{
                        'name':False,
                        'sale_order_id':False,
                        'customer_id':False,
                        'description':False,
                        'batch_allotment_line':[],
                        'requested_qty':False
                      }
               }
        requested_qty = 0
        if batch_request_id:
            batch = self.pool.get('tpt.batch.request').browse(cr, uid, batch_request_id)
            batch_allotment_line = []
            for line in batch.product_information_line:
                batch_allotment_line.append({
                          'product_id': line.product_id.id,
                          #'product_uom_qty':line.product_uom_qty,
                          'product_uom_qty':0.00,
                          'product_type':line.product_type,
                          'uom_po_id': line.uom_po_id.id,
                          'application_id':line.application_id.id,
                    })
                requested_qty += line.product_uom_qty
        res['value'].update({
                    'name':batch.request_date or False,
                    'sale_order_id':batch.sale_order_id and batch.sale_order_id.id or False,
                    'customer_id':batch.customer_id and batch.customer_id.id or False,
                    'description':batch.description or False,
                    'batch_allotment_line': batch_allotment_line,
                    'requested_qty': requested_qty,
        })
        return res
tpt_batch_allotment()

class tpt_form_403(osv.osv):
    _name = "tpt.form.403"
     
    _columns = {
        'from_place':fields.char('From Place', size = 256),
        'to_place':fields.char('To Place', size = 256),
        'from_district':fields.char('From District', size = 256),
        'to_district':fields.char('To District', size = 256),
        'name':fields.many2one('account.invoice','Invoice No'),
        'date':fields.related('name', 'date_invoice', type='date', string='Date',readonly=True),
        'consignor_name':fields.char('Name', size = 256),
        'consignor_street': fields.char('Street', size = 256),
        'consignor_street2': fields.char('', size = 256),
        'consignor_city': fields.char('', size = 256),
        'consignor_country_id': fields.many2one('res.country', ''),
        'consignor_state_id': fields.many2one('res.country.state', ''),
        'consignor_zip': fields.char('', size = 256),
        'consignor_tel':fields.char('Telephone', size = 15),
        'consignor_fax':fields.char('Fax', size = 32),
        'consignor_certi_no':fields.char('Reg. Certificate No', size = 256),
        'consignor_cst_no':fields.char('CST Reg No', size = 256),
        'consignor_date_1':fields.date('Date'),
        'consignor_date_2':fields.date('Date'),
        'transporter_name':fields.char('Name', size = 256),
        'transporter_street': fields.char('Street', size = 256),
        'transporter_street2': fields.char('', size = 256),
        'transporter_city': fields.char('', size = 256),
        'transporter_country_id': fields.many2one('res.country', ''),
        'transporter_state_id': fields.many2one('res.country.state', ''),
        'transporter_zip': fields.char('', size = 256),
        'transporter_owner':fields.char('Owner Partner Name', size = 256),
        'transporter_vehicle_no':fields.char('Vehicle No', size = 32),
        'driver_name':fields.char('Name', size = 256),
        'driver_street': fields.char('Street', size = 256),
        'driver_street2': fields.char('', size = 256),
        'driver_city': fields.char('', size = 256),
        'driver_country_id': fields.many2one('res.country', ''),
        'driver_state_id': fields.many2one('res.country.state', ''),
        'driver_zip': fields.char('', size = 256),
        'driver_licence':fields.char('Driving Licence Number', size = 256),
        'driver_issuing':fields.char('Licence Issuing State', size = 256),
        'good_name':fields.char('Name', size = 256),
        'good_street': fields.char('Street', size = 256),
        'good_street2': fields.char('', size = 256),
        'good_city': fields.char('', size = 256),
        'good_country_id': fields.many2one('res.country', ''),
        'good_state_id': fields.many2one('res.country.state', ''),
        'good_zip': fields.char('', size = 256),
        'good_designation':fields.char('Designation', size = 256),
        'entry_no':fields.char('Entry no', size = 64),
        'reason':fields.char('Reason for abnormal Stoppage', size = 256),
        'result':fields.char('Result if any', size = 256, required = True),
        'arrival':fields.datetime('Arrival Time', required = True),
        'departure':fields.datetime('Departure Time', required = True),
        'consignee_street': fields.char('Street', size = 256),
        'consignee_street2': fields.char('', size = 256),
        'consignee_city': fields.char('', size = 256),
        'consignee_country_id': fields.many2one('res.country', ''),
        'consignee_state_id': fields.many2one('res.country.state', ''),
        'consignee_zip': fields.char('', size = 256),
        'consignee_certi_no':fields.char('Reg. Certificate No', size = 256),
        'consignee_cst_no':fields.char('CST Reg No', size = 256),
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
        #TPT By BalamuruganPurushothaman To Load Consignee List
        'consignee_shift_party': fields.many2one('res.partner', 'Consignee'),
        
        'tpt_consignee_line': fields.one2many('tpt.cus.consignee', 'tpt_consignee_header_id', 'TPT Consignee'),
        'tpt_commission_line': fields.one2many('tpt.cus.ind.commission', 'tpt_commission_header_id', 'TPT Commission'),
                 }
    
    def onchange_consignee_shift_party(self, cr, uid, ids,customer_id=False, context=None):
        vals = {}
        consignee_lines = []
        if customer_id:           
            customer = self.pool.get('res.partner').browse(cr, uid, customer_id)
            for line in customer.consignee_line:
                rs = {
                        'name_consignee_id': line.id,
                        'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or ''),
                        
                      }
                consignee_lines.append((0,0,rs))
            
            vals = {'name': customer.name or False,
                    'street': customer.street or False,
                    'street2': customer.street2 or False,
                    'street3': customer.street3 or False,
                    'city': customer.city or False,
                    'country_id': customer.country_id and customer.country_id.id or False,
                    'state_id': customer.state_id and customer.state_id.id or False,
                    'zip': customer.zip or False,
                    'phone': customer.phone or False,
                    'mobile': customer.mobile or False,
                    'email': customer.email or False,
                    'fax': customer.fax or False,
                    #'payment_term_id':customer.property_payment_term and customer.property_payment_term.id or False,
                    #'blank_consignee_line': consignee_lines or False,
                    #'incoterm_id':customer.inco_terms_id and customer.inco_terms_id.id or False,
                    #'currency_id':customer.currency_id and customer.currency_id.id or False,
                    }
        return {'value': vals}
    
    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
       """ Override search() to always show inactive children when searching via ``child_of`` operator. The ORM will
       always call search() with a simple domain of the form [('parent_id', 'in', [ids])]. """
       # a special ``domain`` is set on the ``child_ids`` o2m to bypass this logic, as it uses similar domain expressions
       if len(args) == 1 and len(args[0]) == 3 and args[0][:2] == ('parent_id','in'):
           context = dict(context or {}, active_test=False)
       if context is None:
            context = {}
       if context.get('search_partner_id'):
           if context.get('blanket_id'):
               sql = '''
                    select customer_id from tpt_blanket_order where id = %s
                '''%(context.get('blanket_id'))
               cr.execute(sql)
               partner_ids = [row[0] for row in cr.fetchall()]
               args += [('id','in',partner_ids)]
       return super(res_partner, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context,
                                               count=count, access_rights_uid=access_rights_uid)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def approve_customer(self,cr, uid, ids,vals, context=None):
       if context is None:
           context = {}
       context.update({'approve':1})
       for line in self.browse(cr, uid, ids, context=context):
           if line.disapprove:
               self.write(cr, uid, ids, {'disapprove':False},context)
           else:
               self.write(cr, uid, ids, {'disapprove':True},context)
       return True
   
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if not context.get('approve',False):
            vals.update({'disapprove':False})
             # Added by P.vinothkumar on 17/10/2016 for validate pan_tin must be 10 digits
            if 'pan_tin' in vals:
                pan = vals['pan_tin'].replace(" ", "")
                if pan == '':
                    raise osv.except_osv(_('Warning!'),_('Please Provide the pan number!'))
                if len(pan) < 10:
                    raise osv.except_osv(_('Warning!'),_('Please enter 10 digits PAN'))
            if 'tin' in vals:
                tin = vals['tin'].replace(" ", "")
                if tin == '':
                    raise osv.except_osv(_('Warning!'),_('Please Provide the tin number!'))
                if len(tin) < 11:
                    raise osv.except_osv(_('Warning!'),_('Please enter 10 digits TIN'))
            # END
        return super(res_partner, self).write(cr, uid,ids, vals, context)
       
#      def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
#        if not args:
#            args = []
#        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
#  
#            self.check_access_rights(cr, uid, 'read')
#            where_query = self._where_calc(cr, uid, args, context=context)
#            self._apply_ir_rules(cr, uid, where_query, 'read', context=context)
#            from_clause, where_clause, where_clause_params = where_query.get_sql()
#            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '
#  
#            # search on the name of the contacts and of its company
#            search_name = name
#            if operator in ('ilike', 'like'):
#                search_name = '%%%s%%' % name
#            if operator in ('=ilike', '=like'):
#                operator = operator[1:]
#  
#            unaccent = get_unaccent_wrapper(cr)
#  
#            # TODO: simplify this in trunk with `display_name`, once it is stored
#            # Perf note: a CTE expression (WITH ...) seems to have an even higher cost
#            #            than this query with duplicated CASE expressions. The bulk of
#            #            the cost is the ORDER BY, and it is inevitable if we want
#            #            relevant results for the next step, otherwise we'd return
#            #            a random selection of `limit` results.
#  
#            display_name = """CASE WHEN company.id IS NULL OR res_partner.is_company
#                                   THEN {partner_name}
#                                   ELSE {company_name} || ', ' || {partner_name}
#                               END""".format(partner_name=unaccent('res_partner.name'),
#                                             company_name=unaccent('company.name'))
#  
#            query = """SELECT res_partner.id
#                         FROM res_partner
#                    LEFT JOIN res_partner company
#                           ON res_partner.parent_id = company.id
#                      {where} ({email} {operator} {percent}
#                           OR {display_name} {operator} {percent})
#                     ORDER BY {display_name}
#                    """.format(where=where_str, operator=operator,
#                               email=unaccent('res_partner.email'),
#                               percent=unaccent('%s'),
#                               display_name=display_name)
#  
#            where_clause_params += [search_name, search_name]
#            if limit:
#                query += ' limit %s'
#                where_clause_params.append(limit)
#            cr.execute(query, where_clause_params)
#            ids = map(lambda x: x[0], cr.fetchall())
#  
#            if ids:
#                return self.name_get(cr, uid, ids, context)
#            else:
#                return []
#        return super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
# #      def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
# #         if context is None:
# #             context = {}
# #         if context.get('check_blanket_id'):
# #             blanket_id = context.get('blanket_id')
# #             if not blanket_id:
# #                 args += [('id','=',-1)]
# #         return super(res_partner, self).search(cr, uid, args, offset, limit, order, context, count)
# #     
# #      def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
# #         ids = self.search(cr, user, args, context=context, limit=limit)
# #         return self.name_get(cr, user, ids, context=context)
    
res_partner()

class tpt_cus_consignee(osv.osv):
    _name = "tpt.cus.consignee"
      
    #TPT-BM-17/05/2016 - FOR MOBILE APP
#     def consignee_name(self, cr, uid, ids, field_name, args, context=None):
#         res = {}
#         for line in self.browse(cr,uid,ids,context=context):
#             res[line.id] = {
#                 'name' : '',
#                 }
#             res[line.id]['name'] = line.tpt_consignee_id.name +' ' + line.tpt_consignee_id.customer_code 
#         return res
    #  
    _columns = {
        'tpt_consignee_header_id': fields.many2one('res.partner', 'Parent', ondelete = 'cascade'),        
        'tpt_consignee_id': fields.many2one('res.partner', 'Consignee Name'),
        'tpt_consignee_code': fields.char('Consignee Code'),
        #'name': fields.function(consignee_name, type = 'string', multi='deltas', string='Name'),#TPT-BM-17/05/2016
        'name': fields.char('Name'),
        'street': fields.related('tpt_consignee_id','street',type='char',relation='res.partner',string='Street',store=True,readonly=True,),
        'street2': fields.related('tpt_consignee_id','street2',type='char',relation='res.partner',string='Street2',store=True,readonly=True,),
        'street3': fields.related('tpt_consignee_id','street3',type='char',relation='res.partner',string='Street3',store=True,readonly=True,),
        'state_id': fields.related('tpt_consignee_id','state_id',type='many2one',relation='res.country.state',string='State',store=True,readonly=True,),
        'city': fields.related('tpt_consignee_id','city',type='char',relation='res.partner',string='City',store=True,readonly=True,),
        'zip': fields.related('tpt_consignee_id','zip',type='char',relation='res.partner',string='Zip',store=True,readonly=True,),
        'country_id': fields.related('tpt_consignee_id','country_id',type='many2one',relation='res.country',string='Country',store=True,readonly=True,),
    }
     
    def onchange_tpt_consignee_id(self, cr, uid, ids, name_consignee_id = False, context=None):
        vals = {}
        if name_consignee_id :
            line = self.pool.get('res.partner').browse(cr, uid, name_consignee_id)
            vals = {
                    'tpt_consignee_code': line.customer_code,    
                    }
        return {'value': vals} 
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['tpt_consignee_id','tpt_consignee_code'], context)
        for record in reads:
            name = ''
            if record['tpt_consignee_code']:
                name += record['tpt_consignee_code'][0:6]+'_'
            if record['tpt_consignee_id']:
                name += record['tpt_consignee_id'][1]
                # Added by P.VINOTHKUMAR on 02/03/2017 for adding consignee location details
                consignee_id = record['tpt_consignee_id'] [0]
                partner_detail = self.pool.get('res.partner').browse(cr, uid, consignee_id)
                if partner_detail.city:
                    city_detail= partner_detail.city
                    name += '_' + city_detail
                if partner_detail.state_id:
                    state_detail= partner_detail.state_id.name
                    name +='_' + state_detail
                #END  
             
            res.append((record['id'], name))
        return res
    ###
    def create(self, cr, uid, vals, context=None):
        if 'tpt_consignee_id' in vals:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['tpt_consignee_id'])
            vals.update({'tpt_consignee_code':partner.customer_code,
                         
                         })
        
        return super(tpt_cus_consignee, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'tpt_consignee_id' in vals:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['tpt_consignee_id'])
            vals.update({'tpt_consignee_code':partner.customer_code,
                         
                         })
        new_write = super(tpt_cus_consignee, self).write(cr, uid,ids, vals, context)

        return new_write
tpt_cus_consignee()   
class tpt_cus_ind_commission(osv.osv):
    _name = "tpt.cus.ind.commission"
      
    _columns = {
        'tpt_commission_header_id': fields.many2one('res.partner', 'Parent', ondelete = 'cascade'),        
        'tpt_commission_id': fields.many2one('res.partner', 'Commission Name'),
        'tpt_commission_code': fields.char('Commission Code'),
    } 
    def onchange_tpt_commission_id(self, cr, uid, ids, name_commission_id = False, context=None):
        vals = {}
        if name_commission_id :
            line = self.pool.get('res.partner').browse(cr, uid, name_commission_id)
            vals = {
                    'tpt_commission_code': line.customer_code,    
                    }
        return {'value': vals} 
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['tpt_commission_id','tpt_commission_code'], context)
        for record in reads:
            name = ''
            if record['tpt_commission_code']:
                name += record['tpt_commission_code'][0:6]+'_'
            if record['tpt_commission_id']:
                name += record['tpt_commission_id'][1]
            
            res.append((record['id'], name))
        return res
    ###
    def create(self, cr, uid, vals, context=None):
        if 'tpt_commission_id' in vals:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['tpt_commission_id'])
            vals.update({'tpt_commission_code':partner.customer_code,
                         
                         })
        
        return super(tpt_cus_ind_commission, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'tpt_commission_id' in vals:
            partner = self.pool.get('res.partner').browse(cr, uid, vals['tpt_commission_id'])
            vals.update({'tpt_commission_code':partner.customer_code,
                         
                         })
        new_write = super(tpt_cus_ind_commission, self).write(cr, uid,ids, vals, context)

        return new_write
tpt_cus_ind_commission()  
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
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),   
        'application_id': fields.many2one('crm.application','Application', ondelete='restrict'),    
        'product_uom_qty': fields.float('Allotted Qty', digits=(16,3)),   
        'uom_po_id': fields.many2one('product.uom','UOM'),   
        'sys_batch':fields.many2one('stock.production.lot','System Batch Number',required=True), 
#         'phy_batch':fields.char('Physical Batch No.', size = 1024)
        'phy_batch':fields.function(get_phy_batch,type='char', size = 1024,string='Physical Batch Number',multi='sum',store=True),
        'used_qty': fields.float('Used Qty', digits=(16,3)), 
        'is_deliver': fields.boolean('Is deliver'),
                }
    
    def create(self, cr, uid, vals, context=None):
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        if 'product_uom_qty' in vals and 'sys_batch' in vals:
            batch = self.pool.get('stock.production.lot').browse(cr, uid, vals['sys_batch'])
            if round(batch.stock_available, 3) < round(vals['product_uom_qty'],3):
                raise osv.except_osv(_('Warning!'),_('Allotted Quantity must be less than available stock Quantity! %s')%batch.name)
        return super(tpt_batch_allotment_line, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        if 'product_uom_qty' in vals and 'sys_batch' in vals:
            batch = self.pool.get('stock.production.lot').browse(cr, uid, vals['sys_batch'])
            #if batch.stock_available < vals['product_uom_qty']:
            if round(batch.stock_available, 3) < round(vals['product_uom_qty'],3):
                raise osv.except_osv(_('Warning!'),_('Allotted quantity should not be greater than Available Quantity!%s')%batch.name)
        return super(tpt_batch_allotment_line, self).write(cr, uid,ids, vals, context)
    
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
                          'message': _('Insufficient Quantity in the Batch % s! \n Available Qty is %s')%(batch.name,batch.stock_available),  
                          }  
                vals['sys_batch']=False
                return {'value': vals,'warning':warning}
            else:
                vals['sys_batch']= sys_batch
                vals['phy_batch']= batch.phy_batch_no or 0
                vals['product_uom_qty']= batch.stock_available
        if sys_batch and not qty:
            batch = self.pool.get('stock.production.lot').browse(cr, uid, sys_batch)
            vals['phy_batch']= batch.phy_batch_no
            vals['product_uom_qty']= batch.stock_available or 0
        return {'value': vals}
    
    def onchange_product_id(self, cr, uid, ids,product_id=False,request_id=False,context=None):
        res = {'value':{
                        'product_type':False,
                        'application_id':False,
                        'uom_po_id':False,
                        }}
        if product_id and request_id:
            product_info_obj = self.pool.get('tpt.product.information')
            product_info_ids = product_info_obj.search(cr, uid, [('product_id','=',product_id),('product_information_id','=',request_id)])
            product_info_id = product_info_obj.browse(cr, uid, product_info_ids)
            if product_info_id:
                for product in product_info_id:
                    res['value'].update({
                                         'product_type':product.product_type or False,
                                        'application_id':product.application_id.id or False,
                                        'uom_po_id':product.uom_po_id and product.uom_po_id.id or False,
                                         })
        else:
            res['value'].update({
                             'product_type':False,
                            'application_id':False,
                            'uom_po_id':False,
                             })
        return res
    
    def _check_batch_allotment_line(self, cr, uid, ids, context=None):
        for batch in self.browse(cr, uid, ids, context=context):
            quotation_ids = self.search(cr, uid, [('id','!=',batch.id),('sys_batch','=',batch.sys_batch.id),('batch_allotment_id','=',batch.batch_allotment_id.id)])
            if quotation_ids:
                raise osv.except_osv(_('Warning!'),_('Can not select more than one time for System Batch Number!'))
                return False
            return True
        
    _constraints = [
        (_check_batch_allotment_line, 'Identical Data', ['sys_batch']),
    ]  

tpt_batch_allotment_line()

class tpt_pgi(osv.osv):
    _name = "tpt.pgi"
     
    _columns = {
        'name': fields.char('Post Googs Issue', size = 1024, readonly=True),
        'do_id':fields.many2one('stock.picking.out','Delivery Order',required = True), 
        'date':fields.date('DO Date',required = True), 
        'customer_id':fields.many2one('res.partner', 'Customer', readonly=True), 
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'pgi_id', 'Product'), 
                }
    _defaults = {
        'name': '/',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.pgi.import') or '/'
        if 'batch_allotment_line' in vals:
            do = self.pool.get('stock.picking.out').browse(cr, uid, vals['do_id'])
            vals.update({'customer_id':do.partner_id and do.partner_id.id or False})
        return super(tpt_pgi, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'batch_allotment_line' in vals:
            do = self.pool.get('stock.picking.out').browse(cr, uid, vals['do_id'])
            vals.update({'customer_id':do.partner_id and do.partner_id.id or False})
        return super(tpt_pgi, self).write(cr, uid,ids, vals, context)
    
    def onchange_do_id(self, cr, uid, ids, do_id=False, context=None):
        vals = {}
        for pgi in ids:
            sql = '''
                delete from tpt_batch_allotment_line where pgi_id = %s
            '''%(pgi)
            cr.execute(sql)
        if do_id:
            do = self.pool.get('stock.picking.out').browse(cr, uid, do_id)
            pgi_line = []
            for line in do.move_lines:
                pgi_line.append((0,0,{
                                      'product_id': line.product_id.id,
                                      'product_uom_qty':line.product_qty,
                                      'product_type':line.product_type,
                                      'uom_po_id': line.product_uom.id,
                                      'application_id':line.application_id and line.application_id.id or False,
                                      'sys_batch':line.prodlot_id and line.prodlot_id.id or False,
                                      }))
            vals = {'date':do.date or False,'batch_allotment_line': pgi_line,'customer_id':do.partner_id and do.partner_id.id or False,'warehouse':do.warehouse and do.warehouse.id or False}
        return {'value':vals}
    
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


class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    _columns = {
        'phy_batch_no': fields.char('Physical Serial No.', size = 1024,required = True), 
                }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_prodlot_by_batch_alot'):
            sale_id = context.get('sale_id', False)
            if sale_id:
                sql = '''
                    select sys_batch from tpt_batch_allotment_line line, tpt_batch_allotment mast
                    where mast.id = line.batch_allotment_id and batch_allotment_id in (select id from tpt_batch_allotment where sale_order_id = %s and state = 'confirm')
                '''%(sale_id)
                cr.execute(sql)
                prodlot_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',prodlot_ids)]
        #TPT-BM-29/06/2016
                sql = '''
                select id from stock_production_lot where id in (
                select prodlot_id from stock_move where picking_id =(
                select return_do_id from sale_order  where id=%s))
                '''%sale_id
                cr.execute(sql)
                temp = cr.fetchall()
                if temp:
                    prodlot_ids = [row[0] for row in temp]
                    args = [('id','in',prodlot_ids)]
        #TPT-END
        return super(stock_production_lot, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
stock_production_lot()  

class tpt_schedule_dispatch_update(osv.osv):
    _name = "tpt.schedule.dispatch.update"
    
    _columns = {
        'name': fields.many2one('tpt.blanket.order', 'Blanket Order', required = True, states={'done':[('readonly', True)]}),
        'bo_line_id': fields.many2one('tpt.blank.order.line', 'Blanket Order Line', required=True, states={'done':[('readonly', True)]}),
        'schedule_date': fields.date('Schedule Dispatch Date', states={'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Approved')],'Status', readonly=True, states={'done':[('readonly', True)]}),
                }
    _defaults = {
        'state': 'draft',
    }
    
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if line.schedule_date:
                self.pool.get('tpt.blank.order.line').write(cr, uid,[line.bo_line_id.id], {'dispatch_date':line.schedule_date}, context)
            else:
                raise osv.except_osv(_('Warning!'),_('Please select Schedule Dispatch Date!')) 
        return self.write(cr, uid, ids,{'state':'done'})
    def bt_print(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        
        prod_ids = self.browse(cr, uid, ids[0])
        datas = {
                 'ids': ids,
                 'model': 'tpt.schedule.dispatch.update',
                 'form': self.read(cr, uid, ids[0], context=context)
            }
        if prod_ids.product_id and prod_ids.product_id.id==2: 
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'fsh_stock_advise_report',
                } 
        else:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'tio2_stock_advise_report',
                } 
tpt_schedule_dispatch_update()

#TPT - By BalamuruganPurushothaman - ON 09/11/2015
class tpt_stock_trans_advise(osv.osv):
    _name = "tpt.stock.trans.advise"
    _rec_name = "product_id"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product',  states={'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'date': fields.date('Date', states={'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'warehouse_from': fields.many2one('stock.location', 'Warehouse From',  states={'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'warehouse_to': fields.many2one('stock.location', 'Warehouse To',  states={'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'truck_no': fields.char('Truck No.', states={'done':[('readonly', True)], 'cancel':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Approved'),('cancel', 'Cancelled'),],'Status', readonly=True, states={'done':[('readonly', True)]}),
        'batch_line': fields.one2many('tpt.move.batch', 'stock_trans_id', 'Stock Transfer Advise', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),    
                }
    _defaults = {
        'state': 'draft',
    }
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    #===========================================================================
    # def onchange_product_id(self, cr, uid, ids, product_id, context=None):
    #     vals = {}
    #     rs = {}
    #     meals_details_order_ids=[]
    #     if product_id:
    #         for master in self.browse(cr, uid, ids):
    #             for line in master.meals_details_order_ids:
    #                 rs = {'product_id':product_id}
    #                 meals_details_order_ids.append((1,line.id,rs))
    #                 vals = {'batch_line':meals_details_order_ids}
    #     return {'value': vals}
    #===========================================================================
    def bt_print(self, cr, uid, ids, context=None):
        '''
        This function prints the stock transfers
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        st_ids = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'tpt.stock.trans.advise',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        if st_ids.product_id.default_code=='M0501010001' or st_ids.product_id.default_code=='M0501010008':
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_stock_trans_titanium_advise_report',
                } 
        else:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_stock_trans_fsh_advise_report',
                } 
    
tpt_stock_trans_advise()

class tpt_move_batch(osv.osv):
    _name = "tpt.move.batch"
    
    _columns = {
        'stock_trans_id': fields.many2one('tpt.stock.trans.advise', 'Stock Transfer Advise', ondelete = 'cascade'),        
        'batch_id': fields.many2one('stock.production.lot', 'Batch No.'),
        'bags': fields.char('Bags', ),
        'qty': fields.float('MT', digits=(16,3)),
        'remarks': fields.char('Remarks'),
     }
    def onchange_sys_batch(self, cr, uid, ids,sys_batch=False,context=None):
        vals = {}
        if sys_batch:
            batch = self.pool.get('stock.production.lot').browse(cr, uid, sys_batch)
            vals['qty']= batch.stock_available or 0
        return {'value': vals}
tpt_move_batch()
 
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
