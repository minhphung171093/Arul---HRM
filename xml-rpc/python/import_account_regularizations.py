# -*- coding: utf-8 -*-

import xmlrpclib
import os
import sys
from fileinput import close
os.chdir('../')
current_path = os.getcwd()
sys.path.append(current_path)
from common.oorpc import OpenObjectRPC, define_arg
import xlrd

def import_account_refularization(oorpc):
    output = open(current_path+'/python/XSBP_Regularization.txt', 'wb')
    wb = xlrd.open_workbook(current_path+'/python/XSBP_Regularization.xls')
    wb.sheet_names()
    sh = wb.sheet_by_index(0)
    
    i = -1
    for rownum in range(sh.nrows):
        i += 1
        if i == 0:
            continue
        row_values = sh.row_values(rownum)
        error = False
        try:
            vals = {}
            balance_account_id = oorpc.search('account.account', [('company_id','=',1),('code','=',str(row_values[7]).split('.')[0])])
            if balance_account_id:
                vals.update({'account_ids':[(4,balance_account_id[0])],})
            else:
                error = True
            if not error:
                exist_sequence = oorpc.search('account.regularization', [('company_id','=',1),('sequence','=',row_values[0])]) or False
                if not exist_sequence:
                    debit_account_id = oorpc.search('account.account', [('company_id','=',1),('code','=',str(row_values[3]).split('.')[0])])
                    credit_account_id = oorpc.search('account.account', [('company_id','=',1),('code','=',str(row_values[5]).split('.')[0])])
                    if debit_account_id and credit_account_id:
                        vals.update({'sequence':row_values[0],
                                'name':row_values[1],
                                'balance_calc':row_values[2],
                                'debit_account_id':debit_account_id[0],
                                'credit_account_id':credit_account_id[0],
                                })
                        oorpc.create('account.regularization', vals)
                        print i
                    else:
                        error = True
                else:
                    oorpc.write('account.regularization', exist_sequence, vals)
        except Exception, e:
            error = True
            row_values.append(e)
        if error:
#            error_line = ''
#            for cell in row_values:
#                error_line += str(cell) + ';'
#            error_line += '\n'
#            if len(row_values):
            output.write(str(row_values) + '\n')
    return True

import psycopg2
import psycopg2.extras
db1_conn_string = "host='192.241.125.163' port='5432' dbname='ketoan_xsbp' user='postgres' password='postgres'"

def update_account_move_with_regularization():
    conn1 = psycopg2.connect(db1_conn_string)
    cur1 = conn1.cursor()
    sql ='''
        SELECT id
         FROM account_move
         WHERE regularization_id is null
    '''
    cur1.execute(sql)
    rows = cur1.fetchall()
    i = 1
    for row in rows:
        sql = '''select arh.id from account_regularization arh join account_regularization_rel rel on arh.id = rel.regularization_id
                 where (arh.debit_account_id in (select aml.account_id from account_move_line aml where aml.move_id = %s)
                    or arh.credit_account_id in (select aml.account_id from account_move_line aml where aml.move_id = %s))
                    and rel.account_id in (select aml.account_id from account_move_line aml where aml.move_id = %s)
            '''%(row[0],row[0],row[0])
        cur1.execute(sql)
        res = cur1.fetchall()
        if len(res) == 1:
            sql = '''update account_move
                    set regularization_id = %s
                    where id=%s
            '''%(res[0][0], row[0])
            cur1.execute(sql)
            cur1.execute('commit')
            print i
            i += 1
        if len(res) > 1:
            print res
        if len(res) == 0:
            print 'Next'
        
if __name__ == '__main__':
    (options, args) = define_arg()
#    oorpc = OpenObjectRPC('localhost', 'vinhthai', 'admin', 'vtadmin', '8069')
    oorpc = OpenObjectRPC('192.241.125.163', 'ketoan_xsbp', 'admin', '1', '6069')
    print 'In progress ...'
#     import_account_refularization(oorpc)
    update_account_move_with_regularization()
    print 'Done.'
    
    
    
    

