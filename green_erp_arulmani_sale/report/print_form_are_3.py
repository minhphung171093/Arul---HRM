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
            'get_amount': self.get_amount,
            'get_copy':self.get_copy,
            'get_arename':self.get_arename,
            'get_hy':self.get_hy,
            'get_amt':self.get_amt,
            'get_iamt':self.get_iamt,
            'get_edamt':self.get_edamt,
            'get_dec':self.get_dec,
            # Added by P.vinothkumar on 03/09/2016
            'get_app':self.get_app,
        })
    def get_dec(self,number=False):
        dec_no = round(number - int(number), 2)
        dec_no = format(dec_no, '.2f') 
        return dec_no[2:]
    def get_amt(self,value=False):
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.0f", value, grouping=True)
        return inr_comma_format
    def get_iamt(self,value=False):
        value=trunc(value)
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.0f", value, grouping=True)
        return inr_comma_format
    def get_edamt(self,inv_id,ed_amt):
        #value = float(value)
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
        if len(name)==19:
            name = name[11:14] 
        else:
            name = name[13:17]    
        #raise osv.except_osv(_('Warning!%s'),_(name))        
        return name
    def get_hy(self,no):
        if no>0:
            return no
        else:    
            return '-'
    def get_copy(self,is_original,is_duplicate,is_triplicate,is_quadruplicate):
        type = ''
        if is_original is True:
            #type =  'ORIGINAL COPY'+'\n'+'\033[1m'+'DUPLICATE COPY'+'\033[0m' +'\n'+'TRIPLICATE COPY'+'\n'+'QUADRUPLICATE COPY'
            type = 'ORIGINAL COPY'+'\n'+'\033[1m'+'DUPLICATE COPY'+ '\033[0m' +'\n'+'TRIPLICATE COPY'+'\n'+'QUADRUPLICATE COPY'
        if is_duplicate is True:
            type = 'ORIGINAL COPY'+'\n'+'DUPLICATE COPY'+'\n'+'TRIPLICATE COPY'+'\n'+'QUADRUPLICATE COPY'
        if is_triplicate is True:
            type = 'ORIGINAL COPY'+'\n'+'DUPLICATE COPY'+'\n'+'TRIPLICATE COPY'+'\n'+'QUADRUPLICATE COPY'
        if is_quadruplicate is True:
            type = 'ORIGINAL COPY'+'\n'+'DUPLICATE COPY'+'\n'+'TRIPLICATE COPY'+'\n'+'QUADRUPLICATE COPY'
        
            
        return type
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')

    def get_amount(self,value=False):
        value = float(value)
        if not value:
            value = 0.0
        value=str(value)
        return value.split('.')
    # Added by P.vinothkumar on 03/09/2016 for display product grades
    def get_app(self, obj):       
        if obj:
            app = ''
            sql = '''
            SELECT id FROM crm_application WHERE code='OPATI TM R001'
            '''
            self.cr.execute(sql)            
            pl_date=self.cr.fetchone()
            a = pl_date[0]
            
            if a:
                #raise osv.except_osv(_('Warning!%s'),_(a))
                if a==obj.id:                                                               
                    return  '       Opati' + u"\u2122" +' R001'
        
        
         # End
        
        
        
        