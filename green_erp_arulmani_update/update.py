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
    
    def check_inspec(self, cr, uid, ids, context=None):
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        inspec_ids = inspec_obj.search(cr, uid, [('state','=','done')])
        result = 'Result for check inspection mapping \n'
        for inspec in inspec_obj.browse(cr, uid, inspec_ids):
            sql = '''
                select case when sum(product_qty)!=%s then 0 else 1 end check_map_inspec from stock_move where inspec_id=%s 
            '''%(inspec.qty,inspec.id)
            cr.execute(sql)
            rs = cr.fetchone()[0]
            if not rs:
                result += str(inspec.id)+', '
        return self.write(cr, uid, ids, {'result':result})
    
tpt_update_stock_move_report()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
