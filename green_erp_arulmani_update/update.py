# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
from datetime import date
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class tpt_update_stock_move_report(osv.osv):
    _name = "tpt.update.stock.move.report"
    
#     def init(self, cr):
#         sql = '''
#             select id from tpt_material_issue where state = 'done' and id not in (select issue_id from stock_move where issue_id is not null )
#         '''
#         cr.execute(sql)
#         for ma in cr.fetchall():
#             issue = self.pool.get('tpt.material.issue').browse(cr, 1, ma[0])
#             location_id = False
#             dest_id = False
#             for iss_line in issue.material_issue_line:
#                 if issue.request_type == 'production':
#                     location_id = issue.warehouse and issue.warehouse.id or False
#                     dest_id = issue.dest_warehouse_id and issue.dest_warehouse_id.id or False
#                 else:
#                     location_id = issue.warehouse and issue.warehouse.id or False
#                     location_ids=self.pool.get('stock.location').search(cr, 1,[('name','=','Scrapped')])
#                     if location_ids:
#                         dest_id = location_ids[0]
#                 sql = '''
#                     select id from stock_move where name = '/' and state = 'done' and location_id = %s and location_dest_id = %s 
#                         and issue_id is NULL and inspec_id is NULL and picking_id is NULL and product_id = %s and product_uom = %s
#                         and product_qty = %s
#                 '''%(location_id,dest_id,iss_line.product_id.id,iss_line.uom_po_id.id,iss_line.product_isu_qty)
#                 cr.execute(sql)
#                 move_ids = cr.fetchone()
#                 if move_ids:
#                     sql = ''' 
#                         update stock_move set issue_id = %s where id = %s
#                     '''%(issue.id,move_ids[0])
#                     cr.execute(sql)
#                     print 'TPT update ISSUE for report', move_ids[0]
#         sql = '''
#             select id from tpt_quanlity_inspection where state in ('done','remaining') and id not in (select inspec_id from stock_move where inspec_id is not null )
#         '''
#         cr.execute(sql)
#         for master in cr.fetchall():
#             inspec = self.pool.get('tpt.quanlity.inspection').browse(cr, 1, master[0])
#             location_id = False
#             loca_id = False
#             dest_1_id = False
#             dest_2_id = False
#             locat_obj = self.pool.get('stock.location')
#             cate = inspec.product_id.categ_id and inspec.product_id.categ_id.cate_name or False
#             parent_sou_ids = locat_obj.search(cr, 1, [('name','=','Quality Inspection'),('usage','=','view')])
#             if parent_sou_ids:
#                 loca_id = locat_obj.search(cr, 1, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_sou_ids[0])])
#                 if loca_id:
#                     location_id = loca_id[0]
#             parent_dest_1_ids = locat_obj.search(cr, 1, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
#             if parent_dest_1_ids:
#                 location_dest_1_ids = locat_obj.search(cr, 1, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_dest_1_ids[0])])
#                 if location_dest_1_ids:
#                     dest_1_id = location_dest_1_ids[0]
#             if cate == 'raw':
#                 parent_dest_2_ids = self.pool.get('stock.location').search(cr, 1, [('name','=','Store'),('usage','=','view')])
#                 if parent_dest_2_ids:
#                     location_dest_2_ids = self.pool.get('stock.location').search(cr, 1, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_dest_2_ids[0])])
#                 if location_dest_2_ids:
#                     dest_2_id = location_dest_2_ids[0]
#             if cate == 'spares':
#                 parent_dest_2_ids = self.pool.get('stock.location').search(cr, 1, [('name','=','Store'),('usage','=','view')])
#                 if parent_dest_2_ids:
#                     location_dest_2_ids = locat_obj.search(cr, 1, [('name','in',['Spares','Spare','spares','spare']),('location_id','=',parent_dest_2_ids[0])])
#                 if location_dest_2_ids:
#                     dest_2_id = location_dest_2_ids[0]
#             sql = '''
#                 select id from stock_move where name = '/' and state = 'done' and location_id = %s and location_dest_id in (%s,%s) 
#                     and issue_id is NULL and inspec_id is NULL and picking_id is NULL and product_id = %s 
#                     and product_id in (select pp.id from product_product pp,product_template pt,product_category cat 
#                         where pp.product_tmpl_id = pt.id and pt.categ_id = cat.id and cat.cate_name = '%s')
#             '''%(location_id,dest_1_id,dest_2_id,inspec.product_id.id,cate)
#             cr.execute(sql)
#             move_ids = cr.fetchall()
#             if move_ids:
#                 cr.execute("UPDATE stock_move SET inspec_id= %s WHERE id in %s",(inspec.id,tuple(move_ids),))
#                 print 'TPT update INSPEC for report', tuple(move_ids)
                 
