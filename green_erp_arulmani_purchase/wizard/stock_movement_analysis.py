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
                }
    

tpt_movement_analysis_line()

class stock_movement_analysis(osv.osv_memory):
    _name = "stock.movement.analysis"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Product Category',required = True),
                'product_id': fields.many2one('product.product', 'Product'),
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
            product = o.product_id.id
            pro_obj = self.pool.get('product.product')
            categ_ids = []
    
            if categ and product:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                            and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
                '''%(categ,product)
                cr.execute(sql)
                categ_ids += [r[0] for r in cr.fetchall()]
                return self.pool.get('product.product').browse(cr,uid,categ_ids)
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
                return ton
                           
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
                return ton
            
        def get_receipt_value(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            hand_quantity = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
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
                            '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
                cr.execute(sql)
                inventory = cr.dictfetchone()
            if categ and categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
                sql = '''
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
                            '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
                cr.execute(sql)
                inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
               '''%(product_id,date_from,date_to) 
            cr.execute(sql)
            for line in cr.dictfetchall():
               if line['action_taken'] == 'need':
                   sql = '''
                       select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                   '''%(line['id'])
                   cr.execute(sql)
                   inspec = cr.dictfetchone()
                   if inspec:
                       hand_quantity += inspec['qty_approve'] or 0
                       total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
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
                    '''%(locat_ids[0],product_id,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
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
            if categ =='spares':
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
                    '''%(locat_ids[0],product_id,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
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
                select * from account_move where doc_type in ('good', 'grn', 'product') 
                    and date between '%(date_from)s' and '%(date_to)s'
                    and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where to_char(date_invoice, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                        or (LEFT(name,17) in (select name from stock_picking where id in (select picking_id from stock_move where to_char(date, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and product_id=%(product_id)s)))
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
                   select name from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s) 
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
                        where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
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
                        where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
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
           
            
        stock_obj = self.pool.get('tpt.form.movement.analysis')
        cr.execute('delete from tpt_form_movement_analysis')
        stock = self.browse(cr, uid, ids[0])
        move_analysis_line = []
        for line in get_categ(stock):
            stock_in_out_line = []
            good = 0
            current = 0
            product = 0
            for seq, phuoc in enumerate(get_detail_lines(stock, line)):
                trans_qty = get_transaction_qty(stock,phuoc['id'], phuoc['material_issue_id'], phuoc['product_dec'], phuoc['doc_type'], line)
                if phuoc['doc_type']=='good':
                    qty = 0
                    value = 0
                    opening_stock = get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)
                    opening_stock_value = get_opening_stock_value(stock,line.id)
                    for l in stock_in_out_line:
                        qty += l[2]['transaction_quantity'] 
                        value += l[2]['stock_value']
                    if seq == 0:
                        st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
                    else:
                        st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
                    st_value = (st)*(trans_qty)
                    good += (-st_value)
                elif phuoc['doc_type']=='product':
                    qty = 0
                    value = 0
                    opening_stock = get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)
                    opening_stock_value = get_opening_stock_value(stock,line.id)
                    for l in stock_in_out_line:
                        qty += l[2]['transaction_quantity'] 
                        value += l[2]['stock_value']
                    if seq == 0:
                        st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
                    else:
                        st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
                    st_value = (st)*(trans_qty)
                    product += (-st_value)
                else:
                    st_value = stock_value(line, phuoc['id'], phuoc['doc_type'])
                self.st_sum_value += st_value
                if seq == 0:
                    cur = get_opening_stock_value(stock,line.id)+st_value+current
                else:
                    cur = st_value+current
                current = cur
                stock_in_out_line.append((0,0,{
                    'transaction_quantity': trans_qty,
                    'stock_value': st_value,
                    'current_material_value':cur,
                }))
            
            
            
            move_analysis_line.append((0,0,{
                'item_code': line.default_code,
                'item_name': line.name,
                'uom':line.uom_id and line.uom_id.name or 0,
                'open_stock': get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id),
                'open_value': get_opening_stock_value(stock,line.id),
                'receipt_qty':get_qty(stock,line.id),
                'receipt_value':get_receipt_value(stock,line.id),
                'consum_qty':get_qty_out(stock,line.id) + get_qty_chuaro(stock,line.id),
#phuoc grn                'consum_value': (get_qty(stock,line.id)*get_qty_out(stock,line.id)) and (get_receipt_value(stock,line.id)/get_qty(stock,line.id)*get_qty_out(stock,line.id)) or 0,
#                 'consum_value':(get_opening_stock(stock,line.id)+get_qty(stock,line.id)) and ((get_receipt_value(stock,line.id)+get_opening_stock_value(stock,line.id))/(get_opening_stock(stock,line.id)+get_qty(stock,line.id))*get_qty_out(stock,line.id)) or 0 ,    
                'consum_value': good + product , 
                'close_stock':get_qty(stock,line.id) - (get_qty_out(stock,line.id) + get_qty_chuaro(stock,line.id)) + (get_opening_stock(stock,line.id)-get_qty_opening_chuaro(stock, line.id)) ,
#phuoc grn                'close_value': get_opening_stock_value(stock,line.id)+get_receipt_value(stock,line.id)-(get_qty(stock,line.id) and (get_receipt_value(stock,line.id)/get_qty(stock,line.id)*get_qty_out(stock,line.id)) or 0)
                'close_value': get_opening_stock_value(stock,line.id)+get_receipt_value(stock,line.id)-(good)-product,   
            
            }))
        vals = {
            'name': 'Stock Movement Analysis ',
            'product_id': stock.product_id.id,
            'product_name': stock.product_id and stock.product_id.name or 'All' ,
            'product_name_title': 'Product: ',
            'date_from': stock.date_from,
            'date_to': stock.date_to,
            'date_from_title':'Date From: ',
            'date_to_title':'To: ',
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
