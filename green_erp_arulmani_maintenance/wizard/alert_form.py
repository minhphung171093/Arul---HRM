# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_reject_mrr(osv.osv_memory):
    _name = "tpt.reject.mrr"
    
    _columns = {    
        'name': fields.text('Reason for Rejection'),
    }
    
    def bt_reject(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids[0])
        mrr_line_id = context.get('active_id', False)
        if mrr_line_id:
            self.pool.get('tpt.material.return.request.line').write(cr, uid, [mrr_line_id], {'state': 'rejected', 'reason_reject': this.name})
        return {'type': 'ir.actions.act_window_close'}
    
tpt_reject_mrr()

