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
from green_erp_arulmani_sale.report import amount_to_text_en
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
import locale

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_date': self.get_date,
            'get_date_time': self.get_date,
            'get_total': self.get_total,
            'get_total_amount': self.get_total_amount,
            'amount_to_text': self.amount_to_text,
            'get_qty_mt': self.get_qty_mt,
            'get_qty_bags': self.get_qty_bags,
            'get_pre': self.get_pre,
            'get_buyer':self.get_buyer,
            'get_app':self.get_app,
            'get_qty_kgs':self.get_qty_kgs,
            'get_rate_kgs':self.get_rate_kgs,
            'get_freight':self.get_freight, 
            'get_total_kgs':self.get_total_kgs,
            'get_freight_lb':self.get_freight_lb, 
            'get_ins_lb':self.get_ins_lb,
            'get_other_lb':self.get_other_lb,
            'get_amt2':self.get_amt2,
            'get_frt_ins_oc':self.get_frt_ins_oc,
            'get_s3':self.get_s3,
            'get_s1_s2':self.get_s1_s2,
            'get_s3_city_zip':self.get_s3_city_zip,
            'get_state_country':self.get_state_country,
            'get_total_amount': self.get_total_amount,
            'get_desc': self.get_desc
            
        })
    def get_desc(self, desc):
        lnt = 0
        if desc:
            lnt = len(desc)
            spaces = 400 - lnt
            #print "bfr", desc
            desc = desc.ljust(spaces)
            #print "aftr", desc
            return desc
    
    def get_amt2(self, amt):
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.2f", amt, grouping=True)
        return inr_comma_format
    
    def get_frt_ins_oc(self, amt, qty, frt):   
        res = {'frt':0.0, 'ins':0.0, 'oc':0.0}     
        if frt>0:
            frt_ins = format(amt / 1000, '.5f')
            frt_ins = frt_ins+'/KG'
        else:
            frt_ins = ''
        
        res = {'frt': frt_ins, 
               'ins': frt_ins, 
               'oc': frt_ins
               }     
        return res
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_date_time(self, date=False):
        if not date:
            date = time.strftime(DATETIME_FORMAT)
        date = datetime.strptime(date, DATETIME_FORMAT)
        return date.strftime('%d/%m/%Y %H:%M')
    
    def get_total(self, invoice_line, insurance):
        val1 = 0.0
        for line in invoice_line:
            val1 = val1 + line.price_unit + line.freight/line.quantity + insurance
        return round(val1, 2)
    
    #===========================================================================
    # def get_total_amount(self, invoice_line, insurance):
    #     val2 = 0.0
    #     for line in invoice_line:
    #         val2 = val2 + line.price_subtotal + line.freight + insurance*line.quantity
    #     return round(val2, 0)
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
        
    def get_pre(self, pre_carriage_by):
        pre = ''
        if pre_carriage_by.lower()=='sea':
            pre = 'Sea'
        return pre
    
    def get_qty_bags(self, qty, uom, type):
        bags_qty = 0.0
        if uom:
            unit = uom.replace(' ','')
            if unit.lower()=='kg' and type == 'domestic':
                rs = round(qty/50,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (50KGS BAGS)'
            if unit.lower()=='kg' and type == 'export':
                rs = round(qty/25,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (25KGS BAGS)'
            if unit.lower()=='bags':
                bags_qty = qty
            if unit.lower()=='tonne' and type == 'domestic':
                rs = round(qty*1000/50,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (50KGS BAGS)'
            if unit.lower()=='tonne' and type == 'export':
                rs = round(qty*1000/25,2)
                bags_qty = str(rs) + ' NOS OF HDPE LINED BAGS (25KGS BAGS)'
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
        return round(mt_qty, 2)
    
    def get_qty_kgs(self, qty, uom, type):
        kgs_qty = 0
        kgs_qty = qty * 1000
        #raise osv.except_osv(_('Warning! %s'),_(round(kgs_qty,10)))
        return round(kgs_qty)
    def get_rate_kgs(self, rate):        
        kgs_rate = 0.00
        kgs_rate = rate / 1000   
        #raise osv.except_osv(_('Warning! %s'),_(kgs_rate))    
        return round(kgs_rate,2)
    def get_freight(self, freight,qty):        
        mt_freight = 0.00
        kgs_freight = 0.00
        mt_freight = freight / qty   
        kgs_freight =  mt_freight / 1000           
        return round(kgs_freight,2)
    
    def get_buyer(self, obj):
        buyer = ''
        if obj.partner_id and obj.cons_loca and obj.partner_id.id != obj.cons_loca.id:
            buyer = (obj.cons_loca and obj.cons_loca.street or '') + ', ' + (obj.cons_loca and obj.cons_loca.street2 or '') + ', ' + (obj.cons_loca and obj.cons_loca.city or '') + ', ' + (obj.cons_loca and (obj.cons_loca.state_id and obj.cons_loca.state_id.name or '') or '') + ', ' + (obj.cons_loca and (obj.cons_loca.country_id and obj.cons_loca.country_id.name or '') or '') + ', ' + (obj.cons_loca and obj.cons_loca.zip or '')
        return buyer
    def get_freight_lb(self, invoice):    
        lb = ''    
        if invoice.sale_id.incoterms_id.code=='CIF':
            lb = 'FREIGHT:'         
        return lb
    def get_ins_lb(self, invoice):    
        lb = ''    
        if invoice.sale_id.incoterms_id.code=='CIF':
            lb = 'INSURANCE:'         
        return lb
    def get_other_lb(self, invoice):    
        lb = ''    
        if invoice.sale_id.incoterms_id.code=='CIF':
            lb = 'OTHER CHARGES:'         
        return lb
    
    def get_app(self, obj):       
        if obj:
            app = ''
            sql = '''
            SELECT id FROM crm_application WHERE code='OPATI TM R001'
            '''
            self.cr.execute(sql)            
            pl_date=self.cr.fetchone()
            a = pl_date[0]
            
            if a:
                #raise osv.except_osv(_('Warning!%s'),_(a))
                if a==obj.id:                                                               
                    return  'OPATIN' + u"\u2122" +' R001'
                
    def get_s1_s2(self,partner):
        if partner.street2:
            return partner.street+", "+partner.street2
        else:
            return partner.street
    def get_s3_city_zip(self,partner):
        if partner.street3 and partner.city and partner.zip:
            return partner.street3+", "+partner.city+", "+partner.zip
        elif partner.street3 and partner.city and not partner.zip:
            return partner.street3+", "+partner.city
        elif not partner.street3 and partner.city and partner.zip:
            return partner.city+", "+partner.zip
        elif partner.street3 and not partner.city and partner.zip:
            return partner.street3+", "+partner.zip
        elif partner.street3 and not partner.city and not partner.zip:
            return partner.street3
        elif not partner.street3 and partner.city and not partner.zip:
            return partner.city
        elif not partner.street3 and not partner.city and partner.zip:
            return partner.zip
    def get_state_country(self,partner):
        if partner.state_id:
            if partner.state_id.name:
                if partner.state_id.name:
                    if (partner.state_id.name).replace(" ", ""):
                        return partner.state_id.name+", "+partner.country_id.name
                    else:
                        return partner.country_id.name
    def get_s3(self,partner):
        if partner.street3 and partner.city:
            return partner.street3+", "+partner.city
        else:
            return partner.city
    def get_total_amount(self, invoice_line):
        val2 = 0.0
        for line in invoice_line:
            val2 = val2 + line.price_subtotal + line.quantity*line.freight + line.insurance*(line.quantity) 
        return round(val2, 2)
    def get_total_kgs(self, invoice_line):
        val1 = 0.0
        for line in invoice_line:
            #mt_freight = freight / qty 
            #raise osv.except_osv(_('Warning!'),_((line.freight)/1000) )
            val1 = val1 + round((line.price_unit/1000),5) + round(line.freight/1000,5) +  round(line.insurance/1000,5)
        val1 = format(val1, '.5f')  
        return val1