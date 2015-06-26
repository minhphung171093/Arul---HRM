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
    
tpt_update_stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

