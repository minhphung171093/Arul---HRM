# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_tds_header(osv.osv_memory):
    _name = "tpt.tds.header.from"
    _columns = {
                'name': fields.char('', readonly=True),                
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'date_from_title': fields.char('', size = 1024), #YuVi
                'date_to_title': fields.char('', size = 1024), #YuVi
                'employee': fields.many2one('res.partner', 'Vendor',ondelete='restrict'),
                'taxes_id':fields.many2one('account.tax','TDS %'),                 
                'code':fields.many2one('account.account', 'GL Account'),
                'invoice_type':fields.selection([('ser_inv','Service Invoice'),('sup_inv','Supplier Invoice (Without PO)'),('freight','Freight Invoice')],'Invoice Type'),
                'tpt_tds_line': fields.one2many('tpt.tds.line', 'tds_id', 'General Line'),
    }
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.tds.header.from'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tds_form_report_pdf', 'datas': datas}
    
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.tds.header.from'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tds_form_report_xls', 'datas': datas}
    
tpt_tds_header()

class tpt_tds_line(osv.osv_memory):
    _name = "tpt.tds.line"
    _columns = {
        'tds_id': fields.many2one('tpt.tds.header.from','TDS Header', ondelete='cascade'),
        'ven_code': fields.char('Vendor Code', size = 1024),
        'ven_name': fields.char('Vendor Name', size = 1024),        
        'vendor_pan_no': fields.char('PAN No', size = 1024),        
        'officialwitholdingtax': fields.char('Document Type', size = 1024),
        'gl_doc': fields.char('GL Document No', size = 1024),
        'sec': fields.char('Holding Tax and Sec', size = 1024),
        'posting_date': fields.date('Posting Date'), 
        'invoicedocno': fields.char('Document No', size = 1024),
        'doc_date': fields.date('Document Date'),
        'bill_no': fields.char('Bill No', size = 1024),
        'bill_date': fields.date('Bill Date', size = 1024), 
        'base_amnt': fields.char('Base Amount', size = 1024), #Yuvi        
        'tax_deduction': fields.char('Tax Deduct', size = 1024),
        'tdsamount': fields.char('TDS Amount', size = 1024), #Yuvi
        'ven_ref': fields.char('Reference', size = 1024),
        
                                                              
    }
tpt_tds_line()


