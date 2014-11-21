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

def import_account_move(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql='''
           SELECT id, create_uid, create_date, write_date, write_uid, name, state, 
               ref, company_id, journal_id, period_id, narration, date, balance, 
               partner_id, to_check, internal_sequence_number
          FROM account_move
          order by id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        date = False
        balance = False
        if row['balance']:
            balance = float(row['balance']) 
        if row['date']:
            date= ((row['date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        vals = {
                    'name':row['name'] or False,
                    'state': row['state'] or False,
                    'ref':row['ref'] or False,
                    'company_id':row['company_id'] or False,
                    'journal_id':row['journal_id'] or False,
                    'period_id':row['period_id'] or False,
                    'narration': row['narration'] or False,
                    'date':date or False,
                    'balance': balance or False,
                    'partner_id':row['partner_id'] or False,
                    'to_check':row['to_check'] or False,
                    'internal_sequence_number': row['internal_sequence_number'] or False,
                }
        new_id = oorpc.create('account.move', vals)
        sql = '''
         update account_move set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_move_id_seq', (SELECT MAX(id) FROM account_move))''')
        cur2.execute('commit')

def import_account_move_line_reconcile(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql ='''
          SELECT id, create_uid, create_date, write_date, write_uid, name, type
          FROM account_move_reconcile
          ORDER BY id;
     '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        vals = {
                    'name':row['name'] or False,
                    'type':row['type'] or False,
                }
        new_id = oorpc.create('account.move.reconcile', vals)
        sql = '''
         update account_move_reconcile set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_move_reconcile_id_seq', (SELECT MAX(id) FROM account_move_reconcile))''')
        cur2.execute('commit')
       
def import_account_move_line(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, statement_id, 
               journal_id, currency_id, date_maturity, partner_id, reconcile_partial_id, 
               blocked, analytic_account_id, credit, centralisation, company_id, 
               tax_code_id, state, debit, ref, account_id, period_id, date_created, 
               date, move_id, name, reconcile_id, tax_amount, product_id, account_tax_id, 
               product_uom_id, amount_currency, quantity
          FROM account_move_line
          order by id;
     '''
        
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        currency_id = False
        date_maturity =False
        credit = False
        debit = False
        date_created = False
        date = False
        tax_amount = False
        amount_currency = False
        quantity = False
        
        if row['currency_id']:
            currency_id = map_cur[row['currency_id']]
        if row['credit']:
            credit= float(row['credit'])
        if row['debit']:
            debit= float(row['debit'])
        if row['tax_amount']:
            tax_amount= float(row['tax_amount'])
        if row['amount_currency']:
            amount_currency= float(row['amount_currency'])
        if row['quantity']:
            quantity= float(row['quantity'])
            
        if row['date_maturity']:
            date_maturity = ((row['date_maturity'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date']:
            date = ((row['date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date_created']:
            date_created = ((row['date_created'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        vals = {
                    'statement_id':row['statement_id'] or False,
                    #'address_id': row['address_id'] or False,
                    'journal_id':row['journal_id'] or False,
                    'currency_id': currency_id or False,
                    'date_maturity':date_maturity or False,
                    'partner_id':row['partner_id'] or False,
                    'reconcile_partial_id':row['reconcile_partial_id'] or False,
                    'blocked': row['blocked'],
                    'analytic_account_id':row['analytic_account_id'] or False,
                    'credit':credit or False,
                    'centralisation':row['centralisation'] or False,
                    'tax_code_id':row['tax_code_id'] or False,
                    'state': row['state'] or False,
                    'debit':debit or False,
                    'ref': row['ref'] or False,
                    'account_id':row['account_id'] or False,
                    'period_id': row['period_id'] or False,
                    'date_created':date_created,
                    'date':date,
                    'move_id':row['move_id'] or False,
                    'name':row['name'] or False,
                    'reconcile_id':row['reconcile_id'] or False,
                    'tax_amount':tax_amount or False,
                    'product_id':row['product_id'] or False,
                    'account_tax_id':row['account_tax_id'] or False,
                    'product_uom_id':row['product_uom_id'] or False,
                    'amount_currency':amount_currency or False,
                    'quantity':quantity or False,
                }
        new_id = oorpc.create('account.move.line', vals)
        sql = '''
         update account_move_line set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_move_line_id_seq', (SELECT MAX(id) FROM account_move_line))''')
        cur2.execute('commit')