#     def init(self, cr):
#         sql = '''
#             select id from stock_move where issue_id is not null and state = 'done' and price_unit is null and picking_id is null and inspec_id is null
#         '''
#         cr.execute(sql)
#         for line in cr.fetchall():
#             move = self.pool.get('stock.move').browse(cr, 1, line[0])
#             sql = '''
#                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                         (select st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id = %s  and st.product_id=%s and date < '%s' 
#                         union all
#                             select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s and date < '%s' 
#                         )foo
#                 '''%(move.location_id.id,move.product_id.id,move.issue_id.date_expec,move.location_id.id,move.product_id.id,move.issue_id.date_expec)
#             cr.execute(sql)
#             inventory = cr.dictfetchone()
#             if inventory:
#                 hand_quantity = float(inventory['ton_sl'])
#                 total_cost = float(inventory['total_cost'])
#                 avg_cost = hand_quantity and total_cost/hand_quantity or 0
#                 sql = '''
#                     update stock_move set price_unit = %s where id = %s
#                 '''%(avg_cost,move.id)
#                 cr.execute(sql)
#                 print 'TPT update ISSUE unit price for report', move.id
#         
#         sql = '''
#             select id from stock_move where inspec_id is not null and state = 'done' and price_unit is null and picking_id is null and issue_id is null
#         '''
#         cr.execute(sql)
#         for line1 in cr.fetchall():
#             move = self.pool.get('stock.move').browse(cr, 1, line1[0])
#             price = move.inspec_id and move.inspec_id.need_inspec_id and move.inspec_id.need_inspec_id.price_unit or 0
#             sql = '''
#                update stock_move set price_unit = %s where id = %s
#             '''%(price,move.id)
#             cr.execute(sql)
#             print 'TPT update INSPEC unit price for report', move.id
    
    _columns = {
        'result': fields.text('Result', readonly=True ),
        'product_id': fields.many2one('product.product', 'Product'),
        'update_line': fields.one2many('tpt.update.inspection.line','update_id','Line'),
    }
    
    def map_issue(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and id not in (select issue_id from stock_move where issue_id is not null )
        '''
        cr.execute(sql)
        for ma in cr.fetchall():
            issue = self.pool.get('tpt.material.issue').browse(cr, 1, ma[0])
            location_id = False
            dest_id = False
            for iss_line in issue.material_issue_line:
                if issue.request_type == 'production':
                    location_id = issue.warehouse and issue.warehouse.id or False
                    dest_id = issue.dest_warehouse_id and issue.dest_warehouse_id.id or False
                else:
                    location_id = issue.warehouse and issue.warehouse.id or False
                    location_ids=self.pool.get('stock.location').search(cr, 1,[('name','=','Scrapped')])
                    if location_ids:
                        dest_id = location_ids[0]
                sql = '''
                    select id from stock_move where name = '/' and state = 'done' and location_id = %s and location_dest_id = %s 
                        and issue_id is NULL and inspec_id is NULL and picking_id is NULL and product_id = %s and product_uom = %s
                        and product_qty = %s
                '''%(location_id,dest_id,iss_line.product_id.id,iss_line.uom_po_id.id,iss_line.product_isu_qty)
                cr.execute(sql)
                move_ids = cr.fetchone()
                if move_ids:
                    sql = ''' 
                        update stock_move set issue_id = %s where id = %s
                    '''%(issue.id,move_ids[0])
                    cr.execute(sql)
                    print 'TPT update ISSUE for report', move_ids[0]
        return self.write(cr, uid, ids, {'result':'TPT update ISSUE for report Done'})
    
    def map_inspec(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_quanlity_inspection where state in ('done','remaining') and id not in (select inspec_id from stock_move where inspec_id is not null )
        '''
        cr.execute(sql)
        for master in cr.fetchall():
            inspec = self.pool.get('tpt.quanlity.inspection').browse(cr, 1, master[0])
            location_id = False
            loca_id = False
            dest_1_id = False
            dest_2_id = False
            locat_obj = self.pool.get('stock.location')
            cate = inspec.product_id.categ_id and inspec.product_id.categ_id.cate_name or False
            parent_sou_ids = locat_obj.search(cr, 1, [('name','=','Quality Inspection'),('usage','=','view')])
            if parent_sou_ids:
                loca_id = locat_obj.search(cr, 1, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_sou_ids[0])])
                if loca_id:
                    location_id = loca_id[0]
            parent_dest_1_ids = locat_obj.search(cr, 1, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
            if parent_dest_1_ids:
                location_dest_1_ids = locat_obj.search(cr, 1, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_dest_1_ids[0])])
                if location_dest_1_ids:
                    dest_1_id = location_dest_1_ids[0]
            if cate == 'raw':
                parent_dest_2_ids = self.pool.get('stock.location').search(cr, 1, [('name','=','Store'),('usage','=','view')])
                if parent_dest_2_ids:
                    location_dest_2_ids = self.pool.get('stock.location').search(cr, 1, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_dest_2_ids[0])])
                if location_dest_2_ids:
                    dest_2_id = location_dest_2_ids[0]
            if cate == 'spares':
                parent_dest_2_ids = self.pool.get('stock.location').search(cr, 1, [('name','=','Store'),('usage','=','view')])
                if parent_dest_2_ids:
                    location_dest_2_ids = locat_obj.search(cr, 1, [('name','in',['Spares','Spare','spares','spare']),('location_id','=',parent_dest_2_ids[0])])
                if location_dest_2_ids:
                    dest_2_id = location_dest_2_ids[0]
            if inspec.remaining_qty and inspec.remaining_qty==inspec.qty:
                sql = '''
                    select id from stock_move where name = '/' and state = 'done' and location_id = %s and location_dest_id in (%s,%s) 
                        and issue_id is NULL and inspec_id is NULL and picking_id is NULL and product_id = %s 
                        and product_id in (select pp.id from product_product pp,product_template pt,product_category cat 
                            where pp.product_tmpl_id = pt.id and pt.categ_id = cat.id and cat.cate_name = '%s') and product_qty = %s
                '''%(location_id,dest_1_id,dest_2_id,inspec.product_id.id,cate,inspec.qty)
            else:
                sql = '''
                    select id from stock_move where name = '/' and state = 'done' and location_id = %s and location_dest_id in (%s,%s) 
                        and issue_id is NULL and inspec_id is NULL and picking_id is NULL and product_id = %s 
                        and product_id in (select pp.id from product_product pp,product_template pt,product_category cat 
                            where pp.product_tmpl_id = pt.id and pt.categ_id = cat.id and cat.cate_name = '%s') and product_qty <= %s
                '''%(location_id,dest_1_id,dest_2_id,inspec.product_id.id,cate,inspec.qty)
            cr.execute(sql)
            move_ids = cr.fetchall()
            if move_ids:
                cr.execute("UPDATE stock_move SET inspec_id= %s WHERE id in %s",(inspec.id,tuple(move_ids),))
                print 'TPT update INSPEC for report', tuple(move_ids)
        return self.write(cr, uid, ids, {'result':'TPT update INSPEC for report Done'})
    
    def update_unit_price(self, cr, uid, ids, context=None):
        sql = '''
            select id from stock_move where issue_id is not null and state = 'done' and price_unit is null and picking_id is null and inspec_id is null
        '''
        cr.execute(sql)
        for line in cr.fetchall():
            move = self.pool.get('stock.move').browse(cr, 1, line[0])
            sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id = %s  and st.product_id=%s and date < '%s' 
                        union all
                            select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_id=%s and st.product_id=%s and date < '%s' 
                        )foo
                '''%(move.location_id.id,move.product_id.id,move.issue_id.date_expec,move.location_id.id,move.product_id.id,move.issue_id.date_expec)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = float(inventory['ton_sl'])
                total_cost = float(inventory['total_cost'])
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    update stock_move set price_unit = %s where id = %s
                '''%(avg_cost,move.id)
                cr.execute(sql)
                print 'TPT update ISSUE unit price for report', move.id
         
        sql = '''
            select id from stock_move where inspec_id is not null and state = 'done' and price_unit is null and picking_id is null and issue_id is null
        '''
        cr.execute(sql)
        for line1 in cr.fetchall():
            move = self.pool.get('stock.move').browse(cr, 1, line1[0])
            price = move.inspec_id and move.inspec_id.need_inspec_id and move.inspec_id.need_inspec_id.price_unit or 0
            sql = '''
               update stock_move set price_unit = %s where id = %s
            '''%(price,move.id)
            cr.execute(sql)
            print 'TPT update INSPEC unit price for report', move.id
        return self.write(cr, uid, ids, {'result':'TPT update UNIT PRICE for report Done'})

    def check_issue(self, cr, uid, ids, context=None):
        issue_obj = self.pool.get('tpt.material.issue')
        issue_ids = issue_obj.search(cr, uid, [('state','=','done')])
        result = 'Result for check issue mapping \n'
        for issue in issue_obj.browse(cr, uid, issue_ids):
            issue_qty = 0
            for line in issue.material_issue_line:
                issue_qty += line.product_isu_qty
            sql = '''
                select case when sum(product_qty)!=%s then 0 else 1 end check_map_issue from stock_move where issue_id=%s 
            '''%(issue_qty,issue.id)
            cr.execute(sql)
            rs = cr.fetchone()[0]
            if not rs:
                result += str(issue.id)+', '
        return self.write(cr, uid, ids, {'result':result})
    
    def check_inspec_without(self, cr, uid, ids, context=None):
        cr.execute(''' delete from tpt_update_inspection_line where update_id=%s ''',(ids[0],))
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        inspec_ids = inspec_obj.search(cr, uid, [('state','=','done')])
        result = 'Result for check inspection mapping \n'
        result_move_ids = []
        update_line = []
        for inspec in inspec_obj.browse(cr, uid, inspec_ids):
            sql = '''
                select case when sum(product_qty)!=%s then 0 else 1 end check_map_inspec from stock_move where inspec_id=%s 
            '''%(inspec.qty,inspec.id)
            cr.execute(sql)
            rs = cr.fetchone()[0]
            if not rs:
                result_move_ids.append(inspec.id)
                move_ids = move_obj.search(cr, uid, [('inspec_id','=',inspec.id),('product_qty','=',inspec.qty)])
                for seq,move_id in enumerate(move_ids):
                    if seq!=0:
                        cr.execute('update stock_move set inspec_id=null where id=%s',(move_id,))
                move_ids = move_obj.search(cr, uid, [('inspec_id','=',inspec.id)])
                if len(move_ids)>1:
                    for move_id in move_ids:
                        update_line.append((0,0,{'inspec_id':inspec.id,'move_id':move_id,'inspection_id':inspec.id,'stock_move_id':move_id}))
        result += str(result_move_ids)
        self.write(cr, uid, ids, {'result':result,'update_line':update_line})
        return result_move_ids
    
    def update_inspec(self, cr, uid, ids, context=None):
        result = 'Done update inspection \n'
        map_ins = self.map_inspec(cr, uid, ids)
        check_ins = self.check_inspec_without(cr, uid, ids)
        while (check_ins):
            map_ins = self.map_inspec(cr, uid, ids)
            check_ins = self.check_inspec_without(cr, uid, ids)
        return self.write(cr, uid, ids, {'result':result})
    
    def check_inspec_without_greater(self, cr, uid, ids, context=None):
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        inspec_ids = inspec_obj.search(cr, uid, [('state','=','done')])
        result = 'Result for check inspection mapping \n'
        result_move_ids = []
        for inspec in inspec_obj.browse(cr, uid, inspec_ids):
            sql = '''
                select case when sum(product_qty)>%s then 0 else 1 end check_map_inspec from stock_move where inspec_id=%s 
            '''%(inspec.qty,inspec.id)
            cr.execute(sql)
            rs = cr.fetchone()[0]
            if not rs:
                result_move_ids.append(inspec.id)
        result += str(result_move_ids)
        return self.write(cr, uid, ids, {'result':result})
    
    def check_inspec_without_less(self, cr, uid, ids, context=None):
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        inspec_ids = inspec_obj.search(cr, uid, [('state','=','done')])
        result = 'Result for check inspection mapping \n'
        result_move_ids = []
        for inspec in inspec_obj.browse(cr, uid, inspec_ids):
            sql = '''
                select case when sum(product_qty)<%s then 0 else 1 end check_map_inspec from stock_move where inspec_id=%s 
            '''%(inspec.qty,inspec.id)
            cr.execute(sql)
            rs = cr.fetchone()[0]
            if not rs:
                result_move_ids.append(inspec.id)
        result += str(result_move_ids)
        return self.write(cr, uid, ids, {'result':result})
    
    def check_inspec(self, cr, uid, ids, context=None):
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        inspec_ids = inspec_obj.search(cr, uid, [('state','=','done')])
        result = 'Result for check inspection mapping \n'
        result_move_ids = []
        for inspec in inspec_obj.browse(cr, uid, inspec_ids):
            sql = '''
                select case when sum(product_qty)!=%s then 0 else 1 end check_map_inspec from stock_move where inspec_id=%s 
            '''%(inspec.qty,inspec.id)
            cr.execute(sql)
            rs = cr.fetchone()[0]
            if not rs:
                result_move_ids.append(inspec.id)
            move_ids = move_obj.search(cr, uid, [('inspec_id','=',inspec.id)])
            if not move_ids and inspec.id not in result_move_ids:
                result_move_ids.append(inspec.id)
        result += str(result_move_ids)
        return self.write(cr, uid, ids, {'result':result})
    
    def create_issue(self, cr, uid, ids, context=None):
        result = 'Done create issue \n'
        issue_obj = self.pool.get('tpt.material.issue')
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        #create for issue 53
        line = issue_obj.browse(cr, uid, 53)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 8015)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 6,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 57
        line = issue_obj.browse(cr, uid, 57)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 8015)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 6,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 235
        line = issue_obj.browse(cr, uid, 235)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 2676)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 6,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 256
        line = issue_obj.browse(cr, uid, 256)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 8061)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 5,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 571
        line = issue_obj.browse(cr, uid, 571)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 11732)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 1,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 680
        line = issue_obj.browse(cr, uid, 680)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 11732)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 10,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 797
        line = issue_obj.browse(cr, uid, 797)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 10718)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 72,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10721)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 7.65,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10722)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 104.5,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10724)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 50,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10726)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 9.75,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10730)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 2.5,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10733)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 80,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10749)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 121,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10754)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 11.058,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10756)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 80,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10760)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 1300,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10791)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 1200,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10734)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 425,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10750)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 2550,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 12966)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 300,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10746)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 40,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10759)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 3.7,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10799)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 1220,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10753)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 2.6,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        #create for issue 1124
        line = issue_obj.browse(cr, uid, 1124)
        if line.request_type == 'production':
            dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
        else:
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                dest_id = location_ids[0]
        product = product_obj.browse(cr, uid, 10725)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 3,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10727)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 6,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        #
        product = product_obj.browse(cr, uid, 10796)
        cate_name = product.categ_id and product.categ_id.cate_name or False
        if cate_name == 'finish':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'raw':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        if cate_name == 'spares':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            if parent_ids:
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
            if locat_ids:
                location_id = locat_ids[0]
        rs = {
              'name': '/',
              'product_id':product.id,
              'product_qty': 600,
              'product_uom':product.uom_po_id and product.uom_po_id.id or False,
              'location_id':line.warehouse and line.warehouse.id or False,
              'location_dest_id':dest_id,
              'issue_id':line.id,
              'date':line.date_expec or False,
              'price_unit': 0,
              }
        move_id = move_obj.create(cr,uid,rs)
        move_obj.action_done(cr, uid, [move_id])
        cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date_expec,line.date_expec,move_id,))
        
        return self.write(cr, uid, ids, {'result':result})
    
    def create_inspec(self, cr, uid, ids, context=None):
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        result = 'Done create inspection \n'
        locat_obj = self.pool.get('stock.location')
        location_id = False
        location_dest_id = False
        parent_ids = locat_obj.search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
        if not parent_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection warehouse, please check it!'))
        locat_ids = locat_obj.search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
        if not locat_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection  location in Quality Inspection  warehouse, please check it!'))
        else:
            location_id = locat_ids[0]
        parent_dest_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
        if not parent_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
        
        for line in inspec_obj.browse(cr, uid, [1, 2, 3, 516]):
            if line.product_id.categ_id.cate_name=='raw':
                location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_dest_ids[0])])
            if line.product_id.categ_id.cate_name=='spares':
                location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Spares','Spare','spares','spare']),('location_id','=',parent_dest_ids[0])])
            if not location_dest_ids:
                raise osv.except_osv(_('Warning!'),_('System does not have Raw Material location in Store warehouse, please check it!'))
            else:
                location_dest_id = location_dest_ids[0]
            rs = {
                  'name': 'TPT create from inspection',
                  'product_id':line.product_id and line.product_id.id or False,
                  'product_qty':line.qty,
                  'product_uom':line.product_id.uom_po_id and line.product_id.uom_po_id.id or False,
                  'location_id':location_id,
                  'location_dest_id':location_dest_id,
                  'inspec_id':line.id,
                  'date':line.date,
                  'price_unit':line.price_unit or 0,
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
            cr.execute('update stock_move set date=%s,date_expected=%s where id=%s',(line.date,line.date,move_id,))
        return self.write(cr, uid, ids, {'result':result})
    
    def sum_avg_cost(self, cr, uid, ids, context=None):
        result = 'Done create inspection \n'
        inventory_obj = self.pool.get('tpt.product.avg.cost')
        product_id = self.browse(cr, uid, ids[0]).product_id.id
        for id in [product_id]:
            sql = '''
                update stock_move set price_unit = 0 where product_id=%s and price_unit<0
            '''%(id)
            cr.execute(sql)
            sql = 'delete from tpt_product_avg_cost where product_id=%s'%(id)
            cr.execute(sql)
            sql = '''
                select foo.loc as loc
                    from
                    (select st.location_id as loc from stock_move st
                        inner join stock_location l on st.location_id= l.id
                            where l.usage = 'internal'
                    union all
                    select st.location_dest_id as loc from stock_move st
                        inner join stock_location l on st.location_dest_id= l.id
                        where l.usage = 'internal'
                        )foo
                   group by foo.loc
            '''
            cr.execute(sql)
            for loc in cr.dictfetchall():
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st 
                            where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id and production_id is null
                        )foo
                '''%(id,loc['loc'])
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = float(inventory['ton_sl'])
                    total_cost = float(inventory['total_cost'])
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl 
                            from 
                                (
                                select st.product_qty*-1 as product_qty
                                    from stock_move st 
                                    where st.state='done'
                                        and st.product_id=%s
                                        and location_id=%s
                                        and location_dest_id != location_id
                                        and production_id is null
                                )foo
                    '''%(id,loc['loc'])
                    cr.execute(sql)
                    out = cr.dictfetchone()
                    if out:
                        hand_quantity = hand_quantity+float(out['ton_sl'])
                        total_cost = avg_cost*hand_quantity
                    
                    sql = '''
                        select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty as product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.
                                 location_dest_id != st.location_id
                                 and production_id is not null
                             union all
                             select st.product_qty*-1 as product_qty
                                from stock_move st 
                                where st.state='done'
                                        and st.product_id=%s
                                            and location_id=%s
                                            and location_dest_id != location_id
                                             and production_id is not null
                            )foo
                    '''%(id,loc['loc'],id,loc['loc'])
                    cr.execute(sql)
                    hand_quantity += cr.fetchone()[0]
                    sql = '''
                        select case when sum(produce_cost)!=0 then sum(produce_cost) else 0 end produce_cost,
                            case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty
                            from mrp_production where location_dest_id=%s and product_id=%s and state='done'
                    '''%(loc['loc'],id)
                    cr.execute(sql)
                    produce = cr.dictfetchone()
                    if produce:
