# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_form_movement_analysis(osv.osv):
    _name = "tpt.form.movement.analysis"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Product Category'),
                'product_id': fields.many2one('product.product', 'Product'),
#                 'product_ids': fields.many2many('product.product', 'product_movement_report', 'movement_id', 'product_id', 'Product'),  
                'date_from':fields.date('Date From'),
                'date_from_title':fields.char('Date From'),
                'date_to':fields.date('To'),
                'date_to_title':fields.char('To'),
                'name':fields.char('Stock Movement Analysis',size=1024,readonly=True),
                'movement_line':fields.one2many('tpt.movement.analysis.line','movement_id','Stock Movement'),
                'categ_name':fields.char('Product Category',size=1024),
                'product_name':fields.char('Product',size=1024),
                'categ_name_title':fields.char('Product Category',size=1024),
                'product_name_title':fields.char('Product Category',size=1024),
                }



    def get_categ_name(self, cr, uid, ids,categ_name = False, context=None):
        if categ_name and categ_name == 'raw':
            cate_name = 'Raw Materials'
        if categ_name and categ_name == 'spares':
            cate_name = 'Spares'
        if categ_name and categ_name == 'finish': #TPT-BM-ON 29/03/2016
            cate_name = 'Finished Product'
        return cate_name
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.form.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_xls', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.form.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_pdf', 'datas': datas}
    
tpt_form_movement_analysis()


