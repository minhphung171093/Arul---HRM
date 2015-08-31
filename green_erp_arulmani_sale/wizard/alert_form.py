# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class alert_warning_form(osv.osv_memory):
    _name = "alert.warning.form"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                }

    
alert_warning_form()


class do_mgnt_confirm(osv.osv_memory):
    _name = "do.mgnt.confirm"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                'reason': fields.char('Reason', size=1024, ),
                }
    
    def action_confirm(self, cr, uid, ids, context=None): 
        audit_id = context.get('audit_id')
        do_obj = self.pool.get('stock.picking').browse(cr, uid, audit_id)
        popup_id = self.pool.get('do.mgnt.confirm').browse(cr, uid, ids[0])
        reason = popup_id.reason
        
        space_removed = reason.replace(" ", "")
        if space_removed == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the Reason!'))
        
        sql = ''' update stock_picking set reason_mgnt_confirm='%s' where id=%s
        '''%(reason,audit_id)
        cr.execute(sql) 
        
        if do_obj.doc_status == 'waiting':
                sql = '''
                    update stock_picking set flag_confirm = True, doc_status='approved' where id = %s
                    '''%(audit_id)
                cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}   
    
    
do_mgnt_confirm()

class tpt_do_adj(osv.osv_memory):
    _name = "tpt.do.adj"
    _columns = {    
            'name': fields.char(string="Title", size=1024, readonly=True),
            'year': fields.selection([(num, str(num)) for num in range(1951, 2026)], 'Year', required = True),
            'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
                }
    _defaults = {
        'year':int(time.strftime('%Y')),
        }
    def get_pro_account_id(self,cr,uid,name,channel):
        account = False
        account_obj = self.pool.get('account.account')
        if name and channel:
            product_name = name.strip()
            dis_channel = channel.strip()
            account_ids = []
            if dis_channel in ['VVTi Domestic','VVTI Domestic']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810001')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810031')])
            if dis_channel in ['VVTi Direct Export','VVTI Direct Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810003')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810032')])
            if dis_channel in ['VVTi Indirect Export','VVTI Indirect Export']:
                if product_name in ['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810004')])
                if product_name in ['FERROUS SULPHATE','FSH','M0501010002']:
                    account_ids = account_obj.search(cr, uid, [('code','=','0000810033')])
            if account_ids:
                account = account_ids[0]
        return account 
    def cleanup_do_posting(self, cr, uid, ids, context=None):
        cb = self.browse(cr, uid, ids[0])
        sql = '''
            delete from account_move where doc_type = 'do'
            and extract(month from date)=%s and extract(year from date)=%s
        '''%(cb.month,cb.year)
        cr.execute(sql)
        
        return {'type': 'ir.actions.act_window_close'}  
    def confirm_do_adj(self, cr, uid, ids, context=None): 
        cb = self.browse(cr, uid, ids[0])
        picking_obj = self.pool.get('stock.picking')
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        sql = '''
            select id from stock_picking where type = 'out' and state = 'done' 
            and extract(month from date)=%s and extract(year from date)=%s
        '''%(cb.month,cb.year)
        cr.execute(sql)
        picking_ids = [r[0] for r in cr.fetchall()]
        if not picking_ids:
            return self.write(cr, uid, ids, {'result':'Create all DO posting Done'}) 
        for line in picking_obj.browse(cr,uid,picking_ids):
            debit = 0.0
            credit = 0.0
            journal_line = []
            dis_channel = line.sale_id and line.sale_id.distribution_channel and line.sale_id.distribution_channel.name or False
            date_period = line.date
            account = False
            asset_id = False
            sql = '''
                select id from account_period where special = False and '%s' between date_start and date_stop and special is False
             
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
             
            sql_journal = '''
            select id from account_journal where code='STJ'
            '''
            cr.execute(sql_journal)
            journal_ids = [r[0] for r in cr.fetchall()]
            journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
            for p in line.move_lines:
                if p.prodlot_id:
                    sale_id = p.sale_line_id and p.sale_line_id.order_id.id or False 
                    used_qty = p.product_qty or 0
                    if sale_id:
                        sql = '''
                                select id from tpt_batch_allotment where sale_order_id = %s and state='confirm'
                            '''%(sale_id)
                        cr.execute(sql)
                   
                        allot_ids = cr.dictfetchone()
                            
                product = self.pool.get('product.product').browse(cr, uid, p.product_id.id)
                debit += product.standard_price and product.standard_price * p.product_qty or 0    
                product_name = p.product_id.default_code 
                product_id = p.product_id.id
                
                account = p.product_id.product_cose_acc_id.id
                if not account:
                    if p.product_id.product_cose_acc_id:
                        account = p.product_id.product_cose_acc_id.id
                    else: 
                        raise osv.except_osv(_('Warning!'),_('Product Cost of Goods Sold Account is not configured! Please configured it!'))
                     
                if p.product_id.product_asset_acc_id:
                    asset_id = p.product_id.product_asset_acc_id.id
                else:
                    raise osv.except_osv(_('Warning!'),_('Product Asset Account is not configured! Please configured it!'))
            if account is False:
                if p.product_id.product_cose_acc_id:
                    account = p.product_id.product_cose_acc_id.id
                else: 
                    raise osv.except_osv(_('Warning!'),_('Product Cost of Goods Sold Account is not configured! Please configured it-2!'))
            if asset_id is False:
                asset_id = p.product_id.product_asset_acc_id.id              
            if asset_id is False:
                raise osv.except_osv(_('Warning!'),_('Asset ID is False'))
            
            journal_line.append((0,0,{
                            'name':line.name, 
                            'account_id': account,
                            'partner_id': line.partner_id and line.partner_id.id,
                            'credit':0,
                            'debit':debit,
                            'product_id':product_id,
                        }))
                 
            journal_line.append((0,0,{
                    'name':line.name, 
                    'account_id': asset_id,
                    'partner_id': line.partner_id and line.partner_id.id,
                    'credit':debit,
                    'debit':0,
                    'product_id':product_id,
                    }))
                      
            value={
                    'journal_id':journal.id,
                    'period_id':period_ids[0] ,
                    'date': date_period,
                    'line_id': journal_line,
                    'doc_type':'do',
                    'ref': line.name,
                    'do_id':line.id,
                    }
            new_jour_id = account_move_obj.create(cr,uid,value)
        #return self.write(cr, uid, ids, {'result':'Create all GRN posting Remaining'}) 
        return {'type': 'ir.actions.act_window_close'}   
    
    
tpt_do_adj()