#                         hand_quantity += float(produce['product_qty'])
                        total_cost += float(produce['produce_cost'])
                        avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    inventory_obj.create(cr, uid, {'product_id':id,
                                                   'warehouse_id':loc['loc'],
                                                   'hand_quantity':hand_quantity,
                                                   'avg_cost':avg_cost,
                                                   'total_cost':total_cost})
        return self.write(cr, uid, ids, {'result':result})
    
    def update_issue_unit_price(self, cr, uid, ids, context=None):
        sql = '''
            select id from stock_move where issue_id is not null and state = 'done' and picking_id is null and inspec_id is null
        '''
        cr.execute(sql)
        for line in cr.fetchall():
            move = self.pool.get('stock.move').browse(cr, 1, line[0])
            sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                        (select st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_dest_id = %s  and st.product_id=%s and date < '%s' 
                        union all
                            select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
                            from stock_move st
                                join stock_location loc1 on st.location_id=loc1.id
                                join stock_location loc2 on st.location_dest_id=loc2.id
                            where st.state='done' and st.location_id=%s and st.product_id=%s and date < '%s' 
                        )foo
                '''%(move.location_id.id,move.product_id.id,move.issue_id.date_expec,move.location_id.id,move.product_id.id,move.issue_id.date_expec)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = float(inventory['ton_sl'])
                total_cost = float(inventory['total_cost'])
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                if avg_cost < 0:
                    avg_cost = 0
                sql = '''
                    update stock_move set price_unit = %s where id = %s
                '''%(avg_cost,move.id)
                cr.execute(sql)
                print 'TPT update ISSUE unit price for report', move.id
         
        return self.write(cr, uid, ids, {'result':'TPT update UNIT PRICE for report Done'})
    
    def update_tpt_quanlity_inspection(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_quanlity_inspection where need_inspec_id is null
        '''
        cr.execute(sql)
        inspection_obj = self.pool.get('tpt.quanlity.inspection')
        inspection_ids = [r[0] for r in cr.fetchall()]
        for line in inspection_obj.browse(cr, uid, inspection_ids):
            sql = '''
                select picking_id from stock_move where product_id=%s and product_qty=%s and picking_id is not null and action_taken='need'
                   and (select count(id) from tpt_quanlity_inspection where name=%s and name not in (select name from tpt_quanlity_inspection 
                   where name in (select picking_id from stock_move where action_taken = 'direct' and state = 'done' )
                   and need_inspec_id is null))>1
            '''%(line.product_id.id,line.qty,line.name.id)
            cr.execute(sql)
            picking_ids = [r[0] for r in cr.fetchall()]
            if picking_ids:
                inspection_obj.write(cr, uid, [line.id], {'name':picking_ids[0]})
        cr.execute(''' update tpt_quanlity_inspection t set need_inspec_id=(select id from stock_move where action_taken = 'need' and picking_id=t.name and product_qty=t.qty and product_id=t.product_id limit 1) where need_inspec_id is null ''')
        return self.write(cr, uid, ids, {'result':'TPT tpt_quanlity_inspection Done'})
    
    def update_tpt_quanlity_inspection_v2(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_quanlity_inspection where name in (select name from tpt_quanlity_inspection group by name having count(name)>1) and need_inspec_id is not null
        '''
        cr.execute(sql)
        inspection_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        inspection_ids = [r[0] for r in cr.fetchall()]
        for line in inspection_obj.browse(cr, uid, inspection_ids):
            move = move_obj.browse(cr, uid, line.need_inspec_id.id)
            cr.execute(''' update tpt_quanlity_inspection set name=%s where id=%s ''',(move.picking_id.id,line.id,))
#         cr.execute(''' update tpt_quanlity_inspection t set need_inspec_id=(select id from stock_move where picking_id=t.name and product_qty=t.qty and product_id=t.product_id limit 1) where id in %s ''',(tuple(inspection_ids),))
        return self.write(cr, uid, ids, {'result':'TPT tpt_quanlity_inspection v2 Done'})
    
    def update_issue_with_posting(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where (select count(id) from account_move where doc_type in ( 'good') and material_issue_id=tpt_material_issue.id)>1
        '''
        cr.execute(sql)
        move_obj = self.pool.get('account.move')
        issue_obj = self.pool.get('tpt.material.issue')
        for line in cr.fetchall():
            sql = '''
                select id,state from account_move where doc_type='good' and material_issue_id = %s order by state
            '''%(line[0])
            cr.execute(sql)
            move = cr.fetchone()
            if move:
                if move[1]=='posted':
                    move_obj.button_cancel(cr, uid, [move[0]])
                cr.execute(''' delete from account_move where id=%s ''',(move[0],))
                
        sql = '''
            select id from account_move where doc_type in ('good') and material_issue_id is null and state='posted'
        '''
        cr.execute(sql)    
        move_ids = [r[0] for r in cr.fetchall()]
        move_obj.button_cancel(cr, uid, move_ids)
        sql = '''
            delete from account_move where doc_type in ('good') and material_issue_id is null
        '''
        cr.execute(sql)
        sql = '''
            select id from tpt_material_issue where (select count(id) from account_move where doc_type in ( 'good') and material_issue_id=tpt_material_issue.id)=0  and state='done'
                limit 150
        '''
        cr.execute(sql)
        issue_ids = [r[0] for r in cr.fetchall()]
        if not issue_ids:
            return self.write(cr, uid, ids, {'result':'TPT update_issue_with_posting Done'})
        issue_obj.bt_create_posting(cr, uid, issue_ids)
        return self.write(cr, uid, ids, {'result':'TPT update_issue_with_posting Remaining'})
    
    def fix_posting_issue(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where (select count(id) from account_move where doc_type in ( 'good') and material_issue_id=tpt_material_issue.id)>1
        '''
        cr.execute(sql)
        move_obj = self.pool.get('account.move')
        issue_obj = self.pool.get('tpt.material.issue')
        for line in cr.fetchall():
            sql = '''
                select id,state from account_move where doc_type='good' and material_issue_id = %s order by state
            '''%(line[0])
            cr.execute(sql)
            move = cr.fetchone()
            if move:
                if move[1]=='posted':
                    move_obj.button_cancel(cr, uid, [move[0]])
                cr.execute(''' delete from account_move where id=%s ''',(move[0],))
                
        sql = '''
            select id from account_move where doc_type in ('good') and state='posted'
        '''
        cr.execute(sql)    
        move_ids = [r[0] for r in cr.fetchall()]
        move_obj.button_cancel(cr, uid, move_ids)
        sql = '''
            delete from account_move where doc_type in ('good') and material_issue_id is null
        '''
        cr.execute(sql)
        sql = '''
            select id from tpt_material_issue where (select count(id) from account_move where doc_type in ( 'good') and material_issue_id=tpt_material_issue.id)=0  and state='done'
                limit 150
        '''
        cr.execute(sql)
        issue_ids = [r[0] for r in cr.fetchall()]
        if not issue_ids:
            return self.write(cr, uid, ids, {'result':'TPT fix_posting_issue Done'})
        issue_obj.bt_create_posting(cr, uid, issue_ids)
        return self.write(cr, uid, ids, {'result':'TPT fix_posting_issue Remaining'})
    
    def check_one_grn_one_posting(self, cr, uid, ids, context=None):
        sql = '''
            select id, name from stock_picking where type = 'in' and state = 'done'
        '''
        cr.execute(sql)
        for picking in cr.dictfetchall():
            sql = '''
                select id from account_move where doc_type = 'grn' and 
                id in (select move_id from account_move_line where LEFT(name,17) = '%s')
            '''%(picking['name'])
            cr.execute(sql)
            accounts = cr.dictfetchall()
            if len(accounts) > 1:
                for num in range(1, len(accounts)):
                    move_id = accounts[num]['id']
                    sql = '''
                        delete from account_move where id = %s
                    '''%(move_id)
                    cr.execute(sql)
                    sql = '''
                        delete from account_move_line where move_id = %s
                    '''%(move_id)
                    cr.execute(sql)
            if len(accounts) < 1:
                account_move_obj = self.pool.get('account.move')
                period_obj = self.pool.get('account.period')
                line = self.pool.get('stock.picking').browse(cr,uid,picking['id'])
                if line.type == 'in' and line.state=='done':
                    debit = 0.0
                    credit = 0.0
                    journal_line = []
                    for move in line.move_lines:
                        if move.purchase_line_id.price_unit:
                            amount = move.purchase_line_id.price_unit * move.product_qty
                        else:
                            amount = 0
                        if move.purchase_line_id.discount:
                            debit += amount - (amount*move.purchase_line_id.discount)/100
                        else:
                            debit += amount - (amount*0)/100
                    date_period = line.date,
                    sql = '''
                        select id from account_period where special = False and '%s' between date_start and date_stop
                     
                    '''%(date_period)
                    cr.execute(sql)
                    period_ids = [r[0] for r in cr.fetchall()]
                    if not period_ids:
                        raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                     
                    for period_id in period_obj.browse(cr,uid,period_ids):
                        sql_journal = '''
                        select id from account_journal
                        '''
                        cr.execute(sql_journal)
                        journal_ids = [r[0] for r in cr.fetchall()]
                        journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                        for p in line.move_lines:
                            if p.purchase_line_id.price_unit:
                                amount_cer = p.purchase_line_id.price_unit * p.product_qty
                            else:
                                amount_cer = 0 * p.product_qty
                            if p.purchase_line_id.discount:
                                credit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                                debit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                            else:
                                credit = amount_cer - (amount_cer*0)/100
                                debit = amount_cer - (amount_cer*0)/100
                            if not p.product_id.product_asset_acc_id:
                                print p.product_id.name
                                raise osv.except_osv(_('Warning!'),_('You need to define Product Asset GL Account for this product'))
                            journal_line.append((0,0,{
                                'name':line.name + ' - ' + p.product_id.name, 
                                'account_id': p.product_id.product_asset_acc_id and p.product_id.product_asset_acc_id.id,
                                'partner_id': line.partner_id and line.partner_id.id or False,
                                'credit':0,
                                'debit':debit,
                                'product_id':p.product_id.id,
                            }))
                            
                            if not p.product_id.purchase_acc_id:
                                raise osv.except_osv(_('Warning!'),_('You need to define Purchase GL Account for this product'))
                            journal_line.append((0,0,{
                                'name':line.name + ' - ' + p.product_id.name, 
                                'account_id': p.product_id.purchase_acc_id and p.product_id.purchase_acc_id.id,
                                'partner_id': line.partner_id and line.partner_id.id or False,
                                'credit':credit,
                                'debit':0,
                                'product_id':p.product_id.id,
                            }))
                             
                        vals={
                            'journal_id':journal.id,
                            'period_id':period_id.id ,
                            'date': date_period,
                            'line_id': journal_line,
                            'doc_type':'grn'
                            }
                        account_move_obj.create(cr,uid,vals)       
        return self.write(cr, uid, ids, {'result':'TPT Done'})
    
    def update_date_stock_move(self, cr, uid, ids, context=None):
        sql = '''
            update stock_move set date = (select date from stock_picking where id=stock_move.picking_id), date_expected = (select date from stock_picking where id=stock_move.picking_id) where picking_id is not null
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'Date Done'})
    
    def update_date_stock_move_from_inspection(self, cr, uid, ids, context=None):
        sql = '''
            update stock_move set date = (select date from tpt_quanlity_inspection where id=stock_move.inspec_id), date_expected = (select date from tpt_quanlity_inspection where id=stock_move.inspec_id) where inspec_id is not null
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'Date Done From Inspection'})
    
    def update_date_inspection(self, cr, uid, ids, context=None):
        sql = '''
            update tpt_quanlity_inspection set date = (select date from stock_move where id=tpt_quanlity_inspection.need_inspec_id) where need_inspec_id is not null
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_date_inspection Done'})
    
    def update_date_between_issue_and_account(self, cr, uid, ids, context=None):
        sql = '''
            update account_move set date = (select date_expec from tpt_material_issue where id = account_move.material_issue_id) where material_issue_id is not null
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_date_between_issue_and_account Done'})
    
    def update_date_between_grn_and_account(self, cr, uid, ids, context=None):
        sql = '''
            select * from stock_picking where state = 'done'
        '''
        cr.execute(sql)
        for picking in cr.dictfetchall():
            sql = '''
                update account_move set date = '%s', ref = '%s' where id in (select move_id from account_move_line where LEFT(name,17) = '%s')
            '''%(picking['date'], picking['name'], picking['name'])
            cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_date_between_grn_and_account Done'})
    
    def update_date_between_issue_and_stockmove(self, cr, uid, ids, context=None):
        sql = '''
            update stock_move set date = (select date_expec from tpt_material_issue where id = stock_move.issue_id) where issue_id is not null
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_date_between_issue_and_stockmove Done'})
    
    def create_quanlity_inspection(self, cr, uid, picking_id):
        quality_inspec = self.pool.get('tpt.quanlity.inspection')
        stock_picking = self.pool.get('stock.picking')
        for move in stock_picking.browse(cr, SUPERUSER_ID, picking_id).move_lines:
            if move.action_taken=='need':
                product_line = []
                if move.product_id.categ_id.cate_name=='raw':
                    for para in move.product_id.spec_parameter_line: 
                        product_line.append((0,0,{
                                            'name':para.name and para.name.id or False,
                                           'value':para.required_spec,
                                           'uom_id':para.uom_po_id and para.uom_po_id.id or False,
                                           }))
                vals={
                        'product_id':move.product_id.id,
                        'qty':move.product_qty,
                        'remaining_qty':move.product_qty,
                        'name':picking_id,
                        'supplier_id':move.picking_id.partner_id.id,
                        'date':move.picking_id.date,
                        'specification_line':product_line,
                        'need_inspec_id':move.id,
                        'price_unit':move.price_unit or 0,
                        }
                quality_inspec.create(cr, SUPERUSER_ID, vals)
        return True
    
    def update_one_stockmove_one_inspection(self, cr, uid, ids, context=None):
        quanlity_inspec = []
        product_qty = 0
        dem = 0
        delete = 0
        sql = '''
            select * from stock_move where picking_id in (select id from stock_picking where state = 'done' and type = 'in') 
            and action_taken = 'need'
        '''
        cr.execute(sql)
        for move in cr.dictfetchall():
            picking = self.pool.get('stock.picking').browse(cr,uid,move['picking_id'])
            sql = '''
                select * from tpt_quanlity_inspection where need_inspec_id = %s and state in ('remaining', 'done')
            '''%(move['id'])
            cr.execute(sql)
            inspections = cr.dictfetchall()
            if inspections:
                if len(inspections) > 1:
                    for num in range(1,len(inspections)):
                        sql = '''
                            delete from stock_move where inspec_id = %s
                        '''%(inspections[num]['id'])
                        cr.execute(sql)
                        sql = '''
                            delete from tpt_quanlity_inspection where id = %s
                        '''%(inspections[num]['id'])
                        cr.execute(sql)
