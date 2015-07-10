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
        })
    def get_copy(self,is_original,is_duplicate,is_triplicate,is_quadruplicate):
        type = ''
        if is_original is True:
            type =  'ORIGINAL COPY'+'\n'+'DUPLICATE COPY'+'\n'+'TRIPLICATE COPY'+'\n'+'QUADRUPLICATE COPY'
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
        
        
        
        