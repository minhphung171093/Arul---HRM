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
        'name': fields.char('Service Tax Register Report', size = 1024),  
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
        'service_id': fields.many2one('tpt.service.tax', 'Service tax(Header ID)'),
        'date': fields.date('Date'),
        'bill_no': fields.char('Bill No',size=64),
        'bill_date': fields.date('Bill Date'),
        'number': fields.char('Invoice Number'),
        'invoice_id':fields.many2one('account.invoice','Invoice No'),
        'partner_id':fields.many2one('res.partner','Party Name'),
         #'party_name': fields.many2one('res.partner', 'Party Name'),
        'party_name': fields.char('Party Name'),
        'open_bal': fields.float('Open. Balance',size=254),
        'taxable_amount': fields.float('Taxable Amount',size=254),
        'service_tax_rate': fields.char('Service Tax Rate',size=64),
        'service_tax': fields.float('Service Tax',size=254),
        'total': fields.float('Total',size=254),
        'debit': fields.float('Debit',size=254),
        'debit_1': fields.float('1%',size=254),
        'debit_2': fields.float('2%',size=254),
        'closing_bal': fields.float('Closing Balance',size=254),
    }

tpt_service_tax_line()


class service_tax_register(osv.osv_memory):
    _name = "service.tax.register"
    
    _columns = {
            'date_from': fields.date('Date From'),
            'date_to': fields.date('Date To'), 
            'account_id':fields.many2one('account.account','GL Account', required= True),
            'assessee_id':fields.selection([('vvtppl','V.V.TITANIUM PIGMENTS PRIVATE LTD')],'NAME OF THE ASSESSEE'),
            'serv_tax_reg_no':fields.selection([('aad','AADCV7723PSD001')],'SERVICE TAX REGISTRATION NUMBER'),
            
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
        
        def get_total(cash):
            sum = 0.0
            for line in cash:                
                sum += line.debit
            return sum
        
        def get_tax_rate_id(moveid):
            moveline_id = moveid.id
            sql = '''
                    select ail.tax_id as taxid from account_invoice_line ail
                    join account_invoice ai on (ai.id = ail.invoice_id)
                    where ail.tax_id is not null and ai.move_id = %s
                '''%(moveline_id)
            cr.execute(sql)
            for move in cr.dictfetchall():
                tax_id = move['taxid']
                return tax_id or False
        
        def get_tax_rate_desc(taxid):
            if taxid:              
                sql = '''
                        select description from account_tax where id = %s
                    '''%(taxid)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    tax_id = move['description']
                    return tax_id or False
        
        def get_invoice_details(o,moveid,type):
            accountid = o.account_id.id       
            moveline_id = moveid
            detail_type = type           

            sql = '''
                    select distinct ai.date_invoice as invoice_date,ai.bill_number as bill_no,
                    ai.bill_date as bill_date,ai.name as inv_name,rs.name as partner,
                    ail.line_net as linenet,t.description as desc,ail.id,ai.move_id,
                    COALESCE(ail.freight,0) as frieght_1,COALESCE(ail.fright,0) as frieght_2,am.doc_type as doc_type,
                    ai.id as invoice_id, rs.id as partner_id                 
                    from account_invoice_line ail
                    join account_invoice ai on (ai.id = ail.invoice_id)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax t on (t.id = ailt.tax_id)                  
                    join account_move am on (am.id = ai.move_id)
                    join account_move_line aml on (aml.move_id = am.id)
                    join res_partner rs on (rs.id = ai.partner_id)
                    where aml.name = ail.name and aml.id = %s
                    and t.is_stax_report = 't'
                '''%(moveid)
            cr.execute(sql)
            for move in cr.dictfetchall():
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
                if type == 'invoice_id':
                    invoice_id = move['invoice_id']
                    return invoice_id or ''  
                if type == 'partner_id':
                    partner_id = move['partner_id']                    
                    return partner_id or ''
                
        
        def get_tot_closing_bal(o):
       
            date_to = o.date_to
            accountid = o.account_id.id
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(cr,uid,accountid)
            code = act_abj.code         
            
                    
            # sum(ail.line_net*(at.amount/100))
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
            #     and ai.date_invoice <= '%s'
            #     group by ail.id 
            #     order by ail.id)a
            # '''%(accountid,accountid,date_to)
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
            #     and ai.date_invoice <= '%s'
            #     group by ail.id 
            #     order by ail.id)a
            # '''%(accountid,accountid,date_to)
            #===================================================================
            
#===============================================================================
# #             if accountid == '402':
# #                 sql = '''
# #                     select COALESCE(sum(a.debit),0) as taxamount from(
# #                     select sum(aml.debit) as debit,aml.id
# #                     from account_move_line aml
# #                     inner join account_move am on (am.id=aml.move_id)
# #                     join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
# #                     join account_invoice_line ail on (ail.invoice_id = ai.id)
# #                     join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
# #                     join account_tax at on (at.id=ailt.tax_id)
# #                     where at.description ~'STax' and at.amount>0 and aml.account_id in (402)
# #                     and am.date <= '%s'
# #                     group by aml.id 
# #                     order by aml.id)a
# #                 '''%(date_to)
# #             for move in cr.dictfetchall():
# #                     total = move['debit']
# #                     return total or 0.00
#===============================================================================
            
            #===================================================================
            # if code == '0000119905':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (402)
            #         and am.date <= '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #     '''%(date_to)
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #             total = move['debit']
            #             return total or 0.00
            #     
            # 
            # elif code == '0000119925':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (506)
            #         and am.date <= '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #     '''%(date_to)
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #             total = move['debit']
            #             return total or 0.00
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
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (507)
            #         and am.date <= '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #     '''%(date_to)
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         total = move['debit']
            #         return total or 0.00    
            #     
            # else: 
            #===================================================================
                
            sql = '''
                    select COALESCE(sum(a.debit),0) as debit from(
                    select sum(aml.debit) as debit,aml.id
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                    join account_invoice_line ail on (ail.invoice_id = ai.id)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax at on (at.id=ailt.tax_id)
                    where at.amount>0 and aml.account_id = %s
                    and am.date <= '%s' and is_stax_report = 't'
                    group by aml.id 
                    order by aml.id)a
                '''%(accountid,date_to)            
            cr.execute(sql)
            for move in cr.dictfetchall():
                total = move['debit']
                return total or 0.00
            
        
        #=======================================================================
        # def get_tax_amnt(o,line):
        #     lineid = line                       
        #     accountid = o.account_id.id            
        #                 
        #     #===================================================================
        #     # sql = '''
        #     #     select COALESCE(aml.debit,0) as debit from account_invoice_line ail
        #     #     join account_invoice ai on (ai.id = ail.invoice_id)
        #     #     join account_move am on (am.id = ai.move_id)
        #     #     join account_move_line aml on (aml.move_id = am.id and aml.account_id=%s)
        #     #     where ail.id = %s
        #     # '''%(accountid,lineid)
        #     #===================================================================
        #     #===================================================================
        #     # 
        #     #     sql = '''
        #     #         select sum(aml.debit) as debit 
        #     #         from account_move_line aml
        #     #         inner join account_move am on (am.id=aml.move_id)
        #     #         inner join account_account aa on (aa.id=aml.account_id and aa.id=%s)
        #     #         join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #     #         where aml.debit>0 and am.state in ('posted') 
        #     #         where ail.id = %s
        #     #     '''%(accountid,lineid)
        #     #===================================================================
        #     
        #     if accountid == 506:  
        #         sql = '''
        #                 select COALESCE((select COALESCE(aml.debit,0) as debit 
        #                 from account_move_line aml
        #                 inner join account_move am on (am.id=aml.move_id)
        #                 inner join account_account aa on (aa.id=aml.account_id and aa.id in (402,506))
        #                 join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #                 where aml.debit>0 and am.state in ('posted') 
        #                 and aml.id = %s),0)
        #              '''%(accountid,lineid)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():
        #             if move['debit']:
        #                  debit = move['debit']                            
        #                  return debit or 0.00
        #             else:
        #                  return 0.00
        #              
        #     if accountid == 507:  
        #         sql = '''
        #                 select COALESCE((select COALESCE(aml.debit,0) as debit 
        #                 from account_move_line aml
        #                 inner join account_move am on (am.id=aml.move_id)
        #                 inner join account_account aa on (aa.id=aml.account_id and aa.id in (402,507))
        #                 join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #                 where aml.debit>0 and am.state in ('posted') 
        #                 and aml.id = %s),0)
        #              '''%(accountid,lineid)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():
        #             if move['debit']:
        #                  debit = move['debit']                            
        #                  return debit or 0.00
        #             else:
        #                  return 0.00
        #              
        #     else:
        #         sql = '''
        #                 select COALESCE((select COALESCE(aml.debit,0) as debit 
        #                 from account_move_line aml
        #                 inner join account_move am on (am.id=aml.move_id)
        #                 inner join account_account aa on (aa.id=aml.account_id and aa.id = %s)
        #                 join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #                 where aml.debit>0 and am.state in ('posted') 
        #                 and aml.id = %s),0)
        #              '''%(accountid,lineid)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():
        #             if move['debit']:
        #                  debit = move['debit']                            
        #                  return debit or 0.00
        #             else:
        #                  return 0.00     
        #=======================================================================
        
        
        def get_debit_balance(o):
            date_from = o.date_from
            date_to = o.date_to
            account_id = o.account_id.id
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(cr,uid,account_id)
            code = act_abj.code
            openbalance = 0.0
                           
            
        #=======================================================================
        #     if code == '0000119905':
        #         sql = '''
        #             select sum(aml.credit) as debit 
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             inner join account_account aa on (aa.id=aml.account_id and aa.id in (402))
        #             join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #             where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
        #             '''%(date_from,date_to)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():
        #             if move['debit']:
        #                 openbalance += move['debit']                        
        #         return openbalance or 0.00
        #     
        #     elif code == '0000119925':
        #          
        #         sql = '''
        #             select sum(aml.credit) as debit 
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             inner join account_account aa on (aa.id=aml.account_id and aa.id in (506))
        #             join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #             where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
        #             '''%(date_from,date_to)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():
        #             if move['debit']:
        #                 openbalance += move['debit']                        
        #         return openbalance or 0.00
        # 
        #     elif code == '0000119926':
        #          
        #         sql = '''
        #             select sum(aml.credit) as debit 
        #             from account_move_line aml
        #             inner join account_move am on (am.id=aml.move_id)
        #             inner join account_account aa on (aa.id=aml.account_id and aa.id in (507))
        #             join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
        #             where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
        #             '''%(date_from,date_to)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():
        #             if move['debit']:
        #                 openbalance += move['debit']                        
        #         return openbalance or 0.00
        #     
        #     else:
        #=======================================================================
                
                
            #===================================================================
            # sql = '''
            #         select sum(aml.credit) as debit 
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         inner join account_account aa on (aa.id=aml.account_id and aa.id = %s)
            #         join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
            #         where aml.debit>0 and am.state in ('posted') and am.date between '%s' and '%s'
            #         '''%(account_id,date_from,date_to)
            #===================================================================
            sql = '''
                    select sum(aml.credit) as debit 
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    inner join account_account aa on (aa.id=aml.account_id and aa.id = %s)
                    join account_invoice i on (i.move_id=am.id and i.type = 'in_invoice')
                    join account_invoice_line ail on (ail.invoice_id = i.id and aml.name = ail.name)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax at on (at.id=ailt.tax_id)
                    where aml.debit>0 and am.state in ('posted') and at.amount>0 
                    and at.is_stax_report = 't'
                    and am.date between '%s' and '%s'
                    '''%(account_id,date_from,date_to)
            cr.execute(sql)
            for move in cr.dictfetchall():
                if move['debit']:
                    openbalance += move['debit']                        
                return openbalance or 0.00
        
        def get_opening_balance(sr):
            date_from = sr.date_from
            account_id = sr.account_id.id
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(cr,uid,account_id)
            code = act_abj.code
            openbalance = 0.0
            
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
            #     '''%(account_id.id,date_from)
            #===================================================================
            #===================================================================
            # sql = '''
            #     select COALESCE(sum(a.debit),0) as taxamount from( 
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
            #     '''%(account_id.id,account_id.id,date_from)
            #===================================================================
            
            #===================================================================
            # if code == '0000119905':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as taxamount from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (402)
            #         and am.date < '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #         '''%(date_from)
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         if move['taxamount']:
            #             openbalance += move['taxamount']                    
            #             return openbalance or 0.00
            # 
            # elif code == '0000119925':            
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as taxamount from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (506)
            #         and am.date < '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #         '''%(date_from)
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         if move['taxamount']:
            #             openbalance += move['taxamount']                    
            #             return openbalance or 0.00
            #         
            # elif code == '0000119926':            
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as taxamount from(
            #         select sum(aml.debit) as debit,aml.id
            #         from account_move_line aml
            #         inner join account_move am on (am.id=aml.move_id)
            #         join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
            #         join account_invoice_line ail on (ail.invoice_id = ai.id)
            #         join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         join account_tax at on (at.id=ailt.tax_id)
            #         where at.description ~'STax' and at.amount>0 and aml.account_id in (507)
            #         and am.date < '%s'
            #         group by aml.id 
            #         order by aml.id)a
            #         '''%(date_from)
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         if move['taxamount']:
            #             openbalance += move['taxamount']                    
            #             return openbalance or 0.00            
            # 
            # else:
            #===================================================================
                
            sql = '''
                    select COALESCE(sum(a.debit),0) as taxamount from(
                    select sum(aml.debit) as debit,aml.id
                    from account_move_line aml
                    inner join account_move am on (am.id=aml.move_id)
                    join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                    join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
                    join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    join account_tax at on (at.id=ailt.tax_id)
                    where at.amount>0 and aml.account_id = %s
                    and am.date < '%s' and at.is_stax_report = 't'
                    group by aml.id 
                    order by aml.id)a
                    '''%(account_id,date_from)
            cr.execute(sql)
            for move in cr.dictfetchall():
                if move['taxamount']:
                    openbalance += move['taxamount']                    
                return openbalance or 0.00
        
        
        def get_total_service_tax(o):
            date_from = o.date_from
            date_to = o.date_to
            account_id = o.account_id.id
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(cr,uid,account_id)
            code = act_abj.code
            total = 0.00            
            balance = 0.0
            
            
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
            #     and ai.date_invoice between '%s' and '%s'
            #     group by ail.id 
            #     order by ail.id)a
            #     '''%(account_id.id,date_from,date_to)
            #===================================================================
            
            
            #===================================================================
            # if code == '0000119905':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from( 
            #         select sum(aml.debit) as debit,ail.id
            #         from account_invoice_line ail
            #         join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #         JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id in (402))
            #         join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id in (402))
            #         where at.description ~'STax' and at.amount>0
            #         and ai.date_invoice between '%s' and '%s'
            #         group by ail.id 
            #         order by ail.id)a
            #         '''%(date_from,date_to)
            #     
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         total += move['debit']               
            #     return round(total,0) or 0.00
            #     
            #     
            # 
            # elif code == '0000119925':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from( 
            #         select sum(aml.debit) as debit,ail.id
            #         from account_invoice_line ail
            #         join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #         JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id in (506))
            #         join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id in (506))
            #         where at.description ~'STax' and at.amount>0
            #         and ai.date_invoice between '%s' and '%s'
            #         group by ail.id 
            #         order by ail.id)a
            #         '''%(date_from,date_to)
            #     
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         total += move['debit']               
            #     return round(total,0) or 0.00
            # 
            # elif code == '0000119926':
            #     sql = '''
            #         select COALESCE(sum(a.debit),0) as debit from( 
            #         select sum(aml.debit) as debit,ail.id
            #         from account_invoice_line ail
            #         join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
            #         JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
            #         Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id in (507))
            #         join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id in (507))
            #         where at.description ~'STax' and at.amount>0
            #         and ai.date_invoice between '%s' and '%s'
            #         group by ail.id 
            #         order by ail.id)a
            #         '''%(date_from,date_to)
            #     
            #     cr.execute(sql)
            #     for move in cr.dictfetchall():
            #         total += move['debit']               
            #     return round(total,0) or 0.00
            # else:
            #===================================================================
                
            sql = '''
                    select COALESCE(sum(a.debit),0) as debit from( 
                    select sum(aml.debit) as debit,ail.id
                    from account_invoice_line ail
                    join account_invoice ai on (ai.id=ail.invoice_id and ai.type = 'in_invoice')
                    JOIN account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                    Join account_tax at on (at.id=ailt.tax_id and at.gl_account_id = %s)
                    join account_move_line aml on (aml.move_id=ai.move_id and aml.account_id = %s)
                    where at.amount>0
                    and ai.date_invoice between '%s' and '%s'
                    group by ail.id 
                    order by ail.id)a
                    '''%(account_id,account_id,date_from,date_to)                
            cr.execute(sql)
            for move in cr.dictfetchall():
                total += move['debit']          
            return round(total,0) or 0.00
        
        def get_invoice(o):
            res = {}
            date_from = o.date_from
            date_to = o.date_to
            account_id = o.account_id.id            
            account_obj = self.pool.get('account.account')
            act_abj = account_obj.browse(cr,uid,account_id)
            code = act_abj.code
            invoice_obj = self.pool.get('account.move.line')
            
            
           
            sql = '''
                        select aml.id
                        from account_move_line aml
                        inner join account_move am on (am.id=aml.move_id)
                        join account_invoice ai on (ai.move_id=am.id and ai.type = 'in_invoice')
                        join account_invoice_line ail on (ail.invoice_id = ai.id and aml.name = ail.name)
                        join account_invoice_line_tax ailt on (ailt.invoice_line_id=ail.id)
                        join account_tax at on (at.id=ailt.tax_id)
                        where at.amount>0
                        and at.is_stax_report = 't'                                                   
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
            if account_id:
                    str = "  and aml.account_id = %s "%(account_id)
                    sql = sql+str
            sql=sql+" order by aml.id"                                       
            cr.execute(sql)
            invoice_ids = [r[0] for r in cr.fetchall()]
            return invoice_obj.browse(cr,uid,invoice_ids)        
           
        
        cr.execute('delete from tpt_service_tax')
        sr_obj = self.pool.get('tpt.service.tax')
        sr = self.browse(cr, uid, ids[0])
        sr_line = []
        openbalance=get_opening_balance(sr)
        debit_total=get_debit_balance(sr)
        temp_taxamt = 0.00
        for line in get_invoice(sr):
            
                sr_line.append((0,0,{
                    'date': get_invoice_details(sr,line.id,'invdate'), #line.move_id.invoice_id.date_invoice or False,
                    'bill_no': get_invoice_details(sr,line.id,'billno'), #line.invoice_id.bill_number or False,
                    'bill_date': get_invoice_details(sr,line.id,'billdate'), #line.invoice_id.bill_date or False,invname
                    'number': get_invoice_details(sr,line.id,'invname'), #line.invoice_id.name or False, 
                    'invoice_id': get_invoice_details(sr,line.id,'invoice_id') or False, #line.invoice_id.name or False,
                    'party_name': get_invoice_details(sr,line.id,'partner') or False, #line.invoice_id.partner_id and line.invoice_id.partner_id.id or False,
                    'partner_id': get_invoice_details(sr,line.id,'partner_id') or False,
                    #'open_bal': round(openbalance+temp_taxamt,0) or 0.00,        #netamt
                    'open_bal': openbalance+temp_taxamt or 0.00,        
                    #'taxable_amount': round(get_invoice_details(sr,line.id,'netamt'),0) or 0.00, #line.line_net,
                    'taxable_amount': get_invoice_details(sr,line.id,'netamt') or 0.00,
                    'service_tax_rate': get_invoice_details(sr,line.id,'tax'), # get_tax_rate_desc(get_tax_rate_id(line.move_id)),
                    #'service_tax': line.line_net * (tax_amt/100), #Commented by YuVi on 28/07/15, for avoid roundoff issue
                    #'service_tax': round(line.line_net * (tax_amt/100),0), #Added by YuVi on 28/07/15, for avoid roundoff issue
                    'service_tax': line.debit or 0.00,#line.debit or 0.00,
                    #'total': round(openbalance+temp_taxamt+line.debit,0) or 0.00, #Added by TPT-Y
                    'total': openbalance+temp_taxamt+line.debit or 0.00,
                    #'total': openbalance+temp_taxamt+(line.line_net * (tax_amt/100)), #Commented by YuVi on 28/07/15, for avoid roundoff issue
                    #'total': round(openbalance+temp_taxamt+(line.line_net * (tax_amt/100)),0), #Added by YuVi on 28/07/15, for avoid roundoff issue
                    'debit': 0.00,
                    #'closing_bal': round(openbalance+temp_taxamt+line.debit,0) or 0.00, #Added by TPT-Y
                    'closing_bal': openbalance+temp_taxamt+line.debit or 0.00, #Added by TPT-Y
                    #'debit_1' : 0.00,
                    #'debit_2' : 0.00,
                    #'closing_bal': openbalance+temp_taxamt+(line.line_net * (tax_amt/100)), #Added by YuVi on 28/07/15, for avoid roundoff issue
                    #'closing_bal': round(openbalance+temp_taxamt+(line.line_net * (tax_amt/100)),0), #Added by YuVi on 28/07/15, for avoid roundoff issue
                }))
                temp_taxamt+=line.debit or 0.00                
            #temp_taxamt+=(line.line_net * (tax_amt/100))
            #temp_taxamt+=get_tax_amnt(sr,line.id)
        
        sr_line.append((0,0,{
             #'open_bal':openbalance+temp_taxamt,
            #'total':round(openbalance+temp_taxamt,0) or 0.00, #get_tot_closing_bal(sr),
            'total':openbalance+temp_taxamt or 0.00,
            #'total':openbalance+temp_taxamt, #Commented by YuVi on 28/07/2015, for avoid roundoff issue
            #'total':round(openbalance+temp_taxamt,0), #Added by YuVi on 28/07/2015, for avoid roundoff issue
            'debit': debit_total or 0.00,
            #'closing_bal': round((openbalance+temp_taxamt) - debit_total,0) or 0.00, #Added by YuVi on 28/07/2015, for avoid roundoff issue
            'closing_bal': (openbalance+temp_taxamt) - debit_total or 0.00,
            
        }))
        
        sr_line.append((0,0,{            
            'service_tax_rate' : 'Total',   
            'service_tax': get_total(get_invoice(sr)) or 0.00,     #get_total_service_tax(sr),
                 
            
        }))        
        
        vals = {
            'name': 'Service Tax Register Report',
            'date_from': sr.date_from,
            'date_to': sr.date_to,
            'account_id': sr.account_id.id,
            'service_line': sr_line,    
        }
        sr_id = sr_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_service_tax_register_form')
        return {
                    'name': 'Service Tax Register Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.service.tax',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': sr_id,
                }
        
        
service_tax_register()

