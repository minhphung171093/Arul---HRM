# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
import locale
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_select_grn_invoice_wiz(osv.osv_memory):
    # def _get_journal(self, cr, uid, context=None):
    #     res = self._get_journal_id(cr, uid, context=context)
    #     if res:
    #         return res[0][0]
    #     return False

    def _get_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        vals = []
        journal_type = 'purchase'
        journal_obj = self.pool.get('account.journal')
        value = journal_obj.search(cr, uid, [('type', '=',journal_type )])
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            # t1 = jr_type.id,jr_type.name
            t1 = jr_type.id
            # if t1 not in vals:
            #     vals.append(t1)
        return t1
    _name = "tpt.select.grn.invoice.wiz"
    _columns = {
        # 'name': fields.char('', readonly=True),
        'tpt_grn_line': fields.one2many('tpt.select.grn.line', 'tpt_select_grn_id', 'Choose GRNs'),
        
        'tpt_po_id': fields.many2one('purchase.order', 'Purchase'),
        # 'journal_id': fields.selection(_get_journal_id, 'Destination Journal'),
        'journal_id':fields.many2one("account.journal", 'Journal'), 
        'invoice_date': fields.date('Invoiced Date'),
    }
    _defaults = {
        'journal_id' : _get_journal_id,
        'invoice_date': time.strftime('%Y-%m-%d'),
    }
    
    def onchange_tpt_po_id(self, cr, uid, ids,tpt_po_id=False, context=None): 
        tpt_grn_line = []
        if tpt_po_id:
            grn_obj = self.pool.get('stock.picking')
