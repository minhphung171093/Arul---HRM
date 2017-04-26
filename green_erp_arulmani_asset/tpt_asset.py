# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#from datetime import datetime
#import datetime
#from datetime import date
from datetime import datetime, date, timedelta #TPT
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class asset_asset(osv.osv):
    _inherit = 'asset.asset'
    _columns = {
                'code':fields.char('Code'), 
                'product_id':fields.many2one('product.product', 'Product'),  
                'category_id':fields.many2one('account.asset.category', 'Asset Category'),
                'ac_code':fields.float('Asset Category Code'),
                'am_code':fields.float('Asset Master Code'), 
    }
    _defaults = {
                 'asset_number' : '/',
                 'am_code' : 0
                 }
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
        bp = self.pool.get('asset.asset').browse(cr, uid, ids[0])
        reads = self.read(cr, uid, ids, ['name','asset_number'], context=context)

        for record in reads:    
            code = record['asset_number']
            name = record['name']
            name = code + ' - ' + name 
            res.append((record['id'], name))
        return res
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if name:
            ids = self.search(cr, user, ['|',('name','ilike',name),('asset_number','ilike',name)]+args, context=context, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    def create(self, cr, uid, vals,context=None):
        asset_categ = self.pool.get('account.asset.category')
        asset_number = asset_categ.browse(cr, uid, vals['category_id'])
        print asset_number.code
        category_code = asset_number.code
        sql= '''
             select case when max(am_code) is null then 01 else max(am_code)+ 1 end as am_code from 
             asset_asset aa join account_asset_category ac on aa.category_id=ac.id where ac.code='%s'                 
            '''%(category_code)
        cr.execute(sql) 
        am_code = cr.dictfetchone()['am_code']
        asset_number = category_code +'-' +'0'+"%g"% am_code
        vals = {'am_code': am_code,
                'asset_number': asset_number,
                'name': vals['name'],
                'product_id':vals['product_id'],
                'category_id':vals['category_id']
                }   
        new_id = super(asset_asset, self).create(cr, uid, vals, context=context)
        return new_id
         
     # commented on P.vinothkumar on 26/08/2016 for normal sequence    
#     def create(self, cr, uid, vals,context=None):
#        
#         sql = '''
#         select code from account_fiscalyear where '%s' between date_start and date_stop
#         '''%(time.strftime('%Y-%m-%d'))
#         cr.execute(sql)
#         fiscalyear = cr.dictfetchone()
#         if not fiscalyear:
#             raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
#         else:
#             sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.asset.master.sequence') 
# 
#         new_id = super(asset_asset, self).create(cr, uid, vals, context)
#         
#         asset_number = self.browse(cr, uid, new_id)
#         category = asset_number.category_id.code
#         self.pool.get('asset.asset').write(cr, uid, asset_number.id, {                                                                              
#            'asset_number' : category + '-' + sequence }) 
# 
#         return new_id 
    def _check_code_id(self, cr, uid, ids, context=None):
        for asset_master in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from asset_asset where id != %s and lower(name) = lower('%s') and product_id = '%s' and category_id = %s
            '''%(asset_master.id,asset_master.name,asset_master.product_id.id,asset_master.category_id.id)
            cr.execute(sql)
            asset_master_ids = [row[0] for row in cr.fetchall()]
            if asset_master_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['name','product_id','category_id']),
    ]  
    
asset_asset()

#Just for 
class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _columns = {
              
#                 'product_id':fields.many2one('product.product', 'Product'),    
#                 'grn_id':fields.many2one('stock.picking', 'GRN'),       
#                 'caps_date':fields.date('Capitalization Date',),  
#                 'desc':fields.text('Description'), 
                'product_id':fields.many2one('product.product', 'Product'),    
                'grn_id':fields.many2one('stock.picking', 'GRN No'),
                'category_id':fields.many2one('account.asset.category', 'Category'),
                'grn_date' : fields.date('GRN Date'),      
                'caps_date':fields.date('Capitalization Date'),  
                'desc':fields.text('Description'),
                'ac_code':fields.float('Asset Category Code'),
                'am_code':fields.float('Asset Master Code'),
                'ar_code':fields.float('Asset Registry Code'),
                'register_code':fields.char('Code'),   
   }
    _defaults = {
                 'register_code' : '/',
                 'ar_code' : 000
                 }
    
account_asset_asset()

class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'
   
    _columns = {
        'code': fields.char('Code', size=1024, required=True)     
    }
    _defaults = {
                 'code' : '/'
                 }
    
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
        bp = self.pool.get('account.asset.category').browse(cr, uid, ids[0])
        reads = self.read(cr, uid, ids, ['name','code'], context=context)

        for record in reads:    
            code = record['code']
            name = record['name']
            name = code + ' - ' + name 
            res.append((record['id'], name))
        return res
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if name:
            ids = self.search(cr, user, ['|',('name','ilike',name),('code','ilike',name)]+args, context=context, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)  
    
    def create(self, cr, uid, vals, context=None):
        sql = '''
        select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        else:
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.asset.category.sequence')
            vals['code'] =  sequence
            
        new_id = super(account_asset_category, self).create(cr, uid, vals, context)
        return new_id    
                
account_asset_category()

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def write(self, cr, uid, ids, vals, context=None):
        #Ref tpt_accounting Line No:506
        new_write = super(stock_picking, self).write(cr, 1,ids, vals, context)
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        asset_obj = self.pool.get('asset.asset')
        asset_reg_obj = self.pool.get('account.asset.asset')
        #
        for grn in self.browse(cr,uid,ids):
            if 'state' in vals and grn.type == 'in' and grn.state=='done':
                for grn_line in grn.move_lines:
                    if grn_line.product_id.cate_name=='assets':
                        asset_ids = asset_obj.search(cr, uid, [('product_id', '=', grn_line.product_id.id)])
                        asset_id = asset_obj.browse(cr, uid, asset_ids[0], context=context)
                        # Added by P.vinothkumar on 27/08/2016 for generate register code
                        asset_categ = self.pool.get('account.asset.category')
                        asset_category = asset_categ.browse(cr, uid, asset_id.category_id.id)
                        asset_master = asset_obj.browse(cr, uid,asset_id.id)
                        category_code = asset_category.code
                        master_code = asset_master.asset_number
                        sql= '''
                                 select case when max(aa.am_code) is null then 01 else max(aa.am_code)+ 1 end as am_code from 
                                 asset_asset aa join account_asset_category ac on aa.category_id=ac.id where ac.code='%s'                 
                                '''%(category_code)
                        cr.execute(sql) 
                        am_code = cr.dictfetchone()['am_code'] 
                        sql='''
                                 select case when max(asset.ar_code) is null then 01 else max(asset.ar_code) + 1 end as ar_code from 
                                 asset_asset am 
                                 inner join account_asset_category ac on am.category_id=ac.id 
                                 inner join account_asset_asset asset on asset.asset_id=am.id
                                 where ac.code='%s' and am.asset_number='%s' 
                                '''%(category_code,master_code)
                        cr.execute(sql)
                        ar_code = cr.dictfetchone()['ar_code'] 
                          # TPT-END      
                        for asset_reg in range(int(grn_line.product_qty)):
                            register_code = category_code +'-' +'0'+"%g"% am_code +'-' +'00'+"%g"% (ar_code) # added on 27/08/2016
                            asset_reg_obj.create(cr, uid, {
                               'product_id': grn_line.product_id and grn_line.product_id.id or False,
                               'partner_id': grn.partner_id.id or False,
                               'register_code':register_code,
                               'purchase_date': grn.date or False, 
                               'grn_id': grn.id or False, # Added by P.vinothkumar on 23/08/2016
                               'state': 'draft',
                               'purchase_value': 1 * grn_line.price_unit or 0,
                               'asset_id': asset_id.id or False,
                               'category_id': asset_id.category_id and asset_id.category_id.id or False,
                               'method': 'linear' or '',
                               })
                            ar_code = ar_code + 1 
                         
        return True
            

stock_picking()   
    
    
class tpt_asset_depreciation(osv.osv):
    _name = 'tpt.asset.depreciation'
    _columns = {
        'name': fields.char('Name'),
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
        'depreciation_line': fields.one2many('tpt.asset.depreciation.line', 'depreciation_id', 'Line'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True),
        
    }
    _defaults = {
        'name': 'Asset Depreciation Posting',
        'state': 'draft',
    }
    def _check_state(self, cr, uid, ids, context=None):
        for asset in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_asset_depreciation where id != %s and state = 'draft'
            '''%(asset.id)
            cr.execute(sql)
            asset_ids = [row[0] for row in cr.fetchall()]
            if asset_ids:  
                raise osv.except_osv(_('Warning!'),_('Can not create more than one record in this window!'))
        return True
    
    _constraints = [
        (_check_state, 'Identical Data', ['state']),
    ] 
    def bt_load(self, cr, uid, ids,context=None):
        if context is None:
            context={}
        vals = {}
        if ids:
            cr.execute(''' delete from tpt_asset_depreciation_line where depreciation_id in %s ''',(tuple(ids),))
        depreciation_line = []
        for asset in self.browse(cr, uid, ids):
            sql = '''
            select dp.id as aaset_depreciation_id, ar.id as asset_reg_id,ar.register_code,am.category_id as category_id, ar.purchase_value, ar.caps_date, dp.depreciation_date, dp.amount from account_asset_depreciation_line dp
            inner join account_asset_asset ar on dp.asset_id=ar.id
            inner join asset_asset am on ar.asset_id=am.id
            where ar.state='open' and dp.move_check='f' 
            '''
            #cr.execute(sql)
            if asset.date_from and asset.date_to:
                sql += " and dp.depreciation_date between '%s' and '%s' "%(asset.date_from, asset.date_to)
            if asset.date_from and not asset.date_to:
                sql += " and dp.depreciation_date >= '%s' "%asset.date_from
            if not asset.date_from and asset.date_to:
                sql += " and dp.depreciation_date <= '%s' "%asset.date_to
            cr.execute(sql)
            for line in cr.dictfetchall():
                depreciation_line.append((0,0,{
                    'aaset_depreciation_id': line['aaset_depreciation_id'] or False,
                    'asset_id': line['asset_reg_id'] or False,
                    'category_id': line['category_id'] or False,
                    'depreciation_date': line['depreciation_date'] or False,
                    'caps_date': line['caps_date'] or False,
                    'gross_value': line['purchase_value'] or 0.0,
                    'amount': line['amount'] or 0.0,
                    'register_code': line['register_code'] or 0.0 # added this line on 29/08/2016
                    
                }))
        
            vals = {'depreciation_line':depreciation_line}
        return self.write(cr, uid, ids,vals)
    
    def bt_confirm(self, cr, uid, ids, context=None):
        can_close = False
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        #currency_obj = self.pool.get('res.currency')
        # Added by vinothkumar on 27/08/2016 for post all assets
        depreciation_id = []
        for depreciation_id in self.browse(cr, uid, ids, context=context):
            line_ids = self.pool.get('tpt.asset.depreciation.line').search(cr, uid,[('depreciation_id','=',depreciation_id.id),('move_check','=',False),
                                                                                 ('flag','=',True)])
            if line_ids: 
                for line in self.pool.get('tpt.asset.depreciation.line').browse(cr,uid,line_ids):
       #TPT VINOTH end#
                    depreciation_date = context.get('depreciation_date') or time.strftime('%Y-%m-%d')
                    dp_date = line.depreciation_date
                    current_date =  time.strftime('%Y-%m-%d')
                    if dp_date > current_date:
                        raise osv.except_osv(_('Warning!'),_('Asset Depreciation Posting not allowed for Future Date!'))
                    #
                    ctx = dict(context, account_period_prefer_normal=True)
                    period_ids = period_obj.find(cr, uid, depreciation_date, context=ctx)
                    company_currency = line.asset_id.company_id.currency_id.id
                    current_currency = line.asset_id.currency_id.id
                    context.update({'date': depreciation_date})
                    amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
                    sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
                    asset_name = line.asset_id.name
                    reference = asset_name #line.name
                    #print line.aaset_depreciation_id.id
                    move_vals = {
                        'name': asset_name,
                        'date': depreciation_date,
                        'ref': reference,
                        'period_id': period_ids and period_ids[0] or False,
                        'journal_id': line.asset_id.category_id.journal_id.id,
                        'doc_type': 'asset_dp'
                        }
                    move_id = move_obj.create(cr, uid, move_vals, context=context)
                    journal_id = line.asset_id.category_id.journal_id.id
                    partner_id = line.asset_id.partner_id.id
                    move_line_obj.create(cr, uid, {
                        'name': asset_name,
                        'ref': reference,
                        'move_id': move_id,
                        'account_id': line.asset_id.category_id.account_depreciation_id.id,
                        'debit': 0.0,
                        'credit': amount,
                        'period_id': period_ids and period_ids[0] or False,
                        'journal_id': journal_id,
                        'partner_id': partner_id,
                        'currency_id': company_currency != current_currency and  current_currency or False,
                        'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                        'date': depreciation_date,
                    })
                    move_line_obj.create(cr, uid, {
                        'name': asset_name,
                        'ref': reference,
                        'move_id': move_id,
                        'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                        'credit': 0.0,
                        'debit': amount,
                        'period_id': period_ids and period_ids[0] or False,
                        'journal_id': journal_id,
                        'partner_id': partner_id,
                        'currency_id': company_currency != current_currency and  current_currency or False,
                        'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                        'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                        'date': depreciation_date,
                        'asset_id': line.asset_id.id
                    })
                    #self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
                    # Auto posting for Depreciation by P.vinothkumar on 24/08/2016
                    auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                    if auto_ids:
                        auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                        if auto_id:
                            move_obj.button_validate(cr,uid, [move_id], context)
                    #self.write(cr, uid, line.id, {'move_check': True}, context=context)                
                   # Added by vinothkumar on 25/08/2016 for update moved assets as 'true'
                    sql = '''
                    update tpt_asset_depreciation_line set move_check='t' where id=%s
                    '''%(line.id)
                    cr.execute(sql)
                    # Added by vinothkumar on 25/08/2016 for remove posted assets in line 
                    sql = '''
                    delete from tpt_asset_depreciation_line where move_check='t'
                    '''
                    cr.execute(sql)
                    #TPT end 
                    #
                    sql = '''
                    update account_asset_depreciation_line set move_check='t', move_id=%s where id=%s
                    '''%(move_id, line.aaset_depreciation_id.id)
                    cr.execute(sql)
                    #
                    created_move_ids.append(move_id)
                    asset_ids.append(line.asset_id.id)
            # we re-evaluate the assets to determine whether we can close them
        for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
            if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                asset.write({'state': 'close'})
        return created_move_ids
    
    # Added by P.vinothkumar on 27/08/2016 for select all depreciation lines
    def bt_select(self, cr, uid, ids,context=None):
            if context is None:
                context={}
            vals = {}
            if ids:
                cr.execute(''' update tpt_asset_depreciation_line set flag='t' ''')
            return self.write(cr, uid, ids,vals)
    
tpt_asset_depreciation()   

class tpt_asset_depreciation_line(osv.osv):
    _name = 'tpt.asset.depreciation.line'
    _columns = {
        'aaset_depreciation_id': fields.many2one('account.asset.depreciation.line', 'Asset Depreciation'),
        'asset_id': fields.many2one('account.asset.asset', 'Asset Name'),# Modified field name on 29/08/2016
        'category_id': fields.many2one('account.asset.category', 'Asset Category'),
        'gross_value': fields.float('Gross Value', ),
        'caps_date': fields.date('Capitalization Date'),
        'depreciation_date': fields.date('Depreciation Date'),
        'amount': fields.float('Depreciation Amount'),
        'move_check': fields.boolean('Posted'),  
        'depreciation_id': fields.many2one('tpt.asset.depreciation', 'Asset Depreciation', ondelete='cascade'),
        'flag':fields.boolean('Select'),  # added field on 27/08/2016 
        'register_code' :fields.char('Asset Reg.No'),  # added field on 29/08/2016      
    }
    
    
    
    def create_move(self, cr, uid, ids, context=None):
        can_close = False
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            depreciation_date = context.get('depreciation_date') or time.strftime('%Y-%m-%d')
            #
            dp_date = line.depreciation_date
            current_date =  time.strftime('%Y-%m-%d')
            if dp_date > current_date:
                raise osv.except_osv(_('Warning!'),_('Asset Depreciation Posting not allowed for Future Date!'))
            #
            ctx = dict(context, account_period_prefer_normal=True)
            period_ids = period_obj.find(cr, uid, depreciation_date, context=ctx)
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
            asset_name = line.asset_id.name
            reference = asset_name #line.name
            #print line.aaset_depreciation_id.id
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                'doc_type': 'asset_dp'
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': line.asset_id.id
            })
            #self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            # Auto posting for Depreciation by P.vinothkumar on 24/08/2016
            auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
            if auto_ids:
                auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                if auto_id:
                    move_obj.button_validate(cr,uid, [move_id], context)
            self.write(cr, uid, line.id, {'move_check': True}, context=context)
            # Added by vinothkumar on 27/08/2016 for update moved assets as 'true' 
            sql = '''
                    update account_asset_depreciation_line set move_check='t' where id=%s
                    '''%(line.id)
            cr.execute(sql)
            # TPT end
            #
            sql = '''
            update account_asset_depreciation_line set move_check='t', move_id=%s where id=%s
            '''%(move_id, line.aaset_depreciation_id.id)
            cr.execute(sql)
            #
            created_move_ids.append(move_id)
            asset_ids.append(line.asset_id.id)
        # we re-evaluate the assets to determine whether we can close them
        for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
            if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                asset.write({'state': 'close'})
        return created_move_ids
    
tpt_asset_depreciation_line()