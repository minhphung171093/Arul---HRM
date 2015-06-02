# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


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
        'opening_stock': fields.float('Opening Stock'),
        'closing_stock': fields.float('Closing Stock'),
        'opening_value': fields.float('Opening Value'),
        'closing_value': fields.float('Closing Value'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.stock.inward.outward'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_inward_outward_xls', 'datas': datas}
#     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
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
        'transaction_quantity': fields.float('Transaction Quantity'),
        'stock_value': fields.float('Stock Value'),
        'current_material_value': fields.float('Current Material Value'),
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
        stock_in_out_line = []
        def get_opening_stock(o):
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move  
                where product_id = %s and picking_id in (select id from stock_picking where date < '%s' and state = 'done' and type = 'in')
            '''%(product_id.id, date_from)
            cr.execute(sql)
            product_qty = cr.dictfetchone()['product_qty']
             
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
            '''%(product_id.id, date_from)
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()['product_isu_qty']
            opening_stock = product_qty-product_isu_qty
            return opening_stock
        
        def get_closing_stock(o):
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move  
                where product_id = %s and picking_id in (select id from stock_picking where date <= '%s' and state = 'done' and type = 'in')
            '''%(product_id.id, date_to)
            cr.execute(sql)
            product_qty = cr.dictfetchone()['product_qty']
             
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec <= '%s' and state = 'done')
            '''%(product_id.id, date_to)
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()['product_isu_qty']
            closing_stock = product_qty-product_isu_qty
            return closing_stock
        
        def get_opening_stock_value(o):
           date_from = o.date_from
           date_to = o.date_to
           product_id = o.product_id
           opening_stock_value = 0
           sql = '''
               select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                   (select st.product_qty,st.price_unit*st.product_qty as price_unit
                       from stock_move st
                           join stock_location loc1 on st.location_id=loc1.id
                           join stock_location loc2 on st.location_dest_id=loc2.id
                       where st.state='done' and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and date<'%s'
                   union all
                       select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                       from stock_move st
                           join stock_location loc1 on st.location_id=loc1.id
                           join stock_location loc2 on st.location_dest_id=loc2.id
                       where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and date<'%s'
                   )foo
           '''%(product_id.id,date_from,product_id.id,date_from)
           cr.execute(sql)
           inventory = cr.dictfetchone()
           if inventory:
               hand_quantity = float(inventory['ton_sl'])
               total_cost = float(inventory['total_cost'])
               avg_cost = hand_quantity and total_cost/hand_quantity or 0
               sql = '''
                   select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                       from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and state='done') and product_id=%s
               '''%(date_from,product_id.id)
               cr.execute(sql)
               product_isu_qty = cr.fetchone()[0]
               opening_stock_value = total_cost-(product_isu_qty*avg_cost)
           return opening_stock_value
        
        def get_detail_lines(o):
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
            sql = '''
                select * from account_move where doc_type in ('freight', 'good', 'grn') and state = 'posted' and date between '%(date_from)s' and '%(date_to)s'
                    and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                        or (name in (select name from stock_picking where id in (select picking_id from stock_move where product_id=%(product_id)s)))
                    ) or material_issue_id in (select id from tpt_material_issue where id in (select material_issue_id from tpt_material_issue_line where product_id=%(product_id)s)) 
                        ) order by date
            '''%{'date_from':date_from,
                 'date_to':date_to,
                 'product_id':product_id.id}
            cr.execute(sql)
            return cr.dictfetchall()
        
        def get_transaction_qty(o, move_id, material_issue_id, move_type):
            date_from = o.date_from
            date_to = o.date_to
            product_id = o.product_id
            if move_type == 'freight':
                sql = '''
                    select case when sum(quantity)!=0 then sum(quantity) else 0 end quantity, product_id from account_invoice_line
                    where invoice_id in (select id from account_invoice where move_id = %s) and product_id = %s
                    group by product_id 
                '''%(move_id, product_id.id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    quantity = qty['quantity']
            if move_type == 'good':
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                    where material_issue_id in (select id from tpt_material_issue where id = %s) and product_id = %s
                    group by product_id 
                '''%(material_issue_id, product_id.id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    quantity = qty['product_isu_qty']
            if move_type == 'grn':
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty, product_id from stock_move
                    where picking_id in (select id from stock_picking where name in (select name from account_move_line where move_id = %s) and product_id = %s)
                    group by product_id 
                '''%(move_id, product_id.id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    quantity = qty['product_qty']
            return quantity
        
        def get_line_stock_value(o, move_id, material_issue_id, move_type):
           date_from = o.date_from
           date_to = o.date_to
           product_id = o.product_id
           opening_stock_value = 0
           if move_type == 'freight':
               sql = '''
                   select warehouse from stock_picking where id in (select grn_no from account_invoice where id in (select sup_inv_id from account_invoice where move_id = %s)) and warehouse is not null
               '''%(move_id)
               cr.execute(sql)
               location = cr.dictfetchone()['warehouse'] 
               sql = '''
                   select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                       (select st.product_qty,st.price_unit*st.product_qty as price_unit
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                           and st.location_dest_id = %s and date between '%s' and '%s'
                       union all
                           select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                           and st.location_id = %s and date between '%s' and '%s'
                       )foo
               '''%(product_id.id, location, date_from, date_to ,product_id.id, location, date_from, date_to)
               cr.execute(sql)
               inventory = cr.dictfetchone()
               if inventory:
                   hand_quantity = float(inventory['ton_sl'])
                   total_cost = float(inventory['total_cost'])
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
           
           if move_type == 'grn':
               sql = '''
                   select warehouse from stock_picking where name in (select name from account_move_line where move_id = %s) and warehouse is not null
               '''%(move_id)
               cr.execute(sql)
               location = cr.dictfetchone()['warehouse'] 
               sql = '''
                   select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                       (select st.product_qty,st.price_unit*st.product_qty as price_unit
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                           and st.location_dest_id = %s and date between '%s' and '%s'
                       union all
                           select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                           and st.location_id = %s and date between '%s' and '%s'
                       )foo
               '''%(product_id.id, location, date_from, date_to ,product_id.id, location, date_from, date_to)
               cr.execute(sql)
               inventory = cr.dictfetchone()
               if inventory:
                   hand_quantity = float(inventory['ton_sl'])
                   total_cost = float(inventory['total_cost'])
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
           
           if move_type == 'good':
               sql = '''
                   select warehouse from tpt_material_issue where id in (select material_issue_id from account_move where material_issue_id = %s) and warehouse is not null
               '''%(material_issue_id)
               cr.execute(sql)
               location = cr.dictfetchone()['warehouse'] 
               sql = '''
                   select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                       (select st.product_qty,st.price_unit*st.product_qty as price_unit
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                           and st.location_dest_id = %s and date between '%s' and '%s'
                       union all
                           select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                           from stock_move st
                               join stock_location loc1 on st.location_id=loc1.id
                               join stock_location loc2 on st.location_dest_id=loc2.id
                           where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                           and st.location_id = %s and date between '%s' and '%s'
                       )foo
               '''%(product_id.id, location, date_from, date_to ,product_id.id, location, date_from, date_to)
               cr.execute(sql)
               inventory = cr.dictfetchone()
               if inventory:
                   hand_quantity = float(inventory['ton_sl'])
                   total_cost = float(inventory['total_cost'])
                   avg_cost = hand_quantity and total_cost/hand_quantity or 0 
               return avg_cost
        
        def closing_value(o,get_detail_lines):
            closing = 0
            for line in get_detail_lines:
                qty = get_transaction_qty(o,line['id'], line['material_issue_id'], line['doc_type'])
                value = get_line_stock_value(o,line['id'], line['material_issue_id'], line['doc_type'])
                closing += qty * value
            return closing
        
        def get_account_move_line(move_id):
            move = self.pool.get('account.move').browse(cr,uid,move_id)
            move_line = move.line_id[0]
            return move_line and move_line.name or ''
        
        def get_doc_type(doc_type):
            if doc_type == 'freight':
                return 'Freight Invoice'
            if doc_type == 'good':
                return 'Good Issue'
            if doc_type == 'grn':
                return 'GRN'
        
        def stock_value(qty, value):
            return qty*value
        
        self.current = 0
        def get_line_current_material(o,stock_value):  
            cur = get_opening_stock_value(o)+stock_value+self.current
            self.current = cur
            return cur
        
        for line in get_detail_lines(stock):
            stock_in_out_line.append((0,0,{
                'creation_date': line['date'],
                'posting_date': line['date'],
                'document_no': get_account_move_line(line['id']),
                'gl_document_no': line['name'],
                'document_type': get_doc_type(line['doc_type']),
                'transaction_quantity': get_transaction_qty(stock,line['id'], line['material_issue_id'], line['doc_type']),
                'stock_value': stock_value(get_transaction_qty(stock,line['id'], line['material_issue_id'], line['doc_type']),get_line_stock_value(stock,line['id'], line['material_issue_id'], line['doc_type'])),
                'current_material_value':get_line_current_material(stock,stock_value(get_transaction_qty(stock,line['id'], line['material_issue_id'], line['doc_type']),get_line_stock_value(stock,line['id'], line['material_issue_id'], line['doc_type']))),
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
            'opening_stock': get_opening_stock(stock),
            'closing_stock': get_closing_stock(stock),
            'opening_value': get_opening_stock_value(stock),
            'closing_value': closing_value(stock,get_detail_lines(stock)),
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

