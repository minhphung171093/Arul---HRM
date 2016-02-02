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
import openerp.addons.decimal_precision as dp
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
            'convert_date_format':self.convert_date_format,
            'decimal_convert':self.decimal_convert,
            'get_move_ids':self.get_move_ids,
            'get_total':self.get_total,
        })
             
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y') 
    
    def convert_date_format(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')         
        
    def get_total(self,invoice):
        sum = 0.00
        for line in invoice:
            if line['tdsamount']:                       
                sum += line['tdsamount']             
        return sum or 0.00
           
        
    def decimal_convert(self, amount):
        if amount:       
             decamount = format(amount, '.2f')
             return decamount
        else:
             return 0.00
 
    def get_cus(self):
        wizard_data = self.localcontext['data']['form']
        ven = (wizard_data['employee'])
        ven_obj = self.pool.get('res.partner')
        return ven_obj.browse(self.cr,self.uid,ven[1])    
  
    
    def get_tds_perc(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['taxes_id']    
     
        
    def get_move_ids(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        tdsperc_obj = self.pool.get('account.invoice.line')  
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        vendor = wizard_data['employee']
        tds = wizard_data['taxes_id']
        gl_accnt = wizard_data['code']            
        invoicetype = wizard_data['invoice_type']         
        base_amnt = 0.0
        tdsamount = 0.0      
        
        invoice_ids = []
        inv_vouch_ids = []
        
        sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ai.type='in_invoice'
                and ail.tds_id is not null
                and ai.purchase_id is not null
            '''
        self.cr.execute(sql)
        with_po_ids = self.cr.fetchall()
            
        sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ai.type='in_invoice'
                and ail.tds_id is not null
                and ai.purchase_id is null

            '''
        self.cr.execute(sql)
        without_po_ids = self.cr.fetchall()
            
        sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ai.type='in_invoice'
                and ail.tds_id_2 is not null
                and ai.sup_inv_id is not null
            '''
        self.cr.execute(sql)
        freight_ids = self.cr.fetchall()
        
        sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                inner join purchase_order po on ai.purchase_id=po.id
                where ai.type='in_invoice'
                and ail.tds_id is not null
                and po.po_document_type='service'
            '''
        self.cr.execute(sql)
        service_ids = self.cr.fetchall()
        
        invoice_ids = with_po_ids + without_po_ids + freight_ids + service_ids
            
        old_inv_ids = str(invoice_ids).replace("[", "").replace("]", "").replace(",),", ",").replace("(", "")            
            
        inv_ids = str(old_inv_ids).replace(",)", "")
        
        
        sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        ail.amount_basic as base_amnt, at.name as tax_deduction, 
                        --cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount,                         
                        case when  am.doc_type='freight' then
                        case when ail.fright_fi_type='3' then
                        cast(round((cast(coalesce(ail.fright,0) As decimal(8,2))*quantity)*at.amount/100,0) As decimal(8, 2))
                        else
                        cast(round((cast(coalesce(ail.fright,0) As decimal(8,2)))*at.amount/100,0) As decimal(8, 2))
                        end
                        else cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2))
                        end as tdsamount,
                        ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
                        join res_partner bp on (bp.id=ai.partner_id)
                        left join account_tax at on (at.id=ail.tds_id or at.id=ail.tds_id_2)
                        where am.date between '%s' and '%s'                       
        '''%(date_from,date_to)
           
        if vendor:
            str1 = "and bp.id = '%s'"%(vendor[0])
            sql = sql+str1
        if tds:
            str1 = "and at.id = %s"%(tds[0])
            sql = sql+str1
        if gl_accnt:
            str1 = "and at.gl_account_id = %s"%(gl_accnt[0])
            sql = sql+str1
        if invoicetype:
            str1 = "and am.doc_type = '%s'"%(invoicetype)
            sql = sql+str1
                
        sql = sql + "and ail.id in (%s)"%(inv_ids)
        self.cr.execute(sql)
        invoice_data = self.cr.dictfetchall()
        
        #TPT-SQL - av.type not in ('payment','receipt') - COMMENTED ON 01/02/2015
        #
        
        
        sql = '''
                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                         case when av.type = 'receipt' then 'Receipt'
                         when av.type = 'payment' then 'Payment'
                         when av.type = 'sale' then 'Sale'
                         when av.type = 'purchase' then 'Purchase' 
                         when av.type = 'receipt' then 'Receipt'
                         else '' end as officialwitholdingtax,
                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date as postingdate,
                         null as bill_no,null as bill_date,
                         0.00 as base_amnt,null as tax_deduction,
                         COALESCE(aml.credit,0.00) as tdsamount,
                         av.reference as ven_ref,av.number as gl_doc,null as sec
                         from account_voucher av
                         join account_journal aj on (aj.id = av.journal_id)
                         join res_partner bp on (bp.id=av.partner_id)
                         inner join account_voucher_line avl on av.id=avl.voucher_id
                         inner join account_account aa on avl.account_id=aa.id
                         inner join account_move am on (am.id=av.move_id)
                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
                         where am.state = 'posted' and aa.name ~ 'TDS' 
                         and av.type not in ('payment','receipt')
                         and am.date between '%s' and '%s'
                        
        '''%(date_from,date_to)            
        if vendor:
            str1 = " and bp.id = %s"%(vendor[0])
            sql = sql+str1          
        if gl_accnt:
            str1 = " and aa.id = %s"%(gl_accnt[0])
            sql = sql+str1
                  
        self.cr.execute(sql)
        voucher_data = self.cr.dictfetchall()            
        return invoice_data + voucher_data 
        

              
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: