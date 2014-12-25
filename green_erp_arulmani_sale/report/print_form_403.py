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
            'get_time': self.get_time,
            'get_departure':self.get_departure,
        })
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')

    def get_time(self, id):
        sql = '''
            select timezone('UTC',arrival::timestamp) from tpt_form_403 where id = %s
        '''%(id)
        self.cr.execute(sql)
        date = [row[0] for row in self.cr.fetchall()]
        if date:
            return date[0].strftime('%H:%M:%S')
        else:
            return ''
    def get_departure(self, id):
        sql = '''
            select timezone('UTC',departure::timestamp) from tpt_form_403 where id = %s
        '''%(id)
        self.cr.execute(sql)
        date = [row[0] for row in self.cr.fetchall()]
        if date:
            return date[0].strftime('%H:%M:%S')
        else:
            return ''
    