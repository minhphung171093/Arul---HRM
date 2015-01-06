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

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'cons_loca':fields.many2one('res.partner','Consignee Location'),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'transporter':fields.char('Transporter Name', size = 64),
        'truck':fields.char('Truck Number', size = 64),
        'remarks':fields.text('Remarks'),
        'doc_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)')],'Document Status'),
        'sale_id': fields.many2one('sale.order', 'Sales Order', ondelete='set null', select=True),
        'do_ref_id': fields.many2one('stock.picking.out','DO Reference'),   
        'move_date': fields.date('Movement Date'),
        'reason': fields.text("Reason for Move"),
#         'location_sour_id': fields.many2one('stock.location', 'Source Location'),
                }
    
    _defaults = {
        'move_date': time.strftime('%Y-%m-%d'),
        'name': '/',
    }
     
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.stock.move.import') or '/'
        return super(stock_picking, self).create(cr, uid, vals, context=context)
    
    def onchange_move_date(self, cr, uid, ids, move_date=False, context=None):
        vals = {}
        warning = {}
        if move_date:
            sql = '''
                select move_date from stock_picking where type='internal' order by move_date desc
            ''' 
            cr.execute(sql)
            move_dates = [row[0] for row in cr.fetchall()]
            if move_dates and move_date < move_dates[0]:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Not allow to create back Movement Date')
                }
                vals = {'move_date':False}
        return {'value': vals,'warning':warning}
    
    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        """ Builds the dict containing the values for the invoice
            @param picking: picking object
            @param partner: object of the partner to invoice
            @param inv_type: type of the invoice ('out_invoice', 'in_invoice', ...)
            @param journal_id: ID of the accounting journal
            @return: dict that will be used to create the invoice object
        """
        if isinstance(partner, int):
            partner = self.pool.get('res.partner').browse(cr, uid, partner, context=context)
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        comment = self._get_comment_invoice(cr, uid, picking)
        invoice_vals = {
            'name': picking.name,
            'origin': (picking.name or '') + (picking.origin and (':' + picking.origin) or ''),
            'type': inv_type,
            'account_id': account_id,
            'partner_id': partner.id,
            'comment': comment,
            'payment_term': payment_term,
            'fiscal_position': partner.property_account_position.id,
            'date_invoice': context.get('date_inv', False),
            'company_id': picking.company_id.id,
            'user_id': uid,
            
            'sale_id': picking.sale_id and picking.sale_id.id or False,
            'payment_term': picking.sale_id.payment_term_id and picking.sale_id.payment_term_id.id or False,
            'currency_id': picking.sale_id.currency_id and picking.sale_id.currency_id.id or False,
            'excise_duty_id': picking.sale_id.excise_duty_id and picking.sale_id.excise_duty_id.id or False,
            'doc_status': 'completed',
            'cons_loca': picking.cons_loca and picking.cons_loca.id or False,
            'delivery_order_id': picking.id,
            'sale_tax_id': picking.sale_id.sale_tax_id and picking.sale_id.sale_tax_id.id or False,
        }
        cur_id = self.get_currency_id(cr, uid, picking)
        if cur_id:
            invoice_vals['currency_id'] = cur_id
        if journal_id:
            invoice_vals['journal_id'] = journal_id
        return invoice_vals
    
stock_picking()

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'cons_loca':fields.many2one('res.partner','Consignee Location'),
        'warehouse':fields.many2one('stock.location','Warehouse'),
        'transporter':fields.char('Transporter Name', size = 64),
        'truck':fields.char('Truck Number', size = 64),
        'remarks':fields.text('Remarks'),
        'doc_status':fields.selection([('draft','Draft'),('waiting','Waiting for Approval'),('completed','Completed(Ready to Process)'),('partially','Partially Delivered'),('close','Closed(Delivered)')],'Document Status'),
        'sale_id': fields.many2one('sale.order', 'Sales Order', ondelete='set null', select=True),
                }
    def write(self, cr, uid, ids, vals, context=None):
        stock = self.browse(cr, uid, ids[0])
        if 'warehouse' in vals:
            location_id = vals['warehouse']
            sql = '''
                UPDATE stock_move
                SET location_id= %s
                WHERE picking_id = %s;
                '''%(location_id,stock.id)
            cr.execute(sql)
        return super(stock_picking_out, self).write(cr, uid,ids, vals, context)
    
    def print_dispatch_slip(self, cr, uid, ids, context=None):
        datas = {
             'ids': ids,
             'model': 'stock.picking.out',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tpt_print_dispatch_slip',
        }
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = "stock.move"
    def get_phy_batch(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for physical in self.browse(cr, uid, ids, context=context):
            res[physical.id] = {
                'phy_batch': physical.prodlot_id and physical.prodlot_id.phy_batch_no or False,
            }
        return res
    _columns = {
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),  
        'application_id': fields.many2one('crm.application','Application'),   
        'prodlot_id': fields.many2one('stock.production.lot', 'System Serial No.', states={'done': [('readonly', True)]}, help="Serial number is used to put a serial number on the production", select=True), 
#         'sys_batch':fields.many2one('stock.production.lot','System Serial No.'), 
#         'phy_batch':fields.char('Physical Batch No.', size = 1024)
        'phy_batch':fields.function(get_phy_batch,type='char', size = 1024,string='Physical Serial No.',multi='sum',store=True),

                }
    
