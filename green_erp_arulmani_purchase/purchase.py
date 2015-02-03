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
        'date_indent':fields.date('Indent Date',required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'document_type':fields.selection([
                                ('base','VV Level Based PR'),
                                ('capital','VV Capital PR'),
                                ('local','VV Local Purchase PR'),
                                ('maintenance','VV Maintenance PR'),
                                ('consumable','VV Consumable PR'),
                                ('outside','VV Outside Service PR'),
                                ('spare','VV Spare (Project) PR'),
                                ('service','VV Service PR'),
                                ],'Document Type',required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'intdent_cate':fields.selection([
                                ('emergency','Emergency Indent'),
                                ('normal','Normal Indent')],'Indent Category',required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'department_id':fields.many2one('hr.department','Department',required = True,  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'create_uid':fields.many2one('res.users','Raised By', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date_expect':fields.date('Expected Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'select_normal':fields.selection([('single','Single Quotation'),
                                          ('special','Special Quotation'),
                                          ('multiple','Multiple Quotation')],'Select', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_id':fields.many2one('res.partner','Supplier',  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'reason':fields.text('Reason', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'purchase_product_line':fields.one2many('tpt.purchase.product','purchase_indent_id','Materials', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Closed'),('done', 'Approve')],'Status', readonly=True),
    }
    _defaults = {
        'state':'draft',
        'date_indent': fields.datetime.now,
        'name': '/',
        'intdent_cate':'normal',
        'document_type':'base',
    }
    
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'done'})
        return True   
    
    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'cancel'})
        return True   

    def create(self, cr, uid, vals, context=None):
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
        return super(tpt_purchase_indent, self).create(cr, uid, vals, context=context)    
    
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
      
        return super(tpt_purchase_indent, self).write(cr, uid,ids, vals, context)
    
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
        return super(tpt_purchase_indent, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)

tpt_purchase_indent()
class tpt_purchase_product(osv.osv):
    _name = 'tpt.purchase.product'
    _columns = {
        'purchase_indent_id':fields.many2one('tpt.purchase.indent','Purchase Product'),
        'product_id': fields.many2one('product.product', 'Material Code',required = True),
        'dec_material':fields.text('Material Decription',required = True),
        'product_uom_qty': fields.float('PO Qty'),   
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        'pending_qty': fields.float('Pending Qty'), 
        'recom_vendor_id': fields.many2one('res.partner', 'Recommended Vendor'),
        'release_by':fields.selection([('1','Store Level'),('2','HOD Level')],'Released By',required = True)
        }  

    def create(self, cr, uid, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        return super(tpt_purchase_product, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'product_id' in vals:
            product = self.pool.get('product.product').browse(cr, uid, vals['product_id'])
            vals.update({'uom_po_id':product.uom_id.id})
        if 'product_uom_qty' in vals:
            if (vals['product_uom_qty'] < 0):
                raise osv.except_osv(_('Warning!'),_('Quantity is not allowed as negative values'))
        return super(tpt_purchase_product, self).write(cr, uid,ids, vals, context)
    
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
    
    def _check_product_category(self, cr, uid, ids, context=None):
        for pro_cate in self.browse(cr, uid, ids, context=context):
            sql = '''
                 select id from product_category where id != %s and lower(name) = lower('%s') and cate_name = '%s'
             '''%(pro_cate.id,pro_cate.name,pro_cate.cate_name)
            cr.execute(sql)
            code_ids = [row[0] for row in cr.fetchall()]
            if code_ids:
                raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))
