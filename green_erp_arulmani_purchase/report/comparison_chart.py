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
            'get_vendor': self.get_vendor,
            'get_disc':self.get_disc,
            'get_info': self.get_info,
            'is_bold': self.is_bold,
            'get_date':self.get_date,
            'get_supplier_code_name': self.get_supplier_code_name,
        })
    
    def get_vendor(self,o,num,line):
        res = {
               'rate': 0,
               'value': 0,
               'disc': 0,
               }
        quotation_obj = self.pool.get('tpt.purchase.quotation')
        quotation_line_obj = self.pool.get('tpt.purchase.quotation.line')
        sql = '''
            select id from tpt_purchase_quotation where comparison_chart_id = %s and tpt_purchase_quotation.select = 'True' order by amount_net,id
        '''%(o.id)
        self.cr.execute(sql)
        quotation_ids = [row[0] for row in self.cr.fetchall()]
        if len(quotation_ids)>=num:
            quotation_line_ids = quotation_line_obj.search(self.cr, self.uid, [('purchase_quotation_id','=',quotation_ids[num-1]),('po_indent_id','=',line.po_indent_id.id),('product_id','=',line.product_id.id),('product_uom_qty','=',line.product_uom_qty),('uom_id','=',line.uom_id.id)], limit=1)
            if quotation_line_ids:
                quotation_line = quotation_line_obj.browse(self.cr, self.uid, quotation_line_ids[0])
                res.update({
                   'rate': quotation_line.price_unit,
                   'value': (quotation_line.price_unit*quotation_line.product_uom_qty),
                   'disc': (quotation_line.price_unit*quotation_line.product_uom_qty)*quotation_line.disc/100,
                   })
        return res
    def get_disc(self,o,num):
        disc = 0
        value = 0
        for line in o.name.rfq_line:
            value += self.get_vendor(o, num, line)['value']
            disc += self.get_vendor(o, num, line)['disc']
        return {
               'disc':disc,
               'sum_value':value,
               }
    
    def is_bold(self,o,r,line):
        rate = []
        for i in range(1,5):
            rate_val = self.get_vendor(o, i, line)['rate']
            if rate_val:
                rate.append(rate_val)
        m = min(rate)
        if r and m==r:
            return True
        return False
    
    def get_info(self,o,num):
        quotation_obj = self.pool.get('tpt.purchase.quotation')
        sql = '''
            select id from tpt_purchase_quotation where comparison_chart_id = %s and tpt_purchase_quotation.select = 'True' order by amount_net,id
        '''%(o.id)
        self.cr.execute(sql)
        quotation_ids = [row[0] for row in self.cr.fetchall()]
        if len(quotation_ids)>=num:
            return quotation_obj.browse(self.cr, self.uid,quotation_ids[num-1])
        else:
            return False
        
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')     
           
    def get_supplier_code_name(self, supplier_id=False):
        code_name = ""
        if supplier_id:
            code_name = supplier_id.vendor_code + "-"  + supplier_id.name
        return code_name    
        
        
        
           
        
        
        
        