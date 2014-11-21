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

def import_product_categrory():
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()
    
    cursor2.execute('TRUNCATE product_category CASCADE')      
    cursor2.execute('commit')
        
    db1_product_category = ['parent_left', 'parent_right', 'create_uid', 'create_date', 'write_date',
                           'write_uid', 'name', 'sequence', 'parent_id', 'type','id']
    
    db2_product_category = ['parent_left', 'parent_right', 'create_uid', 'create_date', 'write_date',
                           'write_uid', 'name', 'sequence', 'parent_id', 'type','id']
    
    sql = "SELECT %s FROM product_category order by id"%(','.join(map(str,db1_product_category)))
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    
    
    number = 1
    for row in old_po:
        values = '''
                     %s,%s,%s,'%s','%s',
                     %s,'%s',%s,%s,'%s', %s
                 '''%(
                       'null','null',row[2],'2014-01-01','2014-01-01',
                       row[5] or 'null' , row[6] or 'null',row[7] or 'null',row[8] or 'null',row[9] or 'null',row[10] or 'null'
                       )
                 
        sql = '''INSERT INTO product_category(%s)
            VALUES (%s)
            RETURNING id'''%(','.join(map(str,db2_product_category)),values)
        cursor2.execute(sql)      
        cursor2.execute('commit')
        print number
        number += 1
        
    sql = "SELECT parent_left,parent_right,id FROM product_category order by id"
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        sql = ' update product_category set parent_left = %s ,parent_right = %s where id = %s' %(row[0],row[1],row[2])
        cursor2.execute(sql)      
        cursor2.execute('commit')
    return True