#             pro_cate_ids = self.search(cr, uid, [('id','!=',pro_cate.id),('name','=',pro_cate.name),('cate_name', '=',pro_cate.cate_name)])
#             if pro_cate_ids:
#                 raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))    
                return False
            return True
        
    _constraints = [
        (_check_product_category, 'Identical Data', ['name', 'cate_name']),
#         (_check_code_id, 'Identical Data', ['name']),
    ]    
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
        }
    
    _defaults = {
        'categ_id': False,
        'sale_ok': False,
        'purchase_ok': False,
                 }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
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
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
   
    def _check_product(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            product_ids = self.search(cr, uid, [('id','!=',product.id),('name','=',product.name),('default_code', '=',product.default_code)])
            if product_ids:
                raise osv.except_osv(_('Warning!'),_('  Product Code and Name should be Unique. !'))
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
                    }
            elif category.cate_name == 'raw':
                vals = {'sale_ok':False,
                    'purchase_ok':True,
                    'batch_appli_ok':False,
                    'cate_name':'raw',
                    }
            else :
                vals = {'sale_ok':False,
                    'purchase_ok':True,
                    'batch_appli_ok':False,
                    'cate_name':category.cate_name,
                    }
        return {'value': vals}   
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
        'name': fields.char('Gate In Pass No', size = 1024, readonly=True),
        'po_id': fields.many2one('purchase.order', 'PO Number', required = True),
        'supplier_id': fields.many2one('res.partner', 'Supplier', required = True),
        'po_date': fields.datetime('PO Date'),
        'gate_date_time': fields.datetime('Gate In Pass Date & Time'),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'gate_in_pass_line': fields.one2many('tpt.gate.in.pass.line', 'gate_in_pass_id', 'Product Details'),
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
                            'po_indent_no': line.po_indent_no and line.po_indent_no.id or False,
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
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val1 = 0.0
            val2 = 0.0
            val3 = 0.0
            for quotation in line.purchase_quotation_line:
                val1 += quotation.sub_total
            res[line.id]['amount_untaxed'] = val1
            val2 = val1 * line.tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
            val3 = val1 + val2
            res[line.id]['amount_total'] = val3
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.purchase.quotation.line').browse(cr, uid, ids, context=context):
            result[line.purchase_quotation_id.id] = True
        return result.keys()
    _columns = {
        'name':fields.char('Quotation No ', size = 1024, readonly = True ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date_quotation':fields.date('Quotation Date',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_id': fields.many2one('res.partner', 'Supplier',required = True,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_location_id': fields.char( 'Supplier Location', size = 1024 ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'quotation_cate':fields.selection([
                                  ('multiple','Multiple Quotation')],'Quotation Category'),
        'quotation_ref':fields.char('Quotation Reference',size = 1024),
        'tax_id': fields.many2one('account.tax', 'Taxes',required=True ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'purchase_quotation_line':fields.one2many('tpt.purchase.quotation.line','purchase_quotation_id','Quotation Line' ,states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_untaxed': fields.function(amount_all_quotation_line, multi='sums',string='Untaxed Amount',
                                         store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10),}, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_tax': fields.function(amount_all_quotation_line, multi='sums',string='Taxes',
                                      store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10), }, 
            states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'amount_total': fields.function(amount_all_quotation_line, multi='sums',string='Total',
                                        store={
                'tpt.purchase.quotation': (lambda self, cr, uid, ids, c={}: ids, ['purchase_quotation_line'], 10),
                'tpt.purchase.quotation.line': (_get_order, ['price_unit', 'sub_total', 'product_uom_qty'], 10), },
             states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'name': '/',
        'date_quotation':fields.datetime.now,
        }  
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'purchase.quotation') or '/'
        return super(tpt_purchase_quotation, self).create(cr, uid, vals, context=context)  
    
    def onchange_supplier_location(self, cr, uid, ids,supplier_id=False, context=None):
        vals = {}
        if supplier_id :
            supplier = self.pool.get('res.partner').browse(cr, uid, supplier_id)
            vals = {
                    'supplier_location_id':supplier.city,
                    }
        return {'value': vals}

