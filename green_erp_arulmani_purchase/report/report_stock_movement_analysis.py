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
                'get_date_from':self.get_date_from,
                'get_date_to':self.get_date_to,
                'get_category':self.get_category,
                'get_product':self.get_product,
                'get_name_product':self.get_name_product,
                'get_categ':self.get_categ,
#               'get_categ_product':self.get_categ_product
              
              
              
        })
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')    
    
    def get_category(self):
        wizard_data = self.localcontext['data']['form']
        cate = (wizard_data['categ_id'])
        cate_obj = self.pool.get('product.category')
        return cate_obj.browse(self.cr,self.uid,cus[0])    
    
    def get_product(self):
        wizard_data = self.localcontext['data']['form']
        pro = (wizard_data['product_id'])
        pro_obj = self.pool.get('product.product')
        return pro_obj.browse(self.cr,self.uid,cus[0])  
    
    def get_name_product(self, product):
        if product == 'raw':
            return "Raw Materials"
        if product == 'spares':
            return "Spares"
    
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date(self):
        date = time.strftime('%Y-%m-%d'),
        date = datetime.strptime(date[0], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_warehouse(self):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        loc_obj = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        return loc_obj   
    
    def get_category(self):
        wizard_data = self.localcontext['data']['form']
        cat = wizard_data['categ_id']
        if cat:
            cat_obj = self.pool.get('product.category').browse(self.cr,self.uid,cat[0])
            return cat_obj
        return False
    
    def get_product(self):
        wizard_data = self.localcontext['data']['form']
        pro = wizard_data['product_id']
        if pro:
            pro_obj = self.pool.get('product.product').browse(self.cr,self.uid,pro[0])
            return pro_obj
        return False

    def get_categ(self):
        wizard_data = self.localcontext['data']['form']
        categ = wizard_data['categ_id']
        product = wizard_data['product_id']
        pro_obj = self.pool.get('product.product')
        categ_ids = []

        if categ and product:
            sql='''
                        select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                        and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
            '''%(categ[0],product[0])
            self.cr.execute(sql)
            categ_ids += [r[0] for r in self.cr.fetchall()]
            return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
        if categ:
            sql='''
                        select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                        and product_product.product_tmpl_id = product_template.id;
            '''%(categ[0])
            self.cr.execute(sql)
            categ_ids += [r[0] for r in self.cr.fetchall()]
            return pro_obj.browse(self.cr,self.uid,categ_ids)
#         if product and not categ:
#             sql='''
#                         select product_product.id 
#                         from product_product,product_template 
#                         where product_template.categ_id in(select product_category.id from product_category) 
#                         and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
#             '''%(product[0])
#             self.cr.execute(sql)
#             categ_ids += [r[0] for r in self.cr.fetchall()]
#             return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
#         if not product and not categ :
#             sql='''
#                         select product_product.id 
#                         from product_product,product_template 
#                         where product_template.categ_id in(select product_category.id from product_category) 
#                         and product_product.product_tmpl_id = product_template.id  ;
#             '''
#             self.cr.execute(sql)
#             categ_ids += [r[0] for r in self.cr.fetchall()]
#             return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
        
    def get_ton_sl(self, line):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        location = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id = %s and st.location_id = %s
                            )foo
                    '''%(line.id,location.id,line.id,location.id)
        self.cr.execute(sql)
        ton_sl = self.cr.dictfetchone()
        return ton_sl and ton_sl['ton_sl'] or 0
    
    def get_ins_qty(self, line):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        location = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Quality Inspection'),('usage','=','view')])
        locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Inspection']),('location_id','=',parent_ids[0])])
        sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id = %s and st.location_id = %s
                            )foo
                    '''%(line.id,locat_ids[0],line.id,locat_ids[0])
        self.cr.execute(sql)
        ton = self.cr.dictfetchone()
        return ton and ton['ton'] or 0
    def get_blo_qty(self, line):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        location = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
        locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_ids[0])])
        sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id = %s and st.location_id = %s
                            )foo
                    '''%(line.id,locat_ids[0],line.id,locat_ids[0])
        self.cr.execute(sql)
        ton = self.cr.dictfetchone()
        return ton and ton['ton'] or 0        

        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

