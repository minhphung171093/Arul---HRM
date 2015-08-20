# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class tpt_stock_on_hand(osv.osv_memory):
    _name = "tpt.stock.on.hand"
    _columns = {
        'name': fields.char('', readonly=True),
        'categ_id': fields.many2one('product.category', 'Material Category', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Material Code', ondelete='cascade'),
        'location_id': fields.many2one('stock.location', 'Warehouse Location', ondelete='cascade'),
        'stock_line': fields.one2many('tpt.stock.on.hand.line', 'stock_id', 'Stock Line'),
        'as_date': fields.date('As on Date'),
        'is_mrp': fields.boolean('Is MRP Type'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.stock.on.hand'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_on_hand_xls', 'datas': datas}
#     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.stock.on.hand'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_on_hand_pdf', 'datas': datas}
    
tpt_stock_on_hand()

class tpt_stock_on_hand_line(osv.osv_memory):
    _name = "tpt.stock.on.hand.line"
    _columns = {
        'stock_id': fields.many2one('tpt.stock.on.hand', 'Line'),
        'code': fields.char('Code', size = 1024),
        'description': fields.char('Mat.Description', size = 1024),
        'uom': fields.char('UOM'),
        'bin_loc': fields.char('Bin Loc.'),
        'onhand_qty': fields.float('On hand Qty',digits=(16,3)),
        'ins_qty': fields.float('Ins.Qty',digits=(16,3)),
        'bl_qty': fields.float('Bl.Qty',digits=(16,3)),
        'mrp': fields.char('MRP'),
        'min_stock': fields.float('Min Stock',digits=(16,3)),
        'max_stock': fields.float('Max Stock',digits=(16,3)),
        're_stock': fields.float('Re-Order Stock',digits=(16,3)),
        'unit_price': fields.float('Unit Price',),
    }

tpt_stock_on_hand_line()

class stock_on_hand_report(osv.osv_memory):
    _name = "stock.on.hand.report"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Material Category'),
                'product_id': fields.many2one('product.product', 'Material Name'),
                'location_id':fields.many2one('stock.location', 'Warehouse Location', required=True),
                'is_mrp': fields.boolean('Is MRP Type'),
                }
    def onchange_categ_id(self, cr, uid, ids,categ_id=False, context=None):
        if categ_id:
            return {'value': {
                              'location_id': False,
                              'product_id': False,
                              } }
    def onchange_product_id(self, cr, uid, ids, categ_id=False, product_id=False, context=None):
        if categ_id and not product_id:
            return {'value': {
                                  'location_id': False,
                                  'product_id': False,
                                  } }
        elif categ_id and product_id:
            return {'value': {
                              'location_id': False,
                              } }
        elif product_id and not categ_id:
            return {'value': {
                              'location_id': False,
                              } }
    
    
    def print_report(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'stock.on.hand.report'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_on_hand', 'datas': datas}
#         def convert_date(self,date):
#             if date:
#                 date = datetime.strptime(date, DATE_FORMAT)
#                 return date.strftime('%d/%m/%Y')
    
#         def get_date(o):
#             date = time.strftime('%Y-%m-%d'),
#             date = datetime.strptime(date[0], DATE_FORMAT)
#             return date.strftime('%d/%m/%Y')
        
        def get_warehouse(o):
            loc = o.location_id.id
            loc_obj = self.pool.get('stock.location').browse(cr,uid,loc)
            return loc_obj   
        
        def get_category(o):
            cat = o.categ_id and o.categ_id.id or False
            if cat:
                cat_obj = self.pool.get('product.category').browse(cr,uid,cat)
                return cat_obj
            return False
        
        def get_product(o):
            pro = o.product_id and o.product_id.id or False
            if pro:
                pro_obj = self.pool.get('product.product').browse(cr,uid,pro)
                return pro_obj
            return False
    
        def get_categ(o):
            loc = o.location_id.id
            categ = o.categ_id and o.categ_id.id or False
            product = o.product_id and o.product_id.id or False
            is_mrp = o.is_mrp
            pro_obj = self.pool.get('product.product')
            categ_ids = []
    
            if is_mrp is True:               
                if categ and product:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                                and product_product.product_tmpl_id = product_template.id and product_product.id = %s 
                                and product_product.mrp_control='t';
                    '''%(categ,product)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return self.pool.get('product.product').browse(cr,uid,categ_ids)
                if categ:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                                and product_product.product_tmpl_id = product_template.id and product_product.mrp_control='t';
                    '''%(categ)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return pro_obj.browse(cr,uid,categ_ids)
                if product and not categ:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category) 
                                and product_product.product_tmpl_id = product_template.id and product_product.id = %s and product_product.mrp_control='t';
                    '''%(product)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return self.pool.get('product.product').browse(cr,uid,categ_ids)
                if not product and not categ :
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category) 
                                and product_product.product_tmpl_id = product_template.id  and product_product.mrp_control='t';
                    '''
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return self.pool.get('product.product').browse(cr,uid,categ_ids)
            else:
                if categ and product:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                                and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
                    '''%(categ,product)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return self.pool.get('product.product').browse(cr,uid,categ_ids)
                if categ:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                                and product_product.product_tmpl_id = product_template.id;
                    '''%(categ)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return pro_obj.browse(cr,uid,categ_ids)
                if product and not categ:
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category) 
                                and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
                    '''%(product)
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return self.pool.get('product.product').browse(cr,uid,categ_ids)
                if not product and not categ :
                    sql='''
                                select product_product.id 
                                from product_product,product_template 
                                where product_template.categ_id in(select product_category.id from product_category) 
                                and product_product.product_tmpl_id = product_template.id  ;
                    '''
                    cr.execute(sql)
                    categ_ids += [r[0] for r in cr.fetchall()]
                    return self.pool.get('product.product').browse(cr,uid,categ_ids)    
            
        def get_ton_sl(o,line):
            loc = o.location_id.id
            location = self.pool.get('stock.location').browse(cr,uid,loc)
            sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_id = %s
                                )foo
                        '''%(line.id,location.id,line.id,location.id)
            cr.execute(sql)
            ton_sl = cr.dictfetchone()
            return ton_sl and ton_sl['ton_sl'] or 0
        
        def get_ins_qty(o,line):
