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

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
                'get_date_from':self.get_date_from,
                'get_categ':self.get_categ,
                'get_day_opening_stock':self.get_day_opening_stock,
                'get_year_opening_stock':self.get_year_opening_stock,
                'get_day_inward':self.get_day_inward,
                'get_day_outward':self.get_day_outward,
                'get_month_outward':self.get_month_outward,
                'get_month_inward':self.get_month_inward,
                'get_year_inward':self.get_year_inward,
                'get_year_outward':self.get_year_outward,
                'get_closing_stock':self.get_closing_stock,
                'convert_date':self.convert_date,

        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_categ(o):
            pro_obj = self.pool.get('product.product')
            categ_ids = []
            sql='''
                      select p.id, p.default_code,name_template as name
                      from product_product p,product_template pt
                      where pt.categ_id in(select pc.id from product_category pc where pc.cate_name = 'raw') 
                      and p.product_tmpl_id = pt.id;
            '''
            cr.execute(sql)
            categ_ids += [r[0] for r in cr.fetchall()]
            return pro_obj.browse(cr,uid,categ_ids)
        
    def get_day_opening_stock(o,product_id):
            open_qty = 0
            date_from = o.date_from
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s'
                            and st.location_dest_id != st.location_id
                            and ( (picking_id in (select id from stock_picking where  state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where  state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                '''%(product_id, date_from,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
            '''%(product_id, locat_ids[0], date_from)
            cr.execute(sql)
            product_qty = cr.dictfetchone()['product_qty']
            open_qty = inventory['ton_sl'] - product_isu_qty['product_isu_qty'] - product_qty
            return open_qty
        
    def get_year_opening_stock(o,product_id):
            open_qty = 0
            date_from = o.date_from
            sql = '''
                select * from account_fiscalyear where '%s' between date_start and date_stop
            '''%(date_from)
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                year = fiscalyear['date_start']
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s'
                            and st.location_dest_id != st.location_id
                            and ( (picking_id in (select id from stock_picking where  state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where  state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,year)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, year,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                if product_isu_qty:
                    open_qty = inventory['ton_sl'] - product_isu_qty['product_isu_qty']
            return open_qty
        
    def get_day_inward(o,product):
            date_from = o.date_from
            ton = 0
            inspec = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s and to_char(date, 'YYYY-MM-DD') = '%s' 
                                    and st.location_dest_id != st.location_id
                                    and (picking_id is not null
                                         or inspec_id is not null
                                         or (id in (select move_id from stock_inventory_move_rel)))
                                    and st.location_id != st.location_dest_id
                                )foo
                        '''%(product,locat_ids[0],date_from)
            cr.execute(sql)
            ton_arr = cr.fetchone()
            if ton_arr:
                ton = ton_arr[0] or 0
            else:
                ton = 0
            return ton
        
    def get_day_outward(o, product):
            sum = 0
            date_from = o.date_from
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec = '%s' and warehouse = %s and state = 'done')
            '''%(product, date_from,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and location_id != location_dest_id
            '''%(product, locat_ids[0], date_from)
            cr.execute(sql)
            product_qty = cr.dictfetchone()
            sum = product_isu_qty['product_isu_qty'] + product_qty['product_qty']
            return sum
        
    def get_month_outward(o, product):
            sum = 0
            date_from = o.date_from
            month_head = date(get_date(date_from)['year'], get_date(date_from)['month'], 01)
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
            '''%(product,month_head, date_from,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id
            '''%(product, locat_ids[0], month_head, date_from)
            cr.execute(sql)
            product_qty = cr.dictfetchone()
            sum = product_isu_qty['product_isu_qty'] + product_qty['product_qty']
            return sum
        
    def get_month_inward(o,product):
            date_from = o.date_from
            month_head = date(get_date(date_from)['year'], get_date(date_from)['month'], 01)
            ton = 0
            inspec = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                (select st.product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s and to_char(date, 'YYYY-MM-DD') between '%s' and '%s' 
                                    and (picking_id is not null
                                         or inspec_id is not null
                                         or (id in (select move_id from stock_inventory_move_rel)))
                                    and st.location_id != st.location_dest_id
                                )foo
                        '''%(product,locat_ids[0],month_head,date_from)
            cr.execute(sql)
            ton_arr = cr.fetchone()
            if ton_arr:
                ton = ton_arr[0] or 0
            else:
                ton = 0
            return ton
        
    def get_year_inward(o,product):
            date_from = o.date_from
            sql = '''
                select * from account_fiscalyear where '%s' between date_start and date_stop
            '''%(date_from)
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                year = fiscalyear['date_start']
                ton = 0
                inspec = 0
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                                select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s and to_char(date, 'YYYY-MM-DD') between '%s' and '%s' 
                                        and st.location_dest_id != st.location_id
                                        and (picking_id is not null
                                             or inspec_id is not null
                                             or (id in (select move_id from stock_inventory_move_rel)))
                                        and st.location_id != st.location_dest_id
                                    )foo
                            '''%(product,locat_ids[0],year,date_from)
                cr.execute(sql)
                ton_arr = cr.fetchone()
                if ton_arr:
                    ton = ton_arr[0] or 0
                else:
                    ton = 0
                return ton
        
    def get_year_outward(o, product):
            date_from = o.date_from
            sql = '''
                select * from account_fiscalyear where '%s' between date_start and date_stop
            '''%(date_from)
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                year = fiscalyear['date_start']
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where to_char(date_expec, 'YYYY-MM-DD') between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(product,year, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                    from stock_move where product_id = %s and state = 'done' and issue_id is null 
                    and picking_id is null and inspec_id is null and location_id = %s 
                    and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and location_id != location_dest_id
                '''%(product, locat_ids[0], year, date_from)
                cr.execute(sql)
                product_qty = cr.dictfetchone()
                sum = product_isu_qty['product_isu_qty'] + product_qty['product_qty']
                return sum    
            
        
    def get_closing_stock(o, open,inward,outward):
            total_cost = 0
            total_cost = open + inward - outward
            return total_cost
        
      
        
    
        
        
    
     
    
   
    
    
    