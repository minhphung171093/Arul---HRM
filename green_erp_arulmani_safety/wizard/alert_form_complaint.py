# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
# WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class alert_form_complaint(osv.osv_memory):
    _name = "alert.form.complaint"
    _columns = {    
#                 'type': fields.selection(WARNING_TYPES, string='Type', readonly=True),
                'title': fields.char(string="Title", size=100, readonly=True),
                'message': fields.text(string="Message ", readonly=True),    
                }
#     _req_name = 'title'

#     def _get_view_id(self, cr, uid):
#         """Get the view id
#         @return: view id, or False if no view found
#         """
#         res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
#             'green_erp_arulmani_safety', 'approve_or_reject_complaint_form_view')
#         return res and res[1] or False
#     
#     def message(self, cr, uid, id, context):
#         message = self.browse(cr, uid, id)
#         message_type = [t[1]for t in WARNING_TYPES if message.type == t[0]][0]
#         print '%s: %s' % (_(message_type), _(message.title))
#         res = {
#             'name': '%s: %s' % (_(message_type), _(message.title)),
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': self._get_view_id(cr, uid),
#             'res_model': 'alert.form.complaint',
#             'domain': [],
#             'context': context,
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'res_id': message.id
#         }
#         return res
#     
#     def warning(self, cr, uid, title, message, context=None):
#         id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'warning'})
#         res = self.message(cr, uid, id, context)
#         return res
    
    def approve_complaint(self, cr, uid, ids, context=None):
        complaint_ids = context.get('active_ids')
        self.pool.get('complaint.register').bt_approve(cr, uid, complaint_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def reject_complaint(self, cr, uid, ids, context=None):
        complaint_ids = context.get('active_ids')
        self.pool.get('complaint.register').bt_reject(cr, uid, complaint_ids)
        return {'type': 'ir.actions.act_window_close'}
    
alert_form_complaint()

class hod_alert_form_complaint(osv.osv_memory):
    _name = "hod.alert.form.complaint"
    _columns = {    
                'title': fields.char(string="Title", size=100, readonly=True),
                'message': fields.text(string="Message ", readonly=True), 
                'hod_reject_reason': fields.text(string="Reason For Rejection"), 
                'create_noti': fields.boolean('Create Notification Entry?'),   
                }
    
    def approve_complaint(self, cr, uid, ids, context=None):
        wizard = self.browse(cr,uid,ids[0])
        notif = wizard.create_noti
        complaint_ids = context.get('active_ids')
        self.pool.get('complaint.register').bt_hod_approve(cr, uid, complaint_ids,notif)
        return {'type': 'ir.actions.act_window_close'}
    
    def reject_complaint(self, cr, uid, ids, context=None):
        wizard = self.browse(cr,uid,ids[0])
        hod_reject_reason = wizard.hod_reject_reason
        complaint_ids = context.get('active_ids')
        self.pool.get('complaint.register').bt_hod_reject(cr, uid, complaint_ids,hod_reject_reason)
        return {'type': 'ir.actions.act_window_close'}
    
hod_alert_form_complaint()