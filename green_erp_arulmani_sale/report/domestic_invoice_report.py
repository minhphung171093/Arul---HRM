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
import locale
from green_erp_arulmani_sale.report import amount_to_text_en
from green_erp_arulmani_sale.report import amount_to_text_indian
from amount_to_text_indian import Number2Words
#locale.setlocale(locale.LC_NUMERIC, "en_IN")
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
            'get_date_time': self.get_date,
            'get_total_amount': self.get_total_amount,
            'amount_to_text': self.amount_to_text,
            'tpt_amount_to_text': self.tpt_amount_to_text,
            'get_qty_mt': self.get_qty_mt,
            'get_qty_mt1': self.get_qty_mt1,
            'get_qty_mt2': self.get_qty_mt2,
            'get_amt': self.get_amt,
            'get_qty_bags': self.get_qty_bags,
#             'get_qty_bags_gross': self.get_qty_bags_gross,
            'get_total': self.get_total,
            'get_ed_example': self.get_ed_example,
            'get_total_example': self.get_total_example,
            'get_excise_duty': self.get_excise_duty, 
            'get_excise_duty_amt': self.get_excise_duty_amt,
            'get_subtotal': self.get_subtotal,
            'get_range_label':self.get_range_label,
            'get_loc':self.get_loc,
            'get_comm':self.get_comm,
            'get_ce':self.get_ce,
            'get_ecc':self.get_ecc,
            'get_pan':self.get_pan,
            'get_cst':self.get_cst,
            'get_tin':self.get_tin,
            'c':self.c, 
            'z':self.z,
            'get_app':self.get_app, 
            'get_if_freight_lb':self.get_if_freight_lb,
            'get_if_freight_amt':self.get_if_freight_amt,
            'get_if_freight_tamt':self.get_if_freight_tamt,
            'get_cst_lb':self.get_cst_lb,
            'get_s3':self.get_s3,
            'get_sub_ed':self.get_sub_ed,
        })
    def get_sub_ed(self, line):        
        amt = 0.0
        amt = line.amount_ed + line.price_subtotal     
        return format(amt,'.2f')
    
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d.%m.%Y')
    
    def get_date_time(self, date=False):
        if not date:
            date = time.strftime(DATETIME_FORMAT)
        date = datetime.strptime(date, DATETIME_FORMAT)
        return date.strftime('%d.%m.%Y %H:%M:%S')
    
    def get_total_amount(self, invoice_line, excise_duty_id, sale_tax_id):
        val = 0.0
        for line in invoice_line:
            val = val + ((line.quantity*line.price_unit)+(line.quantity*line.price_unit)*(excise_duty_id.amount/100))+(((line.quantity*line.price_unit)+(line.quantity*line.price_unit)*(excise_duty_id.amount/100))*sale_tax_id.amount/100)+line.freight
        return round(val)
    
#     def amount_to_text(self, nbr, lang='en'):
#         if lang == 'en':
#             return amount_to_text_en.amount_to_text(nbr, lang, 'inr').upper()
        
    def amount_to_text(self, number):
        text = Number2Words().convertNumberToWords(number).upper()
        if text and len(text)>3 and text[:3]=='AND':
            text = text[3:]
        return text
    def tpt_amount_to_text(self, number,invoice_type):
        text = Number2Words().convertNumberToWords(number).upper()
        if text and len(text)>3 and text[:3]=='AND':
            text = text[3:]
        if invoice_type.name=='VVTI Indirect Export':
             if number==0:
                text = 'NIL'
        return text     
    def get_total(self, quantity, price_unit, freight, excise_duty_id, sale_tax_id):
        val = ((quantity*price_unit)+(quantity*price_unit)*(excise_duty_id.amount/100))+(((quantity*price_unit)+(quantity*price_unit)*(excise_duty_id.amount/100))*sale_tax_id.amount/100)+freight
        return round(val)
    
          
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
    