class tpt_movement_analysis_line(osv.osv):
    _name = "tpt.movement.analysis.line"
    _columns = {    
        'movement_id': fields.many2one('tpt.form.movement.analysis', 'Stock Movement', ondelete='cascade'),
        'item_code': fields.char('Item Code', size = 1024),
        'item_name': fields.char('Item Name', size = 1024),
        'uom': fields.char('UOM', size = 1024),
        'open_stock': fields.float('Opening Stock',digits=(16,3)),
        'open_value': fields.float('Opening Stock Value',digits=(16,3)),
        'receipt_qty': fields.float('Qty (Receipts)',digits=(16,3)),
        'receipt_value':fields.float('Stock Value (Receipts)',digits=(16,3)),
        'consum_qty': fields.float('Qty (Consumption)',digits=(16,3)),
        'consum_value':fields.float('Stock Value (Consumption)',digits=(16,3)),     
        'close_stock': fields.float('Closing Stock',digits=(16,3)),
        'close_value': fields.float('Closing Stock Value',digits=(16,3)),   
        'product_id': fields.many2one('product.product', 'Product'),
                }
    
    #TPT-Y on 07Nov2015
    
    def print_stock_inward(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
         
        stock_obj = self.pool.get('tpt.stock.inward.outward')
        cr.execute('delete from tpt_stock_inward_outward')
        stock = self.browse(cr, uid, ids[0])
        self.current = 0
        self.closing_qty = 0
        self.num_call_grn = {'grn_name':'','num':-1}
        self.transaction_qty = 0
        self.current_transaction_qty = 0
        self.current_price_unit = 0
        self.id = 0
        self.id2 = 0
        self.sum_stock = 0
        self.timecall = 0
        self.st_sum_value = 0
        stock_in_out_line = []
        
        def get_opening_stock(o):
            
            date_from = o.movement_id.date_from
            date_to = o.movement_id.date_to
            product_id = o.product_id
            
            #date_from = o.date_from
            #date_to = o.date_to
            #product_id = o.product_id
            
            categ = product_id.categ_id.cate_name
            if categ=='raw': 
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end product_qty
                            from stock_move st
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD') < '%s'
                                and st.location_dest_id != st.location_id
                                and ( picking_id is not null 
                                or  inspec_id is not null
                                or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_char(date, 'YYYY-MM-DD') <'%s' and state = 'done')))
                            )
                    '''%(locat_ids[0], product_id.id,date_from, date_from)
                cr.execute(sql)
                product_qty = cr.dictfetchone()['product_qty']
                
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                '''%(product_id.id, date_from, locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()['product_isu_qty']
                
#                 sql = '''
#                     select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
#                     from stock_move where product_id = %s and state = 'done' and issue_id is null 
#                     and picking_id is null and inspec_id is null and location_id = %s 
#                     and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
#                 '''%(product_id.id, locat_ids[0], date_from)
#                 cr.execute(sql)
#                 product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
#                 opening_stock = product_qty-product_isu_qty-product_qty_chuaro
                
                opening_stock = product_qty-product_isu_qty
                
            if categ=='spares': 
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
                sql = '''
                    select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end product_qty
                            from stock_move st
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD') < '%s'
                                and st.location_dest_id != st.location_id
                                and ( picking_id is not null 
                                or  inspec_id is not null
                                or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_char(date, 'YYYY-MM-DD') <'%s' and state = 'done')))
                            )
                    '''%(locat_ids[0], product_id.id,date_from, date_from)
                cr.execute(sql)
                product_qty = cr.dictfetchone()['product_qty']
                
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                '''%(product_id.id, date_from, locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()['product_isu_qty']
#                 sql = '''
#                     select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
#                     from stock_move where product_id = %s and state = 'done' and issue_id is null 
#                     and picking_id is null and inspec_id is null and location_id = %s 
#                     and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
#                 '''%(product_id.id, locat_ids[0], date_from)
#                 cr.execute(sql)
#                 product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
#                 opening_stock = product_qty-product_isu_qty-product_qty_chuaro
                opening_stock = product_qty-product_isu_qty
            return opening_stock
        
        
        
        def get_closing_stock(o,get_detail_lines):
            closing = 0
            qty_grn = 0
            qty_good = 0
            for line in get_detail_lines:
                if line['doc_type']=='grn':
                    if self.id != line['id']:
                        self.num_call_grn = {'grn_name':'','num':-1}
                        self.id = line['id']
                    qty_grn += get_transaction_qty(o,line['id'], line['material_issue_id'], line['product_dec'], line['doc_type'])
                if line['doc_type']=='good':
                    if self.id != line['id']:
                        self.num_call_grn = {'grn_name':'','num':-1}
                        self.id = line['id']
                    qty_good += get_transaction_qty(o,line['id'], line['material_issue_id'], line['product_dec'], line['doc_type'])
            closing = qty_grn + qty_good
            return closing
        
        
        def get_opening_stock_value(o):
           
           date_from = o.movement_id.date_from
           date_to = o.movement_id.date_to
           product_id = o.product_id
           
           #date_from = o.date_from
           #date_to = o.date_to
           #product_id = o.product_id
           
           categ = product_id.categ_id.cate_name
           opening_stock_value = 0
           freight_cost = 0
           production_value = 0
           if categ=='raw':
               parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
               locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
               sql = '''
                       select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and st.location_dest_id != st.location_id
                            and ( picking_id is not null 
                            or inspec_id is not null 
                            or (st.id in (select move_id from stock_inventory_move_rel))
                        )
               '''%(locat_ids[0],product_id.id, date_from)
               cr.execute(sql)
               inventory = cr.dictfetchone()
               if inventory:
                   hand_quantity = inventory['ton_sl'] or 0
                   total_cost = inventory['total_cost'] or 0
               sql = '''
                   select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is not null
                        
               '''%(locat_ids[0],product_id.id,date_from)
               cr.execute(sql)
               product_isu_qty = cr.fetchone()[0]
                   
               if product_id.default_code == 'M0501060001':
                   sql = '''
                       select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is null and picking_id is null and inspec_id is null 
                        and id in (select move_id from mrp_production_move_ids)
                            
                   '''%(locat_ids[0],product_id.id,date_from)
                   cr.execute(sql)
                   production_value = cr.fetchone()[0]
               opening_stock_value = total_cost-(product_isu_qty)+freight_cost-production_value
           if categ=='spares':
               parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
               locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
               sql = '''
                       select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and st.location_dest_id != st.location_id
                            and ( picking_id is not null 
                            or inspec_id is not null 
                            or (st.id in (select move_id from stock_inventory_move_rel))
                        )
               '''%(locat_ids[0],product_id.id, date_from)
               cr.execute(sql)
               inventory = cr.dictfetchone()
               if inventory:
                   hand_quantity = inventory['ton_sl'] or 0
                   total_cost = inventory['total_cost'] or 0
#                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
               sql = '''
                   select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is not null
                        
               '''%(locat_ids[0],product_id.id,date_from)
               cr.execute(sql)
               product_isu_qty = cr.fetchone()[0]
               sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where date_invoice < '%s' and sup_inv_id is not null)
                       group by product_id
               '''%(product_id.id, date_from)
               cr.execute(sql)
               for inventory in cr.dictfetchall():
                   freight_cost = inventory['line_net'] or 0
            
               if product_id.default_code == 'M0501060001':
                   sql = '''
                       select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is null and picking_id is null and inspec_id is null 
                        and id in (select move_id from mrp_production_move_ids)
                            
                   '''%(locat_ids[0],product_id.id,date_from)
                   cr.execute(sql)
                   production_value = cr.fetchone()[0]
                   
               opening_stock_value = total_cost-(product_isu_qty)+freight_cost-production_value
           return opening_stock_value
        
        def get_detail_lines(o):            
            
            
            date_from = o.movement_id.date_from
            date_to = o.movement_id.date_to
            product_id = o.product_id
            
            #date_from = o.date_from
            #date_to = o.date_to
            #product_id = o.product_id
            
            parent_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
            parent_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
            sql = '''
                select * from account_move where doc_type in ('good', 'grn', 'product', 'freight') 
                    and date between '%(date_from)s' and '%(date_to)s'
                    and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where to_char(date_invoice, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                        or (ref in (select name from stock_picking where id in (select picking_id from stock_move where to_char(date, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and product_id=%(product_id)s)))
                    ) or material_issue_id in (select id from tpt_material_issue where date_expec between '%(date_from)s' and '%(date_to)s' and warehouse in (%(location_row_id)s,%(location_spare_id)s) and id in (select material_issue_id from tpt_material_issue_line where product_id=%(product_id)s)) 
                        )
                        or product_dec in (select id from mrp_production where date_planned between '%(date_from)s' and '%(date_to)s' and id in (select production_id from mrp_production_move_ids where move_id in (select id from stock_move where product_id = %(product_id)s and location_id in (%(location_row_id)s,%(location_spare_id)s) ))
                         )
                         order by date,doc_type = 'grn' desc, doc_type = 'good' desc, doc_type = 'product' desc, id
            '''%{'date_from':date_from,
                 'date_to':date_to,
                 'product_id':product_id.id,
                 'location_row_id':locat_ids_raw[0],
                 'location_spare_id':locat_ids_spares[0]}
            cr.execute(sql)
            move_line = []
            for line in cr.dictfetchall():
                if line['doc_type'] == 'grn':
                    sql = '''
                        select * from stock_move
                        where  picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s) and product_id = %s)
                    '''%(line['id'], product_id.id)
                    cr.execute(sql)
                    for move in cr.dictfetchall():
                        if move['action_taken'] == 'direct' and move['location_dest_id'] in [locat_ids_raw[0],locat_ids_spares[0]]:
                            move_line.append(line)
                        if move['action_taken'] == 'need':
                            sql = '''
                                select id, qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining') and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                            '''%(move['id'], date_from, date_to)
                            cr.execute(sql)
                            for move_sql in cr.dictfetchall():
                                if move_sql['qty_approve']:
                                    sql = '''
                                        select id from stock_move where inspec_id = %s and state = 'done' and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                                    '''%(move_sql['id'], date_from, date_to)
                                    cr.execute(sql)
                                    move_sql2 = cr.fetchall()
                                    if move_sql2:
                                        move_line.append(line)
                                        
                elif line['doc_type'] == 'product' and product_id.code == 'M0501060001':
                    move_line.append(line)
                else:
                    move_line.append(line)
            return move_line   
        
         
        
        def get_account_move_line(move_id, material_issue_id, product_dec, move_type):
            name = ''
            move = self.pool.get('account.move').browse(cr,uid,move_id)
            if move_type == 'freight':
                sql = '''
                   select name from account_invoice where move_id = %s and sup_inv_id is not null
                '''%(move_id)
                cr.execute(sql)
                for invoice in cr.dictfetchall():
                   name = invoice['name'] or 0
            if move_type == 'good':
                sql = '''
                    select doc_no from tpt_material_issue where id = %s 
                '''%(material_issue_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['doc_no']
            if move_type == 'product':
                sql = '''
                    select name from mrp_production where id = %s 
                '''%(product_dec)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['name']        
            if move_type == 'grn':
                sql = '''
                   select name from stock_picking where name in (select ref from account_move_line where move_id = %s) 
                '''%(move_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['name']
            return name
        
        def get_create_date(move_id, material_issue_id, product_dec, move_type):
            if move_type == 'freight':
                sql = '''
                   select create_date from account_invoice where move_id = %s and sup_inv_id is not null
                '''%(move_id)
                cr.execute(sql)
                for invoice in cr.dictfetchall():
                   date = invoice['create_date'] or 0
            if move_type == 'good':
                sql = '''
                    select create_date from tpt_material_issue where id = %s 
                '''%(material_issue_id)
                cr.execute(sql)
                for issue in cr.dictfetchall():
                    date = issue['create_date']
            if move_type == 'product':
                sql = '''
                    select create_date from mrp_production where id = %s 
                '''%(product_dec)
                cr.execute(sql)
                for product in cr.dictfetchall():
                    date = product['create_date']        
            if move_type == 'grn':
                sql = '''
                   select create_date from stock_picking where name in (select ref from account_move_line where move_id = %s) 
                '''%(move_id)
                cr.execute(sql)
                for picking in cr.dictfetchall():
                    date = picking['create_date']
            return date
        
        def get_transaction_qty(o, move_id, material_issue_id, product_dec, move_type):
            date_from = o.movement_id.date_from
            date_to = o.movement_id.date_to
            product_id = o.product_id
            
            #date_from = o.date_from
            #date_to = o.date_to
            #product_id = o.product_id
            
            categ = product_id.categ_id.cate_name
            quantity = 0
            price_unit = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                if move_type in ('freight', 'sup_inv_po'): #TPT-BM-ON 07/07/2016
                    quantity = 0
                if move_type == 'product':
                    production_id = self.pool.get('mrp.production').browse(cr,uid,product_dec)
                    for line in production_id.move_lines2:
                        if line.product_id.id == product_id.id:
                            quantity += line.product_qty
                    quantity = -quantity
                if move_type == 'good':
                    sql = '''
                        select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                        where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                        group by product_id 
                    '''%(material_issue_id, locat_ids[0], product_id.id)
                    cr.execute(sql)
                    for qty in cr.dictfetchall():
                        quantity = qty['product_isu_qty']
                if move_type == 'grn':
                    sql = '''
                        select * from stock_move
                        where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s)) 
                        and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                    '''%(move_id, product_id.id)
                    cr.execute(sql)
                    moves = cr.dictfetchall()
                    grn_name = get_account_move_line(move_id, material_issue_id, product_dec, move_type)
                    if self.num_call_grn['grn_name']==grn_name:
                        self.num_call_grn['num'] += 1
                    else:
                        self.num_call_grn['grn_name']=grn_name
                        self.num_call_grn['num'] = 0
                    if len(moves)>self.num_call_grn['num']:
                        move = moves[self.num_call_grn['num']]
                        if move['action_taken'] == 'direct' and move['location_dest_id']==locat_ids[0]:
                            quantity = move['product_qty']
                            price_unit = move['price_unit']
                        if move['action_taken'] == 'need':
                            sql1 = '''
                                select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                            '''%(move['id'])
                            cr.execute(sql1)
                            need = cr.dictfetchone()
                            if need:
                                quantity = need['qty_approve'] or 0
                                price_unit = move['price_unit']
            if categ=='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                if move_type in ('freight', 'sup_inv_po'): #TPT-BM-ON 07/07/2016 - sup_inv_po added
                    quantity = 0
                
                if move_type == 'good':
                    sql = '''
                        select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                        where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                        group by product_id 
                    '''%(material_issue_id, locat_ids[0], product_id.id)
                    cr.execute(sql)
                    for qty in cr.dictfetchall():
                        quantity = qty['product_isu_qty']
                if move_type == 'product':
                    production_id = self.pool.get('mrp.production').browse(cr,uid,product_dec)
                    for line in production_id.move_lines2:
                        if line.product_id.id == product_id.id:
                            quantity += line.product_qty
                    quantity = -quantity
                if move_type == 'grn':
                    sql = '''
                        select * from stock_move
                        where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s)) 
                        and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                    '''%(move_id, product_id.id)
                    cr.execute(sql)
                    moves = cr.dictfetchall()
                    grn_name = get_account_move_line(move_id, material_issue_id, product_dec, move_type)
                    if self.num_call_grn['grn_name']==grn_name:
                        self.num_call_grn['num'] += 1
                    else:
                        self.num_call_grn['grn_name']=grn_name
                        self.num_call_grn['num'] = 0
                    if len(moves)>self.num_call_grn['num']:
                        move = moves[self.num_call_grn['num']]
                        if move['action_taken'] == 'direct' and move['location_dest_id']==locat_ids[0]:
                            quantity = move['product_qty']
                            price_unit = move['price_unit']
                        if move['action_taken'] == 'need':
                            sql1 = '''
                                select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                            '''%(move['id'])
                            cr.execute(sql1)
                            need = cr.dictfetchone()
                            if need:
                                quantity = need['qty_approve'] or 0
                                price_unit = move['price_unit']
            self.transaction_qty += quantity
            self.current_transaction_qty = quantity
            self.current_price_unit = price_unit
            return quantity
        
        def sum_trans_qty(o, get_detail_lines):
            sum = 0
            for line in get_detail_lines:
#                 if len(get_detail_lines) <= 1:
                self.num_call_grn = {'grn_name':'','num':-1}
                qty = get_transaction_qty(o, line['id'], line['material_issue_id'], line['product_dec'],line['doc_type'])
                sum += qty
            return sum
        
        def get_date(date):
            res = {}
            date_sec = datetime.strptime(date, DATE_FORMAT)
            day = date_sec.day
            month = date_sec.month
            year = date_sec.year
            res = {
                   'day': day,
                   'month': month,
                   'year': year,
                   }
            return res
        
        def get_line_stock_value(o, move_id, material_issue_id, move_type, date):
           
           date_from = o.movement_id.date_from
           date_to = o.movement_id.date_to
           product_id = o.product_id
           
           #date_from = o.date_from
           #date_to = o.date_to
           #product_id = o.product_id
           categ = product_id.categ_id.cate_name
           opening_stock_value = 0
           total_cost = 0
           hand_quantity = 0
           if categ=='raw':
               parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
               locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
               if move_type == 'freight':
                   sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                       group by product_id
                   '''%(product_id.id, move_id)
                   cr.execute(sql)
                   for inventory in cr.dictfetchall():
                       avg_cost = inventory['line_net'] or 0
               
               if move_type == 'grn':
                   sql = '''
                       select * from stock_move where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s))
                   '''%(move_id) 
                   cr.execute(sql)
                   for line in cr.dictfetchall():
                       if line['action_taken'] == 'need':
                           sql = '''
                               select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                           '''%(line['id'])
                           cr.execute(sql)
                           inspec = cr.dictfetchone()
                           if inspec:
                               hand_quantity += inspec['qty_approve'] or 0
                               total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           
               if move_type == 'good':
                   good = self.pool.get('tpt.material.issue').browse(cr,uid,material_issue_id)
                   sql = '''
                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                         from stock_move st
                             join stock_location loc1 on st.location_id=loc1.id
                             join stock_location loc2 on st.location_dest_id=loc2.id
                         where st.state='done' and st.location_dest_id != st.location_id
                         and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                         and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                            
                    '''%(product_id.id, locat_ids[0], good.date_expec)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                       avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
           
           if categ=='spares':
               parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
               locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])]) 
               if move_type == 'freight':
                   sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                       group by product_id
                   '''%(product_id.id, move_id)
                   cr.execute(sql)
                   for inventory in cr.dictfetchall():
                       avg_cost = inventory['line_net'] or 0
               
               if move_type == 'grn':
                   sql = '''
                            select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id != st.location_id
                            and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                            and st.location_dest_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s')
                            
                    '''%(product_id.id, locat_ids[0], date)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                   sql = '''
                       select * from stock_move where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s))
                   '''%(move_id) 
                   cr.execute(sql)
                   for line in cr.dictfetchall():
                       if line['action_taken'] == 'need':
                           sql = '''
                               select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                           '''%(line['id'])
                           cr.execute(sql)
                           inspec = cr.dictfetchone()
                           if inspec:
                               hand_quantity += inspec['qty_approve'] or 0
                               total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           
               if move_type == 'good':
    
                   sql = '''
                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                         from stock_move st
                             join stock_location loc1 on st.location_id=loc1.id
                             join stock_location loc2 on st.location_dest_id=loc2.id
                         where st.state='done' and st.location_dest_id != st.location_id
                         and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                         and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                            
                    '''%(product_id.id, locat_ids[0], date)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                       avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
           
        
        def closing_value(o,get_detail_lines):
            closing = 0
            for line in get_detail_lines:
                if self.id2 != line['id']:
                    self.num_call_grn = {'grn_name':'','num':-1}
                    self.id2 = line['id']
                qty = get_transaction_qty(o,line['id'], line['material_issue_id'], line['product_dec'],line['doc_type'])
                if line['doc_type']=='freight':
                    qty=1
                elif line['doc_type']=='sup_inv_po':
                    qty=1
                value = get_line_stock_value(o,line['id'], line['material_issue_id'], line['doc_type'], line['date'])
                closing += qty * value
            return closing

        
        def get_doc_type(doc_type):
            if doc_type == 'freight':
                return 'Freight Invoice'
            if doc_type == 'good':
                return 'Good Issue'
            if doc_type == 'grn':
                return 'GRN'
            if doc_type == 'product':
                return 'Production'
        
        def stock_value(o, move_id, doc_type):
            if doc_type=='freight':
                self.current_transaction_qty = 1
                sql = '''
                    select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                    where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                    group by product_id
                   '''%(o.product_id.id, move_id)
                cr.execute(sql)
                for inventory in cr.dictfetchall():
                    avg_cost = inventory['line_net'] or 0
                    return self.current_transaction_qty*avg_cost
            else:
                return self.current_transaction_qty*self.current_price_unit
        
        def qty_physical_inve(o):
            date_from = o.movement_id.date_from
            date_to = o.movement_id.date_to
            product_id = o.product_id
            
            #date_from = o.date_from
            #date_to = o.date_to
            #product_id = o.product_id
            
            categ = product_id.categ_id.cate_name
            parent_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
            parent_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
            
            if categ == 'raw':
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move 
                    where location_dest_id = %s and state = 'done' and location_dest_id != location_id
                    and id in (select move_id from stock_inventory_move_rel) and to_char(date, 'YYYY-MM-DD') between '%s' and '%s' and product_id = %s
                    and location_id != location_dest_id
                '''%(locat_ids_raw[0], date_from, date_to, product_id.id)
                cr.execute(sql)
                product_qty = cr.fetchone()[0]
            if categ == 'spares':
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move 
                    where location_dest_id = %s and state = 'done' and location_dest_id != location_id
                    and id in (select move_id from stock_inventory_move_rel) and to_char(date, 'YYYY-MM-DD') between '%s' and '%s' and product_id = %s
                    and location_id != location_dest_id
                '''%(locat_ids_spares[0], date_from, date_to, product_id.id)
                cr.execute(sql)
                product_qty = cr.fetchone()[0]
            return product_qty
        
        def get_line_current_material(o,stock_value):  
            cur = get_opening_stock_value(o)+stock_value+self.current
            self.current = cur
            return cur
        
        def get_qty_chuaro(o):
            date_from = o.movement_id.date_from
            date_to = o.movement_id.date_to
            product_id = o.product_id
            
            #date_from = o.date_from
            #date_to = o.date_to
            #product_id = o.product_id
            
            categ = product_id.categ_id.cate_name
            if categ == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                if product_id.default_code == 'M0501060001':
                    # Doi voi san pham nay, ta da tru vao trong closing stock roi, nen ko can tru them o ham get_qty_chuaro nua
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id 
                        and product_id not in (select id from product_product where default_code = 'M0501060001')
                    '''%(product_id.id, locat_ids[0], date_from, date_to)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
                    # end
                else:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id 
                    '''%(product_id.id, locat_ids[0], date_from, date_to)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
            if categ == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                if product_id.default_code == 'M0501060001':
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id 
                        and product_id not in (select id from product_product where default_code = 'M0501060001')
                    '''%(product_id.id, locat_ids[0], date_from, date_to)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
                else:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id 
                    '''%(product_id.id, locat_ids[0], date_from, date_to)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
            return product_qty and product_qty['product_qty'] or 0
        
        def get_qty_opening_chuaro(o):
            date_from = o.movement_id.date_from
            date_to = o.movement_id.date_to
            product_id = o.product_id
            
            #date_from = o.date_from
            #date_to = o.date_to
            #product_id = o.product_id
            
            categ = product_id.categ_id.cate_name
            product_qty_chuaro = 0.0
            if categ == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                if product_id.default_code == 'M0501060001':
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id 
                        and name != '/'
                    '''%(product_id.id, locat_ids[0], date_from)
                    cr.execute(sql)
                    product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
                else:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id 
                    '''%(product_id.id, locat_ids[0], date_from)
                    cr.execute(sql)
                    product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
            if categ == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                if product_id.default_code == 'M0501060001':
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id 
                        and name != '/'
                    '''%(product_id.id, locat_ids[0], date_from)
                    cr.execute(sql)
                    product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
                else:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id 
                    '''%(product_id.id, locat_ids[0], date_from)
                    cr.execute(sql)
                    product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
            return product_qty_chuaro
        
        def get_line_qty_chuaro(o, date):            
            #product_id = o.movement_id.product_id
                        
            product_id = o.product_id
            
            categ = product_id.categ_id.cate_name
            if categ == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                if product_id.default_code == 'M0501060001':
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and location_id != location_dest_id 
                        and name != '/'
                    '''%(product_id.id, locat_ids[0], date)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
                else:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and location_id != location_dest_id
                    '''%(product_id.id, locat_ids[0], date)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
            if categ == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                if product_id.default_code == 'M0501060001':
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and location_id != location_dest_id 
                        and name != '/'
                    '''%(product_id.id, locat_ids[0], date)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
                else:
                    sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and location_id != location_dest_id
                    '''%(product_id.id, locat_ids[0], date)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()
            return product_qty and product_qty['product_qty'] or 0
        
        closing_stock = 0
        sl_chuaro = 0
        qty_chuaro = 0
        price = 0
        for seq,line in enumerate(get_detail_lines(stock)):
