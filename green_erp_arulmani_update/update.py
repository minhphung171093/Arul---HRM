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
    
    def init(self, cr):
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
                        where pp.product_tmpl_id = pt.id and pt.categ_id = cat.id and cat.cate_name = '%s')
            '''%(location_id,dest_1_id,dest_2_id,inspec.product_id.id,cate)
            cr.execute(sql)
            move_ids = cr.fetchall()
            if move_ids:
                cr.execute("UPDATE stock_move SET inspec_id= %s WHERE id in %s",inspec.id,(tuple(move_ids),))
                print 'TPT update INSPEC for report', tuple(move_ids)
                        
    _columns = {
        'name': fields.char('Document No.', size=1024, readonly=True ),
    }
    
    
tpt_update_stock_move_report()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
