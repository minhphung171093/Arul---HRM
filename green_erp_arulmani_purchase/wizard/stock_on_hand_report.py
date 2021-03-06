# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from global_utility import tpt_shared_component


class tpt_stock_on_hand(osv.osv):
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
        #datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.stock.on.hand'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_on_hand_xls', 'datas': datas}
#     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.stock.on.hand'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_on_hand_pdf', 'datas': datas}
    
tpt_stock_on_hand()

class tpt_stock_on_hand_line(osv.osv):
    _name = "tpt.stock.on.hand.line"
    _columns = {
        'stock_id': fields.many2one('tpt.stock.on.hand', 'Line'),
        'code': fields.char('Code', size = 1024),
        'description': fields.char('Mat.Description', size = 1024),
        'uom': fields.char('UOM'),
        'bin_loc': fields.char('Bin Loc.'),
        'onhand_qty': fields.float('On-Hand Qty',digits=(16,3)),
        'ins_qty': fields.float('Ins.Qty',digits=(16,3)),
        'bl_qty': fields.float('Bl.Qty',digits=(16,3)),
        'mrp': fields.char('MRP'),
        'min_stock': fields.float('MRP Min Stock',digits=(16,3)),
        'max_stock': fields.float('MRP Max Stock',digits=(16,3)),
        're_stock': fields.float('MRP Re-Order Stock',digits=(16,3)),
        'unit_price': fields.float('Unit Price(Avg Cost)',),
        'po_price': fields.float('Last PO Price',),
        
        'onhand_qty_blocklist': fields.float('Block List',digits=(16,3)),
        'onhand_qty_pl_other': fields.float('Production Line / Other',digits=(16,3)),   
        'onhand_qty_qa_ins': fields.float('Quality Inspection',digits=(16,3)),
        'onhand_qty_st_fsh': fields.float('Store / FSH',digits=(16,3)),
        'onhand_qty_st_rm': fields.float('Store / Raw Material',digits=(16,3)),
        'onhand_qty_st_spare': fields.float('Store / Spare',digits=(16,3)),
        'onhand_qty_st_tio2': fields.float('Store / TIO2',digits=(16,3)),
        'onhand_qty_pl_rm': fields.float('Production Line / Raw Material',digits=(16,3)),  
        'product_id': fields.many2one('product.product', 'Product'),
    }

tpt_stock_on_hand_line()

