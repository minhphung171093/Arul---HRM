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
from xlwt import Row
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.cols = []
        self.rows = []
        self.data_dict = {}
        self.total_dict = {}
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_data': self.get_data,
            'get_lines': self.get_lines,
            'get_cols': self.get_cols,
            'get_cost_center_name': self.get_cost_center_name,
            'get_cell': self.get_cell,
            'get_total_cell': self.get_total_cell,
        })
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_data(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        department_id = wizard_data['department_id']
        section_id = wizard_data['section_id']
        cost_center_ids = wizard_data['cost_center_ids']
        sql = '''
            select ai.date_invoice as date, ai.cost_center_id as cost_center_id,
                case when sum(ai.amount_untaxed)!=0 then sum(ai.amount_untaxed) else 0 end amount_untaxed
                from account_invoice ai
                left join purchase_order po on ai.purchase_id=po.id
                where ((ai.type='in_invoice' and ai.doc_type='service_invoice' and po.po_document_type='service') or (ai.doc_type='supplier_invoice_without' and ai.purchase_id is null))
                    and ai.state in ('open','paid') and ai.cost_center_id is not null 
        '''
        if date_from:
            sql += '''
                and ai.date_invoice>='%s'
            '''%(date_from)
        if date_to:
            sql += '''
                and ai.date_invoice<='%s'
            '''%(date_to)
        if cost_center_ids:
            cost_center_ids = str(cost_center_ids).replace('[', '(')
            cost_center_ids = str(cost_center_ids).replace(']', ')')
            sql += '''
                and ai.cost_center_id in %s
            '''%(cost_center_ids)
        sql += '''
            group by ai.date_invoice, ai.cost_center_id
            order by ai.date_invoice
        '''
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            if line['date'] not in self.rows:
                self.rows.append(line['date'])
            if line['cost_center_id'] not in self.cols:
                self.cols.append(line['cost_center_id'])
            
            if self.data_dict.get(line['date'], False):
                if self.data_dict[line['date']].get(line['cost_center_id'], False):
                    self.data_dict[line['date']][line['cost_center_id']] += line['amount_untaxed']
                else:
                    self.data_dict[line['date']][line['cost_center_id']] = line['amount_untaxed']
            else:
                self.data_dict[line['date']] = {line['cost_center_id']: line['amount_untaxed']}
                
        sql = '''
            select mi.date_expec as date, mi.cost_center_id as cost_center_id,
                case when sum(COALESCE(sm.product_qty,0)*COALESCE(sm.price_unit,0))!=0 then sum(COALESCE(sm.product_qty,0)*COALESCE(sm.price_unit,0)) else 0 end amount_untaxed
                from stock_move sm
                left join tpt_material_issue mi on sm.issue_id=mi.id
                where sm.state in ('done') and mi.cost_center_id is not null 
        '''
        if date_from:
            sql += '''
                and mi.date_expec>='%s'
            '''%(date_from)
        if date_to:
            sql += '''
                and mi.date_expec<='%s'
            '''%(date_to)
        if cost_center_ids:
            cost_center_ids = str(cost_center_ids).replace('[', '(')
            cost_center_ids = str(cost_center_ids).replace(']', ')')
            sql += '''
                and mi.cost_center_id in %s
            '''%(cost_center_ids)
        sql += '''
            group by mi.date_expec, mi.cost_center_id
            order by mi.date_expec
        '''
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            if line['date'] not in self.rows:
                self.rows.append(line['date'])
            if line['cost_center_id'] not in self.cols:
                self.cols.append(line['cost_center_id'])
            
            if self.data_dict.get(line['date'], False):
                if self.data_dict[line['date']].get(line['cost_center_id'], False):
                    self.data_dict[line['date']][line['cost_center_id']] += line['amount_untaxed']
                else:
                    self.data_dict[line['date']][line['cost_center_id']] = line['amount_untaxed']
            else:
                self.data_dict[line['date']] = {line['cost_center_id']: line['amount_untaxed']}
                
        return True
    
    def get_lines(self):
        res = self.rows
        res = sorted(res)
        return res
    
    def get_cols(self):
        return self.cols
    
    def get_cost_center_name(self, cost_center_id):
        if cost_center_id:
            cost_center = self.pool.get('tpt.cost.center').browse(self.cr, self.uid, cost_center_id)
            return cost_center.name+' ('+cost_center.code+')'
        return ''
    
    def get_cell(self, row, col):
        if self.data_dict.get(row, False):
            if self.data_dict[row].get(col, False):
                res = self.data_dict[row][col]
                if self.total_dict.get(col, False):
                    self.total_dict[col] += res
                else:
                    self.total_dict[col] = res
                return res
        return 0
    
    def get_total_cell(self, col):
        if self.total_dict.get(col, False):
            return self.total_dict[col]
        return 0
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

