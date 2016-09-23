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
    
    def bt_approve(self, cr, uid, ids, context=None):
        for mrr in self.browse(cr, uid, ids):
            for line in mrr.return_request_line:
                self.pool.get('tpt.material.return.request.line').write(cr, uid, [line.id], {'state': 'approved'})
        return self.write(cr, uid, ids, {'state': 'approved'})
    
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
                                  ('accepted', 'Accepted'),
                                  ('rejected', 'Rejected'),
                                  ],'Status', readonly=True),
        'reason_reject': fields.text('Reason for Rejection'),
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
    
    def bt_accept(self, cr, uid, ids, context=None):
        price = 0.0
        product_price = 0.0
        tpt_cost = 0
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        journal_line = []
        source_location_id = False
        move_obj = self.pool.get('stock.move')
                
        
        for line in self.browse(cr, uid, ids):
            location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
            if location_ids:
                source_location_id = location_ids[0]
            
            onhand_qty = 0.0
            dest_location_id = False
            locat_ids = []
            parent_ids = []
            cate_name = line.issue_line_id.product_id.categ_id and line.issue_line_id.product_id.categ_id.cate_name or False
            if cate_name == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                dest_location_id = locat_ids[0]
            if cate_name == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
                if locat_ids:
                    dest_location_id = locat_ids[0]
            if dest_location_id and cate_name != 'finish':
                avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',line.issue_line_id.product_id.id),('warehouse_id','=',dest_location_id)])
                unit = 0
                if avg_cost_ids:
                    avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                    unit = avg_cost_id.avg_cost or 0
                product_price = unit * line.issue_line_id.product_isu_qty
                
                rs = {
                      'name': '/',
                      'product_id':line.issue_line_id.product_id and line.issue_line_id.product_id.id or False,
                      'product_qty':line.return_request_qty or False,
                      'product_uom':line.issue_line_id.uom_po_id and line.issue_line_id.uom_po_id.id or False,
                      'location_id':source_location_id,
                      'location_dest_id': dest_location_id,
                      'mrr_line_id':line.id,
                      'date':line.return_request_id.date or False,
                      'price_unit': unit or 0,
                      }
                
                move_id = move_obj.create(cr,uid,rs)
                # boi vi field price unit tu dong lam tron 2 so thap phan nen phai dung sql de update lai
                sql = '''
                        update stock_move set price_unit = %s where id = %s
                '''%(unit, move_id)
                cr.execute(sql)
                move_obj.action_done(cr, uid, [move_id])
                cr.execute(''' update stock_move set date=%s,date_expected=%s where id=%s ''',(line.return_request_id.date,line.return_request_id.date,move_id,))
            
                date_period = line.return_request_id.date
                sql = '''
                    select id from account_journal
                '''
                cr.execute(sql)
                journal_ids = [r[0] for r in cr.fetchall()]
                sql = '''
                    select id from account_period where '%s' between date_start and date_stop and special is False
                '''%(date_period)
                cr.execute(sql)
                period_ids = [r[0] for r in cr.fetchall()]
                 
                if not period_ids:
                    raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                    
                acc_expense = line.issue_line_id.product_id and line.issue_line_id.product_id.property_account_expense and line.issue_line_id.product_id.property_account_expense.id or False
                acc_asset = line.issue_line_id.product_id and line.issue_line_id.product_id.product_asset_acc_id and line.issue_line_id.product_id.product_asset_acc_id.id or False
                if not acc_expense or not acc_asset:
                    raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for all materials!'))
                
                journal_line.append((0,0,{
                            'name':line.return_request_id.name + ' - ' + line.issue_line_id.product_id.name, 
                            'account_id': acc_asset,
                            'debit':0,
                            'credit':product_price,
                            'product_id':line.issue_line_id.product_id.id,
                                       }))
                journal_line.append((0,0,{
                            'name':line.return_request_id.name + ' - ' + line.issue_line_id.product_id.name, 
                            'account_id': acc_expense,
                            'credit':0,
                            'debit':product_price,
                            'product_id':line.issue_line_id.product_id.id,
                        }))
                value={
                    'journal_id':journal_ids[0],
                    'period_id':period_ids[0] ,
                    'ref': line.return_request_id.name,
                    'date': date_period,
                    'mrr_line_id': line.id,
                    'line_id': journal_line,
                    'doc_type':'material_return_request'
                }
                new_jour_id = account_move_obj.create(cr,uid,value)
                auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
                if auto_ids:
                    auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                    if auto_id.material_return_request:
                        try:
                            account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                        except:
                            pass
        return self.write(cr, uid, ids, {'state': 'accepted'})
    
    def bt_reject(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_maintenance', 'tpt_reject_mrr_form_view')
        return {
                    'name': 'Alert',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.reject.mrr',
                    'domain': [],
                    'context': {},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
    
tpt_material_return_request_line()

class stock_move(osv.osv):
    _inherit = "stock.move"
    
    _columns = {
        'mrr_line_id': fields.many2one('tpt.material.return.request.line','Material Return Request Line',ondelete='restrict'),
    }

stock_move()

class account_move(osv.osv):
    _inherit = 'account.move'
    
    _columns = {
        'mrr_line_id': fields.many2one('tpt.material.return.request.line','Material Return Request Line',ondelete='restrict'),
    }
    
account_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