#             sl_chuaro = get_line_qty_chuaro(stock,line['date'])
            trans_qty = get_transaction_qty(stock,line['id'], line['material_issue_id'], line['product_dec'], line['doc_type'])
            closing_stock += trans_qty
            if line['doc_type']=='good':
                qty = 0
                value = 0
                opening_stock = get_opening_stock(stock) - get_qty_opening_chuaro(stock)
                opening_stock_value = get_opening_stock_value(stock)
                for l in stock_in_out_line:
                    qty += l[2]['transaction_quantity'] 
#                     qty_chuaro += l[2]['sl_chuaro']
                    value += l[2]['stock_value']
                if seq == 0:
                    st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
                else:
                    st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
                price = st
                st_value = (st)*(trans_qty)
            elif line['doc_type']=='product':
                qty = 0
                value = 0
                opening_stock = get_opening_stock(stock) - get_qty_opening_chuaro(stock)
                opening_stock_value = get_opening_stock_value(stock)
                for l in stock_in_out_line:
                    qty += l[2]['transaction_quantity'] 
#                     qty_chuaro += l[2]['sl_chuaro']
                    value += l[2]['stock_value']
                if seq == 0:
                    st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
                else:
                    st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
                price = st
                st_value = (st)*(trans_qty)
            else:
                price = self.current_price_unit
                st_value = stock_value(stock, line['id'], line['doc_type'])
            self.st_sum_value += st_value
            if seq == 0:
                cur = get_opening_stock_value(stock)+st_value+self.current
                closing_qty = get_opening_stock(stock) - get_qty_opening_chuaro(stock) + trans_qty + self.closing_qty
            else:
                cur = st_value+self.current
                closing_qty = trans_qty + self.closing_qty
            self.closing_qty = closing_qty
            self.current = cur
            stock_in_out_line.append((0,0,{
                'creation_date': get_create_date(line['id'], line['material_issue_id'], line['product_dec'], line['doc_type']),
                'posting_date': line['date'],
                'document_no': get_account_move_line(line['id'], line['material_issue_id'], line['product_dec'], line['doc_type']),
                'gl_document_no': line['name'],
                'document_type': get_doc_type(line['doc_type']),
                'transaction_quantity': trans_qty,
                'closing_quantity': closing_qty,
                'price_unit': price,
                'stock_value': st_value,
                'current_material_value':cur,
#                 'sl_chuaro': sl_chuaro,
            }))
        if context.get('update_price_unit_for_good_issue',False):
            return stock_in_out_line
        vals = {
            'name': 'Stock Inward and Outward Details',
            'date_from':stock.movement_id.date_from,
            'date_to':stock.movement_id.date_to,
            
            'product_id': stock.product_id.id,
            'product_uom': stock.product_id.uom_id.id,
            'product_name': stock.product_id.name,
            'product_code': stock.product_id.code,            
            'stock_in_out_line': stock_in_out_line,
            'opening_stock': get_opening_stock(stock) - get_qty_opening_chuaro(stock),
            'closing_stock': closing_stock + (get_opening_stock(stock) - get_qty_opening_chuaro(stock)) + qty_physical_inve(stock) - get_qty_chuaro(stock),
            'opening_value': get_opening_stock_value(stock),
            'closing_value': self.st_sum_value + get_opening_stock_value(stock),
        }
        
        stock_id = stock_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_tpt_stock_inward_outward_form')
        return {
                    'name': 'Stock Inward and Outward Details',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.stock.inward.outward',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': stock_id,
                }    

#TPT-Y on 07Nov2015

tpt_movement_analysis_line()

class stock_movement_analysis(osv.osv_memory):
    _name = "stock.movement.analysis"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Product Category',required = True),
#                 'product_id': fields.many2one('product.product', 'Product'),
                'product_ids': fields.many2many('product.product', 'product_movement_report', 'movement_id', 'product_id', 'Products'),  
                'date_from':fields.date('Date From',required = True),
                'date_to':fields.date('To',required = True),
                }
    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def onchange_categ_id(self, cr, uid, ids,categ_id=False, context=None):
        if categ_id:
            return {'value': {
                              'location_id': False,
                              'product_id': False,
                              } }
    def onchange_product_id(self, cr, uid, ids, categ_id=False, product_id=False, context=None):
        if categ_id and not product_id:
            return {'value': {
                                  'location_id': False,
                                  'product_id': False,
                                  } }
        elif categ_id and product_id:
            return {'value': {
                              'location_id': False,
                              } }
        elif product_id and not categ_id:
            return {'value': {
                              'location_id': False,
                              } }
    
    
    def print_report(self, cr, uid, ids, context=None):
        self.num_call_grn = {'grn_name':'','num':-1}
        self.current_transaction_qty = 0
        self.current_price_unit = 0
        self.transaction_qty = 0
        self.st_sum_value = 0
        self.current = 0
        self.good = 0
        def get_categ(o):
            categ = o.categ_id.id
#             product = o.product_id.id
            product = o.product_ids
            product_ids = [r.id for r in o.product_ids]
            pro_obj = self.pool.get('product.product')
            categ_ids = []
            if categ and product:
                for product_id in product_ids:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                                and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
                    '''%(categ,product_id)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
            if categ and not product:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                            and product_product.product_tmpl_id = product_template.id;
                '''%(categ)
                cr.execute(sql)
                categ_ids += [r[0] for r in cr.fetchall()]
            return pro_obj.browse(cr,uid,categ_ids)


        
        
        def get_qty(o, line):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            ton = 0
            inspec = 0
    #         categ_ids = self.pool.get('product.category').search(self.cr, self.uid, [('id','=',categ[0])])
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                                select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                                        and st.location_dest_id != st.location_id
                                        and (picking_id is not null
                                             or inspec_id is not null
                                             or (id in (select move_id from stock_inventory_move_rel)))
                                        and st.location_id != st.location_dest_id
                                    )foo
                            '''%(line,locat_ids[0],date_from,date_to)
                            
                cr.execute(sql)
                ton_arr = cr.fetchone()
                if ton_arr:
                    ton = ton_arr[0] or 0
                else:
                    ton = 0
#                 sql = '''
#                        select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                    '''%(line,date_from,date_to) 
#                 cr.execute(sql)
#                 for move in cr.dictfetchall():
#                    if move['action_taken'] == 'need':
#                        sql = '''
#                            select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
#                        '''%(move['id'])
#                        cr.execute(sql)
#                        inspec_arr = cr.fetchone()
#                        if inspec_arr:
#                            inspec = inspec_arr and inspec_arr[0] or 0
#                        else:
#                            inspec = 0
#                        ton = ton + inspec
                #return ton
                           
            if categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                                        and st.location_dest_id != st.location_id
                                        and (picking_id is not null
                                             or inspec_id is not null
                                             or (id in (select move_id from stock_inventory_move_rel)))
                                        and st.location_id != st.location_dest_id
                                    )foo
                            '''%(line,locat_ids[0],date_from,date_to)
                
#                 sql = '''
#                                 select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
#                                     (select st.product_qty
#                                         from stock_move st 
#                                         where st.state='done' and st.product_id = %s and st.location_dest_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
#                                     )foo
#                             '''%(line,locat_ids[0],date_from,date_to)
                cr.execute(sql)
                ton_arr = cr.fetchone()
                if ton_arr:
                    ton = ton_arr[0] or 0
                else:
                    ton = 0
