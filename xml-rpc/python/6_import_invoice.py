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

map_cur = {1:1,
           2:3,}

def import_account_invoice_line(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, origin, uos_id, 
       account_id, name, invoice_id, price_unit, price_subtotal, company_id, 
       note, discount, account_analytic_id, quantity, partner_id, product_id
      FROM account_invoice_line;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        
        price_unit= False
        price_subtotal = False
        discount = False
        if row['price_unit']:
             price_unit = float(row['price_unit'])
        if row['price_subtotal']:
             price_subtotal = float(row['price_subtotal'])
        if row['discount']:
             discount = float(row['discount'])
        
        vals = {
                    'origin':row['origin'] or False,
                    'uos_id': row['uos_id'] or False,
                    'account_id':row['account_id'] or False,
                    'name':row['name'] or False,
                    'invoice_id':row['invoice_id'] or False,
                    'price_unit':price_unit or False,
                    'price_subtotal':price_subtotal or False,
                    'company_id':row['company_id'] or False,
                    'note':row['note'] or False,
                    'discount':discount or False,
                    'account_analytic_id':row['account_analytic_id'] or False,
                    'quantity':row['quantity'] or False,
                    'partner_id':row['partner_id'] or False,
                    'product_id':row['product_id'] or False,
                }
        new_id = oorpc.create('account.invoice.line', vals)
        sql = '''
         update account_invoice_line set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_invoice_line_id_seq', (SELECT MAX(id) FROM account_invoice_line))''')
        cur2.execute('commit')
        
def import_account_invoice(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
    sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid, origin, comment, 
           date_due, check_total, reference, payment_term, "number", journal_id, 
           currency_id,  partner_id, fiscal_position, 
           user_id, partner_bank_id,  reference_type, 
           company_id, amount_tax, state, type, internal_number, account_id, 
           reconciled, residual, move_name, date_invoice, period_id, amount_untaxed, 
           move_id, amount_total, name
          FROM account_invoice
          order by id;
     '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        check_total = False
        amount_tax = False
        residual = False
        date_invoice = False
        amount_untaxed = False
        date_due = False
        if row['check_total']:
             check_total= float(row['check_total'])
        if row['amount_tax']:
             amount_tax= float(row['amount_tax'])
        if row['residual']:
            residual= float(row['residual'])
        if row['amount_untaxed']:
            amount_untaxed= float(row['amount_untaxed'])
        if row['amount_total']:
            amount_total= float(row['amount_total'])
        if row['date_invoice']:
             date_invoice= ((row['date_invoice'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date_due']:
             date_due= ((row['date_due'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        vals = {
                    'origin':row['origin'] or False,
                    'comment': row['comment'] or False,
                    'date_due':date_due or False,
                    'check_total':check_total or False,
                    'reference':row['reference'] or False,
                    'payment_term':row['payment_term'] or False,
                    'number':row['number'] or False,
                    'journal_id': row['journal_id'] or False,
                    'currency_id': map_cur[row['currency_id']],
                    'partner_id':row['partner_id'] or False,
                    'fiscal_position':row['fiscal_position'] or False,
                    'user_id':row['user_id'] or False,
                    'partner_bank_id':row['partner_bank_id'] or False,
                    'reference_type': row['reference_type'] or False,
                    'company_id':row['company_id'] or False,
                    'amount_tax':amount_tax or False,
                    'state':row['state'] or False,
                    'type':row['type'] or False,
                    'internal_number':row['internal_number'] or False,
                    'account_id': row['account_id'] or False,
                    'reconciled':row['reconciled'] or False,
                    'residual':residual or False,
                    'move_name':row['move_name'] or False,
                    'date_invoice':date_invoice or False,
                    
                    'period_id':row['period_id'] or False,
                    'amount_untaxed': amount_untaxed or False,
                    'move_id':row['move_id'] or False,
                    'amount_total':amount_total or False,
                    'name':row['name'] or False,
                }
        new_id = oorpc.create('account.invoice', vals)
        sql = '''
         update account_invoice set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_invoice_id_seq', (SELECT MAX(id) FROM account_invoice))''')
        cur2.execute('commit')
         
def update_invoice_workflow(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    inv_ids = oorpc.search('account.invoice',[('state','in',['open'])])
    number = 1
    for inv_id in inv_ids:
#         inv = oorpc.read('account.invoice', inv_id, ['state'])
#         if inv['state'] == 'open':
#             cursor2.execute('UPDATE account_invoice SET move_id = Null WHERE id=%s'%(inv_id))
#             cursor2.execute('commit')
#             oorpc.exec_workflow('account.invoice', 'invoice_open', inv_id)
#             cursor2.execute('commit')
#             cursor2.execute('SELECT move_id FROM account_invoice where id=%s'%(inv_id))
#             move_ids = cursor2.fetchall()
#             for move in move_ids:
#                 if move['move_id']:
#                     cursor2.execute('UPDATE account_invoice SET move_id = Null WHERE id=%s'%(inv_id))
#                     cursor2.execute('DELETE FROM account_move_line WHERE move_id=%s'%(move['move_id']))
#                     cursor2.execute('DELETE FROM account_move WHERE id=%s'%(move['move_id']))
            sql ='''
                 SELECT move_id
                  FROM account_invoice
                  where id=%s
             '''%(inv_id)
            cursor1.execute(sql)
            old_po = cursor1.fetchall()
            for row in old_po:
#                 oorpc.write('account.invoice', [inv_id], {'move_id':row['move_id']})
                cursor2.execute('UPDATE account_invoice SET move_id = %s WHERE id=%s'%(row['move_id'],inv_id))
            cursor2.execute('commit')
            print number
            number += 1

def update_invoice_xsbp_workflow(oorpc):
    inv_ids = oorpc.search('account.invoice',[('state','in',['draft'])])
    number = 1
    for inv_id in inv_ids:
        try:
            oorpc.exec_workflow('account.invoice', 'invoice_open', inv_id)
            print number
            number += 1
        except Exception, ex:
            pass
            
if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('192.241.125.163', 'ketoan_xsbp', 'admin', '1', '6069')
    print 'In progress ...'
   
#     import_account_invoice(oorpc)
#     import_account_invoice_line(oorpc)
#     update_invoice_workflow(oorpc)
    update_invoice_xsbp_workflow(oorpc)
    print 'Done.'
    
    
    
    

