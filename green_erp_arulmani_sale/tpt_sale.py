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

class product_product(osv.osv):
    _inherit = "product.product"

    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context and context.get('search_default_categ_id', False):
            args.append((('categ_id', 'child_of', context['search_default_categ_id'])))
        if context.get('search_blanket_id'):
            sql = '''
                select product_id from tpt_blank_order_line where blanket_order_id in(select id from tpt_blanket_order where id = %s)
            '''%(context.get('blanket_id'))
            cr.execute(sql)
            blanket_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',blanket_ids)]
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
    
    _order = "blanket_id"
    
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
            freight = 0.0
            for orderline in line.order_line:
                freight = freight + orderline.freight
                val1 = val1 + orderline.price_subtotal
                res[line.id]['amount_untaxed'] = val1
                val2 = val1 * line.sale_tax_id.amount / 100
                res[line.id]['amount_tax'] = val2
                val3 = val1 + val2 + freight
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
        'document_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)'),('cancelled','Cancelled')],'Document Status'),
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
        'order_policy': 'picking',
        'document_status':'draft',
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

    def onchange_doc_status(self, cr, uid, ids, payment_term_id=False, context=None):
        vals = {}
        if payment_term_id==1:
             vals = {'document_status':'waiting'}
        else:
            vals = {'document_status':'completed'}
        return {'value':vals}

  
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
    
    def onchange_partner_id(self, cr, uid, ids, partner_id=False, blanket_id=False, context=None):
        vals = {}
        consignee_lines = []
#         for blanket in self.browse(cr, uid, ids):
#             sql = '''
#                 delete from order_line where blanket_order_id = %s
#             '''%(blanket.id)
#             cr.execute(sql)
        if partner_id and not blanket_id:
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            vals = {'invoice_address':part.street,
                    'street2':part.street2,
                    'city':part.city,
                    'country_id':part.country_id.id,
                    'state_id':part.state_id.id,
                    'zip':part.zip,
                    'payment_term_id':part.property_payment_term.id,
                    'incoterms_id':part.inco_terms_id and part.inco_terms_id.id or False,
                    }
        return {'value': vals}    
        
#     def create(self, cr, uid, vals, context=None):
#         if vals.get('name','/')=='/':
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.sale.order.import') or '/'
#         return super(sale_order, self).create(cr, uid, vals, context=context)
   
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
        self.write(cr, uid, ids, {'state': 'cancel'})
        sql = '''
            update sale_order set document_status='cancelled' where id = %s
        '''%(sale.id)
        cr.execute(sql)
        return True 
#     
    def create(self, cr, uid, vals, context=None):
#         if 'document_status' in vals:
#             vals['document_status'] = 'draft'
        new_id = super(sale_order, self).create(cr, uid, vals, context)
        sale = self.browse(cr, uid, new_id)
#         sale_ids = sale.search(cr,uid,[('state','!=','cancel')])
        if sale.blanket_id:
            flag=False
#             document_status = 'partially'
            for blanket_line in sale.blanket_id.blank_order_line:
                sql_so = '''
                    select id from sale_order where blanket_id = %s and state!='cancel'
                '''%(sale.blanket_id.id)
                cr.execute(sql_so)
                kq = cr.fetchall()
                so_ids = []
                if kq:
                    for i in kq:
                        so_ids.append(i[0])
                    so_ids = str(so_ids).replace("[","(")
                    so_ids = so_ids.replace("]",")")
                sql = '''
                    select sol.product_id, sum(sol.product_uom_qty) as qty
                    from sale_order_line sol
                    inner join sale_order so on so.id = sol.order_id
                    where sol.order_id in %s and sol.product_id = %s
                    group by sol.product_id
                '''%(so_ids,blanket_line.product_id.id)
                cr.execute(sql)
                kq = cr.fetchall()
                for data in kq:
                    if blanket_line.product_uom_qty < data[1]:
                        document_status = 'partially'
                        raise osv.except_osv(_('Warning!'),_('Quantity must be less than quantity of Blanket Order is product %s'%blanket_line.product_id.name_template))
                    elif blanket_line.product_uom_qty > data[1]:
                        document_status = 'partially'
                        flag=True
                        sql_stt = '''
                            update sale_order set document_status='partially' where id = %s
                        '''%(sale.id)
                        cr.execute(sql_stt)
                    else:
                        document_status = 'close'
                if flag==False:
                    sql_stt = '''
                        update sale_order set document_status='close' where id = %s
                    '''%(sale.id)
                    cr.execute(sql_stt)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
#         if 'document_status' in vals:
#             vals['document_status'] = 'draft'
        new_write = super(sale_order, self).write(cr, uid,ids, vals, context)
        for sale in self.browse(cr, uid, ids):
            if sale.blanket_id:
                flag=False