#             else:
#                 print move['id']
#                 self.create_quanlity_inspection(move['picking_id'])
                    
        return self.write(cr, uid, ids, {'result':'update_one_stockmove_one_inspection Done'})
    
    def update_one_stockmove_one_inspection_v2(self, cr, uid, ids, context=None):
        quanlity_inspec = []
        product_qty = 0
        dem = 0
        delete = 0
        sql = '''
            select * from stock_move where picking_id in (select id from stock_picking where state = 'done' and type = 'in') 
            and action_taken = 'need'
        '''
        cr.execute(sql)
        for move in cr.dictfetchall():
            picking = self.pool.get('stock.picking').browse(cr,uid,move['picking_id'])
            sql = '''
                select * from tpt_quanlity_inspection where need_inspec_id = %s 
            '''%(move['id'])
            cr.execute(sql)
            inspections = cr.dictfetchall()
            if inspections:
                if len(inspections) > 1:
                    for num in range(0,len(inspections)):
                        if inspections[num]['state'] == 'draft': 
                            sql = '''
                                delete from tpt_quanlity_inspection where id = %s
                            '''%(inspections[num]['id'])
                            cr.execute(sql)
                    
        return self.write(cr, uid, ids, {'result':'update_one_stockmove_one_inspection_v2 Done'})
    
    def update_data_104(self, cr, uid, ids, context=None):
        sql = '''
            select picking_id from stock_move where product_id = 12850 and state = 'done' and action_taken = 'need' and product_qty = 24.0
        '''
        cr.execute(sql)
        move = cr.dictfetchone()['picking_id']
        sql = '''
            update tpt_quanlity_inspection set name = %s where id = 104
        '''%(move)
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_data_104 Done'})
    
    def update_aed(self, cr, uid, ids, context=None):
        amount_basic = 0.0
        amount_p_f=0.0
        amount_ed=0.0
        amount_fright=0.0
        line_net = 0.0
        account_inv_obj = self.pool.get('account.invoice.line')
        sql='''
            select id from account_invoice_line
        '''
        cr.execute(sql)
        inv_line_ids = [row[0] for row in cr.fetchall()]
        if inv_line_ids:
            for line in account_inv_obj.browse(cr,uid,inv_line_ids,context=context):
                amount_total_tax=0.0
                amount_basic = (line.quantity * line.price_unit)-((line.quantity * line.price_unit)*line.disc/100)
                if line.p_f_type == '1':
                   amount_p_f = amount_basic * (line.p_f/100)
                elif line.p_f_type == '2':
                    amount_p_f = line.p_f
                elif line.p_f_type == '3':
                    amount_p_f = line.p_f * line.quantity
                else:
                    amount_p_f = line.p_f
                if line.ed_type == '1':
                   amount_ed = (amount_basic + amount_p_f) * (line.ed/100)
                elif line.ed_type == '2':
                    amount_ed = line.ed
                elif line.ed_type == '3':
                    amount_ed = line.ed * line.quantity
                else:
                    amount_ed = line.ed
                if line.fright_type == '1':
                   amount_fright = (amount_basic + amount_p_f + amount_ed) * (line.fright/100)
                elif line.fright_type == '2':
                    amount_fright = line.fright
                elif line.fright_type == '3':
                    amount_fright = line.fright * line.quantity
                else:
                    amount_fright = line.fright
                tax_amounts = [r.amount for r in line.invoice_line_tax_id]
                for tax in tax_amounts:
                    amount_total_tax += tax/100
                line_net = amount_total_tax+amount_fright+amount_ed+amount_p_f+amount_basic+line.aed_id_1
                
                sql = '''
                    update account_invoice_line set line_net = %s where id = %s
                '''%(line_net,line.id)
                cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_aed Done'})
    
    def update_for_lg(self, cr, uid, ids, context=None):
        quanlity_inspec = []
        product_qty = 0
        dem = 0
        delete = 0
        sql = '''
            select * from stock_move where picking_id in (select id from stock_picking where state = 'done' and type = 'in') 
            and action_taken = 'need' and product_id = 10718
        '''
        cr.execute(sql)
        for move in cr.dictfetchall():
            picking = self.pool.get('stock.picking').browse(cr,uid,move['picking_id'])
            sql = '''
                select * from tpt_quanlity_inspection where need_inspec_id = %s 
            '''%(move['id'])
            cr.execute(sql)
            inspections = cr.dictfetchall()
            if not inspections:
                self.create_quanlity_inspection(cr,uid,move['picking_id'])
        return self.write(cr, uid, ids, {'result':'update_for_lg Done'})        
    
    def check_one_stockmove_one_inspection(self, cr, uid, ids, context=None):
        quanlity_inspec = []
        product_qty = 0
        for check in self.browse(cr,uid,ids):
            sql = '''
                    delete from tpt_update_inspection_line where update_id = %s
                '''%(check.id)
            cr.execute(sql)
            
            
        # kiem tra xem cac quanlity inspection ko co need_inspec_id