#             loc = o.location_id
#             location = self.pool.get('stock.location').browse(cr,uid,loc[0])
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Quality Inspection'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Inspection']),('location_id','=',parent_ids[0])])
            sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_id = %s
                                )foo
                        '''%(line.id,locat_ids[0],line.id,locat_ids[0])
            cr.execute(sql)
            ton = cr.dictfetchone()
            return ton and ton['ton'] or 0
        def get_blo_qty(o,line):
#             loc = o.location_id
#             location = self.pool.get('stock.location').browse(cr,uid,loc[0])
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_ids[0])])
            sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                                union all
                                select st.product_qty*-1
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_id = %s
                                )foo
                        '''%(line.id,locat_ids[0],line.id,locat_ids[0])
            cr.execute(sql)
            ton = cr.dictfetchone()
            return ton and ton['ton'] or 0 
        def get_mrp(o,line):
            sql = '''
                select mrp_control from product_product where id=%s
                        '''%(line.id)
            cr.execute(sql)
            mrp = cr.fetchone()
            mrp_type = mrp[0]
            if mrp_type is True:
                return 'Yes'
            else:
                return 'No'
        def get_min_stock(o,line):
            sql = '''
                select min_stock from product_product where id=%s
                        '''%(line.id)
            cr.execute(sql)
            mrp = cr.fetchone()
            min_stock = mrp[0]
            return min_stock or 0
        def get_max_stock(o,line):
            sql = '''
                select max_stock from product_product where id=%s
                        '''%(line.id)
            cr.execute(sql)
            mrp = cr.fetchone()
            max_stock = mrp[0]
            return max_stock or 0
        def get_re_stock(o,line):
            sql = '''
                select re_stock from product_product where id=%s
                        '''%(line.id)
            cr.execute(sql)
            mrp = cr.fetchone()
            re_stock = mrp[0]
            return re_stock or 0
        def get_unit_price(o,line):
            #===================================================================
            # sql = '''
            #     select standard_price from product_product where id=%s
            #             '''%(line.id)
            # cr.execute(sql) 
            # obj = cr.fetchone()
            # unit_price = obj[0]
            #===================================================================
            
            ##
            prod_obj = self.pool.get('product.product')
            acc = prod_obj.browse(cr,uid,line.id)
            unit_price = acc.standard_price
            
            return unit_price or 0
            
        
        cr.execute('delete from tpt_stock_on_hand')
        stock_obj = self.pool.get('tpt.stock.on.hand')
        stock = self.browse(cr, uid, ids[0])
        stock_line = []
        for line in get_categ(stock):
            stock_line.append((0,0,{
                'code': line.code or False,
                'description': line.name or False,
                'uom': line.uom_id and line.uom_id.name or False,
                'bin_loc': line.bin_location or False,
                'onhand_qty': get_ton_sl(stock,line),
                'ins_qty': get_ins_qty(stock,line),
                'bl_qty': get_blo_qty(stock,line),
                'mrp': get_mrp(stock,line),
                'min_stock': get_min_stock(stock,line),
                'max_stock': get_max_stock(stock,line),
                're_stock': get_re_stock(stock,line),
                'unit_price': get_unit_price(stock,line),
                
            }))
        vals = {
            'name': 'STOCK ON HAND REPORT',
            'categ_id': stock.categ_id and stock.categ_id.id or False,
            'product_id': stock.product_id and stock.product_id.id or False,
            'location_id': stock.location_id and stock.location_id.id or False,
            'is_mrp': stock.is_mrp,
            'stock_line': stock_line,
            'as_date': time.strftime('%Y-%m-%d'),
        }
        stock_id = stock_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_tpt_stock_on_hand_form')
        return {
                    'name': 'STOCK ON HAND REPORT',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.stock.on.hand',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': stock_id,
                }
    
stock_on_hand_report()

class product_product(osv.osv):
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_id'):
            if context.get('categ_id'):
                sql = '''
                     select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                        and product_product.product_tmpl_id = product_template.id;
                '''%(context.get('categ_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
product_product()

class stock_location(osv.osv):
    _inherit = "stock.location"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_location_id'):
            if context.get('product_id'):
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
                '''%(context.get('product_id'), context.get('product_id'))
                cr.execute(sql)
                ton_sl = cr.dictfetchone()['ton_sl']
                if ton_sl > 0:
                    sql = '''
                        select location_dest_id from stock_move where state = 'done' and product_id = %s and location_dest_id in (select id from stock_location
                                                                                        where usage = 'internal')
                    '''%(context.get('product_id'))
                    cr.execute(sql)
                    location_ids = [row[0] for row in cr.fetchall()]
                    args += [('id','in',location_ids)]
                else:
                    location_ids = []
                    raise osv.except_osv(_('Warning!'),_('Not exist any quantity in stock for this product!'))
                    args += [('id','in',location_ids)]
        return super(stock_location, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)

stock_location