#                 document_status = 'partially'
                for blanket_line in sale.blanket_id.blank_order_line:
                    sql_so = '''
                        select id from sale_order where blanket_id = %s and state!='cancel'
                    '''%(sale.blanket_id.id)
                    cr.execute(sql_so)
                    kq = cr.fetchall()
                    so_ids = []
                    if kq:
                        for i in kq:
                            so_ids.append(i[0])
                        so_ids = str(so_ids).replace("[","(")
                        so_ids = so_ids.replace("]",")")
                    sql = '''
                        select sol.product_id, sum(sol.product_uom_qty) as qty
                        from sale_order_line sol
                        inner join sale_order so on so.id = sol.order_id
                        where sol.order_id in %s and sol.product_id = %s
                        group by sol.product_id
                    '''%(so_ids,blanket_line.product_id.id)
                    cr.execute(sql)
                    kq = cr.fetchall()
                    for data in kq:
                        if blanket_line.product_uom_qty < data[1]:
                            raise osv.except_osv(_('Warning!'),_('Quantity must be less than quantity of Blanket Order is product %s'%blanket_line.product_id.name_template))
                        elif blanket_line.product_uom_qty > data[1]:
                            flag=True
                            sql_stt = '''
                               update sale_order set document_status='partially' where id = %s
                                '''%(sale.id)
 
                            cr.execute(sql_stt)
                        else:
                            document_status = 'close'
                    if flag==False:
                       sql_stt = '''
                          update sale_order set document_status='close' where id = %s
                           '''%(sale.id)

                       cr.execute(sql_stt)
#                         if blanket_line.product_uom_qty < data[1]:
#                             document_status = 'partially'
#                             raise osv.except_osv(_('Warning!'),_('Quantity must be less than quantity of Blanket Order is product %s'%blanket_line.product_id.name_template))
#                         elif blanket_line.product_uom_qty > data[1]:
#                             document_status = 'partially'
#                             flag=True
#                             self.write(cr,uid,[new_write],{'document_status':document_status})
#                         else:
#                             document_status = 'close'
#                     if flag==False:
#                         self.write(cr,uid,[new_write],{'document_status':document_status})
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
                    'order_policy': 'picking',
                    'partner_invoice_id': addr['invoice'],
                    'document_status':'close',
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
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        picking_out_obj = self.pool.get('stock.picking.out')
        stock_move_obj = self.pool.get('stock.move')
        picking_out_ids = picking_out_obj.search(cr,uid,[('sale_id','=',ids[0])],context=context)
        if picking_out_ids:
            sql = '''
                select name_consignee_id from sale_order_line where order_id = %s group by name_consignee_id
            '''%(ids[0])
            cr.execute(sql)
            consignee_ids = [row[0] for row in cr.fetchall()]
            picking_id = picking_out_ids[0]
            sale = self.browse(cr, uid, ids[0])
            first_picking_id = False
            for i,consignee_id in enumerate(consignee_ids):
                if i==0:
                    first_picking_id = picking_id
                    picking = picking_out_obj.browse(cr, uid, picking_id)
                    picking_out_obj.write(cr, uid, [picking_id], {'cons_loca': consignee_id,'backorder_id':picking_id,'origin':picking.origin,'sale_id':ids[0],'partner_id':sale.partner_id.id})
                else:
                    sql = '''
                        select id from sale_order_line where name_consignee_id = %s and order_id = %s
                    '''%(consignee_id,sale.id)
                    cr.execute(sql)
                    order_line_ids = [row[0] for row in cr.fetchall()]
                    default = {'backorder_id':picking_id,'move_lines':[],'cons_loca': consignee_id}
                    picking = picking_out_obj.browse(cr, uid, picking_id)
                    new_picking_id = picking_out_obj.copy(cr, uid, picking_id, default)
                    picking_out_obj.write(cr, uid, [new_picking_id], {'cons_loca': consignee_id,'backorder_id':picking_id,'origin':picking.origin,'sale_id':ids[0],'partner_id':sale.partner_id.id})
                    stock_move_ids = stock_move_obj.search(cr, uid, [('sale_line_id','in',order_line_ids)])
                    stock_move = stock_move_obj.browse(cr,uid,stock_move_ids[0])
                    stock_move_obj.write(cr, uid, stock_move_ids, {'picking_id':new_picking_id,'product_type':stock_move.sale_line_id.product_type,'application_id':stock_move.sale_line_id.application_id and stock_move.sale_line_id.application_id.id or False})
    #                 wf_service.trg_validate(uid, 'stock.picking', new_picking_id, 'button_confirm', cr)
                    picking_id = new_picking_id
            if first_picking_id:
                for line in picking_out_obj.browse(cr, uid, first_picking_id).move_lines:
                    stock_move_obj.write(cr, uid, [line.id], {'product_type':line.sale_line_id.product_type,'application_id':line.sale_line_id.application_id and line.sale_line_id.application_id.id or False})
        return True
    