stock_move()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
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
            for invoiceline in line.invoice_line:
                freight = freight + invoiceline.freight
                val1 = val1 + invoiceline.price_subtotal
                res[line.id]['amount_untaxed'] = val1
                val2 = val1 * (line.sale_tax_id.amount and line.sale_tax_id.amount / 100 or 1)
                res[line.id]['amount_tax'] = val2
                val3 = val1 + val2 + freight
                res[line.id]['amount_total'] = val3
        return res
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    _columns = {
        'delivery_order_id': fields.many2one('stock.picking.out','Delivery Order', readonly=True),
        'cons_loca': fields.many2one('res.partner','Consignee Location'),
        'sale_id':  fields.many2one('sale.order','Sale Order'), 
        'excise_duty_id': fields.many2one('account.tax','Excise Duty', required = False),
        'sale_tax_id': fields.many2one('account.tax','Sales Tax', required = False),
        'doc_status':fields.selection([('completed','Completed')],'Document Status'),
        'invoice_type':fields.selection([ ('domestic','Domestic'), ('export','Export'), ],'Invoice Type'),
        'vessel_flight_no': fields.char('Vessel/Flight No.', size = 1024),
        'port_of_loading_id': fields.many2one('res.country','Port Of Loading'),
        'port_of_discharge_id': fields.many2one('res.country','Port Of_Discharge'),
        'mark_container_no': fields.char('Marks & No Container No.', size = 1024),
        'insurance': fields.float('Insurance'),
        'pre_carriage_by': fields.selection([('sea','Sea')],'Pre Carriage By'),
        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='sums', help="The amount without tax.", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='sums', help="The total amount."),
                }
    _defaults = {
#         'name': '/',
    }
    
    def onchange_date_invoice(self, cr, uid, ids, date_invoice=False, context=None):
        vals = {}
        warning = {}
        if date_invoice:
            sql = '''
                select date_invoice from account_invoice where type='out_invoice' order by date_invoice desc
            ''' 
            cr.execute(sql)
            date_invoices = [row[0] for row in cr.fetchall()]
            if date_invoices and date_invoice < date_invoices[0]:
                warning = {
                    'title': _('Warning!'),
                    'message': _('Not allow to create back date invoices')
                }
                vals = {'date_invoice':False}
        return {'value': vals,'warning':warning}
    
    def onchange_delivery_order_id(self, cr, uid, ids, delivery_order_id=False, context=None):
        vals = {}
        invoice_lines = []
        if delivery_order_id :
            delivery = self.pool.get('stock.picking.out').browse(cr, uid, delivery_order_id)
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from invoice_line where invoice_id = %s
                '''%(line.id)
                cr.execute(sql)
            for invoice_line in delivery.move_lines:
                rs_invoice = {
                      'product_id': invoice_line.product_id and invoice_line.product_id.id or False,
                      'product_type': invoice_line.product_type or False,
                      'application_id': invoice_line.application_id and invoice_line.application_id.id or False,
                      'quantity': invoice_line.product_qty or False,
                      'uos_id': invoice_line.product_uom and invoice_line.product_uom.id or False,
                      }
                invoice_lines.append((0,0,rs_invoice))
            vals = {'partner_id':delivery.partner_id and delivery.partner_id.id or False,
                    'cons_loca':delivery.partner_id and delivery.cons_loca.id or False,
                    'sale_id': delivery.sale_id and delivery.sale_id.id or False,
                    'doc_status':delivery.doc_status or False,
                    'invoice_line': invoice_lines or False
                    }
        return {'value': vals}
    
#     def create(self, cr, uid, vals, context=None):
#         if vals.get('number','/')=='/':
#             vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.customer.invoice.import') or '/'
#         return super(account_invoice, self).create(cr, uid, vals, context=context)
    
    def invoice_print(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tpt_export_account_invoice',
            'datas': datas,
            'nodestroy' : True
        }
    
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        subtotal = 0.0
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            subtotal = (line.quantity * line.price_unit) + (line.quantity * line.price_unit) * (line.invoice_id.excise_duty_id.amount and line.invoice_id.excise_duty_id.amount/100 or 1)
            res[line.id] = subtotal
        return res
    
    _columns = {
        'product_type': fields.selection([('product', 'Stockable Product'),('consu', 'Consumable'),('service', 'Service')],'Product Type'),
        'application_id': fields.many2one('crm.application', 'Application'),
        'freight': fields.float('FreightAmt'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
       } 
    
account_invoice_line()
