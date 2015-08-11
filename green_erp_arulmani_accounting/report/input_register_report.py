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
            'convert_date':self.convert_date,
            'get_date_from': self.get_date_from,
            'get_date_to': self.get_date_to,
            'get_document_type': self.get_document_type,
            'get_cate_type':self.get_cate_type, # YuVi
            'get_grn_date':self.get_grn_date, # YuVi
             #'convert_datetime':self.convert_datetime, #YuVi
            'get_total':self.get_total, #YuVi
        })
        
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
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
        product_cate_id = wizard_data['product_cate_id']
        invoice_obj = self.pool.get('account.invoice.line')
        invoice_ids = []
        if product_cate_id:
            sql = '''
                select id from account_invoice_line where invoice_id in 
                (select id from account_invoice where date_invoice between '%s' and '%s' and type = 'in_invoice' and purchase_id is not null) 
                and ed is not null and ed != 0
                and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where categ_id = %s))
                '''%(date_from, date_to, product_cate_id[0])
            self.cr.execute(sql)
            invoice_ids = [r[0] for r in self.cr.fetchall()]
        else:
            sql = '''
                select id from account_invoice_line where invoice_id in 
                (select id from account_invoice where date_invoice between '%s' and '%s' and type = 'in_invoice' and purchase_id is not null) 
                and ed is not null and ed != 0
                and product_id in (select id from product_product where product_tmpl_id in (select id from product_template where categ_id in (select id from product_category where cate_name in ('raw','spares'))))
                '''%(date_from, date_to)
            self.cr.execute(sql)
            invoice_ids = [r[0] for r in self.cr.fetchall()]
        return invoice_obj.browse(self.cr,self.uid,invoice_ids)
    
    def get_document_type(self, document_type):
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
        
    #YuVi
    def get_cate_type(self):
        wizard_data = self.localcontext['data']['form']
        type = wizard_data['product_cate_id']
        pro_cat_obj = self.pool.get('product.category')
        category = pro_cat_obj.browse(self.cr,self.uid,type[0])
                
        if category.id == 3:
            return "Monthly Return Cenvat on Input"
        if category.id == 5:
            return "Monthly Return Cenvat on Capital Goods"
        
        
    def get_grn_date(self, inv_id):
        self.cr.execute('''select date from stock_picking where id in (select grn_no from account_invoice where id = %s)''', (inv_id.id,))
        grndate = self.cr.fetchone()         
        date = datetime.strptime(str(grndate[0]), DATETIME_FORMAT)
        temp=date.strftime('%d/%m/%Y')
        #return grndate and grndate[0] or ''
        return temp
    
#     def convert_datetime(self,date):
#         #datercvd = '%Y%m%d'
#         if date:
#             #date = datetime.strptime(date, DATETIME_FORMAT)
#             date = datetime.strptime(date, DATETIME_FORMAT)
#             year = new.date_from[5:7]
#             month = new.date_from[3:4]
#             day = new.date_from[:2]
#             
#             #chop = len(date.split()[-1]) - 4
#             #date = date[:-chop]
#             
#             #===================================================================
#             # datercvd = datetime(
#             #                   year=date.year, 
#             #                   month=date.month,
#             #                   day=date.day,
#             #                   )
#             #===================================================================
#             datercvd = date.strptime(date.strftime('%d/%m/%Y'))
#             #datetime.strptime(date.strftime('%Y%m%d'), '%Y%m%d')
#             return datercvd
        
    def get_total(self, value):
        sum = 0.0
        for line in value:
            sum += line.quantity*line.price_unit   
        return sum
    
     
       
    
        
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

