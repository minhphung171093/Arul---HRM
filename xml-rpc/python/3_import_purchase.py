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
           2:3,}

def import_purchase_order_line(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql='''
        SELECT id, create_uid, create_date, write_date, write_uid, product_uom, 
           order_id, price_unit, move_dest_id, product_qty, partner_id, 
           invoiced, name, date_planned, notes, company_id, state, product_id, 
           account_analytic_id
       FROM purchase_order_line;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        price_unit = False
        product_qty = False
        if row['price_unit']:
             price_unit= float(row['price_unit'])
        if row['product_qty']:
             product_qty= float(row['product_qty'])
        if row['date_planned']:
             date_planned= ((row['date_planned'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        vals = {
                    'product_uom':row['product_uom'] or False,
                    'order_id': row['order_id'] or False,
                    'price_unit':price_unit or False,
                    #'move_dest_id':row['move_dest_id'] or False,
                    'product_qty':product_qty or False,
                    'partner_id':row['partner_id'] or False,
                    'invoiced':row['invoiced'] or False,
                    'name': row['name'] or False,
                    'date_planned': date_planned or False,
                    'company_id':row['company_id'] or False,
                    'state':row['state'] or False,
                    'product_id':row['product_id'] or False,
                    'account_analytic_id':row['account_analytic_id'] or False,
                }
        new_id = oorpc.create('purchase.order.line', vals)
        sql = '''
         update purchase_order_line set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('purchase_order_line_id_seq', (SELECT MAX(id) FROM purchase_order_line))''')
        cur2.execute('commit')
        print number
        number += 1
        
def import_purchase_order(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
    sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid, origin, partner_address_id, 
               warehouse_id, partner_ref, date_order, location_id, date_approve, 
               dest_address_id, fiscal_position, amount_untaxed, name, shipped, 
               partner_id, notes, company_id, amount_tax, invoice_method, state, 
               validator, minimum_planned_date, pricelist_id, amount_total
          FROM purchase_order
          order by id;
     '''
        
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        date_order = False
        date_approve = False
        amount_tax = False
        minimum_planned_date = False
        amount_total = False
        if row['date_order']:
             date_order= ((row['date_order'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date_approve']:
             date_approve= ((row['date_approve'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['minimum_planned_date']:
             minimum_planned_date= ((row['minimum_planned_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['amount_untaxed']:
             amount_untaxed= float(row['amount_untaxed'])
        if row['amount_tax']:
             amount_tax= float(row['amount_tax'])
        if row['amount_total']:
             amount_tax= float(row['amount_total'])
        vals = {
                    'origin':row['origin'] or False,
                    'partner_address_id': row['partner_id'] or False,
                    'warehouse_id':row['warehouse_id'] or False,
                    'partner_ref':row['partner_ref'] or False,
                    'date_order':date_order or False,
                    'location_id':row['location_id'] or False,
                    'date_approve':date_approve or False,
                    'dest_address_id': row['dest_address_id'] or False,
                    'fiscal_position': row['fiscal_position'],
                    'amount_untaxed':amount_untaxed or False,
                    'fiscal_position':row['fiscal_position'] or False,
                    'name':row['name'] or False,
                    'shipped':row['shipped'] or False,
                    'partner_id': row['partner_id'] or False,
                    'notes':row['notes'] or False,
                    'amount_tax':amount_tax or False,
                    'invoice_method':row['invoice_method'] or False,
                    'state':row['state'] or False,
                    'minimum_planned_date': minimum_planned_date or False,
                    'pricelist_id':row['pricelist_id'] or False,
                    'amount_total':amount_tax or False,
                }
        new_id = oorpc.create('purchase.order', vals)
        sql = '''
         update purchase_order set id = %s, validator=%s where id = %s 
         ''' %(row['id'],row['validator'] or "Null",new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('purchase_order_id_seq', (SELECT MAX(id) FROM purchase_order))''')
        cur2.execute('commit')
        print number
        number += 1

def update_po_workflow(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    po_ids = oorpc.search('purchase.order',[('state','in',['confirmed','approved'])])
    for po_id in po_ids:
        po = oorpc.read('purchase.order', po_id, ['state'])
        if po['state'] == 'confirmed':
            oorpc.exec_workflow('purchase.order', 'purchase_confirm', po_id)
        if po['state'] == 'approved':
            oorpc.exec_workflow('purchase.order', 'purchase_approve', po_id)

#     #DELETE all Picking
#     cursor2.execute('''TRUNCATE stock_move CASCADE;
#                         TRUNCATE stock_picking CASCADE;''')      
#     cursor2.execute('commit')
    
if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('localhost', 'doukas70_temp', 'admin', '1', '8069')
    print 'In progress ...'
#     import_purchase_order(oorpc)
#     import_purchase_order_line(oorpc)
#     update_po_workflow(oorpc)
    print 'Done.'
    
    
    
    

