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
            'convert_date': self.convert_date,
            'get_vendor': self.get_vendor,
            'get_vendor_group': self.get_vendor_group,
                    })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_vendor_group(self):
        vendor_group = ''
        wizard_data = self.localcontext['data']['form']
        vendor_group = wizard_data['vendor_group'] 
        if vendor_group == 'Spares':
            vendor_group = 'Spares'
        if vendor_group == 'Domestic':
            vendor_group = 'Domestic'
        if vendor_group == 'Foreign':
            vendor_group = 'Foreign'
        return  vendor_group
# 
#     
    def get_vendor(cb):
#              wizard_data = self.localcontext['data']['form']
#              vendor_group = wizard_data['vendor_group']
#              vendor_id = wizard_data['vendor_id']
#              date = wizard_data['date_from']
         
         vendor_group = cb.vendor_group_id.id
         vendor_id=cb.vendor_id.id
         date=cb.date_from
         #date1 = wizard_data['date_from']
         bp_obj = self.pool.get('res.partner')
         
         if vendor_id and date:
             bp_ids = bp_obj.search(cr,uid, [('id','=',vendor_id)                                                   
                                     ])                                              
        
         if vendor_group:
             bp_ids = bp_obj.search(cr, uid, [('vendor_group_id','=',vendor_group)
                                        ])
             
         if not vendor_id and not vendor_group:
             bp_ids = bp_obj.search(cr, uid, [('vendor_group_id','=','4')
                                                 
                                         ])
         if vendor_id and vendor_group and date:   
             bp_ids = bp_obj.search(cr,uid, [('id','=',vendor_id),
                                                    ('vendor_group_id','=',vendor_group)
                                         ])
             
                 
         res = []
             
         for line in bp_obj.browse(cr, uid, bp_ids):
                 res.append({ 
                     'code': '0',
                     'name': 'Ram',  
                     'balance': '0.00',
                     '0_30_days': '0.00',
                     '31_45_days':'0.00',
                     '46_60_days': '0.00',
                     'over_90_days':'0.00',
                     
                 })
         return res