#             sql = '''
#                 select * from tpt_quanlity_inspection where need_inspec_id is null and state in ('remaining', 'done')
#             '''
#             cr.execute(sql)
#             inspection_nulls = cr.dictfetchall()
#             if inspection_nulls:
#                 for seq, inspection_null in enumerate(inspection_nulls):
#                     quanlity = self.pool.get('tpt.quanlity.inspection').browse(cr,uid,inspection_null['id'])
#                     quanlity_inspec.append((0,0,{
#                                         'name': 'check khong co need_inspec_id',
#                                         'seq': seq + 1,
#                                         'inspec_id': inspection_null['id'],
#                                         'move_id': False,
#                                         'inspec_qty': int(inspection_null['qty']),
#                                         'move_qty': False,
#                                         'inspection_id': int(inspection_null['id']),
#                                         'stock_move_id': False,
#                                         'product_id': quanlity.product_id.id,
#                                         'product_name': quanlity.product_id.name,
#                                         'state_inspec': quanlity.state,
#                                                 }))
        # end
        
        #kiem tra cac quanlity inspection nao co need_inspec_id nhung khong co stock move
        
            sql = '''
                select * from tpt_quanlity_inspection where need_inspec_id is not null and state in ('remaining', 'done')
            '''
            cr.execute(sql)
            for inspection in cr.dictfetchall():
                quanlity = self.pool.get('tpt.quanlity.inspection').browse(cr,uid,inspection['id'])
                sql = '''
                select * from stock_move where picking_id in (select id from stock_picking where state = 'done' and type = 'in') 
                and action_taken = 'need' and id = %s
                '''%(inspection['need_inspec_id'])
                cr.execute(sql)
                moves = cr.dictfetchall()
                if moves:
                    if len(moves) > 1:
                        for seq, move in enumerate(moves):
                            quanlity_inspec.append((0,0,{
                                                'name': 'Co quanlity inspection(need_inspec_id) nhung co nhieu stock move',
                                                'seq': seq + 1,
                                                'inspec_id': inspection['id'],
                                                'move_id': move['id'],
                                                'inspec_qty': int(inspection['qty']),
                                                'move_qty': int(move['product_qty']),
                                                'inspection_id': int(inspection['id']),
                                                'stock_move_id': int(move['id']),
                                                'product_id': quanlity.product_id.id,
                                                'product_name': quanlity.product_id.name,
                                                'state_inspec': quanlity.state,
                                                        }))
                else:
                    quanlity_inspec.append((0,0,{
                                                'name': 'Co quanlity inspection(need_inspec_id) nhung khong co stock move (stock move bi xoa)',
                                                'seq': False,
                                                'inspec_id': inspection['id'],
                                                'move_id': False,
                                                'inspec_qty': int(inspection['qty']),
                                                'move_qty': False,
                                                'inspection_id': int(inspection['id']),
                                                'stock_move_id': False,
                                                'product_id': quanlity.product_id.id,
                                                'product_name': quanlity.product_id.name,
                                                'state_inspec': quanlity.state,
                                                        }))
        # end 
        
            sql = '''
                select * from stock_move where picking_id in (select id from stock_picking where state = 'done' and type = 'in') 
                and action_taken = 'need'
            '''
            cr.execute(sql)
            for move in cr.dictfetchall():
                stock = self.pool.get('stock.move').browse(cr,uid,move['id'])
        # kiem tra xem trong cac quanlity inspection co quanlity inspection nao bi trung need_inspec_id hay khong
                sql = '''
                    select * from tpt_quanlity_inspection where need_inspec_id = %s 
                '''%(move['id'])
                cr.execute(sql)
                inspections = cr.dictfetchall()
                if inspections:
                    if len(inspections) > 1:
                        for seq, inspection in enumerate(inspections):
                            quanlity = self.pool.get('tpt.quanlity.inspection').browse(cr,uid,inspection['id'])
                            quanlity_inspec.append((0,0,{
                                                'name': 'Co 1 stock move nhung co nhieu quanlity inspection(need_inspec_id)',
                                                'seq': seq + 1,
                                                'inspec_id': inspection['id'],
                                                'move_id': move['id'],
                                                'inspec_qty': int(inspection['qty']),
                                                'move_qty': int(move['product_qty']),
                                                'inspection_id': int(inspection['id']),
                                                'stock_move_id': int(move['id']),
                                                'product_id': quanlity.product_id.id,
                                                'product_name': quanlity.product_id.name,
                                                'state_inspec': quanlity.state,
                                                        }))
                else:
                    quanlity_inspec.append((0,0,{
                                                'name': 'Co stock move nhung khong co quanlity inspection',
                                                'seq': False,
                                                'inspec_id': False,
                                                'move_id': move['id'],
                                                'inspec_qty': False,
                                                'move_qty': int(move['product_qty']),
                                                'inspection_id': False,
                                                'stock_move_id': int(move['id']),
                                                'product_id': stock.product_id.id,
                                                'product_name': stock.product_id.name,
                                                        }))
            
        # Kiem tra quanlity inspection voi trang thai done 
            sql = '''
                select * from tpt_quanlity_inspection where state in ('remaining', 'done')
            '''
            cr.execute(sql)
            for quanlity_done in cr.dictfetchall():
                quanlity = self.pool.get('tpt.quanlity.inspection').browse(cr,uid,quanlity_done['id'])
                sql = '''
                    select * from stock_move where inspec_id = %s and state = 'done'
                '''%(quanlity_done['id'])
                cr.execute(sql)
                new_moves = cr.dictfetchall()
#                 if new_moves:
#                     for seq, new_move in enumerate(new_moves):
#                         sql = '''
#                             select sum(product_qty) as product_qty, inspec_id from stock_move where inspec_id = %s and state = 'done' group by inspec_id
#                         '''%(quanlity_done['id'])
#                         cr.execute(sql)
#                         for inspec_move in cr.dictfetchall():
#                             if inspec_move:
#                                 product_qty = inspec_move['product_qty']
#                         qty = quanlity_done['qty']
#                         remaining_qty = quanlity_done['remaining_qty']
#                         if (qty - remaining_qty) != product_qty:
#                             quanlity_inspec.append((0,0,{
#                                                 'name': 'Co quanlity inspection va co stock move moi nhung khong khop so luong',
#                                                 'seq': seq + 1,
#                                                 'inspec_id': quanlity_done['id'],
#                                                 'move_id': new_move['id'],
#                                                 'inspec_qty': quanlity_done['qty'] - quanlity_done['remaining_qty'],
#                                                 'move_qty': product_qty,
#                                                 'inspection_id': quanlity_done['id'],
#                                                 'stock_move_id': new_move['id'],
#                                                         }))
                if not new_moves:
                    quanlity_inspec.append((0,0,{
                                                'name': 'Co quanlity inspection nhung chua tao ra stock move moi',
                                                'seq': False,
                                                'inspec_id': quanlity_done['id'],
                                                'move_id': False,
                                                'inspec_qty': quanlity_done['qty'],
                                                'move_qty': False,
                                                'inspection_id': quanlity_done['id'],
                                                'stock_move_id': False,
                                                'product_id': quanlity.product_id.id,
                                                'product_name': quanlity.product_id.name,
                                                'state_inspec': quanlity.state,
                                                        }))
        return self.write(cr, uid, ids, {'update_line':quanlity_inspec})
    
    def sync_stock_move_and_quanlity_inspection_v1(self, cr, uid, ids, context=None):
        def select_quanlity_inspection_map_stock_move(cr, uid):
            num = 0
            sql = '''
                select id from tpt_quanlity_inspection where need_inspec_id is null
            '''
            cr.execute(sql)
            inspec_ids = [r[0] for r in cr.fetchall()]
            print 'Co inspection Khong co stock move nguon: ',len(inspec_ids),' dong ',inspec_ids
            return inspec_ids

        quanlity_inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')

        quanlity_inspec_ids = True
        while (quanlity_inspec_ids):
            #Co inspection Khong co stock move nguon
            quanlity_inspec_ids = select_quanlity_inspection_map_stock_move(cr, uid)
            for inspec in quanlity_inspec_obj.browse(cr, uid, quanlity_inspec_ids):
                sql = '''
                    select id from stock_move where picking_id=%s and product_id=%s and state='done' and action_taken='need' and
                        id not in (select need_inspec_id from tpt_quanlity_inspection where need_inspec_id is not null)
                '''%(inspec.name.id,inspec.product_id.id)
                cr.execute(sql)
                move_ids = [r[0] for r in cr.fetchall()]
#                 move_ids = move_obj.search(cr, uid, [('picking_id','=',inspec.name.id),('product_id','=',inspec.product_id.id),('state','=','done'),('action_taken','=','need')])
                if len(move_ids)>=1:
                    move = move_obj.browse(cr, uid, move_ids[0])
                    sql = '''
                        delete from stock_move where inspec_id=%s
                    '''%(inspec.id)
                    cr.execute(sql)
                    sql = '''
                        update tpt_quanlity_inspection set qty=%s,remaining_qty=%s,qty_approve=%s,state='draft',need_inspec_id=%s where id = %s
                    '''%(move.product_qty,move.product_qty,move.product_qty,move.id,inspec.id)
                    cr.execute(sql)
                if not move_ids:
                    sql = '''
                        delete from stock_move where inspec_id=%s
                    '''%(inspec.id)
                    cr.execute(sql)
                    sql = '''
                        delete from tpt_quanlity_inspection where id=%s
                    '''%(inspec.id)
                    cr.execute(sql)
                
        return self.write(cr, uid, ids, {'result':'sync_stock_move_and_quanlity_inspection V1 Done'})   
    
    def sync_stock_move_and_quanlity_inspection_v2(self, cr, uid, ids, context=None):
        
        def select_stock_move_map_quanlity_inspection(cr, uid):
            move_miss = 0
            move_more = 0
            sql = '''
                select id from stock_move where state='done' and action_taken='need'
            '''
            cr.execute(sql)
            move_ids = [r[0] for r in cr.fetchall()]
            move_miss_ids = []
            move_more_ids = []
            for move in self.pool.get('stock.move').browse(cr, uid,move_ids):
                sql = '''
                    select id from tpt_quanlity_inspection where need_inspec_id=%s
                '''%(move.id)
                cr.execute(sql)
                inspec_ids = [r[0] for r in cr.fetchall()]
                if len(inspec_ids)==0:
                    move_miss_ids.append(move.id)
                    move_miss+=1
