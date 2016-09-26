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
import base64
import xlrd
from xlrd import open_workbook,xldate_as_tuple
import os

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
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(tpt_update_stock_move_report, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_update_stock_move_report, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    
    _columns = {
        'result': fields.text('Result', readonly=True ),
        'product_id': fields.many2one('product.product', 'Product'),
        'update_line': fields.one2many('tpt.update.inspection.line','update_id','Line'),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data MRS', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
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
        base = 0.0
        tax_debit_amount = 0.0
        tax_credit_amount = 0.0
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
                ###
                amount_total_tax = (amount_basic + amount_p_f + amount_ed)*(amount_total_tax)
                ###
                line_net = amount_total_tax+amount_fright+amount_ed+amount_p_f+amount_basic+line.aed_id_1
                
                ###
                if line.invoice_id.sup_inv_id and line.invoice_id.type=='in_invoice':
                    if line.fright_fi_type == '2':
                        base = line.fright
                        tax_debit_amount = base*(line.tax_id and line.tax_id.amount/100 or 0)
                        tax_credit_amount = base*(line.tax_credit and line.tax_credit.amount/100 or 0)
#                         tax_tds_amount = base*(line.tds_id_2 and line.tds_id_2.amount/100 or 0)
                    else:
                        base = line.fright*line.quantity
                        tax_debit_amount = base*(line.tax_id and line.tax_id.amount/100 or 0)
                        tax_credit_amount = base*(line.tax_credit and line.tax_credit.amount/100 or 0)
#                         tax_tds_amount = base*(line.tds_id_2 and line.tds_id_2.amount/100 or 0)
                    line_net = base+tax_debit_amount-tax_credit_amount
                ###
                
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
    
    def update_invoice_do_sale_blanket(self, cr, uid, ids, context=None):
        sql = '''
            update account_invoice set partner_id=4968,commercial_partner_id=4968 where id=1200;
            update account_invoice_line set partner_id=4968 where invoice_id=1200;
            
            update account_move set partner_id=4968  where id in (select move_id from account_invoice where id=1200);
            update account_move_line set partner_id=4968 where move_id in (select move_id from account_invoice where id=1200);
            
            update stock_picking set partner_id=4968 where id in (select delivery_order_id from account_invoice where id=1200);
            update stock_move set partner_id=4968 where picking_id in (select delivery_order_id from account_invoice where id=1200);
            
            update account_move set partner_id=4968 where id in (select move_id from account_move_line where name=(select name from stock_picking where id in (select delivery_order_id from account_invoice where id=1200)));
            update account_move_line set partner_id=4968 where name=(select name from stock_picking where id in (select delivery_order_id from account_invoice where id=1200));
            
            update sale_order set partner_id=4968,partner_invoice_id=4968,partner_shipping_id=4968 where id in (select sale_id from stock_picking where id in (select delivery_order_id from account_invoice where id=1200));
            update sale_order_line set order_partner_id=4968 where order_id in (select id from sale_order where id in (select sale_id from stock_picking where id in (select delivery_order_id from account_invoice where id=1200)));
            update tpt_blanket_order set customer_id=4968 where id in (select blanket_id from sale_order where id in (select sale_id from stock_picking where id in (select delivery_order_id from account_invoice where id=1200)));
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_invoice_do_sale_blanket Done'})

    def config_GRN_2183(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('account.move')
        sql = '''
            select id from stock_picking where name = 'VVTi/GRN/00002183'
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
                delete from account_move where id in (select move_id from account_move_line where left(name,17)=(select name from stock_picking where id =%s))
            '''%(num)
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

        
        return self.write(cr, uid, ids, {'result':'config_GRN_2183 Done'})    
    
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
            select id from tpt_material_issue where state = 'done' and id not in (select material_issue_id from account_move where doc_type='good' and material_issue_id is not null) 
            limit 500
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
                select id from account_period where '%s' between date_start and date_stop and special is False
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
             
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
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
                    'period_id':period_ids[0] ,
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
    
    def update_invoice_do_sale_blanket(self, cr, uid, ids, context=None):
        sql = '''
            update account_invoice set partner_id=4968,commercial_partner_id=4968 where id=1200;
            update account_invoice_line set partner_id=4968 where invoice_id=1200;
            
            update account_move set partner_id=4968  where id in (select move_id from account_invoice where id=1200);
            update account_move_line set partner_id=4968 where move_id in (select move_id from account_invoice where id=1200);
            
            update stock_picking set partner_id=4968 where id in (select delivery_order_id from account_invoice where id=1200);
            update stock_move set partner_id=4968 where picking_id in (select delivery_order_id from account_invoice where id=1200);
            
            update account_move set partner_id=4968 where id in (select move_id from account_move_line where name=(select name from stock_picking where id in (select delivery_order_id from account_invoice where id=1200)));
            update account_move_line set partner_id=4968 where name=(select name from stock_picking where id in (select delivery_order_id from account_invoice where id=1200));
            
            update sale_order set partner_id=4968,partner_invoice_id=4968,partner_shipping_id=4968 where id in (select sale_id from stock_picking where id in (select delivery_order_id from account_invoice where id=1200));
            update sale_order_line set order_partner_id=4968 where order_id in (select id from sale_order where id in (select sale_id from stock_picking where id in (select delivery_order_id from account_invoice where id=1200)));
            update tpt_blanket_order set customer_id=4968 where id in (select blanket_id from sale_order where id in (select sale_id from stock_picking where id in (select delivery_order_id from account_invoice where id=1200)));
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update_invoice_do_sale_blanket Done'})
    
    def config_GRN_2183(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('account.move')
        sql = '''
            select id from stock_picking where name = 'VVTi/GRN/00002183'
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
                delete from account_move where ref = 'VVTi/GRN/00002183'
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

        
        return self.write(cr, uid, ids, {'result':'config_GRN_2183 Done'})    
    
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
 
    def uom_change_list16th(self, cr, uid, ids, context=None):
        sql = '''
            update purchase_order_line set product_uom=16 where order_id=729 and line_no in (16,17,18,19,20,21,22);
            update purchase_order_line set product_uom=21 where order_id=729 and line_no in (28,29,30,31);
            
            update tpt_purchase_product set uom_po_id=16 where pur_product_id=833
                and description in ('SHUTTERING UPTO 5M HEIGHT',
                                    '-SHUTTERING FROM 5M TO 10M HEIGHT',
                                    'SHUTTERING FROM 10M TO15 M HEIGHT',
                                    'SHUTTERING FROM 15M TO 20M HEIGHT',
                                    'SHUTTERING FROM 20M TO 25M HEIGHT',
                                    'CIRCULAR SHUTTERING UPTO 5M HEIGHT',
                                    'CIRCUL SHUTTERING FROM 5M TO 10M HEIGHT');
            update tpt_purchase_product set uom_po_id=21 where pur_product_id=833
                and description in ('BRICK WORK FROM 5M TO 10M HEIGHT',
                                    'BRICK WORK FROM 10M TO 15M HEIGHT',
                                    'BRICK WORK FROM 15M TO 20M HEIGHT',
                                    'BRICK WORK FROM 20M TO 25M HEIGHT');
                                    
            update tpt_rfq_line set uom_id=16 where rfq_id=725
                and description in ('SHUTTERING UPTO 5M HEIGHT',
                                    '-SHUTTERING FROM 5M TO 10M HEIGHT',
                                    'SHUTTERING FROM 10M TO15 M HEIGHT',
                                    'SHUTTERING FROM 15M TO 20M HEIGHT',
                                    'SHUTTERING FROM 20M TO 25M HEIGHT',
                                    'CIRCULAR SHUTTERING UPTO 5M HEIGHT',
                                    'CIRCUL SHUTTERING FROM 5M TO 10M HEIGHT');
            update tpt_rfq_line set uom_id=21 where rfq_id=725
                and description in ('BRICK WORK FROM 5M TO 10M HEIGHT',
                                    'BRICK WORK FROM 10M TO 15M HEIGHT',
                                    'BRICK WORK FROM 15M TO 20M HEIGHT',
                                    'BRICK WORK FROM 20M TO 25M HEIGHT');
                                    
            update tpt_purchase_quotation_line set uom_id=16 where purchase_quotation_id=930
                and description in ('SHUTTERING UPTO 5M HEIGHT',
                                    '-SHUTTERING FROM 5M TO 10M HEIGHT',
                                    'SHUTTERING FROM 10M TO15 M HEIGHT',
                                    'SHUTTERING FROM 15M TO 20M HEIGHT',
                                    'SHUTTERING FROM 20M TO 25M HEIGHT',
                                    'CIRCULAR SHUTTERING UPTO 5M HEIGHT',
                                    'CIRCUL SHUTTERING FROM 5M TO 10M HEIGHT');
            update tpt_purchase_quotation_line set uom_id=21 where purchase_quotation_id=930
                and description in ('BRICK WORK FROM 5M TO 10M HEIGHT',
                                    'BRICK WORK FROM 10M TO 15M HEIGHT',
                                    'BRICK WORK FROM 15M TO 20M HEIGHT',
                                    'BRICK WORK FROM 20M TO 25M HEIGHT');
        '''
        cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'uom_change_list16th Done'})   
    
    
    def update_price_unit_for_production_COAL(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
#         inout_obj = self.pool.get('stock.inward.outward.report')
#         inout_id = inout_obj.create(cr, uid, {'product_id':10756,'date_from':'2015-01-01','date_to':'2015-12-31'})
#         context.update({'update_price_unit_for_production_COAL':True})
#         inout_val = inout_obj.print_report(cr, uid, [inout_id], context)
#         print inout_val
        
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
                select id from account_period where '%s' between date_start and date_stop and special is False
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
        
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
                        'period_id':period_ids[0] ,
                        'doc_type':'product',
                        'date': line.date_planned,
                        'line_id': journal_line,
                        'product_dec': line.id,
                        'ref': line.name,
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
        move_ids = self.pool.get('stock.move').search(cr, uid, [('production_id','!=',False)])
        for line in move_ids:
            line_id = self.pool.get('stock.move').browse(cr, uid, line)
            if line_id.production_id:
                self.pool.get('stock.move').write(cr, 1,[line_id.id],{'date':line_id.production_id.date_planned})
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
                and id not in (select grn_id from account_move where doc_type='grn' and grn_id is not null) limit 500
        '''
        cr.execute(sql)
        picking_ids = [r[0] for r in cr.fetchall()]
        if not picking_ids:
            return self.write(cr, uid, ids, {'result':'Create all GRN posting Done'}) 
        for line in picking_obj.browse(cr,uid,picking_ids):
            debit = 0.0
            credit = 0.0
            journal_line = []
            for move in line.move_lines:
                amount = move.purchase_line_id.price_unit * move.product_qty
                debit += amount - (amount*move.purchase_line_id.discount)/100
            date_period = line.date,
            sql = '''
                select id from account_period where special = False and '%s' between date_start and date_stop and special is False
             
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
             
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
                'period_id':period_ids[0] ,
                'date': date_period,
                'line_id': journal_line,
                'doc_type':'grn',
                'grn_id':line.id,
                'ref': line.name,
                }
            new_jour_id = account_move_obj.create(cr,uid,value)
        return self.write(cr, uid, ids, {'result':'Create all GRN posting Remaining'}) 

    def update_all_do_posting(self, cr, uid, ids, context=None):
        sql = '''
            delete from account_move where doc_type = 'do'
        '''
        cr.execute(sql)
        
        return self.write(cr, uid, ids, {'result':'update all DO posting Done'}) 
    def get_pro_account_id(self,cr,uid,name,channel):
        account = False
        account_obj = self.pool.get('account.account')
        if name and channel:
            product_name = name.strip()
            dis_channel = channel.strip()
            account_ids = []
            if dis_channel in ['VVTi Domestic','VVTI Domestic']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810001')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810031')])
            if dis_channel in ['VVTi Direct Export','VVTI Direct Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810003')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810032')])
            if dis_channel in ['VVTi Indirect Export','VVTI Indirect Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810004')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810033')])
            if account_ids:
                account = account_ids[0]
        return account
    def create_all_do_posting(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        sql = '''
            select id from stock_picking where type = 'out' and state = 'done' 
                
        ''' #and name in (select ref from account_move where doc_type='do')
        cr.execute(sql)
        picking_ids = [r[0] for r in cr.fetchall()]
        if not picking_ids:
            return self.write(cr, uid, ids, {'result':'Create all DO posting Done'}) 
        for line in picking_obj.browse(cr,uid,picking_ids):
            debit = 0.0
            credit = 0.0
            journal_line = []
            #===================================================================
            # for move in line.move_lines:
            #     amount = move.purchase_line_id.price_unit * move.product_qty
            #     debit += amount - (amount*move.purchase_line_id.discount)/100
            #===================================================================
            dis_channel = line.sale_id and line.sale_id.distribution_channel and line.sale_id.distribution_channel.name or False
            date_period = line.date
            account = False
            asset_id = False
            sql = '''
                select id from account_period where special = False and '%s' between date_start and date_stop and special is False
             
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
             
            sql_journal = '''
            select id from account_journal
            '''
            cr.execute(sql_journal)
            journal_ids = [r[0] for r in cr.fetchall()]
            journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
            for p in line.move_lines:
                if p.prodlot_id:
                    sale_id = p.sale_line_id and p.sale_line_id.order_id.id or False 
                    used_qty = p.product_qty or 0
                    if sale_id:
                        sql = '''
                                select id from tpt_batch_allotment where sale_order_id = %s and state='confirm'
                            '''%(sale_id) #TPT-By BalamuruganPurushothaman ON 29/07/2015 - TO TAKE CONFIRMED "BATCH ALLOTMENT" ONLY - SQL state='confirm is appended'
                        cr.execute(sql)
                            #print "TEST1 : %s"%sql
                        allot_ids = cr.dictfetchone()
                            #===================================================
                            # if allot_ids:
                            #     allot_id = allot_ids['id']
                            #     sql = '''
                            #     select id from tpt_batch_allotment_line where sys_batch = %s and batch_allotment_id = %s
                            #     '''%(p.prodlot_id.id,allot_id)
                            #     cr.execute(sql)
                            #     print 'TEST: %s'%sql
                            #     allot_line_id = cr.dictfetchone()['id']
                            #     line_id = self.pool.get('tpt.batch.allotment.line').browse(cr, uid, allot_line_id)
                            #     used_qty += line_id.used_qty
                            #     sql = '''
                            #         update tpt_batch_allotment_line set product_uom_qty = %s where id = %s
                            #     '''%(used_qty,allot_line_id)
                            #     cr.execute(sql)
                            #     if line_id.product_uom_qty == line_id.used_qty:
                            #         sql = '''
                            #             update tpt_batch_allotment_line set is_deliver = 't' where id = %s
                            #         '''%(allot_line_id)
                            #         cr.execute(sql)
                            #===================================================
                    
                    #TPT START By BalamuruganPurushothaman ON 28/07/2015 - TO SET COST PRICE OF FINISHED PRODUCT IN JOURNAL POSTING INSTEAD OF SALES PROCE WHILE DO CONFIRM PROCESS
                    #debit += p.sale_line_id and p.sale_line_id.price_unit * p.product_qty or 0  ##TPT COMMENTED
                product = self.pool.get('product.product').browse(cr, uid, p.product_id.id)
                debit += product.standard_price and product.standard_price * p.product_qty or 0
                    #TPT END
                    
                    #product_name = p.product_id.name    # TPT - COMMENTED By BalamuruganPurushothaman ON 20/06/2015 
                product_name = p.product_id.default_code # TPT - Added By BalamuruganPurushothaman ON 20/06/2015 fto get GL code with respect to Product Code
                product_id = p.product_id.id
                account = self.get_pro_account_id(cr,uid,product_name,dis_channel)
                if not account:
                    if p.product_id.product_cose_acc_id:
                        account = p.product_id.product_cose_acc_id.id
                    else: 
                        raise osv.except_osv(_('Warning!'),_('Product Cost of Goods Sold Account is not configured! Please configured it!'))
                     
                if p.product_id.product_asset_acc_id:
                    asset_id = p.product_id.product_asset_acc_id.id
                else:
                    raise osv.except_osv(_('Warning!'),_('Product Asset Account is not configured! Please configured it!'))
            if account is False:
                if p.product_id.product_cose_acc_id:
                    account = p.product_id.product_cose_acc_id.id
                else: 
                    raise osv.except_osv(_('Warning!'),_('Product Cost of Goods Sold Account is not configured! Please configured it-2!'))
            if asset_id is False:
                asset_id = p.product_id.product_asset_acc_id.id              
            if asset_id is False:
                raise osv.except_osv(_('Warning!'),_('Asset ID is False'))
            
            journal_line.append((0,0,{
                            'name':line.name, 
                            'account_id': account,
                            'partner_id': line.partner_id and line.partner_id.id,
                            'credit':0,
                            'debit':debit,
                            'product_id':product_id,
                        }))
                 
            journal_line.append((0,0,{
                    'name':line.name, 
                    'account_id': asset_id,
                    'partner_id': line.partner_id and line.partner_id.id,
                    'credit':debit,
                    'debit':0,
                    'product_id':product_id,
                    }))
                      
            value={
                    'journal_id':journal.id,
                    'period_id':period_ids[0] ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type':'do',
                    'ref': line.name,
                    'do_id':line.id,
                    }
            new_jour_id = account_move_obj.create(cr,uid,value)
        return self.write(cr, uid, ids, {'result':'Create all GRN posting Remaining'}) 
    
    def update_gate_out_pass_grn(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [('gate_out_id','!=',False)])
        for move in move_obj.browse(cr, uid, move_ids): 
            sql = '''
                update stock_picking set gate_out_id = %s, invoice_state = '2binvoiced' where id in (select picking_id from stock_move where id = %s)
                        and id not in (select grn_no from account_invoice where grn_no is not null)
            '''%(move.gate_out_id.id,move.id)
            cr.execute(sql)
        return self.write(cr, uid, ids, {'result':'update Gate out pass GRN Done'}) 
    
    def update_internal_move_1795(self, cr, uid, ids, context=None):
        pick_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [('picking_id','=',1795)])
        if move_ids:
#             pick_obj.action_cancel(cr, uid, [1795], context)
            move_obj.action_cancel(cr, uid, move_ids, context)
            move_obj.unlink(cr,uid,move_ids)
#             pick_obj.unlink(cr,uid,[1795])
            cr.execute(''' delete from stock_picking where id= 1795 ''')
        return self.write(cr, uid, ids, {'result':'update internal move 1795 Done'}) 
    
    def delete_dup_issue(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        account_obj = self.pool.get('account.move')
        for issue in ['1003004/2015','1000006/2015','1000000/2015','1002998/2015',
                      '1000860/2015','1000858/2015']:
            issue_ids = self.pool.get('tpt.material.issue').search(cr, uid, [('doc_no','=',issue)])
            for issue_id in issue_ids:
                move_ids = move_obj.search(cr, uid, [('issue_id','=',issue_id)])
                if move_ids:
                    move_obj.action_cancel(cr, uid, move_ids, context)
                    move_obj.unlink(cr,uid,move_ids)
                account_ids = account_obj.search(cr, uid, [('material_issue_id','=',issue_id)])
                if account_ids:
                    account_obj.button_cancel(cr, uid, account_ids)
                    cr.execute(''' delete from account_move where id = %s ''',(account_ids[0],))
                cr.execute(''' delete from tpt_material_issue where id = %s ''',(issue_id,))
        return self.write(cr, uid, ids, {'result':'delete duplicate issue done'}) 
    
    def update_issue_date_and_03092015(self, cr, uid, ids, context=None):
        cr.execute(''' update tpt_material_issue set date_expec = '2015-07-15' where doc_no = '1002763/2015' ''')
        cr.execute(''' update tpt_material_issue set date_expec = '2015-06-04' where doc_no = '1001314/2015' ''')
        cr.execute(''' update tpt_material_issue set date_expec = '2015-07-21' where doc_no = '1002994/2015' ''')
        
        return self.write(cr, uid, ids, {'result':'update date issue 03092015 file: Duplicate to delete done'}) 
    
    def delete_material_request_6000167(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        account_obj = self.pool.get('account.move')
        request_ids = self.pool.get('tpt.material.request').search(cr, uid, [('name','=','6000167/2015')])
        if request_ids:
            issue_ids = self.pool.get('tpt.material.issue').search(cr, uid, [('name','=',request_ids[0])])
            for issue_id in issue_ids:
                move_ids = move_obj.search(cr, uid, [('issue_id','=',issue_id)])
                if move_ids:
                    move_obj.action_cancel(cr, uid, move_ids, context)
                    move_obj.unlink(cr,uid,move_ids)
                account_ids = account_obj.search(cr, uid, [('material_issue_id','=',issue_id)])
                if account_ids:
                    account_obj.button_cancel(cr, uid, account_ids)
                    cr.execute(''' delete from account_move where id = %s ''',(account_ids[0],))
                cr.execute(''' delete from tpt_material_issue where id = %s ''',(issue_id,))
            cr.execute(''' delete from tpt_material_request where id = %s ''',(request_ids[0],))
        return self.write(cr, uid, ids, {'result':'delete MRS 6000167/2015 done'}) 
    
    def update_date_mrs_issue(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            request_obj = self.pool.get('tpt.material.request')
            issue_obj = self.pool.get('tpt.material.issue')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    mrs_name = sh.cell(row, 0).value
                    request_ids = request_obj.search(cr, uid, [('name','=',mrs_name)])
                    up_date = sh.cell(row, 1).value
                    if up_date:
                        date_update = up_date[6:10] + '-' + up_date[3:5] + '-'+ up_date[:2]
                    else:
                        date_update = False
                    if request_ids:
                        cr.execute(''' update tpt_material_request set date_request = %s, date_expec = %s where id in %s ''',(date_update,date_update,tuple(request_ids),))
                        issue_ids = issue_obj.search(cr, uid, [('name','=',request_ids[0])])
                        if issue_ids:
                            cr.execute(''' update tpt_material_issue set date_request = %s, date_expec = %s where id in %s ''',(date_update,date_update,tuple(issue_ids),))
                    dem += 1
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'result':'update date MRS and Issue Negative stock details file done'})
    
    def update_date_grn_negative_stock_file(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            picking_obj = self.pool.get('stock.picking')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    grn_name = sh.cell(row, 0).value
                    grn_ids = picking_obj.search(cr, uid, [('name','=',grn_name)])
                    up_date = sh.cell(row, 1).value
                    if up_date:
                        date_update = up_date[6:10] + '-' + up_date[3:5] + '-'+ up_date[:2]
                    else:
                        date_update = False
                    if grn_ids:
                        cr.execute(''' update stock_picking set date = %s where id in %s ''',(date_update,tuple(grn_ids),))
                    dem += 1
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'result':'update date grn negative stock file done'})
    
    def goods_auto_posting(self, cr, uid, ids, context=None):
        #=======================================================================
        # move_obj = self.pool.get('account.move')
        # move_ids = move_obj.search(cr, uid, [('state','=','draft'),('doc_type','=','good')])
        # for move_id in move_ids:           
        #     move_obj.button_validate(cr,uid, [move_id], context)
        # return self.write(cr, uid, ids, {'result':'Goods Issue Auto Posting Done'})  
        #=======================================================================
        print "test"
        sql = '''
            select name, prd_id, actual_val, qty_up  from vw_ins
        '''
        cr.execute(sql)
        #seq = 1
        for line in  cr.dictfetchall():
            #print seq, line['name'], line['actual_val'],line['qty_up']
            sql = '''
            select count(aml.id) from account_move_line aml
            inner join account_move am on aml.move_id=am.id
            where aml.ref='%s'
            and aml.product_id=%s and am.doc_type='grn' and aml.credit>0
            '''%(line['name'], line['prd_id'])
            cr.execute(sql)
            temp = cr.fetchone()[0]
            if temp>1:
                print "asdf: ",line['name']
            else:
                sql = '''
                update account_move_line set credit=%s where id=(select aml.id from account_move_line aml
                inner join account_move am on aml.move_id=am.id
                where aml.ref='%s'
                and aml.product_id=%s and am.doc_type='grn' and aml.credit>0)
                '''%(line['actual_val'], line['name'], line['prd_id'])
                cr.execute(sql)
                
                sql = '''
                update account_move_line set debit=%s where id=(select aml.id from account_move_line aml
                inner join account_move am on aml.move_id=am.id
                where aml.ref='%s'
                and aml.product_id=%s and am.doc_type='grn' and aml.debit>0)
                '''%(line['actual_val'], line['name'], line['prd_id'])
                cr.execute(sql)

                #print seq, line['name'], line['actual_val']    
            #seq += 1
        return self.write(cr, uid, ids, {'result':'GRN Done'})  
    def prd_auto_posting(self, cr, uid, ids, context=None):
        #=======================================================================
        # move_obj = self.pool.get('account.move')
        # move_ids = move_obj.search(cr, uid, [('state','=','draft'),('doc_type','=','product')])
        # for move_id in move_ids:           
        #     move_obj.button_validate(cr,uid, [move_id], context)
        # return self.write(cr, uid, ids, {'result':'Production Auto Posting Done'})  
        #=======================================================================
        #=======================================================================
        # acc_obj = self.pool.get('account.invoice')
        # acc_line_obj = self.pool.get('account.invoice.line')
        # acc_ids = acc_obj.search(cr, uid, [('doc_type','=','supplier_invoice')])
        # invoice_id = acc_obj.browse(cr, uid, acc_ids)
        # #print len(acc_ids)
        # #i = 1
        # for inv_id in invoice_id:  
        #     i = 1
        #     for acc_line_id in inv_id.invoice_line:  
        #         vals = {'line_no': i}
        #         acc_line_obj.write(cr, uid, [acc_line_id.id], vals)
        #         i+=1
        # return True
        #=======================================================================
        acc_obj = self.pool.get('account.invoice')
        acc_line_obj = self.pool.get('account.invoice.line')
        inv_tax_obj = self.pool.get('account.invoice.line.tax')
        acc_ids = acc_obj.search(cr, uid, [('doc_type','=','supplier_invoice')])
        invoice_id = acc_obj.browse(cr, uid, acc_ids)
        #=======================================================================
        # sql = '''
        # select ail.id from account_invoice_line ail
        #  inner join account_invoice ai on ail.invoice_id=ai.id
        #  where ai.doc_type in ('supplier_invoice_without', 'freight_invoice')             
        #  and ail.id not in (
        # select invoice_line_id from account_invoice_line_tax where invoice_line_id in (
        #  select ail.id from account_invoice_line ail
        #  inner join account_invoice ai on ail.invoice_id=ai.id
        #  where ai.doc_type in ('supplier_invoice_without', 'freight_invoice')   
        #  )
        # )
        # '''
        #=======================================================================
        sql = '''
        select ail.id from account_invoice_line ail
         inner join account_invoice ai on ail.invoice_id=ai.id
         where ai.doc_type='freight_invoice'          
         and ail.id not in (
        select invoice_line_id from account_invoice_line_tax where invoice_line_id in (
         select ail.id from account_invoice_line ail
         inner join account_invoice ai on ail.invoice_id=ai.id
         where ai.doc_type='freight_invoice'
         )
        )
        '''
        cr.execute(sql)
        inv_ids = [r[0] for r in cr.fetchall()]
        for line in acc_line_obj.browse(cr, uid, inv_ids):
            print line.tax_id
            if line.tax_id:
                sql = '''
                insert into account_invoice_line_tax (invoice_line_id, tax_id) values (%s, %s)
                '''%(line.id, line.tax_id and line.tax_id.id)
                cr.execute(sql)
        return True
    def adjust_issue_posting_raw(self, cr, uid, ids, context=None):  
        sql = '''
        select sp.name, to_char(sm.date, 'DD-MM-YYYY') as date, tqi.qty_approve, sm.price_unit, coalesce(tqi.qty_approve*sm.price_unit, 0.0) as amt,
        pp.id as product_id, pp.default_code, pp.name_template, 
        
        (select code from res_country where id=rp.country_id) as country,
        (select code from res_country_state where id=rp.state_id) as state
        
        from stock_move sm
        inner join tpt_quanlity_inspection tqi on sm.id=tqi.need_inspec_id
        inner join stock_picking sp on tqi.name=sp.id
        inner join product_product pp on sm.product_id=pp.id
        
        inner join res_partner rp on sp.partner_id=rp.id

        where --sm.product_id=10721 
        pp.cate_name='raw'
        and sm.date between '2015-04-01' and '2016-08-30'
        order by pp.name_template, sm.date
        '''
        cr.execute(sql)
        str1 = ''
        for line in cr.dictfetchall():
            sql = '''
            select case when sum(aml.debit) is null then 0 else sum(aml.debit) end as debit from account_move_line aml
            inner join account_move am on aml.move_id=am.id
            where am.doc_type='grn' and am.state='posted' and am.date between '2015-04-01' and '2016-08-30' and aml.debit>0
            and aml.ref='%s' and aml.account_id=(select product_asset_acc_id from product_product where id=%s)


            '''%(line['name'], line['product_id'])
            cr.execute(sql)
            #print sql
            debit = 0.0
            debit = cr.fetchone()
            if debit:
                debit = debit[0]
            if round(debit, 2) != round(line['amt'], 2):
                temp = round(round(debit, 2)-round(line['amt'], 2))
                if round(debit, 2)>0:
                    str1 += str(line['name_template']) +', '+ str(line['date']) +', '+str(line['name']) \
                    +' , grn:  '+ str(line['amt']) +', gl: '+ str(debit) + ', '+ line['country'] + ', '+ line['state'] +', diff:'+str(temp)+'\n'
        return self.write(cr, uid, ids, {'result':str1}) 
    def adjust_issue_posting_raw1(self, cr, uid, ids, context=None):  
        prod_obj = self.pool.get('product.product')
        sql = '''
        select pp.id as prod_id, pp.name_template, mi.doc_no, sm.product_qty, sm.price_unit, round(sm.product_qty*sm.price_unit,2) as val, 
        pp.product_asset_acc_id
        from stock_move sm
        inner join tpt_material_issue mi on sm.issue_id=mi.id
        inner join product_product pp on sm.product_id=pp.id
        where --sm.product_id=10759 and 
        pp.cate_name='raw' and sm.location_id=15 and sm.state='done' and 
        sm.date >= '2015-04-01' order by mi.doc_no
        '''
        cr.execute(sql)
        for line in cr.dictfetchall():
            #print line['prod_id'], line['doc_no']
            sql = '''
            select count(*) from account_move_line where ref='%s'
            and product_id=%s and credit>0 and account_id in (%s) and doc_type='good'
            '''%(line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
            cr.execute(sql)
            count = cr.fetchone()[0]
            if count==1:
                #===============================================================
                # print line['name_template'], line['doc_no'] 
                # sql = '''
                # select credit from account_move_line where ref='%s'
                # and product_id=%s and credit>0 and account_id in (%s) and doc_type='good'
                # '''%(line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
                # cr.execute(sql)
                # temp = cr.fetchone()
                # if temp:
                #     temp = temp[0]
                #     if round(temp, 2)!=round(line['val'], 2):
                #===============================================================
                #Move the following to if loop
                prod_ids = prod_obj.browse(cr, uid, line['prod_id'])
                expense = prod_ids.property_account_expense
                sql = '''
                update account_move_line set credit=%s where ref='%s'
                and product_id=%s and credit>0 and account_id= %s and doc_type='good'
                '''%(line['val'], line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
                cr.execute(sql)
                  
                sql = '''
                update account_move_line set debit=%s where ref='%s'
                and product_id=%s and debit>0 and account_id = %s and doc_type='good'
                '''%(line['val'], line['doc_no'], line['prod_id'],  expense.id)
                cr.execute(sql)
                #end
                print "---IM UPDATED----", line['name_template'], line['doc_no'] 
            #end count if   
        return self.write(cr, uid, ids, {'result':'adjust_issue_posting_raw'})  
    def adjust_issue_posting_spares_2015(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        sql = '''
        select pp.id as prod_id, pp.name_template, mi.doc_no, sm.product_qty, sm.price_unit, round(sm.product_qty*sm.price_unit,2) as val, 
        pp.product_asset_acc_id
        from stock_move sm
        inner join tpt_material_issue mi on sm.issue_id=mi.id
        inner join product_product pp on sm.product_id=pp.id
        where --sm.product_id=10759 and 
        pp.cate_name='spares' and sm.location_id=14 and sm.state='done' and 
        sm.date between '2015-04-01' and '2015-12-31' order by mi.doc_no
        '''
        cr.execute(sql)
        for line in cr.dictfetchall():
            #print line['prod_id'], line['doc_no']
            sql = '''
            select count(*) from account_move_line where ref='%s'
            and product_id=%s and credit>0 and account_id in (%s) and doc_type='good'
            '''%(line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
            cr.execute(sql)
            count = cr.fetchone()[0]
            if count==1:
                #===============================================================
                # print line['name_template'], line['doc_no'] 
                # sql = '''
                # select credit from account_move_line where ref='%s'
                # and product_id=%s and credit>0 and account_id in (%s) and doc_type='good'
                # '''%(line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
                # cr.execute(sql)
                # temp = cr.fetchone()
                # if temp:
                #     temp = temp[0]
                #     if round(temp, 2)!=round(line['val'], 2):
                #===============================================================
                #Move the following to if loop
                prod_ids = prod_obj.browse(cr, uid, line['prod_id'])
                expense = prod_ids.property_account_expense
                sql = '''
                update account_move_line set credit=%s where ref='%s'
                and product_id=%s and credit>0 and account_id= %s and doc_type='good'
                '''%(line['val'], line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
                cr.execute(sql)
                 
                sql = '''
                update account_move_line set debit=%s where ref='%s'
                and product_id=%s and debit>0 and account_id = %s and doc_type='good'
                '''%(line['val'], line['doc_no'], line['prod_id'],  expense.id)
                cr.execute(sql)
                #end
                #print "---IM UPDATED----", line['name_template'], line['doc_no'], line['val'] 
            #end count if   
        return self.write(cr, uid, ids, {'result':'Goods Issue Posting Done'})  
    def adjust_issue_posting_spares_2016(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        sql = '''
        select pp.id as prod_id, pp.name_template, mi.doc_no, sm.product_qty, sm.price_unit, round(sm.product_qty*sm.price_unit,2) as val, 
        pp.product_asset_acc_id
        from stock_move sm
        inner join tpt_material_issue mi on sm.issue_id=mi.id
        inner join product_product pp on sm.product_id=pp.id
        where --sm.product_id=10759 and 
        pp.cate_name='spares' and sm.location_id=14 and sm.state='done' and 
        sm.date >= '2016-01-01' order by mi.doc_no
        '''
        cr.execute(sql)
        for line in cr.dictfetchall():
            #print line['prod_id'], line['doc_no']
            sql = '''
            select count(*) from account_move_line where ref='%s'
            and product_id=%s and credit>0 and account_id in (%s) and doc_type='good'
            '''%(line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
            cr.execute(sql)
            count = cr.fetchone()[0]
            if count==1:
                #print line['name_template'], line['doc_no'] 
                sql = '''
                select credit from account_move_line where ref='%s'
                and product_id=%s and credit>0 and account_id in (%s) and doc_type='good'
                '''%(line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
                cr.execute(sql)
                temp = cr.fetchone()
                if temp:
                    temp = temp[0]
                    if line['val']>0 and round(temp, 2)!=round(line['val'], 2):
                        print "---IM UPDATED----", line['name_template'], line['doc_no'], line['val']
                #Move the following to if loop
                        prod_ids = prod_obj.browse(cr, uid, line['prod_id'])
                        expense = prod_ids.property_account_expense
                        sql = '''
                        update account_move_line set credit=%s where ref='%s'
                        and product_id=%s and credit>0 and account_id= %s and doc_type='good'
                        '''%(line['val'], line['doc_no'], line['prod_id'], line['product_asset_acc_id'])
                        cr.execute(sql)
                          
                        sql = '''
                        update account_move_line set debit=%s where ref='%s'
                        and product_id=%s and debit>0 and account_id = %s and doc_type='good'
                        '''%(line['val'], line['doc_no'], line['prod_id'],  expense.id)
                        cr.execute(sql)
                #end
                #
            #end count if   
        return self.write(cr, uid, ids, {'result':'Goods Issue Posting Done'})  
    def config_GRN_3451_3883(self, cr, uid, ids, context=None):
         
        aa_obj = self.pool.get('account.account')   
        aa_ids = aa_obj.search(cr, uid, [])
        aa = aa_obj.browse(cr, uid, aa_ids)
        file1 = open("/home/dev127/Desktop/acc_data.txt", "r+")
        for acc in aa:
            if acc.debit==0.0 and acc.credit==0.0:
                pass 
            elif acc.type=='view':
                pass
            else:
                file1.write(str(acc.id) +' '+ acc.code+' '+str(acc.debit)+' '+str(acc.credit)+'\n')
        file1.close  
        
        #----------------------------- jl_obj = self.pool.get('account.voucher')
        #-------------------------------------------------- debit = credit = 0.0
        #------------------------------------------------------------- sql = '''
        # select id from account_voucher --where id between 1 and 1000 order by id
        #------------------------------------------------------------------- '''
        #------------------------------------------------------- cr.execute(sql)
        #------------------------------- inv_ids = [r[0] for r in cr.fetchall()]
        #----------------------------------------------------------------- a = 0
        #----------------------- for voucher in jl_obj.browse(cr, uid, inv_ids):
            # #===================================================================
            #---------------------------------- # for dr in voucher.line_dr_ids:
            #------------------------------------------ #     debit += dr.amount
            #---------------------------------- # for cr in voucher.line_cr_ids:
            #----------------------------------------- #     credit += cr.amount
            # #===================================================================
            # sql = '''select case when sum(amount)>0 then sum(amount) else 0 end as sum from account_voucher_line where type='cr' and voucher_id=%s
            #-------------------------------------------------- '''%(voucher.id)
            #--------------------------------------------------- cr.execute(sql)
            #----------------------------------------------- res = cr.fetchone()
            #----------------------------------------------------------- if res:
                #----------------------------------------------- credit = res[0]
            #---------------- if float(credit)!=float(voucher.tpt_amount_total):
                #----------------------------------------------------- sql = '''
                #---- update account_voucher set tpt_amount_total=%s where id=%s
                #-------------------------------------- '''%(credit, voucher.id)
                #---------------------------------------------------- #print sql
                #---------------------------------------------------------- a+=1
        #--------------------------------------------------------------- print a
            #cr.execute(sql)
            
            #jl_obj.write(cr, uid, [voucher.id], {'tpt_amount_total':credit or 0})  
        #return True   
    #===========================================================================
    # def config_GRN_3451_3883(self, cr, uid, ids, context=None):
    #     acc_line_obj = self.pool.get('account.invoice.line')
    #     sql = '''
    #     select ail.id from account_invoice_line ail
    #          inner join account_invoice ai on ail.invoice_id=ai.id
    #          where ai.type='in_invoice'
    #     '''
    #     cr.execute(sql)
    #     inv_ids = [r[0] for r in cr.fetchall()]
    #     for move_id in acc_line_obj.browse(cr, uid, inv_ids):
    #         #print move_id.id or 0.00
    #         sql = '''
    #         update account_invoice_line set tpt_tax_amt=%s where id=%s
    #         '''%(move_id.wform_tax_amt, move_id.id)
    #         cr.execute(sql)
    #         #print sql
    #     return self.write(cr, uid, ids, {'result':'Tax Amount Corrections Done'})   
    #===========================================================================
    
    #===========================================================================
    # def config_GRN_3451_3883(self, cr, uid, ids, context=None):
    #     move_obj = self.pool.get('account.move')
    #     partner_obj = self.pool.get('res.partner')
    #     #=======================================================================
    #     # partner_ids = partner_obj.search(cr, uid, [('vendor_code','in',['1200001218','1200001037','1200000581','1100000137','1200000946','1200000790',
    #     #                                                                 '1200001230','1200001132','1200000680','1200000668','1100000277'])])
    #     #=======================================================================
    #      
    #     partner_ids = partner_obj.search(cr, uid, [('vendor_code','in',['1200001260'])])
    # 
    #     for partner_id in partner_ids:
    #         move_ids = move_obj.search(cr, uid, [('partner_id','in',[partner_id]), ('state','=','draft'),('doc_type','=','grn')])
    #         for move_id in move_ids:           
    #             move_obj.button_validate(cr,uid, [move_id], context)
    #     return self.write(cr, uid, ids, {'result':'GRN Auto Posting Done'})   
    #===========================================================================
   
#===============================================================================
#     def config_GRN_3451_3883(self, cr, uid, ids, context=None):
#         invoice_obj = self.pool.get('account.invoice')
#         inspec_obj = self.pool.get('tpt.quanlity.inspection')
#         picking_obj = self.pool.get('stock.picking')
#         move_obj = self.pool.get('account.move')
#         for grn in ['VVTi/GRN/00006706']:#['VVTi/GRN/00004321']:  #['VVTi/GRN/00003451','VVTi/GRN/00003883']
#             sql = '''
#                 select id from stock_picking where name = '%s'
#             '''%(grn)
#             cr.execute(sql)
#             num = cr.fetchone()[0]
#             if num:
#                 sql='''
#                     select id from account_invoice where grn_no = %s
#                 '''%(num)
#                 cr.execute(sql)
#                 inv_id = cr.fetchone()
#                 if inv_id:
#                     invoice_id = invoice_obj.browse(cr, uid, inv_id[0])
#                     if invoice_id.move_id and invoice_id.move_id.id:
#                         move_obj.button_cancel(cr, uid, [invoice_id.move_id.id])
#                         cr.execute(''' delete from account_move_line where move_id = %s''',(invoice_id.move_id.id,))
#                     cr.execute(''' delete from account_invoice_line where invoice_id = %s''',(invoice_id.id,))
#                     cr.execute(''' delete from account_invoice where id = %s''',(invoice_id.id,))
#                     if invoice_id.move_id and invoice_id.move_id.id:
#                         cr.execute(''' delete from account_move where id = %s''',(invoice_id.move_id.id,))
#                     
#                     sql = '''
#                         delete from account_move_line where left(name,17)=(select name from stock_picking where id = %s)
#                     '''%(num)
#                     cr.execute(sql)
#                     sql = '''
#                         delete from account_move where ref = '%s'
#                     '''%(grn)
#                     cr.execute(sql)
#                 sql='''
#                     select id from tpt_quanlity_inspection where need_inspec_id in (select id from stock_move where picking_id = %s)
#                 '''%(num)
#                 cr.execute(sql)
#                 inspec_ids = [row[0] for row in cr.fetchall()]
#                 if inspec_ids:
#                     for move in inspec_ids:
#                         sql='''
#                             select id from stock_move where inspec_id = %s
#                         '''%(move)
#                         cr.execute(sql)
#                         move_ids = [row[0] for row in cr.fetchall()]
#                         if move_ids:
#                             cr.execute('delete from stock_move where id in %s',(tuple(move_ids),))
#                     cr.execute('delete from tpt_quanlity_inspection where id in %s',(tuple(inspec_ids),))
#                 cr.execute(''' update stock_picking set invoice_state ='2binvoiced' where id = %s''',(num,))
#                 picking_obj.action_revert_done(cr, uid, [num], context)
# 
#         
#         return self.write(cr, uid, ids, {'result':'config GRN 3451 3883 Done'})   
#===============================================================================
    def config_GRN_7438(self, cr, uid, ids, context=None):
        invoice_obj = self.pool.get('account.invoice')
        inspec_obj = self.pool.get('tpt.quanlity.inspection')
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('account.move')
        for grn in ['VVTi/GRN/00000773']:#['VVTI/GRN/014480/2016']:#['VVTI/GRN/012944/2016']:#['VVTi/GRN/010906/2016']:#['VVTi/GRN/00010161']:#['VVTi/GRN/00010472']:# ['VVTi/GRN/00007438']:#['VVTi/GRN/00004321']:  #['VVTi/GRN/00003451','VVTi/GRN/00003883']
            sql = '''
                select id from stock_picking where name = '%s'
            '''%(grn)
            cr.execute(sql)
            num = cr.fetchone()[0]
            if num:
                sql='''
                    select id from account_invoice where grn_no = %s
                '''%(num)
                cr.execute(sql)
                inv_id = cr.fetchone()
                if inv_id:
                    invoice_id = invoice_obj.browse(cr, uid, inv_id[0])
                    if invoice_id.move_id and invoice_id.move_id.id:
                        move_obj.button_cancel(cr, uid, [invoice_id.move_id.id])
                        cr.execute(''' delete from account_move_line where move_id = %s''',(invoice_id.move_id.id,))
                    cr.execute(''' delete from account_invoice_line where invoice_id = %s''',(invoice_id.id,))
                    cr.execute(''' delete from account_invoice where id = %s''',(invoice_id.id,))
                    if invoice_id.move_id and invoice_id.move_id.id:
                        cr.execute(''' delete from account_move where id = %s''',(invoice_id.move_id.id,))
                     
                    sql = '''
                        delete from account_move_line where left(name,17)=(select name from stock_picking where id = %s)
                    '''%(num)
                    cr.execute(sql)
                    sql = '''
                        delete from account_move where ref = '%s'
                    '''%(grn)
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
 
         
        return self.write(cr, uid, ids, {'result':'config GRN VVTI/GRN/012821/2016 Done'})  
    
    def update_price_unit_for_production_declaration(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        production_obj = self.pool.get('mrp.production')
        production_ids = production_obj.search(cr, uid, [('state','=','done')])
        for line_ids in production_ids:
            debit = 0
            line = production_obj.browse(cr, uid, line_ids)
            for mat in line.move_lines2:
                categ = mat.product_id.categ_id.cate_name
                if categ=='finish':
                    sql = '''
                        select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
                        case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and location_dest_id != location_id
                            and  (action_taken = 'direct'
                            or (inspec_id is not null and location_dest_id = %s)
                            or (production_id is not null and location_dest_id = %s)
                            or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
                    )
                    '''%(mat.product_id.id,line.date_planned,line.location_src_id.id,line.location_src_id.id)
                    cr.execute(sql)
                    inventory = cr.dictfetchone()
                    if inventory:
                        hand_quantity_in = inventory['ton_sl'] or 0
                        total_cost_in = inventory['total_cost'] or 0
                    sql = '''
                        select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
                        case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and location_dest_id != location_id
                            and  (issue_id is not null
                            or (location_id = %s and id in (select move_id from mrp_production_move_ids))
                    )
                    '''%(mat.product_id.id,line.date_planned, line.location_src_id.id)
                    cr.execute(sql)
                    inventory = cr.dictfetchone()
                    if inventory:
                        hand_quantity_out = inventory['ton_sl'] or 0
                        hand_quantity_out = hand_quantity_out - mat.product_qty
                        total_cost_out = inventory['total_cost'] or 0
                    price_unit = (hand_quantity_in-hand_quantity_out) and (total_cost_in-total_cost_out)/(hand_quantity_in-hand_quantity_out)
                    if price_unit<0:
                        price_unit = 0
                    stock_move_obj.write(cr, 1, [mat.id],{'price_unit':price_unit})
#                     sql = '''
#                         update stock_move set price_unit = %s where id = %s
#                     '''%(price_unit, mat.id)
#                     cr.execute(sql)
                    cost = price_unit*mat.product_qty or 0
                    debit += cost
                
                if categ=='raw':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                    if mat.product_id.default_code != 'M0501060001':
                        sql='''
                            select price_unit from stock_move where date<='%s' and product_id=%s 
                                and issue_id in (select id from tpt_material_issue where request_type='production')
                                order by date desc
                        '''%(line.date_planned,mat.product_id.id)
                        cr.execute(sql)
                        move_ids = cr.fetchone()
                        if move_ids:
#                             sql = '''
#                                 update stock_move set price_unit = %s where id = %s
#                             '''%(move_ids[0], mat.id)
#                             cr.execute(sql)
                            stock_move_obj.write(cr, 1, [mat.id],{'price_unit':move_ids[0]})
                            price_raw = move_ids[0] * (mat.product_qty or 0)
                            debit += price_raw
                        else:
                            stock_move_obj.write(cr, 1, [mat.id],{'price_unit':0})
                            price_raw = 0
                            debit += price_raw 
#                             raise osv.except_osv(_('Warning!'),_("Do not have material issue for this Production Declaration! Please check it!"))
            
            for produce in line.move_created_ids2:
                if produce.product_id.id != line.product_id.id:
                    sql = '''
                        select price_unit from mrp_subproduct where bom_id=%s and product_id=%s
                    '''%(line.bom_id.id,produce.product_id.id)
                    cr.execute(sql)
                    price_ids = cr.fetchone()
                    produce_price = (price_ids and price_ids[0] or 0) * (produce.product_qty or 0)
                    debit -= produce_price
            for act in line.activities_line:
                debit += act.product_cost or 0
            if debit:
                unit_produce = debit/line.product_qty
                move_ids = stock_move_obj.search(cr, uid, [('product_id','=',line.product_id.id),('production_id','=',line.id)])
                if move_ids:
#                     cr.execute(''' update stock_move set price_unit = %s where id in %s ''',(unit_produce,tuple(move_ids),))
                    stock_move_obj.write(cr, 1, move_ids,{'price_unit':unit_produce})
        return self.write(cr, uid, ids, {'result':'update_price_unit_for_production_declaration Done'})  
    
    def create_one_production_declaration_one_posting(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        stock_move_obj = self.pool.get('stock.move')
        production_obj = self.pool.get('mrp.production')
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
#         production_ids = production_obj.search(cr, uid, [('state','=','done')])
        sql = '''
            select id from mrp_production where state = 'done' and id not in (select product_dec from account_move where doc_type='product' and product_dec is not null) 
            limit 200
        '''
        cr.execute(sql)
        production_ids = [r[0] for r in cr.fetchall()]
        if not production_ids:
            return self.write(cr, uid, ids, {'result':'create_one_production_declaration_one_posting Done'}) 
        for line_ids in production_ids:
#         for line_ids in [302,523]:
            debit = 0
            journal_line = []
            line = production_obj.browse(cr, uid, line_ids)
            sql = '''
                    select id from account_journal where name = 'Stock Journal'
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            date_period = line.date_planned
            sql = '''
                select id from account_period where '%s' between date_start and date_stop and special is False
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
            for mat in line.move_lines2:
                categ = mat.product_id.categ_id.cate_name
                if categ=='finish':
#                     sql = '''
#                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
#                         case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                         from stock_move st
#                         where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
#                             and location_dest_id != location_id
#                             and  (action_taken = 'direct'
#                             or (inspec_id is not null and location_dest_id = %s)
#                             or (production_id is not null and location_dest_id = %s)
#                             or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
#                     )
#                     '''%(mat.product_id.id,line.date_planned,line.location_src_id.id,line.location_src_id.id)
#                     cr.execute(sql)
#                     inventory = cr.dictfetchone()
#                     if inventory:
#                         hand_quantity_in = inventory['ton_sl'] or 0
#                         total_cost_in = inventory['total_cost'] or 0
#                     sql = '''
#                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
#                         case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                         from stock_move st
#                         where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
#                             and location_dest_id != location_id
#                             and  (issue_id is not null
#                             or (location_id = %s and id in (select move_id from mrp_production_move_ids))
#                     )
#                     '''%(mat.product_id.id,line.date_planned, line.location_src_id.id)
#                     cr.execute(sql)
#                     inventory = cr.dictfetchone()
#                     if inventory:
#                         hand_quantity_out = inventory['ton_sl'] or 0
#                         hand_quantity_out = hand_quantity_out - mat.product_qty
#                         total_cost_out = inventory['total_cost'] or 0
#                     price_unit = (hand_quantity_in-hand_quantity_out) and (total_cost_in-total_cost_out)/(hand_quantity_in-hand_quantity_out)
#                     stock_move_obj.write(cr, 1, [mat.id],{'price_unit':price_unit})
                    cost = mat.price_unit*mat.product_qty or 0
                    debit += round(cost,2)
                    if cost:
                        if mat.product_id.default_code not in ['M0501010005','M0501010004','M0501010002']:
                            if line.product_id.product_credit_id:
                                journal_line.append((0,0,{
                                                'name':mat.product_id.default_code, 
                                                'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                'debit':0,
                                                'credit':round(cost,2),
                                               }))
                            else:
                                raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                        else:
                            if mat.product_id.product_asset_acc_id:
                                journal_line.append((0,0,{
                                                'name':mat.product_id.default_code, 
                                                'account_id': mat.product_id.product_asset_acc_id and mat.product_id.product_asset_acc_id.id,
                                                'debit':0,
                                                'credit':round(cost,2),
                                               }))
                            else:
                                raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                
                if categ=='raw':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                    if mat.product_id.default_code == 'M0501060001':
                        if locat_ids[0] == line.location_src_id.id:
#                             sql = '''
#                                 select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
#                                 case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                                 from stock_move st
#                                 where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
#                                     and location_dest_id != location_id
#                                     and  (action_taken = 'direct'
#                                     or (inspec_id is not null and location_dest_id = %s)
#                                     or (id in (select move_id from stock_inventory_move_rel where inventory_id != 173))
#                             )
#                             '''%(mat.product_id.id,line.date_planned, locat_ids[0])
#                             cr.execute(sql)
#                             inventory = cr.dictfetchone()
#                             if inventory:
#                                 hand_quantity_in = inventory['ton_sl'] or 0
#                                 total_cost_in = inventory['total_cost'] or 0
#                                 
#                             sql = '''
#                                 select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,
#                                 case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                                 from stock_move st
#                                 where state='done' and product_id = %s and to_char(date, 'YYYY-MM-DD')<'%s'
#                                     and location_dest_id != location_id
#                                     and  (issue_id is not null
#                                     or (location_id = %s and id in (select move_id from mrp_production_move_ids))
#                             )
#                             '''%(mat.product_id.id,line.date_planned, locat_ids[0])
#                             cr.execute(sql)
#                             inventory = cr.dictfetchone()
#                             if inventory:
#                                 hand_quantity_out = inventory['ton_sl'] or 0
#                                 hand_quantity_out = hand_quantity_out - mat.product_qty
#                                 total_cost_out = inventory['total_cost'] or 0
#                             price_unit = (hand_quantity_in-hand_quantity_out) and (total_cost_in-total_cost_out)/(hand_quantity_in-hand_quantity_out)
#                             sql = '''
#                                 update stock_move set price_unit = %s where id = %s
#                             '''%(price_unit, mat.id)
#                             cr.execute(sql)
                            cost = mat.price_unit*mat.product_qty or 0
                            debit += round(cost,2)
                            if cost:
                                if line.product_id.product_credit_id:
                                    journal_line.append((0,0,{
                                                    'name':mat.product_id.code, 
                                                    'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                    'debit':0,
                                                    'credit':round(cost,2),
                                                   }))
                                else:
                                    raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                        else:
                            avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mat.product_id.id),('warehouse_id','=',line.location_src_id.id)])
                            if avg_cost_ids:
                                avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                                unit = avg_cost_id.avg_cost
                                cost = unit * mat.product_qty
                                debit += round(cost,2)
                                if cost:
                                    if line.product_id.product_credit_id:
                                        journal_line.append((0,0,{
                                                        'name':mat.product_id.code, 
                                                        'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                        'debit':0,
                                                        'credit':round(cost,2),
                                                       }))
                                    else:
                                        raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured for Product '%s'! Please configured it!")%(mat.product_id.default_code))
                    else:
#                             stock_move_obj.search(cr, uid, [('date','=',line.date_planned),('product_id','=',mat.product_id.id),('issue_id','!=',False)])
#                         sql='''
#                             select price_unit from stock_move where date='%s' and product_id=%s 
#                                 and issue_id in (select id from tpt_material_issue where request_type='production')
#                                 order by id
#                         '''%(line.date_planned,mat.product_id.id)
#                         cr.execute(sql)
#                         move_ids = cr.fetchone()
#                         if move_ids:
#                             stock_move_obj.write(cr, 1, [mat.id],{'price_unit':move_ids[0]})
#                             price_raw = move_ids[0] * (mat.product_qty or 0)
                        price_raw = mat.price_unit * (mat.product_qty or 0)
                        debit += round(price_raw,2)
                        if line.product_id.product_credit_id:
                            journal_line.append((0,0,{
                                                'name':mat.product_id.code, 
                                                'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                                'debit':0,
                                                'credit':round(price_raw,2),
                                                       }))
                        else:
                            raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured! Please configured it!"))
#                         else:
#                             raise osv.except_osv(_('Warning!'),_("Do not have material issue for this Production Declaration! Please check it!"))
            
            for produce in line.move_created_ids2:
                if produce.product_id.id != line.product_id.id:
                    sql = '''
                        select price_unit from mrp_subproduct where bom_id=%s and product_id=%s
                    '''%(line.bom_id.id,produce.product_id.id)
                    cr.execute(sql)
                    price_ids = cr.fetchone()
                    produce_price = (price_ids and price_ids[0] or 0) * (produce.product_qty or 0)
                    debit -= round(produce_price,2)
                    if line.product_id.product_asset_acc_id:
                        journal_line.append((0,0,{
                                                'name':produce.product_id.default_code, 
                                                'account_id': produce.product_id.product_asset_acc_id and produce.product_id.product_asset_acc_id.id,
                                                'debit':round(produce_price,2),
                                                'credit':0,
                                               }))
                    else:
                        raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(produce.product_id.default_code))
            for act in line.activities_line:
                if line.product_id.product_credit_id:
#                         credit += act.product_cost
                    debit += act.product_cost and round(act.product_cost,2) or 0
                    journal_line.append((0,0,{
                                            'name':act.activities_id.code, 
                                            'account_id': line.product_id.product_credit_id and line.product_id.product_credit_id.id,
                                            'debit':0,
                                            'credit':act.product_cost and round(act.product_cost,2) or 0,
                                           }))
                else:
                    raise osv.except_osv(_('Warning!'),_("Product Credit Account is not configured! Please configured it!"))
            if debit:
                if line.product_id.product_asset_acc_id:
                    journal_line.append((0,0,{
                                            'name':line.product_id.code, 
                                            'account_id': line.product_id.product_asset_acc_id and line.product_id.product_asset_acc_id.id,
                                            'debit': round(debit,2),
                                            'credit':0,
                                           }))
                else:
                    raise osv.except_osv(_('Warning!'),_("Product Asset Account is not configured for Product '%s'! Please configured it!")%(line.product_id.code))
                unit_produce = debit/line.product_qty
                move_ids = stock_move_obj.search(cr, uid, [('product_id','=',line.product_id.id),('production_id','=',line.id)])
                if move_ids:
                    stock_move_obj.write(cr, 1, move_ids,{'price_unit':unit_produce})
                
            value={
                        'journal_id':journal_ids[0],
                        'period_id':period_ids[0] ,
                        'doc_type':'product',
                        'date': line.date_planned,
                        'line_id': journal_line,
                        'product_dec': line.id,
                        'ref': line.name,
                    }
            try:
                new_jour_id = account_move_obj.create(cr,uid,value)
            except:
#                 print ValueError
                print 'production_id', line.id
#                 break
        return self.write(cr, uid, ids, {'result':'create_one_production_declaration_one_posting remaining'})  
    
    def adj_goods_issue(self, cr, uid, ids, context=None):
        temp_obj = self.pool.get('tpt.aml.sl.line')
        sql = '''
            select sm.id, pp.default_code, sm.product_qty, sm.price_unit, sm.issue_id, round(sm.product_qty*sm.price_unit, 2) as total  
            from stock_move sm
            inner join product_product pp on sm.product_id=pp.id
            where to_date(to_char(sm.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '2015-04-01' and '2016-03-31'
            and pp.cate_name='spares' and sm.issue_id is not null and sm.state='done' and sm.price_unit>=0
            --and sm.issue_id=1099
            order by sm.issue_id
        '''
        cr.execute(sql)
        vals = {}
            
        for ma in cr.dictfetchall():
            sql = '''
            select aml.id, aml.account_id from account_move_line aml
            inner join account_move am on aml.move_id=am.id
            where am.material_issue_id=%s --and aml.debit>0
            and aml.id not in (select aml_id from tpt_aml_sl_line)
            order by aml.id limit 2
            '''%ma['issue_id']
            cr.execute(sql)

            for aml in cr.dictfetchall():
                temp_ids = temp_obj.search(cr, uid, [('aml_id','=',aml['id'])])
                if not temp_ids:
                    print ma['issue_id']
                    if aml['account_id']==428:
                        sql = '''
                        update account_move_line set credit=%s where id=%s 
                        '''%(ma['total'], aml['id'])
                        cr.execute(sql)
                        if cr.rowcount>0:
                            vals['aml_id'] = aml['id']
                            temp_obj.create(cr, uid, vals, context)
                    if aml['account_id']==106:
                        sql = '''
                        update account_move_line set debit=%s where id=%s 
                        '''%(ma['total'], aml['id'])
                        cr.execute(sql)
                        if cr.rowcount>0:
                            vals['aml_id'] = aml['id']
                            temp_obj.create(cr, uid, vals, context)
                        
     
        return self.write(cr, uid, ids, {'result':'TPT update ISSUE for report Done'})
    
    def adj_goods_issue_raw_sup_acid(self, cr, uid, ids, context=None):
        temp_obj = self.pool.get('tpt.aml.sl.line')
        sql = '''
            select sm.id, pp.default_code, sm.product_qty, sm.price_unit, sm.issue_id, round(sm.product_qty*sm.price_unit, 2) as total  
            from stock_move sm
            inner join product_product pp on sm.product_id=pp.id
            where to_date(to_char(sm.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '2015-04-01' and '2016-03-31'
            and pp.cate_name='raw' and sm.issue_id is not null and sm.state='done' and sm.price_unit>=0
            and sm.product_id=10749
            order by sm.issue_id
        '''
        cr.execute(sql)
        vals = {}
            
        for ma in cr.dictfetchall():
            sql = '''
            select aml.id, aml.account_id from account_move_line aml
            inner join account_move am on aml.move_id=am.id
            where am.material_issue_id=%s --and aml.debit>0
            and aml.id not in (select aml_id from tpt_aml_sl_line)
            and aml.account_id in (413, 4514)
            order by aml.id limit 2
            '''%ma['issue_id']
            cr.execute(sql)

            for aml in cr.dictfetchall():
                temp_ids = temp_obj.search(cr, uid, [('aml_id','=',aml['id'])])
                if not temp_ids:
                    print ma['issue_id']
                    if aml['account_id']==413:# 0000119403 - RM-SULPHURIC ACID 
                        sql = '''
                        update account_move_line set credit=%s where id=%s 
                        '''%(ma['total'], aml['id'])
                        cr.execute(sql)
                        if cr.rowcount>0:
                            vals['aml_id'] = aml['id']
                            temp_obj.create(cr, uid, vals, context)
                    if aml['account_id']==4514:#0009900028 - SULPHURIC ACID - Cons. 
                        sql = '''
                        update account_move_line set debit=%s where id=%s 
                        '''%(ma['total'], aml['id'])
                        cr.execute(sql)
                        if cr.rowcount>0:
                            vals['aml_id'] = aml['id']
                            temp_obj.create(cr, uid, vals, context)
                        
     
        return self.write(cr, uid, ids, {'result':'TPT update ISSUE for report Done'})
    def adj_third_permission(self, cr, uid, ids, context=None):
        temp_obj = self.pool.get('tpt.aml.sl.line')
        sql = '''
            SELECT to_char(generate_series, 'YYYY-MM-DD') as date FROM generate_series('2016-01-01'::timestamp,'2016-06-30', '1 Months')

        '''
        cr.execute(sql)
        vals = {}
            
        #for ma in cr.dictfetchall():
        for line1 in range(1, 10):
            #print line1
            sql = '''
            select distinct he.id from hr_employee he
            inner join arul_hr_permission_onduty od on he.id=od.employee_id
            where od.non_availability_type_id='permission' and od.state not in ('draft', 'cancel')
            and extract(year from date)=2016
            '''
            cr.execute(sql)
            for line2 in cr.dictfetchall():
                sql = '''
                select id, date, extract(month from date) as month, employee_id, is_third_permission, non_availability_type_id from arul_hr_permission_onduty 
                where state not in ('draft', 'cancel') and non_availability_type_id='permission'
                and extract(year from date)=2016 and extract(month from date)=%s and employee_id=%s
                order by employee_id, date 
                limit 10 offset 2
                '''%(line1, line2['id'])
                cr.execute(sql)
                for line3 in cr.dictfetchall():
                    sql = '''
                    update arul_hr_permission_onduty set is_third_permission='t' where id=%s
                    '''%(line3['id'])
                    cr.execute(sql)
                    #print sql
                    #print line2['id'], line3['date'], line3['id']
                
        return self.write(cr, uid, ids, {'result':'TPT update 3rd Permission Done'})
tpt_update_stock_move_report()

class tpt_aml_sl_line(osv.osv):
    _name = "tpt.aml.sl.line"
    
    _columns = {
                'aml_id': fields.many2one('account.move.line', 'Account Move Line ID'),
                }
    
tpt_aml_sl_line()
    
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
    
    

tpt_update_inspection_line()

class tpt_update_avg_cost(osv.osv):
    _name = "tpt.update.avg.cost"
    
    _columns = {
        'name': fields.char('Name'),
        #'seq': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', 'Product'),
        'update_line': fields.one2many('tpt.update.avg.cost.line','update_id','Line'),
        
    }
    
    def bt_remove(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            cr.execute(''' update stock_move set inspec_id = null where id=%s ''',(line.move_id.id,))
        return self.write(cr, uid, ids, {'remove':True})
    
    def stock_adj(self, cr, uid, ids, context=None):
        #temp_obj = self.pool.get('tpt.aml.sl.line')
        avg_cost_obj = self.pool.get('tmp.avg.cost')
        for line in self.browse(cr, uid, ids):
            sql = '''
                SELECT to_char(generate_series, 'YYYY-MM-DD') as date FROM generate_series('2015-04-01'::timestamp,'2016-09-30', '1 Days')
            ''' 
            cr.execute(sql)
            vals = {}
                
            for date in cr.dictfetchall():
                date = date['date']
                sql = '''
                SELECT sum(onhand_qty) onhand_qty, sum(total_cost) total_cost
                From
                (SELECT  
                case when loc1.usage != 'internal' and loc2.usage = 'internal'
                then stm.product_qty
                else
                case when loc1.usage = 'internal' and loc2.usage != 'internal'
                then -1*stm.product_qty
                else 0.0 end
                end onhand_qty,

                case when loc1.usage != 'internal' and loc2.usage = 'internal'
                then stm.product_qty*stm.price_unit
                else
                case when loc1.usage = 'internal' and loc2.usage != 'internal'
                then -1*stm.product_qty*stm.price_unit
                else 0.0 end
                end total_cost
                       
                FROM stock_move stm
                join stock_location loc1 on stm.location_id=loc1.id
                join stock_location loc2 on stm.location_dest_id=loc2.id
                WHERE stm.state= 'done' and product_id=%s and to_date(to_char(stm.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s' 
                )foo
                '''%(line.product_id.id, date)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity_temp = round(float(inventory['onhand_qty']), 3)
                    total_cost_temp = round(float(inventory['total_cost']), 2)
                    avg_cost = hand_quantity_temp and round(total_cost_temp/hand_quantity_temp,2) or 0                               
                    #total_cost = avg_cost*hand_quantity
                    print date, hand_quantity_temp, total_cost_temp, avg_cost
                    #
                    sql = ''' select                
                    case when 
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
                    and ai.doc_type='freight_invoice' and ai.date_invoice='%s'
                    '''%(line.product_id.id, date)
                    cr.execute(sql)
                    freight = cr.fetchone()[0]
                    
                    sql = '''select 
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
                    ai.state not in ('draft', 'cancel') and ai.date_invoice='%s'
                    and ai.doc_type='supplier_invoice' and ail.fright>0
                    '''%(line.product_id.id, date)
                    cr.execute(sql)
                    sup_freight = cr.fetchone()[0]
                    
                    sql = '''
                    select                      
                    case when sum(ail.tpt_tax_amt)>=0 then sum(ail.tpt_tax_amt) else 0 end as cst_amt 
                    from account_invoice ai
                    inner join account_invoice_line ail on ai.id=ail.invoice_id
                    inner join account_invoice_line_tax ailt on ail.id=ailt.invoice_line_id
                    inner join account_tax t on ailt.tax_id = t.id
                    where ail.product_id=%s and ai.state not in ('draft', 'cancel')  and ai.date_invoice='%s'
                    and ai.doc_type='supplier_invoice' and t.description like '%sCST%s'
                    '''%(line.product_id.id, date, '%', '%')
                    cr.execute(sql)
                    cst = cr.fetchone()[0]
                    
                    sql = '''
                    SELECT sum(onhand_qty) 
                    From
                    (SELECT  
                    case when loc1.usage != 'internal' and loc2.usage = 'internal'
                    then stm.product_qty
                    else
                    case when loc1.usage = 'internal' and loc2.usage != 'internal'
                    then -1*stm.product_qty--stm.product_qty
                    else 0.0 end
                    end onhand_qty
                           
                    FROM stock_move stm
                    join stock_location loc1 on stm.location_id=loc1.id
                    join stock_location loc2 on stm.location_dest_id=loc2.id
                    WHERE stm.state= 'done' and product_id=%s and to_date(to_char(stm.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' 
                    )foo
                    '''%(line.product_id.id, date)
                    cr.execute(sql)
                    open_hand_qty = cr.fetchone()[0]
                    #
                    sql = '''
                    select sm.product_qty, sm.price_unit, mi.doc_no from stock_move sm
                    inner join tpt_material_issue mi on sm.issue_id=mi.id
                    where sm.issue_id is not null and sm.state='done' and sm.product_id=%s and
                    to_date(to_char(sm.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' 
                    '''%(line.product_id.id, date)
                    cr.execute(sql)
                    for cons in cr.dictfetchall():
                        cons_qty = cons['product_qty']
                        cons_value = cons['price_unit']
                    #
                    
                    avg_cost_obj.create(cr, uid, {
                       #'employee_id': employee_ids[0],
                       'product_id': line.product_id.id,
                       'date': date,
                       'hand_qty': hand_quantity_temp,
                       'avg_cost': avg_cost or 0,
                       'total_cost': total_cost_temp,
                       'freight': freight or 0, 
                       'sup_freight': sup_freight or 0,
                       'cst' : cst or 0,
                       'open_hand_qty': open_hand_qty or 0, 
                       'rx_qty': 0,
                       'cons_qty' : cons_qty or 0,
                       'cons_value' : cons_value or 0
                      
                       })
     
        #return self.write(cr, uid, ids, {'result':'TPT update 3rd Permission Done'})
        return True
    


tpt_update_avg_cost()

class temp_avg_cost(osv.osv):
    _name = "tmp.avg.cost"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'date': fields.date('Date'),
        'hand_qty': fields.float('On-Hand', ), 
        'avg_cost': fields.float('Avg Cost ', ), 
        'total_cost': fields.float('Total Cost', ), 
        'freight':fields.float('Freight', ), 
        'sup_freight':fields.float('Supplier Invoice Freight', ), 
        'cst':fields.float('CST Amount', ), 
        'open_hand_qty': fields.float('Opening On-Hand', ), 
        'rx_qty': fields.float('Received Qty', ), 
        'cons_qty': fields.float('Consumption Qty', ), 
        'cons_value': fields.float('Consumption Value', ), 
    }
temp_avg_cost()
    
class tpt_update_avg_cost_line(osv.osv):
    _name = "tpt.update.avg.cost.line"
    
    _columns = {
        'name': fields.char('Name'),
        'seq': fields.integer('Sequence'),
        'product_id': fields.many2one('product.product', 'Product'),
        'date': fields.date('Date'),
        'price_unit': fields.float('Unit Price', ), 
        'update_id': fields.many2one('tpt.update.avg.cost', 'Update', ondelete='cascade'),
    }
    
    def bt_remove(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            cr.execute(''' update stock_move set inspec_id = null where id=%s ''',(line.move_id.id,))
        return self.write(cr, uid, ids, {'remove':True})

tpt_update_avg_cost_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
