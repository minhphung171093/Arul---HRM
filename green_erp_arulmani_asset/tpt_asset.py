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

class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _columns = {
              
                'product_id':fields.many2one('product.product', 'Product'),  
    }
account_asset_asset()