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
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.form.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_xls', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
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
        'open_stock': fields.float('Opening Stock'),
        'open_value': fields.float('Opening Stock Value'),
        'receipt_qty': fields.float('Qty (Receipts)'),
        'receipt_value':fields.float('Stock Value (Receipts)'),
        'consum_qty': fields.float('Qty (Consumption)'),
        'consum_value':fields.float('Stock Value (Consumption)'),     
        'close_stock': fields.float('Closing Stock'),
        'close_value': fields.float('Closing Stock Value'),   
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
                                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s 
                                        
                                        and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
                                    )foo
                            '''%(line,locat_ids[0],date_from,date_to)
                cr.execute(sql)
                ton_arr = cr.fetchone()
                if ton_arr:
                    ton = ton_arr[0] or 0
                else:
                    ton = 0
                sql = '''
                       select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
                   '''%(line,date_from,date_to) 
                cr.execute(sql)
                for move in cr.dictfetchall():
                   if move['action_taken'] == 'need':
                       sql = '''
                           select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                       '''%(move['id'])
                       cr.execute(sql)
                       inspec_arr = cr.fetchone()
                       if inspec_arr:
                           inspec = inspec_arr and inspec_arr[0] or 0
                       else:
                           inspec = 0
                       ton = ton + inspec
                return ton
                           
            if categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                sql = '''
                                select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s 
                                        
                                        and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
                                    )foo
                            '''%(line,locat_ids[0],date_from,date_to)
                cr.execute(sql)
                ton_arr = cr.fetchone()
                if ton_arr:
                    ton = ton_arr[0] or 0
                else:
                    ton = 0
                sql = '''
                       select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
                   '''%(line,date_from,date_to) 
                cr.execute(sql)
                for move in cr.dictfetchall():
                   if move['action_taken'] == 'need':
                       sql = '''
                           select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                       '''%(move['id'])
                       cr.execute(sql)
                       inspec_arr = cr.fetchone()
                       if inspec_arr:
                           inspec = inspec_arr[0] or 0
                       else:
                           inspec = 0
                       ton = ton  + inspec
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
                            where st.state='done' and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
                        )foo
                '''%(locat_ids[0],product_id,date_from,date_to)
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
                            where st.state='done' and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
                        )foo
                '''%(locat_ids[0],product_id,date_from,date_to)
                cr.execute(sql)
                inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')
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
            return product_isu_qty and product_isu_qty['product_isu_qty'] or 0 

        def get_consumption_value(o, product_id):
            date_from = o.date_from
            date_to = o.date_to
            categ = o.categ_id.cate_name
            consum_value = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_id=%s and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')) 
                                or  (issue_id in (select id from tpt_material_issue where date between '%s' and '%s' and state in ('done')))
                                    )
                    '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,date_to,locat_ids[0])
                    cr.execute(sql)
                    product_isu_qty = cr.fetchone()[0]
                    consum_value = (product_isu_qty*avg_cost)
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
                sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_id=%s and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date between '%s' and '%s' and state = 'done')) 
                                or  (issue_id in (select id from tpt_material_issue where date between '%s' and '%s' and state in ('done')))
                                    )
                    '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,date_to,locat_ids[0])
                    cr.execute(sql)
                    product_isu_qty = cr.fetchone()[0]
                    consum_value = (product_isu_qty*avg_cost)
            return consum_value        
        
        def get_opening_stock(o,product_id):
            categ = o.categ_id.cate_name
            date_from = o.date_from
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id = %s  and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                                or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                    )
                        union all
                            select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_id=%s and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                                or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                    )
                        )foo
                    '''%(locat_ids[0],product_id,date_from,date_from,locat_ids[0],product_id,date_from,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                open_qty = (inventory and inventory['ton_sl'] or 0) - product_isu_qty
            if categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id = %s  and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                                or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                    )
                        union all
                            select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_id=%s and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                                or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                    )
                        )foo
                '''%(locat_ids[0],product_id,date_from,date_from,locat_ids[0],product_id,date_from,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                open_qty = (inventory and inventory['ton_sl'] or 0) - product_isu_qty
            return open_qty 
        
        def get_opening_stock_value(o, product_id):
            date_from = o.date_from
            categ = o.categ_id.cate_name
            opening_stock_value = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#                 sql = '''
#                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                         (select st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id = %s  and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or  (issue_id in (select id from tpt_material_issue where date_expec < '%s' and state in ('done')))
#                                     )
#                         union all
#                             select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or  (issue_id in (select id from tpt_material_issue where date_expec < '%s' and state in ('done')))
#                                     )
#                         )foo
#                     '''%(locat_ids[0],product_id,date_from,date_from,date_from,locat_ids[0],product_id,date_from,date_from,date_from)
#                 cr.execute(sql)
#                 inventory = cr.dictfetchone()
#phuoc
#                 sql = '''
#                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                           (select st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id=%s and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or  (issue_id in (select id from tpt_material_issue where date_expec < '%s' and state in ('done')))
#                                     )
#                         )foo
#                     '''%(locat_ids[0],product_id,date_from,date_from,date_from)
#phuoc
                sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                                or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                    )
                    '''%(locat_ids[0],product_id,date_from,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                            from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
                    '''%(date_from,locat_ids[0],product_id)
                    cr.execute(sql)
                    product_isu_qty = cr.fetchone()[0]
                    opening_stock_value = total_cost-(product_isu_qty*avg_cost)
            if categ =='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])            
                sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s
                                and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
                                or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
                                    )
                    '''%(locat_ids[0],product_id,date_from,date_from)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                            from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
                    '''%(date_from,locat_ids[0],product_id)
                    cr.execute(sql)
                    product_isu_qty = cr.fetchone()[0]
                    opening_stock_value = total_cost-(product_isu_qty*avg_cost)
            return opening_stock_value    
        
        def get_closing_stock(o, receipt,consum,opening):
            total_cost = 0
            total_cost = receipt - consum + opening
            return total_cost  
            
        stock_obj = self.pool.get('tpt.form.movement.analysis')
        cr.execute('delete from tpt_form_movement_analysis')
        stock = self.browse(cr, uid, ids[0])
        move_analysis_line = []
        for line in get_categ(stock):
            move_analysis_line.append((0,0,{
                'item_code': line.default_code,
                'item_name': line.name,
                'uom':line.uom_id and line.uom_id.name or 0,
                'open_stock': get_opening_stock(stock,line.id),
                'open_value': get_opening_stock_value(stock,line.id),
                'receipt_qty':get_qty(stock,line.id),
                'receipt_value':get_receipt_value(stock,line.id),
                'consum_qty':get_qty_out(stock,line.id),
                'consum_value':get_consumption_value(stock,line.id),     
                'close_stock':get_closing_stock(stock,get_qty(stock,line.id),get_qty_out(stock,line.id),get_opening_stock(stock,line.id)) ,
                'close_value':get_closing_stock(stock,get_receipt_value(stock,line.id),get_consumption_value(stock,line.id),get_opening_stock_value(stock,line.id)) ,   

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

