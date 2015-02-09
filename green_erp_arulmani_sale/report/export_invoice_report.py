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
            'get_total': self.get_total,
            'get_total_amount': self.get_total_amount,
            'amount_to_text': self.amount_to_text,
            'get_qty_mt': self.get_qty_mt,
            'get_qty_bags': self.get_qty_bags,
            'get_pre': self.get_pre,
            'get_buyer':self.get_buyer,
        })
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_total(self, invoice_line, insurance):
        val1 = 0.0
        for line in invoice_line:
            val1 = val1 + line.price_unit + line.freight/line.quantity + insurance
        return round(val1, 2)
    
    def get_total_amount(self, invoice_line, insurance):
        val2 = 0.0
        for line in invoice_line:
            val2 = val2 + line.price_subtotal + line.freight + insurance*line.quantity
        return round(val2, 2)
    
    def amount_to_text(self, nbr, lang='en', currency=False):
        if lang == 'vn':
            return  amount_to_text_en.amount_to_text(nbr, lang)
        else:
            a= currency
            return amount_to_text_en.amount_to_text(nbr, lang, 'usd') 
        
    def get_pre(self, pre_carriage_by):
        pre = ''
        if pre_carriage_by.lower()=='sea':
            pre = 'Sea'
        return pre
    
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
            if unit.lower() in ['tonne','tonnes','mt','metricton','metrictons']:
                mt_qty = qty
        return round(mt_qty, 2)
    
    def get_buyer(self, obj):
        buyer = ''
        if obj.partner_id and obj.cons_loca and obj.partner_id.id != obj.cons_loca.id:
            buyer = (obj.cons_loca and obj.cons_loca.street or '') + ', ' + (obj.cons_loca and obj.cons_loca.street2 or '') + ', ' + (obj.cons_loca and obj.cons_loca.city or '') + ', ' + (obj.cons_loca and (obj.cons_loca.state_id and obj.cons_loca.state_id.name or '') or '') + ', ' + (obj.cons_loca and (obj.cons_loca.country_id and obj.cons_loca.country_id.name or '') or '') + ', ' + (obj.cons_loca and obj.cons_loca.zip or '')
        return buyer

    