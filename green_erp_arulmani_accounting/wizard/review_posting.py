# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class review_posting(osv.osv_memory):
    _name = "review.posting"
    _inherit = "account.move"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(review_posting, self).default_get(cr, uid, fields, context=context)
        context.update({'tpt_review_posting':True})
        if context.get('tpt_invoice',False):
            vals = self.pool.get('account.invoice').action_move_create(cr, uid, context['active_ids'], context)
            res.update(vals)
        return res
    _columns = {
        'line_id': fields.one2many('review.posting.line', 'move_id', 'Entries', states={'posted':[('readonly',True)]}),
    }
review_posting()

class review_posting_line(osv.osv_memory):
    _name = "review.posting.line"
    _inherit = "account.move.line"
    _columns = {
        'move_id': fields.many2one('review.posting', 'Review Posting', ondelete='cascade'),
    }
review_posting()