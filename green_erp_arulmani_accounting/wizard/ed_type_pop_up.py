# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]

class ed_type_pop_up(osv.osv_memory):
    _name = "ed.type.pop.up"
    _columns = {    
                'ed_type':fields.selection(
                        [('spare_ed_12.36', 'Spares ED value of 12.36%'),
                         ('spare_ed_aed', 'Spares ED value with AED'),
                         ('spare_ed_12.5', 'Spares ED value of 12.5%'),
                         ('raw_ed_12.36', 'Raw material ED value of 12.36%'),
                         ('raw_ed_aed', 'Raw material ED value with AED'),
                         ('raw_ed_12.5', 'Raw material ED value of 12.5%')],
                        'ED Type',required = True),
                'message': fields.text(string="Message ", readonly=True),  
                'invoice_id': fields.many2one('account.invoice','Account Invoice'), 
                }
            
    def tick_ok(self, cr, uid, ids, context=None):
        for ed_type in self.browse(cr,uid,ids):
            positing_line = []
            if ed_type.ed_type == 'spare_ed_12.36':
                credit = 0
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119904'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119904 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/2
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119901'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119901 in Account master !'))
                debit = (ed_type.invoice_id.excise_duty/2)/0.1236*0.1200
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119918'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119918 in Account master !'))
                debit = (ed_type.invoice_id.excise_duty/2)/0.1236*0.1200*2/100
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119919'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119919 in Account master !'))
                debit = (ed_type.invoice_id.excise_duty/2)/0.1236*0.1200*1/100
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119915'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119915 in Account master !'))
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': 0,
                                   'credit': credit,
                                           }))  
                
                
                
            if ed_type.ed_type == 'spare_ed_aed':
                debit_total = 0
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119915'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119915 in Account master !'))
                credit = ed_type.invoice_id.excise_duty + ed_type.invoice_id.aed
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': 0,
                                   'credit': credit or 0,
                                           }))
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119901'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119901 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/2
                debit_total += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119927'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119927 in Account master !'))
                debit = ed_type.invoice_id.aed/2
                debit_total += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119904'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119904 in Account master !'))
                balance = credit - debit_total
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': balance or 0,
                                   'credit': 0,
                                           }))
                
                
            if ed_type.ed_type == 'spare_ed_12.5':
                credit = 0
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119904'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119904 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/2
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit,
                                   'credit': 0,
                                           }))
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119901'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119901 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/2
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119915'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119915 in Account master !'))
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': 0,
                                   'credit': credit,
                                           }))
                
                
                
            if ed_type.ed_type == 'raw_ed_12.36':
                credit = 0
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119902'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119902 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/0.1236*0.1200
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119916'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119916 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/0.1236*0.1200*2/100
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119917'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119917 in Account master !'))
                debit = ed_type.invoice_id.excise_duty/0.1236*0.1200*1/100
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119915'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119915 in Account master !'))
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': 0,
                                   'credit': credit,
                                           }))
                
                
                
            if ed_type.ed_type == 'raw_ed_aed':
                credit = 0
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119902'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119902 in Account master !'))
                debit = ed_type.invoice_id.excise_duty
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119922'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119922 in Account master !'))
                debit = ed_type.invoice_id.aed
                credit += debit
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit or 0,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119915'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119915 in Account master !'))
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': 0,
                                   'credit': credit,
                                           }))
            
            
            #
            if ed_type.ed_type == 'raw_ed_12.5':
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119904'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119904 in Account master !'))
                debit = ed_type.invoice_id.excise_duty
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': debit,
                                   'credit': 0,
                                           }))
                
                account_ids = self.pool.get('account.account').search(cr, uid, [('code','in',['0000119922'])])
                if not account_ids:
                    raise osv.except_osv(_('Warning!'),_('Account is not null, please configure Account with code is 0000119922 in Account master !'))
                credit = ed_type.invoice_id.excise_duty
                positing_line.append((0,0,{
                                   'gl_account_id': account_ids[0],
                                   'gl_desc': False,    
                                   'debit': 0,
                                   'credit': credit,
                                           }))
                
            vals = {
                'invoice_id': ed_type.invoice_id.id or False,
                'ed_type': ed_type.ed_type or False,
                'supplier_id': ed_type.invoice_id.partner_id.id or False,
                'date': ed_type.invoice_id.date_invoice or False,
                'created_on': ed_type.invoice_id.created_on or False,
                'create_uid': ed_type.invoice_id.create_uid.id or False,
                'tpt_ed_invoice_positing_line': positing_line,
            }
        ed_invoice_id = self.pool.get('tpt.ed.invoice.positing').create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_ed_invoice_positing_form')
        return {
                    'name': 'ED Invoice Posting',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.ed.invoice.positing',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': ed_invoice_id,
                }                                    
        
ed_type_pop_up()