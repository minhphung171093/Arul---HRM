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
from amount_to_text_indian import Number2Words
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
        'get_item_txt':self.get_item_txt,
        'get_indent':self.get_indent
            
        })

    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')  

    '''def amount_to_text(self, nbr, lang='en'):
        if lang == 'en':
            return amount_to_text_en.amount_to_text(nbr, lang, 'inr').upper()
            '''
    def amount_to_text(self, number):
        text = Number2Words().convertNumberToWords(number).upper()
        if text and len(text)>3 and text[:3]=='AND':
            text = text[3:]
        return text

    def get_edu_cess(self, basic_excise_duty):
        ecess = 0.0
        ecess = (basic_excise_duty)*2/100
        return ecess

    def get_sec_cess(self, basic_excise_duty):
        sec_cess = 0.0
        sec_cess = (basic_excise_duty)*1/100
        return sec_cess

    def get_item_txt(self, indent_id):
        if indent_id:
            txt = ''
            sql = '''
            SELECT item_text FROM tpt_purchase_product WHERE pur_product_id=%s
            '''%indent_id
            self.cr.execute(sql)
            txt = self.cr.fetchone()
        
        #raise osv.except_osv(_('Warning!%s'),_(p[0]))     
            if txt:
                txt = txt
            return txt
    def get_indent(self, order):
        if order:         
            sql = '''select name from tpt_purchase_indent where id in (select po_indent_no from 
            purchase_order_line where order_id=%s)
            '''%order
            self.cr.execute(sql)
            #txt = self.cr.fetchone()
            
            indent_nos = ''
            for p in self.cr.fetchall(): 
                indent_nos = indent_nos +' '+ p[0]                               
            indent_nos = indent_nos[:20]    
        
            return indent_nos


