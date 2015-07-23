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
from common.oorpc import OpenObjectRPC, define_arg
import psycopg2


class tpt_update_stock_move(osv.osv):
    _name = "tpt.update.stock.move"
    
    _columns = {
        'host': fields.char('Host', size=1024),
        'port': fields.char('Port', size=1024),
        'database': fields.char('Database', size=1024),
        'username': fields.char('Username', size=1024),
        'password': fields.char('Password', size=1024),
        'db_port': fields.char('DB Port', size=1024),
        'db_username': fields.char('DB Username', size=1024),
        'db_password': fields.char('DB Password', size=1024),
        'result': fields.text('Result', readonly=True ),
    }
    
    def update_tm(self, cr, uid, ids, context=None):
        line = self.browse(cr, uid, ids[0])
#         oorpc = OpenObjectRPC(line.host, line.database, line.username, line.password, line.port)
        db_conn_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(line.host, line.db_port, line.database, line.db_username, line.db_password)
        conn = psycopg2.connect(db_conn_string)
        cursor = conn.cursor()
        sql = '''
            select id,company_id,name,product_uos,product_uom,product_uos_qty,location_id,location_dest_id,product_id,product_qty,date,price_unit,date_expected
                 from stock_move where picking_id is null and inspec_id is null and issue_id is null and production_id is null and id not in (select move_id from mrp_production_move_ids)
                    and id not in (select child_id from stock_move_history_ids) and id not in (select move_id from stock_inventory_move_rel) and move_dest_id is null and purchase_line_id is null 
                    and sale_line_id is null and tracking_id is null and prodlot_id is null and state='done'
        '''
        cursor.execute(sql)
        move_ids = cursor.fetchall()
        move_obj = self.pool.get('stock.move')
        move_line_ids = []
        for move in move_ids:
            vals = {'location_id':move[6],
                    'location_dest_id':move[7],
                    'product_id':move[8],
                    'product_qty':move[9],
                    'product_uos_qty':move[5],
                    'product_uom':move[4],
                    'product_uos':move[3],
                    'company_id':move[1],
                    'date':move[10],
                    'name':move[2],
                    'state':'draft',
                    'price_unit':move[11],
                    'date_expected':move[12],}
            move_id = move_obj.create(cr, uid, vals)
            move_line_ids.append(move_id)
            move_obj.action_done(cr, uid, [move_id])
            cr.execute(''' update stock_move set date=%s,date_expected=%s where id=%s ''',(move[10],move[12],move_id,))
        self.pool.get('stock.inventory').create(cr, uid, {
            'name': 'TPT Update Stock Move',
            'date': time.strftime('%Y-%m-%d'),
            'state': 'done',
            'move_ids': [(6,0,move_line_ids)],
            'company_id': 1,
        })
        return self.write(cr, uid, ids, {'result':'TPT update Stock Move Done'})
    
    def update_issue(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        line = self.browse(cr, uid, ids[0])
#         oorpc = OpenObjectRPC(line.host, line.database, line.username, line.password, line.port)
        db_conn_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(line.host, line.db_port, line.database, line.db_username, line.db_password)
        conn = psycopg2.connect(db_conn_string)
        cursor = conn.cursor()
        sql = '''
            select id,name,date_request,date_expec,department_id,request_type,state,gl_account_id,warehouse,dest_warehouse_id
                from tpt_material_issue where state = 'done'
        '''
        cursor.execute(sql)
        issue_ids = cursor.fetchall()
        issue_obj = self.pool.get('tpt.material.issue')
        for issue in issue_ids:
            issue_line = []
            sql = '''
                select id from tpt_material_issue where id = %s
            '''%(issue[0])
            cr.execute(sql)
            cur_id = [r[0] for r in cr.fetchall()]
            if not cur_id:
                sql = '''
                    select product_id,dec_material,product_uom_qty,product_isu_qty,uom_po_id,request_line_id
                        from tpt_material_issue_line where material_issue_id = %s
                '''%(issue[0])
                cursor.execute(sql)
                for line1 in cursor.fetchall():
                    issue_line.append((0,0,{'product_id':line1[0],
                                            'dec_material':line1[1],
                                            'product_uom_qty':line1[2],
                                            'product_isu_qty':line1[3],
                                            'uom_po_id':line1[4],
                                            }))
                
                vals = {'name':issue[1],
                        'date_request':issue[2],
                        'date_expec':issue[3],
                        'department_id':issue[4],
                        'request_type':issue[5],
                        'state':issue[6],
                        'material_issue_line':issue_line,
                        'again':True,
                        'gl_account_id':issue[7],
                        'warehouse':issue[8],
                        'dest_warehouse_id':issue[9],}
                context.update({'create_issue_again':1})
                issue_obj.create(cr, uid, vals, context)
        return self.write(cr, uid, ids, {'result':'TPT update Issue Done'})
    
    def map_issue_sm(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and again is True
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
                        and product_qty = %s and id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where name='TPT Update Stock Move'))
                '''%(location_id,dest_id,iss_line.product_id.id,iss_line.uom_po_id.id,iss_line.product_isu_qty)
                cr.execute(sql)
                move_ids = cr.fetchone()
                if move_ids:
                    sql = ''' 
                        update stock_move set issue_id = %s where id = %s
                    '''%(issue.id,move_ids[0])
                    cr.execute(sql)
#                     cr.execute('''delete from stock_inventory_move_rel 
#                         where move_id = %s and inventory_id in (select id from stock_inventory where name='TPT Update Stock Move')''',(move_ids[0],))
        return self.write(cr, uid, ids, {'result':'TPT map Issue-Stock move Done'})
    
    def check_update_map_issue(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and again is True
        '''
        cr.execute(sql)
        for ma in cr.fetchall():
            issue = self.pool.get('tpt.material.issue').browse(cr, 1, ma[0])
            sql = '''
                select count(*) from tpt_material_issue_line where material_issue_id = %s
            '''%(issue.id)
            cr.execute(sql)
            count_iss_line = cr.fetchone()
            sql = '''
                select count(*) from stock_move where issue_id = %s
            '''%(issue.id)
            cr.execute(sql)
            count_sm = cr.fetchone()
            
            if count_iss_line != count_sm:
                cr.execute('''update stock_move set issue_id = null where issue_id = %s ''',(issue.id,))
                cr.execute('''delete from tpt_material_issue where id = %s''',(issue.id,))
        return self.write(cr, uid, ids, {'result':'TPT check_update_map_issue Done'})
    
    def update_sm_inv_iss(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and again is True
        '''
        cr.execute(sql)
        issue_ids = []
        sm_ids = []
        for ma in cr.fetchall():
            issue = self.pool.get('tpt.material.issue').browse(cr, 1, ma[0])
            sql = '''
                select id,issue_id from stock_move where name = '/' and state = 'done'
                    and issue_id =%s and inspec_id is NULL and picking_id is NULL and
                    id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where name='TPT Update Stock Move'))
            '''%(issue.id)
            cr.execute(sql)
            for map_id in cr.dictfetchall():
                issue_ids.append(map_id['issue_id'])
                sm_ids.append(map_id['id'])
        cr.execute('''delete from stock_inventory_move_rel 
            where move_id in %s and inventory_id in (select id from stock_inventory where name='TPT Update Stock Move')''',(tuple(sm_ids),))
        
        cr.execute('''delete from tpt_material_issue 
            where again is True and id not in %s ''',(tuple(issue_ids),))
        return self.write(cr, uid, ids, {'result':'TPT update_sm_inv_iss Done'})
    
    def update_iss_12_14_15(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        line = self.browse(cr, uid, ids[0])
        db_conn_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'"%(line.host, line.db_port, line.database, line.db_username, line.db_password)
        conn = psycopg2.connect(db_conn_string)
        cursor = conn.cursor()
        sql = '''
            select id,name,date_request,date_expec,department_id,request_type,state,gl_account_id,warehouse,dest_warehouse_id
                from tpt_material_issue where state = 'done' and id in (12,14,15)
        '''
        cursor.execute(sql)
        issue_ids = cursor.fetchall()
        issue_obj = self.pool.get('tpt.material.issue')
        for issue in issue_ids:
            issue_line = []
            sql = '''
                select id from tpt_material_issue where id = %s
            '''%(issue[0])
            cr.execute(sql)
            cur_id = [r[0] for r in cr.fetchall()]
            if not cur_id:
                sql = '''
                    select product_id,dec_material,product_uom_qty,product_isu_qty,uom_po_id,request_line_id
                        from tpt_material_issue_line where material_issue_id = %s
                '''%(issue[0])
                cursor.execute(sql)
                for line1 in cursor.fetchall():
                    issue_line.append((0,0,{'product_id':line1[0],
                                            'dec_material':line1[1],
                                            'product_uom_qty':line1[2],
                                            'product_isu_qty':line1[3],
                                            'uom_po_id':line1[4],
                                            }))
                
                vals = {'name':issue[1],
                        'date_request':issue[2],
                        'date_expec':issue[3],
                        'department_id':issue[4],
                        'request_type':issue[5],
                        'state':issue[6],
                        'material_issue_line':issue_line,
                        'april':True,
                        'gl_account_id':issue[7],
                        'warehouse':issue[8],
                        'dest_warehouse_id':issue[9],}
                context.update({'create_issue_again':1})
                issue_obj.create(cr, uid, vals, context)
        return self.write(cr, uid, ids, {'result':'TPT update_iss_12_14_15 Done'})
    
    def map_iss_12_14_15_sm(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and april is True
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
                        and product_qty = %s and id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where name='TPT Update Stock Move'))
                '''%(location_id,dest_id,iss_line.product_id.id,iss_line.uom_po_id.id,iss_line.product_isu_qty)
                cr.execute(sql)
                move_ids = cr.fetchone()
                if move_ids:
                    sql = ''' 
                        update stock_move set issue_id = %s where id = %s
                    '''%(issue.id,move_ids[0])
                    cr.execute(sql)
                if not move_ids:
                    cr.execute('''delete from tpt_material_issue_line 
                        where id = %s''',(iss_line.id,))
        return self.write(cr, uid, ids, {'result':'TPT map_iss_12_14_15_sm Done'})
    
    def update_sm_inv_iss_12_14_15(self, cr, uid, ids, context=None):
        sql = '''
            select id from tpt_material_issue where state = 'done' and april is True
        '''
        cr.execute(sql)
        sm_ids = []
        for ma in cr.fetchall():
            issue = self.pool.get('tpt.material.issue').browse(cr, 1, ma[0])
            sql = '''
                select id,issue_id from stock_move where name = '/' and state = 'done'
                    and issue_id =%s and inspec_id is NULL and picking_id is NULL and
                    id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where name='TPT Update Stock Move'))
            '''%(issue.id)
            cr.execute(sql)
            for map_id in cr.dictfetchall():
                sm_ids.append(map_id['id'])
        cr.execute('''delete from stock_inventory_move_rel 
            where move_id in %s and inventory_id in (select id from stock_inventory where name='TPT Update Stock Move')''',(tuple(sm_ids),))
        
        return self.write(cr, uid, ids, {'result':'TPT update_sm_inv_iss_12_14_15 Done'})
    
tpt_update_stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