#     
#     def get_balance (self, code, date):
#         credit = 0
# #         sql  = '''
# #                 select case when SUM(debit-credit)=0 then 0 else SUM(debit-credit) end credit from account_move_line where 
# #                 account_id=(select id from account_account where code = '0000'||'%s') and date <= '%s'
# #             '''%(code, date)
#         sql = '''
#                   select 
#                   (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total from account_invoice where 
#                   account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and date_invoice <= '%s')-
#                  (select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
#                  account_id=(select id from account_account where code = '0000'||'%s') and date<='%s' and doc_type='cash_rec')  
#                  as balance 
#               '''%(code, date,code,date)
#         self.cr.execute(sql)
#         credit = self.cr.fetchone() 
#         if credit:
#            credit = credit[0]            
#         return credit 
#     
#     def get_balance_30 (self,code,date):
#         credit = 0
# #         sql  = '''
# #                 select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
# #                 account_id=(select id from account_account where code = '0000'||'%s') and 
# #                 date between (select timestamp '%s' - interval '30 days') and (select timestamp '%s' - interval '1 day')
# #             '''%(code,date,date)
#         sql  = '''
#                    select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total from account_invoice where 
#                    account_id=(select id from account_account where code = '0000'||'%s') and  state!='draft' and
#                    date_invoice between (select timestamp '%s' - interval '30 days')and(select timestamp '%s' - interval '1 day'))
#                  -(select case when sum(debit) is null then 0 else sum(debit) end as debit  from account_move_line where account_id=(select id from account_account where code = '0000'||'%s') 
#                    and doc_type='cash_rec' and date between (select timestamp '%s' - interval '30 days')
#                    and(select timestamp '%s' - interval '1 day'))  as balance_30
#                  '''%(code,date,date,code,date,date)
#         self.cr.execute(sql)
#         credit = self.cr.fetchone()
#         if credit:
#            credit = credit[0]            
#         return credit
#     
#     def get_balance_31_45 (self,code,date):
#         credit = 0
# #         sql  = '''
# #                 select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
# #                 account_id=(select id from account_account where code = '0000'||'%s') and 
# #                 date between (select timestamp '%s' - interval '31 days') and (select timestamp '%s' - interval '45 days')
# #             '''%(code,date,date)
#         sql  = '''
#                    select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total  from account_invoice where 
#                    account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
#                    date_invoice between (select timestamp '%s' - interval '45 days')and(select timestamp '%s' - interval '31 days'))
#                  -(select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
#                    account_id=(select id from account_account where code = '0000'||'%s') 
#                    and doc_type='cash_rec' and date between (select timestamp '%s' - interval '45 days')
#                    and(select timestamp '%s' - interval '31 days'))  as balance_45
#                  '''%(code,date,date,code,date,date)
#         self.cr.execute(sql)
#         credit = self.cr.fetchone()
#         if credit:
#            credit = credit[0]            
#         return credit  
#     
#     def get_balance_46_60 (self,code,date):
#         credit = 0
# #         sql  = '''
# #                 select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
# #                 account_id=(select id from account_account where code = '0000'||'%s') and 
# #                 date between (select timestamp '%s' - interval '46 days') and (select timestamp '%s' - interval '60 days')
# #             '''%(code,date,date)
#         sql  = '''
#                    select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total  from account_invoice where 
#                    account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
#                    date_invoice between (select timestamp '%s' - interval '60 days')and(select timestamp '%s' - interval '46 days'))
#                  -(select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
#                    account_id=(select id from account_account where code = '0000'||'%s') 
#                    and doc_type='cash_rec' and date between (select timestamp '%s' - interval '60 days')
#                    and(select timestamp '%s' - interval '46 days'))  as balance_60
#                  '''%(code,date,date,code,date,date)
#         self.cr.execute(sql)
#         credit = self.cr.fetchone()
#         if credit:
#            credit = credit[0]            
#         return credit 
#     
#     def get_balance_61_90 (self,code,date):
#         credit = 0
# #         sql  = '''
# #                 select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
# #                 account_id=(select id from account_account where code = '0000'||'%s') and 
# #                 date between (select timestamp '%s' - interval '61 days') and (select timestamp '%s' - interval '90 days')
# #             '''%(code,date,date)
#         sql  = '''
#                    select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total  from account_invoice where 
#                    account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
#                    date_invoice between (select timestamp '%s' - interval '90 days')and(select timestamp '%s' - interval '61 days'))
#                  -(select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
#                    account_id=(select id from account_account where code = '0000'||'%s') 
#                    and doc_type='cash_rec' and date between (select timestamp '%s' - interval '90 days')
#                    and(select timestamp '%s' - interval '61 days'))  as balance_90
#                  '''%(code,date,date,code,date,date)
#          
#         self.cr.execute(sql)
#         credit = self.cr.fetchone()
#         if credit:
#            credit = credit[0]            
#         return credit  
#     
#     def get_balance_over_90 (self,code,date):
#         credit = 0
# #         sql  = '''
# #                 select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
# #                 account_id=(select id from account_account where code = '0000'||'%s') and 
# #                 date <= (select timestamp '%s' - interval '90 days')
# #             '''%(code,date)
#         sql = '''
#                   select 
#                   (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total from account_invoice where 
#                   account_id=(select id from account_account where code = '0000'||'%s') and state!='draft'and date_invoice <= (select timestamp '%s' - interval '90 days'))-
#                  (select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
#                  account_id=(select id from account_account where code = '0000'||'%s') and date<=(select timestamp '%s' - interval '90 days') and doc_type='cash_rec')  
#                  as balance 
#               '''%(code, date,code,date) 
#         self.cr.execute(sql)
#         credit = self.cr.fetchone()
#         if credit:
#            credit = credit[0]            
#         return credit  
     
 #TPT end          
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
