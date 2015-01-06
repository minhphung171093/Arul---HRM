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
import amount_to_text_en
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
            'get_total': self.get_total,
        })
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_total_amount(self, invoice_line, excise_duty_id, sale_tax_id):
        val = 0.0
        for line in invoice_line:
            val = val + ((line.quantity*line.price_unit)+(line.quantity*line.price_unit)*(excise_duty_id.amount/100))+(((line.quantity*line.price_unit)+(line.quantity*line.price_unit)*(excise_duty_id.amount/100))*sale_tax_id.amount/100)+line.freight
        return round(val, 2)
    
    def amount_to_text(self, nbr, lang='en'):
        if lang == 'en':
            return amount_to_text_en.amount_to_text(nbr, 'en', lang)   
         
    def get_total(self, quantity, price_unit, freight, excise_duty_id, sale_tax_id):
        val = ((quantity*price_unit)+(quantity*price_unit)*(excise_duty_id.amount/100))+(((quantity*price_unit)+(quantity*price_unit)*(excise_duty_id.amount/100))*sale_tax_id.amount/100)+freight
        return round(val, 2)
          
    def get_qty_bags(self, qty, uom):
        bags_qty = 0.0
        if uom.lower()=='kg':
            bags_qty = qty/50
        if uom.lower()=='bags':
            bags_qty = qty
        if uom.lower()=='mt':
            bags_qty = qty*1000/50
        return round(bags_qty, 2)
          
    def get_qty_mt(self, uos_id, quantity):
        mt_qty = 0.0
        if uos_id.lower()=='kg':
            mt_qty = quantity/1000
        if uos_id.lower()=='bags':
            mt_qty = quantity*50/1000
        if uos_id.lower()=='mt':
            mt_qty = quantity
        return round(mt_qty, 2)
    