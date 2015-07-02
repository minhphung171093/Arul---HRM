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
             #'get_ven_name':self.get_ven_name,
             #'get_inv_type':self.get_inv_type,
            'get_move_ids':self.get_move_ids,
            #'get_tds_perc':self.get_tds_perc,           
            #'get_cus':self.get_cus,
            #'get_doc_type':self.get_doc_type,
            
            
            
        })
    
    
         
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y') 
    
    def get_doc_type(self):
        wizard_data = self.localcontext['data']['form']
        type = (wizard_data['invoice_type'])
        type_obj = self.pool.get('account.move')
        #vendor = ven_obj.browse(self.cr,self.uid,ven[0])
        actmove = type_obj.browse(self.cr,self.uid,type[0])
        print actmove.doc_type        
        if actmove.doc_type == 'ser_inv':
            return "Service Invoice"
        if actmove.doc_type == 'sup_inv':
            return "Supplier Invoice (Without PO)"
        if actmove.doc_type == 'freight':
            return "Freight Invoice"
        #account.move
        
#         if doc_type == 'ser_inv':
#             return "Service Invoice"
#         if doc_type == 'sup_inv':
#             return "Supplier Invoice (Without PO)" 
#         if doc_type == 'freight':
#             return "Freight Invoice"  
    
        
    
    def get_cus(self):
        wizard_data = self.localcontext['data']['form']
        ven = (wizard_data['employee'])
        ven_obj = self.pool.get('res.partner')
        return ven_obj.browse(self.cr,self.uid,ven[1])
    
    #===========================================================================
    # def get_ven_name(self):
    #     wizard_data = self.localcontext['data']['form']
    #     return wizard_data['employee']
    #===========================================================================
    
    def get_tds_perc(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['taxes_id']    
  
        
        
        
    def get_move_ids(self):
        wizard_data = self.localcontext['data']['form']
        tdsperc_obj = self.pool.get('account.invoice.line')       
        move_lines = []
        date_arr = []        
        invoicetype = wizard_data['invoice_type']
        vendor = wizard_data['employee']
        tds = wizard_data['taxes_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']        
                
        if invoicetype == 'ser_inv':
              if vendor and tds:
                    sql = '''
                            select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                            case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                            when am.doc_type ='ser_inv' then 'Service Invoice'
                            when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                            when am.doc_type ='freight' then 'Freight Invoice'
                            else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                            ai.name as invoicedocno, ai.date_invoice as postingdate,
                            ai.bill_number as bill_no,ai.bill_date as bill_date,
                            sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                            round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                            from account_invoice_line ail
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join account_move am on (am.name=ai.number)
                            join res_partner bp on (bp.id=ai.partner_id)
                            join account_tax at on (at.id=ail.tds_id)
                            where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('ser_inv')
                            and ai.date_invoice between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
                            group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                            ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                            order by vendor_code
                        '''%(date_from,date_to,vendor[0],tds[0])
                    self.cr.execute(sql)                    
                    return self.cr.dictfetchall()  
              elif vendor:
                sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                        round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        join account_move am on (am.name=ai.number)
                        join res_partner bp on (bp.id=ai.partner_id)
                        join account_tax at on (at.id=ail.tds_id)
                        where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('ser_inv')
                        and ai.date_invoice between '%s' and '%s' and bp.id = '%s'
                        group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                        ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                        order by vendor_code
                    '''%(date_from,date_to,vendor[0])
                self.cr.execute(sql)                
                return self.cr.dictfetchall()
            
              elif tds:
                sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                        round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        join account_move am on (am.name=ai.number)
                        join res_partner bp on (bp.id=ai.partner_id)
                        join account_tax at on (at.id=ail.tds_id)
                        where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('ser_inv')
                        and ai.date_invoice between '%s' and '%s' and at.id = '%s'
                        group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                        ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                        order by vendor_code
                    '''%(date_from,date_to,tds[0])
                self.cr.execute(sql)                
                return self.cr.dictfetchall()          
            
              else:
                sql = '''
                            select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                            case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                            when am.doc_type ='ser_inv' then 'Service Invoice'
                            when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                            when am.doc_type ='freight' then 'Freight Invoice'
                            else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                            ai.name as invoicedocno, ai.date_invoice as postingdate,
                            ai.bill_number as bill_no,ai.bill_date as bill_date,
                            sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                            round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                            from account_invoice_line ail
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join account_move am on (am.name=ai.number)
                            join res_partner bp on (bp.id=ai.partner_id)
                            join account_tax at on (at.id=ail.tds_id)
                            where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('ser_inv')
                            and ai.date_invoice between '%s' and '%s'
                            group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                            ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                            order by vendor_code
                        '''%(date_from,date_to)
                self.cr.execute(sql)
                return self.cr.dictfetchall()
                        
            
            
        elif invoicetype == 'sup_inv':
            if vendor and tds:
                    sql = '''
                            select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                            case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                            when am.doc_type ='ser_inv' then 'Service Invoice'
                            when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                            when am.doc_type ='freight' then 'Freight Invoice'
                            else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                            ai.name as invoicedocno, ai.date_invoice as postingdate,
                            ai.bill_number as bill_no,ai.bill_date as bill_date,
                            sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                            round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                            from account_invoice_line ail
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join account_move am on (am.name=ai.number)
                            join res_partner bp on (bp.id=ai.partner_id)
                            join account_tax at on (at.id=ail.tds_id)
                            where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('sup_inv')
                            and ai.date_invoice between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
                            group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                            ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                            order by vendor_code
                        '''%(date_from,date_to,vendor[0],tds[0])
                    self.cr.execute(sql)                   
                    return self.cr.dictfetchall()  
            elif vendor:
                sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                        round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        join account_move am on (am.name=ai.number)
                        join res_partner bp on (bp.id=ai.partner_id)
                        join account_tax at on (at.id=ail.tds_id)
                        where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('sup_inv')
                        and ai.date_invoice between '%s' and '%s' and bp.id = '%s'
                        group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                        ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                        order by vendor_code
                    '''%(date_from,date_to,vendor[0])
                self.cr.execute(sql)                
                return self.cr.dictfetchall()
          
            elif tds:
                sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                        round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        join account_move am on (am.name=ai.number)
                        join res_partner bp on (bp.id=ai.partner_id)
                        join account_tax at on (at.id=ail.tds_id)
                        where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('sup_inv')
                        and ai.date_invoice between '%s' and '%s' and at.id = '%s'
                        group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                        ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                        order by vendor_code
                    '''%(date_from,date_to,tds[0])
                self.cr.execute(sql)                
                return self.cr.dictfetchall()  
                        
             
            else:
                sql = '''
                            select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                            case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                            when am.doc_type ='ser_inv' then 'Service Invoice'
                            when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                            when am.doc_type ='freight' then 'Freight Invoice'
                            else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                            ai.name as invoicedocno, ai.date_invoice as postingdate,
                            ai.bill_number as bill_no,ai.bill_date as bill_date,
                            sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                            round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                            from account_invoice_line ail
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join account_move am on (am.name=ai.number)
                            join res_partner bp on (bp.id=ai.partner_id)
                            join account_tax at on (at.id=ail.tds_id)
                            where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('sup_inv')
                            and ai.date_invoice between '%s' and '%s'
                            group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                            ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                            order by vendor_code
                        '''%(date_from,date_to)
                self.cr.execute(sql)
                return self.cr.dictfetchall()
        
        elif invoicetype == 'freight':
            if vendor and tds:
                    sql = '''
                            select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                            case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                            when am.doc_type ='ser_inv' then 'Service Invoice'
                            when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                            when am.doc_type ='freight' then 'Freight Invoice'
                            else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                            ai.name as invoicedocno, ai.date_invoice as postingdate,
                            ai.bill_number as bill_no,ai.bill_date as bill_date,
                            sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                            round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                            from account_invoice_line ail
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join account_move am on (am.name=ai.number)
                            join res_partner bp on (bp.id=ai.partner_id)
                            join account_tax at on (at.id=ail.tds_id)
                            where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('freight')
                            and ai.date_invoice between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
                            group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                            ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                            order by vendor_code
                        '''%(date_from,date_to,vendor[0],tds[0])
                    self.cr.execute(sql)                    
                    return self.cr.dictfetchall()  
            elif vendor:
                sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                        round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        join account_move am on (am.name=ai.number)
                        join res_partner bp on (bp.id=ai.partner_id)
                        join account_tax at on (at.id=ail.tds_id)
                        where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('freight')
                        and ai.date_invoice between '%s' and '%s' and bp.id = '%s'
                        group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                        ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                        order by vendor_code
                    '''%(date_from,date_to,vendor[0])
                self.cr.execute(sql)                
                return self.cr.dictfetchall()
           
            elif tds:
                sql = '''
                        select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                        case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                        when am.doc_type ='ser_inv' then 'Service Invoice'
                        when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                        when am.doc_type ='freight' then 'Freight Invoice'
                        else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                        ai.name as invoicedocno, ai.date_invoice as postingdate,
                        ai.bill_number as bill_no,ai.bill_date as bill_date,
                        sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                        round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        join account_move am on (am.name=ai.number)
                        join res_partner bp on (bp.id=ai.partner_id)
                        join account_tax at on (at.id=ail.tds_id)
                        where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('freight')
                        and ai.date_invoice between '%s' and '%s' and at.id = '%s'
                        group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                        ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                        order by vendor_code
                    '''%(date_from,date_to,tds[0])
                self.cr.execute(sql)                
                return self.cr.dictfetchall()             
            
            else:
                sql = '''
                            select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                            case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                            when am.doc_type ='ser_inv' then 'Service Invoice'
                            when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                            when am.doc_type ='freight' then 'Freight Invoice'
                            else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                            ai.name as invoicedocno, ai.date_invoice as postingdate,
                            ai.bill_number as bill_no,ai.bill_date as bill_date,
                            sum(ail.amount_basic) as base_amnt,round(at.amount,0) as tax_deduction,
                            round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                            from account_invoice_line ail
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join account_move am on (am.name=ai.number)
                            join res_partner bp on (bp.id=ai.partner_id)
                            join account_tax at on (at.id=ail.tds_id)
                            where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('freight')
                            and ai.date_invoice between '%s' and '%s'
                            group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id, 
                            ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                            order by vendor_code
                        '''%(date_from,date_to)
                self.cr.execute(sql)
                return self.cr.dictfetchall()
        
        else:
            sql = '''
                    select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
                    case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
                    when am.doc_type ='ser_inv' then 'Service Invoice'
                    when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
                    when am.doc_type ='freight' then 'Freight Invoice'
                    else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
                    ai.name as invoicedocno, ai.date_invoice as postingdate,
                    ai.bill_number as bill_no,ai.bill_date as bill_date,
                    sum(ail.amount_basic) as base_amnt, round(at.amount,0) as tax_deduction, 
                    round(sum(ail.amount_basic)*at.amount/100,0) as tdsamount, ai.vendor_ref as ven_ref
                    from account_invoice_line ail
                    join account_invoice ai on (ai.id=ail.invoice_id)
                    join account_move am on (am.name=ai.number)
                    join res_partner bp on (bp.id=ai.partner_id)
                    join account_tax at on (at.id=ail.tds_id)
                    where ai.type='in_invoice' and ail.tds_id is not null and am.doc_type in ('sup_pay', 'ser_inv', 'freight')
                    and ai.date_invoice between '%s' and '%s'
                    group by bp.vendor_code, bp.name, pan_tin, am.doc_type, ai.date_invoice,ail.tds_id,
                    ai.name, ai.name, at.amount, ai.bill_number, ai.bill_date, ai.vendor_ref
                    order by vendor_code
                '''%(date_from,date_to)
            self.cr.execute(sql)
            return self.cr.dictfetchall()

    
    
    #===========================================================================
    # def get_tds_perc(self):
    #     wizard_data = self.localcontext['data']['form']
    #     tdsperc = (wizard_data['tds_id'])        
    #     tdsperc_obj = self.pool.get('account.invoice.line')
    #     return tdsperc_obj.browse(self.cr,self.uid,tdsperc[0])
    # 
    # def get_tds_form(self):
    #     wizard_data = self.localcontext['data']['form']
    #     date_from = wizard_data['date_from']
    #     date_to = wizard_data['date_to']
    #     vendor = wizard_data['employee']   
    #     tds = wizard_data['tds_id']
    #     type = wizard_data['invoice_type']
    #     vendor_obj = self.pool.get('res.partner')
    #     
    #     if type == 'serviceinvoice':
    #         account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash'), ('type_trans', '=', 'serviceinvoice')])
    #     elif type == 'serviceinvoicepo':
    #         account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash'), ('type_trans', '=', 'receipt')])
    #     elif type == 'freightinvoice':
    #         account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash'), ('type_trans', '=', 'receipt')])
    #     else:   
    #         account_ids = account_voucher_obj.search(self.cr,self.uid,[('date', '>=', date_from), ('date', '<=', date_to), ('type_cash_bank', '=', 'cash')])
    #     return account_voucher_obj.browse(self.cr,self.uid,account_ids)
    #     
    #     res = []
    #     
    #     if vendor is true:
    #         sql = ''' select id from res_partner where department_id=%s and 
    #             resource_id in (select id from resource_resource where active='t')
    #             '''%(department[0])
    #         self.cr.execute(sql)
    #         employee_ids = [r[0] for r in self.cr.fetchall()]
    #===========================================================================
        
        
        
    
    #===========================================================================
    # def get_tds_form(selfself):
    #     wizard_data = self.localcontext['data']['form']
    #     date_from = wizard_data['date_from']
    #     date_to = wizard_data['date_to']
    #===========================================================================
              
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

