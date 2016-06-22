# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
# WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class alert_form_mo(osv.osv_memory):
    _name = "alert.form.mo"
    _columns = {    
                'title': fields.char(string="Title", size=100, readonly=True),
                'message': fields.text(string="Message ", readonly=True),    
                }

    def approve_complaint(self, cr, uid, ids, context=None):
        complaint_ids = context.get('active_ids')
        self.pool.get('tpt.maintenance.order').bt_approve(cr, uid, complaint_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def reject_complaint(self, cr, uid, ids, context=None):
        complaint_ids = context.get('active_ids')
        self.pool.get('tpt.maintenance.order').bt_reject(cr, uid, complaint_ids)
        return {'type': 'ir.actions.act_window_close'}
    
alert_form_mo()
