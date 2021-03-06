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
            'convert_date': self.convert_date,
            'get_lines': self.get_lines,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_qty(self, categ, line):
        ton = 0
        inspec = 0
        if categ=='raw':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s 
                                    and st.location_dest_id != st.location_id
                                    and (picking_id is not null
                                         or inspec_id is not null
                                         or (id in (select move_id from stock_inventory_move_rel)))
                                    and st.location_id != st.location_dest_id
                                )foo
                        '''%(line,locat_ids[0])
                        
            self.cr.execute(sql)
            ton_arr = self.cr.fetchone()
            if ton_arr:
                ton = ton_arr[0] or 0
            else:
                ton = 0
        if categ =='spares':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                                    and st.location_dest_id != st.location_id
                                    and (picking_id is not null
                                         or inspec_id is not null
                                         or (id in (select move_id from stock_inventory_move_rel)))
                                    and st.location_id != st.location_dest_id
                                )foo
                        '''%(line,locat_ids[0])
            self.cr.execute(sql)
            ton_arr = self.cr.fetchone()
            if ton_arr:
                ton = ton_arr[0] or 0
            else:
                ton = 0
        adj_qty = 0
        sql = '''
        select adj_qty from stock_adjustment where product_id=%s and state='done' and adj_type='increase'
        '''%(line)
        self.cr.execute(sql)
        temp = self.cr.fetchone()
        if temp:
            adj_qty = temp[0]
        ton = ton + adj_qty
        return ton
    
    def get_receipt_value(self, categ, product_id):
        hand_quantity = 0
        inventory = []
        if categ=='raw':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            #TPT-VINOTH-BM-ON 24/05/2016 - Query2 UION PART IS ADDED TO ADD FREIGHT INVOICE AMOUNT
            sql = '''
                select sum(a.ton_sl) ton_sl, sum(a.total_cost) total_cost from (
                
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                    (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id != st.location_id
                        and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' 
                                and (picking_id in (select id from stock_picking where state = 'done')
                                    or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
                                          (select id from stock_inventory where state = 'done'))))
                                )foo
                                
                        -- TPT-BM-ON 08/08/2016 - UNION REMOVED FROM HERE - PLS REF "get_frt_cst_amt" METHOD
            
                )a
                        '''%(locat_ids[0],product_id)
            self.cr.execute(sql)
            inventory = self.cr.dictfetchone()
        if categ and categ =='spares':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
             #TPT START - By P.vinothkumar - ON 24/05/2015 - FOR (adding freight invoice details in query)
            sql = '''
                select sum(a.ton_sl) ton_sl, sum(a.total_cost) total_cost from (
               
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from
                    (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id != st.location_id
                        and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal'
                                and (picking_id in (select id from stock_picking where state = 'done')
                                    or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in
                                          (select id from stock_inventory where state = 'done'))))
                                )foo
                               
                        union
                       
                        select 0 as ton_sl, case when sum(ail.line_net)!=0 then sum(ail.line_net) else 0 end as total_cost from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            where ai.doc_type='freight_invoice' and ai.state not in('draft','cancel') and
            and ail.product_id=%s
           
                )a '''%(locat_ids[0],product_id,product_id)
         #TPT END
         #print sql
        if inventory:
            hand_quantity = inventory['ton_sl'] or 0
            total_cost = inventory['total_cost'] or 0
        sql = '''
               select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where state = 'done')
           '''%(product_id) 
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
           if line['action_taken'] == 'need':
               sql = '''
                   select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
               '''%(line['id'])
               self.cr.execute(sql)
               inspec = self.cr.dictfetchone()
               if inspec:
                   hand_quantity += inspec['qty_approve'] or 0
                   total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
        adj_value = 0
        sql = '''
        select case when sum(product_qty*price_unit) >0 then sum(product_qty*price_unit) else 0 end as value from stock_move sm
        inner join stock_adjustment sa on sm.stock_adj_id=sa.id
        where sa.adj_type='increase' and sm.product_id=%s
        '''%(product_id)
        self.cr.execute(sql)
        temp = self.cr.fetchone()
        if temp:
            adj_value = temp[0]
        total_cost = total_cost + adj_value
        return total_cost
    
    def get_qty_out(self, categ, line):
        total = 0
        if categ=='raw':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where warehouse = %s and state = 'done')
            '''%(line,locat_ids[0])
            self.cr.execute(sql)
            product_isu_qty = self.cr.dictfetchone()
            
        if categ=='spares':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where warehouse = %s and state = 'done')
            '''%(line, locat_ids[0])
            self.cr.execute(sql)
            product_isu_qty = self.cr.dictfetchone()
            
        total = product_isu_qty['product_isu_qty']
        adj_qty = 0
        sql = '''
        select adj_qty from stock_adjustment where product_id=%s and state='done' and adj_type='decrease'
        '''%(line)
        self.cr.execute(sql)
        temp = self.cr.fetchone()
        if temp:
            adj_qty = temp[0]
        total = total + adj_qty
        return total
    
    def get_qty_chuaro(self, categ, line):
        if categ == 'raw':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                and location_id != location_dest_id
            '''%(line, locat_ids[0])
            self.cr.execute(sql)
            product_qty = self.cr.dictfetchone()
        if categ == 'spares':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                location_id != location_dest_id
            '''%(line, locat_ids[0])
            self.cr.execute(sql)
            product_qty = self.cr.dictfetchone()
        return product_qty and product_qty['product_qty'] or 0
    
    def get_consumption_value(self, categ, product_id):
        consum_value = 0
        product = self.pool.get('product.product').browse(self.cr,self.uid,product_id)
        if categ == 'raw':
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end tong
                    from stock_move st
                    where st.state='done' and st.product_id=%s
                        and st.location_dest_id != st.location_id
                        and  (
                            issue_id is not null
                        and id not in (select id
                            from stock_move where product_id = %s and state = 'done' and issue_id is null 
                            and picking_id is null and inspec_id is null and location_id = %s 
                            and location_id != location_dest_id)
                )
            '''%(product_id,product_id, locat_ids[0])
            self.cr.execute(sql)
            #print sql
            consum_value = self.cr.dictfetchone()['tong']
            
            if product.default_code == 'M0501060001':
                sql = '''
                    select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end tong
                        from stock_move
                        where state='done' and product_id in (select id from product_product where default_code = 'M0501060001')
                            and location_dest_id != location_id
                            and  (
                                 issue_id is not null
                            or (location_id = %s and id in (select move_id from mrp_production_move_ids))
                    )
                '''%(locat_ids[0])
                self.cr.execute(sql)
                consum_value = self.cr.dictfetchone()['tong']
                
        if categ == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end tong
                    from stock_move st
                    where st.state='done' and st.product_id=%s
                        and st.location_dest_id != st.location_id
                        and  (
                            issue_id is not null
                        and id not in (select id
                            from stock_move where product_id = %s and state = 'done' and issue_id is null 
                            and picking_id is null and inspec_id is null and location_id = %s 
                            and location_id != location_dest_id)
                )
            '''%(product_id, product_id, locat_ids[0])
            self.cr.execute(sql)
            consum_value = self.cr.dictfetchone()['tong']
        return consum_value
    
    def get_frt_cst_amt(self, product_id):
        amt_opening, amt_receipt = 0.0, 0.0
        amt_opening1, amt_receipt1 = 0.0, 0.0
        amt_opening2, amt_receipt2 = 0.0, 0.0
        ##################
        sql = ''' 
            select 
            
            case when sum(ail.tpt_tax_amt)>=0 then sum(ail.tpt_tax_amt) else 0 end as cst_amt 
            
            from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
            inner join account_tax t on ailt.tax_id = t.id
            where ail.product_id=%s and ai.state not in ('draft', 'cancel') 
            and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
        '''%(product_id, '%', '%')
        self.cr.execute(sql)
        cst_amt = self.cr.fetchone()
        if cst_amt:
            amt_opening += cst_amt[0]
        #
        sql = '''
            select  case when 
            SUM(case when ail.fright_fi_type='2' then ail.fright
            when ail.fright_fi_type='3' then ail.fright*ail.quantity
            else 0 end) >=0
            then 
            SUM(case when ail.fright_fi_type='2' then ail.fright
            when ail.fright_fi_type='3' then ail.fright*ail.quantity
            else 0 end)
            else 0 end as frt_amt
            from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            where ail.product_id=%s and ai.state not in ('draft', 'cancel')
            and ai.doc_type='freight_invoice'
        '''%(product_id)
        self.cr.execute(sql)
        frt_amt = self.cr.fetchone()
        if frt_amt:
            amt_opening += frt_amt[0]   
        #TPT-BM-01/08/2016 - Opening for supplier invoice with freight value entered
        sql = '''
        select 
            case when 
                SUM(case 
                when ail.fright_type='1' then ail.fright*100
                when ail.fright_type='2' then ail.fright*ai.currency_rate
                when ail.fright_type='3' then ail.fright*ail.quantity
                when ail.fright_type is null then ail.fright*ai.currency_rate
                else 0 end) >=0
                then    
                SUM(case 
                when ail.fright_type='1' then ail.fright*100
                when ail.fright_type='2' then ail.fright*ai.currency_rate
                when ail.fright_type='3' then ail.fright*ail.quantity
                when ail.fright_type is null then ail.fright*ai.currency_rate
                else 0 end)                
                else 0 end as frt_amt
            from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            where ail.product_id=%s and 
            ai.state not in ('draft', 'cancel')
            and ai.doc_type='supplier_invoice' and ail.fright>0 
        '''%(product_id)
        self.cr.execute(sql)
        si_frt_amt = self.cr.fetchone()
        if si_frt_amt:
            amt_opening += si_frt_amt[0] 
        sql = '''
            select
            case when sum(ail.tpt_tax_amt)>=0 then sum(ail.tpt_tax_amt) else 0 end as cst_amt 
            from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
            inner join account_tax t on ailt.tax_id = t.id
            where ail.product_id=%s and ai.state not in ('draft', 'cancel') 
            and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
        '''%(product_id, '%', '%')
        self.cr.execute(sql)
        cst_amt1 = self.cr.fetchone()
        if cst_amt1:
            amt_receipt += cst_amt1[0]
        sql = '''
            select case when 
            SUM(case when ail.fright_fi_type='2' then ail.fright
            when ail.fright_fi_type='3' then ail.fright*ail.quantity
            else 0 end) >=0
            then    
            SUM(case when ail.fright_fi_type='2' then ail.fright
            when ail.fright_fi_type='3' then ail.fright*ail.quantity
            else 0 end)                
            else 0 end as frt_amt
            
            from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            where ail.product_id=%s and ai.state not in ('draft', 'cancel')
            and ai.doc_type='freight_invoice'
        '''%(product_id)
        self.cr.execute(sql)
        frt_amt1 = self.cr.fetchone()
        if frt_amt1:
            amt_receipt += frt_amt1[0]    
        sql = '''
        select 
            case when 
                SUM(case 
                when ail.fright_type='1' then ail.fright*100
                when ail.fright_type='2' then ail.fright
                when ail.fright_type='3' then ail.fright*ail.quantity
                when ail.fright_type is null then ail.fright
                else 0 end) >=0
                then    
                SUM(case 
                when ail.fright_type='1' then ail.fright*100
                when ail.fright_type='2' then ail.fright
                when ail.fright_type='3' then ail.fright*ail.quantity
                when ail.fright_type is null then ail.fright
                else 0 end)                
                else 0 end as frt_amt
            from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            where ail.product_id=%s and 
            ai.state not in ('draft', 'cancel')
            and ai.doc_type='supplier_invoice' and ail.fright>0 
        '''%(product_id)
        self.cr.execute(sql)
        si_frt_amt = self.cr.fetchone()
        if si_frt_amt:
            amt_receipt += si_frt_amt[0] 
        return amt_opening, amt_receipt  

    def finish_stock_value(self, product_id, location_id):
        avg_cost = 0
        prod_obj = self.pool.get('product.product')
        prod_id = prod_obj.browse(self.cr, self.uid, product_id)
        avg_cost = prod_id.standard_price or 0
        return avg_cost or 0

    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        product_id = wizard_data['product_id']
        percentage_in_range_from = wizard_data['percentage_in_range_from']
        percentage_in_range_to = wizard_data['percentage_in_range_to']
        stock_value_from = wizard_data['stock_value_from']
        stock_value_to = wizard_data['stock_value_to']
        pro_obj = self.pool.get('product.product')
        res = []
        
        #Tính toán với sản phẩm là raw
        sql='''
            select product_product.id 
            from product_product,product_template 
            where product_template.categ_id in (select product_category.id from product_category where product_category.cate_name in ('raw')) 
            and product_product.product_tmpl_id = product_template.id 
        '''
        if product_id:
            sql += '''
                and product_product.id = %s 
            '''%(product_id[0])
        self.cr.execute(sql)
        product_ids = [r[0] for r in self.cr.fetchall()]
        for product in pro_obj.browse(self.cr,self.uid,product_ids):
            
            receipt_qty = self.get_qty(product.categ_id.cate_name,product.id)
            receipt_value = self.get_receipt_value(product.categ_id.cate_name,product.id) 
            consum_qty = self.get_qty_out(product.categ_id.cate_name,product.id) + self.get_qty_chuaro(product.categ_id.cate_name,product.id)
            consum_value = self.get_consumption_value(product.categ_id.cate_name,product.id)
            opening, receipt = self.get_frt_cst_amt(product.id) 
            receipt_value += receipt
            consum_percent = receipt_value and round(float(consum_value)/float(receipt_value)*100.0,2) or 0.0
            close_value = round(receipt_value, 3) - round(consum_value, 3)
            is_check = True
            if percentage_in_range_from and consum_percent<percentage_in_range_from:
                is_check = False
            if percentage_in_range_to and consum_percent>percentage_in_range_to:
                is_check = False
            if stock_value_from and close_value<stock_value_from:
                is_check = False
            if stock_value_to and close_value>stock_value_to:
                is_check = False
            if is_check:
                res.append({
                    'item_code': product.default_code,
                    'item_name': product.name,
                    'consum_qty':consum_qty,
                    'consum_percent': consum_percent,    
                    'close_stock':receipt_qty - (consum_qty),
                    'close_value': close_value,  
                })
                
        #Tính toán với sản phẩm là spares
        sql='''
            select product_product.id 
            from product_product,product_template 
            where product_template.categ_id in (select product_category.id from product_category where product_category.cate_name in ('spares')) 
            and product_product.product_tmpl_id = product_template.id 
        '''
        if product_id:
            sql += '''
                and product_product.id = %s 
            '''%(product_id[0])
        self.cr.execute(sql)
        product_ids = [r[0] for r in self.cr.fetchall()]
        if product_ids:
            product_ids = str(product_ids).replace("[", "")
            product_ids = product_ids.replace("]", "")
            sql = '''
            select pp.id as product_id, pp.default_code, pp.name_template as name, pu.name as uom,
            
            (select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%(location_spare_id)s 
                        and st.product_id=pp.id 
                        and state = 'done'
                            and st.location_dest_id != st.location_id
                            and ( (picking_id is not null) 
                            or  (inspec_id is not null)
                            or (st.id in (select move_id from 
                            stock_inventory_move_rel where inventory_id in 
                            (select id from stock_inventory where state = 'done')))
                                )) - ((select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
            where product_id = pp.id and material_issue_id in (select id from tpt_material_issue where warehouse = %(location_spare_id)s and state = 'done')) 
            +
            (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                        from stock_move where product_id = pp.id and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %(location_spare_id)s 
                        and location_id != location_dest_id)) opening_stock, 
            
            (select case when sum(st.product_qty*price_unit)!=0 then sum(st.product_qty*price_unit) else 0 end ton_sl
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%(location_spare_id)s 
                        and st.product_id=pp.id 
                        and state = 'done'
                            and st.location_dest_id != st.location_id
                            and ( (picking_id is not null) 
                            or  (inspec_id is not null)
                            or (st.id in (select move_id from 
                            stock_inventory_move_rel where inventory_id in 
                            (select id from stock_inventory where 
      state = 'done')))
                                ))-(select case when sum(price_unit*product_qty)>0 then sum(price_unit*product_qty) else 0 end from stock_move 
            where issue_id is not null and product_id=pp.id
            
            and state='done' )  opening_stock_value, 
           
            (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                        (select st.product_qty
                                            from stock_move st 
                                            where st.state='done' and st.product_id = pp.id and 
                                            st.location_dest_id = %(location_spare_id)s
                                            and st.location_dest_id != st.location_id
                                            and (picking_id is not null
                                                 or inspec_id is not null
                                                 or (id in (select move_id from stock_inventory_move_rel)))
                                            and st.location_id != st.location_dest_id
                                            and st.state = 'done'
                                        )foo)
                     +
                     (select case when sum(adj_qty)!=0 then sum(adj_qty) else 0 end adj_qty from stock_adjustment where product_id=pp.id and state='done' 
                     and adj_type='increase')                   
                                         receipt_qty,
            
            (select case when sum(product_qty*price_unit)>0 then sum(product_qty*price_unit) else 0 end from stock_move where product_id=pp.id and location_dest_id=%(location_spare_id)s 
            and state = 'done') 
            +
            (
            select case when sum(sm.product_qty*sm.price_unit) >0 then sum(sm.product_qty*sm.price_unit) else 0 end as value from stock_move sm
            inner join stock_adjustment sa on sm.stock_adj_id=sa.id
            where sa.adj_type='increase' and sm.product_id=pp.id
            )
            receipt_value,
            
            
            (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_isu_qty from stock_move where product_id=pp.id and issue_id is not null and 
            state='done') 
            +
    
            (select case when sum(sm.product_qty)!=0 then sum(sm.product_qty) else 0 end product_qty  from stock_adjustment sa
            inner join stock_move sm on sa.id=sm.stock_adj_id
            where sa.adj_type='decrease' and sm.state='done' and sm.product_id=pp.id
            )              
                         consum_qty,
             
            
            (select case when sum(price_unit*product_qty)>0 then sum(price_unit*product_qty) else 0 end from stock_move 
            where issue_id is not null and product_id=pp.id and state = 'done'
            ) +
            (
            select case when sum(sm.product_qty*sm.price_unit) >0 then sum(sm.product_qty*sm.price_unit) else 0 end as value from stock_move sm
            inner join stock_adjustment sa on sm.stock_adj_id=sa.id
            where sa.adj_type='decrease' and sm.product_id=pp.id
            )
            as
            consum_value
                                        
            from product_product pp
            inner join product_template pt on  pp.product_tmpl_id=pt.id
            inner join product_uom pu on pt.uom_id=pu.id
            where pp.cate_name='spares'
            and pp.id in (%(product_id)s)
            order by pp.default_code
            '''%{
                'location_spare_id':14,
                'product_id':product_ids#stock.product_id.id prev sql - and pp.id = %(product_id)s
            }
            self.cr.execute(sql)
            for line in self.cr.dictfetchall():
                consum_qty = line['consum_qty'] or 0
                consum_value = round(line['consum_value'] * (10**3)) / float(10**3)
                receipt_value = line['receipt_value'] or 0
                opening, receipt = self.get_frt_cst_amt(line['product_id'])
                receipt_value += receipt
                consum_percent = receipt_value and round(float(consum_value)/float(receipt_value)*100.0,2) or 0.0
                close_value = receipt_value - consum_value
                is_check = True
                if percentage_in_range_from and consum_percent<percentage_in_range_from:
                    is_check = False
                if percentage_in_range_to and consum_percent>percentage_in_range_to:
                    is_check = False
                if stock_value_from and close_value<stock_value_from:
                    is_check = False
                if stock_value_to and close_value>stock_value_to:
                    is_check = False
                if is_check:
                    res.append({
                        'item_code': line['default_code'],
                        'item_name': line['name'],
                        'consum_qty': consum_qty,
                        'consum_percent': consum_percent,
                        'close_stock': line['receipt_qty'] - line['consum_qty'] or 0, 
                        'close_value': close_value,
                    })
            
        #Tính toán với sản phẩm là finish
