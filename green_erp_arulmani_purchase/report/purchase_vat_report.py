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
import math

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

""" 
TPT - By P.Vinothkumar  - on 19/01/2016
Purchase VAT Report : Display the Purchase VAT values for the selected date range
"""

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
          'get_date_from':self.get_date_from,
          'get_date_to':self.get_date_to, 
          'get_vat':self.get_vat, 
         'convert_date':self.convert_date,
        })
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
        return date.strftime('%d/%m/%Y')
    
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y') 
    
    def get_vat(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql='''
            select a.supplier, a.tinno, a.commoditycode, a.invoiceno, a.invoicedate, a.rate,
            sum(a.ed+a.pf+a.basicamt) as purchase_value,
            sum(a.ed+a.pf+a.basicamt*a.amount/100) as vat_paid, a.poname,
           'B' as category
            from
            (select 
            rp.vendor_code||'-'||rp.name as supplier,
            rp.tin as tinno,
            at.description as rate,
            pc.name,
            pl.product_qty,
            p.name as poname,
            pl.price_unit,
            ai.bill_number as invoiceno,
            ai.bill_date as invoicedate,
            case 
            when pc.name='Spares' then 2025
            when pc.name='Consumables' then 2025
            when pc.name='Assets' then 2025
            else 2067 end as commoditycode,
            case 
            when ed_type='1' then (pl.product_qty * pl.price_unit) * ed/100
            when ed_type='2' then ed
            when ed_type='3' then (pl.product_qty * pl.ed)
            else ed end as ed,
            case 
            when p_f_type='1' then (pl.product_qty * pl.price_unit) * p_f/100
            when p_f_type='2' then p_f
            when p_f_type='3' then (pl.product_qty * pl.p_f)
            else p_f end as pf,
            at.amount,
            pl.price_unit as priceunit,
            pl.product_qty as productqty,
            pl.ed_type as ed1,
            pl.p_f_type as pf1,
            (pl.price_unit * pl.product_qty)-(pl.price_unit * pl.product_qty * discount/100) as basicamt
            from purchase_order_line pl
            join purchase_order p on p.id=pl.order_id 
            join account_invoice ai on ai.purchase_id=p.id
            join res_partner rp on rp.id=p.partner_id
            join product_product pr on pr.id=pl.product_id
            join product_category pc on pc.cate_name=pr.cate_name
            join purchase_order_taxe pot on pl.id=pot.ord_id
            join account_tax at on pot.tax_id=at.id
            where p.date_order::date between '%s' and '%s' and p.state='done' 
            and at.is_vat_report=true)a group by a.Rate,a.supplier,a.tinno,a.commoditycode,
            a.invoiceno,a.invoicedate,a.poname order by a.supplier

        '''%(date_from, date_to)
        self.cr.execute(sql);
        res = []
        s_no = 1
        for line in self.cr.dictfetchall():
             res.append({
                        's_no':s_no,
                        'supplier': line['supplier'] or '',
                        'tinno': line['tinno'] or '',
                        'commoditycode': line['commoditycode'] or '',
                        'invoiceno': line['invoiceno'] or '',
                        'invoicedate': line['invoicedate'] or '',  
                        'rate': line['rate'] or '', 
                        'purchase_value': line['purchase_value'] or '', 
                        'vat_paid': line['vat_paid'] or '',
                        'category': line['category'] or '',
                                         
                        })
             s_no += 1
        return res  
    