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
TPT - By P.Vinothkumar  - on 22/01/2016
Purchase CST Report : Display the Purchase CST values for the selected date range
"""

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
          'get_date_from':self.get_date_from,
          'get_date_to':self.get_date_to, 
          'get_cst':self.get_cst, 
          'get_total':self.get_total,
          'get_csttotal':self.get_csttotal,
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
    
    def get_total(self):
        sum = 0.00
        for line in self.get_cst():
           sum += line['purchase_value']
        return sum
    
    def get_csttotal(self):
        sum = 0.00
        for line in self.get_cst():
           sum += line['cst_paid']
        return sum
    
    def get_cst(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql='''
            select a.supplier, a.tinno, a.commoditycode, a.invoiceno, a.invoicedate, a.rate descriptions,
            sum(a.ed+a.pf+a.aed+a.basicamt+a.tpt_tax_amt) as totalvalue,a.rate,
            sum(a.ed+a.pf+a.aed+a.basicamt+a.tpt_tax_amt) as purchase_value,
            sum(a.tpt_tax_amt) as cst_paid, a.poname,a.number, 
           'B' as category, a.type, a.city, a.po_no, a.po_date
            from
            (select 
            rp.name as supplier, rp.city, po.name po_no,po.date_order po_date,
            rp.tin as tinno,
            t.description as rate,
            pc.name,
            t.amount,
            ail.quantity,
            ai.name as poname,
            ail.price_unit,
            ai.doc_type,
            ai.number,
            ai.state,
            ai.bill_number as invoiceno,
            ai.bill_date as invoicedate,
            ai.date_invoice,
            case 
            when pc.name='Spares' then 2025
            when pc.name='Consumables' then 2025
            when pc.name='Assets' then 2025
            else 2067 end as commoditycode,
            case 
            when ail.ed_type='1' then (ail.quantity * ail.price_unit) * ail.ed/100
            when ail.ed_type='2' then ail.ed
            when ail.ed_type='3' then (ail.quantity * ail.ed)
            else ail.ed end as ed,
            case 
            when ail.p_f_type='1' then (ail.quantity * ail.price_unit) * ail.p_f/100
            when ail.p_f_type='2' then ail.p_f
            when ail.p_f_type='3' then (ail.quantity * ail.p_f)
            else ail.p_f end as pf,
            ail.price_unit as priceunit,
            ail.quantity as productqty,
            ail.ed_type as ed1,
            ail.p_f_type as pf1,
            ail.tpt_tax_amt,
            case when ail.aed_id_1 is null then 0 else ail.aed_id_1 end as aed,
            (ail.price_unit * ail.quantity)-(ail.price_unit * ail.quantity * ail.discount/100) as basicamt,
            cast('dr' as text) as type
            from 
            account_invoice ai
            join account_invoice_line ail on ai.id=ail.invoice_id
            join res_partner rp on rp.id=ai.partner_id
            join product_product pr on pr.id=ail.product_id
            join product_category pc on pc.cate_name=pr.cate_name
            join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            join account_tax t on t.id=ailt.tax_id
            join purchase_order po on ai.purchase_id=po.id
            where
             ai.date_invoice::date between '%s' and '%s' and
             ai.state not in ('draft', 'cancel') and
            ai.doc_type not in('freight_invoice')
            and t.description like 'CST%s(P)%s' --t.is_vat_report=true
            )a group by a.Rate,a.supplier,a.tinno,a.commoditycode,a.amount,
            a.invoiceno,a.invoicedate,a.poname,a.date_invoice,a.number,a.type, a.city, a.po_no,
            a.po_date order by a.supplier
          
        '''%(date_from, date_to, '%', '%')
        self.cr.execute(sql);
        res = self.cr.dictfetchall()
        #print sql
        sql = '''
            select av.number as number, av.date date_invoice, av.reference bill_number, null bill_date, null tax_name,
                    rs.name supplier, rs.tin tinno,null invoicetype,null material,null number,null city,
                    null productname, 0 vatbased_qty,0 as vatbased_amt,av.tpt_amount_total as salesvalue,null po_no,null po_date,
                    avl.amount as cst_paid, 0 as paid_amt,
                    null as city, null uom, null as grn, null as number,null as rate, null as name, 
                    null commoditycode, null ed,null pf, null priceunit,
                    null productqty,av.reference as invoiceno, av.date invoicedate,'0000219607 GL' as rate,null totalvalue, null descriptions,
            av.tpt_amount_total-avl.amount as purchase_value,
            --null as vat_paid, 
            null as poname, avl.type as type,
           'J' as category
            from account_voucher_line avl
            inner join account_voucher av on avl.voucher_id=av.id
            inner join account_account aa on avl.account_id=aa.id
            inner join account_move am on av.move_id=am.id
            inner join res_partner rs on av.partner_id=rs.id
            where 
            av.date between '%s' and '%s' and 
            aa.code='0000219607'
        '''%(date_from, date_to)
        self.cr.execute(sql)
        #print sql
        res1 = self.cr.dictfetchall()
        if res1:
            res = res+res1            
        res_set = []
        s_no = 1
        for line in res:
             res_set.append({
                        's_no':s_no,
                        'supplier': line['supplier'] or '',
                        'city':line['city'] or '',
                        'tinno': line['tinno'] or '',
                        'commoditycode': line['commoditycode'] or '',
                        'invoiceno': line['invoiceno'] or '',
                        'invoicedate': line['invoicedate'] or '',
                        'po_no': line['po_no'] or '',
                        'po_date': line['po_date'] or '', 
                        'purchase_value': line['purchase_value'] or 0.00, 
                        'rate': line['rate'] or '', 
                        #'cst_paid': line['cst_paid'] or 0.00,
                        'cst_paid': -line['cst_paid'] if line['type'] == 'cr' else line['cst_paid'] or 0.00,
                        'totalvalue': line['totalvalue'] or '',
                        'category': line['category'] or '',
                        'descriptions': line['descriptions'] or '', 
                        'number': line['number'] or '',                
                        })
             s_no += 1
        return res_set 
    