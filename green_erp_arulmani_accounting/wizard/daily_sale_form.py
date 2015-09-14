# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
import locale
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_daily_sale_report(osv.osv_memory):
    _name = "tpt.daily.sale.report"
    _columns = {
        'name': fields.char('', readonly=True),
        'daily_sale_line': fields.one2many('tpt.daily.sale.line', 'dailysale_id', 'Daily Sale Line'),
        'product_title': fields.char('', readonly=True), 
        'application_title': fields.char('', readonly=True), 
        'state_title': fields.char('', readonly=True), 
        'city_title': fields.char('', readonly=True), 
        'customer_title': fields.char('', readonly=True), 
        'consignee_title': fields.char('', readonly=True),
        'date_from_title': fields.char('', readonly=True), 
        'date_to_title': fields.char('', readonly=True), 
        
        'product_id': fields.many2one('product.product', 'Material', required=False),
        'application_id':fields.many2one('crm.application','Application', required=False),
        'state_id':fields.many2one("res.country.state", 'Region', required=False),
        'customer_id':fields.many2one("res.partner", 'Customer', required=False),
        'name_consignee_id':fields.many2one("res.partner", 'Consignee', required=False),
        'city': fields.char('City', size=128),
        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
    }
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'daily.sale.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daily_sale_report_pdf', 'datas': datas}
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'daily.sale.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daily_sale_report_xls', 'datas': datas}
    
    
tpt_daily_sale_report()

class tpt_daily_sale_line(osv.osv_memory):
    _name = "tpt.daily.sale.line"
    _columns = {
        'dailysale_id': fields.many2one('tpt.daily.sale.report','Daily Sale', ondelete='cascade'),
        'vvt_number': fields.char('Invoice. No', size = 1024),
        'date_invoice': fields.date('Invoice Date'),
        'order_type': fields.char('Billing Type', size = 1024),
        'distribution': fields.char('Distribution Channel', size = 1024),
        'country': fields.char('Destination Country', size = 1024),
        'state': fields.char('Sales Region', size = 1024),
        'city': fields.char('City Name', size = 1024),
        'po_number': fields.char('Purchase Order', size = 1024),
        'po_date': fields.date('Purchase Order Date'),
        'sales_order': fields.char('Sales Order', size = 1024),
        'delivery_order': fields.char('Delivery No', size = 1024),
        'product_code': fields.char('Material', size = 1024),
        'product_name': fields.char('Material Description', size = 1024),
        'application_name': fields.char('Application', size = 1024),
        'customer_code': fields.char('Customer No', size = 1024),
        'partner_name': fields.char('Customer Name', size = 1024),
        'consignee_code': fields.char('Consignee. No', size = 1024),
        'consignee_name': fields.char('Consignee Name', size = 1024),
        'transporter': fields.char('Transport', size = 1024),
        'lr_no': fields.char('LR Number', size = 1024),
        'truck': fields.char('Truck No', size = 1024),
        'booked_to': fields.char('Booked To', size = 1024),
        'customer_group': fields.char('Cus. Grp', size = 1024),
        'payment_term': fields.char('Payment Term', size = 1024),
        'quantity': fields.float('Quantity',digits=(16,3)),
        'price_unit': fields.float('Unit Price',digits=(16,2)),
        'uom': fields.char('UOM', size = 1024),
        'basic_price': fields.float('Basic Price',digits=(16,2)),
        'excise_duty': fields.float('Excise Duty',digits=(16,2)),
        'cst_tax': fields.float('CST',digits=(16,2)),
        'vat_tax': fields.float('VAT',digits=(16,2)),
        'tcs_tax': fields.float('TCS',digits=(16,2)),
        'freight': fields.float('Freight',digits=(16,2)),
        'insurance': fields.float('Insurance',digits=(16,2)),
        'other_charges': fields.float('Others',digits=(16,2)),
        'currency': fields.char('Curr(DOC)', size = 1024),
        'total_amt': fields.float('Value(INR)',digits=(16,2)),
        'other_reasons': fields.char('Order Reason', size = 1024),        
 }
tpt_daily_sale_line()

