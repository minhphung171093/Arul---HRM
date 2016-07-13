# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
import locale
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class customer_ageing_report(osv.osv_memory):
    _name = "customer.ageing.report"
    _columns = {
                'date_from': fields.date('As of Date: '),
                'customer_group': fields.selection([('export','Export'),
                                                   ('domestic','Domestic'),
                                                   ('indirect_export','Indirect Export')],
                                                    'Customer Group'),
                'customer_id': fields.many2one('res.partner','Customer'),
                'ageing_line': fields.one2many('customer.ageing.line', 'customer_ageing_id', 'Customer Ageing Line'),
                }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'customer.ageing.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'customer_ageing_report', 'datas': datas}

    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'customer.ageing.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'customer_ageing_report_pdf', 'datas': datas}

customer_ageing_report()

  #TPT START - By P.VINOTHKUMAR - ON 09/05/2015 - FOR (Generate customer ageing report header and lines) 

class customer_ageing_line(osv.osv_memory):
    _name = "customer.ageing.line" 
    _columns = {
        'customer_ageing_id': fields.many2one('customer.ageing.report', 'Customer Ageing Report',ondelete='cascade'),        
        #'code': fields.many2one('customer.ageing.report', 'code'),
        'code': fields.char('Code'),
        'name': fields.char('name'),
        'balance':fields.char('Balance'),
        '0_30_days': fields.char('0-30 days'),
        '31_45_days': fields.char('31-45 days'),
        '46_60_days': fields.char('46-60 days'),
        '61_90_days': fields.char('61-90 days'),
        'over_90_days': fields.char('Over 90 days'),
    }      
customer_ageing_line()


class customer_ageing(osv.osv_memory):
    _name = "customer.ageing"
    
    _columns = {
            'date_from': fields.date('As of Date: '),
            'customer_group': fields.selection([('export','Export'),
                                                   ('domestic','Domestic'),
                                                   ('indirect_export','Indirect Export')],
                                                    'Customer Group'),
           'customer_id': fields.many2one('res.partner','Customer'),     
            
    }
    

    def print_report(self, cr, uid, ids, context=None):
    
        def convert_date(self, date):
            if date:
                date = datetime.strptime(date, DATE_FORMAT)
                return date.strftime('%d/%m/%Y')
        
        def get_date_from(self):
            wizard_data = self.localcontext['data']['form']
            date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        def get_customer_group(self):
            customer_group = ''
            wizard_data = self.localcontext['data']['form']
            customer_group = wizard_data['customer_group'] 
            if customer_group == 'export':
                customer_group = 'Export'
            if customer_group == 'domestic':
                customer_group = 'Domestic'
            if customer_group == 'indirect_export':
                customer_group = 'Indirect Export'
            return  customer_group
        
        def get_balance (code, date):
            credit = 0
#             sql  = '''
#                     select case when SUM(debit-credit)=0 then 0 else SUM(debit-credit) end credit from account_move_line where 
#                     account_id=(select id from account_account where code = '0000'||'%s') and date <= '%s'
#                 '''%(code, date)
            sql = '''
                  select 
                  (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total from account_invoice where 
                  account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and date_invoice <= '%s')-
                 (select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
                 account_id=(select id from account_account where code = '0000'||'%s') and date<='%s' and doc_type='cash_rec')  
                 as balance 
              '''%(code, date,code,date)
                
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
               credit = credit[0]            
            return credit 
            
        def get_balance_30 (code,date):
            credit = 0
#             sql  = '''
#                     select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
#                     account_id=(select id from account_account where code = '0000'||'%s') and 
#                     date between (select timestamp '%s' - interval '30 days')and(select timestamp '%s' - interval '1 day')
#                 '''%(code,date,date)
            sql  = '''
                   select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total from account_invoice where 
                   account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
                   date_invoice between (select timestamp '%s' - interval '30 days')and(select timestamp '%s' - interval '1 day'))
                 -(select case when sum(debit) is null then 0 else sum(debit) end as debit  from account_move_line where account_id=(select id from account_account where code = '0000'||'%s') 
                   and doc_type='cash_rec' and date between (select timestamp '%s' - interval '30 days')
                   and(select timestamp '%s' - interval '1 day'))  as balance_30
                 '''%(code,date,date,code,date,date)
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
               credit = credit[0]            
            return credit
        
        def get_balance_31_45 (code,date):
            credit = 0
#             sql  = '''
#                     select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
#                     account_id=(select id from account_account where code = '0000'||'%s') and 
#                     date between (select timestamp '%s' - interval '31 days') and (select timestamp '%s' - interval '45 days')
#                 '''%(code,date,date)
            sql  = '''
                   select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total  from account_invoice where 
                   account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
                   date_invoice between (select timestamp '%s' - interval '45 days')and(select timestamp '%s' - interval '31 days'))
                 -(select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
                   account_id=(select id from account_account where code = '0000'||'%s') 
                   and doc_type='cash_rec' and date between (select timestamp '%s' - interval '45 days')
                   and(select timestamp '%s' - interval '31 days'))  as balance_45
                 '''%(code,date,date,code,date,date)
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
               credit = credit[0]            
            return credit  
        
        def get_balance_46_60 (code,date):
            credit = 0
#             sql  = '''
#                     select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
#                     account_id=(select id from account_account where code = '0000'||'%s') and 
#                     date between (select timestamp '%s' - interval '46 days') and (select timestamp '%s' - interval '60 days')
#                 '''%(code,date,date)
            sql  = '''
                   select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total  from account_invoice where 
                   account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
                   date_invoice between (select timestamp '%s' - interval '60 days')and(select timestamp '%s' - interval '46 days'))
                 -(select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
                   account_id=(select id from account_account where code = '0000'||'%s') 
                   and doc_type='cash_rec' and date between (select timestamp '%s' - interval '60 days')
                   and(select timestamp '%s' - interval '46 days'))  as balance_60
                 '''%(code,date,date,code,date,date)
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
               credit = credit[0]            
            return credit 
        
        def get_balance_61_90 (code,date):
            credit = 0
