# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_service_tax(osv.osv_memory):
    _name = "tpt.service.tax"
    _columns = {
        
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'account_id':fields.many2one('account.account','GL Account'),
        'service_line': fields.one2many('tpt.service.tax.line', 'service_id', 'Service tax Line'),
        
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.service.tax'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'service_tax_report', 'datas': datas}

    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.service.tax'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'service_tax_report_pdf', 'datas': datas}
    
tpt_service_tax()

class tpt_service_tax_line(osv.osv_memory):
    _name = "tpt.service.tax.line"
    _columns = {
        'service_id': fields.many2one('tpt.service.tax', 'Service tax'),
        'date': fields.date('Date'),
        'bill_no': fields.char('Bill No',size=64),
        'bill_date': fields.date('Bill Date'),
        'number': fields.char('Invoice Number'),
        'party_name': fields.many2one('res.partner', 'Party Name'),
        'open_bal': fields.float('Open. Balance',size=254),
        'taxable_amount': fields.float('Taxable Amount',size=254),
        'service_tax_rate': fields.char('Service Tax Rate',size=64),
        'service_tax': fields.float('Service Tax',size=254),
        'total': fields.float('Total',size=254),
        'debit': fields.float('Debit',size=254),
        'closing_bal': fields.float('Closing Balance',size=254),
    }

tpt_service_tax_line()


class service_tax_register(osv.osv_memory):
    _name = "service.tax.register"
    
    _columns = {
            'date_from': fields.date('Date From', required=True),
            'date_to': fields.date('Date To', required=True), 
            'account_id':fields.many2one('account.account','GL Account', required=True),
            'assessee_id':fields.selection([('vvtppl','V.V.TITANIUM PIGMENTS PRIVATE LTD')],'NAME OF THE ASSESSEE',required=True),
            'serv_tax_reg_no':fields.selection([('aad','AADCV7723PSD001')],'SERVICE TAX REGISTRATION NUMBER',required=True),
            
    }
    _defaults = {
                 'assessee_id': 'vvtppl',
                 'serv_tax_reg_no':'aad',
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

        
    '''def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'service.tax.register'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'service_tax_report', 'datas': datas}'''
        
    def print_report(self, cr, uid, ids, context=None):        
        
        
        def get_debit_balance(o):  
            #date_from = o.date_from
            date_to = o.date_to
            account_id = o.account_id
            openbalance = 0.00
              
            sql = '''
                select sum(aml.credit) as debit 
                from account_move_line aml
                inner join account_move am on (am.id=aml.move_id)
                inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
                join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
                where aml.debit>0 and am.state in ('posted') and i.date_invoice < '%s'
                '''%(account_id.id,date_to)
            cr.execute(sql)
            for move in cr.dictfetchall():
                if move['debit']:
                    openbalance += move['debit']
                    #openbalance1 = round(openbalance,2) #Added by TPT-Y on 28/07/2015, for avoid roundoff issue
            return round(openbalance,2) or 0.00
        
        def get_opening_balance(o):  
            date_from = o.date_from
            account_id = o.account_id
            openbalance = 0.0  
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
                '''%(account_id.id,date_from)
            cr.execute(sql)
            for move in cr.dictfetchall():
                if move['taxamount']:
                    openbalance += move['taxamount']
            return round(openbalance,2) or 0.00
        
        
        def get_total_service_tax(o):
            date_from = o.date_from
            date_to = o.date_to
            account_id = o.account_id
            total = 0.00            
            balance = 0.0
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
                '''%(account_id.id,date_from,date_to)
            cr.execute(sql)
            for move in cr.dictfetchall():
                total += move['taxamount']                                
            return round(total,2) or 0.00
        
        def get_invoice(o):
            res = {}
            date_from = o.date_from
            date_to = o.date_to
            account_id = o.account_id
            #wizard_data = self.localcontext['data']['form']
            #date_from = wizard_data['date_from']
            #date_to = wizard_data['date_to']
            invoice_obj = self.pool.get('account.invoice.line')
            sql = '''
                select ail.id from account_invoice_line ail
                join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
                JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id=%s)
                where at.description ~'STax' and at.amount>0 and date_invoice between '%s' and '%s'
                order by ail.id
                --order by ai.date_invoice,ai.bill_number,ai.bill_date
                '''%(account_id.id,date_from, date_to) 
            cr.execute(sql)
            invoice_ids = [r[0] for r in cr.fetchall()]
            return invoice_obj.browse(cr,uid,invoice_ids)
       
           
        
        cr.execute('delete from tpt_service_tax')
        sr_obj = self.pool.get('tpt.service.tax')
        sr = self.browse(cr, uid, ids[0])
        sr_line = []
        openbalance=get_opening_balance(sr)
        debit_total=get_debit_balance(sr)
        temp_taxamt = 0
        for line in get_invoice(sr):
            for a in line.invoice_line_tax_id:
                tax_amt = a.amount
                tax_des = a.description
            #tax_amt = [a.amount for a in line.invoice_line_tax_id]
                sr_line.append((0,0,{
                    'date': line.invoice_id.date_invoice or False,
                    'bill_no': line.invoice_id.bill_number or False,
                    'bill_date': line.invoice_id.bill_date or False,
                    'number': line.invoice_id.name or False,
                    'party_name': line.invoice_id.partner_id and line.invoice_id.partner_id.id or False,
                    'open_bal': round(openbalance+temp_taxamt,2) or 0.00,
                    'taxable_amount': round(line.line_net,2) or 0.00,
                    'service_tax_rate':tax_des or '',
                    #'service_tax': line.line_net * (tax_amt/100), #Commented by TPT-Y on 28/07/15, for avoid roundoff issue
                    'service_tax': round(line.line_net * (tax_amt/100),2) or 0.00, #Added by TPT-Y on 28/07/15, for avoid roundoff issue
                    #'total': openbalance+temp_taxamt+(line.line_net * (tax_amt/100)), #Commented by TPT-Y on 28/07/15, for avoid roundoff issue
                    'total': round(openbalance+temp_taxamt+(line.line_net * (tax_amt/100)),2) or 0.00, #Added by TPT-Y on 28/07/15, for avoid roundoff issue
                    'debit': 0.00,
                    'closing_bal': round(openbalance+temp_taxamt+(line.line_net * (tax_amt/100)),2) or 0.00, #Added by TPT-Y on 28/07/15, for avoid roundoff issue
                }))
            temp_taxamt+=(line.line_net * (tax_amt/100))
        sr_line.append((0,0,{            
            'total':round(openbalance+temp_taxamt,2) or 0.00, #Added by TPT-Y on 28/07/2015, for avoid roundoff issue
            'debit':debit_total or 0.00,
            'closing_bal': round((openbalance+temp_taxamt) - debit_total,2) or 0.00, #Added by TPT-Y on 28/07/2015, for avoid roundoff issue
            
        }))
        
        sr_line.append((0,0,{            
            'service_tax_rate' : 'Total',   
            'service_tax':get_total_service_tax(sr),
                 
            
        }))        
        
        vals = {
            
            'date_from': sr.date_from,
            'date_to': sr.date_to,
            'account_id': sr.account_id.id,
            'service_line': sr_line,    
        }
        sr_id = sr_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_service_tax_register_form')
        return {
                    'name': 'service tax Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.service.tax',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': sr_id,
                }
        
        
service_tax_register()

