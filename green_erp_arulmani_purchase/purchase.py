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
from openerp import netsvc

class tpt_purchase_indent(osv.osv):
    _name = 'tpt.purchase.indent'
    _columns = {
        'name': fields.char('Indent No.', size=1024, readonly=True ),
        'date_indent':fields.date('Indent Date',required = True, states={'cancel': [('readonly', True)]}),
        'document_type':fields.selection([
                                ('base','VV Level Based PR'),
                                ('capital','VV Capital PR'),
                                ('local','VV Local Purchase PR'),
                                ('maintenance','VV Maintenance PR'),
                                ('consumable','VV Consumable PR'),
                                ('outside','VV Outside Service PR'),
                                ('spare','VV Spare (Project) PR'),
                                ('service','VV Service PR'),
                                ('normal','VV Normal PR'),
                                ('raw','VV Raw Material PR'),
                                ],'Document Type',required = True, states={'cancel': [('readonly', True)] }),
        'intdent_cate':fields.selection([
                                ('emergency','Emergency Indent'),
                                ('normal','Normal Indent')],'Indent Category',required = True, states={'cancel': [('readonly', True)] }),
        'department_id':fields.many2one('hr.department','Department', states={'cancel': [('readonly', True)] }),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'date_expect':fields.date('Expected Date', states={'cancel': [('readonly', True)] }),
        'select_normal':fields.selection([('single','Single Quotation'),
                                          ('special','Special Quotation'),
                                          ('multiple','Multiple Quotation')],'Select', states={'cancel': [('readonly', True)] }),
        'supplier_id':fields.many2one('res.partner','Supplier',  states={'cancel': [('readonly', True)] }),
        'employee_id':fields.many2one('hr.employee','Employee',  states={'cancel': [('readonly', True)] }),
        'reason':fields.text('Reason', states={'cancel': [('readonly', True)] }),
        'header_text':fields.text('Header Text',states={'cancel': [('readonly', True)] }), #TPT
        'requisitioner':fields.many2one('hr.employee','Requisitioner',states={'cancel': [('readonly', True)] }),
        'purchase_product_line':fields.one2many('tpt.purchase.product','pur_product_id','Materials',states={'cancel': [('readonly', True)] }),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Closed'),
                                  ('done', 'Approve'),('rfq_raised','RFQ Raised'),
                                  ('quotation_raised','Quotation Raised'),
                                  ('po_raised','PO Raised')],'Status', readonly=True),
        'section_id': fields.many2one('arul.hr.section','Section',ondelete='restrict',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'project_id': fields.many2one('tpt.project','Project', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'project_section_id': fields.many2one('tpt.project.section','Project Section',ondelete='restrict',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
    
    }
    
    def _get_department_id(self,cr,uid,context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.employee_id and user.employee_id.department_id and user.employee_id.department_id.id or False

    def _get_section_id(self,cr,uid,context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.employee_id and user.employee_id.section_id and user.employee_id.section_id.id or False

    _defaults = {
        'state':'draft',
        'date_indent': fields.datetime.now,
        'name': '/',
        'intdent_cate':'normal',
#         'department_id': _get_department_id,
#         'section_id':_get_section_id,
#         'create_uid': lambda self,cr,uid,c:uid,
#         'document_type':'base',
    }
    
#     def first_approve(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids):
#             for indent_line in line.purchase_product_line:
#                 self.pool.get('tpt.purchase.product').write(cr, uid, [indent_line.id],{'indent_status':'+'})
#         return self.write(cr, uid, ids,{'state':'first_approve'})
            
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            for indent_line in line.purchase_product_line:
                self.pool.get('tpt.purchase.product').write(cr, uid,  [indent_line.id],{'state':'confirm'})
        return self.write(cr, uid, ids,{'state':'done'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            rfq_ids = self.pool.get('tpt.rfq.line').search(cr,uid,[('po_indent_id','=',line.id), ('state','=','done')])
            po_ids = self.pool.get('purchase.order').search(cr,uid,[('po_indent_no','=',line.id),('state','=','approved')])
            if po_ids:
                raise osv.except_osv(_('Warning!'),_('Purchase Indent was existed at the Purchase Order.!'))
            if rfq_ids:
                raise osv.except_osv(_('Warning!'),_('Purchase Indent was existed at the request for quotation.!'))
            self.write(cr, uid, ids,{'state':'cancel'})
        return True   

    def create(self, cr, uid, vals, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
#         vals['department_id'] = user.employee_id and user.employee_id.department_id and user.employee_id.department_id.id or False
        if 'document_type' in vals:
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                if (vals['document_type']=='base'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.based')
                        vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                if (vals['document_type']=='capital'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.capital')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='local'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.local')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='maintenance'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.maintenance')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='consumable'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.consumable')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='outside'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.outside')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='spare'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.spare')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='service'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.service')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='normal'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.normal')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='raw'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.raw')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
        new_id = super(tpt_purchase_indent, self).create(cr, uid, vals, context=context)    
#         indent = self.browse(cr,uid, new_id)
#         if indent.select_normal != 'multiple':
#             if (len(indent.purchase_product_line)>1):
#                 raise osv.except_osv(_('Warning!'),_(' You must choose Select is multiple if you want more than one product!'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'document_type' in vals:
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                if (vals['document_type']=='base'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.based')
                        vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
                if (vals['document_type']=='capital'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.capital')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='local'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.local')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='maintenance'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.maintenance')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='consumable'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.consumable')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='outside'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.outside')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='spare'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.spare')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='service'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.service')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='normal'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.normal')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
                if (vals['document_type']=='raw'):
                    if vals.get('name','/')=='/':
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.raw')
                        vals['name'] =  sequence and sequence +'/'+fiscalyear['code']or '/'
        new_write = super(tpt_purchase_indent, self).write(cr, uid, ids, vals, context=context)    
        return new_write
    
    def onchange_date_expect(self, cr, uid, ids,date_indent=False, context=None):
        vals = {}
        kq=''
        if date_indent :
            sql='''
            select date(date('%s')+INTERVAL '1 month 1days') as date_indent
            '''%(date_indent)
            cr.execute(sql)
            dates = cr.dictfetchone()['date_indent']
        return {'value': {'date_expect':dates}}
#     def onchange_create_uid(self, cr, uid, ids,create_uid=False, context=None):
#         vals = {}
#         user = self.pool.get('res.users').browse(cr,uid,uid)
#         vals = {
#                 'department_id': user.employee_id and user.employee_id.department_id and user.employee_id.department_id.id,
#                 'section_id': user.employee_id and user.employee_id.section_id and user.employee_id.section_id.id
#                 }
#         return {'value': vals}
    
    def onchange_document_type(self, cr, uid, ids,document_type=False, context=None):
        vals = {'value':{
                        'purchase_product_line':[],
                      }
                
                }
        for indent in self.browse(cr, uid, ids):
            sql = '''
                    delete from tpt_purchase_product where pur_product_id = %s
            '''%(indent.id)
            cr.execute(sql)
        if document_type:
            vals['purchase_product_line']=False
            if document_type == 'base':
                warning = {  
                          'title': _('Warning!'),  
                          'message': _('VV Level Based PR is not created by handle!   '),  
                          }  
                vals['document_type']=False
                return {'value': vals,'warning':warning}
        return {'value': vals}
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_po_indent_no'):
            if context.get('quotation_no'):
                sql = '''
                    select po_indent_id from tpt_purchase_quotation_line where purchase_quotation_id in(select id from tpt_purchase_quotation where id = %s)
                '''%(context.get('quotation_no'))
                cr.execute(sql)
                quotation_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',quotation_ids)]
        if context.get('quotation_no'):
            if context.get('search_po_indent_no_emergency'):
                sql = '''
                    select id from tpt_purchase_indent where intdent_cate = 'normal' and state = 'done'
                '''
                cr.execute(sql)
                emergency_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',emergency_ids)]
        if context.get('search_po_indent_no_gate_in_pass'):
            if context.get('po_id'):
                sql = '''
                    select po_indent_no from purchase_order where id = %s
                '''%(context.get('po_id'))
                cr.execute(sql)
                gate_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',gate_ids)]
        if context.get('search_po_indent_line'):
            if context.get('po_document_type'):
                if context.get('po_document_type')=='standard':
                    sql = '''
                        select pur_product_id from tpt_purchase_product where state = '++' and (doc_type_relate = 'normal' or doc_type_relate = 'maintenance' or doc_type_relate = 'spare' or doc_type_relate = 'base' or doc_type_relate = 'consumable')
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                if context.get('po_document_type')=='local':
                    sql = '''
                        select pur_product_id from tpt_purchase_product where state = '++' and doc_type_relate = 'local' 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                if context.get('po_document_type')=='asset':
                    sql = '''
                        select pur_product_id from tpt_purchase_product where state = '++' and doc_type_relate = 'capital' 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                if context.get('po_document_type')=='raw':
                    sql = '''
                        select pur_product_id from tpt_purchase_product where state = '++' and doc_type_relate = 'raw' 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                if context.get('po_document_type')=='service':
                    sql = '''
                        select pur_product_id from tpt_purchase_product where state = '++' and doc_type_relate = 'service' 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                if context.get('po_document_type')=='out':
                    sql = '''
                        select pur_product_id from tpt_purchase_product where state = '++' and doc_type_relate = 'outside'
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
        if context.get('search_name_of_indent',False):
            name = context['search_name_of_indent']
            pur_ids = self.search(cr, uid, [('name','ilike',name)])
            args += [('id','in',pur_ids)]
        return super(tpt_purchase_indent, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if context is None:
            context = {}
        if name:
            context.update({'search_name_of_indent': name})
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)

tpt_purchase_indent()
class tpt_purchase_product(osv.osv):
    _name = 'tpt.purchase.product'
    def _get_on_hand_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                    select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id in (select id from stock_location
                                                                                        where usage = 'internal')
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id in (select id from stock_location
                                                                                        where usage = 'internal')
                            )foo
                '''%(line.product_id.id,line.product_id.id)
            cr.execute(sql)
            ton_sl = cr.dictfetchone()['ton_sl']
            
            res[line.id] = {
                'on_hand_qty': ton_sl,
            }
        return res
    def _get_total_val(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
               'total_val' : 0.0,
               }
            total = line.product_uom_qty * line.price_unit
            res[line.id]['total_val'] = total
        return res
    
    _columns = {
        'pur_product_id':fields.many2one('tpt.purchase.indent','Purchase Indent',ondelete='cascade' ),
        'product_id': fields.many2one('product.product', 'Material Code'),
        'doc_type_relate':fields.selection([
                                ('base','VV Level Based PR'),
                                ('capital','VV Capital PR'),
                                ('local','VV Local Purchase PR'),
                                ('maintenance','VV Maintenance PR'),
                                ('consumable','VV Consumable PR'),
                                ('outside','VV Outside Service PR'),
                                ('spare','VV Spare (Project) PR'),
                                ('service','VV Service PR'),
                                ('normal','VV Normal PR'),
                                ('raw','VV Raw Material PR'),
                                ],'Document Type'),
#         'doc_type_relate': fields.related('pur_product_id', 'document_type',type = 'char', string='Document Type',store=True),
        #'dec_material':fields.text('Material Description'),
        'description':fields.char('Mat. Description', size = 50),
        'item_text':fields.text('Item Text' ),
        'product_uom_qty': fields.float('Indent Qty' ),   
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'pending_qty': fields.float('Pending Qty' ), 
        #'recom_vendor_id': fields.many2one('res.partner', 'Recommended Vendor'),
        'recom_vendor': fields.char('Recommended Vendor', size = 30 ),
        'release_by':fields.selection([('1','Store Level'),('2','HOD Level')],'Released By'),
        'state':fields.selection([('draft', 'Draft'),('confirm', 'Confirmed'),('close', 'Closed'),
                                          ('+', 'Store Approved'),('++', 'Store & HOD Approved'),
                                          ('x', 'Store Rejected'),('xx', 'Store & HOD Rejected'),
                                          ('rfq_raised','RFQ Raised'),
                                          ('cancel','PO Cancelled'),
                                          ('quotation_raised','Quotation Raised'),
                                          ('po_raised','PO Raised'),
                                          ('quotation_cancel','Quotation Cancelled'),
                                          ],'Indent Status', readonly=True),
#Hung moi them 2 Qty theo yeu casu bala
        'mrs_qty': fields.float('Reserved Qty'),
        'inspection_qty': fields.float('Inspection Quantity' ), 
        'on_hand_qty':fields.function(_get_on_hand_qty,digits=(16,3),type='float',string='On Hand Qty',multi='sum',store=False),
        'department_id_relate':fields.related('pur_product_id', 'department_id',type = 'many2one', relation='hr.department', string='Department',store=True),
        'section_id_relate': fields.related('pur_product_id', 'section_id',type = 'many2one', relation='arul.hr.section', string='Section',store=True),
        'requisitioner_relate':fields.related('pur_product_id', 'requisitioner',type = 'many2one', relation='hr.employee', string='Requisitioner',store=True),
        'date_indent_relate':fields.related('pur_product_id', 'date_indent',type = 'date', string='Indent Date',store=True),
        'flag': fields.boolean('Flag'),
        'store_date':fields.datetime('Store Approved Date',readonly = True),
        'hod_date':fields.datetime('HOD Approved Date',readonly = True),
        'price_unit': fields.float('Unit Price',digits=(16,3) ), 
        'total_val':fields.function(_get_total_val,digits=(16,3),type='float',string='Total Value',multi='avg',store=False),
        }  
#     
    _defaults = {
        'state':'draft',
        'flag': False,
        'price_unit':0.0
    }
    
#     def _check_product_id(self, cr, uid, ids, context=None):
#         for product in self.browse(cr, uid, ids, context=context):
#             product_ids = self.search(cr, uid, [('id','!=',product.id),('product_id', '=',product.product_id.id),('pur_product_id','=',product.pur_product_id.id)])
#             if product_ids:
#                 raise osv.except_osv(_('Warning!'),_('Product was existed !'))
#                 return False
#             return True
#         
#     _constraints = [
#         (_check_product_id, 'Identical Data', ['pur_product_id', 'product_id']),
#     ]   
    
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
#             father = self.pool.get('tpt.purchase.indent').browse(cr,uid,line.pur_product_id.id)
            sql = '''
                    select %s in (select uid from res_groups_users_rel where gid in (select id from res_groups where name='Purchase Store Mgr' 
                    and category_id in (select id from ir_module_category where name='VVTI - PURCHASE')))
                    '''%(uid)
            cr.execute(sql)
            mana = cr.fetchone()
#                 fq = self.pool.get('res_users').browse(cr,uid,uid)
            if line.state == 'confirm':
                if mana[0]:
                    return self.write(cr, uid, ids,{'state':'+','store_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    raise osv.except_osv(_('Warning!'),_('User does not have permission to approve!'))
            if line.state == '+':
                if line.pur_product_id.department_id and line.pur_product_id.department_id.primary_auditor_id and line.pur_product_id.department_id.primary_auditor_id.id==uid:
                    return self.write(cr, uid, ids,{'state':'++','hod_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    raise osv.except_osv(_('Warning!'),_('User does not have permission to approve!'))
    def bt_reject(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            sql = '''
                    select %s in (select uid from res_groups_users_rel where gid in (select id from res_groups where name='Purchase Store Mgr' 
                    and category_id in (select id from ir_module_category where name='VVTI - PURCHASE')))
                    '''%(uid)
            cr.execute(sql)
            mana = cr.fetchone()
            
            if line.state == 'confirm':
                if mana[0]:
                    return self.write(cr, uid, ids,{'state':'x','store_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    raise osv.except_osv(_('Warning!'),_('User does not have permission to reject!'))
            if line.state == '+':
                if line.pur_product_id.department_id and line.pur_product_id.department_id.primary_auditor_id and line.pur_product_id.department_id.primary_auditor_id.id==uid:
                    return self.write(cr, uid, ids,{'state':'xx','hod_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                else:
                    raise osv.except_osv(_('Warning!'),_('User does not have permission to reject!'))
            
#         return self.write(cr, uid, ids,{'state':''})
#     def bt_approve_hod(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids,{'state':'++'})
#     def bt_reject_hod(self, cr, uid, ids, context=None):
#         return self.write(cr, uid, ids,{'state':'xx'})
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        res = {'value':{
                    'uom_po_id':False,
                    'price_unit':False,
                    'description': False,
                    'flag': False,
                    'mrs_qty':0.0,
                    }}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            if product.categ_id.cate_name == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials']),('location_id','=',parent_ids[0])])
                sql = '''
                    select avg_cost from tpt_product_avg_cost where warehouse_id = %s and product_id=%s
                    
                '''%(locat_ids[0],product_id)
                cr.execute(sql)
                avg_cost=cr.dictfetchone()['avg_cost']
                res['value'].update({
                    'price_unit':float(avg_cost),
                    })
            if product.categ_id.cate_name == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Spare'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
                sql = '''
                    select avg_cost from tpt_product_avg_cost where warehouse_id = %s and product_id=%s
                    
                '''%(locat_ids[0],product_id)
                cr.execute(sql)
                avg_cost=cr.dictfetchone()['avg_cost']
                res['value'].update({
                    'price_unit':float(avg_cost),
                    })
            sql = '''
                select case when sum(product_uom_qty) != 0 then sum(product_uom_qty) else 0 end product_mrs_qty from tpt_material_request_line where product_id=%s and material_request_id in (select id from tpt_material_request where state='done' and id not in (select name from tpt_material_issue where state='done'))
            '''%(product_id)
            cr.execute(sql)
            product_mrs_qty=cr.dictfetchone()['product_mrs_qty']
            res['value'].update({
                    'uom_po_id':product.uom_id.id,
                    #'price_unit':product.list_price,
                    'description': product.name,
                    'mrs_qty':float(product_mrs_qty),
                    })
            if product.categ_id.cate_name == 'consum' or product.categ_id.cate_name == 'service':
                res['value'].update({
                    'flag':True,
                    })
        return res
    
    def create(self, cr, uid, vals, context=None):
        
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            sql = '''
                select case when sum(product_uom_qty) != 0 then sum(product_uom_qty) else 0 end product_mrs_qty from tpt_material_request_line where product_id=%s and material_request_id in (select id from tpt_material_request where state='done' and id not in (select name from tpt_material_issue where state='done'))
            '''%(vals['product_id'])
            cr.execute(sql)
            product_mrs_qty=cr.dictfetchone()['product_mrs_qty']
            if product.categ_id.cate_name != 'consum':
                vals.update({
                             'uom_po_id':product.uom_id.id,
                             'description':product.name,
                             'mrs_qty':float(product_mrs_qty),
                             })
            else:
                vals.update({
                             'mrs_qty':float(product_mrs_qty),
                             })
        new_id = super(tpt_purchase_product, self).create(cr, uid, vals, context)
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        if 'pending_qty' in vals:
            if (vals['pending_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Pending Quantity is not allowed as negative values'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            sql = '''
                select case when sum(product_uom_qty) != 0 then sum(product_uom_qty) else 0 end product_mrs_qty from tpt_material_request_line where product_id=%s and material_request_id in (select id from tpt_material_request where state='done' and id not in (select name from tpt_material_issue where state='done'))
            '''%(vals['product_id'])
            cr.execute(sql)
            product_mrs_qty=cr.dictfetchone()['product_mrs_qty']
            if product.categ_id.cate_name != 'consum':
                vals.update({
                             'uom_po_id':product.uom_id.id,
                             'description':product.name,
                             'mrs_qty':float(product_mrs_qty),
                             })
            else:
                vals.update({
                             'mrs_qty':float(product_mrs_qty),
                             })
        new_write = super(tpt_purchase_product, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.product_uom_qty < 0:
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
            if line.pending_qty < 0:
                raise osv.except_osv(_('Warning!'),_('Pending Quantity is not allowed as negative values'))
        return new_write
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
#         reads = self.read(cr, uid, ids, ['id', 'product_id'], context)
#  
#         for record in reads:
        for line in self.browse(cr,uid,ids):
            cate_name = line.product_id.default_code + ' - ' + line.product_id.name
            res.append((line.id,cate_name))
        return res    

    def onchange_hod_qty(self, cr, uid, ids, product_uom_qty=False):
        vals={}
        if product_uom_qty:
            for move in self.read(cr, uid, ids, ['product_uom_qty']):
                if product_uom_qty > move['product_uom_qty']:
                    warning = {  
                              'title': _('Warning!'),  
                              'message': _('The Indent Qty not be greater than the previous Indent Qty!'),  
                              }  
                    vals['product_uom_qty']=move['product_uom_qty']
                    return {'value': vals,'warning':warning}
        return {'value': vals}  

#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_indent_hod'):
#             primary_auditor_ids = self.pool.get('hr.department').search(cr, uid, [('primary_auditor_id','=',uid)])
#             user_id = self.pool.get('res.users').browse(cr, uid, uid)
#             department_id = user_id.employee_id and user_id.employee_id.department_id and user_id.employee_id.department_id.id or False
#             if primary_auditor_ids and department_id:
#                 sql = '''
#                     select id from tpt_purchase_product where pur_product_id in (select id from tpt_purchase_indent where department_id =%s)
#                 '''%(department_id)
#                 cr.execute(sql)
#                 leave_details_ids = [r[0] for r in cr.fetchall()]
#                 args += [('id','in',leave_details_ids)]
#         return super(tpt_purchase_product, self).search(cr, uid, args, offset, limit, order, context, count)
#     
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#        ids = self.search(cr, user, args, context=context, limit=limit)
#        return self.name_get(cr, user, ids, context=context)
   
tpt_purchase_product()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'cate_name':fields.selection([('raw','Raw Materials'),('finish','Finished Product'),('spares','Spares'),('consum','Consumables')], 'Category Name', required = True),
        'description':fields.text('Description',size = 256),
        'tpt_type':fields.selection([('sale','Sale'),('purchase','Purchase')], 'Type'),
        }
#     _defaults = {
#         'tpt_type': 'purchase',
#                  }
    def create(self, cr, uid, vals, context=None):
        if 'name' in vals:
            name = vals['name'].replace(" ","")
            vals['name'] = name
        return super(product_category, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'name' in vals:
            name = vals['name'].replace(" ","")
            vals['name'] = name
        return super(product_category, self).write(cr, uid,ids, vals, context)
    
#     def _check_code_id(self, cr, uid, ids, context=None):
#         for cost in self.browse(cr, uid, ids, context=context):
#             sql = '''
#                 select id from product_category where id != %s and lower(name) = lower('%s')
#             '''%(cost.id,cost.name)
#             cr.execute(sql)
#             cost_ids = [row[0] for row in cr.fetchall()]
#             if cost_ids:  
#                 return False
#         return True
    
#     def _check_product_category(self, cr, uid, ids, context=None):
#         for pro_cate in self.browse(cr, uid, ids, context=context):
#             sql = '''
#                  select id from product_category where id != %s and lower(name) = lower('%s') and cate_name = '%s'
#              '''%(pro_cate.id,pro_cate.name,pro_cate.cate_name)
#             cr.execute(sql)
#             code_ids = [row[0] for row in cr.fetchall()]
#             if code_ids:
#                 raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))
# #             pro_cate_ids = self.search(cr, uid, [('id','!=',pro_cate.id),('name','=',pro_cate.name),('cate_name', '=',pro_cate.cate_name)])
# #             if pro_cate_ids:
# #                 raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))    
#                 return False
#             return True
    def _check_product_category(self, cr, uid, ids, context=None):
        for pro_cate in self.browse(cr, uid, ids, context=context):
            sql = '''
                 select id from product_category where id != %s and (cate_name = '%s' or name = '%s')
             '''%(pro_cate.id,pro_cate.cate_name, pro_cate.name)
            cr.execute(sql)
            code_ids = [row[0] for row in cr.fetchall()]
            if code_ids:
                raise osv.except_osv(_('Warning!'),_(' Product Category Name or Code should be unique!'))
#             pro_cate_ids = self.search(cr, uid, [('id','!=',pro_cate.id),('name','=',pro_cate.name),('cate_name', '=',pro_cate.cate_name)])
#             if pro_cate_ids:
#                 raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))    
                return False
            return True
        
    _constraints = [
        (_check_product_category, 'Identical Data', ['cate_name']),
#         (_check_code_id, 'Identical Data', ['name']),
    ]    
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['cate_name'], context)
 
        for record in reads:
            cate_name = record['cate_name']
            name = ''
            if cate_name == 'raw':
                name = 'Raw Materials'
            if cate_name == 'finish':
                name = 'Finished Product'
            if cate_name == 'spares':
                name = 'Spares'
            if cate_name == 'consum':
                name = 'Consumables'
            res.append((record['id'], name))
        return res
product_category()

class product_product(osv.osv):
    _inherit = "product.product"
    
    def _inventory(self, cr, uid, ids, field_names=None, arg=None, context=None):
        result = {}
        if not ids: return result

#         context['only_with_stock'] = True
        inventory_obj = self.pool.get('tpt.product.inventory')
        for id in ids:
            result.setdefault(id, [])
            sql = 'delete from tpt_product_inventory where product_id=%s'%(id)
            cr.execute(sql)
            sql = '''
                select foo.loc,foo.prodlot_id,foo.id as uom,sum(foo.product_qty) as ton_sl from 
                    (select l2.id as loc,st.prodlot_id,pu.id,st.product_qty
                        from stock_move st 
                            inner join stock_location l2 on st.location_dest_id= l2.id
                            inner join product_uom pu on st.product_uom = pu.id
                        where st.state='done' and st.product_id=%s and l2.usage = 'internal'
                    union all
                    select l1.id as loc,st.prodlot_id,pu.id,st.product_qty*-1
                        from stock_move st 
                            inner join stock_location l1 on st.location_id= l1.id
                            inner join product_uom pu on st.product_uom = pu.id
                        where st.state='done' and st.product_id=%s and l1.usage = 'internal'
                    )foo
                    group by foo.loc,foo.prodlot_id,foo.id
            '''%(id,id)
            cr.execute(sql)
            for inventory in cr.dictfetchall():
                new_id = inventory_obj.create(cr, uid, {'warehouse_id':inventory['loc'],'prodlot_id':inventory['prodlot_id'],'hand_quantity':inventory['ton_sl'],'uom_id':inventory['uom']})
                result[id].append(new_id)
        return result
    def _onhand_qty(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for time in self.browse(cr, uid, ids, context=context):
            res[time.id] = {
                'onhand_qty': 0.0,
            }
            if time.id : 
                sql = '''
                select sum(foo.product_qty) as ton_sl from 
                    (select l2.id as loc,st.prodlot_id,pu.id,st.product_qty
                        from stock_move st 
                            inner join stock_location l2 on st.location_dest_id= l2.id
                            inner join product_uom pu on st.product_uom = pu.id
                        where st.state='done' and st.product_id=%s and l2.usage = 'internal'
                    union all
                    select l1.id as loc,st.prodlot_id,pu.id,st.product_qty*-1
                        from stock_move st 
                            inner join stock_location l1 on st.location_id= l1.id
                            inner join product_uom pu on st.product_uom = pu.id
                        where st.state='done' and st.product_id=%s and l1.usage = 'internal'
                    )foo
                    group by foo.loc,foo.prodlot_id,foo.id
            '''%(time.id,time.id)
                sql1 = '''
                SELECT sum(onhand_qty) onhand_qty
            From
            (SELECT
                   
                case when loc1.usage != 'internal' and loc2.usage = 'internal'
                then stm.primary_qty
                else
                case when loc1.usage = 'internal' and loc2.usage != 'internal'
                then -1*stm.primary_qty 
                else 0.0 end
                end onhand_qty
                        
            FROM stock_move stm 
                join stock_location loc1 on stm.location_id=loc1.id
                join stock_location loc2 on stm.location_dest_id=loc2.id
            WHERE stm.state= 'done' and product_id=%s)foo
                   '''% (time.id)
                cr.execute(sql1)
                a = cr.fetchone()
                if a:
                    time_total = a[0]                            
                else:
                    time_total=0.0
            res[time.id]['onhand_qty'] = time_total            
        return res
    _columns = {
        'description':fields.text('Description'),
        'batch_appli_ok':fields.boolean('Is Batch Applicable'),
        'default_code' : fields.char('Internal Reference', required = True, size=64, select=True),
        'cate_name': fields.char('Cate Name',size=64),
        'supplier_id':fields.many2one('res.partner', 'Supplier'),
        'po_price': fields.float('PO Price'),
        'invoice_address': fields.char('Invoice Address', size = 1024),
        'street2': fields.char('', size = 1024),
        'city': fields.char('', size = 1024),
        'country_id': fields.many2one('res.country', ''),
        'state_id': fields.many2one('res.country.state', ''),
        'zip': fields.char('', size = 1024),
        'inventory_line':fields.function(_inventory, method=True,type='one2many', relation='tpt.product.inventory', string='Inventory'),
        'spec_parameter_line':fields.one2many('tpt.spec.parameters.line', 'product_id', 'Spec Parameters'),
        'tpt_product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Finished Product Type'),
        'min_stock': fields.float('Min. Stock Level'),
        'max_stock': fields.float('Max. Stock Level'),
        're_stock': fields.float('Reorder Level'),
        'po_text': fields.char('PO Text', size = 1024),
        'mrp_control':fields.boolean('MRP Control Type'),
        'tpt_description':fields.text('Description', size = 256),
        'bin_location':fields.char('Bin Location', size = 1024),
        'old_no':fields.char('Old Material No.', size = 1024),
        'tpt_mater_type':fields.selection([('mechan','Mechanical'),
                                           ('store','Store'),
                                           ('civil','Civil'),
                                           ('elect','Electrical'),
                                           ('inst','Instrumentation'),
                                           ('raw_mat','Raw. Mat. & Prod'),
                                           ('qc','QC and R&D'),
                                           ('safe','Safety & Personnel'),('proj','Projects')],'Material Type'),
        'onhand_qty': fields.function(_onhand_qty, string='OnHand Qty', multi='test_qty'),
        
        'tolerance_qty': fields.float('Tolerance'), #TPT
        
        }
    
    _defaults = {
        'categ_id': False,
        'sale_ok': False,
        'purchase_ok': False,
                 }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_cate_name'):
                sql = '''
                     select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.cate_name = 'finish') 
                        and product_product.product_tmpl_id = product_template.id;
                '''
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        if context.get('search_product'):
            if context.get('po_indent_id'):
                sql = '''
                    select product_id from tpt_purchase_product where purchase_indent_id in(select id from tpt_purchase_indent where id = %s)
                '''%(context.get('po_indent_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        if context.get('search_po_product'):
            if context.get('po_indent_no'):
                sql = '''
                    select product_id from tpt_purchase_product where purchase_indent_id in(select id from tpt_purchase_indent where id = %s)
                '''%(context.get('po_indent_no'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        if context.get('search_rfq_product'):
            if context.get('po_indent_id'):
                sql = '''
                    select product_id from tpt_purchase_product where pur_product_id = %s and state = '++'
                '''%(context.get('po_indent_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        if context.get('search_indent_type_cate'):
            if context.get('document_type'):
                if context.get('document_type')=='raw':
                    sql = '''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.cate_name = 'raw') 
                            and product_product.product_tmpl_id = product_template.id and product_template.purchase_ok = True;
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                elif context.get('document_type')=='consumable':
                    sql = '''
                        select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.cate_name = 'consum') 
                        and product_product.product_tmpl_id = product_template.id and product_template.purchase_ok = True;
 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                elif context.get('document_type')=='service':
                    sql = '''
                        select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.cate_name = 'service') 
                        and product_product.product_tmpl_id = product_template.id and product_template.purchase_ok = True;
 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                elif context.get('document_type')=='spare':
                    sql = '''
                                               select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.cate_name = 'spares') 
                        and product_product.product_tmpl_id = product_template.id and product_template.purchase_ok = True;
                     
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                elif context.get('document_type')=='capital':
                    sql = '''
                        select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.cate_name = 'assets') 
                        and product_product.product_tmpl_id = product_template.id and product_template.purchase_ok = True;
 
                    '''
                    cr.execute(sql)
                    pur_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',pur_ids)]
                else:
                        sql = '''
                           select product_product.id from product_product,product_template where product_product.product_tmpl_id = product_template.id and product_template.purchase_ok = True
                        '''
                        cr.execute(sql)
                        pur_ids = [row[0] for row in cr.fetchall()]
                        args += [('id','in',pur_ids)]

        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def _check_product(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
#             product_name_ids = self.search(cr, uid, [('id','!=',product.id),('name','=',product.name)])
            product_code_ids = self.search(cr, uid, [('id','!=',product.id),('default_code', '=',product.default_code)])
            if product_code_ids:
#                 raise osv.except_osv(_('Warning!'),_('Product Code and Name should be Unique!'))
                raise osv.except_osv(_('Warning!'),_('Product Code should be Unique!'))
                return False
            return True
        
    _constraints = [
        (_check_product, 'Identical Data', ['name', 'default_code']),
    ] 
    
    def onchange_supplier_id(self, cr, uid, ids, supplier_id=False):
        vals = {}
        if supplier_id:
            supplier = self.pool.get('res.partner').browse(cr, uid, supplier_id)
            vals = {'invoice_address':supplier.street,
                'street2':supplier.street2,
                'city':supplier.city,
                'country_id':supplier.country_id and supplier.country_id.id or '',
                'state_id':supplier.state_id and supplier.state_id.id or '',
                'zip':supplier.zip,
                }
        return {'value': vals}   
    
    def onchange_category_product_id(self, cr, uid, ids, categ_id=False):
        vals = {}
        if categ_id:
            category = self.pool.get('product.category').browse(cr, uid, categ_id)
            if category.cate_name == 'finish':
                vals = {'sale_ok':True,
                    'purchase_ok':False,
                    'batch_appli_ok':False,
                    'cate_name':'finish',
                    'tpt_mater_type':False,
                    }
            elif category.cate_name == 'raw':
                vals = {'sale_ok':False,
                    'purchase_ok':True,
                    'batch_appli_ok':False,
                    'cate_name':'raw',
                    'tpt_product_type':False,
                    }
            else :
                vals = {'sale_ok':False,
                    'purchase_ok':True,
                    'batch_appli_ok':False,
                    'cate_name':category.cate_name,
                    }
        return {'value': vals}  
    
    def onchange_mrp_control(self, cr, uid, ids,mrp_control=False,context=None):
        res = {'value':{}}
        if not mrp_control:
            for id in ids:
                cr.execute('update product_product set min_stock=null,max_stock=null,re_stock=null where id=%s',(id,))
            res['value'].update({
                        'min_stock':False,
                        'max_stock':False,
                        're_stock':False,
                      })
        return res 
    
    def onchange_batch_appli_ok(self, cr, uid, ids,batch_appli_ok=False,context=None):
        res = {'value':{
                        'track_production':batch_appli_ok,
                        'track_incoming':batch_appli_ok,
                        'track_outgoing':batch_appli_ok,
                      }
               }
        return res 
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('batch_appli_ok'):
            vals.update({
                        'track_production':True,
                        'track_incoming':True,
                        'track_outgoing':True,
                        })
        else:
            vals.update({
                        'track_production':False,
                        'track_incoming':False,
                        'track_outgoing':False,
                        })
        new_id = super(product_product, self).create(cr, uid, vals, context)
        return new_id
        
    def write(self, cr, uid,ids, vals, context=None):
        if 'batch_appli_ok' in vals:
            batch = vals.get('batch_appli_ok')
            if batch:
                vals.update({
                        'track_production':True,
                        'track_incoming':True,
                        'track_outgoing':True,
                        })
            else:
                vals.update({
                        'track_production':False,
                        'track_incoming':False,
                        'track_outgoing':False,
                        })
        return super(product_product, self).write(cr,uid,ids,vals,context) 
        
product_product()

class tpt_product_inventory(osv.osv):
    _name = "tpt.product.inventory"
    
    _columns = {
        'product_id':fields.many2one('product.product', 'Product', ondelete = 'cascade'),
        'warehouse_id':fields.many2one('stock.location', 'Warehouse'),
        'prodlot_id':fields.many2one('stock.production.lot', 'System Batch Number'),
        'hand_quantity' : fields.float('On hand Quantity'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure'),
        }
    
tpt_product_inventory()

class tpt_gate_in_pass(osv.osv):
    _name = "tpt.gate.in.pass"
      
    _columns = {
        'name': fields.char('Gate In Pass No', size = 1024, readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'po_id': fields.many2one('purchase.order', 'PO Number', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_id': fields.many2one('res.partner', 'Supplier', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'po_date': fields.datetime('PO Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'gate_date_time': fields.datetime('Gate In Pass Date & Time', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'gate_in_pass_line': fields.one2many('tpt.gate.in.pass.line', 'gate_in_pass_id', 'Product Details', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'truck_no':fields.text('Truck Number'),
        'invoice_no':fields.text('DC/Invoice No'),
        'requestioner_id':fields.many2one('hr.employee','Requestioner'),
              
                
                
                }
    _defaults={
               'name':'/',
               'gate_date_time': time.strftime("%Y-%m-%d %H:%M:%S"),
               'state': 'draft',
    }
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.gate.in.pass.import') or '/'
        return super(tpt_gate_in_pass, self).create(cr, uid, vals, context=context)
    
    def onchange_po_id(self, cr, uid, ids,po_id=False):
        res = {'value':{
                        'supplier_id':False,
                        'po_date':False,
                        'gate_in_pass_line':[],
                      }
               }
        if po_id:
            po = self.pool.get('purchase.order').browse(cr, uid, po_id)
            gate_in_pass_line = []
            for line in po.order_line:
                gate_in_pass_line.append({
                            'po_indent_no': po.po_indent_no and po.po_indent_no.id or False,
                          'product_id': line.product_id and line.product_id.id or False,
                          'product_qty':line.product_qty or False,
                          'uom_po_id': line.product_uom and line.product_uom.id or False,
                    })
        res['value'].update({
                    'supplier_id':po.partner_id and po.partner_id.id or False,
                    'po_date':po.date_order or False,
                    'gate_in_pass_line': gate_in_pass_line,
        })
        return res
    
tpt_gate_in_pass()

class tpt_purchase_quotation(osv.osv):
    _name = "tpt.purchase.quotation"
    
    def amount_all_quotation_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_line': 0.0,
                'amount_basic': 0.0,
                'amount_p_f': 0.0,
                'amount_ed': 0.0,
                'amount_total_tax': 0.0,
                'amount_fright': 0.0,
                'amount_gross': 0.0,
                'amount_net': 0.0,
                'amount_unit_net': 0.0,
            }
            amount_line = 0.0
            amount_basic = 0.0
            amount_p_f=0.0
            amount_ed=0.0
            amount_total_tax=0.0
            amount_fright=0.0
            amount_gross=0.0
            amount_net=0.0
            amount_unit_net=0.0
            qty = 0.0
            for quotation in line.purchase_quotation_line:
                qty += quotation.product_uom_qty
                basic = (quotation.product_uom_qty * quotation.price_unit) - ( (quotation.product_uom_qty * quotation.price_unit)*quotation.disc/100)
                amount_basic += basic
                if quotation.p_f_type == '1' :
                    p_f = basic * quotation.p_f/100
                elif quotation.p_f_type == '2' :
                    p_f = quotation.p_f
                elif quotation.p_f_type == '3' :
                    p_f = quotation.p_f * quotation.product_uom_qty
                else:
                    p_f = quotation.p_f
                amount_p_f += p_f
                if quotation.e_d_type == '1' :
                    ed = (basic + p_f) * quotation.e_d/100
                elif quotation.e_d_type == '2' :
                    ed = quotation.e_d
                elif quotation.e_d_type == '3':
                    ed = quotation.e_d *  quotation.product_uom_qty
                else:
                    ed = quotation.e_d
                amount_ed += ed
                total_tax = (basic + p_f + ed)*(quotation.tax_id and quotation.tax_id.amount or 0) / 100
                amount_total_tax += total_tax
                if quotation.fright_type == '1' :
                    fright = (basic + p_f + ed + total_tax) * quotation.fright/100
                elif quotation.fright_type == '2' :
                    fright = quotation.fright
                elif quotation.fright_type == '3' :
                    fright = quotation.fright * quotation.product_uom_qty
                else:
                     fright = quotation.fright
                amount_fright += fright
#                 amount_line +=  amount_basic + amount_p_f + quotation.e_d + amount_total_tax + amount_fright
                sql = '''
                    SELECT name FROM account_tax
                                    WHERE name LIKE '%CST%'
                '''
                cr.execute(sql)
                tax_name = cr.dictfetchone()['name']
                #if tax_name:
                if quotation.tax_id.description and 'CST' in quotation.tax_id.description:
                    amount_net = amount_basic + amount_p_f + amount_fright + amount_total_tax
                else:
                    amount_net = amount_basic + amount_p_f + amount_fright
            amount_line += amount_basic
            amount_gross = amount_line + amount_p_f + amount_ed + amount_total_tax + amount_fright
            amount_net = amount_net
            amount_unit_net = qty and amount_net/qty or 0
            res[line.id]['amount_line'] = amount_line
            res[line.id]['amount_basic'] = amount_basic
            res[line.id]['amount_p_f'] = amount_p_f
            res[line.id]['amount_ed'] = amount_ed
            res[line.id]['amount_total_tax'] = amount_total_tax
            res[line.id]['amount_fright'] = amount_fright
            res[line.id]['amount_gross'] = amount_gross
            res[line.id]['amount_net'] = amount_net
            res[line.id]['amount_unit_net'] = amount_unit_net
        return res
    
    def _get_supplier_name(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = line.supplier_id and (line.supplier_id.name + '' +(line.supplier_id.last_name or '')) or ''
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.purchase.quotation.line').browse(cr, uid, ids, context=context):
            result[line.purchase_quotation_id.id] = True
        return result.keys()
    _columns = {
        'name':fields.char('Quotation No ', size = 1024, readonly = True ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date_quotation':fields.date('Quotation Date',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'rfq_no_id':fields.many2one('tpt.request.for.quotation','RFQ No', required = True),
        'supplier_id': fields.many2one('res.partner', 'Vendor Code',required = True,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_name_id': fields.function(_get_supplier_name, type='char',string="Vendor Name"),
        'supplier_location_id': fields.many2one( 'res.country.state','Vendor Location' ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'quotation_cate':fields.selection([
                                ('single','Single Quotation'),
                                ('multiple','Multiple Quotation'),('special','Special Quotation')],'Quotation Category'),
        'quotation_ref':fields.char('Quotation Reference',size = 1024,required=True),
#         'tax_id': fields.many2one('account.tax', 'Taxes',required=True ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'purchase_quotation_line':fields.one2many('tpt.purchase.quotation.line','purchase_quotation_id','Quotation Line' ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_line': fields.function(amount_all_quotation_line, multi='sums',string='Line Amount',
                                         store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10),}, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_basic': fields.function(amount_all_quotation_line, multi='sums',string='Basic Amounts',
                                      store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_p_f': fields.function(amount_all_quotation_line, multi='sums',string='P & F charges',
                                        store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10), },
             states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_ed': fields.function(amount_all_quotation_line, multi='sums',string='Excise Duty',
                                         store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10),}, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_total_tax': fields.function(amount_all_quotation_line, multi='sums',string='Total Tax(CST/VAT)',
                                      store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_fright': fields.function(amount_all_quotation_line, multi='sums',string='Freight',
                                        store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10), },
             states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_gross': fields.function(amount_all_quotation_line, multi='sums',string='Gross Landed Cost',
                                         store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10),}, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_net': fields.function(amount_all_quotation_line, multi='sums',string='Net Landed Cost',
                                      store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_unit_net': fields.function(amount_all_quotation_line, multi='sums',string='Unit Net Landed Cost',
                                        store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit','disc','p_f','p_f_type',   
                                                                'e_d', 'e_d_type','tax_id','fright','fright_type'], 10), },
             states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        
        
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True),
        'for_basis':fields.char('For Basis',size = 1024),
        'schedule':fields.date('Delivery Schedule'),
        'comparison_chart_id':fields.many2one('tpt.comparison.chart','Comparison Chart'),
#         'payment_term_id': fields.related('supplier_id','property_supplier_payment_term',type='many2one',relation='account.payment.term', string='Payment Term'),
        'payment_term_id': fields.many2one('account.payment.term','Payment Term'),
        'select':fields.boolean('Select'),
#         'cate_char': fields.char('Cate Name', size = 1024),
        
        #TPT START - By BalamuruganPurushothaman ON 01/04/2015- FOR PO PRINT
        'freight_term':fields.selection([('To Pay','To Pay'),('Paid','Paid')],('Freight Term')),
        

        'mode_dis': fields.char('Mode Of Dispatch', size = 1024), 
        #TPT END
    }
    _defaults = {
        'state': 'draft',
        'name': '/',
        'date_quotation':fields.datetime.now,
        'quotation_cate':'multiple',
        }  
    
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_quotation_no'):
            sql = '''
                select id from tpt_purchase_quotation
                where state != 'cancel' and id not in (select quotation_no from purchase_order where state not in ('draft','cancel') and quotation_no is not null)
            '''
            cr.execute(sql)
            purchase_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',purchase_ids)]
        return super(tpt_purchase_quotation, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)

    def onchange_rfq_no_id(self, cr, uid, ids,rfq_no_id=False):
        res = {'value':{
                        'purchase_quotation_line':[],
                        'quotation_cate':False,
                      }
               }
        if rfq_no_id:
            rfq = self.pool.get('tpt.request.for.quotation').browse(cr, uid, rfq_no_id)
            rfq_no_line = []
            for line in rfq.rfq_line:
                rfq_no_line.append({
                            'po_indent_id': line.po_indent_id and line.po_indent_id.id or False,
                            'product_id': line.indent_line_id.product_id and line.indent_line_id.product_id.id or False,
                            'product_uom_qty':line.product_uom_qty or False,
                            'uom_id': line.uom_id and line.uom_id.id or False,
                            'price_unit':line.indent_line_id.product_id and line.indent_line_id.product_id.standard_price or False,
                            'description':line.description or False,
                            'item_text':line.item_text or False,
                    })
            if rfq.rfq_category == 'single':
                res['value'].update({
                    'quotation_cate': 'single',
                    })
            elif rfq.rfq_category == 'multiple':
                res['value'].update({
                    'quotation_cate': 'multiple',
                    })
            elif rfq.rfq_category == 'special':
                res['value'].update({
                    'quotation_cate': 'special',
                    })
        res['value'].update({
                    'purchase_quotation_line': rfq_no_line,
        })
        return res
    