#             sql  = '''
#                     select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
#                     account_id=(select id from account_account where code = '0000'||'%s') and 
#                     date between (select timestamp '%s' - interval '61 days') and (select timestamp '%s' - interval '90 days')
#                 '''%(code,date,date)
            sql  = '''
                   select (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total  from account_invoice where 
                   account_id=(select id from account_account where code = '0000'||'%s') and state!='draft' and
                   date_invoice between (select timestamp '%s' - interval '90 days')and(select timestamp '%s' - interval '61 days'))
                 -(select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
                   account_id=(select id from account_account where code = '0000'||'%s') 
                   and doc_type='cash_rec' and date between (select timestamp '%s' - interval '90 days')
                   and(select timestamp '%s' - interval '61 days'))  as balance_90
                 '''%(code,date,date,code,date,date)
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
               credit = credit[0]            
            return credit  
        
        def get_balance_over_90 (code,date):
            credit = 0
#             sql  = '''
#                     select case when SUM(debit-credit)=0.00 or SUM(debit-credit) is null then 0.00 else SUM(debit-credit) end credit from account_move_line where 
#                     account_id=(select id from account_account where code = '0000'||'%s') and 
#                     date <= (select timestamp '%s' - interval '90 days')
#                 '''%(code,date)
            sql = '''
                  select 
                  (select case when sum(amount_total) is null then 0 else sum(amount_total) end as amount_total from account_invoice where 
                  account_id=(select id from account_account where code = '0000'||'%s') and state!='draft'and date_invoice <= (select timestamp '%s' - interval '90 days'))-
                 (select case when sum(debit) is null then 0 else sum(debit) end as debit from account_move_line where 
                 account_id=(select id from account_account where code = '0000'||'%s') and date<=(select timestamp '%s' - interval '90 days') and doc_type='cash_rec')  
                 as balance_over_90 
              '''%(code, date,code,date) 
              
            cr.execute(sql)
            credit = cr.fetchone()
            if credit:
               credit = credit[0]            
            return credit  
        def get_customer(cb):
            #===================================================================
            # wizard_data = self.localcontext['data']['form']
            # customer_group = wizard_data['customer_group']
            # customer_id = wizard_data['customer_id']
            # date = wizard_data['date_from']
            #===================================================================
        
            customer_group = cb.customer_group
            customer_id=cb.customer_id.id
            date=cb.date_from
            #date1 = wizard_data['date_from']
            bp_obj = self.pool.get('res.partner')
            
            if customer_id and date:
                bp_ids = bp_obj.search(cr,uid, [('id','=',customer_id)                                                   
                                        ])                                              
           
            if customer_group:
                bp_ids = bp_obj.search(cr, uid, [('customer','=',True),
                                                       ('customer_account_group_id','=','VVTI Sold to Party'),
                                                       ('arulmani_type','=',customer_group)
                                            ])
            if not customer_id and not customer_group:
                bp_ids = bp_obj.search(cr, uid, [('customer','=',True),
                                                       ('customer_account_group_id','=','VVTI Sold to Party')                   
                                            ])
            if customer_id and customer_group and date:   
                bp_ids = bp_obj.search(cr,uid, [('id','=',customer_id),
                                                       ('arulmani_type','=',customer_group)
                                            ])
            
                
            res = []
            
            for line in bp_obj.browse(cr, uid, bp_ids):
                res.append({ 
                    'code': line['customer_code'] or '',
                    'name': line['name'] or '',  
                    'balance': get_balance(line['customer_code'], date) or 0.00,
                    '0_30_days': get_balance_30(line['customer_code'],date) or 0.00,
                    '31_45_days': get_balance_31_45(line['customer_code'],date) or 0.00,
                    '46_60_days': get_balance_46_60(line['customer_code'],date) or 0.00,
                    '61_90_days': get_balance_61_90(line['customer_code'],date) or 0.00,
                    'over_90_days':get_balance_over_90(line['customer_code'],date) or 0.00,
                    
                })
            return res
        
        def get_amt(amt):       
            locale.setlocale(locale.LC_NUMERIC, "en_IN")
            inr_comma_format = locale.format("%.2f", amt, grouping=True)
            return inr_comma_format
        
        
        cr.execute('delete from customer_ageing_report')
        cb_obj = self.pool.get('customer.ageing.report')
        cb = self.browse(cr, uid, ids[0])
        cb_line = [] 
        for line in get_customer(cb):
            cb_line.append((0,0,{
                    'code': line['code'] or '',
                    'name': line['name'] or '',  
                    'balance': get_amt(line['balance']) or 0.00, 
                    '0_30_days': get_amt(line['0_30_days']) or 0.00, 
                    '31_45_days':get_amt(line['31_45_days']) or 0.00, 
                    '46_60_days':get_amt(line['46_60_days']) or 0.00, 
                    '61_90_days':get_amt(line['61_90_days']) or 0.00, 
                    'over_90_days':get_amt(line['over_90_days']) or 0.00, 
            })) 
                 
        
        vals = {
            'date_from': cb.date_from,           
            'customer_id': cb.customer_id.id or False,
            'customer_group':cb.customer_group, 
            'ageing_line': cb_line,
        }        
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'customer_ageing_report_form')
        return {
                    'name': 'Customer Ageing Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'customer.ageing.report',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                    }
    
customer_ageing()    
    
 #TPT End
 
    
    
    

