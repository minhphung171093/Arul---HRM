# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from datetime import date
import time
import datetime
import math
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from datetime import datetime, timedelta

class account_tax(osv.osv):
    _inherit = 'account.tax'
    
    def _get_tpt_tax_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            amount = line.amount
            if line.child_depend:
                amount = 0
                for child in line.child_ids:
                    amount += child.amount
            if line.amount!=amount:
                super(account_tax, self).write(cr, uid, [line.id], {'amount': amount})
            res[line.id] = amount
        return res
    
    def _get_tax(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.tax').browse(cr, uid, ids, context=context):
            result[line.parent_id.id] = True
        return result.keys()
    
    _columns = {
        'tpt_tax_amount': fields.function(_get_tpt_tax_amount, string='Amount Tax',
                                         store={
                'account.tax': (lambda self, cr, uid, ids, c={}: ids, ['child_ids','child_depend','amount'], 10),
                'account.tax': (_get_tax, ['child_ids','child_depend','amount'], 10),}, 
           states={ 'done':[('readonly', True)]}),
    }
    
    def create(self, cr, uid, vals, context=None):
        new_id = super(account_tax, self).create(cr, uid, vals, context)
        new = self.browse(cr, uid, new_id)
        if new.child_depend:
            amount = 0
            for child in new.child_ids:
                amount += child.amount
            self.write(cr, uid, [new_id],{'amount': amount})
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(account_tax, self).write(cr, uid, ids, vals, context)
        for line in self.browse(cr, uid, ids):
            if line.child_depend:
                amount = 0
                for child in line.child_ids:
                    amount += child.amount
                if line.amount!=amount:
                    super(account_tax, self).write(cr, uid, [line.id], {'amount': amount})
        return new_write
    
#     def search(self, cr, uid, args, offset=0, limit=None, order=None,
#             context=None, count=False):
#         if context is None:
#             context = {}
#  
#         if context and not context.get('tpt_tax_master', False):
#             args += [('parent_id','=',False)]
#  
#         return super(account_tax, self).search(cr, uid, args, offset, limit,
#                 order, context=context, count=count)
    
account_tax()


