# -*- coding: utf-8 -*-
##############################################################################
#
#    Tenth Planet Technologies
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
from green_erp_arulmani_purchase.report import amount_to_text_en

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
		'get_date': self.get_date,
		
		'amount_to_text': self.amount_to_text,
		'get_edu_cess':self.get_edu_cess,
		'get_sec_cess':self.get_sec_cess,
        #'get_item_txt':self.get_item_txt
            
        })

    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')  

    def amount_to_text(self, nbr, lang='en'):
        if lang == 'en':
            return amount_to_text_en.amount_to_text(nbr, lang, 'inr').upper()

    def get_edu_cess(self, basic_excise_duty):
        ecess = 0.0
        ecess = (basic_excise_duty)*2/100
        return ecess

    def get_sec_cess(self, basic_excise_duty):
        sec_cess = 0.0
        sec_cess = (basic_excise_duty)*1/100
        return sec_cess

    
    