#                 sql = '''
#                        select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                    '''%(line,date_from,date_to) 
#                 cr.execute(sql)
#                 for move in cr.dictfetchall():
#                    if move['action_taken'] == 'need':
#                        sql = '''
#                            select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
#                        '''%(move['id'])
#                        cr.execute(sql)
#                        inspec_arr = cr.fetchone()
#                        if inspec_arr:
#                            inspec = inspec_arr[0] or 0
#                        else:
#                            inspec = 0
#                        ton = ton  + inspec
                #return ton
            #TPT-BM- ON 28/04/2016 - to include stock adjustment qty in Rceipts Qty 
            adj_qty = 0
            sql = '''
            select adj_qty from stock_adjustment where product_id=%s and posting_date between '%s' and '%s' and state='done' and adj_type='increase'
            '''%(line, date_from, date_to)
            cr.execute(sql)
            temp = cr.fetchone()
            if temp:
                adj_qty = temp[0]
            ton = ton + adj_qty
            #
            return ton
        def get_receipt_value(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            hand_quantity = 0
            inventory = []
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
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
                                    and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
                                        or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
                                              (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
                                    )foo
                                    
                            -- TPT-BM-ON 08/08/2016 - UNION REMOVED FROM HERE - PLS REF "get_frt_cst_amt" METHOD
                
                    )a
                            '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
                            #%(locat_ids[0],product_id,date_from,date_to,date_from,date_to, date_from, date_to, product_id) #old
                cr.execute(sql)
                inventory = cr.dictfetchone()
                '''
                union                            
                            select 0 as ton_sl, case when sum(ail.line_net)!=0 then sum(ail.line_net) else 0 end as total_cost from account_invoice ai
                inner join account_invoice_line ail on ai.id=ail.invoice_id
                where ai.doc_type='freight_invoice' and  ai.date_invoice between '%s' and '%s' 
                and ail.product_id=%s
                '''
                #print sql
              # Commented by P.vinothkumar on 31/05/2016
              
