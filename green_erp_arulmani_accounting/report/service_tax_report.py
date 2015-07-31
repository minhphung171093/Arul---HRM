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
            'get_invoice':self.get_invoice,
            'get_tax': self.get_tax,
            'get_paid_tax': self.get_paid_tax,
            'get_opening_balance':self.get_opening_balance,
            #'get_service_tax': self.get_service_tax,
            'convert_date': self.convert_date,
            'get_tax_amnt':self.get_tax_amnt,
            'get_tax_desc':self.get_tax_desc,
            'get_total_openbal':self.get_total_openbal,            
            'get_tot_closing_bal':self.get_tot_closing_bal,
            'get_debit_balance':self.get_debit_balance,
            'get_total_service_tax':self.get_total_service_tax,
#             'get_sale_line': self.get_sale_line,
        })
        
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
            
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    
    def get_tax_desc(self,lineid):        
        sql = '''
            select t.description as desc from account_tax t            
            join account_invoice_line_tax ailt on (ailt.tax_id = t.id)
            where ailt.invoice_line_id = '%s'
        '''%(lineid)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
             describ = move['desc']             
             return describ or ''
    
        
    def get_tax_amnt(self,line):
        lineid = line.id
        linet = line.line_net
        decamount = 0.00
        sql = '''
            select COALESCE(t.amount,0) as taxamnt from account_tax t            
            join account_invoice_line_tax ailt on (ailt.tax_id = t.id)
            where ailt.invoice_line_id = '%s'
        '''%(lineid)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
             tax_amnt = move['taxamnt']
             tot_ser_tax = linet * (tax_amnt/100) #Commented by YuVi on 28/07/15, for roundoff issue
             #tot_ser_tax = round(linet * (tax_amnt/100),0) #YuVi on 28/07/15, for roundoff issue            
             return tot_ser_tax or 0.00
         
    def get_tot_closing_bal(self):
        wizard_data = self.localcontext['data']['form']
        #date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        accountid = wizard_data['account_id']
        #acct_id = accountid.id
        
        sql = '''
            select COALESCE(sum(a.taxamt),0) as totamount from( 
            select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
            else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
            from account_invoice_line ail
            join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
            where at.description ~'STax' and at.amount>0
            and ai.date_invoice <= '%s'
            group by ail.id 
            order by ail.id)a
        '''%(accountid[0],date_to)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
            total = move['totamount']
            return total or 0.00
        
    def get_total_service_tax(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        accountid = wizard_data['account_id']        
        
        sql = '''
            select COALESCE(sum(a.taxamt),0) as taxamount from( 
            select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
            else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
            from account_invoice_line ail
            join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
            where at.description ~'STax' and at.amount>0
            and ai.date_invoice between '%s' and '%s'
            group by ail.id 
            order by ail.id)a
            '''%(accountid[0],date_from,date_to)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
            total = move['taxamount']
            #total = round(total1,0)
            return total or 0.00
        
   
    def get_total_openbal(self,lineid):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        accountid = wizard_data['account_id']
        #invoice_date = invdate       
        line_id = lineid        
        temp_taxamt = 0
        
        #=======================================================================
        # sql = '''
        #         select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
        #         else sum(ail.line_net*(at.amount/100)) end as taxamt 
        #         from account_invoice_line ail
        #         join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
        #         JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #         Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
        #         where at.description ~'STax' and at.amount>0
        #         and ail.id<%s and ai.date_invoice>='%s' and ai.date_invoice<='%s'                             
        #        '''%(accountid[0],line_id,date_from,invoice_date)       
        #=======================================================================
        sql = '''
                select COALESCE(sum(a.taxamt),0) as taxamount from( 
                select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
                else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
                from account_invoice_line ail
                join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
                JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
                where at.description ~'STax' and at.amount>0
                and ail.id<%s and ai.date_invoice>='%s'
                group by ail.id 
                order by ail.id)a                          
               '''%(accountid[0],line_id,date_from)
        self.cr.execute(sql)        
        for move in self.cr.dictfetchall():
            #move_amnt = move['taxamt']
            #temp_t = temp_taxamt
            temp_taxamt += move['taxamount']
        return temp_taxamt or 0.00
   
    
    def get_debit_balance(self):
            wizard_data = self.localcontext['data']['form']
            #date_from = wizard_data['date_from']
            date_to = wizard_data['date_to']
            accountid = wizard_data['account_id']
            openbalance = 0.00
            net_amt = 0.00
            sql = '''
                select sum(aml.credit) as debit 
                from account_move_line aml
                inner join account_move am on (am.id=aml.move_id)
                inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
                join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
                where aml.debit>0 and am.state in ('posted') and i.date_invoice < '%s'
                '''%(accountid[0],date_to)
            self.cr.execute(sql)            
            for move in self.cr.dictfetchall():
                if move['debit']:
                    openbalance += move['debit']                    
            return openbalance or 0.00
        
    def get_opening_balance(self):
            wizard_data = self.localcontext['data']['form']
            date_from = wizard_data['date_from']
            #date_to = wizard_data['date_to']
            accountid = wizard_data['account_id']
            openbalance = 0.00
            net_amt = 0.00
            sql = '''
                select COALESCE(sum(a.taxamt),0) as taxamount from( 
                select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
                else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
                from account_invoice_line ail
                join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
                JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
                where at.description ~'STax' and at.amount>0
                and ai.date_invoice<'%s'
                group by ail.id 
                order by ail.id)a
                '''%(accountid[0],date_from)
            self.cr.execute(sql)
            #print sql
            for move in self.cr.dictfetchall():
                if move['taxamount']:
                    openbalance += move['taxamount']
                    #op_amount = openbalance+net_amt
            return openbalance or 0.00
        
    def get_invoice(self):
            wizard_data = self.localcontext['data']['form']
            date_from = wizard_data['date_from']
            date_to = wizard_data['date_to']
            accountid = wizard_data['account_id']
            #res = {}
            
            invoice_obj = self.pool.get('account.invoice.line')
            sql = '''
                select ail.id from account_invoice_line ail
                join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
                JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
                where at.description ~'STax' and at.amount>0 and ai.date_invoice between '%s' and '%s' 
                order by ail.id
                --order by ai.date_invoice,ai.bill_number,ai.bill_date
                '''%(accountid[0],date_from,date_to) 
            self.cr.execute(sql)
            #print sql
            invoice_ids = [r[0] for r in self.cr.fetchall()]
            return invoice_obj.browse(self.cr,self.uid,invoice_ids)

    def get_tax(self, invoice_line_tax_id):
        tax_amounts = 0
        tax_amounts = [r.amount for r in invoice_line_tax_id]
        return tax_amounts
    
    def get_paid_tax(self, invoice_line_tax_id, total):
        tax_paid = 0
        if invoice_line_tax_id:
            tax_amounts = [r.amount for r in invoice_line_tax_id]
            for tax in tax_amounts:
                tax_paid = tax*total/100
        return round(tax_paid,2)
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

