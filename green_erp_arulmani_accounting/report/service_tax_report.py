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
            'get_invoice_details':self.get_invoice_details,
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
    #commentted by YuVi
    #===========================================================================
    # def get_tax_desc(self,line):        
    #     sr_obj = self.pool.get('account.invoice.line')
    #     sr = sr_obj.browse(self.cr, self.uid, line)        
    #     taxid = int(sr.tax_id.id)       
    #     tx_obj = self.pool.get('account.tax')
    #     if taxid:
    #         tx = tx_obj.browse(self.cr, self.uid, taxid)        
    #         return tx.description or ''
    #     else:
    #         return ''
    #===========================================================================
    
    
    def get_total(self,cash):
            sum = 0.0
            for line in cash:                
                sum += line.debit
            return sum
    
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
   
    def get_invoice_details(self,moveid,type):
        wizard_data = self.localcontext['data']['form']
        accountid = wizard_data['account_id']       
        moveline_id = moveid
        detail_type = type
            
        sql = '''
                    select distinct ai.date_invoice as invoice_date,ai.bill_number as bill_no,
                    ai.bill_date as bill_date,ai.name as inv_name,rs.name as partner,
                    ail.line_net as linenet,t.description as desc,ail.id,ai.move_id,
                    COALESCE(ail.freight,0) as frieght_1,COALESCE(ail.fright,0) as frieght_2,am.doc_type as doc_type
                    from account_invoice_line ail
                    join account_invoice ai on (ai.id = ail.invoice_id)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax t on (t.id = ailt.tax_id)                  
                    join account_move am on (am.id = ai.move_id)
                    join account_move_line aml on (aml.move_id = am.id)
                    join res_partner rs on (rs.id = ai.partner_id)
                    where aml.name = ail.name and aml.id = %s
                '''%(moveid)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
                if type == 'billno':
                    billno = move['bill_no']
                    return billno or ''
                if type == 'billdate':
                    billdate = move['bill_date']
                    return billdate or False
                if type == 'invdate':
                    inv_date = move['invoice_date']
                    return inv_date or False
                if type == 'invname':
                    inv_name = move['inv_name']
                    return inv_name or ''
                if type == 'partner':
                    party_name = move['partner']                    
                    return party_name or ''
                if type == 'netamt':
                    if move['doc_type'] == 'freight':
                            net_amnt = move['linenet']
                            return net_amnt or 0.00
                    else:
                          net_amnt = move['linenet'] - (move['frieght_1'] + move['frieght_2'])
                          return net_amnt or 0.00
                if type == 'tax':
                    tax_rate = move['desc']
                    return tax_rate or ''
    
    
    def get_tax_amnt(self,line):
        wizard_data = self.localcontext['data']['form']
        lineid = line.id        
        accountid = wizard_data['account_id']
        #decamount = 0.00
        #=======================================================================
        # sql = '''
        #     select COALESCE(t.amount,0) as taxamnt from account_tax t            
        #     join account_invoice_line_tax ailt on (ailt.tax_id = t.id)
        #     where ailt.invoice_line_id = '%s'
        # '''%(lineid)
        #=======================================================================
        sql = '''
            select COALESCE(aml.debit,0) as debit from account_invoice_line ail
            join account_invoice ai on (ai.id = ail.invoice_id)
            join account_move am on (am.id = ai.move_id)
            join account_move_line aml on (aml.move_id = am.id and aml.account_id=%s)
            where ail.id = %s
        '''%(accountid[0],lineid)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
             debit = move['debit']
             #tax_amnt = move['debit']
             #tot_ser_tax = linet * (tax_amnt/100) #Commented by YuVi on 28/07/15, for roundoff issue
             #tot_ser_tax = round(linet * (tax_amnt/100),0) #YuVi on 28/07/15, for roundoff issue            
             return debit or 0.00
         
    def get_tot_closing_bal(self):
        wizard_data = self.localcontext['data']['form']        
        date_to = wizard_data['date_to']
        accountid = wizard_data['account_id']
        account_obj = self.pool.get('account.account')
        act_abj = account_obj.browse(self.cr,self.uid,accountid[0])
        code = act_abj.code
        
        
        #=======================================================================
        # sql = '''
        #     select COALESCE(sum(a.taxamt),0) as totamount from( 
        #     select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
        #     else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
        #     from account_invoice_line ail
        #     join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
        #     JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #     Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
        #     where at.description ~'STax' and at.amount>0
        #     and ai.date_invoice <= '%s'
        #     group by ail.id 
        #     order by ail.id)a
        # '''%(accountid[0],date_to)
        #=======================================================================
        
        #=======================================================================
        # if code == '0000119925':
        #         sql = '''
        #             select COALESCE(sum(a.debit),0) as debit from(
        #             select sum(aml.debit) as debit,aml.id
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
        #             join account_invoice_line ail on (ail.invoice_id = ai.id)
        #             join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #             join account_tax at on (at.id=ailt.tax_id)
        #             where at.description ~'STax' and at.amount>0 and aml.account_id in (402,506)
        #             and am.date <= '%s'
        #             group by aml.id 
        #             order by aml.id)a
        #         '''%(date_to)
        #         self.cr.execute(sql)
        #         for move in self.cr.dictfetchall():
        #             total = move['debit']
        #             return total or 0.00
        # elif code == '0000119926':
        #         sql = '''
        #             select COALESCE(sum(a.debit),0) as debit from(
        #             select sum(aml.debit) as debit,aml.id
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
        #             join account_invoice_line ail on (ail.invoice_id = ai.id)
        #             join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #             join account_tax at on (at.id=ailt.tax_id)
        #             where at.description ~'STax' and at.amount>0 and aml.account_id in (402,507)
        #             and am.date <= '%s'
        #             group by aml.id 
        #             order by aml.id)a
        #         '''%(date_to)
        #         self.cr.execute(sql)
        #         for move in self.cr.dictfetchall():
        #             total = move['debit']
        #             return total or 0.00
        # 
        # else: 
        #     
        #=======================================================================
            
            
        sql = '''
                    select COALESCE(sum(a.debit),0) as debit from(
                    select sum(aml.debit) as debit,aml.id
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                    join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax at on (at.id=ailt.tax_id)
                    where at.description ~'STax' and at.amount>0 and aml.account_id = %s
                    and am.date <= '%s'
                    group by aml.id 
                    order by aml.id)a
                '''%(accountid[0],date_to)              
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
                total = move['debit']
                return total or 0.00
        
    def get_total_service_tax(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        accountid = wizard_data['account_id']
        account_obj = self.pool.get('account.account')
        act_abj = account_obj.browse(self.cr,self.uid,accountid[0])
        code = act_abj.code        
        
        #=======================================================================
        # sql = '''
        #     select COALESCE(sum(a.taxamt),0) as taxamount from( 
        #     select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
        #     else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
        #     from account_invoice_line ail
        #     join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
        #     JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #     Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
        #     where at.description ~'STax' and at.amount>0
        #     and ai.date_invoice between '%s' and '%s'
        #     group by ail.id 
        #     order by ail.id)a
        #     '''%(accountid[0],date_from,date_to)
        #=======================================================================
        #=======================================================================
        # 
        # if code == '0000119925':
        #         sql = '''
        #             select COALESCE(sum(a.debit),0) as debit from( 
        #             select sum(aml.debit) as debit,ail.id
        #             from account_invoice_line ail
        #             join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
        #             JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #             Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id in (402,506))
        #             join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id in (402,506))
        #             where at.description ~'STax' and at.amount>0
        #             and ai.date_invoice between '%s' and '%s'
        #             group by ail.id 
        #             order by ail.id)a
        #             '''%(date_from,date_to)
        #         self.cr.execute(sql)
        #         for move in self.cr.dictfetchall():
        #             total = move['debit']            
        #             return total or 0.00
        #         
        # elif code == '0000119926':
        #         sql = '''
        #             select COALESCE(sum(a.debit),0) as debit from( 
        #             select sum(aml.debit) as debit,ail.id
        #             from account_invoice_line ail
        #             join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
        #             JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #             Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id in (402,507))
        #             join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id in (402,507))
        #             where at.description ~'STax' and at.amount>0
        #             and ai.date_invoice between '%s' and '%s'
        #             group by ail.id 
        #             order by ail.id)a
        #             '''%(date_from,date_to)
        #         self.cr.execute(sql)
        #         for move in self.cr.dictfetchall():
        #             total = move['debit']            
        #             return total or 0.00
        # else:
        #=======================================================================
            
        sql = '''
                    select COALESCE(sum(a.debit),0) as debit from( 
                    select sum(aml.debit) as debit,ail.id
                    from account_invoice_line ail
                    join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
                    JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    Join account_tax at on (at.id=ailt.tax_id)
                    join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id = %s)
                    where at.description ~'STax' and at.amount>0 and aml.name = ail.name
                    and ai.date_invoice between '%s' and '%s'
                    group by ail.id 
                    order by ail.id)a
                    '''%(accountid[0],date_from,date_to)
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
            total = move['debit']            
            return total or 0.00
        
    
    def get_total_openbal(self,lineid):
        #print lineid
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        accountid = wizard_data['account_id']
        account_obj = self.pool.get('account.account')
        act_abj = account_obj.browse(self.cr,self.uid,accountid[0])
        code = act_abj.code  
        line_id = lineid
        temp_taxamt = 0
       
        #=======================================================================
        # sql = '''
        #         select COALESCE(sum(a.taxamt),0) as taxamount from( 
        #         select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
        #         else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
        #         from account_invoice_line ail
        #         join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
        #         JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #         Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
        #         where at.description ~'STax' and at.amount>0
        #         and ail.id<%s and ai.date_invoice between '%s' and '%s'
        #         group by ail.id 
        #         order by ail.id)a                          
        #        '''%(accountid[0],line_id,date_from,date_to)
        #=======================================================================
        
        #=======================================================================
        # if code == '0000119925':
        #     
        #     sql = '''
        #             select COALESCE(sum(a.debit),0) as debit from(
        #             select sum(aml.debit) as debit,aml.id
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
        #             join account_invoice_line ail on (ail.invoice_id = ai.id)
        #             join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #             join account_tax at on (at.id=ailt.tax_id)
        #             where at.description ~'STax' and at.amount>0 and aml.account_id in (402,506)
        #             and am.date between '%s' and '%s'
        #             group by aml.id 
        #             order by aml.id)a                    
        #            '''%(date_from,date_to)
        #     self.cr.execute(sql)        
        #     for move in self.cr.dictfetchall():            
        #         temp_taxamt += move['debit']
        #     return temp_taxamt or 0.00
        # 
        # elif code == '0000119926':
        #     sql = '''
        #             select COALESCE(sum(a.debit),0) as debit from(
        #             select sum(aml.debit) as debit,aml.id
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
        #             join account_invoice_line ail on (ail.invoice_id = ai.id)
        #             join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
        #             join account_tax at on (at.id=ailt.tax_id)
        #             where at.description ~'STax' and at.amount>0 and aml.account_id in (402,507)
        #             and am.date between '%s' and '%s'
        #             group by aml.id 
        #             order by aml.id)a                    
        #            '''%(date_from,date_to)
        #     self.cr.execute(sql)        
        #     for move in self.cr.dictfetchall():            
        #         temp_taxamt += move['debit']
        #     return temp_taxamt or 0.00
        # 
        # else:
        #=======================================================================
            
            
        sql = '''
                    select COALESCE(sum(a.debit),0) as debit from(
                    select sum(aml.debit) as debit,aml.id
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                    join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax at on (at.id=ailt.tax_id)
                    where at.description ~'STax' 
                    and aml.id< %s and at.amount>0 and aml.account_id = %s
                    and am.date between '%s' and '%s'
                    group by aml.id 
                    order by aml.id)a                   
                   '''%(lineid,accountid[0],date_from,date_to)
        self.cr.execute(sql)        
        for move in self.cr.dictfetchall():            
            temp_taxamt += move['debit']
        return temp_taxamt or 0.00
            
       
 
    
    def get_debit_balance(self):
            wizard_data = self.localcontext['data']['form']
            date_from = wizard_data['date_from']
            date_to = wizard_data['date_to']
            accountid = wizard_data['account_id']
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(self.cr,self.uid,accountid[0])
            code = act_abj.code
            openbalance = 0.00
            net_amt = 0.00
            
            #===================================================================
            # sql = '''
            #     select sum(aml.credit) as credit 
            #     from account_move_line aml
            #     inner join account_move am on (am.id=aml.move_id)
            #     inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
            #     join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
            #     where aml.debit>0 and am.state in ('posted') and i.date_invoice between '%s' and '%s'
            #     '''%(accountid[0],date_from,date_to)
            #===================================================================
            
            #===================================================================
            # if code == '0000119925':
            #      
            #     sql = '''
            #         select sum(aml.credit) as credit 
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         inner join account_account aa on (aa.id=aml.account_id and aa.id in (402,506))
            #         join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
            #         where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
            #         '''%(date_from,date_to)
            #     self.cr.execute(sql)            
            #     for move in self.cr.dictfetchall():
            #         if move['credit']:
            #             openbalance += move['credit']                    
            #     return openbalance
            # 
            # elif code == '0000119926':
            #      
            #     sql = '''
            #         select sum(aml.credit) as credit 
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         inner join account_account aa on (aa.id=aml.account_id and aa.id in (402,507))
            #         join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
            #         where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
            #         '''%(date_from,date_to)
            #     self.cr.execute(sql)            
            #     for move in self.cr.dictfetchall():
            #         if move['credit']:
            #             openbalance += move['credit']                    
            #     return openbalance
            #===================================================================
            
            
            
        
            sql = '''
                    select sum(aml.credit) as credit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id and aa.id = %s)
                    join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
                    where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
                    '''%(accountid[0],date_from,date_to)
            self.cr.execute(sql)            
            for move in self.cr.dictfetchall():
                if move['credit']:
                    openbalance += move['credit']                    
                return openbalance
        
    def get_opening_balance(self):
            wizard_data = self.localcontext['data']['form']
            date_from = wizard_data['date_from']            
            accountid = wizard_data['account_id']
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(self.cr,self.uid,accountid[0])                     
            code = act_abj.code          
            openbalance = 0.00
            net_amt = 0.00
            
            #===================================================================
            # sql = '''
            #     select COALESCE(sum(a.taxamt),0) as taxamount from( 
            #     select case when COALESCE(sum(ail.line_net*(at.amount/100)), 0) = 0 then 0
            #     else sum(ail.line_net*(at.amount/100)) end as taxamt,ail.id
            #     from account_invoice_line ail
            #     join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #     JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #     Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
            #     where at.description ~'STax' and at.amount>0
            #     and ai.date_invoice<'%s'
            #     group by ail.id 
            #     order by ail.id)a
            #     '''%(accountid[0],date_from)
            #===================================================================
            #===================================================================
            # sql = '''
            #     select COALESCE(sum(a.debit),0) as debit from( 
            #     select sum(aml.debit) as debit,ail.id
            #     from account_invoice_line ail
            #     join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #     JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #     Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
            #     join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id=%s)
            #     where at.description ~'STax' and at.amount>0
            #     and ai.date_invoice<'%s'
            #     group by ail.id 
            #     order by ail.id)a
            #     '''%(accountid[0],accountid[0],date_from)
            #===================================================================
            
            #===================================================================
            # if code == '0000119925':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (402,506)
            #         and am.date < '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #         '''%(date_from)
            #     self.cr.execute(sql)            
            #     for move in self.cr.dictfetchall():
            #         if move['debit']:
            #             openbalance += move['debit']
            #     return openbalance or 0.00
            # 
            # elif code == '0000119926':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (402,507)
            #         and am.date < '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #         '''%(date_from)
            #     self.cr.execute(sql)            
            #     for move in self.cr.dictfetchall():
            #         if move['debit']:
            #             openbalance += move['debit']
            #     return openbalance or 0.00
            # 
            # else:
            #===================================================================
            
            
            sql = '''
                    select COALESCE(sum(a.debit),0) as debit from(
                    select sum(aml.debit) as debit,aml.id
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                    join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax at on (at.id=ailt.tax_id)
                    where at.description ~'STax' and at.amount>0 and aml.account_id = %s
                    and am.date < '%s'
                    group by aml.id 
                    order by aml.id)a
                    '''%(accountid[0],date_from)
            self.cr.execute(sql)            
            for move in self.cr.dictfetchall():
                if move['debit']:
                    openbalance += move['debit']
                return openbalance or 0.00
                
        
    def get_invoice(self):
            wizard_data = self.localcontext['data']['form']
            date_from = wizard_data['date_from']
            date_to = wizard_data['date_to']
            accountid = wizard_data['account_id']                       
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(self.cr,self.uid,accountid[0])               
            code = act_abj.id            
            invoice_obj = self.pool.get('account.move.line')
            
            #===================================================================
            # sql = '''
            #     select ail.id from account_invoice_line ail
            #     join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #     JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #     Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
            #     where at.description ~'STax' and at.amount>0 and ai.date_invoice between '%s' and '%s' 
            #     order by ail.id
            #     '''%(accountid[0],date_from,date_to) 
            #===================================================================
            
            
            #===================================================================
            # sql = '''
            #     select ail.id from account_invoice_line ail
            #     join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #     JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #     Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
            #     where at.description ~'STax' and at.amount>0 and ai.date_invoice between '%s' and '%s' 
            #     order by ail.id
            #     '''%(accountid[0],date_from,date_to) 
            #===================================================================
            
            
            #===================================================================
            # if code == '0000119925':
            #     sql = '''
            #                 select aml.id
            #                 from account_move_line aml
            #                 inner join account_move am on (am.id=aml.move_id)
            #                 join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #                 join account_invoice_line ail on (ail.invoice_id = ai.id)
            #                 join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #                 join account_tax at on (at.id=ailt.tax_id)
            #                 where at.description ~'STax' and at.amount>0 and aml.account_id in (402,506)
            #                 and am.date between '%s' and '%s'                
            #             '''%(date_from, date_to)
            #     self.cr.execute(sql)                
            #     invoice_ids = [r[0] for r in self.cr.fetchall()]
            #     return invoice_obj.browse(self.cr,self.uid,invoice_ids)
            # 
            # elif code == '0000119926':
            #     sql = '''
            #             select aml.id
            #             from account_move_line aml
            #             inner join account_move am on (am.id=aml.move_id)
            #             join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #             join account_invoice_line ail on (ail.invoice_id = ai.id)
            #             join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #             join account_tax at on (at.id=ailt.tax_id)
            #             where at.description ~'STax' and at.amount>0 and aml.account_id in (402,507)
            #             and am.date between '%s' and '%s'                
            #             '''%(date_from, date_to)
            #     self.cr.execute(sql)
            #     invoice_ids = [r[0] for r in self.cr.fetchall()]
            #     return invoice_obj.browse(self.cr,self.uid,invoice_ids)                
            # 
            # else:
            #===================================================================
            
            
            #===================================================================
            # sql = '''
            #             select aml.id
            #             from account_move_line aml
            #             inner join account_move am on (am.id=aml.move_id)
            #             join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #             join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
            #             join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #             join account_tax at on (at.id=ailt.tax_id)
            #             where at.description ~'STax' and at.amount>0 and aml.account_id = %s
            #             and am.date between '%s' and '%s'
            #             order by aml.id                
            #         '''%(accountid[0],date_from, date_to)                                          
            #===================================================================
            sql = '''
                        select aml.id
                        from account_move_line aml
                        inner join account_move am on (am.id=aml.move_id)
                        join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                        join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
                        join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                        join account_tax at on (at.id=ailt.tax_id)
                        where at.description ~'STax' and at.amount>0                                                       
                        '''
            if date_from and date_to is False:
                    str = " and am.date <= %s"%(date_from)
                    sql = sql+str
            if date_to and date_from is False:
                    str = " and am.date <= %s"%(date_to)
                    sql = sql+str
            if date_to and date_from:
                    str = " and am.date between '%s' and '%s'"%(date_from,date_to)
                    sql = sql+str
            if accountid[0]:
                    str = "  and aml.account_id = %s "%(accountid[0])
                    sql = sql+str
            sql=sql+" order by aml.id"
            self.cr.execute(sql)
            invoice_ids = [r[0] for r in self.cr.fetchall()]
            return invoice_obj.browse(self.cr,self.uid,invoice_ids)
    
#===============================================================================
#     def get_invoice(self):
#         res = {}
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         invoice_obj = self.pool.get('account.invoice.line')
#         sql = '''
#             select ail.id,
#             inv.date_invoice as invoice_date,
#             inv.bill_number as bill_no,
#             inv.bill_date as bill_dt,
#             rs.name as party_name,
#             inv.name as invoice_no,
#             ail.line_net as net_amount,
#             at.description as desp,
#             ail.line_net * (at.amount/100) as service_amt
#             from account_invoice_line ail
#             join account_invoice ai on (ai.id=ail.invoice_id)
#             JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
#             Join account_tax at on (at.id=ailt.tax_id)
#             join account_invoice inv on (ail.invoice_id = inv.id)
#             join res_partner rs on (inv.partner_id = rs.id)
#             where invoice_id in (select id from account_invoice where date_invoice between '%s' and '%s' and type = 'in_invoice') 
#             and at.description ~'STax' and at.amount>0
#             '''%(date_from, date_to)
#         #self.cr.execute(sql)
#         #invoice_ids = [r[0] for r in self.cr.fetchall()]
#         #return invoice_obj.browse(self.cr,self.uid,invoice_ids)
#         self.cr.execute(sql)                    
#         return self.cr.dictfetchall()
#         
# 
#         
#     '''def get_service_tax(self):
#         res = {}
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         invoice_obj = self.pool.get('account.invoice.line')
#         sql = 
#             select ail.id, 
#             cast(round(sum(ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount
#             from account_invoice_line ail
#             JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
#             Join account_tax at on (at.id=ailt.tax_id)
#             where invoice_id in (select id from account_invoice where date_invoice between '%s' and '%s' and type = 'in_invoice') 
#             and at.description ~'STax' and at.amount>0
#             %(date_from, date_to)
#         self.cr.execute(sql)
#         invoice_ids = [r[0] for r in self.cr.fetchall()]
#         details = invoice_obj.browse(self.cr,self.uid,invoice_ids)  
#         for line in details:
#             for a in line.invoice_line_tax_id:
#                 tax_amt = a.amount
#                 tax_des = a.description
#             
#                 return tax_des'''
#===============================================================================
    
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