#     def get_qty_bags_gross(self, qty, uom, type):
#         rs = 0.0
#         if uom:
#             unit = uom.replace(' ','')
#             if unit.lower()=='kg' and type == 'domestic':
#                 rs = round(qty/50,2)
#             if unit.lower()=='kg' and type == 'export':
#                 rs = round(qty/25,2)
#             if unit.lower()=='bags':
#                 rs = qty
#             if unit.lower()=='tonne' and type == 'domestic':
#                 rs = round(qty*1000/50,2)
#             if unit.lower()=='tonne' and type == 'export':
#                 rs = round(qty*1000/25,2)
#         return rs
          
    def get_qty_mt1(self, qty, uom, type):
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
        #raise osv.except_osv(_('Warning!%s'),_(format(mt_qty,'.3f')))         
        return format(mt_qty, '.3f') 
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
        return round(mt_qty, 3)
    
    def get_qty_mt2(self, qty, price_unit):
        mt_qty = 0.0
        Net_Amt = qty * price_unit       
        #return "{:,}".format(Net_Amt,'.2f')
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.2f", Net_Amt, grouping=True)
        return inr_comma_format
    def get_amt(self, amt):       
        #return "{:,}".format(amt,'.2f')
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.2f", amt, grouping=True)
        return inr_comma_format
    
    def get_ed_example(self,invoice_line,excise_duty_id,sale_tax_id):
        rate = 0.0
        gross = 0.0
        basic_ed = 0.0
        edu_cess = 0.0
        sec_edu_cess = 0.0
        total = 0.0
        cst = 0.0
        total_amount = 0.0
        for line in invoice_line:
            qty_mt = self.get_qty_mt(line.quantity,line.uos_id.name,'domestic')
            rate = line.price_unit or 0
            gross = round(qty_mt * rate,2)
            basic_ed += round((gross*excise_duty_id/100),2)
        return round(basic_ed,0)
     
    def get_excise_duty_amt(self,qty,unit_price,ed):        
        return round(qty*unit_price*ed/100,0)
    
    def get_excise_duty(self, excise_duty_id):
        return round(excise_duty_id,2)
    
    def get_total_example(self,invoice_line,excise_duty_id,sale_tax_id):
        rate = 0.0
        gross = 0.0
        basic_ed = 0.0
        edu_cess = 0.0
        sec_edu_cess = 0.0
        total = 0.0
        cst = 0.0
        total_amount = 0.0
        for line in invoice_line:
            qty_mt = self.get_qty_mt(line.quantity,line.uos_id.name,'domestic')
            rate = line.price_unit or 0
            gross = round(qty_mt * rate,2)
            basic_ed = round((gross*excise_duty_id/100),2)
            #basic_ed = round((gross*round(excise_duty_id,0)/100),2)
            #edu_cess = round(basic_ed * 2 / 100,2)
            #sec_edu_cess =  round(basic_ed * 1 / 100, 2)
            #total = round(gross + basic_ed + edu_cess + sec_edu_cess, 2)
            total = round(gross + basic_ed, 2)
            cst = round(total * sale_tax_id / 100,2)
            freight = qty_mt * line.freight or 0
            total_amount += round(total + cst + freight, 2)
        return round(total_amount,0)
    def get_subtotal(self,invoice_line,excise_duty_id,sale_tax_id):
        rate = 0.0
        gross = 0.0
        ed = 0.0
        
        total = 0.0
        cst = 0.0
        total_amount = 0.0
        for line in invoice_line:
            qty_mt = line.quantity
            rate = line.price_unit or 0
            gross = round(qty_mt * rate,2)
            ed = round((gross*excise_duty_id/100),2)           
            total = gross + ed
            cst = round(total * sale_tax_id / 100,2)
            freight = qty_mt * line.freight or 0
            total_amount += round(total + cst + freight, 2)
        #return round(total_amount,0)
        #return "{:,}".format(total_amount)
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.2f", round(total_amount), grouping=True)
        return inr_comma_format
    def get_range_label(self,invoice):
        if invoice.cons_loca:
            return "Range"
    def get_loc(self,invoice):
        if invoice.cons_loca:
            return "Division"
    def get_comm(self,invoice):
        if invoice.cons_loca:
            return "Commissionerate"
    def get_ce(self,invoice):
        if invoice.cons_loca:
            return "C.E RC Number"
    def get_ecc(self,invoice):
        if invoice.cons_loca:
            return "E.C.C Number"
    def get_pan(self,invoice):
        if invoice.cons_loca:
            return "PAN Number"
    def get_cst(self,invoice):
        if invoice.cons_loca:
            return "CST Number"
    def get_tin(self,invoice):
        if invoice.cons_loca:
            return "TIN Number"
    def c(self,invoice):
        if invoice.cons_loca:   
            return ":"
    def get_if_freight_lb(self,freight):
        if freight>0:
            return "Freight"
        else:
            return "     "
    def z(self,freight):
        if freight>0:
            return "0"
        else:
            return " "
    def get_s3(self,partner):
        #raise osv.except_osv(_('Warning!%s'),s3)
        if partner.street3:
            return partner.street3+", "+partner.city
        else:
            return partner.city or ''
    def get_if_freight_amt(self,freight):
        if freight>0:
            #raise osv.except_osv(_('Warning!%s'),freight)
            x=0.00
            #raise osv.except_osv(_('Warning!%s'),freight)
            x = int(float(freight))
            #x = format(x, '.2f')  
            return round(x)   
    def get_if_freight_tamt(self,qty, freight):
        #raise osv.except_osv(_('Warning!%s'),freight)
        frt_amt = 0
        if freight>0:
            frt_amt = qty * freight
           # frt_amt = format(frt_amt, '.2f')  
            #return round(frt_amt) 
            locale.setlocale(locale.LC_NUMERIC, "en_IN")
            inr_comma_format = locale.format("%.2f", round(frt_amt), grouping=True)
            return inr_comma_format
            #return "{:,}".format(frt_amt,'.2f')  
        
    
    def get_cst_lb(self,tax_code):
        #raise osv.except_osv(_('Warning!%s'),tax_code[:2])
        if tax_code[:3]=='CST':
            return "CST" 
        if tax_code[:3]=='VAT':
            return "VAT"  
        if tax_code[:3]=='TCS':
            return "TCS" 
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
                    return  '       Opati' + u"\u2122" +' R001'