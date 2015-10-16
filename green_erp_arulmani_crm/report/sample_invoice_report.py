# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import amount_to_text_vn
import amount_to_text_en
#from green_erp_arulmani_crm.report import amount_to_text_en
from green_erp_arulmani_crm.report import amount_to_text_en
from green_erp_arulmani_crm.report import amount_to_text_indian
from amount_to_text_indian import Number2Words
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.user_obj = pooler.get_pool(self.cr.dbname).get('res.users')
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'get_total':self.get_total,
            'amount_to_text':self.amount_to_text,
            'get_vietname_date':self.get_vietname_date
            })
    
    def get_vietname_date(self, date):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d-%m-%Y')
    
    def get_total(self,sample_invoice_line):
        sum =0
        for line in sample_invoice_line:
            sum += line.quantity*line.rate_per_kg
        return sum
    #===========================================================================
    # def amount_to_text(self, nbr, lang='vn', currency=False):
    #     if lang == 'vn':
    #         return  amount_to_text_vn.amount_to_text(nbr, lang)
    #     else:
    #         a= currency
    #         return amount_to_text_en.amount_to_text(nbr, 'en', lang)
    #===========================================================================
    def amount_to_text(self, nbr, currency):
        lang='en'
        if currency.name!='INR':
            return amount_to_text_en.amount_to_text(nbr, lang, currency.name).upper() 
        if currency.name=='INR':
            text = Number2Words().convertNumberToWords(nbr).upper()
            if text and len(text)>3 and text[:3]==' ':
                text = text[3:]
            return text  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