#         sql='''
#             select product_product.id 
#             from product_product,product_template 
#             where product_template.categ_id in (select product_category.id from product_category where product_category.cate_name in ('finish')) 
#             and product_product.product_tmpl_id = product_template.id 
#         '''
#         if product_id:
#             sql += '''
#                 and product_product.id = %s 
#             '''%(product_id[0])
#         self.cr.execute(sql)
#         product_ids = [r[0] for r in self.cr.fetchall()]
#         product_ids = str(product_ids).replace("[", "")
#         product_ids = product_ids.replace("]", "")
#         location_id=13
#         for product1 in product_ids:
#             if product1=='2': 
#                 location_id=25 #FSH
#             elif product1=='3': 
#                 location_id=26 #Ferric Sulphate
#             elif product1=='4': 
#                 location_id=13  #TIO2
#             elif product1=='5': 
#                 location_id=27  #Effluent 
#             elif product1=='6': 
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material   
#             elif product1=='7':  
#                 location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material      
#             elif product1=='9':  
#                 location_id=13  #TIO2 
#             elif product1=='10745':  
#                location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material 
#             elif product1=='12906':  
#                location_id=24  #Other        
#             elif product1=='13030':  
#                location_id=24  #Other   
#         sql = ''' select pp.default_code, pp.name_template as name, pu.name uom, 
#         (select sum(product_qty) from stock_move where product_id=pp.id and sale_line_id is null 
#         ) as opening_stock,
#         ---------
#         0 as opening_stock_value,
#         --------
#         (
#         (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end ton_sl
#         from mrp_production where product_id in (%(product_id)s) 
#         +
#         (select case when sum(sil.product_qty)!=0 then sum(sil.product_qty) else 0 end ton_sl from stock_inventory_line sil
#         inner join stock_inventory si on sil.inventory_id=si.id
#         inner join stock_production_lot spl on sil.prod_lot_id=spl.id
#         where si.state='done' and sil.product_id in (%(product_id)s) and sil.product_qty>0 
#         and sil.prod_lot_id is not null)
#         +
#         (select case when sum(ail.quantity)!=0 then sum(ail.quantity) else 0 end quans from account_invoice_line ail
#          inner join account_invoice ai on ail.invoice_id=ai.id
#          where ai.state='cancel' 
#          and ail.product_id=pp.id
#          )
#         )as receipt_qty,
#          --------------
#         0 as receipt_value,
#         ---------
#         (
#         (select case when sum(ail.quantity)!=0 then sum(ail.quantity) else 0 end quans from account_invoice_line ail
#          inner join account_invoice ai on ail.invoice_id=ai.id
#          where ai.state!='cancel' 
#          and ail.product_id=pp.id
#          ) 
#          +
#          (select case when sum(sil.product_qty)!=0 then sum(sil.product_qty) else 0 end ton_sl from stock_inventory_line sil
#         inner join stock_inventory si on sil.inventory_id=si.id
#         inner join stock_production_lot spl on sil.prod_lot_id=spl.id
#         where si.state='done' and sil.product_id in (%(product_id)s) and sil.product_qty>0 
#         and sil.prod_lot_id is not null
#         )
#          )as consum_qty,
#         ---------
#         0 as consum_value,
#         ----------------
#         pp.id as product_id
#         
#         from product_product pp
#         inner join product_template pt on  pp.product_tmpl_id=pt.id
#         inner join product_uom pu on pt.uom_id=pu.id
#         where pp.id in (%(product_id)s)
#         order by pp.default_code
#         '''%{
#             'location_id':location_id,
#             'product_id':product_ids
#             }
#         self.cr.execute(sql)
#         for line in self.cr.dictfetchall():
#             receipt_qty = line['receipt_qty'] or 0
#             consum_qty = line['consum_qty'] or 0
#             receipt_value = receipt_qty * self.finish_stock_value(line['product_id'], location_id)                
#             consum_value = consum_qty * self.finish_stock_value(line['product_id'], location_id)
#             consum_percent = receipt_value and round(float(consum_value)/float(receipt_value)*100.0,2) or 0.0
#             close_value = receipt_value - consum_value
#                 res.append({
#                     'item_code': line['default_code'],
#                     'item_name': line['name'],
#                     'consum_qty': consum_qty,
#                     'consum_percent': consum_percent,
#                     'close_stock': receipt_qty - consum_qty, 
#                     'close_value': close_value,
#                 })
        return res
    
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

