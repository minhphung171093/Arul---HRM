# -*- coding: utf-8 -*-

import xmlrpclib
import os
import sys
from fileinput import close
os.chdir('../')
current_path = os.getcwd()
sys.path.append(current_path)
from common.oorpc import OpenObjectRPC, define_arg

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import psycopg2
import psycopg2.extras

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

db1_conn_string = "host='localhost' port='5432' dbname='doukas61' user='openerp' password='1'"
db2_conn_string = "host='localhost' port='5432' dbname='doukas70_temp' user='openerp' password='1'"

map_cur = {1:1,
           2:3,
           }

def import_stock_move(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql='''
        SELECT id, create_uid, create_date, write_date, write_uid, origin, product_uos_qty, 
           date_expected, product_uom, price_unit, date, prodlot_id, move_dest_id, 
           product_qty, product_uos, partner_id, name, note, product_id, 
           auto_validate, price_currency_id, location_id, company_id, picking_id, 
           priority, state, location_dest_id, tracking_id, product_packaging, 
           purchase_line_id, sale_line_id
      FROM stock_move
      order by id;

    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        product_uos_qty = False
        price_currency_id = False
        if row['product_uos_qty']:
             product_uos_qty= float(row['product_uos_qty'])
        if row['price_unit']:
             price_unit= float(row['price_unit'])
        if row['product_qty']:
             product_qty= float(row['product_qty'])
        if row['product_uos']:
             product_uos= float(row['product_uos'])
        if row['date_expected']:
             date_expected= ((row['date_expected'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date']:
             date= ((row['date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['price_currency_id']:
             price_currency_id=  map_cur[row['price_currency_id']]
        vals = {
                    'origin':row['origin'] or False,
                    'product_uos_qty': product_uos_qty or False,
                    'date_expected':date_expected or False,
                    'move_dest_id':row['move_dest_id'] or False,
                    'product_uom':row['product_uom'] or False,
                    'price_unit':price_unit or False,
                    'date':date or False,
                    'prodlot_id': row['prodlot_id'] or False,
                    'move_dest_id':row['move_dest_id'] or False,
                    'product_qty':product_qty or False,
                    'product_uos':product_uos or False,
                    'partner_id':row['partner_id'] or False,
                    'name': row['name'] or False,
                    'note':row['note'] or False,
                    'product_id':row['product_id'] or False,
                    'auto_validate':row['auto_validate'] or False,
                    'price_currency_id':price_currency_id or False,
                    'location_id': row['location_id'] or False,
                    'company_id':row['company_id'] or False,
                    'picking_id':row['picking_id'] or False,
                    'priority':row['priority'] or False,
                    'state':row['state'] or False,
                    'location_dest_id':row['location_dest_id'] or False,
                    'tracking_id':row['tracking_id'] or False,
                    'product_packaging':row['product_packaging'] or False,
                    'purchase_line_id':row['purchase_line_id'] or False,
                    'sale_line_id':row['sale_line_id'] or False,
                }
        new_id = oorpc.create('stock.move', vals)
        sql = '''
         update stock_move set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('stock_move_id_seq', (SELECT MAX(id) FROM stock_move))''')
        cur2.execute('commit')
        print number
        number += 1

def import_picking(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
#     cursor2.execute('''
#       ALTER TABLE stock_picking
#       drop CONSTRAINT stock_picking_name_uniq  
#      ''')
#     cursor2.execute('commit')
    sql ='''
          SELECT id, create_uid, create_date, write_date, write_uid, origin, address_id, 
               date_done, min_date, date, location_id, stock_journal_id, backorder_id, 
               name, partner_id, move_type, company_id, invoice_state, note, 
               state, location_dest_id, max_date, auto_picking, type, sale_id, 
               purchase_id
          FROM stock_picking
          order by id;
     '''
        
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        date_done = False
        min_date =False
        date = False
        max_date = False
        if row['date_done']:
             date_planned= ((row['date_done'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['min_date']:
             min_date= ((row['min_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date']:
             min_date= ((row['date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['max_date']:
             min_date= ((row['max_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        vals = {
                    'origin':row['origin'] or False,
                    'date_done':date_done or False,
                    'min_date':min_date or False,
                    'date':date or False,
                    'location_id':row['location_id'] or False,
                    'stock_journal_id':row['stock_journal_id'] or False,
                    'name': row['name'],
                    'partner_id':row['partner_id'] or False,
                    'move_type':row['move_type'] or False,
                    'company_id':row['company_id'] or False,
                    'invoice_state':row['invoice_state'] or False,
                    'note': row['note'] or False,
                    'state':row['state'] or False,
                    'location_dest_id': row['location_dest_id'] or False,
                    'max_date':max_date or False,
                    'auto_picking': row['auto_picking'] or False,
                    'sale_id':row['sale_id'] or False,
                    'purchase_id':row['purchase_id'] or False,
                }
        if row['type'] == 'in':
            new_id = oorpc.create('stock.picking.in', vals)
        else:
            new_id = oorpc.create('stock.picking.out', vals)
            
        sql = '''
         update stock_picking set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('stock_picking_id_seq', (SELECT MAX(id) FROM stock_picking))''')
        cur2.execute('commit')
        print number
        number += 1
    
    sql ='''
          SELECT id, backorder_id
          FROM stock_picking
          order by id;
     '''
        
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        backorder_id = 'null'
        if row['backorder_id']:
             backorder_id= row['backorder_id']
        sql = '''
         update stock_picking set backorder_id = %s where id = %s 
         ''' %(backorder_id,row['id'])
        cur2.execute(sql)
        cur2.execute('commit')
    
    cursor2.execute('''
     ALTER TABLE stock_picking
      ADD CONSTRAINT stock_picking_name_uniq UNIQUE(name, company_id); 
     ''')
    cursor2.execute('commit')

def update_picking_workflow(oorpc):
    po_ids = oorpc.search('stock.picking.out',[('state','in',['confirmed','assigned'])])
    for po_id in po_ids:
        po = oorpc.read('stock.picking.out', po_id, ['state'])
        if po['state'] == 'confirmed':
            oorpc.exec_workflow('stock.picking', 'button_confirm', po_id)
#         if po['state'] == 'assigned':
#             oorpc.exec_workflow('stock.picking.out', 'purchase_approve', po_id)
    
    #DELETE all Picking
#     cursor2.execute('''TRUNCATE account_invoice_line CASCADE;
#                         TRUNCATE account_invoice CASCADE;''')      
#     cursor2.execute('commit')

def update_procurement_order(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
     cur1 = conn1.cursor()
     cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     sql='''
             SELECT id, move_id
          FROM procurement_order
          ORDER BY ID;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     number = 1
     for row in old_po:
         if row['move_id']:
             sql = '''
             update procurement_order set move_id = %s where id = %s 
             ''' %(row['move_id'],row['id'])
             cur2.execute(sql)
             cur2.execute('commit')
             print number
             number += 1

def update_purchase_order_line(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql='''
        SELECT id, move_dest_id
       FROM purchase_order_line;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        if row['move_dest_id']:
            sql = '''
             update purchase_order_line set move_dest_id = %s where id = %s 
             ''' %(row['move_dest_id'],row['id'])
            cur2.execute(sql)
            cur2.execute('commit')
            print number
            number += 1

def import_stock_inventory(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, state, name, 
           date_done, date, company_id
        FROM stock_inventory
        order by id;

    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        date_done = False
        quantity = False
        
        if row['date_done']:
            date_done= ((row['date_done'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date']:
            date= ((row['date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        vals = {
                    'state':row['state'] or False,
                    'name':row['name'] or False,
                    'date_done': date_done or False,
                    'date':date or False,
                    'company_id':row['company_id'] or False,
                    }
        new_id = oorpc.create('stock.inventory', vals)
        sql = '''
         update stock_inventory set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('stock_inventory_id_seq', (SELECT MAX(id) FROM stock_inventory))''')
        cur2.execute('commit')
        
def import_stock_inventory_line(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, product_id, 
        product_uom, prod_lot_id, company_id, inventory_id, product_qty, 
        location_id
        FROM stock_inventory_line
        order by id
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        product_qty = False
        
        if row['product_qty']:
            product_qty= float(product_qty)
        vals = {
                    'product_id':row['product_id'] or False,
                    'product_uom':row['product_uom'] or False,
                    'prod_lot_id': row['prod_lot_id'] or False,
                    'company_id':row['company_id'] or False,
                    'inventory_id':row['inventory_id'] or False,
                    'product_qty':product_qty or False,
                    'location_id':row['location_id'] or False
                    }
        new_id = oorpc.create('stock.inventory.line', vals)
        sql = '''
         update stock_inventory_line set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('stock_inventory_line_id_seq', (SELECT MAX(id) FROM stock_inventory_line))''')
        cur2.execute('commit')

def import_stock_inventory_move_ref(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_stock_inventory_move_rel = ['inventory_id', 'move_id']
    
    sql ='''
        SELECT inventory_id, move_id
        FROM stock_inventory_move_rel
        order by inventory_id
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        
        values = '''
                     %s,%s
                 '''%(
                       row['inventory_id'] or 'null' ,row['move_id'] or 'null'
                       )
                 
        sql = '''INSERT INTO stock_inventory_move_rel(%s)
            VALUES (%s)
            '''%(','.join(map(str,db1_stock_inventory_move_rel)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')
        
if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('localhost', 'doukas70_temp', 'admin', '1', '8069')
    print 'In progress ...'

#     import_picking(oorpc)
#     import_stock_move(oorpc)
#     update_picking_workflow(oorpc)

    #Thanh: Update move_id for procurement
#     update_procurement_order(oorpc)
#     update_purchase_order_line(oorpc)

#     import_stock_inventory(oorpc)
#     import_stock_inventory_line(oorpc)
#     import_stock_inventory_move_ref(oorpc)
    
    print 'Done.'
    
    
    
    

