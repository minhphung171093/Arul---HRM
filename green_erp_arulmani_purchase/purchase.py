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
        'raised_from_id':fields.many2one('hr.department','Indent Raised From',required = True,  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'raised_by_id':fields.many2one('hr.employee','Raised By', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date_expect':fields.date('Expected Date', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'select_normal':fields.selection([('single','Single Quotation'),
                                          ('special','Special Quotation'),
                                          ('multiple','Multiple Quotation')],'Select', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'supplier_id':fields.many2one('res.partner','Supplier',  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'reason':fields.text('Reason', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'purchase_product_line':fields.one2many('tpt.purchase.product','purchase_indent_id','Product', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Closed'),('done', 'Approve')],'Status', readonly=True),
    }
    _defaults = {
        'state':'draft',
        'date_indent': fields.datetime.now,
        'name': '/',
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
                        sequence = self.pool.get('ir.sequence').get(cr, uid, 'indent.purchase.capital')
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

tpt_purchase_indent()
class tpt_purchase_product(osv.osv):
    _name = 'tpt.purchase.product'
    _columns = {
        'purchase_indent_id':fields.many2one('tpt.purchase.indent','Purchase Product'),
        'product_id': fields.many2one('product.product', 'Product',required = True),
        'product_uom_qty': fields.float('Quantity'),   
        'uom_po_id': fields.many2one('product.uom', 'UOM', readonly = True),
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

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'supplier_code':fields.char('Supplier Code', size = 1024),
        }
res_partner()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'cate_name':fields.selection([('raw','Raw Materials'),('finish','Finished Product'),('spares','Spares'),('consum','Consumables')], 'Category Name', required = True),
        'description':fields.text('Description'),
        }
    
    def _check_product_category(self, cr, uid, ids, context=None):
        for pro_cate in self.browse(cr, uid, ids, context=context):
            pro_cate_ids = self.search(cr, uid, [('id','!=',pro_cate.id),('name','=',pro_cate.name),('cate_name', '=',pro_cate.cate_name)])
            if pro_cate_ids:
                raise osv.except_osv(_('Warning!'),_(' Product Category Code and Name should be unique!'))
                return False
            return True
        
    _constraints = [
        (_check_product_category, 'Identical Data', ['name', 'cate_name']),
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
                        where st.state='done' and st.product_id=2 and l2.usage = 'internal'
                    union all
                    select l1.id as loc,st.prodlot_id,pu.id,st.product_qty*-1
                        from stock_move st 
                            inner join stock_location l1 on st.location_id= l1.id
                            inner join product_uom pu on st.product_uom = pu.id
                        where st.state='done' and st.product_id=%s and l1.usage = 'internal'
                    )foo
                    group by foo.loc,foo.prodlot_id,foo.id
            '''%(id)
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
        'inventory_line':fields.function(_inventory, method=True,type='one2many', relation='tpt.product.inventory', string='Inventory'),
        }
    
    _defaults = {
        'categ_id': False,
        'sale_ok': False,
        'purchase_ok': False,
                 }
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
#         if context and context.get('search_default_categ_id', False):
#             args.append((('categ_id', 'child_of', context['search_default_categ_id'])))
        if context.get('search_product'):
            if context.get('po_indent_id'):
                sql = '''
                    select product_id from tpt_purchase_product where purchase_indent_id in(select id from tpt_purchase_indent where id = %s)
                '''%(context.get('po_indent_id'))
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
        'product_id':fields.many2one('product.product', 'Product'),
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
        'gate_in_pass_line': fields.one2many('tpt.gate.in.pass.line', 'gate_in_pass_id', 'Product Details'),
                }
    _defaults={
               'name':'/',
               'gate_date_time': time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
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
#                             'po_indent_no': line.
                          'product_id': line.product_id.id,
                          'product_qty':line.product_qty,
                          'uom_po_id': line.product_uom.id,
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
        'name':fields.char('Quotation No ', size = 1024, readonly = True),
        'date_quotation':fields.date('Quotation Date'),
        'supplier_id': fields.many2one('res.partner', 'Supplier',required = True),
        'supplier_location_id': fields.char( 'Supplier Location', size = 1024),
        'quotation_cate':fields.selection([('single','Single Quotation'),
                                  ('special','Special Quotation'),
                                  ('multiple','Multiple Quotation')],'Quotation Category'),
        'quotation_ref':fields.char('Quotation Reference',size = 1024),
        'tax_id': fields.many2one('account.tax', 'Taxes',required=True),
        'purchase_quotation_line':fields.one2many('tpt.purchase.quotation.line','purchase_quotation_id','Quotation Line'),
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
        'price_unit': fields.float('Unit Price'),
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