def import_account_voucher_line(oorpc):

    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_ccount_voucher_line = ['id', 'create_uid', 'create_date', 'write_date', 'write_uid','reconcile',
                           'voucher_id', 'amount_unreconciled', 'account_id', 'name', 'move_line_id',
                           'untax_amount','company_id','amount_original','amount','account_analytic_id','type']
    
    sql='''
           SELECT id, create_uid, create_date, write_date, write_uid, reconcile, 
               voucher_id, amount_unreconciled, account_id, name, move_line_id, 
               untax_amount, company_id, amount_original, amount, account_analytic_id, 
               type
          FROM account_voucher_line
          order by id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    
    number = 1
    for row in old_po:
        date_due = False
        write_date = False
        amount_unreconciled = False
        untax_amount = False
        create_date = False
        
        if row['create_date']:
            create_date= ((row['create_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['write_date']:
            write_date= ((row['write_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['amount_unreconciled']:
            amount_unreconciled= float(row['amount_unreconciled'])
        
        if row['untax_amount']:
            untax_amount= float(row['untax_amount'])
        
        if row['amount_original']:
            amount_original= float(row['amount_original'])
            
        values = '''
                     %s,%s,'%s',%s,%s,%s,
                     %s,%s,%s,'%s',%s,
                     %s,%s,%s,%s,%s,'%s'
                 '''%(
                       row['id'],row['create_uid'] or 'null',create_date or 'null',write_date or 'null',row['write_uid'] or 'null',row['reconcile'] or 'null',
                       row['voucher_id'] or 'null' ,amount_unreconciled or 'null',row['account_id'] or 'null',row['name'] or 'null',row['move_line_id'] or 'null',
                       untax_amount or 'null' , row['company_id'] or 'null',amount_original or 'null',row['amount'] or 'null',row['account_analytic_id'] or 'null',row['type'] or 'null'
                       )
                 
        sql = '''INSERT INTO account_voucher_line(%s)
            VALUES (%s)
            RETURNING id'''%(','.join(map(str,db1_ccount_voucher_line)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')
        print number
        number += 1
        cur2.execute('''SELECT setval('account_voucher_line_id_seq', (SELECT MAX(id) FROM account_voucher_line))''')
        cur2.execute('commit')
    
def import_account_voucher(oorpc):

    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    
    db1_account_voucher = ['id','create_date','create_uid','write_date','write_uid', 'comment','date_due','is_multi_currency','reference','number','company_id',
                                    'narration','partner_id','payment_rate_currency_id','pay_now','writeoff_acc_id',
                                    'state','pre_line','payment_rate','type','payment_option','account_id',
                                    'period_id','date','move_id','tax_id','tax_amount','name','analytic_id',
                                    'journal_id','amount','active']
    
    sql='''
           SELECT id,create_date,create_uid,write_date,write_uid, comment, date_due, is_multi_currency, reference, number, company_id, 
               narration, partner_id, payment_rate_currency_id, pay_now, writeoff_acc_id, 
               state, pre_line, payment_rate, type, payment_option, account_id, 
               period_id, date, move_id, tax_id, tax_amount, name, analytic_id, 
               journal_id, amount
          FROM account_voucher
          order by id;
    '''
    
    
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        date_due = False
        date = False
        payment_rate = False
        amount = False
        tax_amount = False
        period_id = False
        payment_rate_currency_id = False
        if row['payment_rate']:
            payment_rate = float(row['payment_rate']) 
        if row['tax_amount']:
            tax_amount = float(row['tax_amount']) 
        if row['amount']:
            amount = float(row['amount']) 
            
        if row['date_due']:
            date_due= ((row['date_due'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['date']:
            date= ((row['date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if row['payment_rate_currency_id']:
            payment_rate_currency_id = map_cur[row['payment_rate_currency_id']]
        
        if row['period_id']:
            period_id = row['period_id'] 
            
        
        values = '''
                     %s,'%s',%s,'%s',%s,'%s',%s,%s,'%s','%s',%s,
                     %s,%s,%s,'%s',%s,
                     '%s',%s,%s,'%s','%s',%s,
                     %s,'%s',%s,%s,%s,'%s',%s,
                    %s, %s,%s
                 '''%(
                       row['id'] or 'null',row['create_date'] or 'null',row['create_uid'] or 'null',row['write_date'] or 'null',row['write_uid'] or 'null',row['comment'] or 'null',date_due or 'null' ,row['is_multi_currency'] or 'null',row['reference'] or 'null' ,row['number'] or 'null',row['company_id'] or 'null',
                       row['narration'] or 'null' ,row['partner_id'] or 'null',payment_rate_currency_id or 'null' ,row['pay_now'] or 'null',row['writeoff_acc_id'] or 'null' ,
                       row['state'],row['pre_line'],payment_rate or 'null',row['type'] or 'null',row['payment_option'] or 'null',row['account_id'],
                       period_id or 'null',date or 'null',row['move_id'] or 'null',row['tax_id'] or 'null',tax_amount or 'null',row['name'] or 'null',row['analytic_id'] or 'null',
                       row['journal_id'] or 'null',amount or False,'True'
                     )
                 
        sql = '''INSERT INTO account_voucher(%s)
            VALUES (%s)
            '''%(','.join(map(str,db1_account_voucher)),values)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_voucher_id_seq', (SELECT MAX(id) FROM account_voucher))''')
        cur2.execute('commit')        
    
if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('localhost', 'doukas70_temp', 'admin', '1', '8069')
    print 'In progress ...'
#     import_account_move(oorpc)
#     import_account_move_line_reconcile(oorpc)
#     import_account_move_line(oorpc)

#     import_account_voucher(oorpc)
#     import_account_voucher_line(oorpc)
    print 'Done.'
    
    
    
    

