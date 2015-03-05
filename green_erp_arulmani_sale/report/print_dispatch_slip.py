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
            'get_qty_bags': self.get_qty_bags,
            'get_qty_mt': self.get_qty_mt,
            
        })
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATETIME_FORMAT)
        date = datetime.strptime(date, DATETIME_FORMAT)
        return date.strftime('%d/%m/%Y')


    
    def get_qty_bags(self, qty, uom, type):
        bags_qty = 0.0
        if uom:
            unit = uom.replace(' ','')
            if unit.lower()=='kg' and type == 'domestic':
                bags_qty = str(qty/50) + ' NOS OF HDPE LINED BAGS (50KGS BAGS)'
            if unit.lower()=='kg' and type == 'export':
                bags_qty = str(qty/25) + ' NOS OF HDPE LINED BAGS (25KGS BAGS)'
            if unit.lower()=='bags':
                bags_qty = qty
            if unit.lower()=='tonne' and type == 'domestic':
                bags_qty = str(qty*1000/50) + ' NOS OF HDPE LINED BAGS (50KGS BAGS)'
            if unit.lower()=='tonne' and type == 'export':
                bags_qty = str(qty*1000/25) + ' NOS OF HDPE LINED BAGS (25KGS BAGS)'
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
        return round(mt_qty,3)
    

    