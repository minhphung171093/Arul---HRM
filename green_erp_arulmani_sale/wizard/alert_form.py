# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class alert_warning_form(osv.osv_memory):
    _name = "alert.warning.form"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                }

    
alert_warning_form()


class do_mgnt_confirm(osv.osv_memory):
    _name = "do.mgnt.confirm"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                'reason': fields.char('Reason', size=1024, ),
                }
    
    def action_confirm(self, cr, uid, ids, context=None): 
        audit_id = context.get('audit_id')
        do_obj = self.pool.get('stock.picking').browse(cr, uid, audit_id)
        popup_id = self.pool.get('do.mgnt.confirm').browse(cr, uid, ids[0])
        reason = popup_id.reason
        
        space_removed = reason.replace(" ", "")
        if space_removed == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the Reason!'))
        
        sql = ''' update stock_picking set reason_mgnt_confirm='%s' where id=%s
        '''%(reason,audit_id)
        cr.execute(sql) 
        
        if do_obj.doc_status == 'waiting':
                sql = '''
                    update stock_picking set flag_confirm = True, doc_status='approved' where id = %s
                    '''%(audit_id)
                cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}   
    
    
do_mgnt_confirm()

class tpt_do_adj(osv.osv_memory):
    _name = "tpt.do.adj"
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                'reason': fields.char('Reason', size=1024, ),
                }
    
    def action_confirm(self, cr, uid, ids, context=None): 
        audit_id = context.get('audit_id')
        do_obj = self.pool.get('stock.picking').browse(cr, uid, audit_id)
        popup_id = self.pool.get('do.mgnt.confirm').browse(cr, uid, ids[0])
        reason = popup_id.reason
        
        space_removed = reason.replace(" ", "")
        if space_removed == '':
            raise osv.except_osv(_('Warning!'),_('Please Provide the Reason!'))
        
        sql = ''' update stock_picking set reason_mgnt_confirm='%s' where id=%s
        '''%(reason,audit_id)
        cr.execute(sql) 
        
        if do_obj.doc_status == 'waiting':
                sql = '''
                    update stock_picking set flag_confirm = True, doc_status='approved' where id = %s
                    '''%(audit_id)
                cr.execute(sql)
        return {'type': 'ir.actions.act_window_close'}   
    
    
tpt_do_adj()