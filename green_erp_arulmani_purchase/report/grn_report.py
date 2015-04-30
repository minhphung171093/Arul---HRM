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
            'convert_date': self.convert_date,
            'convert_date_time': self.convert_date_time,
            'get_move': self.get_move,
        })
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def convert_date_time(self, date):
        if date:
            date = datetime.strptime(date, DATETIME_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_move(self,move):
        res = ''
        if move == 'direct':
            res = 'Direct Stock Update'
        elif move == 'move':
            res = 'Move to Consumption'
        else:
            res = 'Need Inspection'
        return res
    

    