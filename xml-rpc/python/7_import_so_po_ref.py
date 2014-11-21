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

def import_purchase_invoice_rel(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_purchase_invoice_rel = ['purchase_id', 'invoice_id']
    
    sql ='''
        SELECT purchase_id, invoice_id
         FROM purchase_invoice_rel
         order by purchase_id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        values = '''
                     %s,%s
                 '''%(
                       row['purchase_id'] or 'null' ,row['invoice_id'] or 'null'
                       )
                 
        sql = '''INSERT INTO purchase_invoice_rel(%s)
            VALUES (%s)
            '''%(','.join(map(str,db1_purchase_invoice_rel)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')

def import_purchase_order_line_invoice_rel(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_purchase_invoice_rel = ['order_line_id', 'invoice_id']
    
    sql ='''
        SELECT order_line_id, invoice_id
        FROM purchase_order_line_invoice_rel;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        values = '''
                     %s,%s
                 '''%(
                       row['order_line_id'] or 'null' ,row['invoice_id'] or 'null'
                       )
                 
        sql = '''INSERT INTO purchase_order_line_invoice_rel(%s)
            VALUES (%s)
            '''%(','.join(map(str,db1_purchase_invoice_rel)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')

def import_sale_order_invoice_rel(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_sale_order_invoice_rel = ['order_id', 'invoice_id']
    
    sql ='''
        SELECT order_id, invoice_id
          FROM sale_order_invoice_rel
          order by order_id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        values = '''
                     %s,%s
                 '''%(
                       row['order_id'] or 'null' ,row['invoice_id'] or 'null'
                       )
                 
        sql = '''INSERT INTO sale_order_invoice_rel(%s)
            VALUES (%s)
            '''%(','.join(map(str,db1_sale_order_invoice_rel)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')

def import_sale_order_line_invoice_rel(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_sale_order_line_invoice_rel = ['order_line_id', 'invoice_id']
    
    sql ='''
        SELECT order_line_id, invoice_id
          FROM sale_order_line_invoice_rel;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        values = '''
                     %s,%s
                 '''%(
                       row['order_line_id'] or 'null' ,row['invoice_id'] or 'null'
                       )
                 
        sql = '''INSERT INTO sale_order_line_invoice_rel(%s)
            VALUES (%s)
            '''%(','.join(map(str,db1_sale_order_line_invoice_rel)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')
    
def import_account_invoice_line_tax(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    account_invoice_line_tax = ['invoice_line_id', 'tax_id']
    
    sql ='''
        SELECT invoice_line_id, tax_id
          FROM account_invoice_line_tax;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        values = '''
                     %s,%s
                 '''%(
                       row['invoice_line_id'] or 'null' ,row['tax_id'] or 'null'
                       )
                 
        sql = '''INSERT INTO account_invoice_line_tax(%s)
            VALUES (%s)
            '''%(','.join(map(str,account_invoice_line_tax)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')

def import_account_invoice_tax(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    account_invoice_line_tax = ['invoice_line_id', 'tax_id']
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, tax_amount, 
           account_id, sequence, company_id, invoice_id, manual, base_amount, 
           base_code_id, amount, base, tax_code_id, name
       FROM account_invoice_tax;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
         tax_amount = False
         write_date= False
         date_order = False
         product_uos_qty = False
         if row['tax_amount']:
             tax_amount = float(row['tax_amount'])
         if row['base_amount']:
             base_amount = float(row['base_amount'])
         if row['amount']:
             amount = float(row['amount'])
         if row['base']:
             base = float(row['base'])
            
         vals = {
                    'tax_amount': tax_amount or False,
                    'account_id':row['account_id'] or False,
                    'sequence':row['sequence'] or False,
                    'company_id': row['company_id'] or False,
                    'invoice_id':row['invoice_id'],
                    'manual':row['manual'] or False,
                    'base_amount':base_amount,
                    'base_code_id':row['base_code_id'] or False,
                    'amount':amount or False,
                    'base':base or False,
                    'tax_code_id':row['tax_code_id'] or False,
                    'name':row['name'] or False
                    }
         new_id = oorpc.create('account.invoice.tax', vals)
         cur2.execute('commit')
         sql = '''
         update account_invoice_tax set id = %s where id = %s 
         ''' %(row['id'],new_id)
         cur2.execute(sql)
         cur2.execute('commit')
         cur2.execute('''SELECT setval('account_invoice_tax_id_seq', (SELECT MAX(id) FROM account_invoice_tax))''')
         cur2.execute('commit')
        
def import_res_currency_rate(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
    delete from res_currency_rate;
    commit;
    '''
    cursor2.execute(sql)
    
    account_invoice_line_tax = ['invoice_line_id', 'tax_id']
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, currency_id, 
        rate, name, currency_rate_type_id
        FROM res_currency_rate
        where id in (1,2)
        order by id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
         currency_id = False
         rate = False
         name = False
         if row['rate']:
             rate = float(row['rate']) or False
         currency_id = row['currency_id']
         if currency_id == 2:
             currency_id = 3
         if row['name']:
             name= ((row['name'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
         
         vals = {
                    'currency_id': currency_id or False,
                    'rate':rate or False,
                    'name':name or False,
                    'currency_rate_type_id':row['currency_rate_type_id'] or False,
                    }
         new_id = oorpc.create('res.currency.rate', vals)
         cur2.execute('commit')
         sql = '''
         update res_currency_rate set id = %s where id = %s 
         ''' %(row['id'],new_id)
         cur2.execute(sql)
         cur2.execute('commit')
         cur2.execute('''SELECT setval('res_currency_rate_id_seq', (SELECT MAX(id) FROM res_currency_rate))''')
         cur2.execute('commit')   

if __name__ == '__main__':
    (options, args) = define_arg()
#      'orangina'
    oorpc = OpenObjectRPC('localhost', 'doukas70_temp', 'admin','1', '8069')
    print 'In progress ...'
#     import_purchase_invoice_rel(oorpc)
#     import_purchase_order_line_invoice_rel(oorpc)
#     import_sale_order_invoice_rel(oorpc)
#     import_sale_order_line_invoice_rel(oorpc)

#     import_account_invoice_line_tax(oorpc)
#     import_account_invoice_tax(oorpc)
    
#     import_res_currency_rate(oorpc)
    print 'Done.'
    
    
    
    