def import_product(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor2.execute('TRUNCATE product_template CASCADE')
    cursor2.execute('TRUNCATE product_product CASCADE')      
    cursor2.execute('commit')
    
    cur2.execute('ALTER TABLE product_product ALTER COLUMN product_tmpl_id DROP NOT NULL')
    
    sql ='''
        Select 
        pt.id pt_id,
        pp.id pp_id,
        ean13, 
        default_code,
        name_template,
        supply_method, 
        standard_price,
        uom_id,
        description_purchase  ,
        cost_method,
        track_incoming,
        sale_ok, 
        purchase_ok,
        track_outgoing,
        state,
        loc_rack,
        price_margin,
        description,
        valuation,weight_net,volume,loc_row,description_sale,procure_method,
        variants,rental
        from product_product pp inner join product_template pt on pp.product_tmpl_id = pt.id
        order by pp.id
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        
        vals = {
                    'default_code':row['default_code'] or False,
                    'name':row['name_template'] or False,
                    'ean13': row['ean13'] or False,
                    'supply_method':row['supply_method'] or False,
                    'standard_price': float(row['standard_price']) or False,
                    'uom_id':row['uom_id'] or False,
                    'description_purchase': row['description_purchase'] or False,
                    
                    'cost_method': row['cost_method'] or False,
                    'track_incoming':row['track_incoming'] or False,
                    'sale_ok': row['sale_ok'] or False,
                    'purchase_ok':row['purchase_ok'] or False,
                    
                    'track_outgoing': row['track_outgoing'] or False,
                    'state':row['state'] or False,
                    'loc_rack':row['loc_rack'] or False,
                    'price_margin':float(row['price_margin']) or False,
                    'description':row['description'] or False,
                    'valuation':row['valuation'] or False,
                    'volume':row['volume'] or False,
                    'loc_row':row['loc_row'] or False,
                    'description_sale': row['description_sale'] or False,
                    'procure_method':row['procure_method'] or False,
                    'variants':row['variants'] or False,
                    'rental':row['rental'] or False
                    }
        new_id = oorpc.create('product.product', vals)
        
        sql ='''
            update product_product set id = %s,product_tmpl_id = null where id = %s
        ''' %(row['pp_id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        
        sql ='''
            update product_template set id = %s where id = %s
        ''' %(row['pt_id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        
        sql ='''
            update product_product set product_tmpl_id = %s where id = %s
        ''' %(row['pt_id'],row['pp_id'])
        cur2.execute(sql)
        cur2.execute('commit')
        print number
        number += 1
        
    cur2.execute('ALTER TABLE product_product ALTER COLUMN product_tmpl_id SET NOT NULL')
    cur2.execute('commit')

def import_product_saleprice(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        Select 
        pt.id pt_id,
        pp.id pp_id,
        ean13, 
        default_code,
        name_template,
        supply_method, 
        standard_price,
        uom_id,
        description_purchase  ,
        cost_method,
        track_incoming,
        sale_ok, 
        purchase_ok,
        track_outgoing,
        state,
        loc_rack,
        price_margin,
        description,
        valuation,weight_net,volume,loc_row,description_sale,procure_method,
        variants,rental,
        list_price
        from product_product pp inner join product_template pt on pp.product_tmpl_id = pt.id
        order by pp.id
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    number = 1
    for row in old_po:
        
        sql ='''
            update product_template set list_price = %s where id = %s
        ''' %(row['list_price'],row['pt_id'])
        cur2.execute(sql)
        cur2.execute('commit')
        
        print number
        number += 1
        
    
def res_user(oorpc):
 
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
#      cursor1 = conn1.cursor()
#      cursor2 = conn2.cursor()
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
     cursor2.execute('''
     ALTER TABLE res_groups_users_rel ALTER COLUMN uid DROP NOT NULL;
     ALTER TABLE ir_ui_view_sc ALTER COLUMN user_id DROP NOT NULL;
     ''')
     cursor2.execute('commit')
    
     sql ='''
      SELECT id, name, active, login, password, email, context_tz, signature, 
       context_lang, company_id,  menu_id, menu_tips, date, action_id, user_email, context_section_id, 
       context_department_id, gmail_password, gmail_user, context_project_id
      FROM res_users order by id
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     number = 1
     for row in old_po:
         vals = {
                    'name':row['name'] or False,
                    'active': row['active'] or False,
                    'login':row['login'] or False,
                    'password': row['password'] or False,
                    'email':row['email'] or False,
                    'signature': row['signature'] or False,
                    'company_id': row['company_id'] or False,
                    'menu_id':row['menu_id'] or False,
                    'date':row['date'] and row['date'].strftime(DATETIME_FORMAT) or False,
                    'action_id':row['action_id'] or False,
                    'user_email':row['user_email'] or False,
                    'gmail_password':row['gmail_password'] or False,
                    'gmail_user':row['gmail_user'] or False,
                    }
         if row['id'] == 1:
             oorpc.write('res.users',[1], vals)
         else:
             #Neu ko phai admin thi tao User moi
            try:
                new_id = oorpc.create('res.users',vals)
                #Update lai ID cua User 61 move wa 70
                sql ='''
                update res_groups_users_rel set uid = NULL where uid=%s;
                update ir_ui_view_sc set user_id = NULL where user_id=%s;
                delete from res_company_users_rel where user_id=%s;
                update res_users set id = %s where id = %s;
                update res_groups_users_rel set uid = %s where uid IS NULL;
                update ir_ui_view_sc set user_id = %s where user_id IS NULL;
                insert into res_company_users_rel values(1,%s);
                ''' %(new_id,new_id,new_id,row['id'],new_id,row['id'],row['id'],row['id'])
                cursor2.execute(sql)
                cursor2.execute('commit')
            except:
                pass
         print number
         number += 1
     
     cursor2.execute('''
     ALTER TABLE res_groups_users_rel ALTER COLUMN uid SET NOT NULL;
     ALTER TABLE ir_ui_view_sc ALTER COLUMN user_id SET NOT NULL;
     ''')
     cursor2.execute('commit')   
     return 1
 
def update_res_company(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
#      cur1 = conn1.cursor()
#      cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     sql ='''
              select * from res_company where id = 1
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     for row in old_po:
         sql ='''
             update res_company set partner_dd = %s where id =1
         ''' %(row['partner_id'])
         cur2.execute(sql)
         cur2.execute('commit')
     cur2.execute('ALTER TABLE res_company ALTER COLUMN partner_id set NOT NULL')
     cur2.execute('commit')
         
def import_res_partner(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
     
#      cur1 = conn1.cursor()
#      cur2 = conn2.cursor()
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
     #Remove Partner co ID=4 de khoi bi trung khi update
     part_ids = oorpc.search('res.users',[('name','=','Template User'),('active','=',False)])
     oorpc.delete('res.users', part_ids)
     part_ids = oorpc.search('res.partner',[('name','=','Template User')])
     oorpc.delete('res.partner', part_ids)
     
     db1_res_partner = ['id', 'create_uid', 'create_date', 'write_date', 'write_uid','comment',
                       'ean13', 'color', 'date', 'active', 'lang', 'customer', 'credit_limit', 'user_id', 
                       'name', 'title', 'company_id', 'website', 'parent_id', 'employee', 'supplier', 
                       'ref', 'vat', 'section_id', 'opt_out', 'last_reconciliation_date', 'debit_limit', 
                       'date_partnership', 'partner_latitude', 'partner_weight', 'date_localization', 
                       'activation', 'partner_longitude', 'date_review_next', 'date_review', 'grade_id',
                       'display_name'
                       ]
     #Ko insert thang partner cua Company
     sql ='''
         SELECT id, create_uid, create_date, write_date, write_uid, comment, 
           ean13, color, date, active, lang, customer, credit_limit, user_id, 
           name, title, company_id, website, parent_id, employee, supplier, 
           ref, vat, section_id, opt_out, last_reconciliation_date, debit_limit, 
           date_partnership, partner_latitude, partner_weight, date_localization, 
           activation, partner_longitude, date_review_next, date_review, 
           grade_id
          FROM res_partner
          WHERE id not in (select partner_id from res_company)
          order by id;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     
     #De khoi trung Partner co ID=2 ben V7, update max id tu v61
     if len(old_po):
         max_id = old_po[len(old_po)-1]['id'] + 1
         cursor2.execute('ALTER TABLE res_users ALTER COLUMN partner_id DROP NOT NULL')
         cursor2.execute('commit')
         cursor2.execute('update res_users set partner_id = null where id=1')
         cursor2.execute('commit')
         cursor2.execute('''
            ALTER TABLE mail_followers ALTER COLUMN partner_id DROP NOT NULL;
            update mail_followers set partner_id = null where partner_id in (select id from res_partner where name='Administrator');
            delete from mail_message;
            update res_partner set id = %s where name='Administrator';
            update mail_followers set partner_id = %s where partner_id is null;
            ALTER TABLE mail_followers ALTER COLUMN partner_id SET NOT NULL;
            update res_users set partner_id = %s where id=1;
         '''%(max_id,max_id,max_id))
         cursor2.execute('commit')
     
     cursor2.execute('ALTER TABLE res_partner ALTER COLUMN notification_email_send DROP NOT NULL')
     cursor2.execute('commit')
     
     number = 1
     for row in old_po:
        date_order = False
        write_date= False
        date = False
        name = False
        if row['create_date']:
          create_date = row['create_date'] and (row['create_date'] - relativedelta(hours=7)).strftime(DATETIME_FORMAT) or 'null'
        if row['write_date']:
          write_date = row['write_date'] and (row['write_date'] - relativedelta(hours=7)).strftime(DATETIME_FORMAT) or 'null'
        if row['date']:
           date= row['date'] and (row['date'] - relativedelta(hours=7)).strftime(DATETIME_FORMAT) or 'null'
        if row['name']:
            name = row['name'].replace("'"," ")  
        values = '''
                    %s,%s,'%s','%s',%s,'%s',
                    '%s',%s,'%s',%s,'%s',%s,%s,%s,
                    '%s','%s',%s,'%s',%s,%s,%s,
                    '%s','%s',%s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,%s,
                    '%s'
                '''%(
                      row['id'],row['create_uid'] ,create_date or 'null',write_date or 'null',row['write_uid'] or 'null',row['comment'] or 'null',
                      row['ean13'] or 'null' , row['color'] or 'null',date or 'null',row['active'] or 'null',row['lang'] or 'null',row['customer'] or 'null',row['credit_limit'] or 'null',row['user_id'] or 'null',
                      name or 'null',row['title'] or 'null',row['company_id'] or 'null',row['website'] or 'null',row['parent_id'] or 'null',row['employee'] or 'null',row['supplier'] or 'null',
                      row['ref'] or 'null',row['vat'] or 'null',row['section_id'] or 'null',row['opt_out'] or 'null','null',row['debit_limit'] or 'null',
                      'null',row['partner_latitude'] or 'null',row['partner_weight'] or 'null', 'null',
                      row['activation'] or 'null',row['partner_longitude'] or 'null', 'null','null',row['grade_id'] or 'null',
                      name or 'null'#Thieu field display_name
                      )
        values = values.replace("'null'","Null")
        
        sql = '''INSERT INTO res_partner(%s)
           VALUES (%s)
           RETURNING id'''%(','.join(map(str,db1_res_partner)),values)
        res = cursor2.execute(sql)      
        cursor2.execute('commit')
        
#         if res and res[0]:
#             sql ='''
#                 update res_partner set id = %s where id = %s
#             ''' %(row['pt_id'],row['pp_id'])
#             cur2.execute(sql)
#             cur2.execute('commit')
        
        print number
        number += 1
        
     cursor2.execute('''SELECT setval('res_partner_id_seq', (SELECT MAX(id) + 1 FROM res_partner))''')
     cursor2.execute('commit')
     res_user(oorpc)
     
     cursor2.execute('ALTER TABLE res_partner ALTER COLUMN notification_email_send SET NOT NULL')
     cursor2.execute('commit')
     
#      cur2.execute('ALTER TABLE res_users ALTER COLUMN partner_id SET NOT NULL')
#      cur2.execute('commit')
#      update_res_company(oorpc)
     
def import_account(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    db1_account_account = ['id', 'parent_left', 'parent_right', 'create_uid', 'create_date','write_date',
                           'write_uid', 'code', 'reconcile', 'currency_id', 'user_type','active',
                           'name','level','company_id','shortcut','note','parent_id','currency_mode','type']
    
    sql ='''
        SELECT id, parent_left, parent_right, create_uid, create_date, write_date,write_uid, 
        code, reconcile, currency_id, user_type, active, name, 
           level, company_id, shortcut, note, parent_id, currency_mode,  type
      FROM account_account order by id
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        create_date = row['create_date'] or False
        write_date = row['write_date'] or False
        if create_date:
            create_date = ((row['create_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        if write_date:
            write_date = ((row['write_date'] or 'null') - relativedelta(hours=7)).strftime(DATETIME_FORMAT)
        else:
            write_date = 'null'
        
        values = '''
                     %s, %s, %s, %s, '%s',%s, %s,
                     '%s',%s,%s,%s,%s, '%s',
                     %s,%s,'%s','%s',%s, '%s','%s'
                 '''%(
                       row['id'],'null','null',row['create_uid'], create_date,write_date,row['write_uid'] or 'null' , 
                       row['code'] or 'null',row['reconcile'] or 'null',row['currency_id'] or 'null',row['user_type'] or 'null', row['active'] or 'null', row['name'] or 'null',
                       row['level'] or 'null', row['company_id'] or 'null', row['shortcut'] or 'null',
                       row['note'] or 'null','null',row['currency_mode'] or 'null',row['type'] or 'null'
                       )
        sql = '''INSERT INTO account_account(%s)
            VALUES (%s)
            RETURNING id'''%(','.join(map(str,db1_account_account)),values)
        cursor2.execute(sql)
        cursor2.execute('commit')
    
    sql = "SELECT parent_left,parent_right,id,parent_id,id FROM product_category order by id"
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        sql = ' update account_account set parent_left = %s ,parent_right = %s,parent_id = %s where id = %s' %(row['parent_left'] or 'null',row['parent_right'] or 'null',row['parent_id'] or 'null',row['id'])
        cursor2.execute(sql)      
        cursor2.execute('commit')
    
    cur2.execute('''SELECT setval('account_account_id_seq', (SELECT MAX(id) FROM account_account))''')
    cur2.execute('commit')
    
    return True
    
def import_account_tax(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        delete from account_fiscal_position_tax 
    '''
    cur2.execute(sql)
    cur2.execute('commit')
    
    sql ='''
        delete from account_tax 
    '''
    cur2.execute(sql)
    cur2.execute('commit')
    
        
    db1_account_tax = ['id', 'create_uid', 'create_date', 'write_date', 'write_uid','ref_base_code_id',
                           'domain', 'description', 'ref_tax_code_id', 'sequence', 'account_paid_id',
                           'ref_base_sign','type_tax_use','base_code_id','base_sign','child_depend',
                           'include_base_amount','active','ref_tax_sign','applicable_type','account_collected_id',
                           'company_id','name','tax_code_id','parent_id','amount','python_compute',
                           'tax_sign','python_compute_inv','python_applicable','type','price_include']
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, ref_base_code_id, 
           domain, description, ref_tax_code_id, sequence, account_paid_id, 
           ref_base_sign, type_tax_use, base_code_id, base_sign, child_depend, 
           include_base_amount, active, ref_tax_sign, applicable_type, account_collected_id, 
           company_id, name, tax_code_id, parent_id, amount, python_compute, 
           tax_sign, python_compute_inv, python_applicable, type, price_include
      FROM account_tax 
      order by id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        vals = {
                    'ref_base_code_id':row['ref_base_code_id'] or False,
                    'domain': row['domain'] or False,
                    'description':row['description'] or False,
                    'ref_tax_code_id': row['ref_tax_code_id'] or False,
                    'sequence':row['sequence'] or False,
                    'account_paid_id': row['account_paid_id'] or False,
                    'ref_base_sign': row['ref_base_sign'] or False,
                    'type_tax_use':row['type_tax_use'] or False,
                    'base_sign':row['base_sign'] or False,
                    'child_depend':row['child_depend'] or False,
                    'include_base_amount':row['include_base_amount'] or False,
                    'active':row['active'] or False,
                    'ref_tax_sign':row['ref_tax_sign'] or False,
                    'applicable_type':row['applicable_type'] or False,
                    'account_collected_id':row['account_collected_id'] or False,
                    'company_id':row['company_id'] or False,
                    'name':row['name'] or False,
                    'tax_code_id':row['tax_code_id'] or False,
                    'parent_id':row['parent_id'] or False,
                    'amount':float(row['amount']) or False,
                    'python_compute':row['python_compute'] or False,
                    'tax_sign':row['tax_sign'] or False,
                    'python_compute_inv':row['python_compute_inv'] or False,
                    'python_applicable':row['python_applicable'] or False,
                    'type':row['type'] or False,
                    'price_include':row['price_include'] or False
                    }
        new_id = oorpc.create('account.tax', vals)
        sql = '''
         update account_tax set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
    
    cur2.execute('''SELECT setval('account_tax_id_seq', (SELECT MAX(id) FROM account_tax))''')
    cur2.execute('commit')
        
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, position_id, 
           tax_dest_id, tax_src_id
        FROM account_fiscal_position_tax order by id;
        '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        vals = {
                    'position_id':row['position_id'] or False,
                    'tax_dest_id': row['tax_dest_id'] or False,
                    'tax_src_id':row['tax_src_id'] or False,
                }
        new_id = oorpc.create('account.fiscal.position.tax', vals)
        sql = '''
         update account_fiscal_position_tax set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
    cur2.execute('''SELECT setval('account_fiscal_position_id_seq', (SELECT MAX(id) FROM account_fiscal_position_tax))''')
    cur2.execute('commit')
             
def import_account_tax_code(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        delete from account_tax_code 
    '''
    cur2.execute(sql)
    cur2.execute('commit')
    
    sql ='''
            SELECT id, create_uid, create_date, write_date, write_uid, info, code, 
               name, sequence, company_id, sign, notprintable, parent_id
            FROM account_tax_code
            ORDER BY id
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        vals = {
                    'info':row['info'] or False,
                    'code': row['code'] or False,
                    'name':row['name'] or False,
                    'sequence': row['sequence'] or False,
                    'company_id':row['company_id'] or False,
                    'sign': row['sign'] or False,
                    'notprintable':row['notprintable'] or False,
                    'parent_id':row['parent_id'] or False,
                }
        new_id = oorpc.create('account.tax.code', vals)
        sql = '''
         update account_tax_code set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        
    cur2.execute('''SELECT setval('account_tax_code_id_seq', (SELECT MAX(id) FROM account_tax_code))''')
    cur2.execute('commit')

def import_product_pricelist(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
     
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor2.execute('''
    TRUNCATE product_pricelist_item CASCADE;
    TRUNCATE product_pricelist_version CASCADE;
    TRUNCATE product_pricelist CASCADE;''')      
    cursor2.execute('commit')
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, currency_id, 
           name, active, type, company_id
        FROM product_pricelist;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        vals = {
                    'currency_id':map_cur[row['currency_id']] or False,
                    'name': row['name'] or False,
                    'active':row['active'] or False,
                    'type': row['type'] or False,
                    'company_id':row['company_id'] or False,
                }
        new_id = oorpc.create('product.pricelist', vals)
        sql = '''
         update product_pricelist set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('product_pricelist_id_seq', (SELECT MAX(id) FROM product_pricelist))''')
        cur2.execute('commit')

def import_account_journal(oorpc):
    conn1 = psycopg2.connect(db1_conn_string)
    conn2 = psycopg2.connect(db2_conn_string)
    cur1 = conn1.cursor()
    cur2 = conn2.cursor()
    
    cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql ='''
        delete from account_journal 
    '''
    cur2.execute(sql)
    cur2.execute('commit')
    
    sql ='''
        SELECT id, create_uid, create_date, write_date, write_uid, default_debit_account_id, 
           code, view_id, currency, sequence_id, allow_date, update_posted, 
           user_id, name, centralisation, group_invoice_lines, company_id, 
           entry_posted, type, default_credit_account_id, analytic_journal_id, 
           internal_sequence_id
      FROM account_journal
      order by id;
    '''
    cursor1.execute(sql)
    old_po = cursor1.fetchall()
    for row in old_po:
        vals = {
                    'default_debit_account_id':row['default_debit_account_id'] or False,
                    'code': row['code'] or False,
                    'currency':row['currency'] or False,
                    'sequence_id': row['sequence_id'] or False,
                    'allow_date':row['allow_date'] or False,
                    'update_posted': row['update_posted'] or False,
                    'user_id':row['user_id'] or False,
                    'name':row['name'] or False,
                    
                    'centralisation':row['centralisation'] or False,
                    'group_invoice_lines': row['group_invoice_lines'] or False,
                    'company_id':row['company_id'] or False,
                    'entry_posted':row['entry_posted'] or False,
                    
                    'type': row['type'] or False,
                    'default_credit_account_id':row['default_credit_account_id'] or False,
                    'analytic_journal_id':row['analytic_journal_id'] or False,
                }
        new_id = oorpc.create('account.journal', vals)
        
        sql ='''
              delete  from account_journal_cashbox_line
        '''
        cur2.execute(sql)
        cur2.execute('commit')
        
        sql = '''
         update account_journal set id = %s where id = %s 
         ''' %(row['id'],new_id)
        cur2.execute(sql)
        cur2.execute('commit')
        cur2.execute('''SELECT setval('account_journal_id_seq', (SELECT MAX(id) FROM account_journal))''')
        cur2.execute('commit')

def update_partner_address(oorpc):
     conn1 = psycopg2.connect(db1_conn_string)
     conn2 = psycopg2.connect(db2_conn_string)
    
     cursor1 = conn1.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     cursor2 = conn2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
     
     #Remove Partner co ID=4 de khoi bi trung khi update
     part_ids = oorpc.search('res.users',[('name','=','Template User'),('active','=',False)])
     oorpc.delete('res.users', part_ids)
     part_ids = oorpc.search('res.partner',[('name','=','Template User')])
     oorpc.delete('res.partner', part_ids)
     
     db1_res_partner = ['name', 'create_uid', 'create_date', 'write_date', 'write_uid', 'function', 
                       'fax', 'color', 'street2', 'phone', 'street', 'active', 'city', 
                       'zip', 'title', 'country_id', 'company_id', 'birthdate', 'state_id', 
                       'type', 'email', 'parent_id'
                       ]
     #Ko insert thang partner cua Company
     sql ='''
         SELECT id,name
          FROM res_partner
          WHERE id not in (select partner_id from res_company)
          order by id;
     '''
     cursor1.execute(sql)
     old_po = cursor1.fetchall()
     
     cursor2.execute('ALTER TABLE res_partner ALTER COLUMN notification_email_send DROP NOT NULL')
     cursor2.execute('commit')
     
     number = 1
     for row in old_po:
        sql ='''
         SELECT id, name, create_uid, create_date, write_date, write_uid, function, 
               fax, color, street2, phone, street, active, city, 
               zip, title, country_id, company_id, birthdate, state_id, 
               type, email
          FROM res_partner_address
          WHERE partner_id = %s
          order by id
         '''%(row['id'])
        cursor1.execute(sql)
        old_address = cursor1.fetchall()
        name = False
        if row['name']:
            name = row['name'].replace("'"," ")
            
        stt = 1
        for address in old_address:
            date_order = False
            write_date= False
            address_name = False
            street = False
            street2= False
            city=False
            if address['create_date']:
              create_date = address['create_date'] and (address['create_date'] - relativedelta(hours=7)).strftime(DATETIME_FORMAT) or 'null'
            if address['write_date']:
              write_date = address['write_date'] and (address['write_date'] - relativedelta(hours=7)).strftime(DATETIME_FORMAT) or 'null'
            if address['name']:
                address_name = address['name'].replace("'"," ")
            
            if address['street']:
                street = address['street'].replace("'"," ")
            if address['street2']:
                street2 = address['street2'].replace("'"," ")
            if address['city']:
                city = address['city'].replace("'"," ")
                
            if stt == 1:
                values = '''
                        function='%s', 
                        fax='%s', color=%s, street2='%s', phone='%s', street='%s', active=True, city='%s', 
                        zip='%s', title=%s, country_id=%s, company_id=1, birthdate='%s', state_id=%s, 
                        type='%s', email='%s'
                        '''%( 
                               address['function'] or 'null',
                               address['fax'] or 'null', address['color'] or 'null', street2 or 'null', address['phone'] or 'null', 
                               street or 'null', city or 'null', 
                               address['zip'] or 'null', address['title'], address['country_id'] or 'null', 
                               address['birthdate'] or 'null', address['state_id'] or 'null', 
                               address['type'] or 'null', address['email'] or 'null'
                              )
                if len(old_address) > 1:
                    values += ', is_company=True'
                    
                values = values.replace("'null'","null")
                values = values.replace("None","null")
                
                sql = '''UPDATE res_partner
                   SET %s 
                   WHERE id=%s'''%(values, row['id'])
                res = cursor2.execute(sql)      
                cursor2.execute('commit')
            else:
                values = '''
                        '%s'
                        ,%s,'%s','%s',%s,'%s'
                        ,'%s',%s,'%s','%s'
                        ,'%s', True,'%s'
                        ,'%s',%s,%s,1,'%s',%s
                        ,'%s','%s', %s
                        '''%( 
                               address_name or name,
                               address['create_uid'],create_date,write_date or 'null',address['write_uid'] or 'null' ,address['function'] or 'null',
                               address['fax'] or 'null', address['color'] or 'null', street2 or 'null', address['phone'] or 'null', 
                               street or 'null', city or 'null', 
                               address['zip'] or 'null', address['title'], address['country_id'] or 'null', 
                               address['birthdate'] or 'null', address['state_id'] or 'null', 
                               address['type'] or 'null', address['email'] or 'null', row['id'] or 'null'
                               
                              )
                values = values.replace("'null'","Null")
                values = values.replace("None","null")
                
                sql = '''INSERT INTO res_partner(%s)
                   VALUES (%s)
                   RETURNING id'''%(','.join(map(str,db1_res_partner)),values)
                res = cursor2.execute(sql)      
                cursor2.execute('commit')
            stt +=1
                
            print number
            number += 1
            
     cursor2.execute('''SELECT setval('res_partner_id_seq', (SELECT MAX(id) + 1 FROM res_partner))''')
     cursor2.execute('commit')
     res_user(oorpc)
     
     cursor2.execute('ALTER TABLE res_partner ALTER COLUMN notification_email_send SET NOT NULL')
     cursor2.execute('commit')

if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('localhost', 'doukas70_ok1', 'admin', '1', '8069')
    print 'In progress ...'
    
#First Stage #Chay 1 Lan Duy Nhat
#     import_account(oorpc) #OK
#     import_account_tax_code(oorpc) #OK
#     import_account_tax(oorpc) #OK
#     import_account_journal(oorpc)
#     import_product_pricelist(oorpc)
    
#Second Stage #Chay 1 Lan Duy Nhat
#     import_product_categrory() #OK
#     import_product(oorpc) #OK chay lan 2 ok
#     res_user(oorpc) #OK
#     import_res_partner(oorpc) #OK
    
#     import_product_saleprice(oorpc)
#     update_partner_address(oorpc)
    print 'Done.'
    
    
    
    

