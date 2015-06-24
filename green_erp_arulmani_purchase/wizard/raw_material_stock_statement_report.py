# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime,date

import calendar
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from openerp.report import report_sxw
from openerp import pooler
import random
from datetime import date
from dateutil.rrule import rrule, DAILY

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class tpt_raw_material_stock_statement(osv.osv):
    _name = "tpt.raw.material.stock.statement"
    _columns = {    
                'date_from_title':fields.char('As Of Date'),
                'date_from':fields.date('As Of Date'),
                'statement_line':fields.one2many('tpt.stock.statement.line','statement_id','Stock Statement'),
                }



    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.raw.material.stock.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_statement_xls', 'datas': datas}
     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.raw.material.stock.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_statement_pdf', 'datas': datas}
    
tpt_raw_material_stock_statement()


class tpt_stock_statement_line(osv.osv):
    _name = "tpt.stock.statement.line"
    _columns = {    
        'statement_id': fields.many2one('tpt.raw.material.stock.statement', 'Stock Statement', ondelete='cascade'),
        'item_code': fields.char('Item Code', size = 1024),
        'item_name': fields.char('Item Name', size = 1024),
        'uom': fields.char('UOM', size = 1024),
        'day_open_stock': fields.float('Day Opening Stock'),
        'day_inward': fields.float('Day Inward'),
        'day_outward': fields.float('Day Outward'),
        'day_close_stock': fields.float('Day Closing Stock'),
        'day_close_value': fields.float('Day Closing Value'),   
        'month_open_stock': fields.float('Month Opening Stock'),
        'month_inward': fields.float('Month Inward'),
        'month_outward': fields.float('Month Outward'),
        'month_close_stock': fields.float('Month Closing Stock'),
        'month_close_value': fields.float('Month Closing Value'),   
        'year_open_stock': fields.float('Year Opening Stock'),
        'year_inward': fields.float('Year Inward'),
        'year_outward': fields.float('Year Outward'),
        'year_close_stock': fields.float('Year Closing Stock'),
        'year_close_value': fields.float('Year Closing Value'),  
                }
    

tpt_stock_statement_line()

