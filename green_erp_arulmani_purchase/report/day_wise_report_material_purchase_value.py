# -*- coding: utf-8 -*-
##############################################################################
#
#    Tenth Planet Technologies
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
from green_erp_arulmani_purchase.report.amount_to_text_indian import Number2Words
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from green_erp_arulmani_purchase.report import amount_to_text_en

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.year = False
        self.month = False
        self.day_value = []
        self.num = False
        self.localcontext.update({
            'get_category':self.get_category,
            'get_average':self.get_average,
            'get_year':self.get_year,
            'get_material':self.get_material,  
            'get_line':self.get_line, 
            'get_value':self.get_value, 
            'length_month':self.length_month, 
            'get_day_column':self.get_day_column,  
            'get_avg':self.get_avg,
                                  
        })
        
    def get_category(self):
        wizard_data = self.localcontext['data']['form']
        cat = wizard_data['material_cate']
        if cat:
            cat_id = self.pool.get('product.category').browse(self.cr,self.uid,cat[0])
            if cat_id.cate_name == 'raw':
                return "Raw Materials"
            if cat_id.cate_name == 'spares':
                return "Spares"
            if cat_id.cate_name == 'finish':
                return "Finished Product"
            if cat_id.cate_name == 'consum':
                return "Consumables"
            if cat_id.cate_name == 'assets':
                return "Assets"
            if cat_id.cate_name == 'service':
                return "Services"
        return True
    
    def get_average(self):
        wizard_data = self.localcontext['data']['form']
        avg = wizard_data['avg_value']
        if avg:
            if avg == '0':
                return "0"
            if avg == '1':
                return "1 to 5000"
            if avg == '5001':
                return "Finished 5001 to 10000"
            if avg == 'all':
                return "All"
        return ''
    
    def get_year(self):
        wizard_data = self.localcontext['data']['form']
        year = wizard_data['month_year']
        if year:
            year_id = self.pool.get('account.period').browse(self.cr,self.uid,year[0])
            self.cr.execute('''select EXTRACT(year from date_start) as year, EXTRACT(month from date_start) as month 
                                    from account_period where id = %s''',(year[0],))
            date = self.cr.fetchone()
            self.year = date and int(date[0]) or False
            self.month = date and int(date[1]) or False
            return year_id.name
        
    def get_material(self):
        wizard_data = self.localcontext['data']['form']
        product_ids = wizard_data['material_ids']
        pro_name = ''
        if product_ids:
            for pro in product_ids:
                product_id = self.pool.get('product.product').browse(self.cr,self.uid,pro)
                pro_name += product_id.name + ','
            if pro_name != '':
                pro_name = pro_name[:-1]
        return pro_name
    
    def length_month(self,year, month):
        if month == 2 and (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
            return 29 
        return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
    
    def get_day_column(self):
        day_ids = []
        days = self.length_month(self.year,self.month) or False
        if days:
            for line in range(1,days+1):
                day_ids.append({'day':line})
                line+=1
        return day_ids
    
    def get_line(self):
        wizard_data = self.localcontext['data']['form']
        cat = wizard_data['material_cate']
        product_ids = wizard_data['material_ids']
        avg_value = wizard_data['avg_value']
        if product_ids:
            product_ids = str(product_ids).replace("[","")
            product_ids = str(product_ids).replace("]","")
        else:
            product_ids = ''
        if avg_value:
            avg_value = avg_value
        else:
            avg_value=''
        return self.pool.get('sql.mateiral.purchase.value.day').get_line(self.cr, int(self.year), int(self.month), cat[0], product_ids,avg_value)
#     def get_line(self):
#         product_obj = self.pool.get('product.product')
#         wizard_data = self.localcontext['data']['form']
#         product_ids = wizard_data['material_ids']
#         cat = wizard_data['material_cate']
#         product_report_ids = []
#         if product_ids:
#             product_report_ids = product_ids
#         else :
#             self.cr.execute('''select product_product.id 
#                         from product_product,product_template 
#                         where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
#                         and product_product.product_tmpl_id = product_template.id''',(cat[0],))
#             product_report_ids += [r[0] for r in self.cr.fetchall()]
#          
#         return product_obj.browse(self.cr,self.uid,product_report_ids)
#     
    def get_value(self,line,day):
        value_day = 0
        sql = '''
            select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
            from purchase_order_line 
            where product_id = %s and order_id in (select id from purchase_order where EXTRACT(year from date_order) = %s
            and EXTRACT(month from date_order) = %s and EXTRACT(day from date_order) = %s and state in ('md','approved','done','except_picking','except_invoice'))
        '''%(line,self.year,self.month,day)
        self.cr.execute(sql)
        value_day = self.cr.fetchone()[0]
        value_day = round(value_day,2)
        if value_day:
            self.day_value.append(value_day)
            self.num += 1
        return value_day
    
#     def get_value(self,line,day):
#         value_day = 0
#         sql = '''
#             select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
#             from purchase_order_line 
#             where product_id = %s and order_id in (select id from purchase_order where EXTRACT(year from date_order) = %s
#             and EXTRACT(month from date_order) = %s and EXTRACT(day from date_order) = %s and state in ('md','approved','done','except_picking','except_invoice'))
#         '''%(line,self.year,self.month,day)
#         self.cr.execute(sql)
#         value_day = self.cr.fetchone()[0]
#         value_day = round(value_day,2)
#         if value_day:
#             self.day_value.append(value_day)
#             self.num += 1
#         return value_day
    
    def get_avg(self):
        value_day = 0
        value_day = round(value_day,2)
        total = 0
        avg = 0
        for line in self.day_value:
            total += line
        if self.num:
            avg = total/self.num
        return round(avg,2)
    



