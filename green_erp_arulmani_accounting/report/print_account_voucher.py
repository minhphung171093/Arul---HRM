# -*- coding: utf-8 -*-
##############################################################################
#
#    TPT, Open Source Management Solution
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
import locale
from math import trunc
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from green_erp_arulmani_accounting.report import amount_to_text_en
from green_erp_arulmani_accounting.report import amount_to_text_indian
from amount_to_text_indian import Number2Words

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_date': self.get_date,
            'get_amount': self.get_amount,
            'get_dec': self.get_dec,
            'get_amt': self.get_amt,
            'get_type': self.get_type,
            'amount_to_text': self.amount_to_text,
            
        })
        
    def get_type(self,code):
        if code=='BNK1':
            return 'CASH VOUCHER'
        elif code=='BNK2':
            return 'BANK VOUCHER'
        else:
            return ''
        
    def amount_to_text(self, number):
        text = Number2Words().convertNumberToWords(number).upper()
        if text and len(text)>3 and text[:3]=='AND':
            text = text[3:]
        return text
        
    def get_dec(self,number=False):
        dec_no = round(number - int(number), 2)
        dec_no = format(dec_no, '.2f') 
        return dec_no[2:]
    def get_amt(self,value=False):
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.2f", value, grouping=True)
        return inr_comma_format

    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d.%m.%Y')

    def get_amount(self,value=False):
        value = float(value)
        if not value:
            value = 0.0
        value=str(value)
        return value.split('.')
        
        
        
        