#             sql = '''
#             select id from stock_picking where purchase_id=%s and type='in' and state='done'
#                 and tpt_invoice_id is null and id not in (select grn_no from account_invoice 
#                             where purchase_id = %s and grn_no is not null)
#                 and id not in ( select pic.id 
#                                 from stock_picking pic, tpt_quanlity_inspection ins
#                                 where pic.id=ins.name
#                                     and pic.purchase_id=%s and pic.type='in' and pic.state='done' and ins.state!='done'
#                                 )
#                 and warehouse not in (select id from stock_location where name ='Block List')
#             '''%(tpt_po_id,tpt_po_id,tpt_po_id)
            
            sql = '''
                select id
                
                from stock_picking 
                
                where state='done' and invoice_state='2binvoiced' and purchase_id=%s
                
                and warehouse not in (select id from stock_location where name ='Block List')
                
                and purchase_id not in (select purchase_id from stock_picking where id in (select name from tpt_quanlity_inspection where state!='done'))
                
            '''%(tpt_po_id)
            
            cr.execute(sql)
            grn_ids = [r[0] for r in cr.fetchall()]
            for grn in grn_obj.browse(cr, uid, grn_ids, context):
                tpt_grn_name = grn.name or False
                tpt_grn_id  = grn.id or False
                tpt_grn_line.append((0,0,{'tpt_grn_name': tpt_grn_name, 'tpt_grn_id': tpt_grn_id}))
        return {'value': {'tpt_grn_line': tpt_grn_line}}  
        
    def func_create_invoice(self, cr, uid, ids, picking_ids, context=None):
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id','invoice_date'])
        if context.get('new_picking', False):
            onshipdata_obj['id'] = onshipdata_obj.new_picking
            onshipdata_obj[ids] = onshipdata_obj.new_picking
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        active_ids = picking_ids
        inv_type = 'in_invoice'
        context['inv_type'] = inv_type
        context['not_gen_seq_inv'] = 1
        if isinstance(onshipdata_obj[0]['journal_id'], tuple):
            onshipdata_obj[0]['journal_id'] = onshipdata_obj[0]['journal_id'][0]
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
              journal_id = onshipdata_obj[0]['journal_id'],
              group = False,
              type = 'in_invoice',
              context=context)
        return res
    
    def check_inspec(self, cr, uid, picking_ids, context=None):
        if context is None:
            context = {}
        res = {}
        for pick in self.pool.get('stock.picking').browse(cr, uid, picking_ids, context=context):
            if pick.type == 'in':
                sql = '''
                    select case when count(id)>0 then 1 else 0 end abc from tpt_quanlity_inspection where state in ('draft','remaining') and name=%s
                '''%(pick.id)
                cr.execute(sql)
                abc = cr.fetchone()[0]
                if abc:
                    raise osv.except_osv(_('Warning!'),_('You should check Quality Inspection of %s before the Create Invoice !'%pick.name))
                ###TPT-START-By TPT-R - ON 20/11/2015 - TO DO NOT ALLOW BLANK INVOICE LINE CREATED IN SYSEM - REF INCIDENT NO: 3095
                grn_qty = 0
                qty = 0
                remaining_qty = 0
                qty_approve = 0
                sql = '''
                select case when sum(qty)>0 then sum(qty) else 0 end qty, 
                case when sum(remaining_qty)>0 then sum(remaining_qty) else 0 end remaining_qty,
                case when sum(qty_approve)>0 then sum(qty_approve) else 0 end qty_approve
                from tpt_quanlity_inspection where state in ('done')and name=%s
                '''%(pick.id)
                cr.execute(sql)
                for inspec in cr.fetchall():
                    qty = inspec[0]
                    remaining_qty = inspec[1]
                    qty_approve = inspec[2]               
                for line in pick.move_lines:    
                    if line.action_taken=='need':
                        grn_qty += line.product_uos_qty
                if grn_qty==qty and remaining_qty ==0 and qty_approve==0 and line.action_taken=='need':
                    raise osv.except_osv(_('Warning!'),_('Should not allow to Create Invoice. The Quality Inspection of %s has been rejected !'%pick.name))
                ###TPT-END
                
        return res
    
    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice_ids = []
        data_pool = self.pool.get('ir.model.data')
        picking_ids = []
        for wizard in self.browse(cr, uid, ids, context=context):
            for line in wizard.tpt_grn_line:
                if line.tpt_grn_id:
                    picking_ids.append((line.tpt_grn_id.id))
        currency_id = False
        currency_name = False
        if picking_ids:
            self.check_inspec(cr, uid, picking_ids, context=context)
        for wiz in self.browse(cr, uid, ids, context=context):
            for picking_id in picking_ids:
                pick_id = self.pool.get('stock.picking').browse(cr, uid, picking_id)
                if pick_id.type == 'in':
                    currency_id = pick_id.purchase_id and pick_id.purchase_id.currency_id and pick_id.purchase_id.currency_id.id or False
                    currency_name = pick_id.purchase_id and pick_id.purchase_id.currency_id and pick_id.purchase_id.currency_id.name or False
                if pick_id.type == 'out': 
                    currency_id = pick_id.sale_id and pick_id.sale_id.currency_id and pick_id.sale_id.currency_id.id or False
                    currency_name = pick_id.sale_id and pick_id.sale_id.currency_id and pick_id.sale_id.currency_id.name or False
                if currency_id:
                    if currency_name != 'INR':
                        if not wiz.invoice_date:
                            raise osv.except_osv(_('Warning!'),_('Please choose date of invoice!')) 
                        cur_rate_obj =self.pool.get('res.currency.rate')
                        cur_rate_ids = cur_rate_obj.search(cr, uid, [('currency_id','=',currency_id),('name','=',wiz.invoice_date)])
                        if not cur_rate_ids:
                            raise osv.except_osv(_('Warning!'),_('Rate of currency is not defined on %s!'%wiz.invoice_date)) 
                        else:
                            cur_rate_ids1 = cur_rate_obj.search(cr, uid, [('currency_id','=',currency_id),('name','=',wiz.invoice_date), ('rate_type', '=', 'selling')])
                            if not cur_rate_ids1:
                                raise osv.except_osv(_('Warning!'),_('Selling Rate of Currency is not defined on %s!'%wiz.invoice_date))
                else:
                    raise osv.except_osv(_('Warning!'),_('Please check again! Do not have currency for Picking order %s!'%pick_id.name))
        res = self.func_create_invoice(cr, uid, ids, picking_ids, context=context)
        invoice_ids += res.values()
        inv_id = invoice_ids and invoice_ids.pop(0) or False
        for inv in invoice_ids:
            for line in self.pool.get('account.invoice').browse(cr, uid, inv, context=context).invoice_line:
                self.pool.get('account.invoice.line').write(cr,uid,line.id,{'invoice_id':inv_id})
        self.pool.get('account.invoice').unlink(cr, 1, invoice_ids)
        # update tpt_invoice_id
        self.pool.get('stock.picking').write(cr,uid,picking_ids,{'tpt_invoice_id':inv_id})
        # generate seq
        sql = '''
        select code from account_fiscalyear where '%s' between date_start and date_stop
       '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not inv_id:
            raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
        if fiscalyear:
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.supplier.invoice.sequence') or '/'
            name =  sequence and sequence+'/'+fiscalyear['code'] or '/'
            self.pool.get('account.invoice').write(cr,uid,[inv_id],{'name':name,'grn_no':False})
        
        inv_type = "in_invoice"
        action_model = False
        action = {}
        action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,[inv_id]))+"])]"
        return action

tpt_select_grn_invoice_wiz()

class tpt_select_grn_line(osv.osv_memory):
    _name = "tpt.select.grn.line"
    _columns = {
        'tpt_select_grn_id':fields.many2one("tpt.select.grn.invoice.wiz", 'GRN'), 
        'tpt_grn_name': fields.char('GRN'), 
        'tpt_grn_id':fields.many2one("stock.picking.in", 'GRN'),  
 }
tpt_select_grn_line()