#                 if len(inspec_ids)>1:
#                     move_more_ids.append(move.id)
#                     move_more+=1
#                     print 'stock move nguon co nhieu quanlity inspection: ',move['id'],move_more,' voi ',inspec_ids
            print 'stock move nguon khong co quanlity inspection: ',move_miss,' dong ',move_miss_ids
            return move_miss_ids
        
        quanlity_inspec_obj = self.pool.get('tpt.quanlity.inspection')
        move_obj = self.pool.get('stock.move')
        #stock move nguon khong co quanlity inspection
        move_miss_ids = select_stock_move_map_quanlity_inspection(cr, uid)
        for move in move_obj.browse(cr, uid, move_miss_ids):
            product_line = []
            if move.product_id.categ_id.cate_name=='raw':
                for para in move.product_id.spec_parameter_line: 
                    product_line.append((0,0,{
                                        'name':para.name and para.name.id or False,
                                       'value':para.required_spec,
                                       'uom_id':para.uom_po_id and para.uom_po_id.id or False,
                                       }))
            vals={
                    'product_id':move.product_id.id,
                    'qty':move.product_qty,
                    'remaining_qty':move.product_qty,
                    'name':move.picking_id.id,
                    'supplier_id':move.picking_id.partner_id.id,
                    'date':move.picking_id.date,
                    'specification_line':product_line,
                    'need_inspec_id':move.id,
                    'price_unit':move.price_unit or 0,
                    }
            quanlity_inspec_obj.create(cr, SUPERUSER_ID, vals)
        
        sql = '''
            delete from stock_move where inspec_id in(select id from tpt_quanlity_inspection where need_inspec_id not in (select id from stock_move where state='done' and action_taken='need'))
        '''
        cr.execute(sql)
        sql = '''
            delete from tpt_quanlity_inspection where need_inspec_id not in (select id from stock_move where state='done' and action_taken='need')
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'sync_stock_move_and_quanlity_inspection V2 Done'})  
    
    def delete_2_issue_2406_2407(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move_line where move_id in (select id from account_move 
            where material_issue_id in (select id from tpt_material_issue where doc_no in ('1002356/2015','1002357/2015'))) 
        '''
        cr.execute(sql)
        sql = '''
            delete from account_move 
            where material_issue_id in (select id from tpt_material_issue where doc_no in ('1002356/2015','1002357/2015'))
        '''
        cr.execute(sql)
        sql = '''
            delete from stock_move where issue_id in (select id from tpt_material_issue where doc_no in ('1002356/2015','1002357/2015'))
        '''
        cr.execute(sql)
        sql = '''
            delete from tpt_material_issue_line 
            where material_issue_id in (select id from tpt_material_issue where doc_no in ('1002356/2015','1002357/2015'))
        '''
        cr.execute(sql)
        sql = '''
            delete from tpt_material_issue where doc_no in ('1002356/2015','1002357/2015')
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'delete_2_issue_2406_2407 Done'}) 
    
    def delete_account_move_old_data_for_issue(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move_line 
            where move_id in (select id from account_move where doc_type = 'good') 
        '''
        cr.execute(sql)
        sql = '''
            delete from account_move where doc_type = 'good' 
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'delete_account_move_old_data_for_issue Done'}) 
    
    def create_one_issue_one_posting(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and id not in (select material_issue_id from account_move where doc_type='good' and material_issue_id is not null) limit 500
        '''
        cr.execute(sql)
        issue_ids = [r[0] for r in cr.fetchall()]
        dem = 1
        if not issue_ids:
            return self.write(cr, uid, ids, {'result':'create_one_issue_one_posting Done'}) 
        for line in self.pool.get('tpt.material.issue').browse(cr,uid,issue_ids):
            journal_line = []
            date_period = line.date_expec
            sql = '''
                select id from account_journal
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            sql = '''
                select id from account_period where '%s' between date_start and date_stop
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
             
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            for period_id in self.pool.get('account.period').browse(cr,uid,period_ids):
                
                for mater in line.material_issue_line:
    #                 price += mater.product_id.standard_price * mater.product_isu_qty
                    acc_expense = mater.product_id and mater.product_id.property_account_expense and mater.product_id.property_account_expense.id or False
                    acc_asset = mater.product_id and mater.product_id.product_asset_acc_id and mater.product_id.product_asset_acc_id.id or False
                    if not acc_expense or not acc_asset:
                        raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for all materials!'))
                    avg_cost_ids = self.pool.get('tpt.product.avg.cost').search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                    unit = 1
                    if avg_cost_ids:
                        avg_cost_id = self.pool.get('tpt.product.avg.cost').browse(cr, uid, avg_cost_ids[0])
                        unit = avg_cost_id.avg_cost or 0
                    sql = '''
                        select price_unit from stock_move where product_id=%s and product_qty=%s and issue_id=%s
                    '''%(mater.product_id.id,mater.product_isu_qty,mater.material_issue_id.id)
                    cr.execute(sql)
                    move_price = cr.fetchone()
                    if move_price and move_price[0] and move_price[0]>0:
                        unit=move_price[0]
                    if not unit or unit<0:
                        unit=1
#                     price += unit * mater.product_isu_qty
                    product_price = unit * mater.product_isu_qty
                    
                    journal_line.append((0,0,{
                                            'name':line.doc_no + ' - ' + mater.product_id.name, 
                                            'account_id': acc_asset,
                                            'debit':0,
                                            'credit':product_price,
                                            'product_id':mater.product_id.id,
                                             
                                           }))
                    journal_line.append((0,0,{
                                'name':line.doc_no + ' - ' + mater.product_id.name, 
                                'account_id': acc_expense,
                                'credit':0,
                                'debit':product_price,
                                'product_id':mater.product_id.id,
                            }))
            value={
                    'journal_id':journal_ids[0],
                    'period_id':period_id.id ,
                    'ref': line.doc_no,
                    'date': date_period,
                    'material_issue_id': line.id,
                    'line_id': journal_line,
                    'doc_type':'good'
                    }
            new_jour_id = self.pool.get('account.move').create(cr,uid,value)
            print 'Phuoc: ',dem, new_jour_id
            dem+=1
        return self.write(cr, uid, ids, {'result':'create_one_issue_one_posting Remaining'})    
    
               
    
    def update_price_unit_from_quanlity_inspection(self, cr, uid, ids, context=None):
        sql = '''
            select * from stock_move where state = 'done' and picking_id is not null and action_taken = 'need'
        '''
        cr.execute(sql)
        move_olds = cr.dictfetchall()
        if move_olds:
            for move in move_olds:
                sql = '''
                    select * from tpt_quanlity_inspection where state in ('remaining', 'done') and need_inspec_id = %s and need_inspec_id is not null
                '''%(move['id'])
                cr.execute(sql)
                quanlity_inspections = cr.dictfetchall()
                if quanlity_inspections:
                    for inspection in quanlity_inspections:
                        sql = '''
                            select id from stock_move where inspec_id = %s and state = 'done' and inspec_id is not null
                        '''%(inspection['id'])
                        cr.execute(sql)
                        move_new = cr.dictfetchone()['id']
                        sql = '''
                            update stock_move set price_unit = %s where id = %s
                        '''%(move['price_unit'], move_new)
                        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_price_unit_from_quanlity_inspection Done'})
    
    

    def update_price_unit_for_good_issue(self, cr, uid, ids, context=None):
        sql = '''
            select product_product.id as product_id
            from product_product,product_template 
            where product_template.categ_id in(select product_category.id from product_category where cate_name in('spares','raw') )
            and product_product.product_tmpl_id = product_template.id;
        '''
        cr.execute(sql)
        product_ids = cr.dictfetchall()
        for product in product_ids:
            stock_move = []
            product_id = self.pool.get('product.product').browse(cr,uid,product['product_id'])
            if product_id.categ_id.cate_name == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            if product_id.categ_id.cate_name == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])]) 
            sql = '''
                select id, inspec_id, picking_id, issue_id, product_qty, price_unit, date
                        from stock_move st
                        where st.state='done' and st.product_id=%s
                            and st.location_dest_id != st.location_id
                            and  (action_taken = 'direct'
                            or (inspec_id is not null and location_dest_id = %s)
                            or issue_id is not null
                            or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
                            and id not in (select id
                                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                                and picking_id is null and inspec_id is null and location_id = %s 
                                and location_id != location_dest_id)
                    )order by to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD'), inspec_id, picking_id, issue_id
            '''%(product_id.id, locat_ids[0], product_id.id, locat_ids[0])
            cr.execute(sql)
            for move in cr.dictfetchall():
                if move['issue_id']:
                    qty = 0
                    value = 0
                    for line in stock_move:
                        qty += line[2]['quantity'] 
                        value += line[2]['price']
                    price = qty and value/qty or 0
