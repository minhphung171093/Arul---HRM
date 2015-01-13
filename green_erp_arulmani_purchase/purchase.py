# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar
import openerp.addons.decimal_precision as dp


class gate_in_pass(osv.osv):
    _name = "gate.in.pass"
      
    _columns = {
        'name': fields.char('Gate In Pass No', size = 1024, readonly=True),
        'po_number': fields.char('PO Number', size = 1024),
        'supplier_id': fields.many2one('res.partner', 'Supplier', required = True),
        'po_date': fields.datetime('PO Date'),
        'gate_date_time': fields.datetime('Gate In Pass Date & Time'),
                }
    _defaults={
               'name':'/',
               'gate_date_time': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'gate.in.pass.import') or '/'
        return super(gate_in_pass, self).create(cr, uid, vals, context=context)
    
gate_in_pass()

