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
db1_conn_string = "host='192.241.125.163' port='5432' dbname='ketoan_xsbp' user='postgres' password='postgres'"

def create_employee(oorpc):
    with open (current_path+"/python/201409010639.txt", "r") as myfile:
        datas=myfile.readlines()
        
        for i,data in enumerate(datas):
            emp_ids = oorpc.search('hr.employee',[('employee_id','=',data[43:51])])
            if not emp_ids:
                vals = {'name':data[43:51],'employee_id':data[43:51]}
                print i
                oorpc.create('hr.employee',vals)
    return True
if __name__ == '__main__':
    (options, args) = define_arg()
    oorpc = OpenObjectRPC('localhost', 'Arul', 'admin', '1', '8069')
    print 'In progress ...'
    create_employee(oorpc)
    print 'Done.'
    
    
    
    

