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
            'get_date': self.get_date,
            'get_qty_bags': self.get_qty_bags,
            'get_qty_mt': self.get_qty_mt,
            'get_qty_kg':self.get_qty_kg,
            'get_buyer': self.get_buyer,
            'get_consignee': self.get_consignee,
        })
    
    def get_invoice_info(self, do_id):
        port_of_loading_name = ''
        port_of_discharge_name = ''
        sql = '''
            select vvt_number, to_char(date_invoice,'yyyy.mm.dd'), vessel_flight_no, port_of_loading_id, 
            port_of_discharge_id, mark_container_no, invoice_type from account_invoice where delivery_order_id = %s
            '''%(do_id)
        self.cr.execute(sql)
        vals = self.cr.dictfetchone()
        port_of_loading_id = vals['port_of_loading_id']
        port_of_discharge_id = vals['port_of_discharge_id']
        if port_of_loading_id:
            self.cr.execute(''' select name from res_country where id = %s '''%(port_of_loading_id))
            res1 = self.cr.fetchone()
            port_of_loading_name = res1[0]
        if port_of_discharge_id:
            self.cr.execute(''' select name from res_country where id = %s '''%(port_of_discharge_id))
            res2 = self.cr.fetchone()
            port_of_discharge_name = res2[0]
        vals.update({
                     'port_of_loading_id':port_of_loading_name,
                     'port_of_discharge_id':port_of_discharge_name,
                     }) 
        return vals
    
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
            if unit.lower()=='kg':
                mt_qty = qty/1000
            if unit.lower()=='bags' and type == 'domestic':
                mt_qty = qty*50/1000
            if unit.lower()=='bags' and type == 'export':
                mt_qty = qty*25/1000
            if unit.lower()=='tonne':
                mt_qty = qty
        return mt_qty
    
    def get_qty_kg(self, qty, uom, type):
        mt_qty = 0.0
        if uom:
            unit = uom.replace(' ','')
            if unit.lower()=='kg':
                mt_qty = qty
            if unit.lower()=='bags' and type == 'domestic':
                mt_qty = qty*50
            if unit.lower()=='bags' and type == 'export':
                mt_qty = qty*25
            if unit.lower()=='tonne':
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
    

    