class stock_on_hand_report(osv.osv_memory):
    _name = "stock.on.hand.report"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Material Category'),
                'product_id': fields.many2one('product.product', 'Material Name'),
                'location_id':fields.many2one('stock.location', 'Warehouse Location',),
                'is_mrp': fields.boolean('Is MRP Type'),
                'date': fields.date('As on Date'),
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
            #===================================================================
            # sql = '''
            #                 select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
            #                     (select st.product_qty
            #                         from stock_move st 
            #                         where st.state='done' and st.product_id = %s and st.location_dest_id = %s
            #                     union all
            #                     select st.product_qty*-1
            #                         from stock_move st 
            #                         where st.state='done' and st.product_id = %s and st.location_id = %s
            #                     )foo
            #             '''%(line.id,location.id,line.id,location.id)
            #===================================================================
            sql = '''
                SELECT sum(onhand_qty) ton_sl
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
                   '''% (line.id)
            
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
            
        ###
        
        def get_blocklist(o,line):
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
        def get_pl_other(o,line):
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Other'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Other')])
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
        def get_qa_ins(o,line):
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
        def get_st_fsh(o,line):
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
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
        def get_st_rm(o,line):
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Raw Material'),('location_id','=',parent_ids[0])])
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
        def get_st_spare(o,line):
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Spares'),('location_id','=',parent_ids[0])])
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
        def get_st_tio2(o,line):
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','TIO2'),('location_id','=',parent_ids[0])])
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
        ### 
        ###
        ##TPT-START - TO ADDRESS PERFORMANCE ISSUE - BY BalamuruganPurushothaman  on 02/09/2015
        def get_prod(o):
            #TPT_BM-07/06/2016 - AS ON DATE AS PARAM
            if o.date:
                date = o.date
            else:
                date = time.strftime('%Y-%m-%d')
             # Modified by P.VINOTHKUMAR on 03/12/2016 sql script for fix restrict rejected qty displayed in on-hand field     
            sql = '''
                        select pp.id as product_id, pp.default_code, pt.name, pt.standard_price, pu.name as uom, pp.bin_location,
              pp.min_stock,  pp.max_stock,  pp.re_stock,
             (select case when sum(onhand_qty)>0 then sum(onhand_qty) else 0 end ton
                        From
                        (SELECT
                               
                            case when loc1.usage != 'internal' and loc2.usage = 'internal'
                            then stm.primary_qty
                            else
                            case when loc1.usage = 'internal' and loc2.usage != 'internal'
                            then -1*stm.primary_qty 
                            else
                            case when loc1.usage = 'internal' and loc2.usage = 'internal' and loc2.id=
                            (select id from stock_location where name='Block List' and usage='internal')
                            then -1*stm.primary_qty
                            else 0.0 end
                            end end onhand_qty
                                    
                        FROM stock_move stm 
                            join stock_location loc1 on stm.location_id=loc1.id
                            join stock_location loc2 on stm.location_dest_id=loc2.id
                        WHERE stm.state= 'done' and product_id=pp.id and stm.date <= '%(date)s')foo) onhand_qty,
            
            (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Raw Material' and 
                        usage='internal' and location_id=(select id from stock_location where name='Store'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and 
                        st.location_id =(select id from stock_location where name='Raw Material' and 
                        usage='internal' and location_id=(select id from stock_location where name='Store') and st.date <= '%(date)s')
                    )foo) store_rm,
                    
             (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.location_dest_id 
                        =(select id from stock_location where name='Spares' and 
                        usage='internal')
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.location_id 
                        =(select id from stock_location where name='Spares' and 
                        usage='internal' and st.date <= '%(date)s')
                    )foo) store_spare,
                    
            (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Inspection' and 
                        usage='internal')
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and 
                        st.location_id =(select id from stock_location where name='Inspection' and 
                        usage='internal') and st.date <= '%(date)s'
                    )foo) ins_qty,
            (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and 
                        st.location_dest_id =(select id from stock_location where name='Block List' and 
                        usage='internal') and st.date <= '%(date)s'
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and 
                        st.location_id =(select id from stock_location where name='Block List' and 
                        usage='internal') and st.date <= '%(date)s'
                    )foo) block_qty,
             (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and  st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Other' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_id =(select id from stock_location where name='Other' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    )foo) pl_others,
             (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='FSH' and 
                        usage='internal' and location_id=(select id from stock_location where name='Store'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_id =(select id from stock_location where name='FSH' and 
                        usage='internal' and location_id=(select id from stock_location where name='Store'))
                    )foo) store_fsh    ,
            (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='TIO2' and 
                        usage='internal' and location_id=(select id from stock_location where name='Store'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_id =(select id from stock_location where name='TIO2' and 
                        usage='internal' and location_id=(select id from stock_location where name='Store'))
                    )foo) store_tio2,
                    
            (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Raw Material' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_id =(select id from stock_location where name='Raw Material' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    )foo) pl_rm, 
                    
                    (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Ferric Sulphate' and 
                        usage='internal' )
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_id =(select id from stock_location where name='Ferric Sulphate' and 
                        usage='internal' )
                    )foo) pl_ferric,
                    
                    (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Other' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date <= '%(date)s' and
                        st.location_id =(select id from stock_location where name='Other' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    )foo) pl_other, 
                    
                    pp.id product_id, pp.cate_name as categ
            
            
            from product_product pp
            inner join product_template pt on pp.product_tmpl_id=pt.id 
            inner join product_uom pu on pt.uom_id=pu.id
            ''' % {'date':date}
            
            categ_id = o.categ_id and o.categ_id.id
            product_id = o.product_id and o.product_id.id
            is_mrp = stock.is_mrp
            
            #===================================================================
            # if stock.date:
            #     str = " inner join stock_move sm on pp.id=sm.product_id where sm.date >= '%s'" % (stock.date)
            #     sql = sql+str
            #===================================================================
            if categ_id or product_id or stock.is_mrp:
                str = " where"
                sql = sql+str
            if categ_id and not product_id and is_mrp is False:
                str = " pt.categ_id=%s" % categ_id
                sql = sql+str
            if not categ_id and product_id and is_mrp is False:
                str = " pp.id = %s" % product_id
                sql = sql+str 
            if not categ_id and not product_id and is_mrp is True:
                str = " pp.mrp_control = 't'"
                sql = sql+str 
            if categ_id and product_id and is_mrp is True:
                str = "  pt.categ_id=%s and pp.id = %s and pp.mrp_control = 't'" % (categ_id,product_id)
                sql = sql+str
            if categ_id and product_id and is_mrp is False:
                str = "  pt.categ_id=%s and pp.id = %s" % (categ_id,product_id)
                sql = sql+str
            if categ_id and not product_id and is_mrp is True :
                str = "  pt.categ_id=%s and pp.mrp_control = 't'" % (categ_id)
                sql = sql+str
            if not categ_id and product_id and is_mrp is True:
                str = " pp.id = %s and pp.mrp_control = 't'" % (product_id)
                sql = sql+str
            
            str = " order by pp.default_code asc"
            sql = sql+str
            cr.execute(sql)
            #print sql
            return cr.dictfetchall()
        ###
        def get_avg_cost(product_id, categ, std_price):
            avg_cost = 0
            if categ=='raw':
                location_id=15
            elif categ=='spares':
                location_id=14
            elif categ=='finish':
                if product_id==4 or product_id==9:
                    location_id=13
                elif product_id==2:
                    location_id=25
                else:
                    location_id=24
            avg_cost_obj = self.pool.get('tpt.product.avg.cost')        
            avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',product_id),('warehouse_id','=',location_id)])
            if avg_cost_ids:
                avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                avg_cost = avg_cost_id.avg_cost or 0
            if categ=='finish':
                avg_cost = std_price    
            if avg_cost == 0.00:
                sql='''select max(sm.id) as id from stock_move sm join product_product pp on sm.product_id=pp.id and pp.id=%s
                '''%(product_id)
                cr.execute(sql)
                price = cr.dictfetchone()['id']
                if price: 
                    sql='''select price_unit from stock_move where id=%s
                    '''%(price)
                    cr.execute(sql)
                    avg_cost = cr.dictfetchone()['price_unit']    
            return avg_cost or 0.00
        def get_lastpo_cost(product_id, categ, std_price):
            sql = '''
                select case when price_unit>0 then price_unit else 0 end avg_cost from purchase_order_line where id = (
                select max(id) from purchase_order_line pol
                where pol.product_id=%s)
            '''%(product_id)
            cr.execute(sql)
            avg = cr.dictfetchone()
            avg_cost = 0
            if avg:
                avg_cost=avg['avg_cost']
            if categ=='finish':
                avg_cost = 0.00
            return float(avg_cost)
       # Added by P.vinothkumar on 02/07/2016 for modify logics in stock on hand report
        def opening_stock(product_id, default_code):
            location = tpt_shared_component.warehouse_module() 
            location_id = location.get_finished_location(default_code) 
            sql='''
            select
            sum(st.product_qty) as product_qty
            from stock_move st
            where st.state='done' and st.product_id=%s and st.location_dest_id=%s 
            and st.location_dest_id != st.location_id
            and name like 'INV:%s'
            and EXTRACT(month FROM st.date)<4 and EXTRACT(Year FROM st.date)=2015'''%(product_id,location_id, '%')
            cr.execute(sql)
            Opening_stock = cr.fetchone()[0]
            return Opening_stock or 0.00
        
        def sale_qty(product_id, date):
            sql='''
                select sum(ail.quantity) from account_invoice_line ail
                inner join account_invoice ai on ail.invoice_id=ai.id
                where ail.product_id=%s and ai.date_invoice <= '%s' and ai.state not in ('draft','cancel')
                '''%(product_id,date)
            cr.execute(sql)
            sales_qty=cr.fetchone()[0]
            return sales_qty or 0.00
        
        def production_qty(product_id, date):
            sql='''
                Select  sum(product_qty) as productionQty 
                from mrp_production mrp 
                Inner join product_product p on (p.id=mrp.product_id and p.id not in (7))  
                where date_planned <= '%s' and mrp.state='done'
                and p.id =(%s)'''%(date,product_id)
            cr.execute(sql)
            prod_qty=cr.fetchone()[0]    
            return prod_qty or 0.00
        
        def total_received_qty(product_id, date):
            sql='''
                select sum(a.AdjustedQty) as adjustedqty 
                from (
                select p.id as ProductID,si.id as ReferenceID, si.name as stockAdjustmentName, si.date as StockAdjustmentDate,
                EXTRACT(month FROM si.date) transactionmonth, EXTRACT(year FROM si.date) transactionyear,
                p.name_template as productName, spl.name as SystemBatchNo,spl.phy_batch_no as PhysicalBatchNo, 
                product_qty as AdjustedQty,'Increased to 1 MT' as adjustmenttype from stock_inventory_line sil 
                Inner join stock_production_lot spl on (spl.id=sil.prod_lot_id)
                Inner join product_product p on (p.id=sil.product_id)
                Inner join stock_inventory si on (si.id=sil.inventory_id)
                where sil.product_id=4 and spl.name like '%s(M)%s' and 
                 si.date <= '%s'
                )a '''%('%', '%', date)
            cr.execute(sql)
            received_qty=cr.fetchone()
            if received_qty:
                received_qty = received_qty[0]
            return received_qty or 0.00  
        # TPT P.Vinothkumar END      
        cr.execute('delete from tpt_stock_on_hand')
        stock_obj = self.pool.get('tpt.stock.on.hand')
        stock = self.browse(cr, uid, ids[0])
        stock_line = []
        onhand, store_tio2, store_fsh  = 0, 0, 0
        for line in get_prod(stock):
            # Added by P.vinothkumar on 02/07/2016 for calculate onhandqty,store(tio2) and store(fsh)  
                onhand = line['onhand_qty']
                store_tio2 = line['store_tio2']
                store_fsh = line['store_fsh']
                if stock.categ_id.cate_name=='finish':
                    prd_obj = self.pool.get('product.product')
                    prd = prd_obj.browse(cr, uid, line['product_id'])
                    open_qty = opening_stock(prd.id, prd.default_code)
                    prod_qty = production_qty(prd.id, stock.date)
                    sales_qty= sale_qty(prd.id, stock.date)
                    receive_qty1= total_received_qty(prd.id, stock.date)
                    receive_qty2=receive_qty1
                    if prd.default_code=='M0501010001':
                        receive_qty1=0.0
                    elif  prd.default_code=='M0501010008':
                        receive_qty2=0.0
                        receive_qty1=-receive_qty1
                    else:
                        receive_qty1=0.0
                        receive_qty2=0.0           
                    onhand= open_qty+prod_qty+receive_qty1+receive_qty2-sales_qty
                    store_tio2 = open_qty+prod_qty+receive_qty1+receive_qty2-sales_qty
