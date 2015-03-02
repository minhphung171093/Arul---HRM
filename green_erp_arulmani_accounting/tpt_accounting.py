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



class account_invoice(osv.osv):
    _inherit = "account.invoice"
     
    _columns = {
        'created_by':fields.char('Created By', size = 1024),
        'created_on': fields.date('Created On'),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order'),
        'vendor_ref': fields.char('Vendor Reference', size = 1024),
    }
     
account_invoice() 

# class account_invoice_line(osv.osv):
#     _inherit = "account.invoice.line"
#     
#     _columns = {
#         'created_by':fields.char('Created By', size = 1024),
#         'created_on': fields.date('Created On'),
#         'purchase_id': fields.many2one('purchase.order', 'Purchase Order'),
#         'vendor_ref': fields.char('Vendor Reference', size = 1024),
#     }
# account_invoice_line()

       