#             if categ and categ =='spares':
#                 parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
#                 locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
#                 sql = '''
#                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                         (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id != st.location_id
#                             and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' 
#                             and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                                              or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
#                                               (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
#                                     )foo
#                             '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
            #TPT-VINOTH-BM-ON 24/05/2016 - Query2 UION PART IS ADDED TO ADD FREIGHT INVOICE AMOUNT
            if categ and categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
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
                                    and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
                                        or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in
                                              (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
                                    )foo
                                   
                            union
                           
                            select 0 as ton_sl, case when sum(ail.line_net)!=0 then sum(ail.line_net) else 0 end as total_cost from account_invoice ai
                inner join account_invoice_line ail on ai.id=ail.invoice_id
                where ai.doc_type='freight_invoice' and  ai.date_invoice between '%s' and '%s' and ai.state not in('draft','cancel') and
                and ail.product_id=%s
               
                    )a '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to, date_from, date_to, product_id)
             #TPT END
             #print sql
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
               '''%(product_id,date_from,date_to) 
            cr.execute(sql)
            for line in cr.dictfetchall():
               if line['action_taken'] == 'need':
                   #TPT-BM-ON 18/08/2016-To skip quality inspection record for which invoices yet to be created, since grn posting will be
                   #created once invoice is created - Rollback
#                    sql = '''
#                    select count(*) from account_move_line aml
#                     inner join stock_picking sp on aml.ref=sp.name
#                     where sp.id=%s
#                    '''%line['picking_id']
#                    cr.execute(sql)
#                    count_grn_post = cr.fetchone()[0]
#                    if count_grn_post>1:
                   #
                   sql = '''
                       select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                   '''%(line['id'])
                   cr.execute(sql)
                   inspec = cr.dictfetchone()
                   if inspec:
                       hand_quantity += inspec['qty_approve'] or 0
                       total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
                   #
            #TPT-BM-ON 15/09/2016 - TO ADD STOCK ADJ VALUE
            adj_value = 0
            sql = '''
            select case when sum(product_qty*price_unit) >0 then sum(product_qty*price_unit) else 0 end as value from stock_move sm
            inner join stock_adjustment sa on sm.stock_adj_id=sa.id
            where sa.adj_type='increase' and sm.product_id=%s and sm.date between '%s' and '%s'
            '''%(product_id, date_from, date_to)
            cr.execute(sql)
            temp = cr.fetchone()
            if temp:
                adj_value = temp[0]
            total_cost = total_cost + adj_value
                
            #
            return total_cost  
            
        def get_qty_out(o, line):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            total = 0
    #         categ_ids = self.pool.get('product.category').search(self.cr, self.uid, [('id','=',categ[0])])
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#                 sql = '''
#                                 select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
#                                     (select st.product_qty as product_qty
#                                         from stock_move st 
#                                         where st.state='done' and st.product_id = %s and st.location_id = %s 
#                                         
#                                         and picking_id in (select id from stock_picking where move_date between '%s' and '%s' and state = 'done')
#                                     )foo
#                             '''%(line,locat_ids[0],date_from,date_to)
#                 cr.execute(sql)
#                 ton = cr.dictfetchone()
                
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(line, date_from,date_to,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                
            if categ=='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
#                 sql = '''
#                                 select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
#                                     (select st.product_qty
#                                         from stock_move st 
#                                         where st.state='done' and st.product_id = %s and st.location_id = %s 
#                                         
#                                         and picking_id in (select id from stock_picking where move_date between '%s' and '%s' and state = 'done')
#                                     )foo
#                             '''%(line,locat_ids[0],date_from,date_to)
#                 cr.execute(sql)
#                 ton = cr.dictfetchone()
                
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(line, date_from,date_to,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                
            total = product_isu_qty['product_isu_qty']
            #TPT-BM- ON 28/04/2016 - to include stock adjustment qty in Rceipts Qty 
            adj_qty = 0
            sql = '''
            select adj_qty from stock_adjustment where product_id=%s and posting_date between '%s' and '%s' and state='done' and adj_type='decrease'
            '''%(line, date_from, date_to)
            cr.execute(sql)
            temp = cr.fetchone()
            if temp:
                adj_qty = temp[0]
            total = total + adj_qty
            return total
        
        def get_qty_chuaro(o, line):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            if categ == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                    from stock_move where product_id = %s and state = 'done' and issue_id is null 
                    and picking_id is null and inspec_id is null and location_id = %s 
                    and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id
                '''%(line, locat_ids[0], date_from,date_to)
                cr.execute(sql)
                product_qty = cr.dictfetchone()
            if categ == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                    from stock_move where product_id = %s and state = 'done' and issue_id is null 
                    and picking_id is null and inspec_id is null and location_id = %s 
                    and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id
                '''%(line, locat_ids[0], date_from,date_to)
                cr.execute(sql)
                product_qty = cr.dictfetchone()
            return product_qty and product_qty['product_qty'] or 0
        def finish_stock_value(product_id, location_id):
            avg_cost = 0
            #===================================================================
            # avg_cost_obj = self.pool.get('tpt.product.avg.cost')
            # avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',product_id),('warehouse_id','=',location_id)])
            # if avg_cost_ids:
            #     avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
            #     avg_cost = avg_cost_id.avg_cost   
            #===================================================================
            prod_obj = self.pool.get('product.product')
            prod_id = prod_obj.browse(cr, uid, product_id)
            avg_cost = prod_id.standard_price or 0
            return avg_cost or 0
        def get_consumption_value(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            consum_value = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#                 sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
#  
#                                 and ( (issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and state in ('done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_to)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
#                 if inventory:
#                     hand_quantity = inventory['ton_sl'] or 0
#                     total_cost = inventory['total_cost'] or 0
#                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(product_id, date_from,date_to,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()['product_isu_qty']
                consum_value = product_isu_qty
#                 sql = '''
#                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                         (select st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
#                         union all
#                             select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
#                         )foo
#                 '''%(locat_ids[0],product_id,date_from,date_to,locat_ids[0],product_id,date_from,date_to)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
            if categ and categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
#                 sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s
#                                 and ( (issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and state in ('done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_to)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
#                 if inventory:
#                     hand_quantity = inventory['ton_sl'] or 0
#                     total_cost = inventory['total_cost'] or 0
#                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(product_id, date_from,date_to,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()['product_isu_qty']
                consum_value = product_isu_qty
                #TPT-BM-ON 15/09/2016 - TO INCLUDE STOCK ADJ VALUE INTO SM ANALYSIS REPORT
                adj_value = 0
                sql = '''
                select case when sum(product_qty*price_unit) >0 then sum(product_qty*price_unit) else 0 end as value from stock_move sm
                inner join stock_adjustment sa on sm.stock_adj_id=sa.id
                where sa.adj_type='decrease' and sm.product_id=%s and sm.date between '%s' and '%s'
                '''%(product_id, date_from, date_to)
                cr.execute(sql)
                temp = cr.fetchone()
                if temp:
                    adj_value = temp[0]
                consum_value = consum_value + adj_value
                #
            return consum_value        
        
        def get_opening_stock(o,product_id):
            categ = o.categ_id.cate_name
            date_from = o.date_from
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
                                    )
                    '''%(locat_ids[0],product_id,date_from,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                
#                 sql = '''
#                     select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
#                     from stock_move where product_id = %s and state = 'done' and issue_id is null 
#                     and picking_id is null and inspec_id is null and location_id = %s 
#                     and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
#                 '''%(product_id, locat_ids[0], date_from)
#                 cr.execute(sql)
#                 product_qty = cr.dictfetchone()['product_qty']
                
                open_qty = (inventory and inventory['ton_sl'] or 0) - product_isu_qty 
            if categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
                sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state = 'done'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
                                    )
                    '''%(locat_ids[0],product_id,date_from,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                
#                 sql = '''
#                     select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
#                     from stock_move where product_id = %s and state = 'done' and issue_id is null 
#                     and picking_id is null and inspec_id is null and location_id = %s 
#                     and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
#                 '''%(product_id, locat_ids[0], date_from)
#                 cr.execute(sql)
#                 product_qty = cr.dictfetchone()['product_qty']
                
                open_qty = (inventory and inventory['ton_sl'] or 0) - product_isu_qty
            return open_qty 
        
        def get_opening_stock_value(o, product_id):
            date_from = o.date_from
            categ = o.categ_id.cate_name
            opening_stock_value = 0
            production_value = 0
            product = self.pool.get('product.product').browse(cr,uid,product_id)
#             if categ=='raw':
#                 parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
#                 locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#                 sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                             where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
#                                 and st.location_dest_id != st.location_id
#                                 and ( picking_id is not null 
#                                 or inspec_id is not null 
#                                 or (st.id in (select move_id from stock_inventory_move_rel))
#                         )
#                     '''%(locat_ids[0],product_id,date_from)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                #TPT START - By P.vinothkumar - ON 31/05/2015 - FOR (adding freight invoice details in query)
                sql = '''
                          select sum(a.ton_sl) ton_sl, sum(a.total_cost) total_cost from
                        (select 
                        case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
                        case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                                                        and st.location_dest_id != st.location_id
                                                        and ( picking_id is not null 
                                                        or inspec_id is not null 
                                                        or (st.id in (select move_id from stock_inventory_move_rel))
                                                )
                        union
                                        select 0 as ton_sl, case when sum(ail.line_net)!=0 then sum(ail.line_net) else 0 end as total_cost from account_invoice ai
                                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                                        where ai.doc_type='freight_invoice' and  ai.date_invoice < '%s' and ai.state not in ('draft','cancel')
                                        and ail.product_id=%s)a
                    '''%(locat_ids[0],product_id,date_from,date_from,product_id)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                #TPT End
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
#                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                   select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is not null
                        
                '''%(locat_ids[0],product_id,date_from)
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                
                if product.default_code == 'M0501060001':
                   sql = '''
                       select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is null and picking_id is null and inspec_id is null 
                        and id in (select move_id from mrp_production_move_ids)
                            
                   '''%(locat_ids[0],product.id,date_from)
                   cr.execute(sql)
                   production_value = cr.fetchone()[0]
                opening_stock_value = total_cost-(product_isu_qty)-production_value
              #commented by P.vinothkumar on 31/05/2016  
#             if categ =='spares':
#                 parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
#                 locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
#                 sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                             where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
#                                 and st.location_dest_id != st.location_id
#                                 and ( picking_id is not null 
#                                 or inspec_id is not null 
#                                 or (st.id in (select move_id from stock_inventory_move_rel))
#                         )
#                     '''%(locat_ids[0],product_id,date_from)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
            if categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
                #TPT START - By P.vinothkumar - ON 31/05/2015 - FOR (adding freight invoice details in query)
                sql = '''
                          select sum(a.ton_sl) ton_sl, sum(a.total_cost) total_cost from
                        (select 
                        case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
                        case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                                                        and st.location_dest_id != st.location_id
                                                        and ( picking_id is not null 
                                                        or inspec_id is not null 
                                                        or (st.id in (select move_id from stock_inventory_move_rel))
                                                )
                        union
                                        select 0 as ton_sl, case when sum(ail.line_net)!=0 then sum(ail.line_net) else 0 end as total_cost from account_invoice ai
                                        inner join account_invoice_line ail on ai.id=ail.invoice_id
                                        where ai.doc_type='freight_invoice' and  ai.date_invoice < '%s' and ai.state not in ('draft','cancel')
                                        and ail.product_id=%s)a
                    '''%(locat_ids[0],product_id,date_from,date_from,product_id)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                #TPT End
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
#                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                   select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is not null
                        
                '''%(locat_ids[0],product_id,date_from)
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                if product.default_code == 'M0501060001':
                   sql = '''
                       select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                        and issue_id is null and picking_id is null and inspec_id is null 
                        and id in (select move_id from mrp_production_move_ids)
                            
                   '''%(locat_ids[0],product.id,date_from)
                   cr.execute(sql)
                   production_value = cr.fetchone()[0]
                opening_stock_value = total_cost-(product_isu_qty)-production_value
            return opening_stock_value    
        
        def get_closing_stock(o, receipt,consum,opening):
            total_cost = 0
            total_cost = receipt - consum + opening
            return total_cost  
        
        def get_detail_lines(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
#             product_id = o.product_id
            parent_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
            parent_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
            sql = '''
                select * from account_move where doc_type in ('good', 'grn', 'product', 'freight') 
                    and date between '%(date_from)s' and '%(date_to)s'
                    and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where to_char(date_invoice, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                        or (ref in (select name from stock_picking where id in (select picking_id from stock_move where to_char(date, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and product_id=%(product_id)s)))
                    ) or material_issue_id in (select id from tpt_material_issue where date_expec between '%(date_from)s' and '%(date_to)s' and warehouse in (%(location_row_id)s,%(location_spare_id)s) and id in (select material_issue_id from tpt_material_issue_line where product_id=%(product_id)s)) 
                        )
                        or product_dec in (select id from mrp_production where date_planned between '%(date_from)s' and '%(date_to)s' and id in (select production_id from mrp_production_move_ids where move_id in (select id from stock_move where product_id = %(product_id)s and location_id in (%(location_row_id)s,%(location_spare_id)s) ))
                         )
                         order by date,doc_type = 'grn' desc, doc_type = 'good' desc, doc_type = 'product' desc, id
            '''%{'date_from':date_from,
                 'date_to':date_to,
                 'product_id':product_id.id,
                 'location_row_id':locat_ids_raw[0],
                 'location_spare_id':locat_ids_spares[0]}
            cr.execute(sql)
            move_line = []
            for line in cr.dictfetchall():
#                 if line['doc_type'] != 'grn':
#                     move_line.append(line)
                if line['doc_type'] == 'grn':
                    sql = '''
                        select * from stock_move
                        where  picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s) and product_id = %s)
                    '''%(line['id'], product_id.id)
                    cr.execute(sql)
                    for move in cr.dictfetchall():
                        if move['action_taken'] == 'direct' and move['location_dest_id'] in [locat_ids_raw[0],locat_ids_spares[0]]:
                            move_line.append(line)
                        if move['action_taken'] == 'need':
                            sql = '''
                                select id, qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining') and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                            '''%(move['id'], date_from, date_to)
                            cr.execute(sql)
                            for move_sql in cr.dictfetchall():
                                if move_sql['qty_approve']:
                                    sql = '''
                                        select id from stock_move where inspec_id = %s and state = 'done' and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                                    '''%(move_sql['id'], date_from, date_to)
                                    cr.execute(sql)
                                    move_sql2 = cr.fetchall()
                                    if move_sql2:
                                        move_line.append(line)
                elif line['doc_type'] == 'product' and product_id.code == 'M0501060001':
                    move_line.append(line)
                else:
                    move_line.append(line)
            return move_line 
        
        def get_account_move_line(move_id, material_issue_id, move_type):
            
            move = self.pool.get('account.move').browse(cr,uid,move_id)
            if move_type == 'freight':
                sql = '''
                   select name from account_invoice where move_id = %s and sup_inv_id is not null
                '''%(move_id)
                cr.execute(sql)
                for invoice in cr.dictfetchall():
                   name = invoice['name'] or 0
            if move_type == 'good':
                sql = '''
                    select doc_no from tpt_material_issue where id = %s 
                '''%(material_issue_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['doc_no']
            if move_type == 'grn':
                sql = '''
                   select name from stock_picking where name in (select ref from account_move_line where move_id = %s) 
                '''%(move_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['name']
            return name
        
        def get_transaction_qty(o, move_id, material_issue_id, product_dec, move_type, product_id):
            date_from = o.date_from
            date_to = o.date_to
            categ = product_id.categ_id.cate_name
            quantity = 0
            price_unit = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                if move_type == 'freight':
                    quantity = 0
                if move_type == 'product':
                    production_id = self.pool.get('mrp.production').browse(cr,uid,product_dec)
                    for line in production_id.move_lines2:
                        if line.product_id.id == product_id.id:
                            quantity += line.product_qty
                    quantity = -quantity
                if move_type == 'good':
                    sql = '''
                        select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                        where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                        group by product_id 
                    '''%(material_issue_id, locat_ids[0], product_id.id)
                    cr.execute(sql)
                    for qty in cr.dictfetchall():
                        quantity = qty['product_isu_qty']
                if move_type == 'grn':
                    sql = '''
                        select * from stock_move
                        where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s)) 
                        and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                    '''%(move_id, product_id.id)
                    cr.execute(sql)
                    moves = cr.dictfetchall()
                    grn_name = get_account_move_line(move_id, material_issue_id, move_type)
                    if self.num_call_grn['grn_name']==grn_name:
                        self.num_call_grn['num'] += 1
                    else:
                        self.num_call_grn['grn_name']=grn_name
                        self.num_call_grn['num'] = 0
                    if len(moves)>self.num_call_grn['num']:
                        move = moves[self.num_call_grn['num']]
                        if move['action_taken'] == 'direct' and move['location_dest_id']==locat_ids[0]:
                            quantity = move['product_qty']
                            price_unit = move['price_unit']
                        if move['action_taken'] == 'need':
                            sql1 = '''
                                select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                            '''%(move['id'])
                            cr.execute(sql1)
                            need = cr.dictfetchone()
                            if need:
                                quantity = need['qty_approve'] or 0
                                price_unit = move['price_unit']
            if categ=='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                if move_type == 'freight':
                    quantity = 0
                if move_type == 'product':
                    production_id = self.pool.get('mrp.production').browse(cr,uid,product_dec)
                    for line in production_id.move_lines2:
                        if line.product_id.id == product_id.id:
                            quantity += line.product_qty
                    quantity = -quantity
                if move_type == 'good':
                    sql = '''
                        select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                        where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                        group by product_id 
                    '''%(material_issue_id, locat_ids[0], product_id.id)
                    cr.execute(sql)
                    for qty in cr.dictfetchall():
                        quantity = qty['product_isu_qty']
                if move_type == 'grn':
                    sql = '''
                        select * from stock_move
                        where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s)) 
                        and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                    '''%(move_id, product_id.id)
                    cr.execute(sql)
                    moves = cr.dictfetchall()
                    grn_name = get_account_move_line(move_id, material_issue_id, move_type)
                    if self.num_call_grn['grn_name']==grn_name:
                        self.num_call_grn['num'] += 1
                    else:
                        self.num_call_grn['grn_name']=grn_name
                        self.num_call_grn['num'] = 0
                    if len(moves)>self.num_call_grn['num']:
                        move = moves[self.num_call_grn['num']]
                        if move['action_taken'] == 'direct' and move['location_dest_id']==locat_ids[0]:
                            quantity = move['product_qty']
                            price_unit = move['price_unit']
                        if move['action_taken'] == 'need':
                            sql1 = '''
                                select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                            '''%(move['id'])
                            cr.execute(sql1)
                            need = cr.dictfetchone()
                            if need:
                                quantity = need['qty_approve'] or 0
                                price_unit = move['price_unit']
            self.transaction_qty += quantity
            self.current_transaction_qty = quantity
            self.current_price_unit = price_unit
            return quantity
        
        def stock_value(product_id, move_id, doc_type):
            if doc_type=='freight':
                self.current_transaction_qty = 1
                sql = '''
                    select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                    where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                    group by product_id
                   '''%(product_id.id, move_id)
                cr.execute(sql)
                for inventory in cr.dictfetchall():
                    avg_cost = inventory['line_net'] or 0
                    return self.current_transaction_qty*avg_cost
            else:
                return self.current_transaction_qty*self.current_price_unit
            
        def get_qty_opening_chuaro(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
#             product_id = o.product_id
            categ = o.categ_id.cate_name
            if categ == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                    from stock_move where product_id = %s and state = 'done' and issue_id is null 
                    and picking_id is null and inspec_id is null and location_id = %s 
                    and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
                '''%(product_id, locat_ids[0], date_from)
                cr.execute(sql)
                product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
            if categ == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                    from stock_move where product_id = %s and state = 'done' and issue_id is null 
                    and picking_id is null and inspec_id is null and location_id = %s 
                    and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
                '''%(product_id, locat_ids[0], date_from)
                cr.execute(sql)
                product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
            return product_qty_chuaro
        
        def get_line_stock_value(o, move_id, material_issue_id, move_type, date, product_id):
           date_from = o.date_from
           date_to = o.date_to
           categ = product_id.categ_id.cate_name
           opening_stock_value = 0
           total_cost = 0
           hand_quantity = 0
           if categ=='raw':
               parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
               locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
               if move_type == 'freight':
                   sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                       group by product_id
                   '''%(product_id.id, move_id)
                   cr.execute(sql)
                   for inventory in cr.dictfetchall():
                       avg_cost = inventory['line_net'] or 0
               
               if move_type == 'grn':
                   sql = '''
                            select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id != st.location_id
                            and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                            and st.location_dest_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s')
                            
                    '''%(product_id.id, locat_ids[0], date)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                   sql = '''
                       select * from stock_move where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s))
                   '''%(move_id) 
                   cr.execute(sql)
                   for line in cr.dictfetchall():
                       if line['action_taken'] == 'need':
                           sql = '''
                               select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                           '''%(line['id'])
                           cr.execute(sql)
                           inspec = cr.dictfetchone()
                           if inspec:
                               hand_quantity += inspec['qty_approve'] or 0
                               total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           
               if move_type == 'good':
                   good = self.pool.get('tpt.material.issue').browse(cr,uid,material_issue_id)
                   sql = '''
                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                         from stock_move st
                             join stock_location loc1 on st.location_id=loc1.id
                             join stock_location loc2 on st.location_dest_id=loc2.id
                         where st.state='done' and st.location_dest_id != st.location_id
                         and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                         and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                            
                    '''%(product_id.id, locat_ids[0], good.date_expec)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                       avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
           
           if categ=='spares':
               parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
               locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])]) 
               if move_type == 'freight':
                   sql = '''
                       select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                       where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                       group by product_id
                   '''%(product_id.id, move_id)
                   cr.execute(sql)
                   for inventory in cr.dictfetchall():
                       avg_cost = inventory['line_net'] or 0
               
               if move_type == 'grn':
                   sql = '''
                            select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id != st.location_id
                            and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                            and st.location_dest_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s')
                            
                    '''%(product_id.id, locat_ids[0], date)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                   sql = '''
                       select * from stock_move where picking_id in (select id from stock_picking where name in (select ref from account_move_line where move_id = %s))
                   '''%(move_id) 
                   cr.execute(sql)
                   for line in cr.dictfetchall():
                       if line['action_taken'] == 'need':
                           sql = '''
                               select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                           '''%(line['id'])
                           cr.execute(sql)
                           inspec = cr.dictfetchone()
                           if inspec:
                               hand_quantity += inspec['qty_approve'] or 0
                               total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
           
               if move_type == 'good':
    
                   sql = '''
                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                         from stock_move st
                             join stock_location loc1 on st.location_id=loc1.id
                             join stock_location loc2 on st.location_dest_id=loc2.id
                         where st.state='done' and st.location_dest_id != st.location_id
                         and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                         and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                            
                    '''%(product_id.id, locat_ids[0], date)
                   cr.execute(sql)
                   inventory = cr.dictfetchone()
                   if inventory:
                       hand_quantity = inventory['ton_sl'] or 0
                       total_cost = inventory['total_cost'] or 0
                       avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
        
        #TPT-BM-ON 07/07/2016 - FOR FREIGHT-CST INCLUSION
        def get_frt_cst_amt(product_id, from_date, to_date):
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
                and ai.date_invoice < '%s' 
            '''%(product_id, '%', '%', from_date)
            cr.execute(sql)
            cst_amt = cr.fetchone()
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
                and ai.date_invoice < '%s'
            '''%(product_id, from_date)
            cr.execute(sql)
            frt_amt = cr.fetchone()
            if frt_amt:
                amt_opening += frt_amt[0]   
            #TPT-BM-01/08/2016 - Opening for supplier invoice with freight value entered
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
                and ai.date_invoice < '%s'
            '''%(product_id, from_date)
            cr.execute(sql)
            si_frt_amt = cr.fetchone()
            if si_frt_amt:
                amt_opening += si_frt_amt[0] 
            #tpt-end
            # --------------- #
            sql = '''
                select
                case when sum(ail.tpt_tax_amt)>=0 then sum(ail.tpt_tax_amt) else 0 end as cst_amt 
                from account_invoice ai
                inner join account_invoice_line ail on ai.id=ail.invoice_id
                inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                inner join account_tax t on ailt.tax_id = t.id
                where ail.product_id=%s and ai.state not in ('draft', 'cancel') 
                and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
                and ai.date_invoice between '%s' and '%s'
            '''%(product_id, '%', '%', from_date, to_date)
            cr.execute(sql)
            #print sql
            cst_amt1 = cr.fetchone()
            if cst_amt1:
                amt_receipt += cst_amt1[0]
            #click here
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
                and ai.date_invoice between '%s' and '%s'
            '''%(product_id, from_date, to_date)
            cr.execute(sql)
            #print sql
            frt_amt1 = cr.fetchone()
            if frt_amt1:
                amt_receipt += frt_amt1[0]    
            #TPT-BM-01/08/2016 - Opening for supplier invoice with freight value entered 
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
                and ai.date_invoice between '%s' and '%s'
            '''%(product_id, from_date, to_date)
            cr.execute(sql)
            si_frt_amt = cr.fetchone()
            if si_frt_amt:
                amt_receipt += si_frt_amt[0] 
            #tpt-end             
            return amt_opening, amt_receipt   
        #
        
        def get_consumption_value(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
#             product_id = o.product_id
            categ = o.categ_id.cate_name
            consum_value = 0
            product = self.pool.get('product.product').browse(cr,uid,product_id)
#             print product_id, product.name
            if categ == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end tong
                        from stock_move st
                        where st.state='done' and st.product_id=%s
                            and st.location_dest_id != st.location_id
                            and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
                            and  (
                                issue_id is not null
                            and id not in (select id
                                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                                and picking_id is null and inspec_id is null and location_id = %s 
                                and location_id != location_dest_id)
                    )
                '''%(product_id, date_from, date_to, product_id, locat_ids[0])
                cr.execute(sql)
                #print sql
                consum_value = cr.dictfetchone()['tong']
                
                if product.default_code == 'M0501060001':
                    sql = '''
                        select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end tong
                            from stock_move
                            where state='done' and product_id in (select id from product_product where default_code = 'M0501060001')
                                and location_dest_id != location_id
                                and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
                                and  (
                                     issue_id is not null
                                or (location_id = %s and id in (select move_id from mrp_production_move_ids))
                        )
                    '''%(date_from, date_to, locat_ids[0])
                    cr.execute(sql)
                    consum_value = cr.dictfetchone()['tong']
                    
            if categ == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_qty * price_unit)!=0 then sum(product_qty * price_unit) else 0 end tong
                        from stock_move st
                        where st.state='done' and st.product_id=%s
                            and st.location_dest_id != st.location_id
                            and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
                            and  (
                                issue_id is not null
                            and id not in (select id
                                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                                and picking_id is null and inspec_id is null and location_id = %s 
                                and location_id != location_dest_id)
                    )
                '''%(product_id, date_from, date_to, product_id, locat_ids[0])
                cr.execute(sql)
                consum_value = cr.dictfetchone()['tong']
            return consum_value
           
            
        stock_obj = self.pool.get('tpt.form.movement.analysis')
        cr.execute('delete from tpt_form_movement_analysis')
        stock = self.browse(cr, uid, ids[0])
        move_analysis_line = []
        if stock.categ_id.cate_name=='raw': # TPT-Added by BalamuruganPurushothaman on 07/09/2015 - TO FIX PERFORMANCE ISSUE - THE FOLLOWING BLOCK WILL BE EXECUTED FOR RAWMATERIAL CATEGORY ONLY
            for line in get_categ(stock):
    #             stock_in_out_line = []
    #             good = 0
    #             current = 0
    #             product = 0
    #             for seq, phuoc in enumerate(get_detail_lines(stock, line)):
    #                 trans_qty = get_transaction_qty(stock,phuoc['id'], phuoc['material_issue_id'], phuoc['product_dec'], phuoc['doc_type'], line)
    #                 if phuoc['doc_type']=='good':
    #                     qty = 0
    #                     value = 0
    #                     opening_stock = get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)
    #                     opening_stock_value = get_opening_stock_value(stock,line.id)
    #                     for l in stock_in_out_line:
    #                         qty += l[2]['transaction_quantity'] 
    #                         value += l[2]['stock_value']
    #                     if seq == 0:
    #                         st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
    #                     else:
    #                         st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
    #                     st_value = (st)*(trans_qty)
    #                     good += (-st_value)
    #                 elif phuoc['doc_type']=='product':
    #                     qty = 0
    #                     value = 0
    #                     opening_stock = get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)
    #                     opening_stock_value = get_opening_stock_value(stock,line.id)
    #                     for l in stock_in_out_line:
    #                         qty += l[2]['transaction_quantity'] 
    #                         value += l[2]['stock_value']
    #                     if seq == 0:
    #                         st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
    #                     else:
    #                         st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
    #                     st_value = (st)*(trans_qty)
    #                     product += (-st_value)
    #                 else:
    #                     st_value = stock_value(line, phuoc['id'], phuoc['doc_type'])
    #                 self.st_sum_value += st_value
    #                 if seq == 0:
    #                     cur = get_opening_stock_value(stock,line.id)+st_value+current
    #                 else:
    #                     cur = st_value+current
    #                 current = cur
    #                 stock_in_out_line.append((0,0,{
    #                     'transaction_quantity': trans_qty,
    #                     'stock_value': st_value,
    #                     'current_material_value':cur,
    #                 }))
                
                open_stock = get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)
                open_value = get_opening_stock_value(stock,line.id)
                receipt_qty = get_qty(stock,line.id)
                receipt_value = get_receipt_value(stock,line.id) 
                consum_qty = get_qty_out(stock,line.id) + get_qty_chuaro(stock,line.id)
                consum_value = get_consumption_value(stock, line.id)
                #TPT-BM-ON 07/07/2016 - FOR FREIGHT-CST INCLUSION- enabled on 01/08/2016
                opening, receipt = get_frt_cst_amt(line.id, stock.date_from, stock.date_to) 
                open_value += opening 
                receipt_value += receipt
                #TPT-END
                move_analysis_line.append((0,0,{
                    'item_code': line.default_code,
                    'item_name': line.name,
                    'uom':line.uom_id and line.uom_id.name or 0,
                    'open_stock': open_stock,
                    'open_value': open_value,
                    'receipt_qty':receipt_qty,
                    'receipt_value':receipt_value,
                    'consum_qty':consum_qty,
                    'consum_value': consum_value,    
                    'close_stock':receipt_qty - (consum_qty) + (open_stock) ,
                    'close_value': open_value + receipt_value - consum_value,  
                    'product_id': line.id or False,     
                
                }))
        # TPT - ON 07/09/2015 BY BalamuruganPurushothaman - TO FIX PERFORMANCE ISSUE - FOR SPARE MATERIALS
        if stock.categ_id.cate_name=='spares':
            if stock.product_ids:
                product = stock.product_ids
                product_ids = [r.id for r in stock.product_ids]
                product_ids = str(product_ids).replace("[", "")
                product_ids = product_ids.replace("]", "")
                sql = '''
                select pp.id as product_id, pp.default_code, pp.name_template as name, pu.name as uom,
                
                (select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%(location_spare_id)s 
                            and st.product_id=pp.id  and 
                            to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s'
                            and state = 'done'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from 
                                stock_inventory_move_rel where inventory_id in 
                                (select id from stock_inventory where 
          to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s' and state = 'done')))
                                    )) - ((select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = pp.id and material_issue_id in (select id from tpt_material_issue where date_expec 
                < '%(date_from)s' and warehouse = %(location_spare_id)s and state = 'done')) 
                +
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                            from stock_move where product_id = pp.id and state = 'done' and issue_id is null 
                            and picking_id is null and inspec_id is null and location_id = %(location_spare_id)s 
                            and date < '%(date_from)s' and location_id != location_dest_id)) opening_stock, 
                
                (select case when sum(st.product_qty*price_unit)!=0 then sum(st.product_qty*price_unit) else 0 end ton_sl
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%(location_spare_id)s 
                            and st.product_id=pp.id  and 
                            to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s'
                            and state = 'done'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from 
                                stock_inventory_move_rel where inventory_id in 
                                (select id from stock_inventory where 
          to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s' and state = 'done')))
                                    ))-(select case when sum(price_unit*product_qty)>0 then sum(price_unit*product_qty) else 0 end from stock_move 
                where issue_id is not null and product_id=pp.id
                and date < '%(date_from)s' 
                and state='done' )  opening_stock_value, 
               
                (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                            (select st.product_qty
                                                from stock_move st 
                                                where st.state='done' and st.product_id = pp.id and 
                                                st.location_dest_id = %(location_spare_id)s and date between '%(date_from)s' and '%(date_to)s'
                                                and st.location_dest_id != st.location_id
                                                and (picking_id is not null
                                                     or inspec_id is not null
                                                     or (id in (select move_id from stock_inventory_move_rel)))
                                                and st.location_id != st.location_dest_id
                                                and st.state = 'done'
                                            )foo)
                         +
                         (select case when sum(adj_qty)!=0 then sum(adj_qty) else 0 end adj_qty from stock_adjustment where product_id=pp.id and posting_date between '%(date_from)s' and '%(date_to)s' and state='done' 
                         and adj_type='increase')                   
                                             receipt_qty,
                
                (select case when sum(product_qty*price_unit)>0 then sum(product_qty*price_unit) else 0 end from stock_move where product_id=pp.id and location_dest_id=%(location_spare_id)s 
                and date between '%(date_from)s' and '%(date_to)s' and state = 'done') 
                +
                (
                select case when sum(sm.product_qty*sm.price_unit) >0 then sum(sm.product_qty*sm.price_unit) else 0 end as value from stock_move sm
                inner join stock_adjustment sa on sm.stock_adj_id=sa.id
                where sa.adj_type='increase' and sm.product_id=pp.id and sm.date between '%(date_from)s' and '%(date_to)s'
                )
                receipt_value,
                
                
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_isu_qty from stock_move where product_id=pp.id and issue_id is not null and 
                date between '%(date_from)s' and '%(date_to)s' and state='done') 
                +

                (select case when sum(sm.product_qty)!=0 then sum(sm.product_qty) else 0 end product_qty  from stock_adjustment sa
                inner join stock_move sm on sa.id=sm.stock_adj_id
                where sm.state='done' and sm.product_id=pp.id and sm.date between '%(date_from)s' and '%(date_to)s'
                )              
                             consum_qty,
                 
                
                (select case when sum(price_unit*product_qty)>0 then sum(price_unit*product_qty) else 0 end from stock_move 
                where issue_id is not null and product_id=pp.id and date between '%(date_from)s' and '%(date_to)s' and state = 'done'
                ) +
                (
                select case when sum(sm.product_qty*sm.price_unit) >0 then sum(sm.product_qty*sm.price_unit) else 0 end as value from stock_move sm
                inner join stock_adjustment sa on sm.stock_adj_id=sa.id
                where sa.adj_type='decrease' and sm.product_id=pp.id and sm.date between '%(date_from)s' and '%(date_to)s'
                )
                as
                consum_value
                                            
                from product_product pp
                inner join product_template pt on  pp.product_tmpl_id=pt.id
                inner join product_uom pu on pt.uom_id=pu.id
                where pp.cate_name='spares'
                and pp.id in (%(product_id)s)
                order by pp.default_code
                '''%{'date_from':stock.date_from,
                    'date_to':stock.date_to,
                    'location_spare_id':14,
                    'product_id':product_ids#stock.product_id.id prev sql - and pp.id = %(product_id)s
                    }
                cr.execute(sql)  
                #TPT-BalamuruganPurushothaman - ON 11/03/2016  - for stock mimatch b/w onhand & stock inward/outware report 
                '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = pp.id and material_issue_id in (select id from tpt_material_issue where date_expec 
                between '%(date_from)s' and '%(date_to)s' and warehouse = %(location_spare_id)s and state = 'done')
                
                ----------above changed into the following script for calculating sum of issued quantity for the given period---------------
                
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_isu_qty from stock_move where product_id=pp.id and issue_id is not null and 
                date between '%(date_from)s' and '%(date_to)s' and state='done'
                
                --- tpt-bm-on 16/09/2016 removed the following from consumption qty script
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                            from stock_move where product_id = pp.id and state = 'done' and issue_id is null 
                            and picking_id is null and inspec_id is null and location_id = %(location_spare_id)s 
                            and date between '%(date_from)s' and '%(date_to)s' and location_id != location_dest_id)
                ''' 
                #TPT-END
            else:
                sql = '''
                select pp.id as product_id, pp.default_code, pp.name_template as name, pu.name as uom,
                
                (select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%(location_spare_id)s 
                            and st.product_id=pp.id  and 
                            to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s'
                            and state = 'done'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from 
                                stock_inventory_move_rel where inventory_id in 
                                (select id from stock_inventory where 
          to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s' and state = 'done')))
                                    ))- ((select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = pp.id and material_issue_id in (select id from tpt_material_issue where date_expec 
                < '%(date_from)s' and warehouse = %(location_spare_id)s and state = 'done')) 
                +
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                            from stock_move where product_id = pp.id and state = 'done' and issue_id is null 
                            and picking_id is null and inspec_id is null and location_id = %(location_spare_id)s 
                            and date < '%(date_from)s' and location_id != location_dest_id)) opening_stock, 
                
                (select case when sum(st.product_qty*price_unit)!=0 then sum(st.product_qty*price_unit) else 0 end ton_sl
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%(location_spare_id)s 
                            and st.product_id=pp.id  and 
                            to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s'
                            and state = 'done'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from 
                                stock_inventory_move_rel where inventory_id in 
                                (select id from stock_inventory where 
          to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%(date_from)s' and state = 'done')))
                                    )) -(select case when sum(price_unit*product_qty)>0 then sum(price_unit*product_qty) else 0 end 
                                    from stock_move 
                where issue_id is not null and product_id=pp.id
                and date < '%(date_from)s' 
                and state='done' )  opening_stock_value, 
               
                (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                            (select st.product_qty
                                                from stock_move st 
                                                where st.state='done' and st.product_id = pp.id and 
                                                st.location_dest_id = %(location_spare_id)s and date between '%(date_from)s' and '%(date_to)s'
                                                and st.location_dest_id != st.location_id
                                                and (picking_id is not null
                                                     or inspec_id is not null
                                                     or (id in (select move_id from stock_inventory_move_rel)))
                                                and st.location_id != st.location_dest_id
                                                and st.state = 'done'
                                            )foo)
                              +
                              (select case when sum(adj_qty)!=0 then sum(adj_qty) else 0 end adj_qty from stock_adjustment where product_id=pp.id and posting_date between '%(date_from)s' and '%(date_to)s' and state='done' 
                         and adj_type='increase')                  
                                             receipt_qty,
                
                (select case when sum(product_qty*price_unit)>0 then sum(product_qty*price_unit) else 0 end from stock_move where product_id=pp.id and location_dest_id=%(location_spare_id)s 
                and date between '%(date_from)s' and '%(date_to)s' and state = 'done') receipt_value,
                
                
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_isu_qty from stock_move where product_id=pp.id and issue_id is not null and 
                date between '%(date_from)s' and '%(date_to)s' and state='done') 
                +
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                            from stock_move where product_id = pp.id and state = 'done' and issue_id is null 
                            and picking_id is null and inspec_id is null and location_id = %(location_spare_id)s 
                            and date between '%(date_from)s' and '%(date_to)s' and location_id != location_dest_id)
                +
                (select case when sum(adj_qty)!=0 then sum(adj_qty) else 0 end adj_qty   from stock_adjustment where product_id=pp.id and posting_date between '%(date_from)s' and '%(date_to)s' and state='done' 
                and adj_type='decrease')    
                             consum_qty,
                 
                
                (select case when sum(price_unit*product_qty)>0 then sum(price_unit*product_qty) else 0 end from stock_move 
                where issue_id is not null and product_id=pp.id
                and date between '%(date_from)s' and '%(date_to)s'
                and state = 'done'
                ) consum_value
                                            
                from product_product pp
                inner join product_template pt on  pp.product_tmpl_id=pt.id
                inner join product_uom pu on pt.uom_id=pu.id
                where pp.cate_name='spares'
                order by pp.default_code
                '''%{'date_from':stock.date_from,
                    'date_to':stock.date_to,
                    'location_spare_id':14,
                    }
                cr.execute(sql) 
            #print sql
            for line in cr.dictfetchall():
                #
                opening_value = line['opening_stock_value'] or 0
                receipt_value = line['receipt_value'] or 0
                #TPT-BM-ON 07/07/2016 - FOR FREIGHT-CST INCLUSION
                opening, receipt = get_frt_cst_amt(line['product_id'], stock.date_from, stock.date_to)
                opening_value += opening
                receipt_value += receipt
                #TPT_END
                move_analysis_line.append((0,0,{
                    'item_code': line['default_code'],
                    'item_name': line['name'],
                    'uom':line['uom'] or 0,
                    'open_stock': line['opening_stock'] or 0,
                    'open_value': opening_value or 0,
                    'receipt_qty':line['receipt_qty'] or 0,
                    'receipt_value':receipt_value or 0,
                    'consum_qty':line['consum_qty'] or 0,
                    'consum_value': line['consum_value'] or 0 , 
                    'close_stock':line['opening_stock'] + line['receipt_qty'] - line['consum_qty'] or 0,
                    'close_value':opening_value + receipt_value - line['consum_value'], 
                    'product_id': line['product_id'] or False,                              
                                                
                                                
        }))
        if stock.categ_id.cate_name=='finish':
            location_id=13
            res = []
            res1 = []
            if stock.product_ids:
                product = stock.product_ids
                product_ids = [r.id for r in stock.product_ids]
                product_ids = str(product_ids).replace("[", "")
                product_ids = product_ids.replace("]", "")
                for product1 in product_ids:
                    if product_ids=='2': 
                        location_id=25 #FSH
                    elif product_ids=='3': 
                        location_id=26 #Ferric Sulphate
                    elif product_ids=='4': 
                        location_id=13  #TIO2
                    elif product_ids=='5': 
                        location_id=27  #Effluent 
                    elif product_ids=='6': 
                        location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material   
                    elif product_ids=='7':  
                        location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material      
                    elif product_ids=='9':  
                        location_id=13  #TIO2 
                    elif product_ids=='10745':  
                       location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material 
                    elif product_ids=='12906':  
                       location_id=24  #Other        
                    elif product_ids=='13030':  
                       location_id=24  #Other   
                        
                sql = ''' select pp.default_code, pp.name_template as name, pu.name uom, 
                (select sum(product_qty) from stock_move where product_id=pp.id and sale_line_id is null and date < '%(date_from)s'
                ) as opening_stock,
                ---------
                0 as opening_stock_value,
                --------
                (
                (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end ton_sl
                from mrp_production where product_id=%(product_id)s and 
                date_planned between '%(date_from)s' and '%(date_to)s') 
                +
                (select case when sum(sil.product_qty)!=0 then sum(sil.product_qty) else 0 end ton_sl from stock_inventory_line sil
                inner join stock_inventory si on sil.inventory_id=si.id
                inner join stock_production_lot spl on sil.prod_lot_id=spl.id
                where si.state='done' and sil.product_id=%(product_id)s and sil.product_qty>0 
                and sil.prod_lot_id is not null
                and si.date::date between '%(date_from)s' and '%(date_to)s')
                +
                (select case when sum(ail.quantity)!=0 then sum(ail.quantity) else 0 end quans from account_invoice_line ail
                 inner join account_invoice ai on ail.invoice_id=ai.id
                 where ai.state='cancel' 
                 and ail.product_id=pp.id
                 and ai.date_invoice  between '%(date_from)s' and '%(date_to)s')
                )as receipt_qty,
                 --------------
                0 as receipt_value,
                ---------
                (
                (select case when sum(ail.quantity)!=0 then sum(ail.quantity) else 0 end quans from account_invoice_line ail
                 inner join account_invoice ai on ail.invoice_id=ai.id
                 where ai.state!='cancel' 
                 and ail.product_id=pp.id
                 and ai.date_invoice  between '%(date_from)s' and '%(date_to)s') 
                 +
                 (select case when sum(sil.product_qty)!=0 then sum(sil.product_qty) else 0 end ton_sl from stock_inventory_line sil
                inner join stock_inventory si on sil.inventory_id=si.id
                inner join stock_production_lot spl on sil.prod_lot_id=spl.id
                where si.state='done' and sil.product_id=%(product_id)s and sil.product_qty>0 
                and sil.prod_lot_id is not null
                and si.date::date between '%(date_from)s' and '%(date_to)s')
                 )as consum_qty,
                ---------
                0 as consum_value,
                ----------------
                pp.id as product_id
                
                from product_product pp
                inner join product_template pt on  pp.product_tmpl_id=pt.id
                inner join product_uom pu on pt.uom_id=pu.id
                where pp.id in (%(product_id)s)
                order by pp.default_code
                '''%{'date_from':stock.date_from,
                    'date_to':stock.date_to,
                    'location_id':location_id,
                    #'location_dest_id':9,
                    'product_id':product_ids
                    }
                cr.execute(sql)
                res = cr.dictfetchall() 
                #print sql
                '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end ton_sl
                from mrp_production where product_id=4 and date_planned between '2016-01-01' and '2016-01-31'
                '''
            else:
                prod_obj = self.pool.get('product.product')
                prod_ids = prod_obj.search(cr, uid, [('cate_name', '=', 'finish')])
                for product_ids in prod_ids:
                    #product_ids = product_ids.id
                    if product_ids=='2': 
                        location_id=25 #FSH
                    elif product_ids=='3': 
                        location_id=26 #Ferric Sulphate
                    elif product_ids=='4': 
                        location_id=13  #TIO2
                    elif product_ids=='5': 
                        location_id=27  #Effluent 
                    elif product_ids=='6': 
                        location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material   
                    elif product_ids=='7':  
                        location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material      
                    elif product_ids=='9':  
                        location_id=13  #TIO2 
                    elif product_ids=='10745':  
                       location_id=23  #Physical Locations / VVTi Pigments / Production Line / Raw Material 
                    elif product_ids=='12906':  
                       location_id=24  #Other        
                    elif product_ids=='13030':  
                       location_id=24  #Other   
                    sql = ''' select pp.default_code, pp.name_template as name, pu.name uom, 
                    ---------------------
                    (select sum(product_qty) from stock_move where product_id=%(product_id)s and sale_line_id is null and date < '%(date_from)s'
                    ) as opening_stock,
                    ---------------------
                    0 as opening_stock_value,
                    -------------------
                   (
                    (select case when sum(product_qty)!=0 then sum(product_qty) else 0 end ton_sl
                    from mrp_production where product_id=%(product_id)s and 
                    date_planned between '%(date_from)s' and '%(date_to)s') 
                    +
                    (select case when sum(sil.product_qty)!=0 then sum(sil.product_qty) else 0 end ton_sl from stock_inventory_line sil
                    inner join stock_inventory si on sil.inventory_id=si.id
                    inner join stock_production_lot spl on sil.prod_lot_id=spl.id
                    where si.state='done' and sil.product_id=%(product_id)s and sil.product_qty>0 
                    and sil.prod_lot_id is not null
                    and si.date::date between '%(date_from)s' and '%(date_to)s')
                    +
                    (select case when sum(ail.quantity)!=0 then sum(ail.quantity) else 0 end quans from account_invoice_line ail
                     inner join account_invoice ai on ail.invoice_id=ai.id
                     where ai.state='cancel' 
                     and ail.product_id=pp.id
                     and ai.date_invoice  between '%(date_from)s' and '%(date_to)s')
                    )as receipt_qty,
                 --------------
                    0 as receipt_value,
                     --------------
                    0 as receipt_value,
                    ---------
                    (
                    (select case when sum(ail.quantity)!=0 then sum(ail.quantity) else 0 end quans from account_invoice_line ail
                     inner join account_invoice ai on ail.invoice_id=ai.id
                     where ai.state!='cancel' 
                     and ail.product_id=pp.id
                     and ai.date_invoice  between '%(date_from)s' and '%(date_to)s') 
                     +
                     (select case when sum(sil.product_qty)!=0 then sum(sil.product_qty) else 0 end ton_sl from stock_inventory_line sil
                    inner join stock_inventory si on sil.inventory_id=si.id
                    inner join stock_production_lot spl on sil.prod_lot_id=spl.id
                    where si.state='done' and sil.product_id=%(product_id)s and sil.product_qty>0 
                    and sil.prod_lot_id is not null
                    and si.date::date between '%(date_from)s' and '%(date_to)s')
                     )as consum_qty,
                    ----------------
                    pp.id as product_id
                    
                    from product_product pp
                    inner join product_template pt on  pp.product_tmpl_id=pt.id
                    inner join product_uom pu on pt.uom_id=pu.id
                    where pp.cate_name='finish' and pp.id=%(product_id)s
                    order by pp.default_code
                    '''%{'date_from':stock.date_from,
                        'date_to':stock.date_to,
                        'location_id':location_id,
                        'product_id':product_ids
                        }
                    cr.execute(sql)
                    res_in = cr.dictfetchall()
                    res1 = res1 + res_in
                res = res + res1
                
            for line in res:
                open_value = 0.0
                receipt_value = 0.0
                consum_value = 0.0
                close_value = 0.0
                close_stock = 0.0
                
                open_stock = 0
                receipt_qty = 0
                consum_qty =0
                open_stock = line['opening_stock'] or 0
                receipt_qty = line['receipt_qty'] or 0
                consum_qty = line['consum_qty'] or 0
                
                
                open_value = open_stock * finish_stock_value(line['product_id'], location_id)
                receipt_value = receipt_qty * finish_stock_value(line['product_id'], location_id)                
                consum_value = consum_qty * finish_stock_value(line['product_id'], location_id)
                
                move_analysis_line.append((0,0,{
                    'item_code': line['default_code'],
                    'item_name': line['name'],
                    'uom':line['uom'] or 0,
                    'open_stock': line['opening_stock'],
                    'open_value': open_value, #line['opening_stock'] or 0 * finish_stock_value(line['product_id'], location_id) or 0,
                    'receipt_qty':line['receipt_qty'],
                    'receipt_value':receipt_value, #line['receipt_qty'] or 0 * finish_stock_value(line['product_id'], location_id) or 0,
                    'consum_qty':line['consum_qty'],
                    'consum_value': consum_value, #line['consum_value'] or 0 , 
                    'close_stock':open_stock + receipt_qty - consum_qty or 0,
                    #'close_value':line['opening_stock_value']+line['receipt_value']-line['consum_value'],
                    'close_value': open_value + receipt_value - consum_value, # Modified by P.VINOTHKUMAR for calculate close_value on 01/04/2016@6:33PM
                    'product_id': line['product_id'] or False,                              
                })) 
        ###
            
            
