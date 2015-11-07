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
            'convert_date': self.convert_date,
            'convert_date_time': self.convert_date_time,
            'get_move': self.get_move,
            'get_line': self.get_line,
            'get_amt': self.get_amt,
        })
    #commentted by TPT-P
    def get_amt(self, amt):          
        locale.setlocale(locale.LC_NUMERIC, "en_IN")
        inr_comma_format = locale.format("%.3f", amt, grouping=True)
        return inr_comma_format
    
    def get_line(self, header_id):
        if header_id:
            sql = '''
            select sm.si_no as si_no, pi.name indent_no,emp.name_related req, pp.default_code code, sm.description as description, 
            case when sm.action_taken='direct' then 'Direct Stock Update' 
            when sm.action_taken = 'need' then 'Need Inspection'  
            when sm.action_taken = 'move' then 'Move to Consumption' end doc_type,
            sm.product_qty,pu.name as product_uom,sm.bin_location
            from stock_move sm
            inner join tpt_purchase_indent pi on sm.po_indent_id=pi.id
            inner join product_product pp on sm.product_id=pp.id
            --inner join product_template pt on pp.id=pt.id
            left join product_uom pu on (pu.id = sm.product_uom)
            left join hr_employee emp on pi.requisitioner=emp.id
            
            where picking_id=%s
            order by si_no 
            '''%header_id.id
            #inner join stock_picking sp on sm.picking_id=sp.id
            self.cr.execute(sql)
            #return 
            res = []
            si_no = 1
            for line in self.cr.dictfetchall():
                res.append({
                            'si_no': si_no or '',# line['si_no'] or '',
                            'indent_no':line['indent_no'] or '',
                            'req':line['req'] or '',
                            'code':line['code'] or '',
                            'description':line['description'] or '',
                            'doc_type':line['doc_type'] or '',
                            'product_qty':self.get_amt(line['product_qty']) or 0.000,
                            'product_uom':line['product_uom'] or '',
                            'bin_location':line['bin_location'] or '',
                            
                            
                            })
                si_no = si_no + 1
            return res
    
    
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def convert_date_time(self, date):
        if date:
            date = datetime.strptime(date, DATETIME_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_move(self,move):
        res = ''
        if move == 'direct':
            res = 'Direct Stock Update'
        elif move == 'move':
            res = 'Move to Consumption'
        else:
            res = 'Need Inspection'
        return res
    

    