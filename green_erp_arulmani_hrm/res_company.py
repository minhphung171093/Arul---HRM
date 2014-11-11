# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
                'company_code': fields.char('Street', size=128),
                'reg_name': fields.char('Name', size=128),
                'reg_street': fields.char('Street', size=128),
                'reg_zip': fields.char('Zip', change_default=True, size=24),
                'reg_city': fields.char('City', size=128),
                'reg_state_id': fields.many2one("res.country.state", 'State', domain="[('country_id', '=', country_id)]"),
                'reg_country_id': fields.many2one('res.country', 'Country'),
                }    
res_company()   