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
    
