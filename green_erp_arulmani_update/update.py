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
                   and (select count(id) from tpt_quanlity_inspection where name=%s)>1
            '''%(line.product_id.id,line.qty,line.name.id)
            cr.execute(sql)
            picking_ids = [r[0] for r in cr.fetchall()]
            if picking_ids:
                inspection_obj.write(cr, uid, [line.id], {'name':picking_ids[0]})
        cr.execute(''' update tpt_quanlity_inspection t set need_inspec_id=(select id from stock_move where picking_id=t.name and product_qty=t.qty and product_id=t.product_id limit 1) where need_inspec_id is null ''')
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
        return self.write(cr, uid, ids, {'result':'TPT fix_posting_issue Remaining'})
    
tpt_update_stock_move_report()

class tpt_update_inspection_line(osv.osv):
    _name = "tpt.update.inspection.line"
    
    _columns = {
        'inspec_id': fields.many2one('tpt.quanlity.inspection', 'Quanlity Inspection'),
        'inspection_id': fields.integer('Quanlity Inspection'),
        'inspec_qty': fields.related('inspec_id','qty', string='Inspection Qty', digits=(16,3)),
        'move_id': fields.many2one('stock.move', 'Stock Move'),
        'stock_move_id': fields.integer('Stock Move'),
        'move_qty': fields.related('move_id','product_qty', string='Move Qty', digits=(16,3)),
        'remove': fields.boolean('Remove'),
        'update_id': fields.many2one('tpt.update.stock.move.report', 'Update', ondelete='cascade'),
    }
    
    def bt_remove(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            cr.execute(''' update stock_move set inspec_id = null where id=%s ''',(line.move_id.id,))
        return self.write(cr, uid, ids, {'remove':True})

tpt_update_inspection_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
