# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_voucher': self.get_voucher,
            'convert_date_cash': self.convert_date_cash,
            'get_invoice':self.get_invoice,
            'get_doc_type':self.get_doc_type,
            'get_total':self.get_total,
            'get_gl_acct':self.get_gl_acct, #TPT-Y
            'get_balance':self.get_balance, #TPT-Y
            'get_pur_doc_no':self.get_pur_doc_no, #TPT-Y
            'get_emp':self.get_emp, #TPT-Y
            'get_cost_center':self.get_cost_center,
            'get_partner':self.get_partner,
            'get_employee_id':self.get_employee_id,
            'get_line_employee_id':self.get_line_employee_id,
        })
        
    def get_emp(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['employee']:
            emp_id = wizard_data['employee']
            #emp_emp = emp_id[0]
            acc_obj = self.pool.get('res.partner')
            acc = acc_obj.browse(self.cr,self.uid,emp_id[0])
            emp_name = acc.name
            return emp_name
        return ''
    
    def get_partner(self,move_id):
            emp_id = move_id.id
            if emp_id:
                sql ='''
                     select customer,name,customer_code,vendor_code from res_partner where id = %s
                     '''%(emp_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                     if move['customer'] == 't':
                         if move['customer_code'] and move['name']:
                            partner = move['customer_code'] +'-'+ move['name']
                            return partner or ''
                         elif move['name']:
                             partner = move['name']
                             return partner or ''
                     else:
                             if move['vendor_code'] and move['name']:
                                partner = move['vendor_code'] +'-'+ move['name']
                                return partner or ''
                             elif move['name']:
                                 partner = move['name']
                                 return partner or ''
    
    def get_cost_center(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['cost_center_id']:
            cos_cent = wizard_data['cost_center_id']
            #emp_emp = emp_id[0]
            cc_obj = self.pool.get('tpt.cost.center')
            acc = cc_obj.browse(self.cr,self.uid,cc_obj[0])
            cost_name = cc.name
            return cost_name
        return ''
    def get_employee_id(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['employee_id']:
            employee_id = wizard_data['employee_id']
            #emp_emp = emp_id[0]
            emp_obj = self.pool.get('hr.employee')
            #acc = cc_obj.browse(self.cr,self.uid,emp_obj[0])
            emp_obj_ids = emp_obj.search(self.cr, self.uid, [('id','=',employee_id[0])])
            emp_obj1 = emp_obj.browse(self.cr,self.uid,emp_obj_ids[0])
            employee_id = emp_obj1.employee_id   
            
            return employee_id+'-'+emp_obj1.name or ''
        else:
            return ''
    def get_line_employee_id(self, move_id):
        if move_id:
            av_obj = self.pool.get('account.voucher')
            av_obj_ids = av_obj.search(self.cr, self.uid, [('move_id','=',move_id)])
            av_obj1 = av_obj.browse(self.cr,self.uid,av_obj_ids[0])
            if av_obj1.employee_id.employee_id:
                emp = av_obj1.employee_id.employee_id +'-'+av_obj1.employee_id.name
                return emp
        else:
            return ''
        
    def get_voucher(self,move_id):
        wizard_data = self.localcontext['data']['form']
        gl_account = wizard_data['account_id']
        acc_obj = self.pool.get('account.account')
        acc = acc_obj.browse(self.cr,self.uid,gl_account[0])
        sql = '''
            select cost_center_id from account_voucher where move_id =%s
        '''%(move_id)
        self.cr.execute(sql)
        p = self.cr.fetchone()
        cost_center = ''
        if p and p[0]:
            cost_center = self.pool.get('tpt.cost.center').browse(self.cr, self.uid, p[0]).name
        return cost_center
    
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    #TPT-Y
    def get_gl_acct(self):
        wizard_data = self.localcontext['data']['form']
        gl_account = wizard_data['account_id']        
        acc_obj = self.pool.get('account.account')
        acc = acc_obj.browse(self.cr,self.uid,gl_account[0])
        gl_act = acc.code +''+acc.name
        return gl_act
    #TPT-Y
    
    #TPT-Y
    def get_pur_doc_no(self,move_id):       
        sql = '''
            select name from purchase_order where id
              in (select purchase_id from account_invoice where move_id = %s)
        '''%(move_id)
        self.cr.execute(sql)
        pur_doc_no = self.cr.fetchone()
        return pur_doc_no       
        
    #TPT-Y
    
            
    def convert_date_cash(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date(self):
        res = {}
        date = time.strftime('%d/%m/%Y'),
        date = datetime.strptime(date[0], DATE_FORMAT)
        day = date.day
        month = date.month
        year = date.year
        res = {
               'day': day,
               'month': month,
               'year': year,
               }
        return res

    def get_doc_type(self, doc_type):
        if doc_type == 'cus_inv':
            return "Customer Invoice"
        if doc_type == 'cus_pay':
            return "Customer Payment"
        if doc_type == 'sup_inv_po':
            return "Supplier Invoice(With PO)"
        if doc_type == 'sup_inv':
            return "Supplier Invoice(Without PO)"
        if doc_type == 'sup_pay':
            return "Supplier Payment"
        if doc_type == 'payroll':
            return "Executives Payroll"
        if doc_type == 'staff_payroll':
            return "Staff Payroll"
        if doc_type == 'worker_payroll':
            return "Workers Payroll"
        if doc_type == 'grn':
            return "GRN"
        if doc_type == 'good':
            return "Good Issue"
        if doc_type == 'do':
            return "DO"
        if doc_type == 'inventory':
            return "Inventory Transfer"
        if doc_type == 'manual':
            return "Manual Journal"
        if doc_type == 'cash_pay':
            return "Cash Payment"
        if doc_type == 'cash_rec':
            return "Cash Receipt"
        if doc_type == 'bank_pay':
            return "Bank Payment"
        if doc_type == 'bank_rec':
            return "Bank Receipt"
        if doc_type == 'ser_inv':
            return "Service Invoice"
        if doc_type == 'product':
            return "Production"
        if doc_type == '':
            return "Journal Voucher"
        
    
    def get_total(self, cash,type):
        sum = 0.0
        for line in cash:
            if type == 'credit':
                sum += line.credit
            if type == 'debit':
                sum += line.debit
        return sum
    
    #TPT-Y
    def get_balance(self, get_invoice):
            credit = 0.0
            debit = 0.0
            for line in get_invoice:
                debit += line.debit
                credit += line.credit
            balance = float(debit) - float(credit)
            balance = float(balance)
            return balance
    #TPT-Y
        
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        gl_account = wizard_data['account_id']
        acc_obj = self.pool.get('account.account')
        acc = acc_obj.browse(self.cr,self.uid,gl_account[0])
        doc_type = wizard_data['doc_type']
        doc_no = wizard_data['doc_no'] or ''
        narration = wizard_data['narration'] or ''
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        is_posted = wizard_data['is_posted']
        emp_id = wizard_data['employee']
        cost_center = wizard_data['cost_center_id']
        employee_id = wizard_data['employee_id']
        acount_move_line_obj = self.pool.get('account.move.line')
        acount_move_obj = self.pool.get('account.move')
        cus_ids = []
        
        sql = '''
            select ml.id from account_move_line ml
            join account_move m on (m.id=ml.move_id)
            left join account_voucher av on (av.move_id = ml.move_id)
            left join tpt_cost_center cc on (cc.id = av.cost_center_id) 
            where m.date between '%s' and '%s' and ml.account_id = %s           
            '''%(date_from, date_to, acc.id)
        if doc_type:
            str = " and m.doc_type in('%s')"%(doc_type)
            sql = sql+str
        if doc_no:
            str = " and m.name ~'%s'"%(doc_no)
            sql = sql+str
        if narration:
            str = " and ml.ref ~'%s'"%(narration)
            sql = sql+str            
        if is_posted:
            str = " and m.state = 'posted'"
            sql = sql+str
        if emp_id:
            str = " and ml.partner_id = %s"%(emp_id[0])
            sql = sql+str
        if employee_id:
            str = " and av.employee_id = %s"%(employee_id[0])
            sql = sql+str
        if cost_center:
            str = " and cc.id = %s"%(cost_center[0])
            sql = sql+str
                
        sql=sql+" order by m.date,m.name"
            
        self.cr.execute(sql)
        cus_ids = [r[0] for r in self.cr.fetchall()]    
        return acount_move_line_obj.browse(self.cr,self.uid,cus_ids)
        
        #=======================================================================
        # if is_posted is True:
        #     if doc_no :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id) 
        #             where m.state = 'posted' and m.date between '%s' and '%s' 
        #             and m.name ~'%s' and m.state = 'posted' and ml.account_id = %s
        #             order by m.date,m.name    
        #         '''%(date_from, date_to,doc_no,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif narration :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id) 
        #             where m.state = 'posted' and m.date between '%s' and '%s' 
        #             and m.state = 'posted' and ml.account_id = %s and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,acc.id,narration)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_no and narration:
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)
        #             where m.state = 'posted' and m.date between '%s' and '%s' 
        #             and m.name ~'%s' and m.state = 'posted' and ml.account_id = %s and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,doc_no,acc.id,narration)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_type :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id) 
        #             where m.state = 'posted' and m.date between '%s' and '%s' 
        #             and m.doc_type in('%s') and m.state = 'posted' and ml.account_id = %s
        #             order by m.date,m.name   
        #         '''%(date_from, date_to,doc_type,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif narration and doc_type :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id) 
        #             where m.state = 'posted' and m.date between '%s' and '%s' 
        #             and m.doc_type in('%s') and m.state = 'posted' and ml.account_id = %s and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,doc_type,acc.id,doc_no)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_no and doc_type :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id) 
        #             where m.state = 'posted' and m.date between '%s' and '%s' and m.doc_type in('%s') 
        #             and m.name ~'%s' and m.state = 'posted' and ml.account_id = %s
        #             order by m.date,m.name 
        #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_no and doc_type and narration:
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)
        #             where state = 'posted' and date between '%s' and '%s' 
        #             and doc_type in('%s') and name ~'%s' and state = 'posted'
        #             and account_id = %s and ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     else:
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)
        #             where m.state = 'posted' and m.date between '%s' and '%s' 
        #             and m.state = 'posted' and ml.account_id = %s
        #             order by m.date,m.name
        #         '''%(date_from, date_to,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        # else: #MAJOR ELSE
        #     if doc_no :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)
        #             where m.date between '%s' and '%s' and m.name ~'%s' 
        #             and ml.account_id = %s
        #             order by m.date,m.name  
        #         '''%(date_from, date_to,doc_no,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif narration :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)
        #             where m.date between '%s' and '%s' and ml.account_id = %s 
        #             and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,acc.id,narration)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_no and narration:
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)  
        #             where m.date between '%s' and '%s' and m.name ~'%s' 
        #             and ml.account_id = %s and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,doc_no,acc.id,narration)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_type :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)  
        #             where m.date between '%s' and '%s' and m.doc_type in('%s') 
        #             and ml.account_id = %s
        #             order by m.date,m.name   
        #         '''%(date_from, date_to,doc_type,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif narration and doc_type :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)  
        #             where m.date between '%s' and '%s' and m.doc_type in('%s') 
        #             and ml.account_id = %s and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,doc_type,acc.id,doc_no)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_no and doc_type :
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id) 
        #             where m.date between '%s' and '%s' and m.doc_type in('%s') 
        #             and m.name ~'%s' and ml.account_id = %s
        #             order by m.date,m.name 
        #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     elif doc_no and doc_type and narration:
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)  
        #             where m.date between '%s' and '%s' and m.doc_type in('%s') 
        #             and m.name ~'%s' and ml.account_id = %s and ml.ref ~'%s'
        #             order by m.date,m.name
        #         '''%(date_from, date_to,doc_type,doc_no,acc.id)
        #         self.cr.execute(sql)
        #         cus_ids = [r[0] for r in self.cr.fetchall()]
        #     else:
        #         sql = '''
        #             select ml.id from account_move_line ml
        #             join account_move m on (m.id=ml.move_id)  
        #             where m.date between '%s' and '%s' and ml.account_id = %s
        #             order by m.date,m.name
        #         '''%(date_from, date_to,acc.id)
        #=======================================================================
        
    
        
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
