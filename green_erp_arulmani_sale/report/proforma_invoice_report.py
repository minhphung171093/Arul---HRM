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
            'length_month': self.length_month,
            'get_month_name': self.get_month_name,
            'get_qty_mt': self.get_qty_mt,
            'get_state':self.get_state,
            'get_bill_loc':self.get_bill_loc,
            
        })
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def length_month(self,year, month):
        if month == 2 and (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
            return 29 
        return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
    def get_month_name(self, month):
        _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
        d = _months[month]
        return d

    def get_qty_mt(self, qty, uom):
        mt_qty = 0.0
        if uom.lower()=='kg':
            mt_qty = qty/1000
        if uom.lower()=='bags':
            mt_qty = qty*50/1000
        if uom.lower()=='mt':
            mt_qty = qty
        return mt_qty
    
    def get_state(self,o):
        a=''
        if o.state_id:
            a+=o.state_id.name+', '
        a+=o.country_id and o.country_id.name or ''
        return a

    def get_bill_loc(self, obj):
        cons = ''
        if obj.customer_id:
            if obj.customer_id.street:
                cons += (obj.customer_id.street or '') + ', \n'
            if obj.customer_id.street2:
                cons += (obj.customer_id.street2 or '') + ', \n'
            if obj.customer_id.city:
                cons += (obj.customer_id.city or '') + ', \n'
            if obj.customer_id.state_id:
                cons += (obj.customer_id.state_id.name or '') + ', \n'
            if obj.customer_id.country_id:
                cons += (obj.customer_id.country_id.name or '') + ', \n'
            if obj.customer_id.zip:
                cons += obj.customer_id.zip or ''
        return cons
    
    
    
    
    