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
            'get_qty_bags': self.get_qty_bags,
            'get_qty_mt': self.get_qty_mt,
            'get_buyer': self.get_buyer,
        })
    
    def get_invoice_info(self, do_id):
        port_of_loading_name = ''
        port_of_discharge_name = ''
        sql = '''
            select vvt_number, to_char(date_invoice,'yyyy.mm.dd'), vessel_flight_no, port_of_loading_id, 
            port_of_discharge_id, mark_container_no from account_invoice where delivery_order_id = %s
            '''%(do_id)
        self.cr.execute(sql)
        vals = self.cr.dictfetchone()
        port_of_loading_id = vals['port_of_loading_id']
        port_of_discharge_id = vals['port_of_discharge_id']
        self.cr.execute(''' select name from res_country where id = %s '''%(port_of_loading_id))
        res1 = self.cr.fetchone()
        if res1 and res1[0]:
            port_of_loading_name = res1[0]
        self.cr.execute(''' select name from res_country where id = %s '''%(port_of_discharge_id))
        res2 = self.cr.fetchone()
        if res2 and res2[0]:
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
        if uom.lower()=='kg' and type == 'domestic':
            bags_qty = qty/50 + 'NOS OF HDPE LINED BAGS (50KGS BAGS)'
        if uom.lower()=='kg' and type == 'export':
            bags_qty = qty/25 + 'NOS OF HDPE LINED BAGS (25KGS BAGS)'
        if uom.lower()=='bags':
            bags_qty = qty
        if uom.lower()=='mt' and type == 'domestic':
            bags_qty = qty*1000/50 + 'NOS OF HDPE LINED BAGS (50KGS BAGS)'
        if uom.lower()=='mt' and type == 'export':
            bags_qty = qty*1000/25 + 'NOS OF HDPE LINED BAGS (25KGS BAGS)'
        return bags_qty
    
    def get_qty_mt(self, qty, uom, type):
        mt_qty = 0.0
        if uom.lower()=='kg':
            mt_qty = qty/1000
        if uom.lower()=='bags' and type == 'domestic':
            mt_qty = qty*50/1000
        if uom.lower()=='bags' and type == 'export':
            mt_qty = qty*25/1000
        if uom.lower()=='mt':
            mt_qty = qty
        return mt_qty
    
    def get_qty_kg(self, qty, uom, type):
        mt_qty = 0.0
        if uom.lower()=='kg':
            mt_qty = qty
        if uom.lower()=='bags' and type == 'domestic':
            mt_qty = qty*50
        if uom.lower()=='bags' and type == 'export':
            mt_qty = qty*25
        if uom.lower()=='mt':
            mt_qty = qty*1000
        return mt_qty
    
    def get_buyer(self, obj):
        buyer = ''
        if obj.partner_id and obj.cons_loca and obj.partner_id.id != obj.cons_loca.id:
            buyer = (obj.cons_loca and obj.cons_loca.street or '') + ', ' + (obj.cons_loca and obj.cons_loca.street2 or '') + ', ' + (obj.cons_loca and obj.cons_loca.city or '') + ', ' + (obj.cons_loca and (obj.cons_loca.state_id and obj.cons_loca.state_id.name or '') or '') + ', ' + (obj.cons_loca and (obj.cons_loca.country_id and obj.cons_loca.country_id.name or '') or '') + ', ' + (obj.cons_loca and obj.cons_loca.zip or '')
        return buyer
    

    