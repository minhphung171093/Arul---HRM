# -*- coding: utf-8 -*-
##############################################################################
#
#    HLVSolution, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
from green_erp_arulmani_sale.report import amount_to_text_en
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
            'get_date': self.get_date,
            'get_total_amount': self.get_total_amount,
            'amount_to_text': self.amount_to_text,
            'get_qty_mt': self.get_qty_mt,
            'get_qty_bags': self.get_qty_bags,
#             'get_qty_bags_gross': self.get_qty_bags_gross,
            'get_total': self.get_total,
            'get_total_example': self.get_total_example,
        })
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d.%m.%Y')
    
    def get_total_amount(self, invoice_line, excise_duty_id, sale_tax_id):
        val = 0.0
        for line in invoice_line:
            val = val + ((line.quantity*line.price_unit)+(line.quantity*line.price_unit)*(excise_duty_id.amount/100))+(((line.quantity*line.price_unit)+(line.quantity*line.price_unit)*(excise_duty_id.amount/100))*sale_tax_id.amount/100)+line.freight
        return round(val, 2)
    
    def amount_to_text(self, nbr, lang='en'):
        if lang == 'en':
            return amount_to_text_en.amount_to_text(nbr, lang, 'inr').upper()
         
    def get_total(self, quantity, price_unit, freight, excise_duty_id, sale_tax_id):
        val = ((quantity*price_unit)+(quantity*price_unit)*(excise_duty_id.amount/100))+(((quantity*price_unit)+(quantity*price_unit)*(excise_duty_id.amount/100))*sale_tax_id.amount/100)+freight
        return round(val, 2)
    
          
    def get_qty_bags(self, qty, uom, type):
        bags_qty = 0.0
        if uom:
            unit = uom.replace(' ','')
            if unit.lower()=='kg' and type == 'domestic':
                rs = round(qty/50,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (50KGS BAGS)'
            if unit.lower()=='kg' and type == 'export':
                rs = round(qty/25,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (25KGS BAGS)'
            if unit.lower()=='bags':
                bags_qty = qty
            if unit.lower()=='tonne' and type == 'domestic':
                rs = round(qty*1000/50,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (50KGS BAGS)'
            if unit.lower()=='tonne' and type == 'export':
                rs = round(qty*1000/25,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (25KGS BAGS)'
        return bags_qty
    
#     def get_qty_bags_gross(self, qty, uom, type):
#         rs = 0.0
#         if uom:
#             unit = uom.replace(' ','')
#             if unit.lower()=='kg' and type == 'domestic':
#                 rs = round(qty/50,2)
#             if unit.lower()=='kg' and type == 'export':
#                 rs = round(qty/25,2)
#             if unit.lower()=='bags':
#                 rs = qty
#             if unit.lower()=='tonne' and type == 'domestic':
#                 rs = round(qty*1000/50,2)
#             if unit.lower()=='tonne' and type == 'export':
#                 rs = round(qty*1000/25,2)
#         return rs
          
    def get_qty_mt(self, qty, uom, type):
        mt_qty = 0.0
        if uom:
            unit = uom.replace(' ','')
            if unit.lower() in ['kg','kgs']:
                mt_qty = qty/1000
            if unit.lower()=='bags' and type == 'domestic':
                mt_qty = qty*50/1000
            if unit.lower()=='bags' and type == 'export':
                mt_qty = qty*25/1000
            if unit.lower() in ['tonne','mt','metricton','metrictons']:
                mt_qty = qty
        return round(mt_qty, 2)
    
    def get_total_example(self,invoice_line,excise_duty_id,sale_tax_id):
        rate = 0.0
        gross = 0.0
        basic_ed = 0.0
        edu_cess = 0.0
        sec_edu_cess = 0.0
        total = 0.0
        cst = 0.0
        total_amount = 0.0
        for line in invoice_line:
            qty_mt = self.get_qty_mt(line.quantity,line.uos_id.name,'domestic')
            rate = line.price_unit or 0
            gross = round(qty_mt * rate,2)
            basic_ed = round((gross*excise_duty_id/100),2)
            edu_cess = round(basic_ed * 2 / 100,2)
            sec_edu_cess =  round(basic_ed * 1 / 100, 2)
            total = round(gross + basic_ed + edu_cess + sec_edu_cess, 2)
            cst = round(total * sale_tax_id / 100,2)
            total_amount += round(gross + basic_ed + edu_cess + sec_edu_cess + total +cst, 2)
        return round(total_amount,2)
    