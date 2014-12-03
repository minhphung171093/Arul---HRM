# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
WARNING_TYPES = [('warning','Warning'),('info','Information'),('error','Error')]
class alert_form(osv.osv_memory):
    _name = "alert.form"
    _columns = {    
                'type': fields.selection(WARNING_TYPES, string='Type', readonly=True),
                'title': fields.char(string="Title", size=100, readonly=True),
                'message': fields.text(string="Message ", readonly=True),    
                }
    _req_name = 'title'

    def _get_view_id(self, cr, uid):
        """Get the view id
        @return: view id, or False if no view found
        """
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
            'green_erp_arulmani_hrm', 'alert_form_view')
        return res and res[1] or False
    
    def message(self, cr, uid, id, context):
        message = self.browse(cr, uid, id)
        message_type = [t[1]for t in WARNING_TYPES if message.type == t[0]][0]
        print '%s: %s' % (_(message_type), _(message.title))
        res = {
            'name': '%s: %s' % (_(message_type), _(message.title)),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self._get_view_id(cr, uid),
            'res_model': 'alert.form',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': message.id
        }
        return res
    
    def warning(self, cr, uid, title, message, context=None):
        id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'warning'})
        res = self.message(cr, uid, id, context)
        return res
    
    def info(self, cr, uid, title, message, context=None):
        id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'info'})
        res = self.message(cr, uid, id, context)
        return res
    
    def error(self, cr, uid, title, message, context=None):
        id = self.create(cr, uid, {'title': title, 'message': message, 'type': 'error'})
        res = self.message(cr, uid, id, context)
        return res
    
    def reject(self, cr, uid, ids, context=None):
        payroll_obj = self.pool.get('arul.hr.payroll.executions')
        execution_id = context.get('active_ids')[0]
        print execution_id
        line = self.pool.get('tpt.hr.payroll.approve.reject').browse(cr,uid,execution_id)
        executions_obj = self.pool.get('arul.hr.payroll.executions.details')
        payroll_ids = payroll_obj.search(cr, uid, [('year', '=', line.year), ('month', '=', line.month),('state', '=', 'confirm')])
        if not payroll_ids:
            raise osv.except_osv(_('Warning !'), _("Do not find the confirmed payroll!"))
        payroll_obj.write(cr, uid, payroll_ids, {'state':'draft'})
        executions_ids = executions_obj.search(cr, uid, [('payroll_executions_id','in',payroll_ids)])
        if not executions_ids:
            raise osv.except_osv(_('Warning !'), _("Can not confirm this payroll!"))
        else:
            executions_obj.unlink(cr, uid, executions_ids, context=context)
        self.pool.get('tpt.hr.payroll.approve.reject').write(cr, uid, [execution_id], {'state':'cancel'})
        return {'type': 'ir.actions.act_window_close'}
        
alert_form()