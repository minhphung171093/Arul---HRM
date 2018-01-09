# -*- coding: utf-8 -*-
import calendar
from datetime import datetime
import datetime
import time

from global_utility import tpt_shared_component
from openerp import SUPERUSER_ID, netsvc, tools
import openerp.addons.decimal_precision as dp
from openerp.osv import osv, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from openerp.tools.translate import _


class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        invoice_line_vals = super(stock_picking,self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id,invoice_vals, context)
        if picking.type=='in':
            invoice_line_vals.update({
                'tpt_grn_id': picking.id,
                'tpt_grn_line_id': move_line and move_line.id or False,
            })
        return invoice_line_vals

stock_picking()