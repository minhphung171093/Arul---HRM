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
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_opening_stock': self.get_opening_stock,
            'get_detail_lines': self.get_detail_lines,
            'get_posting_date': self.get_posting_date,
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_opening_stock(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        sql = '''
            select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move  
            where product_id = %s and picking_id in (select id from stock_picking where date < '%s' and state = 'done' and type = 'in')
        '''%(product_id[0], date_from)
        self.cr.execute(sql)
        product_qty = self.cr.dictfetchone()['product_qty']
         
        sql = '''
            select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
            where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
        '''%(product_id[0], date_from)
        self.cr.execute(sql)
        product_isu_qty = self.cr.dictfetchone()['product_isu_qty']
        opening_stock = product_qty-product_isu_qty
        return opening_stock
    
    def get_detail_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        sql = '''
            select * from account_move where doc_type in ('freight', 'good', 'grn') and state = 'posted' and date between '%s' and '%s'
        '''%(date_from, date_to)
        self.cr.execute(sql)
        return self.cr.dictfetchall()
    
    def get_posting_date(self, move_id, type, issue_id):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        date = []
        if type == 'freight':
            sql = '''
                select ail.product_id as product_id, ai.date_invoice as date_invoice from account_invoice ai, account_invoice_line ail where ail.invoice_id = ai.id and ai.move_id = %s and ai.state != 'draft'
            '''%(move_id)
            self.cr.execute(sql)
            for data in self.cr.dictfetchall():
                if product_id[0] == data['product_id']:
                    date = data['date_invoice']
        if type == 'good':
            if issue_id:
                sql = '''
                    select mil.product_id as product_id, mi.date_expec as date_expec from tpt_material_issue mi, tpt_material_issue_line mil where mil.material_issue_id=mi.id and mi.id = %s and mi.state = 'done'
                '''%(issue_id)
                self.cr.execute(sql)
                for data in self.cr.dictfetchall():
                    if product_id[0] == data['product_id']:
                        date = data['date_expec']
        return date
                    
        
            
        

        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