#     def bt_approve(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids):
#             self.write(cr, uid, ids,{'state':'done'})
#         return True   
#     
#     def bt_cancel(self, cr, uid, ids, context=None):
#         for line in self.browse(cr, uid, ids):
#             self.write(cr, uid, ids,{'state':'cancel'})
#         return True   

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
            self.write(cr, uid, ids,{'state':'cancel'})
        return True    
   
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
    
    def subtotal_purchase_quotation_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        subtotal = 0.0
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
               'sub_total' : 0.0,
               }
            subtotal = (line.product_uom_qty * line.price_unit)
            res[line.id]['sub_total'] = subtotal
        return res
    _columns = {
        'purchase_quotation_id':fields.many2one('tpt.purchase.quotation','Purchase Quotitation', ondelete = 'cascade'),
        'po_indent_id':fields.many2one('tpt.purchase.indent','PO Indent',required = True),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.float('Quantity', readonly=True),   
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly=True),
        'price_unit': fields.float('Unit Price', readonly=True),
        'sub_total': fields.function(subtotal_purchase_quotation_line, multi='deltas' ,string='SubTotal'),
        }
    
    def create(self, cr, uid, vals, context=None):
        if 'po_indent_id' in vals:
            if 'product_id' in vals:
                indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, vals['po_indent_id'])
                for line in indent.purchase_product_line:
                    if vals['product_id'] == line.product_id.id:
                        vals.update({
                                'uom_po_id':line.uom_po_id.id,
                                'product_uom_qty':line.product_uom_qty,
                                })
        return super(tpt_purchase_quotation_line, self).create(cr, uid, vals, context)    
  
    def write(self, cr, uid, vals, context=None):
        if 'po_indent_id' in vals:
            if 'product_id' in vals:
                indent = self.pool.get('tpt.purchase.indent').browse(cr, uid, vals['po_indent_id'])
                for line in indent.purchase_product_line:
                    if vals['product_id'] == line.product_id.id:
                        vals.update({
                                'uom_po_id':line.uom_po_id.id,
                                'product_uom_qty':line.product_uom_qty,
                                })
        return super(tpt_purchase_quotation_line, self).create(cr, uid, vals, context)    
    
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

    def _check_quotation(self, cr, uid, ids, context=None):
        for quotation in self.browse(cr, uid, ids, context=context):
            quotation_ids = self.search(cr, uid, [('id','!=',quotation.id),('po_indent_id','=',quotation.po_indent_id.id),('product_id', '=',quotation.product_id.id),('purchase_quotation_id','=',quotation.purchase_quotation_id.id)])
            if quotation_ids:
                raise osv.except_osv(_('Warning!'),_('PO Indent and Product were existed !'))
                return False
            return True
        
    _constraints = [
        (_check_quotation, 'Identical Data', ['po_indent_id', 'product_id']),
    ]       
    
tpt_purchase_quotation_line()

