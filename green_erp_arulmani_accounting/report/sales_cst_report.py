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
TPT - By P.Vinothkumar  - on 29/01/2016
Sales CST Report : Display the Sales CST values for the selected date range
"""

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
          'get_date_from':self.get_date_from,
          'get_date_to':self.get_date_to, 
          'get_sales_cst':self.get_sales_cst, 
          'convert_date':self.convert_date,
          'get_total':self.get_total,          # Added  on 10/02/2016 by P.VINOTHKUMAR
          'get_csttotal':self.get_csttotal     # Added  on 10/02/2016 by P.VINOTHKUMAR
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
   # The following method is added on 10/02/2016 by P.VINOTHKUMAR 
    def get_total(self):
        sum = 0.00
        for line in self.get_sales_cst():
           sum += line['salesvalue']
        return sum
   # The following method is added on 10/02/2016 by P.VINOTHKUMAR 
    def get_csttotal(self):
        sum = 0.00
        for line in self.get_sales_cst():
           sum += line['cst_paid']
        return sum
     #  Query modified on 10/02/2016 by P.VINOTHKUMAR      
    def get_sales_cst(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        cst_paid=0.0
        sql='''  
                    select
                    rp.name as customer,
                    rp.tin as tinno,
                    case
                    when pc.name='FinishedProduct' then '2001'
                    else '-' end as commoditycode,
                    ai.vvt_number as invoiceno,
                    ai.date_invoice as invoicedate,
                    'F' as category,
                    case
                        when at.description='CST 2%s  (S)' then 'CST 2'
                        when at.description='CST 1%s (S)' then 'CST 1'
                        when at.description='CST 4%s (S)' then 'CST 4'
                        when at.description='CST 0%s  (S) - Indirect Export' then 'CST 0'
                        when at.description='CST 0%s (S) - Domestic' then 'CST 0'
                        else 'cst' end as rate,
                    s.amount_untaxed as salesvalue,
                    case when coalesce(s.amount_tax,0)=0 then 0 else s.amount_tax end as cst_paid
                    from sale_order_line sl
                    join sale_order s on s.id=sl.order_id
                    join account_invoice ai on ai.sale_id=s.id
                    join res_partner rp on rp.id=s.partner_id
                    join product_product pr on pr.id=sl.product_id
                    join product_category pc on pc.cate_name=pr.cate_name
                    join account_tax at on s.sale_tax_id=at.id
                    where ai.date_invoice::date between '%s' and '%s' and s.state='done'
                    and at.description like 'CST%s(S)' order by customer
        '''%('%','%','%','%','%',date_from, date_to,'%')
        self.cr.execute(sql)
        res = []
        s_no = 1
        for line in self.cr.dictfetchall():
             res.append({
                        's_no':s_no,
                        'customer': line['customer'] or '',
                        'tinno': line['tinno'] or '',
                        'commoditycode': line['commoditycode'] or '',
                        'invoiceno': line['invoiceno'] or '',
                        'invoicedate': line['invoicedate'] or '',
                        'salesvalue': line['salesvalue'] or '', 
                        'rate': line['rate'] or '', 
                        'category': line['category'] or '', #  Added this line on 10/02/2016 by P.VINOTHKUMAR  
                        'cst_paid': line['cst_paid'] or 0.00,               
                        })
             s_no += 1
        return res 
    

    
