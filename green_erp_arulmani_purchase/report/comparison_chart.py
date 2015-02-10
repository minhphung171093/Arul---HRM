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
            
        })
    
    def get_vendor(self,o,num):
        res = {
               'rate': 0,
               'value': 0,
               }
        quotation_obj = self.pool.get('tpt.purchase.quotation')
        sql = '''
            select id from tpt_purchase_quotation where comparison_chart_id = %s and tpt_purchase_quotation.select = 'True'
        '''%(o.id)
        self.cr.execute(sql)
        quotation_ids = [row[0] for row in self.cr.fetchall()]
#         if len(quotation_ids)>=num:
            
        
        
        
        
        
        