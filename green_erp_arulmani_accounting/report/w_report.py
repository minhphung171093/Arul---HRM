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
            'get_invoice':self.get_invoice,
            #'get_tax': self.get_tax,
            #'get_paid_tax': self.get_paid_tax,
            'convert_date': self.convert_date,
            'tpt_get_invoice':self.tpt_get_invoice,
#             'get_sale_line': self.get_sale_line,
        })
        
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        
        sql = '''
            select b.inv_doc as inv_doc,b.date_invoice,b.bill_number,b.bill_date,b.tax_name,
                b.partnername,b.tin,
                b.productname,b.vatbased_qty,b.vatbased_amt,(b.taxamt*b.vatbased_amt)/100 as paid_amt_1,b.amount_tax as paid_amt,
                b.uom from (
                select 
                rank() Over (Partition BY a.invoice_id,a.tax_id order by a.line_net desc) as productrank,
                a.inv_doc,a.date_invoice,a.bill_number,a.bill_date,a.taxamt,a.tax_name,
                a.partnername,a.tin,
                a.productname,a.vatbased_qty,a.vatbased_amt,a.amount_tax,a.uom
                from (
                select ail.invoice_id,i.name as inv_doc,i.date_invoice,i.bill_number,i.bill_date,at.name as tax_name,
                rp.name as partnername,rp.tin, 
                ail.name as productname,
                sum(ail.quantity) over (partition by ail.invoice_id,ailt.tax_id) as vatbased_qty,
            case when ed_type='1' or ed_type is null then 
            case when p_f_type='1' or p_f_type is null then
                sum((ail.quantity*ail.price_unit)+((ail.quantity*ail.price_unit)*ail.ed/100)
                +coalesce(ail.aed_id_1,0)+((ail.quantity*ail.price_unit)*ail.p_f/100)) over (partition by ail.invoice_id,ailt.tax_id) 
                 when p_f_type='2' then
                sum((ail.quantity*ail.price_unit)+((ail.quantity*ail.price_unit)*ail.ed/100)
                +coalesce(ail.aed_id_1,0)+coalesce(ail.p_f,0)) over (partition by ail.invoice_id,ailt.tax_id) 
                 when p_f_type='3' then
                sum((ail.quantity*ail.price_unit)+((ail.quantity*ail.price_unit)*ail.ed/100)
                +coalesce(ail.aed_id_1,0)+(ail.p_f*ail.quantity)) over (partition by ail.invoice_id,ailt.tax_id)  
                 else 0 
            end
            when ed_type='2' then
            case when p_f_type='1' or p_f_type is null then
                sum((ail.quantity*ail.price_unit)+coalesce(ail.ed,0)
                +coalesce(ail.aed_id_1,0)+((ail.quantity*ail.price_unit)*coalesce(ail.p_f,0)/100)) over (partition by ail.invoice_id,ailt.tax_id) 
                when p_f_type='2' then
                sum((ail.quantity*ail.price_unit)+coalesce(ail.ed,0)
                +coalesce(ail.aed_id_1,0)+coalesce(ail.p_f,0)) over (partition by ail.invoice_id,ailt.tax_id)
                when p_f_type='3' then
                sum((ail.quantity*ail.price_unit)+coalesce(ail.ed,0)
                +coalesce(ail.aed_id_1,0)+(ail.p_f*ail.quantity)) over (partition by ail.invoice_id,ailt.tax_id) 
                else 0
             end
            when ed_type='3' then
            case when p_f_type='1' or p_f_type is null then
                sum((ail.quantity*ail.price_unit)+(ail.ed*ail.quantity)+coalesce(ail.aed_id_1,0)
                +(ail.quantity*ail.price_unit)*ail.p_f/100) over (partition by ail.invoice_id,ailt.tax_id) 
                when p_f_type='2' then
                sum((ail.quantity*ail.price_unit)+(ail.ed*ail.quantity)+coalesce(ail.aed_id_1,0)
                +coalesce(ail.p_f,0)) over (partition by ail.invoice_id,ailt.tax_id) 
                when p_f_type='3' then
                    sum((ail.quantity*ail.price_unit)+(ail.ed*ail.quantity)+coalesce(ail.aed_id_1,0)
                +(ail.p_f*ail.quantity)) over (partition by ail.invoice_id,ailt.tax_id) 
               else 0
             end
            else 0
            end as vatbased_amt,
            i.amount_tax,
                ailt.tax_id,at.amount as taxamt,
                pu.name as uom,ail.line_net-ail.fright as line_net
                from account_invoice_line ail
                JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                join account_invoice i on (i.id=ail.invoice_id and type = 'in_invoice')
                join res_partner rp on (rp.id=i.partner_id)
                Join account_tax at on (at.id=ailt.tax_id)
                join product_product p on (p.id=ail.product_id)
                join product_uom pu on (pu.id=ail.uos_id)
                join account_move am on (am.id=i.move_id)
                where date_invoice between '%s' and '%s' and 
                at.description ~'VAT' and at.amount>0 and i.move_id>0 and am.state='posted' and am.doc_type<>'freight'
                )a 
                )b where b.productrank=1
            '''%(date_from, date_to)
        self.cr.execute(sql)
        #return self.cr.dictfetchall()
        #TPT-BM - TO ADD THE JOURNAL ENTRIES WITH W-FORM REPORT - ON 23/03/2016
        res = self.cr.dictfetchall()
        sql = '''
            select av.number as inv_doc, av.date date_invoice, null bill_number, null bill_date, null tax_name,
                    null partnername, null tin,
                    null productname, 0 vatbased_qty,0 as vatbased_amt,
                    avl.amount as paid_amt_1, 0 as paid_amt,
                    null uom 
    
            from account_voucher_line avl
            inner join account_voucher av on avl.voucher_id=av.id
            inner join account_account aa on avl.account_id=aa.id
            inner join account_move am on av.move_id=am.id
            where 
            av.date between '%s' and '%s' and 
            aa.code='0000119908'
        '''%(date_from, date_to)
        self.cr.execute(sql)       
        res1 = self.cr.dictfetchall()
        if res1:
            res = res+res1
        return res
        #TPT-END
    def tpt_get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']  
        res = []
        inv_obj = self.pool.get('account.invoice')
        emp_obj = self.pool.get('hr.employee')
        inv_line_obj = self.pool.get('account.invoice.line')
        sql = '''
        select  
        ai.name as inv_doc, at.description tax_name,rs.name partnername, rs.tin, ai.bill_number, ai.bill_date,ai.date_invoice,
        case when sum(ail.tpt_tax_amt)>0 then sum(ail.tpt_tax_amt) else 0 end  as paid_amt_1,
        sum(ail.quantity) as vatbased_qty, pu.name as uom, ail.name as productname, sum(ail.line_net) as vatbased_amt, sp.name grn,ai.number as number
        from account_invoice ai
            inner join account_invoice_line ail on ai.id=ail.invoice_id
            inner join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            inner join account_tax at on (at.id=ailt.tax_id)
            inner join res_partner rs on ai.partner_id=rs.id
            inner join stock_picking sp on ai.grn_no=sp.id
            inner join product_uom pu on ail.uos_id=pu.id
            where ai.date_invoice between '%s' and '%s' and
            at.description like '%s' and ai.type='in_invoice'
            and at.amount>0 and ai.doc_type<>'freight_invoice' and ai.state not in ('draft', 'cancel')
            group by at.id, ai.name, rs.name, rs.tin, ai.bill_number, ai.bill_date, ai.date_invoice, 
            sp.name,ai.number, ail.name, pu.name
        order by ai.name
        '''%(date_from, date_to, "VAT%(P)")
        self.cr.execute(sql)
        res = self.cr.dictfetchall()
        
        sql = '''
            select av.name as inv_doc, av.date date_invoice, null bill_number, null bill_date, 
            null tax_name,
            rs.name partnername, rs.tin,
            null productname, 0 vatbased_qty,av.tpt_amount_total as vatbased_amt,
            avl.amount as paid_amt_1, 0 as paid_amt,
            null uom, null as grn, av.number as number
    
            from account_voucher_line avl
            inner join account_voucher av on avl.voucher_id=av.id
            inner join account_account aa on avl.account_id=aa.id
            inner join account_move am on av.move_id=am.id
            inner join res_partner rs on av.partner_id=rs.id
            where avl.type='dr' and
            av.date between '%s' and '%s' and 
            aa.code='0000119908'
        '''%(date_from, date_to)
        self.cr.execute(sql)        
        res1 = self.cr.dictfetchall()
        if res1:
            res = res+res1
        return res  
    
    
        
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

