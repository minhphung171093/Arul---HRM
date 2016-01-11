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
            'convert_date':self.convert_date,
            'convert_date_time':self.convert_date_time,
            'get_month_name': self.get_month_name,                     
            'get_month':self.get_month,
            'get_year':self.get_year,
            'get_po':self.get_po,
            'get_categ':self.get_categ,
            
        })
            
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def convert_date_time(self,date):
        if date:
            date = datetime.strptime(date, DATETIME_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_month_name(self, month):
       month = int(month)
       _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
       d = _months[month]
       return d
        
    def get_month(self):
        wizard_data = self.localcontext['data']['form']
        return self.get_month_name(wizard_data['month'])
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['year'] 
    
    def get_categ(self):
        wizard_data = self.localcontext['data']['form']
        categ_id=wizard_data['categ_id']
        prd_categ_obj = self.pool.get('product.category') 
        cate_name = ''
        if categ_id:
          prd_categ_ids = prd_categ_obj.browse(self.cr,self.uid,categ_id[0])  
          cate_name = prd_categ_ids.name
        return cate_name
    
        
    def get_po(self):
        wizard_data = self.localcontext['data']['form']
        month=wizard_data['month']
        year=wizard_data['year'] 
        categ_id=wizard_data['categ_id']
        prd_categ_obj = self.pool.get('product.category') 
        
        
        sql = '''
        select p.date_order::date as po_date,
                    p.name as PO_No,
                    b.name as Vendor_Name,
                    case when pr.name_template='-' then pr.default_code else pr.name_template end as Materials,
                    pc.name as materialtype,
                    pl.product_qty as Qty,
                    uom.name as UOM,
                    pl.line_net as Net_Value
                    from
                    purchase_order_line pl
                    join purchase_order p on p.id=pl.order_id 
                    join res_partner b on b.id=p.partner_id  
                    join product_product pr on pr.id=pl.product_id
                    join product_uom uom on uom.id=pl.product_uom
                    join product_category pc on pc.cate_name=pr.cate_name
                    where pl.line_net>=1000000 and p.state='done' 
                    and EXTRACT(month FROM p.date_order)='%s' 
                    and EXTRACT(year FROM p.date_order)='%s' 
        '''%(int(month),int(year))
        if categ_id:
            prd_categ_ids = prd_categ_obj.browse(self.cr,self.uid,categ_id[0])
            cate_name = prd_categ_ids.cate_name
            sql += " and pc.cate_name='%s'"%cate_name
        sql += " order by PO_Date"   
        
        
        
        print sql                        
        self.cr.execute(sql);
        res = []
        s_no = 1
        for line in self.cr.dictfetchall():            
            res.append({
                        's_no':s_no,
                        'po_date': line['po_date'] or '',
                        'po_no': line['po_no'] or '',
                        'vendor_name': line['vendor_name'] or '',
                        'materials': line['materials'] or '',
                        'qty': line['qty'] or '',  
                        'uom': line['uom'] or '', 
                        'net_value': line['net_value'] or '',                  
                        })
            s_no += 1
        return res  
    
  
        #return self.cr.dictfetchall()
        
        
        
        
        
        
        
        
        
        
    