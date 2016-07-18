# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from global_utility import tpt_shared_component

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
              'get_date':self.get_date,
              'get_warehouse':self.get_warehouse,
              'get_categ':self.get_categ,
              'get_ton_sl':self.get_ton_sl,
              'get_category':self.get_category,
              'get_product':self.get_product,
              'get_ins_qty':self.get_ins_qty,
              'get_blo_qty':self.get_blo_qty,
              'get_mrp':self.get_mrp,
              'get_mrp_type':self.get_mrp_type, 
              'get_min_stock':self.get_min_stock,
              'get_max_stock':self.get_max_stock,
              'get_re_stock':self.get_re_stock, 
              'get_unit_price':self.get_unit_price, 
              
              'get_blocklist':self.get_blocklist,
              'get_pl_other':self.get_pl_other,
              'get_qa_ins':self.get_qa_ins,
              'get_st_fsh':self.get_st_fsh,
              'get_st_rm':self.get_st_rm,
              'get_st_spare':self.get_st_spare,
              'get_st_tio2':self.get_st_tio2,
              'get_prod':self.get_prod, #TPT-BM
    
        })
    ###
    def get_avg_cost(self, product_id, categ, std_price):
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
        avg_cost_ids = avg_cost_obj.search(self.cr, self.uid, [('product_id','=',product_id),('warehouse_id','=',location_id)])
        if avg_cost_ids:
            avg_cost_id = avg_cost_obj.browse(self.cr, self.uid, avg_cost_ids[0])
            avg_cost = avg_cost_id.avg_cost or 0
        if categ=='finish':
            avg_cost = std_price
        return avg_cost
    def get_lastpo_cost(self, product_id, categ, std_price):
        sql = '''
                select case when price_unit>0 then price_unit else 0 end avg_cost from purchase_order_line where id = (
                select max(id) from purchase_order_line pol
                where pol.product_id=%s)
            '''%(product_id)
        self.cr.execute(sql)
        avg = self.cr.dictfetchone()
        avg_cost = 0
        if avg:
            avg_cost=avg['avg_cost']
        if categ=='finish':
            avg_cost = 0.00
        return float(avg_cost)
    #
    
    # Added by P.vinothkumar on 02/07/2016 for modify logics in stock on hand report
    def opening_stock(self, product_id, default_code):
        location = tpt_shared_component.warehouse_module() 
        location_id = location.get_finished_location(default_code) 
        sql='''
        select
        sum(st.product_qty) as product_qty
        from stock_move st
        where st.state='done' and st.product_id=%s and st.location_dest_id=%s 
        and st.location_dest_id != st.location_id
        and name = 'INV:Update'
        and EXTRACT(month FROM st.date)<4 and EXTRACT(Year FROM st.date)=2015'''%(product_id,location_id)
        self.cr.execute(sql)
        Opening_stock = self.cr.fetchone()[0]
        return Opening_stock or 0.00
    
    def sale_qty(self, product_id, date):
        sql='''
            select sum(ail.quantity) from account_invoice_line ail
            inner join account_invoice ai on ail.invoice_id=ai.id
            where ail.product_id=%s and ai.date_invoice < '%s'
           
            '''%(product_id,date)
        self.cr.execute(sql)
        sales_qty=self.cr.fetchone()[0]
        return sales_qty or 0.00
    
    def production_qty(self, product_id, date):
        sql='''
            Select  sum(product_qty) as productionQty 
            from mrp_production mrp 
            Inner join product_product p on (p.id=mrp.product_id and p.id not in (7))  
            where date_planned < '%s' 
            and p.id =(%s)'''%(date,product_id)
        self.cr.execute(sql)
        prod_qty=self.cr.fetchone()[0]    
        return prod_qty or 0.00
    
    def total_received_qty(self, product_id, date):
        sql='''
            select sum(a.AdjustedQty) as adjustedqty 
            from (
            select p.id as ProductID,si.id as ReferenceID, si.name as stockAdjustmentName, si.date as StockAdjustmentDate,
            EXTRACT(month FROM si.date) transactionmonth, EXTRACT(year FROM si.date) transactionyear,
            p.name_template as productName, spl.name as SystemBatchNo,spl.phy_batch_no as PhysicalBatchNo, 
            product_qty as AdjustedQty,'Inself.creased to 1 MT' as adjustmenttype from stock_inventory_line sil 
            Inner join stock_production_lot spl on (spl.id=sil.prod_lot_id)
            Inner join product_product p on (p.id=sil.product_id)
            Inner join stock_inventory si on (si.id=sil.inventory_id)
            where sil.product_id=4 and spl.name like '%s(M)%s' and 
             si.date < '%s'
            )a '''%('%', '%', date)
        self.cr.execute(sql)
        received_qty=self.cr.fetchone()
        if received_qty:
            received_qty = received_qty[0]
        return received_qty or 0.00  
    # TPT P.Vinothkumar END      
        
        
    #
    ##TPT-START - TO ADDRESS PERFORMANCE ISSUE - By BalamuruganPurushothaman on 02/09/2015
    def get_prod(self): 
        #TPT_BM-07/06/2016 - AS ON DATE AS PARAM
        wizard_data = self.localcontext['data']['form']
        date = wizard_data['as_date']
        sql = '''
                    select pp.default_code, pt.name, pt.standard_price, pu.name as uom, pp.bin_location,
          pp.min_stock,  pp.max_stock,  pp.re_stock,
         (select case when sum(onhand_qty)>0 then sum(onhand_qty) else 0 end ton
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
                    WHERE stm.state= 'done' and product_id=pp.id and stm.date<='%(date)s' )foo) onhand_qty,
        
        (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_dest_id =(select id from stock_location where name='Raw Material' and 
                    usage='internal' and location_id=(select id from stock_location where name='Store'))
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='Raw Material' and 
                    usage='internal' and location_id=(select id from stock_location where name='Store'))
                )foo) store_rm,
                
         (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and st.location_dest_id 
                    =(select id from stock_location where name='Spares' and 
                    usage='internal')
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and st.location_id 
                    =(select id from stock_location where name='Spares' and 
                    usage='internal')
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
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='Inspection' and 
                    usage='internal')
                )foo) ins_qty,
        (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_dest_id =(select id from stock_location where name='Block List' and 
                    usage='internal')
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='Block List' and 
                    usage='internal')
                )foo) block_qty,
         (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_dest_id =(select id from stock_location where name='Other' and 
                    usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='Other' and 
                    usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                )foo) pl_others,
         (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_dest_id =(select id from stock_location where name='FSH' and 
                    usage='internal' and location_id=(select id from stock_location where name='Store'))
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='FSH' and 
                    usage='internal' and location_id=(select id from stock_location where name='Store'))
                )foo) store_fsh    ,
        (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_dest_id =(select id from stock_location where name='TIO2' and 
                    usage='internal' and location_id=(select id from stock_location where name='Store'))
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='TIO2' and 
                    usage='internal' and location_id=(select id from stock_location where name='Store'))
                )foo) store_tio2,                 
        
        (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                (
                select st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_dest_id =(select id from stock_location where name='Raw Material' and 
                    usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                union all
                select st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = pp.id and st.date<='%(date)s' and
                    st.location_id =(select id from stock_location where name='Raw Material' and 
                    usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                )foo) pl_rm, 
                
                (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date < '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Ferric Sulphate' and 
                        usage='internal' )
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date < '%(date)s' and
                        st.location_id =(select id from stock_location where name='Ferric Sulphate' and 
                        usage='internal' )
                    )foo) pl_ferric,
                    
                    (select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                    (
                    select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date < '%(date)s' and
                        st.location_dest_id =(select id from stock_location where name='Other' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = pp.id and st.date < '%(date)s' and
                        st.location_id =(select id from stock_location where name='Other' and 
                        usage='internal' and location_id=(select id from stock_location where name='Production Line'))
                    )foo) pl_other, 
                
                pp.id product_id, pp.cate_name as categ
                 
        from product_product pp
        inner join product_template pt on pp.product_tmpl_id=pt.id 
        inner join product_uom pu on pt.uom_id=pu.id
        ''' % {'date':date}
            
        
        categ_id = wizard_data['categ_id']
        categ_id = categ_id[0]
        product_id = wizard_data['product_id']
        #product_id = product_id[0]
        is_mrp = wizard_data['is_mrp']
        res = [] 
            
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
            str = "  pt.categ_id=%s and pp.id = %s and pp.mrp_control = 't'" % (categ_id,product_id[0])
            sql = sql+str
        if categ_id and product_id and is_mrp is False:
            str = "  pt.categ_id=%s and pp.id = %s" % (categ_id,product_id[0])
            sql = sql+str
        if categ_id and not product_id and is_mrp is True :
            str = "  pt.categ_id=%s and pp.mrp_control = 't'" % (categ_id)
            sql = sql+str
        if not categ_id and product_id and is_mrp is True:
            str = " pp.id = %s and pp.mrp_control = 't'" % (product_id[0])
            sql = sql+str
        str = " order by pp.default_code asc"
        sql = sql+str
        self.cr.execute(sql)        
        prd_obj = self.pool.get('product.product')
        #prd = prd_obj.browse(self.cr, self.uid, product_id[0])
        onhand, store_tio2, store_fsh  = 0, 0, 0
        for line in self.cr.dictfetchall():
            #
            #if prd.cate_name == 'finish':
            onhand = line['onhand_qty']
            store_tio2 = line['store_tio2']
            prd_obj = self.pool.get('product.product')
            prd = prd_obj.browse(self.cr, self.uid, line['product_id'])
            if prd.cate_name == 'finish':
                open_qty = self.opening_stock(prd.id, prd.default_code)
                prod_qty = self.production_qty(prd.id, date)
                sales_qty = self.sale_qty(prd.id, date)
                receive_qty1 = self.total_received_qty(prd.id, date)
                receive_qty2 = receive_qty1
                if prd.default_code=='M0501010001':
                    receive_qty1=0.0
                elif  prd.default_code=='M0501010008':
                    receive_qty2=0.0
                    receive_qty1=-receive_qty1
                else:
                    receive_qty1=0.0
                    receive_qty2=0.0           
                onhand= open_qty + prod_qty + receive_qty1 + receive_qty2 - sales_qty
                store_tio2 = open_qty + prod_qty + receive_qty1 + receive_qty2 - sales_qty
                if prd.default_code=='M0501010002':
                    store_fsh = open_qty + prod_qty + receive_qty1+receive_qty2 - sales_qty
                    store_tio2= 0.0
                else: 
                    store_fsh=0.0  
    
                if prd.default_code in ['M0501010006']:#FERRIC SULPHATE
                    onhand = line['pl_ferric'] or ''
                    store_tio2, store_fsh = 0, 0
                elif prd.default_code in ['M0501010001', 'M0501010008']:#Anatase, Rutile
                    store_fsh = 0
                elif prd.default_code in ['M0501010009', 'M0501010010']:# COAL TAR, COAL FINES - pl_other
                    onhand = line['pl_other'] or ''
                    onhand = line['onhand_qty']
                    store_tio2, store_fsh = 0, 0
                elif prd.default_code=='M0501010002': #FERROUS
                    onhand = line['store_fsh']
                else:
                    onhand = line['onhand_qty']
                    store_tio2 = line['store_tio2']
                    store_fsh = line['store_fsh'] or ''
            #
            res.append({
                'code': line['default_code'] or '',
                'description': line['name'] or '',
                 'uom': line['uom'] or '',
                 'bin_loc': line['bin_location'] or '',
                 'onhand_qty': onhand or 0, #line['onhand_qty'] or 0,
                 #'mrp': line['mrp'] or '',
                 'min_stock': line['min_stock'] or 0,
                 'max_stock': line['max_stock'] or 0,
                 're_stock': line['re_stock'] or 0,
                 'unit_price': self.get_avg_cost(line['product_id'], line['categ'],line['standard_price']),#line['standard_price'] or 0,
                 'po_price': self.get_lastpo_cost(line['product_id'], line['categ'],line['standard_price']),
                 'onhand_qty_blocklist': line['block_qty'] or 0 ,
                 'onhand_qty_pl_other': line['pl_others'] or 0,
                 'onhand_qty_qa_ins': line['ins_qty'] or 0 , 
                 'onhand_qty_st_rm': line['store_rm'] or 0,
                 'onhand_qty_st_spare': line['store_spare'] or 0 ,
                 'onhand_qty_st_fsh': line['store_fsh'] or 0, #line['store_fsh'] or 0,
                 'onhand_qty_st_tio2': store_tio2 or 0, #line['store_tio2'] or 0,  
                 'onhand_qty_pl_rm': line['pl_rm'] or 0,
            })
        return res
        
            
    ##TPT-END
    def convert_date(self,type):
        if type:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
            
    def convert_date(self,date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date(self):
        date = time.strftime('%Y-%m-%d'),
        date = datetime.strptime(date[0], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_warehouse(self):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        loc_obj = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        return loc_obj   
    
    def get_category(self):
        wizard_data = self.localcontext['data']['form']
        cat = wizard_data['categ_id']
        if cat:
            cat_obj = self.pool.get('product.category').browse(self.cr,self.uid,cat[0])
            return cat_obj
        return False
    
    def get_product(self):
        wizard_data = self.localcontext['data']['form']
        pro = wizard_data['product_id']
        if pro:
            pro_obj = self.pool.get('product.product').browse(self.cr,self.uid,pro[0])
            return pro_obj
        return False

    def get_categ(self):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        categ = wizard_data['categ_id']
        product = wizard_data['product_id']
        is_mrp = wizard_data['is_mrp']
        pro_obj = self.pool.get('product.product')
        categ_ids = []

        if is_mrp:
            if categ and product:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                            and product_product.product_tmpl_id = product_template.id and product_product.id = %s and product_product.mrp_control='t';
                '''%(categ[0],product[0])
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
            if categ:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                            and product_product.product_tmpl_id = product_template.id and product_product.mrp_control='t';
                '''%(categ[0])
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return pro_obj.browse(self.cr,self.uid,categ_ids)
            if product and not categ:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category) 
                            and product_product.product_tmpl_id = product_template.id and product_product.id = %s and product_product.mrp_control='t';
                '''%(product[0])
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
            if not product and not categ :
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category) 
                            and product_product.product_tmpl_id = product_template.id  and product_product.mrp_control='t';
                '''
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
        else:
            if categ and product:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                            and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
                '''%(categ[0],product[0])
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
            if categ:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                            and product_product.product_tmpl_id = product_template.id;
                '''%(categ[0])
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return pro_obj.browse(self.cr,self.uid,categ_ids)
            if product and not categ:
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category) 
                            and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
                '''%(product[0])
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
            if not product and not categ :
                sql='''
                            select product_product.id 
                            from product_product,product_template 
                            where product_template.categ_id in(select product_category.id from product_category) 
                            and product_product.product_tmpl_id = product_template.id  ;
                '''
                self.cr.execute(sql)
                categ_ids += [r[0] for r in self.cr.fetchall()]
                return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
        
    def get_ton_sl(self, line):
        wizard_data = self.localcontext['data']['form']
        #loc = wizard_data['location_id']
        #location = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        #=======================================================================
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
        #=======================================================================
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
        self.cr.execute(sql)
        ton_sl = self.cr.dictfetchone()
        return ton_sl and ton_sl['ton_sl'] or 0
    
    def get_ins_qty(self, line):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        location = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Quality Inspection'),('usage','=','view')])
        locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Inspection']),('location_id','=',parent_ids[0])])
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
        self.cr.execute(sql)
        ton = self.cr.dictfetchone()
        return ton and ton['ton'] or 0
    def get_blo_qty(self, line):
        wizard_data = self.localcontext['data']['form']
        loc = wizard_data['location_id']
        location = self.pool.get('stock.location').browse(self.cr,self.uid,loc[0])
        parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
        locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_ids[0])])
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
        self.cr.execute(sql)
        ton = self.cr.dictfetchone()
        return ton and ton['ton'] or 0        
    
    def get_mrp(self):
        wizard_data = self.localcontext['data']['form']
        mrp = wizard_data['is_mrp']
        if mrp is True:
            return 'MRP Controlled Product'
        else:
            return 'Both MRP Controlled Product & Others' 
    def get_mrp_type(self, line):
        wizard_data = self.localcontext['data']['form']
        mrp_type = wizard_data['is_mrp']    
        sql = '''
                        select mrp_control from product_product where id=%s
                    '''%(line.id)
        self.cr.execute(sql)
        ton = self.cr.fetchone()
        ton = ton[0]
        if mrp_type is True:
            return 'Yes'
        else:
            return 'No'  
    def get_min_stock(self, line):
            sql = '''
                select min_stock from product_product where id=%s
                        '''%(line.id)
            self.cr.execute(sql)
            mrp = self.cr.fetchone()
            min_stock = mrp[0]
            return min_stock or 0
    def get_max_stock(self, line):
            sql = '''
                select max_stock from product_product where id=%s
                        '''%(line.id)
            self.cr.execute(sql)
            mrp = self.cr.fetchone()
            max_stock = mrp[0]
            return max_stock or 0
    def get_re_stock(self, line):
            sql = '''
                select re_stock from product_product where id=%s
                        '''%(line.id)
            self.cr.execute(sql)
            mrp = self.cr.fetchone()
            re_stock = mrp[0]
            return re_stock or 0   
    def get_unit_price(self, line):
            prod_obj = self.pool.get('product.product')
            acc = prod_obj.browse(self.cr,self.uid,line.id)
            unit_price = acc.standard_price
            return unit_price or 0 
    def get_blocklist(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Block List','Block','Blocked List','Blocked']),('location_id','=',parent_ids[0])])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0 
    def get_pl_other(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Other'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Other')])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0
    def get_qa_ins(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Quality Inspection'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Inspection']),('location_id','=',parent_ids[0])])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0
    def get_st_fsh(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0 
    def get_st_rm(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Raw Material'),('location_id','=',parent_ids[0])])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0 
    def get_st_spare(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Spares'),('location_id','=',parent_ids[0])])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0 
    def get_st_tio2(self,line):
            parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','TIO2'),('location_id','=',parent_ids[0])])
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
            self.cr.execute(sql)
            ton = self.cr.dictfetchone()
            return ton and ton['ton'] or 0 
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: