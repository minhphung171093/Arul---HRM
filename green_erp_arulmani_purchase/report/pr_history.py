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
from green_erp_arulmani_purchase.report.amount_to_text_indian import Number2Words
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
		'get_date_from': self.get_date_from,
        'get_date_to': self.get_date_to,
        'get_invoice':self.get_invoice,
        'convert_date':self.convert_date,
        'convert_date_time':self.convert_date_time,	
		
        })
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = ''
        if wizard_data['date_from']:
            date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)      
            date = date.strftime('%d/%m/%Y')
        return date        
          
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = ''
        if wizard_data['date_to']:
            date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
            date = date.strftime('%d/%m/%Y')
        return date
    
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def convert_date_time(self,date):
        if date:
            date = datetime.strptime(date, DATETIME_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_invoice(self, ind_no):
        res = {}                
        wizard_data = self.localcontext['data']['form']
        indent_no = ind_no.name
        
        #date_from = wizard_data['date_from']
        #date_to = wizard_data['date_to']  
                         
        sql = '''
                    select distinct tpi.date_indent as indentdate,tpi.name as indent_no,pp.name_template as mat_name,pp.default_code as mat_code,
                    tpp.hod_date as hodreldate,tpp.product_uom_qty as indentqty,pu.name as uom,rfql.product_uom_qty as rfqquantity,
                    rfq.rfq_date as rfqdate,rfq.name as rfqname,pol.product_qty as poqty,po.name as purchaseorderno,
                    po.date_order as podate,po.md_approve_date as mdapproveddate,rp.name as vendor,sm.product_qty as grnqty,
                    sp.name as grnno,sp.date as grndate,ai.name as invoiceno,ai.date_invoice as invoicedate,ai.amount_total as invoicetotal                    
                    from tpt_purchase_indent as tpi
                    inner join tpt_purchase_product as tpp on tpi.id = tpp.pur_product_id
                    join product_product pp on pp.id = tpp.product_id
                    inner join product_uom as pu on tpp.uom_po_id=pu.id
                    left join tpt_rfq_line as rfql on tpp.id = rfql.indent_line_id
                    left join tpt_request_for_quotation as rfq on rfql.rfq_id=rfq.id
                    left join purchase_order_line as pol on tpp.pur_product_id=pol.po_indent_no and tpp.description = pol.description
                    left join purchase_order as po on pol.order_id=po.id
                    left join res_partner as rp on po.partner_id=rp.id
                    left join stock_move as sm on tpp.pur_product_id=sm.po_indent_id and tpp.description=sm.description
                    left join stock_picking as sp on sm.picking_id=sp.id and po.id=sp.purchase_id
                    left join account_invoice as ai on sm.picking_id=ai.grn_no
                    where tpi.name = '%s'
                    '''%(indent_no)
                                
        self.cr.execute(sql)
        return self.cr.dictfetchall()