#     def onchange_rfq_no_id(self, cr, uid, ids,rfq_no_id=False):
#         res = {}
#         rfq_no_line = []
#         if rfq_no_id:
#             for quotation in self.browse(cr, uid, ids):
#                 sql = '''
#                     delete from tpt_purchase_quotation_line where purchase_quotation_id = %s
#                 '''%(quotation.id)
#                 cr.execute(sql)
#             rfq = self.pool.get('tpt.request.for.quotation').browse(cr, uid, rfq_no_id)
#             rfq_no_line = []
# #             if product_id:
# #                 product = self.pool.get('product.product').browse(cr, uid, product_id)
#             
#             for line in rfq.rfq_line:
#                 rfq_no_line.append((0,0,{
#                             'po_indent_id': line.po_indent_id and line.po_indent_id.id or False,
#                             'product_id': line.product_id and line.product_id.id or False,
#                             'product_uom_qty':line.product_uom_qty or False,
#                             'uom_id': line.uom_id and line.uom_id.id or False,
#                             'price_unit':line.product_id and line.product_id.standard_price or False,
#                     }))
#         return {'value': {'purchase_quotation_line': rfq_no_line}}
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.quotation') or '/'
        if 'rfq_no_id' in vals:
            cate = self.pool.get('tpt.request.for.quotation').browse(cr, uid, vals['rfq_no_id'])
            vals.update({
                         'quotation_cate':cate.rfq_category,
                         })
        new_id = super(tpt_purchase_quotation, self).create(cr, uid, vals, context)
        if 'rfq_no_id' in vals and vals['rfq_no_id']:
            rfq = self.pool.get('tpt.request.for.quotation').browse(cr,uid,vals['rfq_no_id'])
            for vendor in rfq.rfq_supplier:
                sql = '''
                    select id from tpt_purchase_quotation where rfq_no_id = %s and supplier_id  = %s
                '''%(rfq.id, vendor.vendor_id.id)
                cr.execute(sql)
                rfquotation_ids = [r[0] for r in cr.fetchall()]
                if rfquotation_ids:
                    for rfquotation_id in rfquotation_ids:
                        quotation_id = self.browse(cr,uid,rfquotation_id)
                        sql = '''
                            update tpt_rfq_supplier set quotation_no_id = %s where vendor_id = %s and rfq_id in (select id from tpt_request_for_quotation where id = %s)
                        '''%(quotation_id.id, quotation_id.supplier_id.id, quotation_id.rfq_no_id.id)
                        cr.execute(sql)
        