class tds_form_report(osv.osv_memory):
    _name = "tds.form.report"
    _columns = {
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),                 
                'employee': fields.many2one('res.partner', 'Vendor',ondelete='restrict'),                
                'taxes_id':fields.many2one('account.tax','TDS %'),                 
                'code':fields.many2one('account.account', 'GL Account'),
                'invoice_type':fields.selection([('ser_inv','Service Invoice'),('sup_inv','Supplier Invoice (Without PO)'),('freight','Freight Invoice')],'Invoice Type'),
               }
    
    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def print_report(self, cr, uid, ids, context=None):
        
        def get_total(invoice):
            sum = 0.00
            for line in invoice:
                if line['tdsamount']:                                                                       
                    sum += line['tdsamount']          
            return sum or 0.00
                #else:
                  #  return 0.00             
        
        def get_cus(self):
            wizard_data = self.localcontext['data']['form']
            ven = (wizard_data['employee'])
            ven_obj = self.pool.get('res.partner')
            return ven_obj.browse(self.cr,self.uid,ven[1])
        
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
            
        def decimal_convert(amount):
            if amount:    
               decamount = format(amount, '.2f')
               return decamount or 0.00
            else:
               return 0.00
  
    
        def get_tds_perc(self):
            wizard_data = self.localcontext['data']['form']
            return wizard_data['taxes_id']  
        
        def get_invoice(sls):         
            res = {}
            date_from = sls.date_from
            date_to = sls.date_to
            vendor = sls.employee.id
            tds = sls.taxes_id.id
            gl_accnt = sls.code.id
            invoicetype = sls.invoice_type
            
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
            cr.execute(sql)
            with_po_ids = cr.fetchall()
            
            sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ai.type='in_invoice'
                and ail.tds_id is not null
                and ai.purchase_id is null

            '''
            cr.execute(sql)
            without_po_ids = cr.fetchall()
            
            sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ai.type='in_invoice'
                and ail.tds_id_2 is not null
                and ai.sup_inv_id is not null
            '''
            cr.execute(sql)
            freight_ids = cr.fetchall()
            sql = '''
                select ail.id from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                inner join purchase_order po on ai.purchase_id=po.id
                where ai.type='in_invoice'
                and ail.tds_id is not null
                and po.po_document_type='service'
            '''
            cr.execute(sql)
            service_ids = cr.fetchall()
            
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
                        case when am.doc_type ='sup_inv_po' then cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2))
                        when am.doc_type ='ser_inv' then ai.amount_total_tds
                        when am.doc_type ='sup_inv' then ai.amount_total_tds
                        when am.doc_type ='freight' then ai.amount_total_tds_2
                        else 0 end as tdsamount,
                        ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
                        from account_invoice_line ail
                        join account_invoice ai on (ai.id=ail.invoice_id)
                        inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
                        join res_partner bp on (bp.id=ai.partner_id)
                        left join account_tax at on (at.id=ail.tds_id or at.id=ail.tds_id_2)
                        where am.date between '%s' and '%s'                       
            '''%(date_from,date_to)
           
            if vendor:
                str1 = "and bp.id = %s"%(vendor)
                sql = sql+str1
            if tds:
                str1 = "and at.id = %s"%(tds)
                sql = sql+str1
            if gl_accnt:
                str1 = "and at.gl_account_id = %s"%(gl_accnt)
                sql = sql+str1
            if invoicetype:
                str1 = "and am.doc_type = '%s'"%(invoicetype)
                sql = sql+str1
                
            sql = sql + "and ail.id in (%s)"%(inv_ids)
                
            cr.execute(sql)
            invoice_data = cr.dictfetchall()
            
            
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
                str1 = "and bp.id = %s"%(vendor)     
                sql = sql+str1       
            if gl_accnt:
                str1 = " and aa.id = %s"%(gl_accnt) 
                sql = sql+str1
                     
            cr.execute(sql)
            voucher_data = cr.dictfetchall()            
            return invoice_data + voucher_data
            
            
            
            
#===============================================================================
#             invoicetype = sls.invoice_type
#             vendor = sls.employee.id
#             tds = sls.taxes_id.id
#             gl_accnt = sls.code.id
#             base_amnt = 0.0
#             tdsamount = 0.0
#             
#             if invoicetype == 'ser_inv':
#               if vendor and tds and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                       
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                     cr.execute(sql)                                      
#                     return cr.dictfetchall()
#             
#               elif vendor and tds:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'                                                       
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,tds,date_from,date_to,vendor,tds,date_from,date_to,vendor)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()       
#        
#               elif vendor and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'                                                       
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()            
#           
#               elif tds and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,tds,gl_accnt,date_from,date_to,tds,gl_accnt,date_from,date_to,gl_accnt)
#                     cr.execute(sql)                                   
#                     return cr.dictfetchall()           
#                      
#               elif vendor:
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' 
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,vendor,date_from,date_to,vendor,date_from,date_to,vendor)
#                 cr.execute(sql)                
#                 return cr.dictfetchall()
#             
#               elif tds:
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'  
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,tds,date_from,date_to,tds,date_from,date_to)
#                 cr.execute(sql)                
#                 return cr.dictfetchall() 
#             
#               elif gl_accnt:
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'   
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,gl_accnt,date_from,date_to,gl_accnt,date_from,date_to,gl_accnt)
#                 cr.execute(sql)                
#                 return cr.dictfetchall()          
#             
#               else:
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('ser_inv')
#                         and am.date between '%s' and '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'    
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,date_from,date_to,date_from,date_to)
#                 cr.execute(sql)                
#                 return cr.dictfetchall()
#             
#             elif invoicetype == 'sup_inv':
#                 if vendor and tds and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'    
#                         )a
#                         order by a.ven_code,a.gl_doc                         
#                         '''%(date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()
#                 
#                 elif vendor and tds:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'    
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,tds,date_from,date_to,vendor,tds,date_from,date_to,vendor)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()
#                 
#                 elif vendor and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()
#                 
#                 elif tds and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,tds,gl_accnt,date_from,date_to,tds,gl_accnt,date_from,date_to,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()
#                 
#                 elif vendor:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and bp.id = '%s'                                                        
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,date_from,date_to,vendor,date_from,date_to,vendor)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()
#                 
#                 elif tds:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and at.id = '%s'                                                         
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,tds,date_from,date_to,tds,date_from,date_to)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()
#                 
#                 elif gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'                                                         
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,gl_accnt,date_from,date_to,gl_accnt,date_from,date_to,gl_accnt)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()
#                 
#                 else:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv')
#                         and am.date between '%s' and '%s'                                                            
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'      
#                         )a
#                         order by a.ven_code,a.gl_doc
#                             '''%(date_from,date_to,date_from,date_to,date_from,date_to)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()  
#                     ##sup_inv
#             
#             ##freight
#             elif invoicetype == 'freight':
#                   if vendor and tds and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                            
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'      
#                         )a
#                         order by a.ven_code,a.gl_doc                          
#                         '''%(date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()
#                 
#                   elif vendor and tds:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
#                         
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'                                                             
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'        
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,tds,date_from,date_to,vendor,tds,date_from,date_to,vendor)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()      
#            
#                   elif vendor and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'  
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'                                                             
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'        
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()            
#               
#                   elif tds and gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s' 
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                             
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'           
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,tds,gl_accnt,date_from,date_to,tds,gl_accnt,date_from,date_to,gl_accnt)
#                     cr.execute(sql)                    
#                     return cr.dictfetchall()           
#                          
#                   elif vendor:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s'                                                               
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'               
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,vendor,date_from,date_to,vendor,date_from,date_to,vendor)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()
#                 
#                   elif tds:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and at.id = '%s'                                                               
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'                
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,tds,date_from,date_to,tds,date_from,date_to)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()  
#                 
#                   elif gl_accnt:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'                
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,gl_accnt,date_from,date_to,gl_accnt,date_from,date_to,gl_accnt)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()          
#                   
#                   else:
#                     sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('freight')
#                         and am.date between '%s' and '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'                
#                         )a
#                         order by a.ven_code,a.gl_doc
#                         '''%(date_from,date_to,date_from,date_to,date_from,date_to)
#                     cr.execute(sql)                
#                     return cr.dictfetchall()
#             ##freightend
#             
#             elif vendor and tds and gl_accnt:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'                
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,tds,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                 cr.execute(sql)
#                 return cr.dictfetchall()
#             
#             elif vendor and gl_accnt:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.gl_account_id = '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s' and aa.id = '%s'                
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt,date_from,date_to,vendor,gl_accnt)
#                 cr.execute(sql)               
#                 return cr.dictfetchall()
#             
#             elif vendor and tds:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s' and at.id = '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'                 
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,vendor,tds,date_from,date_to,vendor,tds,date_from,date_to,vendor)
#                 cr.execute(sql)
#                 return cr.dictfetchall()
#             
#             elif tds and gl_accnt:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and at.id = '%s' and at.gl_account_id = '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'                 
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,tds,gl_accnt,date_from,date_to,tds,gl_accnt,date_from,date_to,gl_accnt)
#                 cr.execute(sql)
#                 return cr.dictfetchall()
#             
#             elif vendor:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and bp.id = '%s'                                                                
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and bp.id = '%s'                   
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,vendor,date_from,date_to,vendor,date_from,date_to,vendor)
#                 cr.execute(sql)
#                 return cr.dictfetchall()
#             
#             elif tds:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and at.id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and at.id = '%s'                                                                 
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'                     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,tds,date_from,date_to,tds,date_from,date_to)
#                 cr.execute(sql)
#                 return cr.dictfetchall()
#             
#             elif gl_accnt:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s' and at.gl_account_id = '%s'                                                                  
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s' and aa.id = '%s'                     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,gl_accnt,date_from,date_to,gl_accnt,date_from,date_to,gl_accnt)
#                 cr.execute(sql)
#                 print sql
#                 return cr.dictfetchall()
#             
#             else:            
#                 sql = '''
#                         Select a.ven_code,a.ven_name,a.vendor_pan_no,a.officialwitholdingtax,
#                         a.tds_id,a.invoicedocno,a.postingdate,a.bill_no,a.bill_date,a.base_amnt,a.tax_deduction,
#                         COALESCE(a.tdsamount,0.00) as tdsamount,a.ven_ref,a.gl_doc,a.sec
#                         from(
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.amount_basic as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.amount_basic)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                                             
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id)
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id is not null
#                         and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s'
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when am.doc_type ='sup_inv_po' then 'Supplier Invoice with PO' 
#                         when am.doc_type ='ser_inv' then 'Service Invoice'
#                         when am.doc_type ='sup_inv' then 'Supplier Invoice Without PO' 
#                         when am.doc_type ='freight' then 'Freight Invoice'
#                         else '' end as officialwitholdingtax,null as witholdingtaxsectioon, ail.tds_id, 
#                         ai.name as invoicedocno, ai.date_invoice as postingdate,
#                         ai.bill_number as bill_no,ai.bill_date as bill_date,
#                         ail.line_net as base_amnt, at.name as tax_deduction, 
#                         cast(round((ail.line_net)*at.amount/100,0) As decimal(8, 2)) as tdsamount, 
#                         ai.vendor_ref as ven_ref, ai.number as gl_doc,at.section as sec
#                         from account_invoice_line ail
#                         join account_invoice ai on (ai.id=ail.invoice_id)
#                         inner join account_move am on (am.name=ai.number and ai.move_id = am.id)                       
#                         join res_partner bp on (bp.id=ai.partner_id)
#                         left join account_tax at on (at.id=ail.tds_id_2)                                             
#                         where am.state = 'posted' and ai.type='in_invoice' 
#                         and ail.tds_id_2 is not null and am.doc_type in ('sup_inv', 'ser_inv', 'freight')
#                         and am.date between '%s' and '%s'                                                                  
# 
#                         union all
# 
#                         select bp.vendor_code as ven_code, bp.name as ven_name,bp.pan_tin as vendor_pan_no,
#                         case when av.type = 'receipt' then 'Receipt'
#                         when av.type = 'payment' then 'Payment'
#                         when av.type = 'sale' then 'Sale'
#                         when av.type = 'purhase' then 'Purhase' else '' end as officialwitholdingtax,
#                         null as witholdingtaxsection,null as tds_id,av.name as invoicedocno,av.date,null as bill_number,null as bill_date,
#                         0.00 as base_amnt,null as tax_deduction,
#                         Case when aml.debit = '0.00' then -aml.credit else aml.debit end as tdsamount,
#                         av.reference as ven_ref,av.number as gl_doc,null as sec
#                         from account_voucher av
#                         join res_partner bp on (bp.id=av.partner_id)
#                         inner join account_voucher_line avl on av.id=avl.voucher_id
#                         inner join account_account aa on avl.account_id=aa.id
#                         inner join account_move am on (am.id=av.move_id)
#                         inner join account_move_line aml on (aml.move_id=av.move_id and aa.id = aml.account_id)
#                         where am.state = 'posted' and aa.name ~ 'TDS' 
#                         and am.date between '%s' and '%s'                     
#                         )a
#                         order by a.ven_code,a.gl_doc
#                     '''%(date_from,date_to,date_from,date_to,date_from,date_to)
#                 cr.execute(sql)
#                 return cr.dictfetchall()
#===============================================================================
            
           
              
       
        cr.execute('delete from tpt_tds_header_from')
        sls_obj = self.pool.get('tpt.tds.header.from')
        sls = self.browse(cr, uid, ids[0])
        sls_line = []
        for line in get_invoice(sls):
            sls_line.append((0,0,{
                'ven_code': line['ven_code'],                  
                'ven_name': line['ven_name'],                
                'vendor_pan_no': line['vendor_pan_no'],
                'sec': line['sec'],
                'gl_doc': line['gl_doc'],
                'officialwitholdingtax': line['officialwitholdingtax'],
                'posting_date': line['postingdate'],
                'invoicedocno': line['invoicedocno'],
                'doc_date': line['postingdate'],
                'bill_no': line['bill_no'],
                'bill_date': line['bill_date'],
                'base_amnt': decimal_convert(line['base_amnt']),
                'tax_deduction': line['tax_deduction'],
                'tdsamount': decimal_convert(line['tdsamount']) or 0.00,
                'ven_ref': line['ven_ref'],
            }))            
        sls_line.append((0,0,{
                'tax_deduction' : 'Total',
                'tdsamount': decimal_convert(get_total(get_invoice(sls))) or 0.00,           
        }))
        vals = {
                'name': 'TDS Report',
                'date_from_title': 'Date From: ', #YuVi
                'date_to_title': 'Date To: ', #YuVi                
                'date_from': sls.date_from,
                'date_to': sls.date_to,
                'invoice_type':  sls.invoice_type or False,
                'employee': sls.employee.id or False,
                'taxes_id': sls.taxes_id.id or False,
                'code': sls.code.id or False,      
                'tpt_tds_line': sls_line,
            }
        sls_id = sls_obj.create(cr, uid, vals)
               
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_accounting', 'view_tpt_tds_header')
        return {
                        'name': 'TDS Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'tpt.tds.header.from',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': sls_id,
                }
 
tds_form_report()