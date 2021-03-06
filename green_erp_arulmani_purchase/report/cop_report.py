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
        self.data_line = {}
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_boms': self.get_boms,
            'get_lines': self.get_lines,
            'set_data_line': self.set_data_line,
            'get_data_line': self.get_data_line,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_boms(self):
        wizard_data = self.localcontext['data']['form']
        bom_ids = wizard_data['bom_ids']
        if not bom_ids:
            bom_ids = self.pool.get('mrp.bom').search(self.cr, self.uid, [('bom_id','=',False)])
        return self.pool.get('mrp.bom').browse(self.cr, self.uid, bom_ids)
    
    def get_lines(self, bom):
        sql = '''
            select b.product_id as product_id, pp.default_code as product_code, pt.name as product_name, pp.tpt_description as description,
                coalesce(b.product_qty,0) as product_qty, coalesce(b.price_unit,0) as price_unit, coalesce(b.product_cost,0) as product_cost
                
                from mrp_bom b
                left join product_product pp on b.product_id=pp.id
                left join product_template pt on pp.product_tmpl_id=pt.id
                left join product_category pc on pt.categ_id=pc.id
                
            where bom_id=%s and pc.cate_name='raw'
        '''%(bom.id)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_product_qty(self, product_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select sum(coalesce(product_qty, 0)) as product_qty
                from stock_move
                
                where production_id in (
                    select id from mrp_production where state='done' and date_planned between '%s' and '%s'
                ) and product_id=%s
        '''%(date_from,date_to,product_id)
        self.cr.execute(sql)
        product_qty = self.cr.fetchone()
        return product_qty and product_qty[0] or 0
    
    def get_consumption_qty(self, product_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select sum(coalesce(product_qty, 0)) as product_qty
                from mrp_production_product_line
                
                where production_id in (
                    select id from mrp_production where state='done' and date_planned between '%s' and '%s'
                ) and product_id=%s
        '''%(date_from,date_to,product_id)
        self.cr.execute(sql)
        product_qty = self.cr.fetchone()
        return product_qty and product_qty[0] or 0
    
    def get_consumption_value(self, product_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select sum(coalesce(sm.product_qty, 0)*coalesce(sm.price_unit, 0)) as product_qty
                from stock_move sm
                left join mrp_production_move_ids mpm on mpm.move_id=sm.id
                left join mrp_production mp on mpm.production_id=mp.id
                where mp.state='done' and mp.date_planned between '%s' and '%s' and sm.product_id=%s
        '''%(date_from,date_to,product_id)
        self.cr.execute(sql)
        product_value = self.cr.fetchone()
        return product_value and product_value[0] or 0
    
    def get_request_qty(self, product_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select sum(coalesce(product_uom_qty, 0)) as product_qty
            
                from tpt_material_request_line
                where product_id=%s and material_request_id in (
                    select id from tpt_material_request where state not in ('draft','cancel') and date_request between '%s' and '%s'
                )
        '''%(product_id,date_from,date_to)
        self.cr.execute(sql)
        product_qty = self.cr.fetchone()
        return product_qty and product_qty[0] or 0
    
    def get_issued_qty(self, product_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select sum(coalesce(product_isu_qty, 0)) as product_qty
            
                from tpt_material_issue_line
                where product_id=%s and material_issue_id in (
                    select id from tpt_material_issue where state not in ('draft') and date_expec between '%s' and '%s'
                )
        '''%(product_id,date_from,date_to)
        self.cr.execute(sql)
        product_qty = self.cr.fetchone()
        return product_qty and product_qty[0] or 0
    
    def get_issued_value(self, product_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select sum(coalesce(product_qty, 0)*coalesce(price_unit, 0)) as product_value
            
                from stock_move
                where product_id=%s and issue_id in (
                    select id from tpt_material_issue where state not in ('draft') and date_expec between '%s' and '%s'
                )
        '''%(product_id,date_from,date_to)
        self.cr.execute(sql)
        product_value = self.cr.fetchone()
        return product_value and product_value[0] or 0
    
    def set_data_line(self, line):
        product_id = line['product_id']
        actual_quantity = self.get_consumption_qty(product_id)
        actual_value = self.get_consumption_value(product_id)
        actual_rate = actual_quantity and float(actual_value)/float(actual_quantity)
        production_qty = self.get_product_qty(product_id)
        actual_per_ton = production_qty and float(actual_quantity)/float(production_qty)
        cost_per_ton = actual_rate*actual_per_ton
        norms_per_ton = production_qty and float(line['product_qty'])/float(production_qty)
        cost_per_ton2 = line['price_unit']*norms_per_ton
        total_12 = line['product_cost']*actual_per_ton
        variance_price_variance = cost_per_ton-total_12
        total_14 = variance_price_variance*production_qty
        usage_variance = total_12-cost_per_ton2
        total_16 = usage_variance*production_qty
        total_variance_per_ton = variance_price_variance + cost_per_ton2
        total_18 = actual_value - line['product_cost']
        self.data_line = {
            'actual_quantity': actual_quantity,
            'actual_rate': actual_rate,
            'actual_value': actual_value,
            'actual_per_ton': actual_per_ton,
            'cost_per_ton': cost_per_ton,
            'norms_per_ton': norms_per_ton,
            'cost_per_ton2': cost_per_ton2,
            'total_12': total_12,
            'variance_price_variance': variance_price_variance,
            'total_14': total_14,
            'usage_variance': usage_variance,
            'total_16': total_16,
            'total_variance_per_ton': total_variance_per_ton,
            'total_18': total_18,
        }
        return True
    
    def get_data_line(self, col):
        if self.data_line.get(col, False): 
            return self.data_line[col]
        return 0