class daily_sale_form(osv.osv_memory):
    _name = "daily.sale.form"
    _columns = {    
                'product_id': fields.many2one('product.product', 'Material', required=False),
                'application_id':fields.many2one('crm.application','Application', required=False),
                'state_id':fields.many2one("res.country.state", 'Region', required=False),
                'customer_id':fields.many2one("res.partner", 'Customer', required=False),
                'name_consignee_id':fields.many2one("res.partner", 'Consignee', required=False),
                'city': fields.char('City', size=128),
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                }
    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def print_report(self, cr, uid, ids, context=None):
        
         # TPT-Y added on 31Aug2015, fix - 3156
        def get_total(cash,type):
            sum = 0.00            
            for line in cash:
                if type == 'total_amt':
                    sum += line.invoice_id.amount_total_inr
                if type == 'total_basic_amt':
                    sum += line.quantity*line.price_unit
                if type == 'qty':
                    sum += line.quantity
                if type == 'exs_duty':
                    sum += line.quantity*line.price_unit*(line.invoice_id.excise_duty_id and line.invoice_id.excise_duty_id.amount or 0.0)/100                   
            return sum
        
        def convert_date(date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
        
        def get_invoice_type(invoice_type):
            if invoice_type == 'domestic':
                return "Domestic/Indirect Export"
            if invoice_type == 'export':
                return "Export"
        
        def get_order_type(order_type):
            if order_type == 'domestic':
                return "Domestic"
            if order_type == 'export':
                return "Export"
        
        def get_customer_group(customer):
            if customer == 'export':
                return "Export"
            if customer == 'domestic':
                return "Domestic"
            if customer == 'indirect_export':
                return "Indirect Export"
        
        def get_cst_tax(tax, untax):
            amount = 0
            if 'CST' in tax.name:
                amount = tax.amount
                return round(amount*untax/100,2)
    
        def get_vat_tax(tax, untax):
            amount = 0
            if 'VAT' in tax.name:
                amount = tax.amount
                return round(amount*untax/100,2)
    
        def get_tcs_tax(tax, untax):
            amount = 0
            if 'TCS' in tax.name:
                amount = tax.amount
                return round(amount*untax/100,2)
            
        def decimal_convert(amount):       
            decamount = format(amount, '.3f')
            return decamount
            
        def get_invoice(cb):
            res = {}
            product_id = cb.product_id.id
            #print cb.product_id.id
            application_id = cb.application_id.id
            state_id = cb.state_id.id
            customer_id = cb.customer_id.id
            name_consignee_id = cb.name_consignee_id.id
            city = cb.city
            date_from = cb.date_from
            date_to = cb.date_to
            
            invoice_obj = self.pool.get('account.invoice.line')
            invoice_ids = []
            sql = '''
            select il.id from account_invoice_line il
            join account_invoice i on (i.id=il.invoice_id)
            join res_partner p on (p.id=i.partner_id)
            where i.date_invoice between '%s' and '%s' and i.type = 'out_invoice'          
            '''%(date_from, date_to)
            if product_id:
                str = " and il.product_id=%s"%(product_id)
                sql = sql+str
            if application_id:
                str = " and il.application_id=%s"%(application_id)
                sql = sql+str 
            if state_id:
                str = " and p.state_id=%s"%(state_id)
                sql = sql+str
            if customer_id:
                str = " and il.partner_id=%s"%(customer_id)
                sql = sql+str
            if name_consignee_id:
                str = " and i.cons_loca=%s"%(name_consignee_id)
                sql = sql+str
            if city:
                str = " and UPPER(btrim(p.city))=UPPER(btrim('%s'))"%(city)
                sql = sql+str
                
            sql=sql+" order by i.vvt_number"       
        
            cr.execute(sql)
            invoice_ids = [r[0] for r in cr.fetchall()]
            return invoice_obj.browse(cr,uid,invoice_ids)
        
        
        cr.execute('delete from tpt_daily_sale_report')
        cb_obj = self.pool.get('tpt.daily.sale.report')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        for line in get_invoice(cb):
            cb_line.append((0,0,{
                    'vvt_number': line.invoice_id.vvt_number,
                    #'date_invoice':convert_date(line.invoice_id.date_invoice or ''),
                    'date_invoice':line.invoice_id.date_invoice or False,
                    'order_type':get_order_type(line.invoice_id.sale_id and line.invoice_id.sale_id.order_type or ''),
                    #'distribution':line.invoice_id.sale_id and line.invoice_id.sale_id.distribution_channel.name or '',
                    'distribution':line.invoice_id.partner_id and line.invoice_id.partner_id.distribution_channel.name or '',
                    'country':line.invoice_id.partner_id and line.invoice_id.partner_id.country_id.name or '',
                    'state':line.invoice_id.partner_id and line.invoice_id.partner_id.state_id.name or '',
                    'city':line.invoice_id.partner_id and line.invoice_id.partner_id.city or '',
                    'po_number':line.invoice_id.sale_id.po_number,
                    #'po_date':convert_date(line.invoice_id.sale_id and line.invoice_id.sale_id.po_date or ''),
                    'po_date':line.invoice_id.sale_id and line.invoice_id.sale_id.po_date or False,
                    'sales_order':line.invoice_id.sale_id and line.invoice_id.sale_id.name or '',
                    'delivery_order':line.invoice_id.delivery_order_id and line.invoice_id.delivery_order_id.name or '',
                    'product_code':line.product_id and line.product_id.default_code or '',
                    'product_name':line.product_id and line.product_id.name or '',
                    'application_name':line.application_id and line.application_id.name or '',
                    'customer_code':line.invoice_id.partner_id and line.invoice_id.partner_id.customer_code or '',
                    'partner_name':line.invoice_id.partner_id and line.invoice_id.partner_id.name or '',
                    'consignee_code':line.invoice_id.cons_loca and line.invoice_id.cons_loca.customer_code or '',
                    'consignee_name':line.invoice_id.cons_loca and line.invoice_id.cons_loca.name or '',
                    'transporter':line.invoice_id.delivery_order_id.transporter,
                    'lr_no':line.invoice_id.lr_no,
                    'truck':line.invoice_id.delivery_order_id.truck,
                    'booked_to':line.invoice_id.booked_to,
                    'customer_group':get_customer_group(line.invoice_id.partner_id and line.invoice_id.partner_id.arulmani_type or ''),
                    'payment_term':line.invoice_id.payment_term and line.invoice_id.payment_term.name or '',
                    'quantity': decimal_convert(line.quantity) or 0.000, #YuVi                    
                    'price_unit':line.price_unit or '',
                    'uom':line.uos_id and line.uos_id.name or '',
                    'basic_price':line.quantity*line.price_unit or 0.00,
                    'excise_duty':round(line.quantity*line.price_unit*(line.invoice_id.excise_duty_id and line.invoice_id.excise_duty_id.amount or 0.0)/100,2),
                    'cst_tax':get_cst_tax(line.invoice_id.sale_tax_id, line.invoice_id.amount_untaxed) or 0.00,
                    'vat_tax':get_vat_tax(line.invoice_id.sale_tax_id, line.invoice_id.amount_untaxed) or 0.00,
                    'tcs_tax':get_tcs_tax(line.invoice_id.sale_tax_id, line.invoice_id.amount_untaxed) or 0.00,
                    'freight':(line.freight * line.quantity) or 0.00,
                    'insurance':line.invoice_id.insurance or 0.00,
                    'other_charges':line.invoice_id.other_charges or 0.00,
                    'currency':line.invoice_id.currency_id and line.invoice_id.currency_id.name or '',
                    'total_amt':line.invoice_id.amount_total_inr or 0.00,
                    'other_reasons':line.invoice_id.other_info or '',
            }))
            
        cb_line.append((0,0,{
            'currency': 'Total',
            'uom': 'Total Basic Price',
            'payment_term': 'Total Quantity',
            'total_amt': round(get_total(get_invoice(cb),'total_amt'),0) or 0.00,
            'basic_price': round(get_total(get_invoice(cb),'total_basic_amt'),0) or 0.00,
            'quantity': get_total(get_invoice(cb),'qty') or 0.000, #exs_duty
            'excise_duty' : round(get_total(get_invoice(cb),'exs_duty'),0) or 0.000,
        }))
        
        vals = {
            'name': 'Daily Sale Report',
            'product_title': 'Material : ', 
            'application_title': 'Application : ', 
            'state_title': 'Region : ', 
            'city_title': 'City : ', 
            'customer_title': 'Customer : ', 
            'consignee_title': 'Consignee : ',
            'date_from_title': 'Date From : ', 
            'date_to_title': 'Date To : ',
            'product_id': cb.product_id.id,
            'application_id': cb.application_id.id,
            'state_id': cb.state_id.id,
            'customer_id': cb.customer_id.id,
            'name_consignee_id': cb.name_consignee_id.id,
            'city': cb.city,
            'date_from': cb.date_from,
            'date_to': cb.date_to,
            'daily_sale_line': cb_line,
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_daily_sale_report')
        return {
                    'name': 'Daily Sale Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.daily.sale.report',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                }
        
daily_sale_form()