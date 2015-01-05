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
            'get_total': self.get_total,
            'get_total_amount': self.get_total_amount,
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
            
        
    

    