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
        self.start = False
        self.stop = False
        self.localcontext.update({
            'get_category':self.get_category,
            'get_average':self.get_average,
            'get_year':self.get_year,
            'get_material':self.get_material,  
            'get_line':self.get_line, 
            'get_value':self.get_value, 
                                  
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
        year = wizard_data['year']
        if year:
            year_id = self.pool.get('account.fiscalyear').browse(self.cr,self.uid,year[0])
            self.cr.execute('''select EXTRACT(year from date_start) as start, EXTRACT(year from date_stop) as stop 
                                    from account_fiscalyear where id = %s''',(year[0],))
            date = self.cr.fetchone()
            self.start = date and date[0] or False
            self.stop = date and date[1] or False
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
        return self.pool.get('sql.mateiral.purchase.value.month').get_line(self.cr, int(self.start), int(self.stop), cat[0], product_ids,avg_value)
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
    
    def get_value(self,line):
        res ={}
        year = False
        total = 0.0
        n = 0
        avg_value = 0
        for month in [4,5,6,7,8,9,10,11,12,1,2,3]:
            if month not in [1,2,3]:
                year = self.start
            else :
                year = self.stop
            sql = '''
                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end value1 
                from purchase_order_line 
                where product_id = %s and order_id in (select id from purchase_order where EXTRACT(year from date_order) = %s
                and EXTRACT(month from date_order) = %s and state in ('md','approved','done','except_picking','except_invoice'))
            '''%(line,year,month)
            self.cr.execute(sql)
            value_month = self.cr.fetchone()[0]
            value_month = round(value_month,2)
            if month == 4:
                res.update({'4':value_month})
            if month == 5:
                res.update({'5':value_month})
            if month == 6:
                res.update({'6':value_month})
            if month == 7:
                res.update({'7':value_month})
            if month == 8:
                res.update({'8':value_month})
            if month == 9:
                res.update({'9':value_month})
            if month == 10:
                res.update({'10':value_month})
            if month == 11:
                res.update({'11':value_month})
            if month == 12:
                res.update({'12':value_month})
            if month == 1:
                res.update({'1':value_month})
            if month == 2:
                res.update({'2':value_month})
            if month == 3:
                res.update({'3':value_month})
            total += value_month
            if value_month > 0:
                n += 1
        if n:
            avg_value = total/n
        res.update({'avg':round(avg_value,2)})
        return res