#Hung them khi tao Quotation thi cap nhat lai trang thai cua PO indent
        quotation = self.browse(cr,uid,new_id)
        sql = '''
            select id from tpt_request_for_quotation where id = %s
        '''%(quotation.rfq_no_id.id)
        cr.execute(sql)
        rfq_ids = [r[0] for r in cr.fetchall()]
        if rfq_ids:
            self.pool.get('tpt.request.for.quotation').write(cr,uid,rfq_ids,{
                                                                         'raised_ok': True
                                                                         })
        
        for rfq_line in quotation.purchase_quotation_line:
            sql = '''
                select id from tpt_purchase_product where pur_product_id=%s and product_id=%s
                
                '''%(rfq_line.po_indent_id.id,rfq_line.product_id.id)
            cr.execute(sql)
            indent_line_ids = [row[0] for row in cr.fetchall()]
            if indent_line_ids:
                self.pool.get('tpt.purchase.product').write(cr, uid, indent_line_ids,{'state':'quotation_raised'})
        return new_id  
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'rfq_no_id' in vals:
            cate = self.pool.get('tpt.request.for.quotation').browse(cr, uid, vals['rfq_no_id'])
            vals.update({
                         'quotation_cate':cate.rfq_category,
                         })
        new_write = super(tpt_purchase_quotation, self).write(cr, uid,ids, vals, context)
        for quotation in self.browse(cr,uid,ids):
            for line in quotation.purchase_quotation_line:
                if 'state' in vals and vals['state']=='cancel':
                    sql = '''
                        update tpt_purchase_product set state='quotation_cancel' where pur_product_id=%s and product_id=%s
                    '''%(line.po_indent_id.id,line.product_id.id)
                    cr.execute(sql)
            sql = '''
                select id from tpt_request_for_quotation where id = %s
            '''%(quotation.rfq_no_id.id)
            cr.execute(sql)
            rfq_ids = [r[0] for r in cr.fetchall()]
            if rfq_ids:
                self.pool.get('tpt.request.for.quotation').write(cr,uid,rfq_ids,{
                                                                         'raised_ok': True
                                                                         })
        return new_write    
    
    
    def onchange_supplier_location(self, cr, uid, ids,supplier_id=False, context=None):
        vals = {}
        if supplier_id :
            supplier = self.pool.get('res.partner').browse(cr, uid, supplier_id)
            vals = {
                    'supplier_location_id':supplier.state_id and supplier.state_id.id or False,
                    'supplier_name_id': supplier.name + '' +(supplier.last_name or ''),
                    }
        return {'value': vals}
    
    def bt_tick_mark(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'tick_purchase_chart_form_view')
        return {
                    'name': 'Purchase Chart',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tick.purchase.chart',
                    'domain': [],
                    'context': {'default_message':'Do you want to confirm the Quotation to Purchase order?'},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }

    def bt_cross_mark(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            po_ids = self.pool.get('purchase.order').search(cr,uid,[('quotation_no','=',line.id)])
            if po_ids:
                raise osv.except_osv(_('Warning!'),_('Quotation was existed at the Purchase Order.!'))
            self.write(cr, uid, ids,{'state':'cancel','comparison_chart_id':False})
        return True

#     def bt_approve(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids):
#             self.write(cr, uid, ids,{'state':'done'})
#         return True   
#     
    def bt_copy_quote(self, cr, uid, ids, context=None):
        default = {'quotation_cate':'single','name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.quotation') or '/'}
        new_id = self.copy(cr, uid, ids[0],default)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_tpt_purchase_quotation_form')
        return {
                    'name': 'Quotation',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.purchase.quotation',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id':new_id,
                } 


   
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('check_supplier_location_id'):
#             supplier_id = context.get('supplier_id')8754
#             if not supplier_id:
#                 args += [('id','=',-1)]
#                 
#         return super(tpt_purchase_quotation, self).search(cr, uid, args, offset, limit, order, context, count)    

tpt_purchase_quotation()

class tpt_purchase_quotation_line(osv.osv):
    _name = "tpt.purchase.quotation.line"
    
    def line_net_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        amount_basic = 0.0
        amount_p_f=0.0
        amount_ed=0.0
        amount_total_tax=0.0
        amount_fright=0.0
        
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                    'line_net': 0.0,
                }  
            amount_basic = (line.product_uom_qty * line.price_unit)-((line.product_uom_qty * line.price_unit)*line.disc/100)
            if line.p_f_type == '1':
               amount_p_f = amount_basic * (line.p_f/100)
            elif line.p_f_type == '2':
                amount_p_f = line.p_f
            elif line.p_f_type == '3':
                amount_p_f = line.p_f * line.product_uom_qty
            else:
                amount_p_f = line.p_f
            if line.e_d_type == '1':
               amount_ed = (amount_basic + amount_p_f) * (line.e_d/100)
            elif line.e_d_type == '2':
                amount_ed = line.e_d
            elif line.p_f_type == '3':
                amount_ed = line.e_d * line.product_uom_qty
            else:
                amount_ed = line.e_d
            if line.fright_type == '1':
               amount_fright = (amount_basic + amount_p_f + amount_ed) * (line.fright/100)
            elif line.fright_type == '2':
                amount_fright = line.fright
            elif line.fright_type == '3':
                amount_fright = line.fright * line.product_uom_qty
            else:
                amount_fright = line.fright