#                     self.pool.get('stock.move').write(cr,uid,[move['id']], {
#                                                                             'price_unit': round(price,3)
#                                                                             })
                    sql = '''
                        update stock_move set price_unit = %s where id = %s
                    '''%(price, move['id'])
                    cr.execute(sql)
                    stock_move.append((0,0,{
                                            'quantity': -move['product_qty'],
                                            'price': -(move['product_qty']*price),
                                            }))
                else:
                    stock_move.append((0,0,{
                                            'quantity': move['product_qty'],
                                            'price': move['product_qty']*move['price_unit'],
                                            }))
                
                    
                        
        return self.write(cr, uid, ids, {'result':'update_price_unit_for_good_issue Done'})  
    
    def update_price_unit_for_production_COAL(self, cr, uid, ids, context=None):
        stock_move = []
        parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
        sql = '''
            select id, inspec_id, picking_id, issue_id, product_qty, price_unit, location_id, product_id, date
                        from stock_move
                        where state='done' and product_id in (select id from product_product where default_code = 'M0501060001')
                            and location_dest_id != location_id
                            and  (action_taken = 'direct'
                            or (inspec_id is not null and location_dest_id = %s)
                            or issue_id is not null
                            or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
                            or (location_id = %s and id in (select move_id from mrp_production_move_ids))
                    )order by to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD'), inspec_id, picking_id, issue_id
        '''%(locat_ids[0], locat_ids[0])
        cr.execute(sql)
        for move in cr.dictfetchall():
            if move['issue_id']:
                qty = 0
                value = 0
                for line in stock_move:
                    qty += line[2]['quantity'] 
                    value += line[2]['price']
                price = qty and value/qty or 0
                sql = '''
                    update stock_move set price_unit = %s where id = %s
                '''%(price, move['id'])
                cr.execute(sql)
                stock_move.append((0,0,{
                                        'quantity': -move['product_qty'],
                                        'price': -(move['product_qty']*price),
                                        }))
            elif not move['issue_id'] and not move['picking_id'] and not move['inspec_id'] and move['location_id'] == locat_ids[0]:
                qty = 0
                value = 0
                for line in stock_move:
                    qty += line[2]['quantity'] 
                    value += line[2]['price']
                price = qty and value/qty or 0
                sql = '''
                    update stock_move set price_unit = %s where id = %s
                '''%(price, move['id'])
                cr.execute(sql)
                stock_move.append((0,0,{
                                        'quantity': -move['product_qty'],
                                        'price': -(move['product_qty']*price),
                                        }))
            else:
                stock_move.append((0,0,{
                                        'quantity': move['product_qty'],
                                        'price': move['product_qty']*move['price_unit'],
                                        }))
#             sql = '''
#                    select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
#                    where product_id = %s and invoice_id in (select id from account_invoice where date_invoice = '%s' and sup_inv_id is not null)
#                    group by product_id
#                '''%(move['product_id'], move['date'])
#             cr.execute(sql)
#             for inventory in cr.dictfetchall():
#                 freight_cost = inventory['line_net'] or 0
#             if freight_cost:
#                 stock_move.append((0,0,{
#                                         'quantity': 0,
#                                         'price': freight_cost,
#                                         }))
            
        return self.write(cr, uid, ids, {'result':'update_price_unit_for_production_COAL Done'}) 
    
    def update_issue_line_for_request_6000028 (self, cr, uid, ids, context=None):
        sql = '''
            select material_issue_id from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where state = 'done' 
            and name in (select id from tpt_material_request where name = '6000028/2015'))
        '''
        cr.execute(sql)
        material_issue_id = cr.dictfetchone()['material_issue_id']
        if material_issue_id:
            issue = self.pool.get('tpt.material.issue').browse(cr, uid, material_issue_id, context=context)
            issue_line = []
            for line in issue.material_issue_line:
                line_ids = self.pool.get('tpt.material.issue.line').search(cr, uid,[('id','!=',line.id),('product_id','=',line.product_id.id),('product_isu_qty','=',line.product_isu_qty),('material_issue_id','=',line.material_issue_id.id)])
                if line_ids and line_ids[0] not in issue_line:
                    sql = '''
                        delete from tpt_material_issue_line 
                        where id = %s
                    '''%(line_ids[0])
                    cr.execute(sql)
                    issue_line.append(line.id)
            
#             for product_id in [10730, 10733, 10734,10746,10748,10749,10750,10754,10756,10759,10760,10796,10799]:
#                 
#                 sql = '''
#                         select id from tpt_material_issue_line 
#                         where product_id = %s and material_issue_id = %s
#                     '''%(product_id, material_issue_id)
#                 cr.execute(sql)
#                 line_ids = cr.fetchall()[0]
#                 sql = '''
#                         delete from tpt_material_issue_line 
#                         where id = %s
#                     '''%(line_ids)
#                 cr.execute(sql)
                ###################### delete stock move
                    sql = '''
                            select count(*) from stock_move 
                            where product_id = %s and issue_id = %s
                        '''%(line.product_id.id, material_issue_id)
                    cr.execute(sql)
                    number = cr.fetchone()[0]
                    if number == 2:
#                     move_ids = cr.fetchall()[0]
                        sql = '''
                            select id from stock_move 
                            where product_id = %s and issue_id = %s
                        '''%(line.product_id.id, material_issue_id)
                        cr.execute(sql)
                        move_ids = cr.fetchall()[0]
                        sql = '''
                                delete from stock_move 
                                where id = %s
                            '''%(move_ids)
                        cr.execute(sql)
                
        return self.write(cr, uid, ids, {'result':'update_issue_line_for_request_6000028 Done'})
    
    def delete_account_move_6000028(self, cr, uid, ids, context=None):
#         sql = '''
#             delete from account_move_line 
#             where move_id in (select id from account_move where doc_type = 'good' 
#             and material_issue_id in (select id from tpt_material_issue where state = 'done' 
#             and name in (select id from tpt_material_request where name = '6000028/2015') ) )
#         '''
#         cr.execute(sql)
#         sql = '''
#             delete from account_move where doc_type = 'good' and material_issue_id in (select id from tpt_material_issue where state = 'done' 
#             and name in (select id from tpt_material_request where name = '6000028/2015') )
#         '''
#         cr.execute(sql)
        
        sql = '''
            delete from account_move_line 
            where move_id in (select id from account_move where doc_type = 'good' 
            and material_issue_id = 3066 ) 
        '''
        cr.execute(sql)
        
        sql = '''
            delete from account_move where doc_type = 'good' and material_issue_id = 3066
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'delete_account_move_6000028 Done'}) 
    
    def create_posting_6000028(self, cr, uid, ids, context=None):
#         sql = '''
#             select id from tpt_material_issue where state = 'done' and name in (select id from tpt_material_request where name = '6000028/2015')
#         '''
#         cr.execute(sql)
        sql = '''
            select id from tpt_material_issue where id = 3066
        '''
        cr.execute(sql)
        issue_ids = [r[0] for r in cr.fetchall()]
        dem = 1
        for line in self.pool.get('tpt.material.issue').browse(cr,uid,issue_ids):
            journal_line = []
            date_period = line.date_expec
            sql = '''
                select id from account_journal
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            sql = '''
                select id from account_period where '%s' between date_start and date_stop
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
             
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            for period_id in self.pool.get('account.period').browse(cr,uid,period_ids):
                
                for mater in line.material_issue_line:
    #                 price += mater.product_id.standard_price * mater.product_isu_qty
                    acc_expense = mater.product_id and mater.product_id.property_account_expense and mater.product_id.property_account_expense.id or False
                    acc_asset = mater.product_id and mater.product_id.product_asset_acc_id and mater.product_id.product_asset_acc_id.id or False
                    if not acc_expense or not acc_asset:
                        raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for all materials!'))
                    avg_cost_ids = self.pool.get('tpt.product.avg.cost').search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                    unit = 1
                    if avg_cost_ids:
                        avg_cost_id = self.pool.get('tpt.product.avg.cost').browse(cr, uid, avg_cost_ids[0])
                        unit = avg_cost_id.avg_cost or 0
                    sql = '''
                        select price_unit from stock_move where product_id=%s and product_qty=%s and issue_id=%s
                    '''%(mater.product_id.id,mater.product_isu_qty,mater.material_issue_id.id)
                    cr.execute(sql)
                    move_price = cr.fetchone()
                    if move_price and move_price[0] and move_price[0]>0:
                        unit=move_price[0]
                    if not unit or unit<0:
                        unit=1
