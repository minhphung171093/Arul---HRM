# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

from osv import osv, fields
import decimal_precision as dp

import math
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import re
from tools.translate import _

class account_account(osv.osv):
    _inherit = "account.account"
    _columns = {
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('code',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
account_account()

class account_account_template(osv.osv):
    _inherit = "account.account.template"
    _columns = {
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('code',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
account_account_template()

class account_tax_template(osv.osv):
    _inherit = "account.tax.template"
    _columns = {
    }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('code','=',name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
account_tax_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