#             if 
            amount_total_tax = line.tax_id and line.tax_id.amount/100 or 0
            line_net = amount_total_tax+amount_fright+amount_ed+amount_p_f+amount_basic
            res[line.id]['line_net'] = line_net
        return res
    
    _columns = {
        'purchase_quotation_id':fields.many2one('tpt.purchase.quotation','Purchase Quotitation', ondelete = 'cascade'),
        'po_indent_id':fields.many2one('tpt.purchase.indent','Indent No', readonly = True),
        'product_id': fields.many2one('product.product', 'Material Name',readonly = True),
        'product_uom_qty': fields.float('Qty', readonly = True),   
        'uom_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'price_unit': fields.float('Unit Price', required=True),
        'disc': fields.float('Disc'),
        'p_f': fields.float('P&F'),
        'p_f_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('P&F Type')),
        'e_d': fields.float('ED'),
        'e_d_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('ED Type')),
        'tax_id': fields.many2one('account.tax', 'Taxes',required = True),
        'fright': fields.float('Frt'),
        'fright_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('Frt Type')),
        'line_net': fields.function(line_net_line, store = True, multi='deltas' ,string='SubTotal'),
        'line_no': fields.integer('SI.No', readonly = True),
        'order_charge': fields.float('Other Charges'),
        'description':fields.char('Mat.Desc', size = 50, readonly = True),
        #TPT
        'item_text': fields.char('Item Text'), 
        }
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('purchase_quotation_id','=',line.purchase_quotation_id.id),('line_no','>',line.line_no)])
            if update_ids:
                cr.execute("UPDATE tpt_purchase_quotation_line SET line_no=line_no-1 WHERE id in %s",(tuple(update_ids),))
        return super(tpt_purchase_quotation_line, self).unlink(cr, uid, ids, context)  
    
    def create(self, cr, uid, vals, context=None):
        if 'price_unit' in vals:
            if (vals['price_unit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Price Unit is not allowed as negative values'))
        if 'disc' in vals:
            if (vals['disc'] < 0):
                raise osv.except_osv(_('Warning!'),_('Disc is not allowed as negative values'))
        if 'p_f' in vals:
            if (vals['p_f'] < 0):
                raise osv.except_osv(_('Warning!'),_('PF is not allowed as negative values'))
        if 'e_d' in vals:
            if (vals['e_d'] < 0):
                raise osv.except_osv(_('Warning!'),_('ED is not allowed as negative values'))
        if 'fright' in vals:
            if (vals['fright'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not allowed as negative values'))
        if 'order_charge' in vals:
            if (vals['order_charge'] < 0):
                raise osv.except_osv(_('Warning!'),_('Other Charge is not allowed as negative values'))
        if vals.get('purchase_quotation_id',False):
            vals['line_no'] = len(self.search(cr, uid,[('purchase_quotation_id', '=', vals['purchase_quotation_id'])])) + 1
        if 'po_indent_id' in vals:
            if 'product_id' in vals:
                indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, vals['po_indent_id'])
                for line in indent.purchase_product_line:
                    if vals['product_id'] == line.product_id.id:
                        vals.update({
#                                 'uom_po_id':line.uom_po_id.id,
#                                 'product_uom_qty':line.product_uom_qty,
                                })
        
        return super(tpt_purchase_quotation_line, self).create(cr, uid, vals, context)    
  
    def write(self, cr, uid,ids, vals, context=None):
        if 'price_unit' in vals:
            if (vals['price_unit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Price Unit is not allowed as negative values'))
        if 'disc' in vals:
            if (vals['disc'] < 0):
                raise osv.except_osv(_('Warning!'),_('Disc is not allowed as negative values'))
        if 'p_f' in vals:
            if (vals['p_f'] < 0):
                raise osv.except_osv(_('Warning!'),_('PF is not allowed as negative values'))
        if 'e_d' in vals:
            if (vals['e_d'] < 0):
                raise osv.except_osv(_('Warning!'),_('ED is not allowed as negative values'))
        if 'fright' in vals:
            if (vals['fright'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not allowed as negative values'))
        if 'order_charge' in vals:
            if (vals['order_charge'] < 0):
                raise osv.except_osv(_('Warning!'),_('Other Charge is not allowed as negative values'))
        if 'po_indent_id' in vals:
            if 'product_id' in vals:
                indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, vals['po_indent_id'])
                for line in indent.purchase_product_line:
                    if vals['product_id'] == line.product_id.id:
                        vals.update({
#                                 'uom_po_id':line.uom_po_id.id,
#                                 'product_uom_qty':line.product_uom_qty,
                                })
        return super(tpt_purchase_quotation_line, self).write(cr, uid,ids, vals, context)    
    
    def onchange_po_indent_id(self, cr, uid, ids,po_indent_id=False, context=None):
        if po_indent_id:
            return {'value': {'product_id': False}}    
    
    def onchange_quotation_product_id(self, cr, uid, ids,product_id=False, po_indent_id=False, context=None):
        vals = {}
        if po_indent_id and product_id: 
            indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_id)
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            for line in indent.purchase_product_line:
                if product_id == line.product_id.id:
                    vals = {
                            'price_unit':product.standard_price,
                            'uom_po_id':line.uom_po_id and line.uom_po_id.id or False,
                            'product_uom_qty':line.product_uom_qty or False,
                            }
        return {'value': vals}   



#     def _check_quotation(self, cr, uid, ids, context=None):
#         for quotation in self.browse(cr, uid, ids, context=context):
#             quotation_ids = self.search(cr, uid, [('id','!=',quotation.id),('po_indent_id','=',quotation.po_indent_id.id),('product_id', '=',quotation.product_id.id),('purchase_quotation_id','=',quotation.purchase_quotation_id.id)])
#             if quotation_ids:
#                 raise osv.except_osv(_('Warning!'),_('PO Indent and Product were existed !'))
#                 return False
#             return True
#         
#     _constraints = [
#         (_check_quotation, 'Identical Data', ['po_indent_id', 'product_id']),
#     ]       
    
tpt_purchase_quotation_line()

class tpt_comparison_chart(osv.osv):
    _name = "tpt.comparison.chart"
      
    _columns = {
        'name':fields.many2one('tpt.request.for.quotation','RFQ No', required = True),
        'date':fields.date('Create Date', size = 1024,required=True),
        'quotation_cate':fields.selection([
                                  ('multiple','Multiple Quotation')],'Quotation Category'),
        'create_uid':fields.many2one('res.users','Created By'),
        'comparison_chart_line':fields.one2many('tpt.purchase.quotation','comparison_chart_id','Line')
                }
    
    def onchange_request_quotation(self, cr, uid, ids,name=False, context=None):
        vals = {}
        if name :
            quotation_ids = self.pool.get('tpt.purchase.quotation').search(cr, uid, [('rfq_no_id','=',name),('state','=','draft')])
            vals = {'comparison_chart_line':[(6,0,quotation_ids)]}
        return {'value': vals}

    def create(self, cr, uid, vals, context=None):
        if vals.get('name',False):
#             quotation_ids = self.pool.get('tpt.purchase.quotation').search(cr, uid, [('rfq_no_id','=',vals['name']),('state','=','draft')])
            sql = '''
                select id from tpt_purchase_quotation where rfq_no_id = %s and state = 'draft' order by amount_net 
            '''%(vals['name'])
            cr.execute(sql)
            quotation_ids = [r[0] for r in cr.fetchall()]
            vals.update({'comparison_chart_line':[(6,0,quotation_ids)]})
        return super(tpt_comparison_chart, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid,ids, vals, context=None):
        if vals.get('name',False):
#             quotation_ids = self.pool.get('tpt.purchase.quotation').search(cr, uid, [('rfq_no_id','=',vals['name']),('state','=','draft')])
            sql = '''
                select id from tpt_purchase_quotation where rfq_no_id = %s and state = 'draft' order by amount_net 
            '''%(vals['name'])
            cr.execute(sql)
            quotation_ids = [r[0] for r in cr.fetchall()]
            vals.update({'comparison_chart_line':[(6,0,quotation_ids)]})
        return super(tpt_comparison_chart, self).write(cr, uid,ids, vals, context=context)

    def bt_load(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
#             quotation_ids = self.pool.get('tpt.purchase.quotation').search(cr, uid, [('rfq_no_id','=',line.name.id),('state','=','draft')])
            sql = '''
                select * from tpt_purchase_quotation where rfq_no_id = %s  order by amount_net 
            '''%(line.name.id)
            cr.execute(sql)
            quotation_ids = [r[0] for r in cr.fetchall()]
            vals={'comparison_chart_line':[(6,0,quotation_ids)]}
            self.write(cr, uid,[line.id], vals, context=context)
        return True
    
    def get_loo_file_name(self, cr, uid, id, name_report, context={}):
        chart_obj = self.browse(cr, uid, id, context)
        chart_name = chart_obj.name.name or ''
        file_name = name_report + ' ' + chart_name
        return file_name

    def get_report_file_name(self, cr, uid, id, report_name, context={}):
        res = {}
#         res = super(tpt_comparison_chart,self).get_report_file_name(cr, uid, id, report_name, context=context)
        report_xml_pool = self.pool.get('ir.actions.report.xml')
        report_ids = report_xml_pool.search(cr, uid, [('report_name','=',report_name)])
        name_report = report_name
        if report_ids:
            name_report = report_xml_pool.browse(cr, uid, report_ids[0]).name
#             res = super(tpt_comparison_chart,self).get_report_file_name(cr, uid, id, report_name, context=context)
        if res:
            return res
        else:
            return {
                'tpt_comparison_chart' : self.get_loo_file_name,
            }[report_name](cr, uid, id, name_report, context) 


    def bt_print(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        sql = '''
            select case when count(*)!=0 then count(*) else 0 end total_select from tpt_purchase_quotation where comparison_chart_id = %s and tpt_purchase_quotation.select = 'True'
        '''%(ids[0])
        cr.execute(sql)
        total_select=cr.dictfetchone()['total_select']
        if total_select > 4:
            raise osv.except_osv(_('Warning!'),_('Should not choose more than 4 lines from Quotation !'))
        datas = {
             'ids': ids,
             'model': 'tpt.comparison.chart',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tpt_comparison_chart',
        }

tpt_comparison_chart()

class tpt_gate_in_pass_line(osv.osv):
    _name = "tpt.gate.in.pass.line"
    _columns = {
        'gate_in_pass_id': fields.many2one('tpt.gate.in.pass','Gate In Pass',ondelete = 'cascade'),
        'po_indent_no': fields.many2one('tpt.purchase.indent', 'PO Indent No'),
        'product_id': fields.many2one('product.product', 'Material'),
        'product_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
        'description':fields.char('Mat. Description', size = 50),
                }
    _defaults={
               'product_qty': 1,
    }
    
    def create(self, cr, uid, vals, context=None):
        
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id,'description':product.name})
        new_id = super(tpt_gate_in_pass_line, self).create(cr, uid, vals, context)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id,'description':product.name})
        new_write = super(tpt_gate_in_pass_line, self).write(cr, uid,ids, vals, context)
        return new_write
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'uom_po_id':product.uom_id.id,
                    'description': product.name,
                    }
        return {'value': vals}
      
tpt_gate_in_pass_line()

class tpt_spec_parameters_line(osv.osv):
    _name = "tpt.spec.parameters.line"
    _columns = {
        'product_id': fields.many2one('product.product','Product',ondelete = 'cascade'),
        'name': fields.many2one('tpt.quality.parameters','Testing Parameters',required=True,ondelete='restrict'),
        'required_spec': fields.float('Required Specifications'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
                }
      
tpt_spec_parameters_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def amount_all_po_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'p_f_charge': 0.0,
                'excise_duty': 0.0,
                'amount_tax': 0.0,
                'fright': 0.0,
            }
            amount_untaxed = 0.0
            p_f_charge=0.0
            excise_duty=0.0
            amount_total_tax=0.0
            total_tax = 0.0
            amount_fright=0.0
            qty = 0.0
            for po in line.order_line:
                tax = 0
                qty += po.product_qty
                basic = (po.product_qty * po.price_unit) - ( (po.product_qty * po.price_unit)*po.discount/100)
                amount_untaxed += basic
                if po.p_f_type == '1' :
                    p_f = basic * po.p_f/100
                elif po.p_f_type == '2' :
                    p_f = po.p_f
                elif po.p_f_type == '3':
                    p_f = po.p_f * po.product_qty
                else:
                    p_f = po.p_f
                p_f_charge += p_f
                if po.ed_type == '1' :
                    ed = (basic + p_f) * po.ed/100
                elif po.ed_type == '2' :
                    ed = po.ed
                elif po.ed_type == '3' :
                    ed = po.ed *  po.product_qty
                else:
                    ed = po.ed
                excise_duty += ed
                if po.fright_type == '1' :
                    fright = (basic + p_f + ed + amount_total_tax) * po.fright/100
                elif po.fright_type == '2' :
                    fright = po.fright
                elif po.fright_type == '3' :
                    fright = po.fright * po.product_qty
                else:
                    fright = po.fright
                amount_fright += fright
                tax_amounts = [r.amount for r in po.taxes_id]
                for tax_amount in tax_amounts:
                    tax += tax_amount/100
