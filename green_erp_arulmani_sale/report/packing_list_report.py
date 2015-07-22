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
            'get_invoice_info':self.get_invoice_info,
            'get_invoice_line_info':self.get_invoice_line_info,
            'get_date': self.get_date,
            'get_qty_bags': self.get_qty_bags,
            'get_qty_mt': self.get_qty_mt,
            'get_qty_kg':self.get_qty_kg,
            'get_buyer': self.get_buyer,
            'get_consignee': self.get_consignee,
            'get_stock_line': self.get_stock_line,
            'get_s3':self.get_s3,
            'get_s1_s2':self.get_s1_s2,
            'get_s3_city_zip':self.get_s3_city_zip,
            'get_state_country':self.get_state_country,
        })
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
        #raise osv.except_osv(_('Warning!%s'),partner.state_id.name)
        if partner:
            if partner.state_id.name:
                if (partner.state_id.name).replace(" ", ""):
                    return partner.state_id.name+", "+partner.country_id.name
                else:
                    return partner.country_id.name
    def get_s3(self,partner):
        if partner.street3:
            return partner.street3+", "+partner.city
        else:
            return partner.city
    def get_s3(self,partner):
        #raise osv.except_osv(_('Warning!%s'),s3)
        if partner.street3:
            return partner.street3+", "+partner.city
        else:
            return partner.city
    def get_stock_line(self, lines):
        prod_qty=0
        qty=0
        for line in lines:           
            qty=line.product_qty
            qty = qty + qty
        #raise osv.except_osv(_('Warning!'),_(i))    
        
        return qty
    def get_invoice_info(self, do_id):
        port_of_loading_name = ''
        port_of_discharge_name = ''
        disc_goods = ''
        final_desti = ''
        country_dest = ''
        tod_place = ''
        lc_no = ''
        payment_term = ''
        gross_weight = 0
        sql = '''
            select vvt_number, to_char(date_invoice,'dd/mm/yyyy'), vessel_flight_no, port_of_loading_id, 
            port_of_discharge_id, mark_container_no, invoice_type,disc_goods,final_desti,country_dest,
            tod_place,lc_no,payment_term,case when gross_weight>0 then gross_weight else 0 end gross_weight  from account_invoice where delivery_order_id = %s
            '''%(do_id)
        self.cr.execute(sql)
        vals = self.cr.dictfetchone()
        #raise osv.except_osv(_('Warning!'),_(sql))    
        port_of_loading_id = vals['port_of_loading_id']
        port_of_discharge_id = vals['port_of_discharge_id']
        disc_goods = vals['disc_goods']
        final_desti = vals['final_desti']
        country_dest = vals['country_dest']
        tod_place = vals['tod_place']
        lc_no = vals['lc_no']
        temp_pay = vals['payment_term'] 
        gross_weight = vals['gross_weight']
        #inv_id = vals[0]
        port_of_loading_name = port_of_loading_id
        port_of_discharge_name = port_of_discharge_id
        if temp_pay:
            sql = '''
            select name from account_payment_term where id=%s
            '''%temp_pay
            self.cr.execute(sql)
            vals1 = self.cr.dictfetchone()
            payment_term = vals1['name']
        #=======================================================================
        # sql = '''
        # select quantity from account_invoice_line where invoice_id = %s
        # '''%1
        # self.cr.execute(sql)
        # vals = self.cr.dictfetchone()
        # qty = vals['quantity']
        #=======================================================================
        
        #=======================================================================
        # if port_of_loading_id:
        #     self.cr.execute(''' select name from res_country where id = %s '''%(port_of_loading_id))
        #     res1 = self.cr.fetchone()
        #     port_of_loading_name = res1[0]
        # if port_of_discharge_id:
        #     self.cr.execute(''' select name from res_country where id = %s '''%(port_of_discharge_id))
        #     res2 = self.cr.fetchone()
        #     port_of_discharge_name = res2[0]
        #=======================================================================
        vals.update({
                     'port_of_loading_id':port_of_loading_name,
                     'port_of_discharge_id':port_of_discharge_name,
                     'disc_goods':disc_goods,
                     'final_desti':final_desti,
                     'country_dest':country_dest,
                     'tod_place':tod_place,
                     'lc_no':lc_no,
                     'payment_term':payment_term,
                     'gross_weight':"{:,}".format(int(gross_weight)),# int(gross_weight),
                     #'qty':qty,
                     }) 
        return vals
    def get_invoice_line_info(self, do_id):
        qty = 0
        sql = '''
            select id from account_invoice where delivery_order_id = %s
            '''%(do_id)
        self.cr.execute(sql)
        vals = self.cr.dictfetchone()
         
        
        inv_id = vals['id']
        
        #raise osv.except_osv(_('Warning!'),_(inv_id))   
        sql = '''
        select quantity from account_invoice_line where invoice_id = %s
        '''%inv_id
        self.cr.execute(sql)
        vals = self.cr.dictfetchone()
        qty = vals['quantity']
        qty = qty * 1000
        vals.update({
                     'qty':"{:,}".format(int(qty)),
                     })
        return vals
    def get_date(self, date=False): 
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
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
        return mt_qty
    
    def get_qty_kg(self, qty, uom, type):
        mt_qty = 0.0
        if uom:
            unit = uom.replace(' ','')
            if unit.lower() in ['kg','kgs']:
                mt_qty = qty
            if unit.lower()=='bags' and type == 'domestic':
                mt_qty = qty*50
            if unit.lower()=='bags' and type == 'export':
                mt_qty = qty*25
            if unit.lower() in ['tonne','tonnes','mt','metricton','metrictons']:
                mt_qty = qty*1000
        return mt_qty
    
    def get_consignee(self, obj):
        cons = ''
        if obj.partner_id:
            if obj.partner_id.name:
                cons += obj.partner_id.name  + ' & '
            if obj.partner_id.street:
                cons += obj.partner_id.street + ', '
            if obj.partner_id.street2:
                cons += obj.partner_id.street2 + ', '
            if obj.partner_id.city:
                cons += obj.partner_id.city + ', '
            if obj.partner_id.state_id:
                cons += obj.partner_id.state_id.name + ', '
            if obj.partner_id.country_id:
                cons += obj.partner_id.country_id.name  + ', '
            if obj.partner_id.zip:
                cons += obj.partner_id.zip
        return cons
    
    def get_buyer(self, obj):
        buyer = ''
        if obj.partner_id and obj.cons_loca and obj.partner_id.id != obj.cons_loca.id:
            if obj.cons_loca:
                if obj.cons_loca.street:
                    buyer += obj.cons_loca.street + ', '
                if obj.cons_loca.street2:
                    buyer += obj.cons_loca.street2 + ', '
                if obj.cons_loca.city:
                    buyer += obj.cons_loca.city + ', '
                if obj.cons_loca.state_id:
                    buyer += obj.cons_loca.state_id.name + ', '
                if obj.cons_loca.country_id:
                    buyer += obj.cons_loca.country_id.name  + ', '
                if obj.cons_loca.zip:
                    buyer += obj.cons_loca.zip
#             buyer = (obj.cons_loca and obj.cons_loca.street or '') + ', ' + (obj.cons_loca and obj.cons_loca.street2 or '') + ', ' + (obj.cons_loca and obj.cons_loca.city or '') + ', ' + (obj.cons_loca and (obj.cons_loca.state_id and obj.cons_loca.state_id.name or '') or '') + ', ' + (obj.cons_loca and (obj.cons_loca.country_id and obj.cons_loca.country_id.name or '') or '') + ', ' + (obj.cons_loca and obj.cons_loca.zip or '')
        return buyer
    

    