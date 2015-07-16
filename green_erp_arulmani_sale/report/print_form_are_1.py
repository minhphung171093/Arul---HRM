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
import locale
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
            'get_amount':self.get_amount,
            'get_copy':self.get_copy,
            'get_arename':self.get_arename,
            'get_amt':self.get_amt,
            'get_edamt':self.get_edamt,
        })
    def get_amt(self,value=False):
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.0f", value, grouping=True)
        return inr_comma_format
    def get_edamt(self,inv_id,ed_amt):
        sql = ''' 
        select quantity,price_unit from account_invoice_line where invoice_id=%s
        '''%inv_id
        self.cr.execute(sql)   
        for k in self.cr.fetchall():
            qty=k[0]
            unit_price=k[1]     
        amt = qty * unit_price * ed_amt / 100     
        
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.0f", amt, grouping=True)
        return inr_comma_format
    def get_arename(self,name):
        name = name[13:16]          
        return name
    def get_copy(self,is_original,is_duplicate,is_triplicate,is_quadruplicate,is_extra):
        type = ''
        if is_original is True:
            type = 'ORIGINAL COPY'
        if is_duplicate is True:
            type = 'DUPLICATE COPY'
        if is_triplicate is True:
            type = 'TRIPLICATE COPY'
        if is_quadruplicate is True:
            type = 'QUADRUPLICATE COPY'
        if is_extra is True:
            type = 'EXTRA COPY'
            
        return type
    def get_amount(self,value=False):
        value = float(value)
        if not value:
            value = 0.0
        value=str(value)
        return value.split('.')
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_total(self, duty_rate_line):
        val1 = 0.0
        for line in duty_rate_line:
            val1 = val1 + line.amount_inr
        return val1 
        

    