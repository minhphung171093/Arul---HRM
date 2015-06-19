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
from datetime import date
from dateutil.rrule import rrule, DAILY

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.current = 0
        self.num_call_grn = {'grn_name':'','num':-1}
        self.transaction_qty = 0
        self.current_transaction_qty = 0
        self.id = 0
        self.id2 = 0
        self.id3 = 0
        self.st_sum_value = 0
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_opening_stock': self.get_opening_stock,
            'get_detail_lines': self.get_detail_lines,
            'get_doc_type': self.get_doc_type,
            'get_account_move_line': self.get_account_move_line,
            'get_transaction_qty': self.get_transaction_qty,
            'get_opening_stock_value': self.get_opening_stock_value,
            'get_closing_stock': self.get_closing_stock,
            'get_line_stock_value': self.get_line_stock_value,
            'closing_value': self.closing_value,
            'stock_value':self.stock_value,
            'get_line_current_material':self.get_line_current_material,
            'sum_trans_qty': self.sum_trans_qty,
            'get_true_trans_qty': self.get_true_trans_qty,
            'get_lines': self.get_lines,
        })
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
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
        product = sel.pool.get('product.product').browse(self.cr, self.uid, product_id[0])
        categ = product.categ_id.cate_name
        if categ=='raw': 
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end product_qty
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s
                            and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where date <'%s' and state = 'done')))
                                )
                '''%(locat_ids[0], product_id[0],date_from,date_from,date_from)
            self.cr.execute(sql)
            product_qty = self.cr.dictfetchone()['product_qty']
            
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
            '''%(product_id[0], date_from)
            self.cr.execute(sql)
            product_isu_qty = self.cr.dictfetchone()['product_isu_qty']
            opening_stock = product_qty-product_isu_qty
            
        if categ=='spares': 
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])]) 
            sql = '''
                select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end product_qty
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s
                            and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where date <'%s' and state = 'done')))
                                )
                '''%(locat_ids[0], product_id[0],date_from,date_from,date_from)
            self.cr.execute(sql)
            product_qty = self.cr.dictfetchone()['product_qty']
            
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
            '''%(product_id[0], date_from)
            self.cr.execute(sql)
            product_isu_qty = self.cr.dictfetchone()['product_isu_qty']
            opening_stock = product_qty-product_isu_qty
        return round(opening_stock,2)
     
    def get_closing_stock(self, get_detail_lines):
        closing = 0
        qty_grn = 0
        qty_good = 0
        for line in get_detail_lines:
            if line['doc_type']=='grn':
                if self.id2 != line['id']:
                    self.num_call_grn = {'grn_name':'','num':-1}
                    self.id2 = line['id']
                qty_grn += self.get_transaction_qty(line['id'], line['material_issue_id'], line['doc_type'])
            if line['doc_type']=='good':
                if self.id2 != line['id']:
                    self.num_call_grn = {'grn_name':'','num':-1}
                    self.id2 = line['id']
                qty_good += self.get_transaction_qty(line['id'], line['material_issue_id'], line['doc_type'])
        closing = qty_grn + qty_good
        return closing
        
    
    def get_detail_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        sql = '''
            select * from account_move where doc_type in ('freight', 'good', 'grn') and date between '%(date_from)s' and '%(date_to)s'
                and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                    or (LEFT(name,17) in (select name from stock_picking where id in (select picking_id from stock_move where product_id=%(product_id)s)))
                ) or material_issue_id in (select id from tpt_material_issue where id in (select material_issue_id from tpt_material_issue_line where product_id=%(product_id)s)) 
                    ) order by date, id
        '''%{'date_from':date_from,
             'date_to':date_to,
             'product_id':product_id[0]}
        self.cr.execute(sql)
        move_line = []
        for line in self.cr.dictfetchall():
            if line['doc_type'] != 'grn':
                move_line.append(line)
            else:
                parent_ids_raw = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
                locat_ids_raw = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
                parent_ids_spares = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
                locat_ids_spares = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
                sql = '''
                    select * from stock_move
                    where picking_id in (select id from stock_picking where (warehouse = %s or warehouse = %s) and name in (select LEFT(name,17) from account_move_line where move_id = %s) and product_id = %s)
                '''%(locat_ids_raw[0], locat_ids_spares[0], line['id'], product_id[0])
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    if move['action_taken'] == 'direct':
                        move_line.append(line)
                    if move['action_taken'] == 'need':
                        sql = '''
                            select remaining_qty from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                        '''%(move['id'])
                        self.cr.execute(sql)
                        move_sql = self.cr.fetchone()
                        if move_sql:
                            move_line.append(line)
        return move_line    
            
    def get_lines(self):
        stock_in_out_line = []
        for line in self.get_detail_lines():
            trans_qty = self.get_transaction_qty(line['id'], line['material_issue_id'], line['doc_type'])
            if line['doc_type']=='good':
                qty = 0
                value = 0
                for l in stock_in_out_line:
                    qty += l['transaction_quantity']
                    value += l['stock_value']
                st = qty and value/qty or 0
                st_value = st*trans_qty
            else:
                st_value = self.stock_value(self.get_line_stock_value(line['id'], line['material_issue_id'], line['doc_type'], line['date']), line)
            self.st_sum_value += st_value
            stock_in_out_line.append({
                'creation_date': line['date'],
                'date': line['date'],
                'id': line['id'],
                'name': line['name'],
                'doc_type': line['doc_type'],
                'posting_date': line['date'],
                'document_no': self.get_account_move_line(line['id']),
                'gl_document_no': line['name'],
                'document_type': self.get_doc_type(line['doc_type']),
                'transaction_quantity': trans_qty,
                'stock_value': st_value,
                'material_issue_id': line['material_issue_id'],
                'current_material_value':self.get_line_current_material(self.stock_value(self.get_line_stock_value(line['id'], line['material_issue_id'], line['doc_type'], line['date']), line)),
            })
        return stock_in_out_line
    
    def closing_value(self):
#         closing = 0
#         for line in get_detail_lines:
# #             if len(get_detail_lines) <= 1:
#             if self.id3 != line['id']:
#                 self.num_call_grn = {'grn_name':'','num':-1}
#                 self.id3 = line['id']
#             qty = self.get_transaction_qty(line['id'], line['material_issue_id'], line['doc_type'])
#             if line['doc_type']=='freight':
#                 qty=1
#             value = self.get_line_stock_value(line['id'], line['material_issue_id'], line['doc_type'], line['date'])
#             closing += qty * value
        self.get_lines()
        return self.st_sum_value+ self.get_opening_stock_value()
    
    def sum_trans_qty(self, get_detail_lines):
        sum = 0
        for line in get_detail_lines:
#             if len(get_detail_lines) <= 1:
            self.num_call_grn = {'grn_name':'','num':-1}
            qty = self.get_transaction_qty(line['id'], line['material_issue_id'], line['doc_type'])
            sum += qty
        return sum
        
    
    def stock_value(self, value, line):
        if line['doc_type']=='freight':
            self.current_transaction_qty = 1
        return self.current_transaction_qty*value
    
    def get_line_current_material(self,stock_value):  
        cur = self.get_opening_stock_value()+stock_value+self.current
        self.current = cur
        return cur
        
    
    def get_account_move_line(self, move_id):
        move = self.pool.get('account.move').browse(self.cr,self.uid,move_id)
        move_line = move.line_id[0]
        return move_line and move_line.name or ''
    
    def get_line_grn(self, move_id, move_type):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        quantity = 0
        if move_type == 'grn':
            sql = '''
                select * from stock_move
                where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s) and product_id = %s)
                group by product_id 
            '''%(move_id, product_id[0])
            self.cr.execute(sql)
            return self.cr.dictfetchall()
    
    def get_true_trans_qty(self, line, get_detail_lines):
#         if len(get_detail_lines) == 1:
        
        if self.id != line['id']:
            self.num_call_grn = {'grn_name':'','num':-1}
            self.id = line['id']
        return self.get_transaction_qty(line['id'], line['material_issue_id'], line['doc_type'])
    
    
    def get_transaction_qty(self, move_id, material_issue_id, move_type):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        product_id = wizard_data['product_id']
        product = sel.pool.get('product.product').browse(self.cr, self.uid, product_id[0])
        categ = product.categ_id.cate_name
        quantity = 0
        if categ=='raw':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            if move_type == 'freight':
                quantity = 0
            if move_type == 'good':
                sql = '''
                    select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                    where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                    group by product_id 
                '''%(material_issue_id, locat_ids[0], product_id[0])
                self.cr.execute(sql)
                for qty in self.cr.dictfetchall():
                    quantity = qty['product_isu_qty']
            if move_type == 'grn':
                sql = '''
                    select * from stock_move
                    where picking_id in (select id from stock_picking where warehouse = %s and name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
                    and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                '''%(locat_ids[0], move_id, product_id[0])
                self.cr.execute(sql)
                moves = self.cr.dictfetchall()
                grn_name = self.get_account_move_line(move_id)
                if self.num_call_grn['grn_name']==grn_name:
                    self.num_call_grn['num'] += 1
                else:
                    self.num_call_grn['grn_name']=grn_name
                    self.num_call_grn['num'] = 0
                if len(moves)>self.num_call_grn['num']:
                    move = moves[self.num_call_grn['num']]
                    if move['action_taken'] == 'direct':
                        quantity = move['product_qty']
                    if move['action_taken'] == 'need':
                        sql1 = '''
                            select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                        '''%(move['id'])
                        self.cr.execute(sql1)
                        need = self.cr.dictfetchone()
                        if need:
                            quantity = need['qty_approve'] or 0
        if categ=='spares':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
            if move_type == 'freight':
                quantity = 0
            if move_type == 'good':
                sql = '''
                    select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                    where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                    group by product_id 
                '''%(material_issue_id, locat_ids[0], product_id[0])
                self.cr.execute(sql)
                for qty in self.cr.dictfetchall():
                    quantity = qty['product_isu_qty']
            if move_type == 'grn':
                sql = '''
                    select * from stock_move
                    where picking_id in (select id from stock_picking where warehouse = %s and name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
                    and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                '''%(locat_ids[0], move_id, product_id[0])
                self.cr.execute(sql)
                moves = self.cr.dictfetchall()
                grn_name = self.get_account_move_line(move_id)
                if self.num_call_grn['grn_name']==grn_name:
                    self.num_call_grn['num'] += 1
                else:
                    self.num_call_grn['grn_name']=grn_name
                    self.num_call_grn['num'] = 0
                if len(moves)>self.num_call_grn['num']:
                    move = moves[self.num_call_grn['num']]
                    if move['action_taken'] == 'direct':
                        quantity = move['product_qty']
                    if move['action_taken'] == 'need':
                        sql1 = '''
                            select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                        '''%(move['id'])
                        self.cr.execute(sql1)
                        need = self.cr.dictfetchone()
                        if need:
                            quantity = need['qty_approve'] or 0
        self.transaction_qty += quantity
        self.current_transaction_qty = quantity
        return quantity
        
    
    def get_doc_type(self, doc_type):
        if doc_type == 'freight':
            return 'Freight Invoice'
        if doc_type == 'good':
            return 'Good Issue'
        if doc_type == 'grn':
            return 'GRN'
        
    def get_opening_stock_value(self):
       wizard_data = self.localcontext['data']['form']
       date_from = wizard_data['date_from']
       date_to = wizard_data['date_to']
       product_id = wizard_data['product_id']
       product = sel.pool.get('product.product').browse(self.cr, self.uid, product_id[0])
       categ = product.categ_id.cate_name
       opening_stock_value = 0
       freight_cost = 0
       if categ=='raw':
           parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
           locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
           sql = '''
               select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s
                            and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                )
           '''%(locat_ids[0], product_id[0], date_from, date_from, date_from)
           self.cr.execute(sql)
           inventory = self.cr.dictfetchone()
           if inventory:
               hand_quantity = inventory['ton_sl'] or 0
               total_cost = inventory['total_cost'] or 0
               avg_cost = hand_quantity and total_cost/hand_quantity or 0
               sql = '''
                   select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                       from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and state='done') and product_id=%s
               '''%(date_from,product_id[0])
               self.cr.execute(sql)
               product_isu_qty = self.cr.fetchone()[0]
               sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where date_invoice < '%s' and sup_inv_id is not null)
                       group by product_id
               '''%(product_id[0], date_from)
               self.cr.execute(sql)
               for inventory in self.cr.dictfetchall():
                   freight_cost = inventory['line_net'] or 0
               opening_stock_value = total_cost-(product_isu_qty*avg_cost) + freight_cost
       if categ=='spares':
           parent_ids = self.pool.get('stock.location').search(self.cr,self. uid, [('name','=','Store'),('usage','=','view')])
           locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
           sql = '''
               select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s
                            and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                )
           '''%(locat_ids[0], product_id[0], date_from, date_from, date_from)
           self.cr.execute(sql)
           inventory = self.cr.dictfetchone()
           if inventory:
               hand_quantity = inventory['ton_sl'] or 0
               total_cost = inventory['total_cost'] or 0
               avg_cost = hand_quantity and total_cost/hand_quantity or 0
               sql = '''
                   select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                       from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and state='done') and product_id=%s
               '''%(date_from,product_id[0])
               self.cr.execute(sql)
               product_isu_qty = self.cr.fetchone()[0]
               sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where date_invoice < '%s' and sup_inv_id is not null)
                       group by product_id
               '''%(product_id[0], date_from)
               self.cr.execute(sql)
               for inventory in self.cr.dictfetchall():
                   freight_cost = inventory['line_net'] or 0
               opening_stock_value = total_cost-(product_isu_qty*avg_cost) + freight_cost
       return opening_stock_value
    
    def get_line_stock_value(self, move_id, material_issue_id, move_type, date):
       wizard_data = self.localcontext['data']['form']
       date_from = wizard_data['date_from']
       date_to = wizard_data['date_to']
       product_id = wizard_data['product_id']
       product = sel.pool.get('product.product').browse(self.cr, self.uid, product_id[0])
       categ = product.categ_id.cate_name
       opening_stock_value = 0
       hand_quantity = 0
       total_cost = 0
       avg_cost = 0
       if categ=='raw':
           parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
           locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
           if move_type == 'freight':
               sql = '''
                   select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                   where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                   group by product_id
               '''%(product_id[0], move_id)
               self.cr.execute(sql)
               for inventory in self.cr.dictfetchall():
                   avg_cost = inventory['line_net'] or 0
           
           if move_type == 'grn':
               sql = '''
                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                           and st.location_dest_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s')
                           
                   '''%(product_id[0], locat_ids[0], date)
               self.cr.execute(sql)
               inventory = self.cr.dictfetchone()
               if inventory:
                   hand_quantity = inventory['ton_sl'] or 0
                   total_cost = inventory['total_cost'] or 0
               sql = '''
                   select * from stock_move where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s))
               '''%(move_id) 
               self.cr.execute(sql)
               for line in self.cr.dictfetchall():
                   if line['action_taken'] == 'need':
                       sql = '''
                           select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                       '''%(line['id'])
                       self.cr.execute(sql)
                       inspec = self.cr.dictfetchone()
                       if inspec:
                           hand_quantity += inspec['qty_approve'] or 0
                           total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
               avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           
           if move_type == 'good':
               good = self.pool.get('tpt.material.issue').browse(cr,uid,material_issue_id)
               sql = '''
                        select case when sum(-1*st.product_qty)!=0 then sum(-1*st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                        and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                           
                   '''%(product_id[0], locat_ids[0], good.date_expec)
               self.cr.execute(sql)
               inventory = self.cr.dictfetchone()
               if inventory:
                   hand_quantity = inventory['ton_sl'] or 0
                   total_cost = inventory['total_cost'] or 0
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           return avg_cost
       
       if categ=='spares':
           parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
           locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
           if move_type == 'freight':
               sql = '''
                   select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                   where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                   group by product_id
               '''%(product_id[0], move_id)
               self.cr.execute(sql)
               for inventory in self.cr.dictfetchall():
                   avg_cost = inventory['line_net'] or 0
           
           if move_type == 'grn':
               sql = '''
                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                           and st.location_dest_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s')
                           
                   '''%(product_id[0], locat_ids[0], date)
               self.cr.execute(sql)
               inventory = self.cr.dictfetchone()
               if inventory:
                   hand_quantity = inventory['ton_sl'] or 0
                   total_cost = inventory['total_cost'] or 0
               sql = '''
                   select * from stock_move where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s))
               '''%(move_id) 
               self.cr.execute(sql)
               for line in self.cr.dictfetchall():
                   if line['action_taken'] == 'need':
                       sql = '''
                           select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                       '''%(line['id'])
                       self.cr.execute(sql)
                       inspec = self.cr.dictfetchone()
                       if inspec:
                           hand_quantity += inspec['qty_approve'] or 0
                           total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
               avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           
           if move_type == 'good':
               sql = '''
                        select case when sum(-1*st.product_qty)!=0 then sum(-1*st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                        and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                           
                   '''%(product_id[0], locat_ids[0], date)
               self.cr.execute(sql)
               inventory = self.cr.dictfetchone()
               if inventory:
                   hand_quantity = inventory['ton_sl'] or 0
                   total_cost = inventory['total_cost'] or 0
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           return avg_cost
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