sale_order()

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
            subtotal = (line.product_uom_qty * line.price_unit) + (line.product_uom_qty * line.price_unit) * (line.order_id.excise_duty_id.amount/100)
            res[line.id] = subtotal
        return res
     
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required = True),
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'freight': fields.float('Freight'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'name_consignee_id': fields.many2one('res.partner', 'Consignee', required = True),
        'location': fields.char('Location', size = 1024),   
        'product_uom_qty': fields.float('Quantity', digits=(16,2), required=True, readonly=True, states={'draft': [('readonly', False)]}),
    }
    def create(self, cr, uid, vals, context=None):
        if 'freight' in vals:
            if (vals['freight'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not negative value'))
        return super(sale_order_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'freight' in vals:
            if (vals['freight'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not negative value'))
        return super(sale_order_line, self).write(cr, uid,ids, vals, context)

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
sale_order_line()


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
            freight = 0.0
            for orderline in line.blank_order_line:
                freight = freight + orderline.freight
                val1 += orderline.sub_total
            res[line.id]['amount_untaxed'] = val1
            val2 = val1 * line.sale_tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
            val3 = val1 + val2 + freight
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
                        'location': str(line.street or '') + str(line.street2 or '') + ' , ' + str(line.city or ''),
                        
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
                    'currency_id':customer.currency_id and customer.currency_id.id or False,
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
        'product_type': fields.selection([('rutile', 'Rutile'),('anatase', 'Anatase')],'Product Type'),
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
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        return super(tpt_blank_order_line, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        return super(tpt_blank_order_line, self).write(cr, uid,ids, vals, context)
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'uom_po_id':product.uom_id.id,
                    'price_unit':product.list_price,
                    'description': product.name
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
        'name': fields.char('Request No', size = 1024,readonly=True, required = True , states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'sale_order_id': fields.many2one('sale.order', 'Sales Order', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'customer_id': fields.many2one('res.partner', 'Customer', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'description': fields.text('Description', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'request_date': fields.date('Request Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'product_information_line': fields.one2many('tpt.product.information', 'product_information_id', 'Product Information', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
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
            batch_allotment_ids = self.pool.get('tpt.batch.allotment').search(cr,uid,[('batch_request_id', '=',line.id )])
            if batch_allotment_ids:
                raise osv.except_osv(_('Warning!'),_('Batch Request has already existed on Batch Allotment'))
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def _check_sale_order_id(self, cr, uid, ids, context=None):
        for request in self.browse(cr, uid, ids, context=context):
            request_ids = self.search(cr, uid, [('id','!=',request.id),('sale_order_id','=',request.sale_order_id.id)])
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
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.batch.req.import') or '/'
        if 'sale_order_id' in vals:
            sale = self.pool.get('sale.order').browse(cr, uid, vals['sale_order_id'])
            product_lines = []
            for line in sale.order_line:
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
        'product_id': fields.many2one('product.product', 'Product',required = True),     
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),   
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
        'sale_order_id':fields.many2one('sale.order','Sale Order',required = True),   
        'customer_id':fields.many2one('res.partner', 'Customer', required = True), 
        'description':fields.text('Description'),
        'state': fields.selection([('to_approve', 'To Approved'), ('refuse', 'Refused'),('confirm', 'Approve'), ('cancel', 'Cancelled')],'Status'),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'batch_allotment_id', 'Product Information'), 
                }
    _defaults = {
              'state': 'to_approve',
    }
    def create(self, cr, uid, vals, context=None):
        
        return super(tpt_batch_allotment, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        
        return super(tpt_batch_allotment, self).write(cr, uid,ids, vals, context)
    def confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirm'})
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
                 }
    
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
        'name': fields.char('Post Googs Issue', size = 1024, readonly=True),
        'do_id':fields.many2one('stock.picking.out','Delivery Order',required = True), 
        'date':fields.date('DO Date',required = True), 
        'customer_id':fields.many2one('res.partner', 'Customer', required = True), 
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'batch_allotment_line': fields.one2many('tpt.batch.allotment.line', 'pgi_id', 'Product'), 
                }
    _defaults = {
        'name': '/',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.pgi.import') or '/'
        return super(tpt_pgi, self).create(cr, uid, vals, context=context)
    
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
                    select sys_batch from tpt_batch_allotment_line where batch_allotment_id in (select id from tpt_batch_allotment where sale_order_id = %s)
                '''%(sale_id)
                cr.execute(sql)
                prodlot_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',prodlot_ids)]
        return super(stock_production_lot, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
stock_production_lot()  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