#                 amount_total_tax += basic*tax
                #TPT-COMMENTED & ADDED BY BalamuruganPurushothaman ON 07/04/2015 - TO BLOCK FREIGHT AMT TO BE ADDED IN TAX CALCULATION
                #amount_total_tax = (basic + p_f + ed + fright )*(tax) #Trong them + frieght vao ham tinh Tax
                amount_total_tax = (basic + p_f + ed)*(tax) #TPT-HERE fright IS REMOVED
                total_tax += amount_total_tax
                
            res[line.id]['amount_untaxed'] = amount_untaxed
            res[line.id]['p_f_charge'] = p_f_charge
            res[line.id]['excise_duty'] = excise_duty
            res[line.id]['amount_tax'] = total_tax
            res[line.id]['fright'] = amount_fright
            res[line.id]['amount_total'] = amount_untaxed+p_f_charge+excise_duty+total_tax+amount_fright
        return res
    
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    _columns = {
        'po_document_type':fields.selection([('raw','VV Raw material PO'),('asset','VV Capital PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'PO Document Type', required = True, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        'quotation_no': fields.many2one('tpt.purchase.quotation', 'Quotation No', required = True, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
#         'po_indent_no' : fields.many2one('tpt.purchase.indent', 'PO Indent No', required = True, track_visibility='onchange'),
        'partner_ref': fields.char('Quotation Reference', states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}, size=64,
            help="Reference of the sales order or quotation sent by your supplier. It's mainly used to do the matching when you receive the products as this reference is usually written on the delivery order sent by your supplier.", track_visibility='onchange'),
        'state_id': fields.many2one('res.country.state', 'Vendor Location', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        'for_basis': fields.char('For Basis', size = 1024, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        'mode_dis': fields.char('Mode Of Dispatch', size = 1024, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        'date_order':fields.date('Order Date', required=True, states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}, select=True, help="Date on which this document has been created.", track_visibility='onchange',),
        'ecc_no': fields.char('ECC No', size = 1024, track_visibility='onchange'),
        'payment_term_id': fields.many2one('account.payment.term', 'Payment Term', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        #'deli_sche': fields.char('Delivery Schedule', size = 1024, track_visibility='onchange'),
        'deli_sche':fields.date('Delivery Schedule', states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}, select=True, help="Date on which this document has been Scheduled to Dispatch.", track_visibility='onchange'),
        'partner_id':fields.many2one('res.partner', 'Supplier', required=True, states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]},
            change_default=True, track_visibility='always'),
        'company_id': fields.many2one('res.company','Company',required=True,select=1, states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}, track_visibility='onchange'),
        'reason': fields.text('Reason', size = 1024, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),        
        
        
        #ham function
        
        'amount_untaxed': fields.function(amount_all_po_line, multi='sums', string='Untaxed Amount',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),   
                'purchase.order.line': (_get_order, ['product_qty', 'product_uom', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','taxes_id','fright','fright_type'], 10)}),
                
        'p_f_charge': fields.function(amount_all_po_line, multi='sums',string='P & F charges',
                                        store={
               'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),   
            'purchase.order.line': (_get_order, ['product_qty', 'product_uom', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','taxes_id','fright','fright_type'], 10)}),
         'excise_duty': fields.function(amount_all_po_line, multi='sums',string='Excise Duty',
                                        store={
               'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),   
            'purchase.order.line': (_get_order, ['product_qty', 'product_uom', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','taxes_id','fright','fright_type'], 10)}),  
        'fright': fields.function(amount_all_po_line, multi='sums',string='Freight',
                                        store={
               'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),   
            'purchase.order.line': (_get_order, ['product_qty', 'product_uom', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','taxes_id','fright','fright_type'], 10)}), 
                
        'amount_tax': fields.function(amount_all_po_line, string='Taxes',
            store={
                'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),   
            'purchase.order.line': (_get_order, ['product_qty', 'product_uom', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','taxes_id','fright','fright_type'], 10) 
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(amount_all_po_line, string='Total',
            store={
               'purchase.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),   
            'purchase.order.line': (_get_order, ['product_qty', 'product_uom', 'price_unit','discount','p_f','p_f_type',   
                                                                'ed', 'ed_type','taxes_id','fright','fright_type'], 10) 
            }, multi="sums",help="The total amount"),
        'state': fields.selection([
                                   ('draft', 'Draft PO'),
                                    ('sent', 'RFQ Sent'),
                                    ('amendement', 'Amendement'),
                                    ('head', 'Purchase Head Approved'),
                                    ('gm', 'GM Approval'),
                                    ('md', 'Ready For GRN'),
                                    ('confirmed', 'Waiting Approval'),
                                    ('approved', 'Purchase Order'),
                                    ('except_picking', 'Shipping Exception'),
                                    ('except_invoice', 'Invoice Exception'),
                                    ('done', 'Done'),
                                    ('cancel', 'Cancelled'),
                                   ], 'Status', required=True, readonly=True,
                                  ),
        'check_amendement':fields.boolean("Amended",readonly=True),
        'order_line': fields.one2many('purchase.order.line', 'order_id', 'Order Lines', states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
        
        #TPT START By BalamuruganPurushothaman ON 01/04/2015 - FOR PO PRINT
        'freight_term':fields.selection([('To Pay','To Pay'),('Paid','Paid')],('Freight Term'),states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)],'md':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),   
        #'quotation_ref':fields.char('Quotation Reference',size = 1024,required=True),
        #TPT END
        }
    
    _default = {
        'name':'/',
        'check_amendement':False,
               }
    def action_amendement(self, cr, uid, ids, context=None):
        for purchase in self.browse(cr,uid,ids):
            self.write(cr, uid, ids,{'state':'amendement','check_amendement':True}) 
            order_obj = self.pool.get('purchase.order.line')
            sql = '''
                select id from purchase_order_line where order_id = %s
            '''%(purchase.id)
            cr.execute(sql)
            purchase_ids = [r[0] for r in cr.fetchall()]
            order_obj.write(cr, uid, purchase_ids,{'state':'amendement'})
        
        return True
    
    def action_gm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'gm'})
    
    def action_md(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'md'})
    
    #TPT-PO PRINT ON 4/4/2015
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the request for quotation and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'purchase.order',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        invoice_ids = self.browse(cr, uid, ids[0])  
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'tpt_purchase_order',
                 'datas': datas,
#                 'nodestroy' : True
                }
        #TPT ENDss
    
    def action_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for purchase in self.browse(cr, uid, ids, context=context):
            for pick in purchase.picking_ids:
                if pick.state in ('done'):
                    raise osv.except_osv(
                        _('Unable to cancel this purchase order.'),
                        _('First cancel all receptions related to this purchase order.'))
            for pick in purchase.picking_ids:
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_cancel', cr)
            for inv in purchase.invoice_ids:
                if inv and inv.state not in ('cancel','draft'):
                    raise osv.except_osv(
                        _('Unable to cancel this purchase order.'),
                        _('You must first cancel all receptions related to this purchase order.'))
                if inv:
                    wf_service.trg_validate(uid, 'account.invoice', inv.id, 'invoice_cancel', cr)
        self.write(cr,uid,ids,{'state':'cancel'})

        for (id, name) in self.name_get(cr, uid, ids):
            wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_cancel', cr)
        return True
   
    def onchange_quotation_no(self, cr, uid, ids,quotation_no=False, context=None):
        vals = {}
        if quotation_no:
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from purchase_order_line where order_id = %s
                '''%(line.id)
                cr.execute(sql)
        po_line = []
        if quotation_no:
            quotation = self.pool.get('tpt.purchase.quotation').browse(cr, uid, quotation_no)
            for line in quotation.purchase_quotation_line:
                rs = {
                      'po_indent_no': line.po_indent_id and line.po_indent_id.id or False,
                      'product_id': line.product_id and line.product_id.id or False,
                      'product_qty': line.product_uom_qty or False,
                      'product_uom': line.uom_id and line.uom_id.id or False,
                      'price_unit': line.price_unit or False,
                      'discount': line.disc or False,
                      'p_f': line.p_f or False,
                      'p_f_type':line.p_f_type or False,
                      'ed':line.e_d or False,
                      'ed_type':line.e_d_type or False,
                      'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
                      'fright':line.fright or False,
                      'fright_type':line.fright_type or False,
                
#                       'price_subtotal': line.sub_total or False,
#                       'date_planned':quotation.date_quotation or False,
                      'name': line.product_id and line.product_id.name or False,
                      'description':line.description or False,
                      }
                po_line.append((0,0,rs))
            vals = {
                    'partner_id':quotation.supplier_id and quotation.supplier_id.id or '',
                    'for_basis':quotation.for_basis or '',
                    'state_id':quotation.supplier_location_id and quotation.supplier_location_id.id or '',
                    'deli_sche': quotation.schedule or '',
                    #TPT
                    
                    'mode_dis': quotation.mode_dis or '',
                    'freight_term': quotation.freight_term or '',
                    #'quotation_ref': quotation.quotation_ref or '',
                    
                    'for_basis': quotation.for_basis or '',
                    'deli_sche': quotation.schedule or '',
                    'payment_term_id':quotation.payment_term_id and quotation.payment_term_id.id or '',
#                     'po_indent_no': False,
                    'order_line': po_line,
                    }
        return {'value': vals}
    
    def onchange_po_indent_no(self, cr, uid, ids,quotation_no=False, po_indent_no=False, context=None):
        vals = {}
        po_line = []
        if po_indent_no and not quotation_no:
            indent_lines = []
#             indent_ids = []
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from purchase_order_line where order_id = %s
                '''%(line.id)
                cr.execute(sql)
            indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_no)
#             indent_ids = self.pool.get('tpt.purchase.indent').search(cr, uid, [('intdent_cate','=','emergency'),('state', '=', 'draft')])
            for indent_line in indent.purchase_product_line:
                rs = {
                      'product_id': indent_line.product_id and indent_line.product_id.id or False,
                      'product_qty': indent_line.product_uom_qty or False,
                      'product_uom': indent_line.uom_po_id and indent_line.uom_po_id.id or False,
                      'name': '/',
                      }
                indent_lines.append((0,0,rs))
            return {'value':{'order_line': indent_lines}}
        if quotation_no and po_indent_no:
            for indent in self.browse(cr, uid, ids):
                sql = '''
                    delete from purchase_order_line where order_id = %s
                '''%(indent.id)
                cr.execute(sql)
                
            quotation = self.pool.get('tpt.purchase.quotation').browse(cr, uid, quotation_no)
            for line in quotation.purchase_quotation_line:
                if po_indent_no==line.po_indent_id.id:
                    sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from purchase_order_line where order_id in (select id from purchase_order where po_indent_no=%s and state!='cancel')
                    '''%(line.po_indent_id.id)
                    cr.execute(sql)
                    product_qty = cr.dictfetchone()['product_qty']
                    rs = {
                          'product_id': line.product_id and line.product_id.id or False,
                          'product_qty': line.product_uom_qty-product_qty or False,
                          'product_uom': line.uom_id and line.uom_id.id or False,
                          'price_unit': line.price_unit or False,
                          'discount': line.disc or False,
                          'p_f': line.p_f or False,
                          'p_f_type': line.p_f_type or False,
                          'ed': line.e_d or False,
                          'ed_type': line.e_d_type or False,
                          'fright': line.fright or False,
                          'fright_type': line.fright_type or False,
                          'line_net': line.line_net or False,
                          'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
#                           'price_subtotal': line.sub_total or False,
                          'date_planned':quotation.date_quotation or False,
                          'name':'/'
                          }
                    po_line.append((0,0,rs))
#             for line in quotation.purchase_quotation_line:
#                 if po_indent_no==line.po_indent_id.id:
#                     rs = {
#                           'product_id': line.product_id and line.product_id.id or False,
#                           'product_qty': line.product_uom_qty or False,
#                           'product_uom': line.uom_id and line.uom_id.id or False,
#                           'price_unit': line.price_unit or False,
#                           'discount': line.disc or False,
#                           'p_f': line.p_f or False,
#                           'p_f_type': line.p_f_type or False,
#                           'ed': line.e_d or False,
#                           'ed_type': line.e_d_type or False,
#                           'fright': line.fright or False,
#                           'fright_type': line.fright_type or False,
#                           'line_net': line.line_net or False,
#                           'taxes_id': [(6,0,[line.tax_id and line.tax_id.id])],
# #                           'price_subtotal': line.sub_total or False,
#                           'date_planned':quotation.date_quotation or False,
#                           'name':'/'
#                           }
#                     po_line.append((0,0,rs))
            vals = {
                    'partner_id':quotation.supplier_id and quotation.supplier_id.id or '',
                    'partner_ref':quotation.quotation_ref or '',
                    'p_f_charge': quotation.amount_p_f or '',
                    'excise_duty': quotation.amount_ed or '',
                    'fright': quotation.amount_fright or '',
                    
                    'mode_dis': quotation.mode_dis or '',
                    'freight_term': quotation.freight_term or '',
                    
                    'for_basis': quotation.for_basis or '',
                    'deli_sche': quotation.schedule or '',
                    'payment_term_id':quotation.payment_term_id and quotation.payment_term_id.id or '',
                    #'quotation_ref': quotation.quotation_ref or '',
#                     'amount_untaxed': quotation.amount_basic or '',
#                     'amount_tax': quotation.amount_total_tax or '',
                    'order_line': po_line,
                    }
            pur_int = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_no)
            if pur_int.document_type == 'service':
                vals['po_document_type'] = 'service'
            return {'value': vals}
    def create(self, cr, uid, vals, context=None):
        new_id = super(purchase_order, self).create(cr, uid, vals, context)
        new = self.browse(cr, uid, new_id)
        sql = '''
            select code from account_fiscalyear where '%s' between date_start and date_stop
        '''%(time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        if (new.po_document_type=='asset'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.asset')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        if (new.po_document_type=='standard'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.standard')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        if (new.po_document_type=='local'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.local')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        if (new.po_document_type=='return'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.return')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        if (new.po_document_type=='service'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.service')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        if (new.po_document_type=='out'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.out.service')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        if (new.po_document_type=='raw'):
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.raw.material')
            sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new_id)
            cr.execute(sql)
        #Hung sua khi tao PO se cap nhat lai trang thai cua PO indent la po_raised
#         self.pool.get('tpt.purchase.indent').write(cr, uid, [new.po_indent_no.id],{'state':'done'})
#         if new.quotation_no and new.po_indent_no:
#             quotation = self.pool.get('tpt.purchase.quotation').browse(cr, uid, new.quotation_no)
#             
#             sql = '''
#                 select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_po from purchase_order_line where order_id in (select id from purchase_order where po_indent_no=%s and state!='cancel')
#             '''%(new.po_indent_no.id)
#             cr.execute(sql)
#             product_qty_po = cr.dictfetchone()['product_qty_po']
#             sql = '''
#                 select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_qty_quotation from tpt_purchase_quotation_line where po_indent_id = %s
#             '''%(new.po_indent_no.id)
#             cr.execute(sql)
#             product_qty_quotation = cr.dictfetchone()['product_qty_quotation']
#             if product_qty_po==product_qty_quotation:
#                 sql = '''
#                     update tpt_purchase_indent set state = 'cancel' where id=%s 
#                 '''%(new.po_indent_no.id)
#                 cr.execute(sql)
            
#         if not new.quotation_no and new.po_indent_no:    
#             date_order = datetime.datetime.strptime(new.date_order,'%Y-%m-%d')
#             date_order_month = date_order.month
#             date_order_year = date_order.year
#             sql = '''
#                     select sum(amount_total) as total from purchase_order where EXTRACT(month from date_order) = %s and EXTRACT(year from date_order) = %s
#             '''%(date_order_month,date_order_year)
#             cr.execute(sql)
#             amount_total = cr.dictfetchone()
#             if (amount_total['total'] > 200000):
#                 raise osv.except_osv(_('Warning!'),_('You are confirm %s the Emergency Purchase reaches 2 Lakhs Limit (2,00,000) in the current month. This can be processed only when the next month starts'%(amount_total['total'])))
#             sql = '''
#                             select product_id, sum(product_qty) as po_product_qty from purchase_order_line where order_id = %s group by product_id
#                         '''%(new.id)
#             cr.execute(sql)
#             for purchase_line in cr.dictfetchall():
#                 sql = '''
#                         select case when sum(product_uom_qty) <%s then 1 else 0 end indent_product_qty 
#                         from tpt_purchase_product
#                         where product_id=%s and purchase_indent_id in (select id from tpt_purchase_indent where id = %s)
#                     '''%(purchase_line['po_product_qty'], purchase_line['product_id'], new.po_indent_no.id)
#                 cr.execute(sql)
#                 quantity = cr.dictfetchone()
#                 if (quantity['indent_product_qty']==1):
#                     raise osv.except_osv(_('Warning!'),_('You are input %s quantity in Purchase Order but quantity in Purchase Indent do not enough for this Product .' %(purchase_line['po_product_qty'])))        
        
        if new.po_document_type == 'local':
            if new.quotation_no and new.quotation_no.quotation_cate:
                if (new.amount_total > 5000):
                    raise osv.except_osv(_('Warning!'),_('Can not process because Total > 5000 for VV Local PO'))
#         if new.po_indent_no.document_type == 'local':
#             if new.po_document_type != 'local':
#                 raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#         if new.po_indent_no.document_type == 'capital':
#             if new.po_document_type != 'asset':
#                 raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#         if new.po_indent_no.document_type == 'raw':
#             if new.po_document_type != 'raw':
#                 raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#         if new.po_indent_no.document_type == 'service':
#             if new.po_document_type != 'service':
#                 raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#         if new.po_indent_no.document_type == 'outside':
#             if new.po_document_type != 'out':
#                 raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#         if new.po_indent_no.document_type in ('maintenance','spare','normal','base','consumable'):
#             if new.po_document_type != 'standard':
#                 raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
        for line in new.order_line:        
            if new.quotation_no:
                if line.po_indent_no:
                    sql = '''
                            select id from tpt_purchase_product where pur_product_id=%s and product_id=%s
                            
                            '''%(line.po_indent_no.id,line.product_id.id)
                    cr.execute(sql)
                    indent_line_ids = [row[0] for row in cr.fetchall()]
                    if indent_line_ids:
                            self.pool.get('tpt.purchase.product').write(cr, uid, indent_line_ids,{'state':'po_raised'})
                    sql = '''
                                select po_indent_no, product_id, sum(product_qty) as po_product_qty from purchase_order_line where order_id = %s group by po_indent_no, product_id
                            '''%(new.id)
                    cr.execute(sql)
                    for purchase_line in cr.dictfetchall():
                        sql = '''
                                select case when sum(product_uom_qty) <%s then 1 else 0 end quotation_product_qty 
                                from tpt_purchase_quotation_line
                                where po_indent_id=%s and product_id=%s and purchase_quotation_id=%s
                            '''%(purchase_line['po_product_qty'], purchase_line['po_indent_no'], purchase_line['product_id'], new.quotation_no.id)
                        cr.execute(sql)
                        quantity = cr.dictfetchone()
                        if (quantity['quotation_product_qty']==1):
                            raise osv.except_osv(_('Warning!'),_('You are input %s quantity in Purchase Order but quantity in Quotation do not enough for this Purchase Indent and Product .' %(purchase_line['po_product_qty'])))        
            
        return new_id
    
    
    def write(self, cr, uid, ids, vals, context=None):

        new_write = super(purchase_order, self).write(cr, uid, ids, vals, context)
        for new in self.browse(cr, uid, ids):
            for line in new.order_line:
                if 'state' in vals and vals['state']=='approved':
                    sql = '''
                        update tpt_purchase_product set state='close' where pur_product_id=%s and product_id=%s
                    '''%(line.po_indent_no.id,line.product_id.id)
                    cr.execute(sql)
                if 'state' in vals and vals['state']=='cancel':
                    sql = '''
                        update tpt_purchase_product set state='cancel' where pur_product_id=%s and product_id=%s
                    '''%(line.po_indent_no.id,line.product_id.id)
                    cr.execute(sql)
#             sql = '''
#                 select code from account_fiscalyear where '%s' between date_start and date_stop
#             '''%(time.strftime('%Y-%m-%d'))
#             cr.execute(sql)
#             fiscalyear = cr.dictfetchone()
#             if not fiscalyear:
#                 raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
#             if (new.po_document_type=='asset'):
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.asset')
#                 sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
#                 cr.execute(sql)
#             if (new.po_document_type=='standard'):
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.standard')
#                 sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
#                 cr.execute(sql)
#             if (new.po_document_type=='local'):
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.local')
#                 sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
#                 cr.execute(sql)
#             if (new.po_document_type=='return'):
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.return')
#                 sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
#                 cr.execute(sql)
#             if (new.po_document_type=='service'):
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.service')
#                 sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
#                 cr.execute(sql)
#             if (new.po_document_type=='out'):
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.out.service')
#                 sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
#                 cr.execute(sql)
            if 'state' in vals:
                if vals['state'] == 'approved':
                    sql = '''
                        update tpt_request_for_quotation set state = 'close' where id = %s 
                    '''%(new.quotation_no.rfq_no_id.id)
                    cr.execute(sql)
                if vals['state'] == 'cancel':
                    sql = '''
                        update tpt_request_for_quotation set state = 'done' where id = %s
                    '''%(new.quotation_no.rfq_no_id.id)
                    cr.execute(sql)
            date_order = datetime.datetime.strptime(new.date_order,'%Y-%m-%d')
            
#             if new.quotation_no and new.po_indent_no:
#                 quotation = self.pool.get('tpt.purchase.quotation').browse(cr, uid, new.quotation_no)
#                 sql = '''
#                     select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_po from purchase_order_line where order_id in (select id from purchase_order where po_indent_no=%s and state!='cancel')
#                 '''%(new.po_indent_no.id)
#                 cr.execute(sql)
#                 product_qty_po = cr.dictfetchone()['product_qty_po']
#                 sql = '''
#                     select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_qty_quotation from tpt_purchase_quotation_line where po_indent_id = %s
#                 '''%(new.po_indent_no.id)
#                 cr.execute(sql)
#                 product_qty_quotation = cr.dictfetchone()['product_qty_quotation']
#                 if product_qty_po==product_qty_quotation:
#                     sql = '''
#                         update tpt_purchase_quotation set state = 'cancel' where id=%s 
#                     '''%(new.quotation_no.id)
#                     cr.execute(sql)
#             
#             if not new.quotation_no and new.po_indent_no:
#                 date_order_month = date_order.month
#                 date_order_year = date_order.year
#                 sql = '''
#                         select sum(amount_total) as total from purchase_order where EXTRACT(month from date_order) = %s and EXTRACT(year from date_order) = %s
#                 '''%(date_order_month,date_order_year)
#                 cr.execute(sql)
#                 amount_total = cr.dictfetchone()
#                 if (amount_total['total'] > 200000):
#                     raise osv.except_osv(_('Warning!'),_('You are confirm %s the Emergency Purchase reaches 2 Lakhs Limit (2,00,000) in the current month. This can be processed only when the next month starts'%(amount_total['total'])))
#                 
#                 sql = '''
#                             select product_id, sum(product_qty) as po_product_qty from purchase_order_line where order_id = %s group by product_id
#                         '''%(new.id)
#                 cr.execute(sql)
#                 for purchase_line in cr.dictfetchall():
#                     sql = '''
#                             select case when sum(product_uom_qty) <%s then 1 else 0 end indent_product_qty 
#                             from tpt_purchase_product
#                             where product_id=%s and purchase_indent_id in (select id from tpt_purchase_indent where id = %s)
#                         '''%(purchase_line['po_product_qty'], purchase_line['product_id'], new.po_indent_no.id)
#                     cr.execute(sql)
#                     quantity = cr.dictfetchone()
#                     if (quantity['indent_product_qty']==1):
#                         raise osv.except_osv(_('Warning!'),_('You are input %s quantity in Purchase Order but quantity in Purchase Indent do not enough for this Product .' %(purchase_line['po_product_qty'])))        
#             if new.po_indent_no.document_type == 'local':
#                 if new.po_document_type != 'local':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#             if new.po_indent_no.document_type == 'capital':
#                 if new.po_document_type != 'asset':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#             if new.po_indent_no.document_type == 'raw':
#                 if new.po_document_type != 'raw':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#             if new.po_indent_no.document_type == 'service':
#                 if new.po_document_type != 'service':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#             if new.po_indent_no.document_type == 'outside':
#                 if new.po_document_type != 'out':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#             if new.po_indent_no.document_type in ('maintenance','spare','normal','base','consumable'):
#                 if new.po_document_type != 'standard':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))            


            
            if new.po_document_type == 'local':
#                 if new.po_indent_no.document_type != 'local':
#                     raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
                if new.quotation_no and new.quotation_no.quotation_cate:
                    if (new.amount_total > 5000):
                        raise osv.except_osv(_('Warning!'),_('Can not process because Total > 5000 for VV Local PO'))
                
                        
            if new.quotation_no :
                sql = '''
                            select po_indent_no, product_id, sum(product_qty) as po_product_qty from purchase_order_line where order_id = %s group by po_indent_no, product_id
                        '''%(new.id)
                cr.execute(sql)
                for purchase_line in cr.dictfetchall():
                    sql = '''
                            select case when sum(product_uom_qty) <%s then 1 else 0 end quotation_product_qty 
                            from tpt_purchase_quotation_line
                            where po_indent_id=%s and product_id=%s and purchase_quotation_id=%s
                        '''%(purchase_line['po_product_qty'], purchase_line['po_indent_no'], purchase_line['product_id'], new.quotation_no.id)
                    cr.execute(sql)
                    quantity = cr.dictfetchone()
                    if (quantity['quotation_product_qty']==1):
                        raise osv.except_osv(_('Warning!'),_('You are input %s quantity in Purchase Order but quantity in Quotation do not enough for this Purchase Indent and Product .' %(purchase_line['po_product_qty'])))
#                 for line in new.order_line:
#                     if line.product_id:
#                         sql = '''
#                                     select product_id, sum(product_qty) as po_product_qty from purchase_order_line where order_id = %s group by product_id
#                                 '''%(new.id)
#                         cr.execute(sql)
#                         for purchase_line in cr.dictfetchall():
#                             sql = '''
#                                     select case when sum(product_uom_qty) <%s then 1 else 0 end quotation_product_qty 
#                                     from tpt_purchase_quotation_line
#                                     where po_indent_id=%s and product_id=%s and purchase_quotation_id=%s
#                                 '''%(purchase_line['po_product_qty'], new.po_indent_no.id, purchase_line['product_id'], new.quotation_no.id)
#                             cr.execute(sql)
#                             quantity = cr.dictfetchone()
#                             if (quantity['quotation_product_qty']==1):
#                                 raise osv.except_osv(_('Warning!'),_('You are input %s quantity in Purchase Order but quantity in Quotation do not enough for this Purchase Indent and Product .' %(purchase_line['po_product_qty'])))        
                        
        return new_write
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_po_id'):
            sql = '''
                select id from purchase_order 
                where state != 'cancel' and id not in (select po_id from tpt_gate_in_pass gate where gate.state != 'draft' and po_id is not null)
            '''
            cr.execute(sql)
            po_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',po_ids)]
        return super(purchase_order, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def _prepare_order_picking(self, cr, uid, order, context=None):
        return {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'partner_id': order.partner_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'type': 'in',
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
            'document_type': order.po_document_type or False,
            'po_date': order.date_order or False,
        }
 
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        act_taken = False
        if order_line and order_line.product_id and order_line.product_id.categ_id and order_line.product_id.categ_id.cate_name == 'consum':
            act_taken = 'move'
        
        location_dest_id = order.location_id.id
        if order_line.product_id.categ_id.cate_name == 'consum':
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Virtual Locations'),('usage','=','view')])
            if not parent_ids:
                raise osv.except_osv(_('Warning!'),_('System does not have Virtual Locations warehouse, please check it!'))
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Consumption']),('location_id','=',parent_ids[0])])
            if not locat_ids:
                raise osv.except_osv(_('Warning!'),_('System does not have Consumption location in Virtual Locations warehouse, please check it!'))
            location_dest_id = locat_ids[0]
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'bin_location': order_line.product_id.bin_location or False,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': location_dest_id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit,
            'po_indent_id': order_line.po_indent_no and order_line.po_indent_no.id or False,
            'action_taken': act_taken,
            'description':order_line.description or False,
        }
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"

    def get_short_qty(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                '    ': 0.0,
            }
            short = 0
            sql = '''
                select case when sum(product_qty) != 0 then sum(product_qty) else 0 end product_qty from stock_move where purchase_line_id = %s and state='cancel'
            '''%(line.id)
            cr.execute(sql)
            product_qty = cr.dictfetchone()['product_qty']
            res[line.id]['short_qty'] = product_qty
        return res
    
    def line_net_line_po(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        amount_basic = 0.0
        amount_p_f=0.0
        amount_ed=0.0
        amount_fright=0.0
        tax = 0.0
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                    'line_net': 0.0,
                    'amount_basic': 0.0,
                }  
            amount_total_tax=0.0
            total_tax = 0.0
            amount_basic = (line.product_qty * line.price_unit)-((line.product_qty * line.price_unit)*line.discount/100)
            if line.p_f_type == '1':
               amount_p_f = amount_basic * (line.p_f/100)
            elif line.p_f_type == '2':
                amount_p_f = line.p_f
            elif line.p_f_type == '3':
                amount_p_f = line.p_f * line.product_qty
            else:
                amount_p_f = line.p_f
            if line.ed_type == '1':
               amount_ed = (amount_basic + amount_p_f) * (line.ed/100)
            elif line.ed_type == '2':
                amount_ed = line.ed
            elif line.ed_type == '3':
                amount_ed = line.ed * line.product_qty
            else:
                amount_ed = line.ed
            if line.fright_type == '1':
               amount_fright = (amount_basic + amount_p_f + amount_ed) * (line.fright/100)
            elif line.fright_type == '2':
                amount_fright = line.fright
            elif line.fright_type == '3':
                amount_fright = line.fright * line.product_qty
            else: 
                amount_fright = line.fright

            tax_amounts = [r.amount for r in line.taxes_id]
            
            for tax_amount in tax_amounts:
                    tax += tax_amount/100
            #total_tax = (amount_basic + amount_fright + amount_ed + amount_p_f)*(tax)
            total_tax = (amount_basic + amount_ed + amount_p_f)*(tax) #TPT-HERE fright IS REMOVED
            
            amount_total_tax += total_tax
            sql = '''
                SELECT name FROM account_tax
                                WHERE name LIKE '%CST%'
            '''
            cr.execute(sql)
            tax_name = cr.dictfetchone()['name']
            po_tax_name =''
            po_tax_name = [r.description for r in line.taxes_id]
            po_tax_name = str(po_tax_name)
            #if tax_name:
            #if po_tax_name[3:6]=='CST':
            res[line.id]['line_net'] = amount_total_tax+amount_fright+amount_ed+amount_p_f+amount_basic
            #else:
            #    res[line.id]['line_net'] = amount_fright+amount_ed+amount_p_f+amount_basic
            
            res[line.id]['amount_basic'] = amount_basic
        return res
    
    _columns = {
#                 'purchase_tax_id': fields.many2one('account.tax', 'Taxes', domain="[('type_tax_use','=','purchase')]", required = True), 
                
                'po_indent_no':fields.many2one('tpt.purchase.indent','Indent No', required = True,states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
                'product_id': fields.many2one('product.product', 'Material', domain=[('purchase_ok','=',True)], change_default=True, states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)],'amendement':[('readonly',True)]}),
                'product_qty': fields.float('Qty', digits_compute=dp.get_precision('Product Unit of Measure'), required=True, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),    
                'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'discount': fields.float('Disc', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'p_f': fields.float('P&F', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'p_f_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('P&F Type'), track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),
                'ed': fields.float('ED', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'ed_type':fields.selection([('1','%'),('2','Rs'),('3','Per Qty')],('ED Type'), track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'taxes_id': fields.many2many('account.tax', 'purchase_order_taxe', 'ord_id', 'tax_id', 'Taxes', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'fright': fields.float('Frt', track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'fright_type':fields.selection([('1','%'),('2','Rs'), ('3','Per Qty')],('Frt Type'), track_visibility='onchange',states={'cancel':[('readonly',True)],'confirmed':[('readonly',True)],'head':[('readonly',True)],'gm':[('readonly',True)], 'approved':[('readonly',True)],'done':[('readonly',True)]}),  
                'line_no': fields.integer('Sl.No', readonly = True),
                # ham function line_net
                'short_qty': fields.function(get_short_qty,type='float',digits=(16,0),multi='sum', string='Short Closed Qty',),
                'amount_basic': fields.function(line_net_line_po, store = True, multi='deltas' ,string='Value',),
                'line_net': fields.function(line_net_line_po, store = True, multi='deltas' ,string='Line Net',),
                'state': fields.selection([('amendement', 'Amendement'), ('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')], 'Status', required=True, readonly=True,
                                  help=' * The \'Draft\' status is set automatically when purchase order in draft status. \
                                       \n* The \'Confirmed\' status is set automatically as confirm when purchase order in confirm status. \
                                       \n* The \'Done\' status is set automatically when purchase order is set as done. \
                                       \n* The \'Cancelled\' status is set automatically when user cancel purchase order.'),
                'description':fields.char('Description', size = 50, readonly = True),
                #TPT
                #'item_text': fields.char('Item Text'), 
                }   
    

    _defaults = {
                 'date_planned':time.strftime('%Y-%m-%d'),
                 'state': 'draft',
                 }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('order_id',False):
            vals['line_no'] = len(self.search(cr, uid,[('order_id', '=', vals['order_id'])])) + 1
        if 'price_unit' in vals:
            if (vals['price_unit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Price Unit is not allowed as negative values'))
        if 'discount' in vals:
            if (vals['discount'] < 0):
                raise osv.except_osv(_('Warning!'),_('Disc is not allowed as negative values'))
        if 'p_f' in vals:
            if (vals['p_f'] < 0):
                raise osv.except_osv(_('Warning!'),_('PF is not allowed as negative values'))
        if 'ed' in vals:
            if (vals['ed'] < 0):
                raise osv.except_osv(_('Warning!'),_('ED is not allowed as negative values'))
        if 'fright' in vals:
            if (vals['fright'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not allowed as negative values'))
        return super(purchase_order_line, self).create(cr, uid, vals, context)
    def write(self, cr, uid,ids, vals, context=None):
        if 'price_unit' in vals:
            if (vals['price_unit'] < 0):
                raise osv.except_osv(_('Warning!'),_('Price Unit is not allowed as negative values'))
        if 'discount' in vals:
            if (vals['discount'] < 0):
                raise osv.except_osv(_('Warning!'),_('Disc is not allowed as negative values'))
        if 'p_f' in vals:
            if (vals['p_f'] < 0):
                raise osv.except_osv(_('Warning!'),_('PF is not allowed as negative values'))
        if 'ed' in vals:
            if (vals['ed'] < 0):
                raise osv.except_osv(_('Warning!'),_('ED is not allowed as negative values'))
        if 'fright' in vals:
            if (vals['fright'] < 0):
                raise osv.except_osv(_('Warning!'),_('Freight is not allowed as negative values'))  
        return super(purchase_order_line, self).write(cr, uid,ids, vals, context)   
    def unlink(self, cr, uid, ids, context=None):
        procurement_ids_to_cancel = []
        for line in self.browse(cr, uid, ids, context=context):
            update_ids = self.search(cr, uid,[('order_id','=',line.order_id.id),('line_no','>',line.line_no)])
            if update_ids:
                cr.execute("UPDATE purchase_order_line SET line_no=line_no-1 WHERE id in %s",(tuple(update_ids),))
            if line.move_dest_id:
                procurement_ids_to_cancel.extend(procurement.id for procurement in line.move_dest_id.procurements)
            #TPT - Commented By BalamuruganPurushothaman - ON 08/04/2015 - TO AVOID THIS WARNING WHEN PO LINE IS DELETED
            #if (line.order_id.quotation_no.state == 'done'):
            #    raise osv.except_osv(_('Warning!'), _('This PO line can not be deleted!')) 
        if procurement_ids_to_cancel:
            self.pool['procurement.order'].action_cancel(cr, uid, procurement_ids_to_cancel)
        return super(purchase_order_line, self).unlink(cr, uid, ids, context=context)
    
    
    def onchange_po_indent_no(self, cr, uid, ids,po_indent_no=False, context=None):
        if po_indent_no:
            return {'value': {'product_id': False}}    
        
#     def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
#             partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
#             name=False, price_unit=False, context=None):
#         """
#         onchange handler of product_uom.
#         """
#         if context is None:
#             context = {}
#         if not uom_id:
#             return {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
#         context = dict(context, purchase_uom_check=True)
#         return self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
#             partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
#             name=name, price_unit=price_unit, context=context)
 
  
    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False,  po_indent_no = False, context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}
 
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        
        if not product_id:
            return res
 
        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')
 
        # - check for the presence of partner_id and pricelist_id
        #if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        #if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))
 
        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
         
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})
 
        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
 
        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id
 
        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
            uom_id = product_uom_po_id
 
        res['value'].update({'product_uom': uom_id})
 
        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.date.context_today(self,cr,uid,context=context)
 
 
        supplierinfo = False
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if (qty or 0.0) < min_qty: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})
 
        # - determine price_unit and taxes_id
        if pricelist_id:
            price = product_pricelist.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order})[pricelist_id]
        else:
            price = product.standard_price
 
        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})
 
        if po_indent_no and product_id: 
            indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_no)
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            for line in indent.purchase_product_line:
                if product_id == line.product_id.id:
                    res['value'].update( {
                            'price_unit':product.standard_price,
                            'product_uom':line.uom_po_id and line.uom_po_id.id or False,
                            'product_qty':line.product_uom_qty or False,
                            })
 
        return res
 
      
#     def onchange_product_id(self, cr, uid, ids, product_id=False, po_indent_no=False, context=None):
#         vals = {}
#         if po_indent_no and product_id: 
#             po = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_no)
#             product = self.pool.get('product.product').browse(cr, uid, product_id)
#             for line in po.purchase_product_line:
#                 if product_id == line.product_id.id:
#                     vals = {
#                             'price_unit':product.standard_price,
#                             'uom_po_id':line.uom_po_id and line.uom_po_id.id or False,
#                             'product_uom_qty':line.product_uom_qty or False,
#                             }
#         return {'value': vals}   
purchase_order_line()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_grn_no_id'):
            sql = '''
                select picking_id from stock_move where state = 'cancel' group by picking_id
            '''
            cr.execute(sql)
            picking_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',picking_ids)]
        return super(stock_picking_in, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)


    
stock_picking_in()    
    
class tpt_good_return_request(osv.osv):
    _name = "tpt.good.return.request"
    
    _columns = {
        'grn_no_id' : fields.many2one('stock.picking.in', 'GRN No', required = True, states={'cancel': [('readonly', True)],'done':[('readonly', True)]}), 
        'request_date': fields.datetime('Request Date', states={'cancel': [('readonly', True)],'done':[('readonly', True)]}), 
        'product_detail_line': fields.one2many('tpt.product.detail.line', 'request_id', 'Material Details', states={'cancel': [('readonly', True)],'done':[('readonly', True)]}), 
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancelled'),('done', 'Done')],'Status', readonly=True),
                }
    _defaults = {
        'request_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['grn_no_id'], context)
  
        for record in reads:
            name = record['grn_no_id']
            res.append((record['id'], name))
        return res 
    
    def onchange_grn_no_id(self, cr, uid, ids,grn_no_id=False,context=None):
        vals = {}
        if grn_no_id :
            details = []
            picking = self.pool.get('stock.picking.in').browse(cr, uid, grn_no_id)
            stock = self.pool.get('stock.move')
            stock_ids = stock.search(cr,uid,[('picking_id','=',grn_no_id), ('state', '=', 'cancel')])
            for line in stock.browse(cr,uid,stock_ids):
                quality_ids = self.pool.get('tpt.quanlity.inspection').search(cr,uid,[('need_inspec_id','=',line.id)])
                for quality in self.pool.get('tpt.quanlity.inspection').browse(cr,uid,quality_ids):
                    rs = {
                          'product_id':line.product_id and line.product_id.id or False,
                          'product_qty': line.product_qty or False,
                          'uom_po_id': line.product_uom and line.product_uom.id or False,
                          'state': 'reject',
                          'reason': quality.reason,
                          }
                details.append((0,0,rs))
                     
        return {'value': {'product_detail_line': details}}
    
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'done'})
        return True 

    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'cancel'})
        return True     
tpt_good_return_request()

class tpt_product_detail_line(osv.osv):
    _name = "tpt.product.detail.line"
    
    _columns = {
        'request_id': fields.many2one('tpt.good.return.request', 'Request', ondelete = 'cascade'),        
        'product_id': fields.many2one('product.product', 'Material'),
        'product_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
        'state':fields.selection([('reject', 'Reject')],'Status', readonly=True),
        'reason': fields.text('Reason'),
        }
    _defaults = {
        'state': 'reject',
    }
tpt_product_detail_line()

class tpt_quanlity_inspection(osv.osv):
    _name = "tpt.quanlity.inspection"
    _columns = {
        'name' : fields.many2one('stock.picking.in','GRN No',required = True,readonly = True,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'need_inspec_id':fields.many2one('stock.move','Need Inspec',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date':fields.datetime('Create Date',readonly = True,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_id':fields.many2one('res.partner','Supplier',required = True,readonly = True,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'product_id': fields.many2one('product.product', 'Product',required = True,readonly = True,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'reason':fields.text('Reason',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'specification_line':fields.one2many('tpt.product.specification','specification_id','Product Specification'),
        'qty':fields.float('Qty',digits=(16,3),states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'remaining_qty':fields.float('Remaining Qty', readonly= True),
        'state':fields.selection([('draft', 'Draft'),('remaining', 'Remaining'),('done', 'Done')],'Status', readonly=True),
                }
    _defaults = {
        'state':'draft',
                 }

    def bt_approve(self,cr,uid,ids,context=None):
        move_obj = self.pool.get('stock.move')
        locat_obj = self.pool.get('stock.location')
        location_id = False
        location_dest_id = False
        parent_ids = locat_obj.search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
        if not parent_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection warehouse, please check it!'))
        locat_ids = locat_obj.search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
        if not locat_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection  location in Quality Inspection  warehouse, please check it!'))
        else:
            location_id = locat_ids[0]
            
        parent_dest_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
        if not parent_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
        location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_dest_ids[0])])
        if not location_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Raw Material location in Store warehouse, please check it!'))
        else:
            location_dest_id = location_dest_ids[0]
        for line in self.browse(cr,uid,ids):
            rs = {
                  'name': '/',
                  'product_id':line.product_id and line.product_id.id or False,
                  'product_qty':line.qty or False,
                  'product_uom':line.product_id.uom_po_id and line.product_id.uom_po_id.id or False,
                  'location_id':location_id,
                  'location_dest_id':location_dest_id,
                  
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
#             move_obj.action_done(cr, uid, [line.need_inspec_id.id])
        return self.write(cr, uid, ids, {'state':'done'})
    
    def bt_reject(self,cr,uid,ids,context=None):
        move_obj = self.pool.get('stock.move')
#         picking_obj = self.pool.get('stock.picking')
#         for line in self.browse(cr,uid,ids):
#             move_obj.action_cancel(cr, uid, [line.need_inspec_id.id])
#             picking_obj.do_partial(cr, uid, [line.name.id], {})
        locat_obj = self.pool.get('stock.location')
        location_id = False
        location_dest_id = False
        parent_ids = locat_obj.search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
        if not parent_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection warehouse, please check it!'))
        locat_ids = locat_obj.search(cr, uid, [('name','in',['Quality Inspection','Inspection']),('location_id','=',parent_ids[0])])
        if not locat_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Quality Inspection  location in Quality Inspection  warehouse, please check it!'))
        else:
            location_id = locat_ids[0]
            
        parent_dest_ids = locat_obj.search(cr, uid, [('name','=','Blocked List'),('usage','=','view')])
        if not parent_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Blocked List warehouse, please check it!'))
        location_dest_ids = locat_obj.search(cr, uid, [('name','in',['Blocked List','Block List']),('location_id','=',parent_dest_ids[0])])
        if not location_dest_ids:
            raise osv.except_osv(_('Warning!'),_('System does not have Blocked List location in Blocked List warehouse, please check it!'))
        else:
            location_dest_id = location_dest_ids[0]
        for line in self.browse(cr,uid,ids):
            rs = {
                  'name': '/',
                  'product_id':line.product_id and line.product_id.id or False,
                  'product_qty':line.qty or False,
                  'product_uom':line.product_id.uom_po_id and line.product_id.uom_po_id.id or False,
                  'location_id':location_id,
                  'location_dest_id':location_dest_id,
                  
                  }
            move_id = move_obj.create(cr,uid,rs)
            move_obj.action_done(cr, uid, [move_id])
        return self.write(cr, uid, ids, {'state':'cancel'})

#     def onchange_grn_no(self, cr, uid, ids,name=False, context=None):
#         vals = {}
#         po_line = []
#         if name:
#             grn = self.pool.get('tpt.quanlity.inspection').browse(cr, uid, name)
# #             for line in quotation.purchase_quotation_line:
# #                 rs = {
# #                       'po_indent_no': line.po_indent_id and line.product_id.id or False,
# #                       'product_id': line.product_id and line.product_id.id or False,
# #                       'product_qty': line.product_uom_qty or False,
# #                       'product_uom': line.uom_po_id and line.uom_po_id.id or False,
# #                       'price_unit': line.price_unit or False,
# #                       'price_subtotal': line.sub_total or False,
# #                       'date_planned':quotation.date_quotation or False,
# #                       }
# #                 po_line.append((0,0,rs))
#             vals = {
#                     'partner_id':quotation.supplier_id and quotation.supplier_id.id or '',
#                     'partner_ref':quotation.quotation_ref or '',
#                     'purchase_tax_id':quotation.tax_id and quotation.tax_id.id or '',
#                     'order_line': po_line,
#                     }
#         return {'value': vals}

tpt_quanlity_inspection()
class tpt_product_specification(osv.osv):
    _name = "tpt.product.specification"
    _columns = {
        'name' : fields.char('Parameters',size = 1024,required = True),
        'value' : fields.float('Value',digits=(16,3),required = True),
        'exp_value' : fields.char('Experimental Value',size = 1024),
        'specification_id':fields.many2one('res.partner','Supplier'),
 
                }
tpt_product_specification()

class tpt_gate_out_pass(osv.osv):
    _name = "tpt.gate.out.pass"
      
    _columns = {
        'name': fields.char('Gate Out Pass No', size = 1024, readonly=True),
        'po_id': fields.many2one('purchase.order', 'PO Number', required = True),
        'supplier_id': fields.many2one('res.partner', 'Supplier', required = True),
        'grn_id': fields.many2one('stock.picking.in','GRN No', required = True), 
        'gate_date_time': fields.datetime('Gate Out Pass Date & Time'),
        'gate_out_pass_line': fields.one2many('tpt.gate.out.pass.line', 'gate_out_pass_id', 'Product Details'),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
                }
    _defaults={
               'name':'/',
               'gate_date_time': time.strftime("%Y-%m-%d %H:%M:%S"),
               'state': 'draft',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.gate.out.pass.import') or '/'
        return super(tpt_gate_out_pass, self).create(cr, uid, vals, context=context)
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    def onchange_grn_id(self, cr, uid, ids,grn_id=False):
        res = {'value':{
                        'supplier_id':False,
                        'po_id':False,
                        'gate_out_pass_line':[],
                      }
               }
        if grn_id:
            gate_out_pass_line = []
            good_req_ids = self.pool.get('tpt.good.return.request').search(cr, uid,[('grn_no_id','=',grn_id)])
            good_req_id = self.pool.get('tpt.good.return.request').browse(cr,uid,good_req_ids[0])
            for line in good_req_id.product_detail_line:
                gate_out_pass_line.append({
                          'product_id': line.product_id and line.product_id.id or False,
                          'product_qty':line.product_qty or False,
                          'uom_po_id': line.uom_po_id and line.uom_po_id.id or False,
                          'reason': line.reason or False,
                    })
        res['value'].update({
                    'supplier_id': good_req_id.grn_no_id and good_req_id.grn_no_id.partner_id and good_req_id.grn_no_id.partner_id.id or False,
                    'po_id': good_req_id.grn_no_id and good_req_id.grn_no_id.purchase_id and good_req_id.grn_no_id.purchase_id.id or False,
                    'gate_out_pass_line': gate_out_pass_line,
        })
        return res
    
tpt_gate_out_pass()

class tpt_gate_out_pass_line(osv.osv):
    _name = "tpt.gate.out.pass.line"
    _columns = {
        'gate_out_pass_id': fields.many2one('tpt.gate.out.pass','Gate Out Pass',ondelete = 'cascade'),
        'product_id': fields.many2one('product.product', 'Material'),
        'product_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
        'reason': fields.char('Reason for Rejection', size = 1024),
                }
    _defaults={
               'product_qty': 1,
    }
      
tpt_gate_out_pass_line()
class tpt_pur_organi_code(osv.osv):
    _name = "tpt.pur.organi.code"
    _columns = {
        'name': fields.char('Name', size = 1024),
                }
tpt_pur_organi_code()

class tpt_vendor_group(osv.osv):
    _name = "tpt.vendor.group"
    _order = "code"
    _columns = {
                
        'name': fields.char('Name', size = 1024, required=True),
        'code':fields.char('Code',size = 256,required = True),
        'active':fields.boolean('Active'),
        'vendor_sub_line':fields.one2many('tpt.vendor.sub.group','vendor_group_id','Vendor Sub Group'),
                }
    
    _defaults = {
        'active': True,
    }
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_vendor_group, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_vendor_group, self).write(cr, uid,ids, vals, context)



    def _check_code_id(self, cr, uid, ids, context=None):
        for vendor in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_vendor_group where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(vendor.id,vendor.code,vendor.name)
            cr.execute(sql)
            vendor_ids = [row[0] for row in cr.fetchall()]
            if vendor_ids:  
                raise osv.except_osv(_('Warning!'),_('Name or Code in Vendor Group should be unique!'))
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
    
tpt_vendor_group()

class tpt_vendor_sub_group(osv.osv):
    _name = "tpt.vendor.sub.group"
    _columns = {
        'name': fields.char('Name', size = 1024,required=True),
        'code':fields.char('Code',size = 256,required = True),
        'vendor_group_id':fields.many2one('tpt.vendor.group','Vendor Group',required = True),
                }
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_vendor_sub_group, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_vendor_sub_group, self).write(cr, uid,ids, vals, context)

    def _check_code_id(self, cr, uid, ids, context=None):
        for vendor in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_vendor_sub_group where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(vendor.id,vendor.code,vendor.name)
            cr.execute(sql)
            vendor_ids = [row[0] for row in cr.fetchall()]
            if vendor_ids:  
                raise osv.except_osv(_('Warning!'),_('Name or Code in Vendor Sub Group should be unique!'))
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
tpt_vendor_sub_group()

class tpt_quality_parameters(osv.osv):
    _name = "tpt.quality.parameters"
    _columns = {
        'name': fields.char('Parameter Name', size = 1024,required=True),
        'code':fields.char('Parameter Code',size = 256,required = True),
        'description':fields.text('Description'),
                }
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_quality_parameters, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(tpt_quality_parameters, self).write(cr, uid,ids, vals, context)

    def _check_code_id(self, cr, uid, ids, context=None):
        for parameter in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_quality_parameters where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(parameter.id,parameter.code,parameter.name)
            cr.execute(sql)
            parameter_ids = [row[0] for row in cr.fetchall()]
            if parameter_ids:  
                raise osv.except_osv(_('Warning!'),_('Name or Code in Quality Parameters should be unique!'))
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]
tpt_quality_parameters()

class tpt_request_for_quotation(osv.osv):
    _name = "tpt.request.for.quotation"
    
#     def date_system(self, cr, uid, ids, field_name, args, context=None):
#         res = {}
#         for line in self.browse(cr,uid,ids,context=context):
#             res[line.id] = {
#                 'date_test' : False,
#                 }
#             sql = '''
#                 select date(date('rfq_date')+INTERVAL '0days') as date_sys from tpt_request_for_quotation where id = %s
#             '''%(line.id)      
#             cr.execute(sql)
#             date_sys = cr.dictfetchone()['date_sys']
#             res[line.id]['date_test'] = date_sys
#         return res

    _columns = {
        'name': fields.char('RFQ No', size = 1024,readonly=True, required = True , states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'close':[('readonly', True)]}),
        'rfq_date': fields.date('RFQ Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'close':[('readonly', True)]}),
        'rfq_category': fields.selection([('single','Single'),('multiple','Multiple'),('special','Special')],'RFQ Category', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'close':[('readonly', True)]}),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'create_on': fields.datetime('Created on', readonly = True),
        'expect_quote_date': fields.date('Expected Quote Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'close':[('readonly', True)]}),
        'rfq_line': fields.one2many('tpt.rfq.line', 'rfq_id', 'RFQ Line'),
        'rfq_supplier': fields.one2many('tpt.rfq.supplier', 'rfq_id', 'Supplier Line', states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'close':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Confirm'),('close', 'Closed')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)], 'close':[('readonly', True)]}),  
        'raised_ok': fields.boolean('Raised',readonly =True ), 
        'po_document_type':fields.selection([('raw','VV Raw material PO'),('asset','VV Capital PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'Document Type', required = True ),
#         'date_test': fields.function(date_system, store = True, type = 'date', string='RFQ Date'),  
#         'date_test': fields.date('date_test'),
                }
    _defaults={
               'name':'/',
               'state': 'draft',
               'rfq_date':time.strftime('%Y-%m-%d'),
               'create_on':fields.datetime.now,
               'raised_ok': False,
#                 'date_test': time.strftime('%Y-%m-%d')
    }
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_rfq_id'):
            sql = '''
                select id from tpt_request_for_quotation 
                where state not in ('draft','cancel','close') and rfq_category = 'multiple' and id not in (select cc.name from tpt_comparison_chart cc ,tpt_request_for_quotation rfq where cc.name = rfq.id)
            '''
            cr.execute(sql)
            po_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',po_ids)]
        return super(tpt_request_for_quotation, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)    

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
      
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            for po_indent in line.rfq_line:
                sql = '''
                    select id from tpt_purchase_product where pur_product_id=%s and product_id=%s
                '''%(po_indent.po_indent_id.id,po_indent.product_id.id)
                cr.execute(sql)
                indent_line_ids = [row[0] for row in cr.fetchall()]
                if indent_line_ids:
                    self.pool.get('tpt.purchase.product').write(cr, uid, indent_line_ids,{'state':'rfq_raised'})
                    
            rfq_line_obj = self.pool.get('tpt.rfq.line')        
            sql = '''
                select id from tpt_rfq_line where rfq_id = %s
            '''%(line.id)
            cr.execute(sql)
            rfq_line_ids = [r[0] for r in cr.fetchall()]
            rfq_line_obj.write(cr, uid, rfq_line_ids,{'state':'done'})
        return self.write(cr, uid, ids,{'state':'done'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            quotation_ids = self.pool.get('tpt.purchase.quotation').search(cr,uid,[('rfq_no_id','=',line.id)])
            chart_ids = self.pool.get('tpt.comparison.chart').search(cr,uid,[('name','=',line.id)])
            if quotation_ids:
                raise osv.except_osv(_('Warning!'),_('RFQ was existed at the Quotation.!'))
            if chart_ids:
                raise osv.except_osv(_('Warning!'),_('RFQ was existed at the Comparison Chart.!'))
            self.write(cr, uid, ids,{'state':'cancel'})
        return True   
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.rfq.import') or '/'
        new_id = super(tpt_request_for_quotation, self).create(cr, uid, vals, context)
        rfq = self.browse(cr,uid,new_id)
#         for line in rfq.rfq_line:
#             if rfq.po_document_type and line.po_indent_id.document_type:
#                 if rfq.po_document_type == 'local':
#                     if line.po_indent_id.document_type  != 'local':
#                         raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                 if rfq.po_document_type  == 'asset':
#                     if line.po_indent_id.document_type != 'capital' :
#                         raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                 if  rfq.po_document_type == 'raw':
#                     if line.po_indent_id.document_type != 'raw':
#                         raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                 if rfq.po_document_type == 'service':
#                     if line.po_indent_id.document_type  != 'service':
#                         raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                 if rfq.po_document_type == 'out':
#                     if line.po_indent_id.document_type  != 'outside':
#                         raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                 if rfq.po_document_type == 'standard' :
#                     if line.po_indent_id.document_type not in ('maintenance','spare','normal','base','consumable'):
#                         raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
        if rfq.rfq_category:
            if rfq.rfq_category != 'multiple':
                if (len(rfq.rfq_supplier) > 1):
                    raise osv.except_osv(_('Warning!'),_('You must choose RFQ category is multiple if you want more than one vendors!'))
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        new_write = super(tpt_request_for_quotation, self).write(cr, uid,ids, vals, context)
        for rfq in self.browse(cr,uid,ids):
#             for line in rfq.rfq_line:
#                  if rfq.po_document_type and line.po_indent_id.document_type:
#                     if rfq.po_document_type == 'local':
#                         if line.po_indent_id.document_type  != 'local':
#                             raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                     if rfq.po_document_type  == 'asset':
#                         if line.po_indent_id.document_type != 'capital' :
#                             raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                     if  rfq.po_document_type == 'raw':
#                         if line.po_indent_id.document_type != 'raw':
#                             raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                     if rfq.po_document_type == 'service':
#                         if line.po_indent_id.document_type  != 'service':
#                             raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                     if rfq.po_document_type == 'out':
#                         if line.po_indent_id.document_type  != 'outside':
#                             raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
#                     if rfq.po_document_type == 'standard' :
#                         if line.po_indent_id.document_type not in ('maintenance','spare','normal','base','consumable'):
#                             raise osv.except_osv(_('Warning!'),_('Indent not allowed create with Document Type this'))
            if rfq.rfq_category:
                if rfq.rfq_category != 'multiple':
                    if (len(rfq.rfq_supplier) > 1):
                        raise osv.except_osv(_('Warning!'),_('You must choose RFQ category is multiple if you want more than one vendors!'))
        return new_write
    
tpt_request_for_quotation()

class tpt_rfq_line(osv.osv):
    _name = 'tpt.rfq.line'
    _columns = {
        'rfq_id': fields.many2one('tpt.request.for.quotation','RFQ',ondelete='cascade'),
        'po_indent_id':fields.many2one('tpt.purchase.indent','PO Indent', required = True),
        'product_id': fields.many2one('product.product', 'Material',required = True),
        'indent_line_id': fields.many2one('tpt.purchase.product', 'Material', required = True),
        'description': fields.char('Mat.Desc'), 
        'recom_vendor': fields.char('Recom.Vendor'), 
        'item_text': fields.char('Item Text'), 
        'product_uom_qty': fields.float('Quantity', readonly = True),   
        'uom_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Confirm'),('close', 'Closed')],'Status', readonly=True),
        }  
    _defaults = {
        'state': 'draft',         
                 }
    
#     def _check_rfq_line(self, cr, uid, ids, context=None):
#         for product in self.browse(cr, uid, ids, context=context):
#             product_ids = self.search(cr, uid, [('id','!=',product.id),('po_indent_id', '=',product.po_indent_id.id), ('product_id', '=',product.product_id.id),('rfq_id','=',product.rfq_id.id)])
#             if product_ids:
#                 raise osv.except_osv(_('Warning!'),_('PO Indent and Product were existed !'))
#                 return False
#             return True
#         
#     _constraints = [
#         (_check_rfq_line, 'Identical Data', ['pur_product_id', 'product_id','po_indent_id']),
#     ]   
    
    def create(self, cr, uid, vals, context=None):
        if 'po_indent_id' in vals:
            if 'indent_line_id' in vals:
                line = self.pool.get('tpt.purchase.product').browse(cr, uid, vals['indent_line_id'])
                vals.update({
                        'uom_id':line.uom_po_id.id,
                        'product_uom_qty':line.product_uom_qty,
                        })
        return super(tpt_rfq_line, self).create(cr, uid, vals, context)    
  
    def write(self, cr, uid, ids, vals, context=None):
        if 'po_indent_id' in vals:
            if 'indent_line_id' in vals:
                line = self.pool.get('tpt.purchase.product').browse(cr, uid, vals['indent_line_id'])
                vals.update({
                        'uom_id':line.uom_po_id.id,
                        'product_uom_qty':line.product_uom_qty,
                        })
        return super(tpt_rfq_line, self).write(cr, uid, ids, vals, context)    
    
    def onchange_rfq_indent_id(self, cr, uid, ids,po_indent_id=False, context=None):
        if po_indent_id:
            indent = self.pool.get('tpt.purchase.indent').browse(cr,uid,po_indent_id)
            return {'value': {
                              'indent_line_id': False,
                              'item_text': indent.header_text,
                              }}  
        
#     def onchange_rfq_product_id(self, cr, uid, ids,product_id=False, po_indent_id=False, context=None):
#         vals = {}
#         if po_indent_id and product_id: 
#             indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_id)
#             product = self.pool.get('product.product').browse(cr, uid, product_id)
#             for line in indent.purchase_product_line:
#                 if product_id == line.product_id.id:
#                     vals = {
#                             'description':line.description and line.description or False,
#                             'item_text':line.item_text and line.item_text or False,
#                             'recom_vendor':line.recom_vendor and line.recom_vendor or False,
#                             'uom_id':line.uom_po_id and line.uom_po_id.id or False,
#                             'product_uom_qty':line.product_uom_qty or False,
#                             }
#         return {'value': vals}
    
    def onchange_rfq_indent_line_id(self, cr, uid, ids,indent_line_id=False, po_indent_id=False, context=None):
        vals = {}
        if po_indent_id and indent_line_id: 
            indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, po_indent_id)
#             product = self.pool.get('product.product').browse(cr, uid, product_id)
            line = self.pool.get('tpt.purchase.product').browse(cr, uid, indent_line_id)
            vals = {
                    'description':line.description and line.description or False,
                    'item_text':line.item_text and line.item_text or False,
                    'recom_vendor':line.recom_vendor and line.recom_vendor or False,
                    'uom_id':line.uom_po_id and line.uom_po_id.id or False,
                    'product_uom_qty':line.product_uom_qty or False,
                    'product_id':line.product_id.id,
                    }
        return {'value': vals}  
tpt_rfq_line()

class tpt_rfq_supplier(osv.osv):
    _name = 'tpt.rfq.supplier'
    _columns = {
        'rfq_id': fields.many2one('tpt.request.for.quotation','RFQ'),
        'vendor_id':fields.many2one('res.partner','Vendor Name', required = True),
        'state_id': fields.many2one('res.country.state', 'Vendor Location'),
        'quotation_no_id': fields.many2one('tpt.purchase.quotation', 'Quotation No', readonly = True),
#         'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        }  
    


    
    def onchange_rfq_vendor_id(self, cr, uid, ids,vendor_id=False, context=None):
        vals = {}
        if vendor_id: 
            vendor = self.pool.get('res.partner').browse(cr, uid, vendor_id)
            vals = {
                    'state_id':vendor.state_id and vendor.state_id.id or False,
                            }
        return {'value': vals}   
    
    def bt_print(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'tpt.rfq.supplier',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'tpt_rfq_supplier',
#                 'datas': datas,
#                 'nodestroy' : True
        }
    
tpt_rfq_supplier()

class res_partner(osv.osv):
    _inherit = "res.partner"   
    _columns = {
#         'supplier_code':fields.char('Vendor Code', size = 256),
        'vendor_code':fields.char('Vendor Code', size = 20),
        'contact_per':fields.char('Contact Person', size = 1024),
        'vendor_tag':fields.char('Tag', size = 1024),
        'pur_orgin_code_id':fields.many2one('tpt.pur.organi.code','Purchase Organisation Code'),
        'vendor_group_id':fields.many2one('tpt.vendor.group','Vendor Class (Group)'),
        'vendor_sub_group_id':fields.many2one('tpt.vendor.sub.group','Vendor Sub Class (Sub Group)'),   
                
                }
    def onchange_vendor_group_id(self, cr, uid, ids,vendor_group_id=False, context=None):
        return {'value': {'vendor_sub_group_id': False}}

#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_supplier_code'):
#             if context.get('product_id'):
#                 sql = '''
#                     select vendor_id from tpt_rfq_supplier where quotation_no_id in (select id from tpt_request_for_quotation where id = %s)
#                 '''%(context.get('product_id'))
#                 cr.execute(sql)
#                 product_ids = [row[0] for row in cr.fetchall()]
#                 args += [('id','in',product_ids)]
#         return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count) 
# #     
# #     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
# #        ids = self.search(cr, user, args, context=context, limit=limit)
# #        return self.name_get(cr, user, ids, context=context)

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_supplier_code'):
            if context.get('rfq_no_id'):
                sql = '''
                    select vendor_id from tpt_rfq_supplier where rfq_id = %s
                '''%(context.get('rfq_no_id'))
                cr.execute(sql)
                partner_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',partner_ids)]
                
        if context.get('search_recom_product'):
            if context.get('product_id'):
                sql = '''
                    select name from product_supplierinfo where product_id in (select id from product_product where id = %s)
                '''%(context.get('product_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count) 
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Overrides orm name_get method"""
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
        res = super(res_partner,self).name_get(cr, uid, ids, context)
        if context.get('search_supplier_code'):
            res = []
            reads = self.read(cr, uid, ids, ['vendor_code'], context)
            for record in reads:
                name = record['vendor_code']
                res.append((record['id'], name))
        return res
   
res_partner()   

class tpt_material_request(osv.osv):
    _name = "tpt.material.request"
    def _get_department_id(self,cr,uid,context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        return user.employee_id and user.employee_id.department_id and user.employee_id.department_id.id or False
    _columns = {
        'name': fields.char('Material Request No', size = 1024,readonly = True,states={'done':[('readonly', True)]}),
        'date_request':fields.date('Material Request Date',required = True,states={'done':[('readonly', True)]}),
        'date_expec':fields.date('Expected Date',states={'done':[('readonly', True)]}),
        'department_id':fields.many2one('hr.department','Department',required = True,  states={ 'done':[('readonly', True)]}),
        'create_uid':fields.many2one('res.users','Request Raised By', states={'done':[('readonly', True)]}),
        'section_id': fields.many2one('arul.hr.section','Section',ondelete='restrict', states={'done':[('readonly', True)]}),
        'requisitioner':fields.many2one('hr.employee','Requisitioner', states={'done':[('readonly', True)]}),
        'project_id': fields.many2one('tpt.project','Project', states={'done':[('readonly', True)]}),
        'project_section_id': fields.many2one('tpt.project.section','Project Section',ondelete='restrict',states={'done':[('readonly', True)]}),
        'material_request_line':fields.one2many('tpt.material.request.line','material_request_id','Vendor Group',states={'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Approve')],'Status', readonly=True),
        'request_type':fields.selection([('production', 'Production'),('normal', 'Normal'),('main', 'Maintenance')],'Request Type', states={'done':[('readonly', True)]}),
                }
    _defaults = {
        'state':'draft',      
        'name': '/',
        'date_request': fields.datetime.now,
        'department_id': _get_department_id,
    }
    
    
    def create(self, cr, uid, vals, context=None):
        user = self.pool.get('res.users').browse(cr,uid,uid)
        product_obj = self.pool.get('product.product')
#         vals['department_id'] = user.employee_id and user.employee_id.department_id and user.employee_id.department_id.id or False
        if vals.get('name','/')=='/':
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.material.request.import')
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        new_id = super(tpt_material_request, self).create(cr, uid, vals, context)
        material = self.browse(cr,uid,new_id)
        sql = '''
                select product_id, prodlot_id, sum(product_uom_qty) as product_qty from tpt_material_request_line where material_request_id = %s group by product_id,prodlot_id
                '''%(material.id)
        cr.execute(sql)
        for order_line in cr.dictfetchall():
            location_id = False
            locat_ids = []
            parent_ids = []
            
            product_id = product_obj.browse(cr,uid,order_line['product_id'])
            cate_name = product_id.categ_id and product_id.categ_id.cate_name or False
            if cate_name == 'finish':
                lot = order_line['prodlot_id'] or False
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
                if locat_ids:
                    location_id = locat_ids[0]
                    if lot:
                        sql = '''
                        SELECT sum(onhand_qty) onhand_qty
                        From
                        (SELECT
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and loc2.id = %s and prodlot_id = %s
                            then stm.primary_qty
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and loc1.id = %s and prodlot_id = %s
                            then -1*stm.primary_qty 
                            else 0.0 end
                            end onhand_qty
                                    
                        FROM stock_move stm 
                            join stock_location loc1 on stm.location_id=loc1.id
                            join stock_location loc2 on stm.location_dest_id=loc2.id
                        WHERE stm.state= 'done' and product_id=%s)foo
                        '''%(location_id,lot,location_id,lot,order_line['product_id'])
                    else:
                        sql = '''
                        SELECT sum(onhand_qty) onhand_qty
                        From
                        (SELECT
                            case when loc1.usage != 'internal' and loc2.usage = 'internal' and loc2.id = %s
                            then stm.primary_qty
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal' and loc1.id = %s
                            then -1*stm.primary_qty 
                            else 0.0 end
                            end onhand_qty
                                    
                        FROM stock_move stm 
                            join stock_location loc1 on stm.location_id=loc1.id
                            join stock_location loc2 on stm.location_dest_id=loc2.id
                        WHERE stm.state= 'done' and product_id=%s)foo
                        '''%(location_id,location_id,order_line['product_id'])
                    cr.execute(sql)
                    onhand_qty = cr.dictfetchone()['onhand_qty']
                    if (order_line['product_qty'] > onhand_qty):
                        raise osv.except_osv(_('Warning!'),_('You are confirm %s but only %s available for this product in stock.' %(order_line['product_qty'], onhand_qty)))
            if cate_name == 'raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                if locat_ids:
                    location_id = locat_ids[0]
            if cate_name == 'spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Spare'),('location_id','=',parent_ids[0])])
                if locat_ids:
                    location_id = locat_ids[0]
            if location_id and cate_name != 'finish':
                sql = '''
                SELECT sum(onhand_qty) onhand_qty
                From
                (SELECT
                       
                    case when loc1.usage != 'internal' and loc2.usage = 'internal' and loc2.id = %s
                    then stm.primary_qty
                    else
                    case when loc1.usage = 'internal' and loc2.usage != 'internal' and loc1.id = %s
                    then -1*stm.primary_qty 
                    else 0.0 end
                    end onhand_qty
                            
                FROM stock_move stm 
                    join stock_location loc1 on stm.location_id=loc1.id
                    join stock_location loc2 on stm.location_dest_id=loc2.id
                WHERE stm.state= 'done' and product_id=%s)foo
                '''%(location_id,location_id,order_line['product_id'])
                cr.execute(sql)
                onhand_qty = cr.dictfetchone()['onhand_qty']
                if (order_line['product_qty'] > onhand_qty):
                    raise osv.except_osv(_('Warning!'),_('You are confirm %s but only %s available for this product in stock.' %(order_line['product_qty'], onhand_qty)))
        return new_id

    def onchange_create_uid(self, cr, uid, ids,create_uid=False, context=None):
        vals = {}
        user = self.pool.get('res.users').browse(cr,uid,uid)
        vals = {
                'department_id': user.employee_id and user.employee_id.department_id and user.employee_id.department_id.id,
                }
        return {'value': vals}
     
    def write(self, cr, uid, ids, vals, context=None):
#         if vals.get('name','/')=='/':
#             sql = '''
#                 select code from account_fiscalyear where '%s' between date_start and date_stop
#             '''%(time.strftime('%Y-%m-%d'))
#             cr.execute(sql)
#             fiscalyear = cr.dictfetchone()
#             if not fiscalyear:
#                 raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
#             else:
#                 sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.material.request.import')
#                 vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        new_write = super(tpt_material_request, self).write(cr, uid,ids, vals, context)
        product_obj = self.pool.get('product.product')
        for material in self.browse(cr,uid,ids):
            sql = '''
                select product_id, prodlot_id, sum(product_uom_qty) as product_qty from tpt_material_request_line where material_request_id = %s group by product_id,prodlot_id
                '''%(material.id)
            cr.execute(sql)
            for order_line in cr.dictfetchall():
                location_id = False
                locat_ids = []
                parent_ids = []
                product_id = product_obj.browse(cr,uid,order_line['product_id'])
                cate_name = product_id.categ_id and product_id.categ_id.cate_name or False
                if cate_name == 'finish':
                    lot = order_line['prodlot_id'] or False
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                        if lot:
                            sql = '''
                            SELECT sum(onhand_qty) onhand_qty
                            From
                            (SELECT
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and loc2.id = %s and prodlot_id = %s
                                then stm.primary_qty
                                else
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and loc1.id = %s and prodlot_id = %s
                                then -1*stm.primary_qty 
                                else 0.0 end
                                end onhand_qty
                                        
                            FROM stock_move stm 
                                join stock_location loc1 on stm.location_id=loc1.id
                                join stock_location loc2 on stm.location_dest_id=loc2.id
                            WHERE stm.state= 'done' and product_id=%s)foo
                            '''%(location_id,lot,location_id,lot,order_line['product_id'])
                        else:
                            sql = '''
                            SELECT sum(onhand_qty) onhand_qty
                            From
                            (SELECT
                                case when loc1.usage != 'internal' and loc2.usage = 'internal' and loc2.id = %s
                                then stm.primary_qty
                                else
                                case when loc1.usage = 'internal' and loc2.usage != 'internal' and loc1.id = %s
                                then -1*stm.primary_qty 
                                else 0.0 end
                                end onhand_qty
                                        
                            FROM stock_move stm 
                                join stock_location loc1 on stm.location_id=loc1.id
                                join stock_location loc2 on stm.location_dest_id=loc2.id
                            WHERE stm.state= 'done' and product_id=%s)foo
                            '''%(location_id,location_id,order_line['product_id'])
                        cr.execute(sql)
                        onhand_qty = cr.dictfetchone()['onhand_qty']
                        if (order_line['product_qty'] > onhand_qty):
                            raise osv.except_osv(_('Warning!'),_('You are confirm %s but only %s available for this product in stock.' %(order_line['product_qty'], onhand_qty)))
                if cate_name == 'raw':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                if cate_name == 'spares':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Spare'),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                if location_id and cate_name != 'finish':
                    sql = '''
                    SELECT sum(onhand_qty) onhand_qty
                    From
                    (SELECT
                           
                        case when loc1.usage != 'internal' and loc2.usage = 'internal' and loc2.id = %s
                        then stm.primary_qty
                        else
                        case when loc1.usage = 'internal' and loc2.usage != 'internal' and loc1.id = %s
                        then -1*stm.primary_qty 
                        else 0.0 end
                        end onhand_qty
                                
                    FROM stock_move stm 
                        join stock_location loc1 on stm.location_id=loc1.id
                        join stock_location loc2 on stm.location_dest_id=loc2.id
                    WHERE stm.state= 'done' and product_id=%s)foo
                    '''%(location_id,location_id,order_line['product_id'])
                    cr.execute(sql)
                    onhand_qty = cr.dictfetchone()['onhand_qty']
                    if (order_line['product_qty'] > onhand_qty):
                        raise osv.except_osv(_('Warning!'),_('You are confirm %s but only %s available for this product in stock.' %(order_line['product_qty'], onhand_qty)))
        return new_write

    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'done'})
        return True   

    def onchange_date_expect(self, cr, uid, ids,date_request=False, context=None):
        vals = {}
        if date_request :
            sql='''
            select date(date('%s')+INTERVAL '1 month 1days') as date_request
            '''%(date_request)
            cr.execute(sql)
            dates = cr.dictfetchone()['date_request']
        return {'value': {'date_expec':dates}}
    
    def onchange_request_type(self, cr, uid, ids,request_type=False, context=None):
        vals = {}
        if request_type:
            for request in self.browse(cr, uid, ids):
                for line in request.material_request_line:
                    sql = '''
                        update tpt_material_request_line set request_type = '%s' where id=%s
                    '''%(request_type,line.id)
                    cr.execute(sql)
        return {'value':vals} 
tpt_material_request()


class tpt_material_request_line(osv.osv):
    _name = "tpt.material.request.line"
    
    def _get_on_hand_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            sql = '''
                    select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id in (select id from stock_location
                                                                                        where usage = 'internal')
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id in (select id from stock_location
                                                                                        where usage = 'internal')
                            )foo
                '''%(line.product_id.id,line.product_id.id)
            cr.execute(sql)
            ton_sl = cr.dictfetchone()['ton_sl']
            
            res[line.id] = {
                'on_hand_qty': ton_sl,
            }
        return res
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Material Code',required = True),
        'dec_material':fields.text('Material Decription', readonly = True),
        'product_uom_qty': fields.float('Requested Qty',digits=(16,3) ),   
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'material_request_id': fields.many2one('tpt.material.request', 'Material'),
        'on_hand_qty':fields.function(_get_on_hand_qty,digits=(16,3),type='float',string='On Hand Qty',multi='sum',store=False),
        'request_type':fields.selection([('production', 'Production'),('normal', 'Normal'),('main', 'Maintenance')],'Request Type'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Batch No'),
                }
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        res = {'value':{
                    'dec_material': False,
                    }}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            res['value'].update({
                    'dec_material': product.name,
                    })
        return res
    
    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id,
                        'dec_material':product.name})    
        new_id = super(tpt_material_request_line, self).create(cr, uid, vals, context)
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id,
                        'dec_material':product.name})   
        new_write = super(tpt_material_request_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.product_uom_qty < 0:
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        return new_write
tpt_material_request_line()

class tpt_material_issue(osv.osv):
    _name = "tpt.material.issue"
    _columns = {
        'name': fields.many2one('tpt.material.request','Material Request No',required = True,states={'done':[('readonly', True)]}),
        'date_request':fields.date('Material Request Date',states={'done':[('readonly', True)]}),
        'date_expec':fields.date('Material Issue Date',states={'done':[('readonly', True)]}),
        'department_id':fields.many2one('hr.department','Department',readonly=True),
        'request_type':fields.selection([('production', 'Production'),('normal', 'Normal'),('main', 'Maintenance')],'Request Type', states={'done':[('readonly', True)]}),
        'material_issue_line':fields.one2many('tpt.material.issue.line','material_issue_id','Vendor Group',states={'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('done', 'Approve')],'Status', readonly=True),
        'doc_no': fields.char('Document Number', size = 1024,readonly = True),
                }
    _defaults = {
        'state':'draft',    
        'doc_no': '/',  
    }

#     def create(self, cr, uid, vals, context=None):
#         if 'name' in vals:
#             request = self.pool.get('tpt.material.request').browse(cr, uid, vals['name'])
#             vals.update({'date_request': request.date_request or False,
#                     })
#         return super(tpt_material_issue, self).create(cr, uid, vals, context=context)
# 
#     def write(self, cr, uid, ids, vals, context=None):
#         if 'name' in vals:
#             request = self.pool.get('tpt.material.request').browse(cr, uid, vals['name'])
#             vals.update({'date_request': request.date_request or False,
#                     })
#         return super(tpt_material_issue, self).write(cr, uid,ids, vals, context)
   
    def onchange_material(self, cr, uid, ids,name=False, context=None):
        vals = {}
        product_information_line = []
        for issue in self.browse(cr, uid, ids):
            sql = '''
                delete from tpt_material_issue_line where material_issue_id = %s
            '''%(issue.id)
            cr.execute(sql)
        if name:
            request = self.pool.get('tpt.material.request').browse(cr, uid, name)
            for line in request.material_request_line:
                rs = {
                      'product_id': line.product_id and line.product_id.id or False,
                      'product_uom_qty': line.product_uom_qty or False,
                      'uom_po_id': line.uom_po_id and line.uom_po_id.id or False,
                      'dec_material':line.dec_material or False,
                      'product_isu_qty': line.product_uom_qty or False,
                      
                      }
                product_information_line.append((0,0,rs))
            vals = {'date_request': request.date_request or False,
                    'date_expec':request.date_expec or False,
                    'department_id':request.department_id and request.department_id.id or False,
                    'material_issue_line':product_information_line,
                    'request_type': request.request_type,
                    }
        return {'value': vals}

    def bt_approve(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
        for line in self.browse(cr, uid, ids):
            for p in line.material_issue_line:
                rs = {
                      'name': '/',
                      'product_id':p.product_id and p.product_id.id or False,
                      'product_qty':p.product_isu_qty or False,
                      'product_uom':p.uom_po_id and p.uom_po_id.id or False,
                      'location_id':line.warehouse and line.warehouse.id or False,
                      'location_dest_id':location_ids[0],
                      
                      }
                move_id = move_obj.create(cr,uid,rs)
                move_obj.action_done(cr, uid, [move_id])
        return self.write(cr, uid, ids,{'state':'done'})

    def onchange_date_expect(self, cr, uid, ids,date_request=False, context=None):
        vals = {}
        if date_request :
            sql='''
            select date(date('%s')+INTERVAL '1 month 1days') as date_request
            '''%(date_request)
            cr.execute(sql)
            dates = cr.dictfetchone()['date_request']
        return {'value': {'date_expec':dates}}    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('doc_no','/')=='/':
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.material.issue.import')
                vals['doc_no'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
        if 'name' in vals:
            request = self.pool.get('tpt.material.request').browse(cr, uid, vals['name'])
        
            vals.update({'department_id':request.department_id.id}) 
        new_id = super(tpt_material_issue, self).create(cr, uid, vals, context)
        return new_id
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'department_id' in vals:
            department_id = self.pool.get('hr.department').browse(cr, uid, vals['department_id'])
            if department_id:
                vals.update({'department_id':department_id.id})   
        new_write = super(tpt_material_issue, self).write(cr, uid,ids, vals, context)
        return new_write
    
tpt_material_issue()

class tpt_material_issue_line(osv.osv):
    _name = "tpt.material.issue.line"
    _columns = {
        'product_id': fields.many2one('product.product', 'Material Code',readonly = True),
        'dec_material':fields.text('Material Decription',readonly = True),
        'product_uom_qty': fields.float('Requested Qty',digits=(16,3),readonly = True),  
        'product_isu_qty': fields.float('Issue Qty',digits=(16,3),required = True), 
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'material_issue_id': fields.many2one('tpt.material.issue', 'Material'),
                }
    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})    
        new_id = super(tpt_material_issue_line, self).create(cr, uid, vals, context)
        if 'product_isu_qty' in vals:
            if (vals['product_isu_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Issue Quantity is not allowed as negative values'))
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})    
        new_write = super(tpt_material_issue_line, self).write(cr, uid,ids, vals, context)
        for line in self.browse(cr,uid,ids):
            if line.product_isu_qty < 0:
                raise osv.except_osv(_('Warning!'),_('Issue Quantity is not allowed as negative values'))
        return new_write
tpt_material_issue_line()