#             move_analysis_line.append((0,0,{
#                 'item_code': line.default_code,
#                 'item_name': line.name,
#                 'uom':line.uom_id and line.uom_id.name or 0,
#                 'open_stock': get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id),
#                 'open_value': get_opening_stock_value(stock,line.id),
#                 'receipt_qty':get_qty(stock,line.id),
#                 'receipt_value':get_receipt_value(stock,line.id),
#                 'consum_qty':get_qty_out(stock,line.id) + get_qty_chuaro(stock,line.id),
#                 'consum_value': get_consumption_value(stock, line.id),    
# #                 'consum_value': good + product , 
#                 'close_stock':get_qty(stock,line.id) - (get_qty_out(stock,line.id) + get_qty_chuaro(stock,line.id)) + (get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)) ,
# #phuoc grn                'close_value': get_opening_stock_value(stock,line.id)+get_receipt_value(stock,line.id)-(get_qty(stock,line.id) and (get_receipt_value(stock,line.id)/get_qty(stock,line.id)*get_qty_out(stock,line.id)) or 0)
#                 'close_value': get_opening_stock_value(stock,line.id)+get_receipt_value(stock,line.id)-get_consumption_value(stock,line.id),   
#             
#             }))
        product_name = ''
        name_ids = [r.name for r in stock.product_ids]
        for name in name_ids:
            product_name += name + ', '
        vals = {
            'name': 'Stock Movement Analysis ',
#             'product_id': stock.product_id.id,
            'product_name': stock.product_ids and product_name or 'All' ,
#             'product_name': 'All' ,
            'product_name_title': 'Product: ',
            'date_from': stock.date_from,
            'date_to': stock.date_to,
            'date_from_title':'Date From: ',
            'date_to_title':'Date To: ',
            'categ_id': stock.categ_id.id,
            'categ_name': stock_obj.get_categ_name(cr, uid, ids,stock.categ_id.cate_name),
            'categ_name_title': 'Product Category: ',
            'movement_line':move_analysis_line,
        }
        stock_id = stock_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_tpt_form_movement_analysis')
        return {
                    'name': 'Stock Movement Analysis',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.form.movement.analysis',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': stock_id,
                }
        
stock_movement_analysis()


class product_product(osv.osv):
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_id'):
            if context.get('categ_id'):
                sql = '''
                     select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                        and product_product.product_tmpl_id = product_template.id;
                '''%(context.get('categ_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
product_product()