#                     price += unit * mater.product_isu_qty
                    product_price = unit * mater.product_isu_qty
                    
                    journal_line.append((0,0,{
                                            'name':line.doc_no + ' - ' + mater.product_id.name, 
                                            'account_id': acc_asset,
                                            'debit':0,
                                            'credit':product_price,
                                            'product_id':mater.product_id.id,
                                             
                                           }))
                    journal_line.append((0,0,{
                                'name':line.doc_no + ' - ' + mater.product_id.name, 
                                'account_id': acc_expense,
                                'credit':0,
                                'debit':product_price,
                                'product_id':mater.product_id.id,
                            }))
            value={
                    'journal_id':journal_ids[0],
                    'period_id':period_id.id ,
                    'ref': line.doc_no,
                    'date': date_period,
                    'material_issue_id': line.id,
                    'line_id': journal_line,
                    'doc_type':'good'
                    }
            new_jour_id = self.pool.get('account.move').create(cr,uid,value)
            print 'Phuoc: ',dem, new_jour_id
            dem+=1
        return self.write(cr, uid, ids, {'result':'create_posting_6000028 Done'})   
    
    def delete_issue_1000750(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move_line where move_id in (select id from account_move 
            where material_issue_id in (select id from tpt_material_issue where doc_no in ('1000750/2015'))) 
        '''
        cr.execute(sql)
        sql = '''
            delete from account_move 
            where material_issue_id in (select id from tpt_material_issue where doc_no in ('1000750/2015'))
        '''
        cr.execute(sql)
        sql = '''
            delete from stock_move where issue_id in (select id from tpt_material_issue where doc_no in ('1000750/2015'))
        '''
        cr.execute(sql)
        sql = '''
            delete from tpt_material_issue_line 
            where material_issue_id in (select id from tpt_material_issue where doc_no in ('1000750/2015'))
        '''
        cr.execute(sql)
        sql = '''
            delete from tpt_material_issue where doc_no in ('1000750/2015')
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'delete_issue_1000750 Done'}) 
    
    def update_grn_stockmove_qty_for_may(self, cr, uid, ids, context=None):
        sql = '''
            delete from stock_move where id = 37688
        '''
        cr.execute(sql)
        sql = '''
            delete from stock_inventory_move_rel where move_id = 37688 and inventory_id = 173
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_grn_stockmove_qty_33.34_for_may Done'}) 
    
    def update_SULPHURIC_ACID_for_june(self, cr, uid, ids, context=None):
        sql = '''
            delete from stock_inventory_move_rel where move_id = 37599 and inventory_id = 173
        '''
        cr.execute(sql)
        
        sql = '''
            delete from stock_move where id = 37599
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'update SULPHURIC ACID qty 10.025 for June Done'}) 
    
    def update_PP_HDPE_for_june(self, cr, uid, ids, context=None):
        sql = '''
            delete from stock_inventory_move_rel where inventory_id in (165,166,175,177)
        '''
        cr.execute(sql)
        
        sql = '''
            delete from stock_move where id in (34593, 34811, 39229, 39540)
        '''
        cr.execute(sql)
        
        sql = '''
            delete from stock_inventory where id in (165,166,175,177)
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'update PP/HDPE for June Done'}) 
    
    def delete_account_move_production(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move_line where move_id in (select id from account_move where doc_type = 'product')
        '''
        cr.execute(sql)
        
        sql = '''
            delete from account_move where doc_type = 'product'
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'delete_account_move_production Done'}) 
    
    def delete_account_move_production(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move_line where move_id in (select id from account_move where doc_type = 'product')
        '''
        cr.execute(sql)
        
        sql = '''
            delete from account_move where doc_type = 'product'
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'delete_account_move_production Done'}) 
    
    def create_one_production_one_posting(self, cr, uid, ids, context=None):
        production_obj = self.pool.get('mrp.production')
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        journal_line = []
        credit = 0
        price = 0
        sql = '''
            select id from mrp_production where state = 'done' and id not in (select product_dec from account_move where doc_type = 'product' and product_dec is not null) limit 150
        '''
        cr.execute(sql)
        production_ids = [r[0] for r in cr.fetchall()]
        dem = 1
        if not production_ids:
            self.write(cr, uid, ids, {'result':'create_one_production_one_posting Done'}) 
        for line in production_obj.browse(cr,uid,production_ids):
            sql = '''
                    select id from account_journal
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            date_period = line.date_planned,
            sql = '''
                select id from account_period where '%s' between date_start and date_stop
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            for period_id in period_obj.browse(cr,uid,period_ids):
        
                if line.state=='done':
                    for mat in line.move_lines2:
                        cost = mat.price_unit * mat.product_qty
                        price += cost
                        if cost:
                            if mat.product_id.purchase_acc_id:
                                journal_line.append((0,0,{
                                                'name':mat.product_id.code, 
                                                'account_id': mat.product_id.purchase_acc_id and mat.product_id.purchase_acc_id.id,
                                                'debit':cost,
                                                'credit':0,
                                               }))
                            else:
                                raise osv.except_osv(_('Warning!'),_("Purchase GL Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.code))
                    for act in line.bom_id.activities_line:
                        if act.activities_id.act_acc_id:
                            credit += act.product_cost
                            journal_line.append((0,0,{
                                                    'name':act.activities_id.code, 
                                                    'account_id': act.activities_id.act_acc_id and act.activities_id.act_acc_id.id,
                                                    'debit':act.product_cost or 0,
                                                    'credit':0,
                                                   }))
                        else:
                            raise osv.except_osv(_('Warning!'),_("Activity Account is not configured for Activity '%s'! Please configured it!")%(act.activities_id.code))
                    credit += price
                    if credit:
                        if line.product_id.product_asset_acc_id:
                            journal_line.append((0,0,{
                                                    'name':line.product_id.code, 
                                                    'account_id': line.product_id.product_asset_acc_id and line.product_id.product_asset_acc_id.id,
                                                    'debit': 0,
                                                    'credit':credit ,
                                                   }))
                        else:
                            raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(line.product_id.code))
            value={
                        'journal_id':journal_ids[0],
                        'period_id':period_id.id ,
                        'doc_type':'product',
                        'date': line.date_planned,
                        'line_id': journal_line,
                        'product_dec': line.id,
                    }
            new_jour_id = account_move_obj.create(cr,uid,value)
            print 'Phuoc: ', dem, line.id
            dem += 1
            sql = '''
                update mrp_production set produce_cost = %s where id=%s 
            '''%(credit,line.id)
            cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'create_one_production_one_posting Remaining'}) 
    
    def update_date_between_production_and_stockmove(self, cr, uid, ids, context=None):
        sql = '''
            select production_id from mrp_production_move_ids where production_id is not null
        '''
        cr.execute(sql)
        production_ids = cr.fetchall()
        cr.execute("select id, date_planned from mrp_production where id in %s",(tuple(production_ids),))
        for production in cr.dictfetchall():
            sql = '''
                update stock_move set date = '%s' where id in (select move_id from mrp_production_move_ids where production_id = %s)
            '''%(production['date_planned'], production['id'])
            cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_date_between_production_and_stockmove Done'})  
    
    def update_date_between_freight_and_accountmove(self, cr, uid, ids, context=None):
        sql = '''
            update account_move set date = (select date_invoice from account_invoice where move_id = account_move.id and sup_inv_id is not null) where doc_type = 'freight'
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_date_between_freight_and_accountmove Done'})  
    
    def config_GRN_1155(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('account.move')
        sql = '''
            select id from stock_picking where name = 'VVTi/GRN/00001155'
        '''
        cr.execute(sql)
        num = cr.fetchone()[0]
        if num:
            sql='''
                select id from account_invoice where grn_no = %s
            '''%(num)
            cr.execute(sql)
            inv_id = cr.fetchone()[0]
            invoice_id = invoice_obj.browse(cr, uid, inv_id)
            move_obj.button_cancel(cr, uid, [invoice_id.move_id.id])
            cr.execute(''' delete from account_move_line where move_id = %s''',(invoice_id.move_id.id,))
            cr.execute(''' delete from account_invoice_line where invoice_id = %s''',(invoice_id.id,))
            cr.execute(''' delete from account_invoice where id = %s''',(invoice_id.id,))
            cr.execute(''' delete from account_move where id = %s''',(invoice_id.move_id.id,))
            
            sql = '''
                delete from account_move_line where left(name,17)=(select name from stock_picking where id = %s)
            '''%(num)
            cr.execute(sql)
            sql = '''
                delete from account_move where ref = 'VVTi/GRN/00001155'
            '''
            cr.execute(sql)
            sql='''
                select id from tpt_quanlity_inspection where need_inspec_id in (select id from stock_move where picking_id = %s)
            '''%(num)
            cr.execute(sql)
            inspec_ids = [row[0] for row in cr.fetchall()]
            if inspec_ids:
                for move in inspec_ids:
                    sql='''
                        select id from stock_move where inspec_id = %s
                    '''%(move)
                    cr.execute(sql)
                    move_ids = [row[0] for row in cr.fetchall()]
                    if move_ids:
                        cr.execute('delete from stock_move where id in %s',(tuple(move_ids),))
                cr.execute('delete from tpt_quanlity_inspection where id in %s',(tuple(inspec_ids),))
            cr.execute(''' update stock_picking set invoice_state ='2binvoiced' where id = %s''',(num,))
            picking_obj.action_revert_done(cr, uid, [num], context)
            picking_obj.action_cancel(cr, uid, [num], context)

        
        return self.write(cr, uid, ids, {'result':'config_GRN_1155 Done'})  
    
    def update_SULPHURIC_ACID_2_for_june(self, cr, uid, ids, context=None):
#         sql = '''select * from stock_inventory_move_rel where move_id in (select id from stock_move where product_id = 10749 and product_qty = 6) 
#             and inventory_id in (select id from stock_inventory where name = 'TPT Update Stock Move')
#             '''
#         cr.execute(sql)
        
        sql = '''
            delete from stock_inventory_move_rel where move_id = 37683 and inventory_id = 173
        '''
        cr.execute(sql)
        
        sql = '''
            delete from stock_move where id = 37683
        '''
        cr.execute(sql)
        
        sql = '''
            update tpt_quanlity_inspection set qty_approve = 16.025, remaining_qty = 0 where id = 1558 
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'update SULPHURIC ACID qty 6.00 for June Done'}) 
    
    def update_all_grn_posting(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move where doc_type = 'grn'
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'update all GRN posting Done'}) 
    
    def create_all_grn_posting(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        sql = '''
            select id from stock_picking where type = 'in' and state = 'done' 
                and id not in (select grn_id from account_move where doc_type='grn' and grn_id is not null) limit 200
        '''
        cr.execute(sql)
        picking_ids = [r[0] for r in cr.fetchall()]
        for line in picking_obj.browse(cr,uid,picking_ids):
            debit = 0.0
            credit = 0.0
            journal_line = []
            for move in line.move_lines:
                amount = move.purchase_line_id.price_unit * move.product_qty
                debit += amount - (amount*move.purchase_line_id.discount)/100
            date_period = line.date,
            sql = '''
                select id from account_period where special = False and '%s' between date_start and date_stop
             
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
             
            for period_id in period_obj.browse(cr,uid,period_ids):
                sql_journal = '''
                select id from account_journal
                '''
                cr.execute(sql_journal)
                journal_ids = [r[0] for r in cr.fetchall()]
                journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
                for p in line.move_lines:
                    amount_cer = p.purchase_line_id.price_unit * p.product_qty
                    credit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                    debit = amount_cer - (amount_cer*p.purchase_line_id.discount)/100
                    if not p.product_id.product_asset_acc_id:
                        raise osv.except_osv(_('Warning!'),_('You need to define Product Asset GL Account for this product'))
                    journal_line.append((0,0,{
                        'name':line.name + ' - ' + p.product_id.name, 
                        'account_id': p.product_id.product_asset_acc_id and p.product_id.product_asset_acc_id.id,
                        'partner_id': line.partner_id and line.partner_id.id or False,
                        'credit':0,
                        'debit':debit,
                        'product_id':p.product_id.id,
                    }))
                    
                    if not p.product_id.purchase_acc_id:
                        raise osv.except_osv(_('Warning!'),_('You need to define Purchase GL Account for this product'))
                    journal_line.append((0,0,{
                        'name':line.name + ' - ' + p.product_id.name, 
                        'account_id': p.product_id.purchase_acc_id and p.product_id.purchase_acc_id.id,
                        'partner_id': line.partner_id and line.partner_id.id or False,
                        'credit':credit,
                        'debit':0,
                        'product_id':p.product_id.id,
                    }))
                     
                value={
                    'journal_id':journal.id,
                    'period_id':period_id.id ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type':'grn',
                    'grn_id':line.id,
                    'ref': line.name,
                    }
                new_jour_id = account_move_obj.create(cr,uid,value)
        return self.write(cr, uid, ids, {'result':'Create all GRN posting Done'}) 
tpt_update_stock_move_report()


class tpt_update_inspection_line(osv.osv):
    _name = "tpt.update.inspection.line"
    
    _columns = {
        'name': fields.char('Name'),
        'seq': fields.integer('Sequence'),
        'inspec_id': fields.many2one('tpt.quanlity.inspection', 'Quanlity Inspection'),
        'inspection_id': fields.integer('Quanlity Inspection'),
        'inspec_qty': fields.related('inspec_id','qty', string='Inspection Qty', digits=(16,3)),
        'move_id': fields.many2one('stock.move', 'Stock Move'),
        'stock_move_id': fields.integer('Stock Move'),
        'move_qty': fields.related('move_id','product_qty', string='Move Qty', digits=(16,3)),
        'remove': fields.boolean('Remove'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_name': fields.char('Product Name'),
        'state_inspec': fields.related('inspec_id', 'state', type='selection',selection=[
            ('draft', 'Draft'),('remaining', 'Remaining'),('done', 'Done')
            ], string='State Inspec'),
        'update_id': fields.many2one('tpt.update.stock.move.report', 'Update', ondelete='cascade'),
    }
    
    def bt_remove(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            cr.execute(''' update stock_move set inspec_id = null where id=%s ''',(line.move_id.id,))
        return self.write(cr, uid, ids, {'remove':True})

tpt_update_inspection_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
