# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
from datetime import date
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'employee_id':fields.many2one('hr.employee','Employee'),
                }
    def mapp_check_credentials(self, cr, uid, ids, user_name, password, context=None):
        """ Override this method to plug additional authentication methods"""
        #res_obj = self.pool.get('res.users') 
        #res_user = res_obj.search(cr, uid, [('login','=',user_name)])
        res = self.search(cr, SUPERUSER_ID, [('login','=',user_name),('password','=',password)])
        if not res:
            return "False"
        else:
            return "True"
        #=======================================================================
        # try:
        #     return super(res_users, self).check_credentials(cr, uid, password)
        # except openerp.exceptions.AccessDenied:
        #     res = self.search(cr, SUPERUSER_ID, [('id', '=', uid), ('oauth_access_token', '=', password)])
        #     if not res:
        #         raise    
        #=======================================================================
res_users()


