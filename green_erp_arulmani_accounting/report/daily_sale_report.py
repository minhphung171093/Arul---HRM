# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_invoice':self.get_invoice,
            'get_invoice_type':self.get_invoice_type,
            'get_customer_group': self.get_customer_group,
            'get_cst_tax': self.get_cst_tax,
            'get_vat_tax': self.get_vat_tax,
            'get_tcs_tax': self.get_tcs_tax,
            'get_order_type': self.get_order_type,
            'convert_date': self.convert_date,
#             'get_sale_line': self.get_sale_line,
        })
        
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date(self):
        res = {}
        date = time.strftime('%Y-%m-%d'),
        date = datetime.strptime(date[0], DATE_FORMAT)
        day = date.day
        month = date.month
        year = date.year
        res = {
               'day': day,
               'month': month,
               'year': year,
               }
        return res
        
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        application_id = wizard_data['application_id']
        state_id = wizard_data['state_id']
        customer_id = wizard_data['customer_id']
        city = wizard_data['city']
        name_consignee_id = wizard_data['name_consignee_id']
        
        invoice_obj = self.pool.get('account.invoice.line')
        sql = '''
            select il.id from account_invoice_line il
            join account_invoice i on (i.id=il.invoice_id)
            join res_partner p on (p.id=i.partner_id)
            where i.date_invoice between '%s' and '%s' and i.type = 'out_invoice'          
            '''%(date_from, date_to)
        if product_id:
           str = " and il.product_id=%s"%(product_id[0])
           sql = sql+str
        if application_id:
           str = " and il.application_id=%s"%(application_id[0])
           sql = sql+str 
        if state_id:
           str = " and p.state_id=%s"%(state_id[0])
           sql = sql+str
        if customer_id:
           str = " and il.partner_id=%s"%(customer_id[0])
           sql = sql+str
        if name_consignee_id:
           str = " and i.cons_loca=%s"%(name_consignee_id[0])
           sql = sql+str
        if city:
           str = " and UPPER(btrim(p.city))=UPPER(btrim('%s'))"%(city)
           sql = sql+str
        sql=sql+" order by i.vvt_number"
        
        self.cr.execute(sql)
        invoice_ids = [r[0] for r in self.cr.fetchall()]
        return invoice_obj.browse(self.cr,self.uid,invoice_ids)
    
    def get_invoice_type(self, invoice_type):
        if invoice_type == 'domestic':
            return "Domestic/Indirect Export"
        if invoice_type == 'export':
            return "Export"
        
    def get_order_type(self, order_type):
        if order_type == 'domestic':
            return "Domestic"
        if order_type == 'export':
            return "Export"
        
    def get_customer_group(self, customer):
        if customer == 'export':
            return "Export"
        if customer == 'domestic':
            return "Domestic"
        if customer == 'indirect_export':
            return "Indirect Export"
        
    def get_cst_tax(self, tax, untax):
        amount = 0
        if 'CST' in tax.name:
            amount = tax.amount
        return round(amount*untax/100,2)
    
    def get_vat_tax(self, tax, untax):
        amount = 0
        if 'VAT' in tax.name:
            amount = tax.amount
        return round(amount*untax/100,2)
    
    def get_tcs_tax(self, tax, untax):
        amount = 0
        if 'TCS' in tax.name:
            amount = tax.amount
        return round(amount*untax/100,2)
        
    
#     def get_sale_line(self,invoice):
#         line = invoice[0]
#         order_lines = line.invoice_id.sale_id.order_line
#             
#         return self.pool.get('sale.order.line').browse(self.cr,self.uid,order_lines[0])
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