class tpt_raw_stock_statement(osv.osv_memory):
    _name = "tpt.raw.stock.statement"
    _columns = {    
               'date_from':fields.date('As Of Date',required=True),
                }
    
    
    
    def print_report(self, cr, uid, ids, context=None):
        def get_date(date):
            res = {}
    #         date = time.strftime('%Y-%m-%d'),
            date_sec = datetime.strptime(date, DATE_FORMAT)
            day = date_sec.day
            month = date_sec.month
            year = date_sec.year
            res = {
                   'day': day,
                   'month': month,
                   'year': year,
                   }
            return res
        def get_categ(o):
            pro_obj = self.pool.get('product.product')
            categ_ids = []
            sql='''
                        select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where cate_name = 'raw') 
                        and product_product.product_tmpl_id = product_template.id;
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
                            and ( (picking_id in (select id from stock_picking where  state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where  state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                if product_isu_qty:
                    open_qty = inventory['ton_sl'] - product_isu_qty['product_isu_qty']
            return open_qty
        def get_day_opening_stock_value(o, product_id):
            opening_stock_value = 0
            date_from = o.date_from
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s'
                            and ( (picking_id in (select id from stock_picking where to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,date_from,date_from,date_from,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                        from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
                '''%(date_from,locat_ids[0],product_id)
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                if product_isu_qty:
                    opening_stock_value = total_cost-(product_isu_qty['product_isu_qty']*avg_cost)
                return opening_stock_value
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
        
        def get_day_inward_value(o,product):
            date_from = o.date_from
            hand_quantity = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                    (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id = %s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and loc1.usage != 'internal' and loc2.usage = 'internal' 
                                and (picking_id in (select id from stock_picking where  to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and state = 'done')
                                    or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
                                          (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and state = 'done'))))
                                )foo
                        '''%(locat_ids[0],product,date_from,date_from,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s' and state = 'done')
               '''%(product,date_from) 
            cr.execute(sql)
            for line in cr.dictfetchall():
               if line['action_taken'] == 'need':
                   sql = '''
                       select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                   '''%(line['id'])
                   cr.execute(sql)
                   inspec = cr.dictfetchone()
                   if inspec:
                       hand_quantity += inspec['qty_approve'] or 0
                       total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
            return total_cost                          
        def get_day_outward(o, product):
            date_from = o.date_from
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec = '%s' and warehouse = %s and state = 'done')
            '''%(product, date_from,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            return product_isu_qty and product_isu_qty['product_isu_qty'] or 0 

        def get_day_outward_value(o, product_id):
            date_from = o.date_from
            consum_value = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_id=%s and st.product_id=%s and  to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'

                            and ( (issue_id in (select id from tpt_material_issue where date_expec = '%s' and state in ('done')))
                                )
                '''%(locat_ids[0],product_id,date_from,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec = '%s' and warehouse = %s and state = 'done')
                '''%(product_id, date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                if product_isu_qty:
                    consum_value = (product_isu_qty['product_isu_qty']*avg_cost)
            return consum_value   
       
        def get_month_opening_stock(o,product_id):
            open_qty = 0
            date_from = o.date_from
            retirement = ''
            if date_from:
                day = date_from[8:10]
                month = date_from[5:7]
                year = date_from[:4]
                if month == "01":
                    year = int(year)-1
                    num_of_month = calendar.monthrange(year,12)[1]
                    retirement = datetime(int(year),12,int(num_of_month))
                elif month != "01":
                    month = int(month)-1
                    num_of_month = calendar.monthrange(int(year),int(month))[1]
                    retirement = datetime(int(year),int(month),num_of_month)
            if retirement:
                retirement=retirement.strftime('%Y-%m-%d')
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s'
                            and ( (picking_id in (select id from stock_picking where  state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where  state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,retirement)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                sql = '''
                        select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                    '''%(product_id, retirement,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
                if product_isu_qty:
                    open_qty = inventory['ton_sl'] - product_isu_qty['product_isu_qty']
            return open_qty        
        
        def get_month_opening_stock_value(o, product_id):
            opening_stock_value = 0
            date_from = o.date_from
            retirement = ''
            if date_from:
                day = date_from[8:10]
                month = date_from[5:7]
                year = date_from[:4]
                if month == "01":
                    year = int(year)-1
                    num_of_month = calendar.monthrange(year,12)[1]
                    retirement = datetime(int(year),12,int(num_of_month))
                elif month != "01":
                    month = int(month)-1
                    num_of_month = calendar.monthrange(int(year),int(month))[1]
                    retirement = datetime(int(year),int(month),num_of_month)
            if retirement:
                retirement=retirement.strftime('%Y-%m-%d')
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s'
                            and ( (picking_id in (select id from stock_picking where  state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where  state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,retirement)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                        from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
                '''%(retirement,locat_ids[0],product_id)
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                opening_stock_value = total_cost-(product_isu_qty*avg_cost)
            return opening_stock_value
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
        
        def get_month_inward_value(o,product):
            date_from = o.date_from
            month_head = date(get_date(date_from)['year'], get_date(date_from)['month'], 01)
            hand_quantity = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                    (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id = %s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and loc1.usage != 'internal' and loc2.usage = 'internal' 
                                and (picking_id in (select id from stock_picking where  state = 'done')
                                    or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
                                          (select id from stock_inventory where  state = 'done'))))
                                )foo
                        '''%(locat_ids[0],product,month_head,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
               '''%(product,month_head,date_from) 
            cr.execute(sql)
            for line in cr.dictfetchall():
               if line['action_taken'] == 'need':
                   sql = '''
                       select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                   '''%(line['id'])
                   cr.execute(sql)
                   inspec = cr.dictfetchone()
                   if inspec:
                       hand_quantity += inspec['qty_approve'] or 0
                       total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
            return total_cost  
        
        def get_month_outward(o, product):
            date_from = o.date_from
            month_head = date(get_date(date_from)['year'], get_date(date_from)['month'], 01)
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                where product_id = %s and material_issue_id in (select id from tpt_material_issue where to_char(date_expec, 'YYYY-MM-DD') between '%s' and '%s' and warehouse = %s and state = 'done')
            '''%(product,month_head, date_from,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            return product_isu_qty and product_isu_qty['product_isu_qty'] or 0 
        
        def get_month_outward_value(o, product_id):
            date_from = o.date_from
            month_head = date(get_date(date_from)['year'], get_date(date_from)['month'], 01)
            consum_value = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'

                            and ( (issue_id in (select id from tpt_material_issue where state in ('done')))
                                )
                '''%(locat_ids[0],product_id,month_head,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(product_id,month_head,date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                consum_value = (product_isu_qty*avg_cost)
            return consum_value          
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
        
        def get_year_opening_stock_value(o, product_id):
            opening_stock_value = 0
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
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s'
                            and ( (picking_id in (select id from stock_picking where  state = 'done')) 
                            or  (inspec_id in (select id from tpt_quanlity_inspection where  state in ('done','remaining')))
                            or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where  state = 'done')))
                                )
                '''%(locat_ids[0],product_id,year)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                        from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
                '''%(year,locat_ids[0],product_id)
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                opening_stock_value = total_cost-(product_isu_qty*avg_cost)
            return opening_stock_value
        
          
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
            
        def get_year_inward_value(o,product):
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
            hand_quantity = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
                    (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_dest_id = %s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and loc1.usage != 'internal' and loc2.usage = 'internal' 
                                and (picking_id in (select id from stock_picking where  state = 'done')
                                    or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
                                          (select id from stock_inventory where  state = 'done'))))
                                )foo
                        '''%(locat_ids[0],product,year,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
               '''%(product,year,date_from) 
            cr.execute(sql)
            for line in cr.dictfetchall():
               if line['action_taken'] == 'need':
                   sql = '''
                       select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
                   '''%(line['id'])
                   cr.execute(sql)
                   inspec = cr.dictfetchone()
                   if inspec:
                       hand_quantity += inspec['qty_approve'] or 0
                       total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
            return total_cost 
            
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
                return product_isu_qty and product_isu_qty['product_isu_qty'] or 0 
            
        def get_year_outward_value(o, product_id):
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
            consum_value = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                            join stock_location loc1 on st.location_id=loc1.id
                            join stock_location loc2 on st.location_dest_id=loc2.id
                        where st.state='done' and st.location_id=%s and st.product_id=%s and to_date(to_char(st.date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'

                            and ( (issue_id in (select id from tpt_material_issue where state in ('done')))
                                )
                '''%(locat_ids[0],product_id,year,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
                '''%(product_id,year,date_from,locat_ids[0])
                cr.execute(sql)
                product_isu_qty = cr.fetchone()[0]
                consum_value = (product_isu_qty*avg_cost)
            return consum_value
            
        def get_closing_stock(o, open,inward,outward):
            total_cost = 0
            total_cost = open + inward - outward
            return total_cost  

            
        statement_obj = self.pool.get('tpt.raw.material.stock.statement')
        cr.execute('delete from tpt_raw_material_stock_statement')
        statement = self.browse(cr, uid, ids[0])
        statement_line = []
        for line in get_categ(statement):
            statement_line.append((0,0,{
                'item_code': line.default_code,
                'item_name': line.name,
                'uom':line.uom_id and line.uom_id.name or 0,
                'day_open_stock': get_day_opening_stock(statement,line.id),
                'day_inward':get_day_inward(statement,line.id),
                'day_outward': get_day_outward(statement,line.id),
                'day_close_stock': get_closing_stock(statement,get_day_opening_stock(statement,line.id),get_day_inward(statement,line.id),get_day_outward(statement,line.id)),
                'day_close_value': get_closing_stock(statement,get_day_opening_stock_value(statement,line.id),get_day_inward_value(statement,line.id),get_day_outward_value(statement,line.id)),   
                'month_open_stock': get_month_opening_stock(statement,line.id),
                'month_inward': get_month_inward(statement,line.id),
                'month_outward': get_month_outward(statement,line.id),
                'month_close_stock': get_closing_stock(statement,get_month_opening_stock(statement,line.id),get_month_inward(statement,line.id),get_month_outward(statement,line.id)),
                'month_close_value': get_closing_stock(statement,get_month_opening_stock_value(statement,line.id),get_month_inward_value(statement,line.id),get_month_outward_value(statement,line.id)),   
                'year_open_stock': get_year_opening_stock(statement,line.id),
                'year_inward': get_year_inward(statement,line.id),
                'year_outward': get_year_outward(statement,line.id),
                'year_close_stock': get_closing_stock(statement,get_year_opening_stock(statement,line.id),get_year_inward(statement,line.id),get_year_outward(statement,line.id)),
                'year_close_value': get_closing_stock(statement,get_year_opening_stock_value(statement,line.id),get_year_inward_value(statement,line.id),get_year_outward_value(statement,line.id)),   
 
            }))
        vals = {
            'name': 'Raw Material Stock Statement',
            'date_from': statement.date_from,
            'date_from_title':'As Of Date: ',
            'statement_line':statement_line,
        }
        statement_id = statement_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_tpt_raw_material_stock_statement')
        return {
                    'name': 'Raw Material Stock Statement',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.raw.material.stock.statement',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': statement_id,
                }
        
tpt_raw_stock_statement()


# class product_product(osv.osv):
#     _inherit = "product.product"
#     
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_product_id'):
#             if context.get('categ_id'):
#                 sql = '''
#                      select product_product.id 
#                         from product_product,product_template 
#                         where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
#                         and product_product.product_tmpl_id = product_template.id;
#                 '''%(context.get('categ_id'))
#                 cr.execute(sql)
#                 product_ids = [row[0] for row in cr.fetchall()]
#                 args += [('id','in',product_ids)]
#         return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
# 
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#        ids = self.search(cr, user, args, context=context, limit=limit)
#        return self.name_get(cr, user, ids, context=context)
# product_product()
