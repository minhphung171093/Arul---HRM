# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class tpt_input_register(osv.osv_memory): 
    _name = "tpt.input.register"
    _columns = {
                'name': fields.char('Input Register Report', size = 1024),
                'date_from': fields.date('Posting Date From', required=True), #YuVi
                'date_to': fields.date('To', required=True), #YuVi
                'product_cate_id':fields.many2one('product.category', 'Product Category'),
                'date_from_title': fields.char('', size = 1024), #YuVi
                'date_to_title': fields.char('', size = 1024), #YuVi
                'input_line': fields.one2many('tpt.input.register.line', 'input_id', 'Input Register Line'),
                }
   
    def print_xls(self, cr, uid, ids, context=None):
       if context is None:
            context = {}
       datas = {'ids': context.get('active_ids', [])}
       datas['model'] = 'tpt.input.register'
       datas['form'] = self.read(cr, uid, ids)[0]
       datas['form'].update({'active_id':context.get('active_ids',False)})
       return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_input_register_report_xlf', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
       if context is None:
                context = {}
       datas = {'ids': context.get('active_ids', [])}
       datas['model'] = 'tpt.input.register'
       datas['form'] = self.read(cr, uid, ids)[0]
       datas['form'].update({'active_id':context.get('active_ids',False)})
       return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_input_register_report_pdf', 'datas': datas}
   
    
tpt_input_register()

class tpt_input_register_line(osv.osv_memory):
    _name = "tpt.input.register.line"
    _columns = {
        'input_id': fields.many2one('tpt.input.register', 'Input Register', ondelete='cascade'),
        'doc_type': fields.char('Invoice Type', size = 1024), # YuVi
        'doc_no': fields.char('Document No', size = 1024),
        'inv_ex_date': fields.date('Excise Invoice Date' ),
        'supplier':fields.char('Name of The Supplier',size = 1024),
        'supplier_type':fields.char('Type of Supplier',size = 1024),        
        'date_rcvd':fields.date('Date On Which Inputs were Received'),
        'sup_ec_no':fields.char('Suppliers ECC Number',size = 1024),
        'Value': fields.float('Value'),
        'Cenvat': fields.float('Cenvat'),
        'desc': fields.char('Description Of Main Item in the document',size = 1024),
        'cha_id': fields.char('Chapter Id of Main Item In the Document',size = 1024),
        'qty': fields.char('Quantity',size = 1024),
        'uom': fields.char('Unit Of Measure',size = 1024),
         #'uom': fields.char('Unit Of Measure',size = 1024),
        'billno': fields.char('Bill no',size = 1024),
        'billdate': fields.date('Bill Date'),
        'postdate': fields.date('Posting Date',size = 1024),
        #'total' : fields.float('Total'),                
         
    }

tpt_input_register_line()


