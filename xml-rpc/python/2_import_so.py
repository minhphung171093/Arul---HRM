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
db2_conn_string = "host='localhost' port='5432' dbname='doukas70_ok1' user='openerp' password='1'"
   

def import_sale_shop(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
    sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid, name, pricelist_id, 
               project_id, company_id, payment_default_id, warehouse_id
          FROM sale_shop order by id;
     '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
            vals = {
                        'name':row['name'] or False,
                        'pricelist_id': row['pricelist_id'] or False,
                        'project_id':row['project_id'] or False,
                        'company_id':row['company_id'] or False,
                        'payment_default_id':row['payment_default_id'] or False,
                        'warehouse_id':row['warehouse_id'] or False,
                    }
            new_id = oorpc.create('sale.shop', vals)
            sql = '''
             update sale_shop set id = %s where id = %s 
             ''' %(row['id'],new_id)
            cur2.execute(sql)
            cur2.execute('commit')
    cur2.execute('''SELECT setval('sale_shop_id_seq', (SELECT MAX(id) FROM sale_shop))''')
    cur2.execute('commit')

def import_sale_config(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
     cur1 = conn1.cursor()
     cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
     sql ='''
        delete from sale_shop 
     '''
     cur2.execute(sql)
     cur2.execute('commit')
     
        
     sql ='''
        delete from sale_order 
     '''
     cur2.execute(sql)
     cur2.execute('commit')
     
     sql ='''
        delete from account_payment_term_line 
     '''
     cur2.execute(sql)
     cur2.execute('commit')
     
     sql ='''
        delete from account_payment_term 
     '''
     cur2.execute(sql)
     cur2.execute('commit')
     
     sql ='''
          SELECT id, create_uid, create_date, write_date, write_uid, active, note, 
               name
          FROM account_payment_term order by id;
     '''
    
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     for row in old_po:
            vals = {
                        'active':row['active'] or False,
                        'note': row['note'] or False,
                        'name':row['name'] or False,
                    }
            new_id = oorpc.create('account.payment.term', vals)
            sql = '''
             update account_payment_term set id = %s where id = %s 
             ''' %(row['id'],new_id)
            cur2.execute(sql)
            cur2.execute('commit')
    
            
     cur2.execute('''SELECT setval('account_payment_term_id_seq', (SELECT MAX(id) FROM account_payment_term))''')
     cur2.execute('commit')
     
     sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid, payment_id, 
           name, value_amount, sequence, days2, days, value
         FROM account_payment_term_line order by id;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     for row in old_po:
        value_amount = False
        if row['value_amount']:
            value_amount = float(row['value_amount']) 
        vals = {
                    'payment_id':row['payment_id'] or False,
                    'name': row['name'] or False,
                    'value_amount':value_amount ,
                    'sequence':row['sequence'] or False,
                    'days2':row['days2'] or False,
                    'days':row['days'] or False,
                    'value':row['value'] or False,
                }
        new_id = oorpc.create('account.payment.term.line', vals)
        sql = '''
         update account_payment_term_line set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
     cur2.execute('''SELECT setval('account_payment_term_line_id_seq', (SELECT MAX(id) FROM account_payment_term_line))''')
     cur2.execute('commit')
     
def import_procurement_order(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
     cur1 = conn1.cursor()
     cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     sql='''
             SELECT id, create_uid, create_date, write_date, write_uid, origin, product_uom, 
               product_uos_qty, procure_method, product_qty, product_uos, message, 
               location_id, move_id, note, name, date_planned, close_move, company_id, 
               date_close, priority, state, product_id, purchase_id
          FROM procurement_order
          ORDER BY ID;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     for row in old_po:
         product_uos = False
         date_close= False
         date_planned = False
         if row['date_planned']:
             date_planned= ((row['date_planned'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
         if row['date_close']:
             date_close= ((row['date_close'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
         if row['product_uos']:
             product_uos= float(row['product_uos'])
             
         vals = {
                    'origin': row['origin'] or False,
                    'product_uom':row['product_uom'] or False,
                    'product_uos_qty':row['product_uos_qty'] or False,
                    'procure_method': row['procure_method'] or False,
                    'product_qty':float(row['product_qty']) or False,
                    'product_uos':product_uos or False,
                    'message': row['message'] or False,
                    'location_id':row['location_id'] or False,
                    #'move_id':row['move_id'] or False,
                    'note': row['note'] or False,
                    'name':row['name'] or False,
                    'date_planned':date_planned or False,
                    'close_move': row['close_move'] or False,
                    'company_id':row['company_id'] or False,
                    'date_close':date_close or False,
                    'priority': row['priority'] or False,
                    'state':row['state'] or False,
                    'product_id':row['product_id'] or False,
                    'purchase_id': row['purchase_id'] or False,
                    }
         new_id = oorpc.create('procurement.order', vals)
         cur2.execute('commit')
         sql = '''
         update procurement_order set id = %s where id = %s 
         ''' %(row['id'],new_id)
         cur2.execute(sql)
         cur2.execute('commit')
         cur2.execute('''SELECT setval('sale_order_id_seq', (SELECT MAX(id) FROM sale_order))''')
         cur2.execute('commit')
         
def import_sale_order_line(oorpc): 
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
     cur1 = conn1.cursor()
     cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
     sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid, product_uos_qty, 
           product_uom, sequence, order_id, price_unit, product_uom_qty, 
           discount, product_uos, name, company_id, salesman_id, state, 
           product_id, order_partner_id, th_weight, invoiced, type, address_allotment_id, 
           margin, purchase_price, procurement_id, delay, product_packaging
         FROM sale_order_line 
         order by id;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     number = 1
     for row in old_po:
         purchase_price = False
         write_date= False
         date_order = False
         product_uos_qty = False
         if row['purchase_price']:
             purchase_price = float(row['purchase_price'])
         if row['product_uos_qty']:
             purchase_price = float(row['product_uos_qty'])
            
         vals = {
                    'product_uos_qty': product_uos_qty or False,
                    'product_uom':row['product_uom'] or False,
                    'sequence':row['sequence'] or False,
                    'order_id': row['order_id'] or False,
                    'price_unit':float(row['price_unit']) or False,
                    'product_uom_qty':float(row['product_uom_qty']) or False,
                    'discount': float(row['discount']) or False,
                    'product_uos':row['product_uos'] or False,
                    'name':row['name'] or False,
                    'company_id': row['company_id'] or False,
                    'salesman_id':row['salesman_id'] or False,
                    'state':row['state'] or False,
                    'product_id': row['product_id'] or False,
                    'order_partner_id':row['order_partner_id'] or False,
                    'th_weight':row['th_weight'] or False,
                    'invoiced': row['invoiced'] or False,
                    'type':row['type'] or False,
                    'address_allotment_id':row['address_allotment_id'] or False,
                    'margin': float(row['margin']) or False,
                    'purchase_price':purchase_price,
                    'procurement_id':row['procurement_id'] or False,
                    'delay': row['delay'] or False,
                    'product_packaging':row['product_packaging'] or False,
                    }
         new_id = oorpc.create('sale.order.line', vals)
         cur2.execute('commit')
         sql = '''
         update sale_order_line set id = %s where id = %s 
         ''' %(row['id'],new_id)
         cur2.execute(sql)
         cur2.execute('commit')
         cur2.execute('''SELECT setval('sale_order_line_id_seq', (SELECT MAX(id) FROM sale_order_line))''')
         cur2.execute('commit')
         print number
         number += 1
         
def import_sale_order(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
     cur1 = conn1.cursor()
     cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid,
               origin, picking_policy, 
               order_policy, shop_id, client_order_ref, date_order, partner_id, 
               note, fiscal_position, amount_untaxed, payment_term, company_id, 
               amount_tax, state, pricelist_id, project_id, incoterm,  
               partner_invoice_id, user_id, date_confirm, amount_total, name, 
               partner_shipping_id, shipped, invoice_quantity, section_id,
               margin
          FROM sale_order
          ORDER BY id;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     number = 1
     for row in old_po:
         date_order = False
         write_date= False
         date_order = False
         if row['date_order']:
             date_order= ((row['date_order'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
         if row['date_confirm']:
            date_confirm = ((row['date_order'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
         vals = {
                    'origin': row['origin'] or False,
                    'picking_policy':row['picking_policy'] or False,
                    'order_policy':row['order_policy'] or False,
                    
                    'shop_id':row['shop_id'] or False,
                    'client_order_ref':row['client_order_ref'] or False,
                    'date_order':date_order or False,
                    'partner_id':row['partner_id'] or False,
                    
                    'note': row['note'] or False,
                    'fiscal_position': row['fiscal_position'] or False,
                    'amount_untaxed':float(row['amount_untaxed']) or False,
                    'payment_term':row['payment_term'] or False,
                    'company_id':row['company_id'] or False,
                    'amount_tax':float(row['amount_tax']) or False,
                    'state':row['state'] or False,
                    'pricelist_id':row['pricelist_id'] or False,
                    
                    'project_id':row['project_id'] or False,
                    'incoterm':row['incoterm'] or False,
                    'user_id':row['user_id'] or False,
                    'date_confirm':date_confirm or False,
                    
                    'amount_total':float(row['amount_total']) or False,
                    'name':row['name'] or False,
                    'partner_shipping_id':row['partner_id'] or False,
                    'shipped':row['shipped'] or False,
                    'partner_invoice_id':row['partner_id'] or False,
                    'invoice_quantity':row['invoice_quantity'] or False,
                    'section_id':row['section_id'] or False,
                    'margin':row['margin'] and float(row['margin']) or False,
                    }
         new_id = oorpc.create('sale.order', vals)
         cur2.execute('commit')
         sql = '''
         update sale_order set id = %s where id = %s 
         ''' %(row['id'],new_id)
         cur2.execute(sql)
         cur2.execute('commit')
         sql = '''
         update wkf_instance set res_id=%s where res_type='sale.order' and res_id=%s 
         ''' %(row['id'],new_id)
         cur2.execute(sql)
         cur2.execute('commit')
         
         cur2.execute('''SELECT setval('sale_order_id_seq', (SELECT MAX(id) FROM sale_order))''')
         cur2.execute('commit')
         print number
         number += 1

def update_so_workflow(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    so_ids = oorpc.search('sale.order',[('state','in',['manual'])])
    number = 1
    for so_id in so_ids:
        so = oorpc.read('sale.order', so_id, ['state'])
#         if so['state'] == 'progress':
#             oorpc.exec_workflow('sale.order', 'order_confirm', so_id)
        if so['state'] == 'manual':
            oorpc.exec_workflow('sale.order', 'manual_invoice', so_id)
            print number
            number += 1
    #DELETE all Picking
#     cursor2.execute('''TRUNCATE stock_move CASCADE;
#                         TRUNCATE stock_picking CASCADE;''')      
#     cursor2.execute('commit')
    
if __name__ == '__main__':
    (options, args) = define_arg()
#     oorpc = OpenObjectRPC('localhost', 'doukas71', 'admin', 'orangina', '8069')
    oorpc = OpenObjectRPC('localhost', 'doukas70_ok1', 'admin', '1', '8069')
    print 'In progress ...'
   #SO ko can update Work-Flow
   #Da update zo DB template
#     import_sale_config(oorpc)
#     import_sale_shop(oorpc)
#     import_procurement_order(oorpc)

#     import_sale_order(oorpc)
#     import_sale_order_line(oorpc)
#     update_so_workflow(oorpc)
    print 'Done.'
    
    
    
    

