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
from math import trunc
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
            'get_datetime': self.get_datetime,
            'get_approx_value': self.get_approx_value,
    
            'get_amount':self.get_amount,
       
            'get_amt':self.get_amt,
            'get_iamt':self.get_iamt,

            'get_dec':self.get_dec, 
            # Added by SSR ON 20/04/2017 - Incident Id - 2482
            'get_gatepass_type':self.get_gatepass_type,
            'get_return_type':self.get_return_type
        })
    def get_approx_value(self, po_id, product_id, prod_qty):
        sql = '''
        select price_unit from purchase_order_line where order_id=%s and product_id=%s
        '''%(po_id.id, product_id.id)        
        self.cr.execute(sql)
        a = self.cr.fetchone()
        res = prod_qty * a[0]
        res = self.get_amt(res)
        return res
        
    def get_dec(self,number=False):
        dec_no = round(number - int(number), 2)
        dec_no = format(dec_no, '.3f') 
        return dec_no[2:]
    
    def get_amt(self,value=False):
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.2f", value, grouping=True)
        return inr_comma_format
    
    def get_iamt(self,value=False):
        value=trunc(value)
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.3f", value, grouping=True)
        return inr_comma_format
    
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
    
    def get_datetime(self, date=False):
        if not date:
            date = time.strftime(DATETIME_FORMAT)
        date = datetime.strptime(date, DATETIME_FORMAT)
        return date.strftime('%d/%m/%Y')
    
     # Added by SSR ON 20/04/2017 - Incident Id - 2482
    def get_gatepass_type(self,pass_type,date=False):
        type = ''
        var = pass_type
        if var == 'return-purchase' or var == 'return-service':
            date = time.strftime(DATETIME_FORMAT)
            date = datetime.strptime(date, DATETIME_FORMAT)
            date.strftime('%d/%m/%Y')
            type='DATE OF RETURN :'
            type += date.strftime('%d/%m/%Y')
        elif var == 'non-return-purchase' or var == 'non-return-service':
            type=''
        return type
        
    def get_return_type(self,pass_type,date=False):
        type = ''
        var = pass_type
        if var == 'return-purchase' or var == 'return-service':
            type='RETURNABLE'
        elif var == 'non-return-purchase' or var == 'non-return-service':
            type=' NON-RETURNABLE'                
        return type
    
    ##
    