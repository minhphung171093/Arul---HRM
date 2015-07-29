# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import date
from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"



class tpt_stock_inward_outward(osv.osv):
    _name = "tpt.stock.inward.outward"
    _columns = {
        'name': fields.char('', readonly=True),
        'product_id': fields.many2one('product.product', 'Material'),
        'product_uom': fields.many2one('product.uom', 'UOM'),
        'product_name': fields.char('Product Name: '),
        'product_code': fields.char('Product Code: '),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
        'stock_in_out_line': fields.one2many('tpt.stock.inward.outward.line','stock_in_out_id','Line'),
        'opening_stock': fields.float('Opening Stock',digits=(16,3)),
        'closing_stock': fields.float('Closing Stock',digits=(16,3)),
        'opening_value': fields.float('Opening Value',digits=(16,3)),
        'closing_value': fields.float('Closing Value',digits=(16,3)),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         for line in self.browse(cr, uid, ids, context=context):
#             context.update({'active_ids': [line.id]})
        datas = {'ids': ids}
        datas['model'] = 'tpt.stock.inward.outward'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_inward_outward_xls', 'datas': datas}
#     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         for line in self.browse(cr, uid, ids, context=context):
#             context.update({'active_ids': [line.id]})
        datas = {'ids': ids}
        datas['model'] = 'tpt.stock.inward.outward'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_inward_outward_pdf', 'datas': datas}
    
tpt_stock_inward_outward()

class tpt_stock_inward_outward_line(osv.osv):
    _name = "tpt.stock.inward.outward.line"
    _columns = {
        'creation_date': fields.date('Creation Date'),
        'stock_in_out_id': fields.many2one('tpt.stock.inward.outward', 'Stock inward outward',ondelete='cascade'),
        'posting_date': fields.date('Posting Date'),
        'document_no': fields.char('Document No', size=1024),
        'gl_document_no': fields.char('GL Document No', size=1024),
        'document_type': fields.char('Document Type', size=1024),
        'transaction_quantity': fields.float('Transaction Quantity',digits=(16,3)),
        'stock_value': fields.float('Stock Value',digits=(16,3)),
        'current_material_value': fields.float('Current Material Value',digits=(16,3)),
        'price_unit': fields.float('Price Unit',digits=(16,3)),
#         'sl_chuaro': fields.float('SL Chua Ro'),
    }
    
tpt_stock_inward_outward_line()

class stock_inward_outward_report(osv.osv_memory):
    _name = "stock.inward.outward.report"
    _columns = {    
                'product_id': fields.many2one('product.product', 'Material', required=True),
                'date_from':fields.date('Date From', required=True),
                'date_to':fields.date('Date To', required=True),
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
    
    def print_report(self, cr, uid, ids, context=None):
        stock_obj = self.pool.get('tpt.stock.inward.outward')
        cr.execute('delete from tpt_stock_inward_outward')
        stock = self.browse(cr, uid, ids[0])
        self.current = 0
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
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
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
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
                '''%(product_id.id, date_from)
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
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
                '''%(product_id.id, date_from)
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
           date_from = o.date_from
           date_to = o.date_to
           product_id = o.product_id
           categ = product_id.categ_id.cate_name
           opening_stock_value = 0
           freight_cost = 0
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
#                sql = '''
#                    select product_qty, date
#                     from stock_move where product_id = 10718 and state = 'done' and issue_id is null 
#                     and picking_id is null and inspec_id is null and location_id = 15 
#                     and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '2015-04-01' and '2015-04-30' 
#                     and location_id != location_dest_id
#                '''
               opening_stock_value = total_cost-(product_isu_qty)+freight_cost
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
               opening_stock_value = total_cost-(product_isu_qty)+freight_cost
           return opening_stock_value
        
        def get_detail_lines(o):
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
            parent_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
            parent_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
            sql = '''
                select * from account_move where doc_type in ('freight', 'good', 'grn', 'product') 
                    and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where to_char(date_invoice, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                        or (LEFT(name,17) in (select name from stock_picking where id in (select picking_id from stock_move where to_char(date, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and product_id=%(product_id)s)))
                    ) or material_issue_id in (select id from tpt_material_issue where date_expec between '%(date_from)s' and '%(date_to)s' and warehouse in (%(location_row_id)s,%(location_spare_id)s) and id in (select material_issue_id from tpt_material_issue_line where product_id=%(product_id)s)) 
                        )
                        or product_dec in (select id from mrp_production where date_planned between '%(date_from)s' and '%(date_to)s' and id in (select production_id from mrp_production_move_ids where move_id in (select id from stock_move where product_id = %(product_id)s and location_id in (%(location_row_id)s,%(location_spare_id)s) ))
                         )
                         order by date,doc_type = 'grn' desc, id
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
                        where  picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s) and product_id = %s)
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
                   select name from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s) 
                '''%(move_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['name']
            return name
        
        def get_transaction_qty(o, move_id, material_issue_id, product_dec, move_type):
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
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
                        where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
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
                if move_type == 'freight':
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
                        where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
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
           date_from = o.date_from
           date_to = o.date_to
           product_id = o.product_id
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
                       select * from stock_move where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s))
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
                       select * from stock_move where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s))
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
#                 if len(get_detail_lines) <= 1:
                if self.id2 != line['id']:
                    self.num_call_grn = {'grn_name':'','num':-1}
                    self.id2 = line['id']
                qty = get_transaction_qty(o,line['id'], line['material_issue_id'], line['product_dec'],line['doc_type'])
                if line['doc_type']=='freight':
                    qty=1
                value = get_line_stock_value(o,line['id'], line['material_issue_id'], line['doc_type'], line['date'])
                closing += qty * value
            return closing
        
#         def closing_value(o,get_detail_lines):
#             return self.sum_stock
        
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
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
            categ = product_id.categ_id.cate_name
            parent_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
            parent_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
#             sql = '''
#                 select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move 
#                 where location_dest_id in (%s, %s) and id in (select move_id from stock_inventory_move_rel) and to_char(date, 'YYYY-MM-DD') between '%s' and '%s' and product_id = %s
#             '''%(locat_ids_raw[0], locat_ids_spares[0], date_from, date_to, product_id.id)
#             cr.execute(sql)
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
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
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
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
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
            else:
                cur = st_value+self.current
            self.current = cur
            stock_in_out_line.append((0,0,{
                'creation_date': line['date'],
                'posting_date': line['date'],
                'document_no': get_account_move_line(line['id'], line['material_issue_id'], line['product_dec'], line['doc_type']),
                'gl_document_no': line['name'],
                'document_type': get_doc_type(line['doc_type']),
                'transaction_quantity': trans_qty,
                'price_unit': price,
                'stock_value': st_value,
                'current_material_value':cur,
#                 'sl_chuaro': sl_chuaro,
            }))
            
        vals = {
            'name': 'Stock Inward and Outward Details',
            'product_id': stock.product_id.id,
            'product_uom': stock.product_id.uom_id.id,
            'product_name': stock.product_id.name,
            'product_code': stock.product_id.code,
            'date_from':stock.date_from,
            'date_to':stock.date_to,
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
    
stock_inward_outward_report()

class product_product(osv.osv):
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_inward_outward'):
            sql = '''
                 select product_product.id 
                    from product_product,product_template 
                    where product_template.categ_id in(select id from product_category where cate_name in ('raw','spares'))
                    and product_product.product_tmpl_id = product_template.id
            '''
            cr.execute(sql)
            product_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
product_product()