class input_register_form(osv.osv_memory):
    _name = "input.register.form"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'product_cate_id':fields.many2one('product.category', 'Product Category', required=True),
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
        
        def convert_date(date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
        
        #YuVi_2
        def decimal_convert(amount):       
            decamount = format(amount, '.3f')
            return decamount
        #YuVi
            
        def get_grn_date(inv_id):
            print inv_id           
            sql = '''
                  select date from stock_picking where id in (select grn_no from account_invoice where id = %s)
                  '''%(inv_id)
            cr.execute(sql)
            grndate = cr.fetchone()
            date = datetime.strptime(str(grndate[0]), DATETIME_FORMAT)
            temp=date.strftime('%Y/%m/%d/')
            return temp
        
        def get_total(value):
            sum = 0.00
            for line in value:
                sum += line.quantity*line.price_unit   
            return sum
        
        def get_document_type(document_type):
            if document_type == 'raw':
                return "VV Raw material PO"
            if document_type == 'asset':
                return "VV Capital PO"
            if document_type == 'standard':
                return "VV Standard PO"
            if document_type == 'return':
                return "VV Return PO"
            if document_type == 'service':
                return "VV Service PO"
            if document_type == 'out':
                return "VV Out Service PO"
            
        def get_total(value):
            #print value
            sum = 0.0
            for line in value:
                sum += line.quantity*line.price_unit   
            return sum
        
        def get_cate_type():
            type = sls.product_cate_id.id         
            #pro_cat_obj = self.pool.get('product.category')
            #category = pro_cat_obj.browse(cr,uid,type[0])
            if type == 3:
                return "Monthly Return Cenvat on Input"
            if type == 5:
                return "Monthly Return Cenvat on Capital Goods"
        
        def get_invoice(sls):
            res = {}            
            date_from = sls.date_from
            date_to = sls.date_to
            product_cate_id = sls.product_cate_id.id
            #wizard_data = self.localcontext['data']['form']
            #date_from = wizard_data['date_from']
            #date_to = wizard_data['date_to']
            #product_cate_id = wizard_data['product_cate_id']
            invoice_obj = self.pool.get('account.invoice.line')
            invoice_ids = []
            if product_cate_id:
                sql = '''
                    select id from account_invoice_line where invoice_id in 
                    (select id from account_invoice where date_invoice between '%s' and '%s' and type = 'in_invoice' and purchase_id is not null) 
                    and ed is not null and ed != 0
                    and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where categ_id = %s))
                    '''%(date_from, date_to, product_cate_id)
                cr.execute(sql)
                invoice_ids = [r[0] for r in cr.fetchall()]
            else:
                sql = '''
                    select id from account_invoice_line where invoice_id in 
                    (select id from account_invoice where date_invoice between '%s' and '%s' and type = 'in_invoice' and purchase_id is not null) 
                    and ed is not null and ed != 0
                    and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where categ_id in (select id from product_category where cate_name in ('raw','spares'))))
                    '''%(date_from, date_to)
                cr.execute(sql)
                invoice_ids = [r[0] for r in cr.fetchall()]
            return invoice_obj.browse(cr,uid,invoice_ids)
        
        cr.execute('delete from tpt_input_register')
        sls_obj = self.pool.get('tpt.input.register')
        sls = self.browse(cr, uid, ids[0])
        sls_line = []
        for line in get_invoice(sls):
            sls_line.append((0,0,{                              
                'doc_type': get_document_type(line.invoice_id.purchase_id and line.invoice_id.purchase_id.po_document_type) or '',
                'doc_no':line.invoice_id.name or '',
                'inv_ex_date': line.invoice_id and line.invoice_id.date_invoice or False,
                'supplier': line.invoice_id.partner_id and line.invoice_id.partner_id.name or '',
                'supplier_type': line.invoice_id.partner_id and line.invoice_id.partner_id.vendor_type or '',
                'date_rcvd': get_grn_date(line.invoice_id.id) or False,
                'sup_ec_no': line.invoice_id.partner_id and line.invoice_id.partner_id.ecc or '',
                'Value': (line.quantity*line.price_unit) or 0.00,
                'Cenvat': line.invoice_id.excise_duty or 0.00,
                'desc':line.product_id and line.product_id.name_template or '',
                'cha_id': line.product_id and line.product_id.chapter or '',
                'qty': decimal_convert(line.quantity) or 0.000, #YuVi_2
                'uom': line.uos_id and line.uos_id.name or '',
                'billno': line.invoice_id.bill_number,
                'billdate': line.invoice_id.bill_date or False,
                'postdate': line.invoice_id and line.invoice_id.date_invoice or False,                 
            }))
        sls_line.append((0,0,{
            'sup_ec_no': 'Total',
            'Value': round(get_total(get_invoice(sls)),2) or 0.00,
            
        }))
        vals = {
                #'name': 'Input Register Report',
                'name': get_cate_type(),
                'date_from_title': 'Date From: ', #YuVi
                'date_to_title': 'Date To: ', #YuVi
                'date_from': sls.date_from,
                'date_to' : sls.date_to,
                'product_cate_id': sls.product_cate_id.id,
                'input_line': sls_line, 
            }
        sls_id = sls_obj.create(cr,uid,vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_input_register')
        return {
                        'name': 'Input Register Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'tpt.input.register',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': sls_id,
                    }
        
       
        #=======================================================================
        # if context is None:
        #     context = {}
        # datas = {'ids': context.get('active_ids', [])}
        # datas['model'] = 'input.register.form'
        # datas['form'] = self.read(cr, uid, ids)[0]
        # datas['form'].update({'active_id':context.get('active_ids',False)})
        # return {'type': 'ir.actions.report.xml', 'report_name': 'input_register_report', 'datas': datas}
        #=======================================================================
       
        
input_register_form()