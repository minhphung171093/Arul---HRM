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
import amount_to_text_vn
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
            'get_total': self.get_total,
            'get_total_amount': self.get_total_amount,
            'amount_to_text': self.amount_to_text,
            'get_qty_mt': self.get_qty_mt,
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
        return val1
    
    def get_total_amount(self, invoice_line, insurance):
        val2 = 0.0
        for line in invoice_line:
            val2 = val2 + line.price_subtotal + line.freight + insurance*line.quantity
        return val2
    
    def amount_to_text(self, nbr, lang='en', currency=False):
        if lang == 'vn':
            return  amount_to_text_en.amount_to_text(nbr, lang)
        else:
            a= currency
            return amount_to_text_en.amount_to_text(nbr, 'en', lang) 
        
    def get_pre(self, pre_carriage_by):
        pre = ''
        if pre_carriage_by.lower()=='sea':
            pre = 'Sea'
        return pre
    
    def get_qty_mt(self, qty, uom):
        mt_qty = 0.0
        if uom.lower()=='kg':
            mt_qty = qty/1000
        if uom.lower()=='bags':
            mt_qty = qty*50/1000
        if uom.lower()=='mt':
            mt_qty = qty
        return mt_qty
    
    def get_buyer(self, obj):
        buyer = ''
        if obj.partner_id and obj.cons_loca and obj.partner_id.id != obj.cons_loca.id:
            buyer = (obj.cons_loca and obj.cons_loca.street or '') + ', ' + (obj.cons_loca and obj.cons_loca.street2 or '') + ', ' + (obj.cons_loca and obj.cons_loca.city or '') + ', ' + (obj.cons_loca and (obj.cons_loca.state_id and obj.cons_loca.state_id.name or '') or '') + ', ' + (obj.cons_loca and (obj.cons_loca.country_id and obj.cons_loca.country_id.name or '') or '') + ', ' + (obj.cons_loca and obj.cons_loca.zip or '')
        return buyer

    