#                     if prd.default_code=='M0501010002':
#                         store_fsh = open_qty+prod_qty+receive_qty1+receive_qty2-sales_qty
#                         store_tio2= 0.0
#                     else: 
#                         store_fsh=0.0  
                       
                    #onhand = 0
                    if prd.default_code in ['M0501010006']:#FERRIC SULPHATE
                        onhand = onhand #line['pl_ferric'] or ''
                        store_tio2, store_fsh = 0, 0
                    elif prd.default_code in ['M0501010001', 'M0501010008']:#Anatase, Rutile
                        store_fsh = 0
                        onhand = line['onhand_qty']
                        store_tio2 = line['store_tio2']
                    elif prd.default_code in ['M0501010009', 'M0501010010']:# COAL TAR, COAL FINES - pl_other
                        onhand = line['pl_other'] or ''
                        onhand = line['onhand_qty']
                        store_tio2, store_fsh = 0, 0
                    elif prd.default_code=='M0501010002':#FERROUS
                        #TPT-START- BM - ON 03/08/2016 - TO DEDUCE CONSUMMED QTY DURING FERRIC SULPHATE PRODUCTION
                        sql = '''
                        select case when sum(product_qty)!=0 then sum(product_qty) else 0 end as fsh_cons_qty from stock_move where 
                        prodlot_id is not null and
                        location_id=(select id from stock_location where complete_name='Physical Locations / VVTi Pigments / Production Line / Raw Material')
                        and location_dest_id=(select id from stock_location where complete_name='Virtual Locations / Production') and
                        state='done' and product_id=%s and 
                        date <= '%s'
                        '''%(prd.id, stock.date)
                        cr.execute(sql)
                        fsh_cons_qty = cr.fetchone()[0]
                        onhand = open_qty + prod_qty + receive_qty1 + receive_qty2 - sales_qty - fsh_cons_qty
                        onhand = store_fsh 
                        #TPT-END 
                        store_tio2= 0.0
                    else:
                        onhand = 0
                        store_tio2 = 0
                        store_fsh = 0
                stock_line.append((0,0,{
                 'code': line['default_code'] or '',
                 'description': line['name'] or '',
                 'uom': line['uom'] or '',
                 'bin_loc': line['bin_location'] or '',
                 'onhand_qty': onhand or '', #line['onhand_qty'] or '',
                 #'mrp': line['mrp'] or '',
                 'min_stock': line['min_stock'] or '',
                 'max_stock': line['max_stock'] or '',
                 're_stock': line['re_stock'] or '',
                 'unit_price': get_avg_cost(line['product_id'], line['categ'],line['standard_price']),#line['standard_price'] or '',
                 'po_price': get_lastpo_cost(line['product_id'], line['categ'],line['standard_price']),
                 'onhand_qty_blocklist': line['block_qty'] or '' ,
                 'onhand_qty_pl_other': line['pl_others'] or '',
                 'onhand_qty_qa_ins': line['ins_qty'] or '' , 
                 'onhand_qty_st_rm': line['store_rm'] or '',
                 'onhand_qty_st_spare': line['store_spare'] or '' ,
                 'onhand_qty_st_fsh': store_fsh, #line['store_fsh'] or '',
                 'onhand_qty_st_tio2': store_tio2 or '',#'onhand_qty_st_tio2': line['store_tio2'] or '', 
                 'onhand_qty_pl_rm': line['pl_rm'] or '',   
                 'product_id': line['product_id'] or False,  
            }))        
        ## TPT-FOLLOWING SNIPPET IS COMMENTED - BY BalamuruganPurushothaman
        #=======================================================================
        # for line in get_categ(stock):
        #     stock_line.append((0,0,{
        #         'code': line.code or False,
        #         'description': line.name or False,
        #         'uom': line.uom_id and line.uom_id.name or False,
        #         'bin_loc': line.bin_location or False,
        #         'onhand_qty': get_ton_sl(stock,line),
        #         'ins_qty': get_ins_qty(stock,line),
        #         'bl_qty': get_blo_qty(stock,line),
        #         'mrp': get_mrp(stock,line),
        #         'min_stock': get_min_stock(stock,line),
        #         'max_stock': get_max_stock(stock,line),
        #         're_stock': get_re_stock(stock,line),
        #         'unit_price': get_unit_price(stock,line),
        #         
        #         'onhand_qty_blocklist': get_blocklist(stock,line),
        #         'onhand_qty_pl_other': get_pl_other(stock,line),
        #         'onhand_qty_qa_ins': get_qa_ins(stock,line),
        #         'onhand_qty_st_fsh': get_st_fsh(stock,line),
        #         'onhand_qty_st_rm': get_st_rm(stock,line),
        #         'onhand_qty_st_spare': get_st_spare(stock,line),
        #         'onhand_qty_st_tio2': get_st_tio2(stock,line),
        #         
        #         
        #     }))
        #=======================================================================
        if stock.date:
            date = stock.date
        else:
            date = time.strftime('%Y-%m-%d')
        vals = {
            'name': 'STOCK ON HAND REPORT',
            'categ_id': stock.categ_id and stock.categ_id.id or False,
            'product_id': stock.product_id and stock.product_id.id or False,
            'location_id': stock.location_id and stock.location_id.id or False,
            'is_mrp': stock.is_mrp,
            'stock_line': stock_line,
            'as_date': date, #time.strftime('%Y-%m-%d'),
            'date' : date
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