class tpt_gate_in_pass_line(osv.osv):
    _name = "tpt.gate.in.pass.line"
    _columns = {
        'gate_in_pass_id': fields.many2one('tpt.gate.in.pass','Gate In Pass',ondelete = 'cascade'),
        'po_indent_no': fields.many2one('tpt.purchase.indent', 'PO Indent No'),
        'product_id': fields.many2one('product.product', 'Product'),
        'product_qty': fields.float('Quantity'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
                }
    _defaults={
               'product_qty': 1,
    }
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {
                    'uom_po_id':product.uom_id.id,
                    }
        return {'value': vals}
      
tpt_gate_in_pass_line()

class tpt_spec_parameters_line(osv.osv):
    _name = "tpt.spec.parameters.line"
    _columns = {
        'product_id': fields.many2one('product.product','Product',ondelete = 'cascade'),
        'name': fields.char('Testing Parameters', size = 1024, required = True),
        'required_spec': fields.float('Required Specifications'),
        'uom_po_id': fields.many2one('product.uom', 'UOM'),
                }
      
tpt_spec_parameters_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val1 = 0.0
            val2 = 0.0
            val3 = 0.0
            for po in line.order_line:
                val1 += po.price_subtotal
            res[line.id]['amount_untaxed'] = val1
            val2 = val1 * line.purchase_tax_id.amount / 100
            res[line.id]['amount_tax'] = val2
            val3 = val1 + val2
            res[line.id]['amount_total'] = val3
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    _columns = {
        'po_document_type':fields.selection([('asset','VV Asset PO'),('standard','VV Standard PO'),('local','VV Local PO'),('return','VV Return PO'),('service','VV Service PO'),('out','VV Out Service PO')],'PO Document Type'),
        'quotation_no': fields.many2one('tpt.purchase.quotation', 'Quotation No'),
        'purchase_tax_id': fields.many2one('account.tax', 'Taxes', domain="[('type_tax_use','=','purchase')]", required = True), 
        'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums",help="The total amount"),
                }
    
    _default = {
        'name':'/',
               }
   
    def onchange_quotation_no(self, cr, uid, ids,quotation_no=False, context=None):
        vals = {}
        po_line = []
        if quotation_no:
            quotation = self.pool.get('tpt.purchase.quotation').browse(cr, uid, quotation_no)
            for line in quotation.purchase_quotation_line:
                rs = {
                      'po_indent_no': line.po_indent_id and line.po_indent_id.id or False,
                      'product_id': line.product_id and line.product_id.id or False,
                      'product_qty': line.product_uom_qty or False,
                      'product_uom': line.uom_po_id and line.uom_po_id.id or False,
                      'price_unit': line.price_unit or False,
                      'price_subtotal': line.sub_total or False,
                      'date_planned':quotation.date_quotation or False,
#                       'name':'/'
                      }
                po_line.append((0,0,rs))
            vals = {
                    'partner_id':quotation.supplier_id and quotation.supplier_id.id or '',
                    'partner_ref':quotation.quotation_ref or '',
                    'purchase_tax_id':quotation.tax_id and quotation.tax_id.id or '',
                    'order_line': po_line,
                    }
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
            
        date_order = datetime.datetime.strptime(new.date_order,'%Y-%m-%d')
        date_order_month = date_order.month
        date_order_year = date_order.year
        sql = '''
                select sum(amount_total) as total from purchase_order where EXTRACT(month from date_order) = %s and EXTRACT(year from date_order) = %s
        '''%(date_order_month,date_order_year)
        cr.execute(sql)
        amount_total = cr.dictfetchone()
        if (amount_total['total'] > 2000000):
            raise osv.except_osv(_('Warning!'),_('The Emergency Purchase reaches 2 Lakhs Limit (2,000,000) in the current month. This can be processed only when the next month starts'))
        if new.po_document_type == 'local':
            if new.quotation_no and new.quotation_no.quotation_cate:
                if (new.amount_total > 5000):
                    raise osv.except_osv(_('Warning!'),_('Can not process because Total > 5000 for VV Local PO'))
                
        if 'quotation_no' in vals:
            for line in new.order_line:
                if line.po_indent_no and line.product_id:
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
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            if (new.po_document_type=='asset'):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.asset')
                sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
                cr.execute(sql)
            if (new.po_document_type=='standard'):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.standard')
                sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
                cr.execute(sql)
            if (new.po_document_type=='local'):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.local')
                sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
                cr.execute(sql)
            if (new.po_document_type=='return'):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.return')
                sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
                cr.execute(sql)
            if (new.po_document_type=='service'):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.service')
                sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
                cr.execute(sql)
            if (new.po_document_type=='out'):
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.out.service')
                sql = '''update purchase_order set name='%s' where id =%s'''%(sequence+'/'+fiscalyear['code']or '/',new.id)
                cr.execute(sql)
            date_order = datetime.datetime.strptime(new.date_order,'%Y-%m-%d')
            
        date_order_month = date_order.month
        date_order_year = date_order.year
        sql = '''
                select sum(amount_total) as total from purchase_order where EXTRACT(month from date_order) = %s and EXTRACT(year from date_order) = %s
        '''%(date_order_month,date_order_year)
        cr.execute(sql)
        amount_total = cr.dictfetchone()
        if (amount_total['total'] > 2000000):
            raise osv.except_osv(_('Warning!'),_('The Emergency Purchase reaches 2 Lakhs Limit (2,000,000) in the current month. This can be processed only when the next month starts'))
        
            if new.po_document_type == 'local':
                if new.quotation_no and new.quotation_no.quotation_cate:
                    if (new.amount_total > 5000):
                        raise osv.except_osv(_('Warning!'),_('Can not process because Total > 5000 for VV Local PO'))
                    
        if 'quotation_no' in vals:
            for line in new.order_line:
                if line.po_indent_no and line.product_id:
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
                        
        return new_write
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_po_id'):
            sql = '''
                select id from purchase_order 
                where state != 'cancel' and id not in (select po_id from tpt_gate_in_pass gate,purchase_order po where gate.po_id = po.id and gate.state != 'cancel')
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
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id.id,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit,
            'po_indent_id': order_line.po_indent_no and order_line.po_indent_no.id or False,
        }
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    
    
    _columns = {
        'po_indent_no' : fields.many2one('tpt.purchase.indent', 'PO Indent No'),
                }
    _defaults = {
                 'date_planned':time.strftime('%Y-%m-%d'),
                 }
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
        'product_detail_line': fields.one2many('tpt.product.detail.line', 'request_id', 'Product Detail', states={'cancel': [('readonly', True)],'done':[('readonly', True)]}), 
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
        'product_id': fields.many2one('product.product', 'Product'),
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
        'qty':fields.float('Qty',states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Rejected'),('done', 'Approved')],'Status', readonly=True),
                }
    _defaults = {
        'state':'draft',
                 }

    def bt_approve(self,cr,uid,ids,context=None):
        move_obj = self.pool.get('stock.move')
        for line in self.browse(cr,uid,ids):
            move_obj.action_done(cr, uid, [line.need_inspec_id.id])
        return self.write(cr, uid, ids, {'state':'done'})
    
    def bt_reject(self,cr,uid,ids,context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        for line in self.browse(cr,uid,ids):
            move_obj.action_cancel(cr, uid, [line.need_inspec_id.id])
            picking_obj.do_partial(cr, uid, [line.name.id], {})
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
        'value' : fields.float('Value',required = True),
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
        'product_id': fields.many2one('product.product', 'Product'),
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
    
    _columns = {
        'name': fields.char('RFQ No', size = 1024,readonly=True, required = True ),
        'rfq_date': fields.datetime('RFQ Date'),
        'rfq_category': fields.selection([('single','Single'),('mutiple','Multiple'),('special','Special')],'RFQ Category'),   
        'create_on': fields.datetime('Created on'),
        'expect_quote_date': fields.date('Expected Quote Date'),
        'rfq_line': fields.one2many('tpt.rfq.line', 'rfq_id', 'RFQ Line'), 
        'rfq_supplier': fields.one2many('tpt.rfq.supplier', 'rfq_id', 'Supplier Line'), 
                }
    _defaults={
               'name':'/',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.rfq.import') or '/'
        return super(tpt_request_for_quotation, self).create(cr, uid, vals, context=context)
    
tpt_request_for_quotation()

class tpt_rfq_line(osv.osv):
    _name = 'tpt.rfq.line'
    _columns = {
        'rfq_id': fields.many2one('tpt.request.for.quotation','RFQ'),
        'po_indent_id':fields.many2one('tpt.purchase.indent','PO Indent', required = True),
        'product_id': fields.many2one('product.product', 'Material',required = True),
        'product_uom_qty': fields.float('Quantity'),   
        'uom_id': fields.many2one('product.uom', 'UOM', readonly = True),
        }  

tpt_rfq_line()

class tpt_rfq_supplier(osv.osv):
    _name = 'tpt.rfq.supplier'
    _columns = {
        'rfq_id': fields.many2one('tpt.request.for.quotation','RFQ'),
        'vendor_id':fields.many2one('res.partner','Vendor Name', required = True),
        'state_id': fields.many2one('res.country.state', 'Vendor Location'),
        'quotation_no_id': fields.many2one('tpt.purchase.quotation', 'Quotation No'),
#         'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
        }  

tpt_rfq_supplier()

class res_partner(osv.osv):
    _inherit = "res.partner"   
    _columns = {
#         'supplier_code':fields.char('Vendor Code', size = 256),
        'vendor_code':fields.char('Vendor Code', size = 20, required = True),
        'contact_per':fields.char('Contact Person', size = 1024),
        'vendor_tag':fields.char('Tag', size = 1024),
        'pur_orgin_code_id':fields.many2one('tpt.pur.organi.code','Purchase Organisation Code'),
        'vendor_group_id':fields.many2one('tpt.vendor.group','Vendor Class (Group)', required = True),
        'vendor_sub_group_id':fields.many2one('tpt.vendor.sub.group','Vendor Sub Class (Sub Group)'),   
                
                }
    def onchange_vendor_group_id(self, cr, uid, ids,vendor_group_id=False, context=None):
        return {'value': {'vendor_sub_group_id': False}}

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
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
  
res_partner()    
