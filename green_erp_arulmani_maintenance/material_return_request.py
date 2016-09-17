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

from array import array
import xmlrpclib


class tpt_material_return_request(osv.osv):
    _name = "tpt.material.return.request"
    
    _columns = {
        'name':fields.char('Return Request No', size = 1024,required=True,readonly=True,states={'draft': [('readonly', False)]}),
        'date':fields.date('Return Request Date',readonly=True,states={'draft': [('readonly', False)]}),
        'maintenance_id': fields.many2one('tpt.maintenance.oder', 'Maintenance Order No',readonly=True,states={'draft': [('readonly', False)]}),
        'request_id': fields.many2one('tpt.material.request', 'Material Request No',readonly=True,states={'draft': [('readonly', False)]}),
        'issue_id': fields.many2one('tpt.material.issue', 'Issue No',readonly=True,states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department',readonly=True,states={'draft': [('readonly', False)]}),
        'section_id': fields.many2one('arul.hr.section', 'Section',readonly=True,states={'draft': [('readonly', False)]}),
        'reason':fields.text('Reason For Return',readonly=True,states={'draft': [('readonly', False)]}),
        'return_request_line': fields.one2many('tpt.material.return.request.line', 'return_request_id', 'Line',readonly=True,states={'draft': [('readonly', False)]}),
        'state':fields.selection([('draft', 'Draft'),
                                  ('confirmed', 'Confirmed'),
                                  ('approved', 'Approved'),
                                  ('rejected', 'Rejected'),
                                  ],'Status', readonly=True),
    }
    
    _defaults = {
        'name': '/',
        'state': 'draft',
    }
    
    def create(self, cr, uid, vals, context=None):
        sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        if vals.get('name','/')=='/' or not vals.get('name', False):
           sequence = self.pool.get('ir.sequence').get(cr, uid, 'material.return.request') or '/' 
           vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        return super(tpt_material_return_request, self).create(cr, uid, vals, context)
    
    def onchange_maintenance_id(self, cr, uid, ids, maintenance_id=False, context=None):
        vals = {}
        if maintenance_id:
            maintenance = self.pool.get('tpt.maintenance.oder').browse(cr, uid, maintenance_id)
            vals = {
                'department_id': maintenance.department_id and maintenance.department_id.id or False,
                'section_id': maintenance.section_id and maintenance.section_id.id or False,
            }
        return {'value': vals}
    
    def bt_confirm(self, cr, uid, ids, context=None):
        for mrr in self.browse(cr, uid, ids):
            for line in mrr.return_request_line:
                self.pool.get('tpt.material.return.request.line').write(cr, uid, [line.id], {'state': 'confirmed'})
        return self.write(cr, uid, ids, {'state': 'confirmed'})
    
tpt_material_return_request()

class tpt_material_return_request_line(osv.osv):
    _name = "tpt.material.return.request.line"
    
    _columns = {
        'return_request_id': fields.many2one('tpt.material.return.request', 'Return Request', ondelete='cascade'),
        'issue_line_id': fields.many2one('tpt.material.issue.line', 'Material Code'),
        'name':fields.related('issue_line_id', 'dec_material',string='Material Description', type='char', readonly=True),
        'requested_qty': fields.related('issue_line_id', 'product_uom_qty',string='Requested Qty',digits=(16,3), type='float', readonly=True),
        'issued_qty': fields.related('issue_line_id', 'product_isu_qty',string='Issued Qty',digits=(16,3), type='float', readonly=True),
        'return_request_qty': fields.float('Return Request Qty',digits=(16,3)),
        'return_request_no': fields.related('return_request_id', 'name',string='Return Request No', type='char', readonly=True),
        'return_request_date': fields.related('return_request_id', 'date',string='Return Request Date', type='date', readonly=True),
        'maintenance_id': fields.related('return_request_id', 'maintenance_id',string='Maintenance Order No', type='many2one', relation="tpt.maintenance.oder", readonly=True),
        'issue_id': fields.related('return_request_id', 'issue_id',string='Issue No', type='many2one', relation="tpt.material.issue", readonly=True),
        'request_id': fields.related('return_request_id', 'request_id',string='Material Request No', type='many2one', relation="tpt.material.request", readonly=True),
        'department_id': fields.related('return_request_id', 'department_id',string='Department', type='many2one', relation="hr.department", readonly=True),
        'section_id': fields.related('return_request_id', 'section_id',string='Section', type='many2one', relation="arul.hr.section", readonly=True),
        'state':fields.selection([('draft', 'Draft'),
                                  ('confirmed', 'Confirmed'),
                                  ('approved', 'Approved'),
                                  ('rejected', 'Rejected'),
                                  ],'Status', readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
    }
    
    def onchange_issue_line_id(self, cr, uid, ids, issue_line_id=False, context=None):
        vals = {}
        if issue_line_id:
            issue_line = self.pool.get('tpt.material.issue.line').browse(cr, uid, issue_line_id)
            vals = {
                'name': issue_line.dec_material,
                'requested_qty': issue_line.product_uom_qty,
                'issued_qty': issue_line.product_isu_qty,
            }
        return {'value': vals}
    
    def onchange_return_request_qty(self, cr, uid, ids, issued_qty=0, return_request_qty=0, context=None):
        vals = {}
        warning = []
        if return_request_qty > issued_qty:
            vals = {'return_request_qty': issued_qty}
            warning = {
                'title': _('Warning!'),
                'message': _('Return Request quantity should not be greater than the issued quantity.')
            }
        return {'value': vals, 'warning': warning}
    
tpt_material_return_request_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
