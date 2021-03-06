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
                'name':fields.char('Raw Material Stock Statement'),
                'date_from_title':fields.char('As Of Date'),
                'date_from':fields.date('As Of Date'),
                'statement_line':fields.one2many('tpt.stock.statement.line','statement_id','Stock Statement'),
                }
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
        datas['model'] = 'tpt.raw.material.stock.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_statement_xls', 'datas': datas}
     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         datas = {'ids': context.get('active_ids', [])}
        datas = {'ids': ids}
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
        'day_open_stock': fields.float('Day Opening Stock',digits=(16,3)),
        'day_inward': fields.float('Day Inward',digits=(16,3)),
        'day_outward': fields.float('Day Outward',digits=(16,3)),
        'day_close_stock': fields.float('Day Closing Stock',digits=(16,3)),
        'day_close_value': fields.float('Day Closing Value',digits=(16,3)),   
        'month_open_stock': fields.float('Month Opening Stock',digits=(16,3)),
        'month_inward': fields.float('Month Inward',digits=(16,3)),
        'month_outward': fields.float('Month Outward',digits=(16,3)),
        'month_close_stock': fields.float('Month Closing Stock',digits=(16,3)),
        'month_close_value': fields.float('Month Closing Value',digits=(16,3)),   
        'year_open_stock': fields.float('Year Opening Stock',digits=(16,3)),
        'year_inward': fields.float('Year Inward',digits=(16,3)),
        'year_outward': fields.float('Year Outward',digits=(16,3)),
        'year_close_stock': fields.float('Year Closing Stock',digits=(16,3)),
        'year_close_value': fields.float('Year Closing Value',digits=(16,3)),  
                }
    

tpt_stock_statement_line()

class tpt_raw_stock_statement(osv.osv_memory):
    _name = "tpt.raw.stock.statement"
    _columns = {    
               'date_from':fields.date('As Of Date',required=True),
                }
    
    
    
    def print_report(self, cr, uid, ids, context=None):
        self.num_call_grn = {'grn_name':'','num':-1}
        self.current_transaction_qty = 0
        self.transaction_qty = 0
        self.st_sum_value = 0
        self.current = 0
        self.good = 0
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
        
        def get_day_opening_stock_date_period(o,product_id):
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
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
                                    )
                '''%(locat_ids[0],product_id,year,year)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                    where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
                '''%(product_id, year,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
            '''%(product_id, locat_ids[0], year)
            cr.execute(sql)
            product_qty = cr.dictfetchone()['product_qty']
            open_qty = inventory['ton_sl'] - product_isu_qty['product_isu_qty'] - product_qty
            return open_qty
        
        def get_day_opening_stock_value(o, product_id):
            date_from = o.date_from
            production_value = 0
            sql = '''
                select * from account_fiscalyear where '%s' between date_start and date_stop
            '''%(date_from)
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            product = self.pool.get('product.product').browse(cr,uid,product_id)
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            else:
                year = fiscalyear['date_start']
            opening_stock_value = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                        from stock_move st
                        where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and st.location_dest_id != st.location_id
                            and ( picking_id is not null 
                            or inspec_id is not null 
                            or (st.id in (select move_id from stock_inventory_move_rel))
                    )
                '''%(locat_ids[0],product_id,year)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
#                 avg_cost = hand_quantity and total_cost/hand_quantity or 0
            sql = '''
               select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                    from stock_move st
                    where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                    and issue_id is not null
                    
            '''%(locat_ids[0],product_id,year)
            cr.execute(sql)
            product_isu_qty = cr.fetchone()[0]
            if product.default_code == 'M0501060001':
               sql = '''
                   select case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                    from stock_move st
                    where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                    and issue_id is null and picking_id is null and inspec_id is null 
                    and id in (select move_id from mrp_production_move_ids)
                        
               '''%(locat_ids[0],product.id,year)
               cr.execute(sql)
               production_value = cr.fetchone()[0]
            opening_stock_value = total_cost-(product_isu_qty)-production_value
            return opening_stock_value
            
        def get_day_closing_stock_value(o, product_id):
            opening_stock_value = 0
            date_from = o.date_from
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD') <= '%s'
                                and st.location_dest_id != st.location_id
                                and ( picking_id is not null 
                                or inspec_id is not null 
                                or (st.id in (select move_id from stock_inventory_move_rel))
                        )
                '''%(locat_ids[0],product_id,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
                avg_cost = hand_quantity and total_cost/hand_quantity or 0
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
                            from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<='%s' and warehouse = %s and state='done') and product_id=%s
                '''%(date_from,locat_ids[0],product_id)
                cr.execute(sql)
                product_isu_qty = cr.dictfetchone()
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
                                and st.location_dest_id != st.location_id
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
                            and st.location_dest_id != st.location_id
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
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s'
                                and st.location_dest_id != st.location_id
                                and ( (picking_id is not null) 
                                or  (inspec_id is not null)
                                or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s' and state = 'done')))
                                    )
                '''%(locat_ids[0],product_id,retirement,retirement)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
                        where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec <= '%s' and warehouse = %s and state = 'done')
                '''%(product_id, retirement,locat_ids[0])
            cr.execute(sql)
            product_isu_qty = cr.dictfetchone()
            sql = '''
                    select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty 
                        from stock_move where product_id = %s and state = 'done' and issue_id is null 
                        and picking_id is null and inspec_id is null and location_id = %s 
                        and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s' and location_id != location_dest_id
            '''%(product_id, locat_ids[0], retirement)
            cr.execute(sql)
            product_qty = cr.dictfetchone()['product_qty']
            open_qty = inventory['ton_sl'] - product_isu_qty['product_isu_qty'] - product_qty
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
                            and st.location_dest_id != st.location_id
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
                        from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<='%s' and warehouse = %s and state='done') and product_id=%s
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
                                and st.location_dest_id != st.location_id
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
                            and st.location_dest_id != st.location_id
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
                            and st.location_dest_id != st.location_id
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
                                and st.location_dest_id != st.location_id
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
                            and st.location_dest_id != st.location_id
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
        
        def get_detail_lines(o, product_id):
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
            parent_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_raw = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids_raw[0])])
            parent_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids_spares = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids_spares[0])])
            sql = '''
                select * from account_move where doc_type in ('good', 'grn', 'product') 
                    and date between '%(date_from)s' and '%(date_to)s'
                    and ( id in (select move_id from account_move_line where (move_id in (select move_id from account_invoice where to_char(date_invoice, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and id in (select invoice_id from account_invoice_line where product_id=%(product_id)s)))
                        or (LEFT(name,17) in (select name from stock_picking where id in (select picking_id from stock_move where to_char(date, 'YYYY-MM-DD') between '%(date_from)s' and '%(date_to)s' and product_id=%(product_id)s)))
                    ) or material_issue_id in (select id from tpt_material_issue where date_expec between '%(date_from)s' and '%(date_to)s' and warehouse in (%(location_row_id)s) and id in (select material_issue_id from tpt_material_issue_line where product_id=%(product_id)s)) 
                        )
                        or product_dec in (select id from mrp_production where date_planned between '%(date_from)s' and '%(date_to)s' and id in (select production_id from mrp_production_move_ids where move_id in (select id from stock_move where product_id = %(product_id)s and location_id in (%(location_row_id)s) ))
                         )
                         order by date,doc_type = 'grn' desc, doc_type = 'good' desc, doc_type = 'product' desc, id
            '''%{'date_from':year,
                 'date_to':date_from,
                 'product_id':product_id.id,
                 'location_row_id':locat_ids_raw[0],
                 }
            cr.execute(sql)
            move_line = []
            for line in cr.dictfetchall():
#                 if line['doc_type'] != 'grn':
#                     move_line.append(line)
                if line['doc_type'] == 'grn':
                    sql = '''
                        select * from stock_move
                        where  picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s) and product_id = %s)
                    '''%(line['id'], product_id.id)
                    cr.execute(sql)
                    for move in cr.dictfetchall():
                        if move['action_taken'] == 'direct' and move['location_dest_id'] in [locat_ids_raw[0],locat_ids_spares[0]]:
                            move_line.append(line)
                        if move['action_taken'] == 'need':
                            sql = '''
                                select id, qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining') and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                            '''%(move['id'], year, date_from)
                            cr.execute(sql)
                            for move_sql in cr.dictfetchall():
                                if move_sql['qty_approve']:
                                    sql = '''
                                        select id from stock_move where inspec_id = %s and state = 'done' and to_char(date, 'YYYY-MM-DD') between '%s' and '%s'
                                    '''%(move_sql['id'],year,date_from)
                                    cr.execute(sql)
                                    move_sql2 = cr.fetchall()
                                    if move_sql2:
                                        move_line.append(line)
                elif line['doc_type'] == 'product' and product_id.code == 'M0501060001':
                    move_line.append(line)
                else:
                    move_line.append(line)
            return move_line 
        
        def get_account_move_line(move_id, material_issue_id, move_type):
            
            move = self.pool.get('account.move').browse(cr,uid,move_id)
            if move_type == 'freight':
                sql = '''
                   select name from account_invoice where move_id = %s and sup_inv_id is not null
                '''%(move_id)
                cr.execute(sql)
                for invoice in cr.dictfetchall():
                   name = invoice['name'] or 0
            if move_type == 'good':
                sql = '''
                    select doc_no from tpt_material_issue where id = %s 
                '''%(material_issue_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['doc_no']
            if move_type == 'grn':
                sql = '''
                   select name from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s) 
                '''%(move_id)
                cr.execute(sql)
                for qty in cr.dictfetchall():
                    name = qty['name']
            return name
        
        def get_transaction_qty(o, move_id, material_issue_id, product_dec, move_type, product_id):
            date_from = o.date_from
            categ = product_id.categ_id.cate_name
            quantity = 0
            price_unit = 0
            if categ=='raw':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
                if move_type == 'freight':
                    quantity = 0
                if move_type == 'product':
                    production_id = self.pool.get('mrp.production').browse(cr,uid,product_dec)
                    for line in production_id.move_lines2:
                        if line.product_id.id == product_id.id:
                            quantity += line.product_qty
                    quantity = -quantity
                if move_type == 'good':
                    sql = '''
                        select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                        where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                        group by product_id 
                    '''%(material_issue_id, locat_ids[0], product_id.id)
                    cr.execute(sql)
                    for qty in cr.dictfetchall():
                        quantity = qty['product_isu_qty']
                if move_type == 'grn':
                    sql = '''
                        select * from stock_move
                        where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
                        and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                    '''%(move_id, product_id.id)
                    cr.execute(sql)
                    moves = cr.dictfetchall()
                    grn_name = get_account_move_line(move_id, material_issue_id, move_type)
                    if self.num_call_grn['grn_name']==grn_name:
                        self.num_call_grn['num'] += 1
                    else:
                        self.num_call_grn['grn_name']=grn_name
                        self.num_call_grn['num'] = 0
                    if len(moves)>self.num_call_grn['num']:
                        move = moves[self.num_call_grn['num']]
                        if move['action_taken'] == 'direct' and move['location_dest_id']==locat_ids[0]:
                            quantity = move['product_qty']
                            price_unit = move['price_unit']
                        if move['action_taken'] == 'need':
                            sql1 = '''
                                select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                            '''%(move['id'])
                            cr.execute(sql1)
                            need = cr.dictfetchone()
                            if need:
                                quantity = need['qty_approve'] or 0
                                price_unit = move['price_unit']
            if categ=='spares':
                parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
                if move_type == 'freight':
                    quantity = 0
                if move_type == 'product':
                    production_id = self.pool.get('mrp.production').browse(cr,uid,product_dec)
                    for line in production_id.move_lines2:
                        if line.product_id.id == product_id.id:
                            quantity += line.product_qty
                    quantity = -quantity
                if move_type == 'good':
                    sql = '''
                        select case when sum(-1*product_isu_qty)!=0 then sum(-1*product_isu_qty) else 0 end product_isu_qty, product_id from tpt_material_issue_line
                        where material_issue_id in (select id from tpt_material_issue where id = %s and warehouse = %s and state = 'done') and product_id = %s
                        group by product_id 
                    '''%(material_issue_id, locat_ids[0], product_id.id)
                    cr.execute(sql)
                    for qty in cr.dictfetchall():
                        quantity = qty['product_isu_qty']
                if move_type == 'grn':
                    sql = '''
                        select * from stock_move
                        where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s)) 
                        and product_id = %s and ((id in (select need_inspec_id from tpt_quanlity_inspection where state in ('done', 'remaining')) and action_taken='need') or action_taken='direct') order by si_no
                    '''%(move_id, product_id.id)
                    cr.execute(sql)
                    moves = cr.dictfetchall()
                    grn_name = get_account_move_line(move_id, material_issue_id, move_type)
                    if self.num_call_grn['grn_name']==grn_name:
                        self.num_call_grn['num'] += 1
                    else:
                        self.num_call_grn['grn_name']=grn_name
                        self.num_call_grn['num'] = 0
                    if len(moves)>self.num_call_grn['num']:
                        move = moves[self.num_call_grn['num']]
                        if move['action_taken'] == 'direct' and move['location_dest_id']==locat_ids[0]:
                            quantity = move['product_qty']
                            price_unit = move['price_unit']
                        if move['action_taken'] == 'need':
                            sql1 = '''
                                select qty_approve from tpt_quanlity_inspection where state in ('done', 'remaining') and need_inspec_id=%s
                            '''%(move['id'])
                            cr.execute(sql1)
                            need = cr.dictfetchone()
                            if need:
                                quantity = need['qty_approve'] or 0
                                price_unit = move['price_unit']
            self.transaction_qty += quantity
            self.current_transaction_qty = quantity
            self.current_price_unit = price_unit
            return quantity
        
        def stock_value(product_id, move_id, doc_type):
            if doc_type=='freight':
                self.current_transaction_qty = 1
                sql = '''
                    select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                    where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                    group by product_id
                   '''%(product_id.id, move_id)
                cr.execute(sql)
                for inventory in cr.dictfetchall():
                    avg_cost = inventory['line_net'] or 0
                    return self.current_transaction_qty*avg_cost
            else:
                return self.current_transaction_qty*self.current_price_unit
        
        def get_line_stock_value(o, move_id, material_issue_id, move_type, date, product_id):
            date_from = o.date_from
            opening_stock_value = 0
            total_cost = 0
            hand_quantity = 0
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            if move_type == 'freight':
                sql = '''
                    select case when sum(line_net)!=0 then sum(line_net) else 0 end line_net, product_id from account_invoice_line 
                    where product_id = %s and invoice_id in (select id from account_invoice where move_id = %s and sup_inv_id is not null)
                    group by product_id
                '''%(product_id.id, move_id)
                cr.execute(sql)
                for inventory in cr.dictfetchall():
                    avg_cost = inventory['line_net'] or 0
            
            if move_type == 'grn':
                sql = '''
                         select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                         from stock_move st
                             join stock_location loc1 on st.location_id=loc1.id
                             join stock_location loc2 on st.location_dest_id=loc2.id
                         where st.state='done' and st.location_dest_id != st.location_id
                         and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' and st.location_id!=st.location_dest_id
                         and st.location_dest_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s')
                         
                 '''%(product_id.id, locat_ids[0], date)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
                sql = '''
                    select * from stock_move where picking_id in (select id from stock_picking where name in (select LEFT(name,17) from account_move_line where move_id = %s))
                '''%(move_id) 
                cr.execute(sql)
                for line in cr.dictfetchall():
                    if line['action_taken'] == 'need':
                        sql = '''
                            select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done', 'remaining')
                        '''%(line['id'])
                        cr.execute(sql)
                        inspec = cr.dictfetchone()
                        if inspec:
                            hand_quantity += inspec['qty_approve'] or 0
                            total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
                avg_cost = hand_quantity and total_cost/hand_quantity or 0 
       
            if move_type == 'good':
                good = self.pool.get('tpt.material.issue').browse(cr,uid,material_issue_id)
                sql = '''
                      select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                      from stock_move st
                          join stock_location loc1 on st.location_id=loc1.id
                          join stock_location loc2 on st.location_dest_id=loc2.id
                      where st.state='done' and st.location_dest_id != st.location_id
                      and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and st.location_id!=st.location_dest_id
                      and st.location_id = %s and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') = '%s'
                         
                 '''%(product_id.id, locat_ids[0], good.date_expec)
                cr.execute(sql)
                inventory = cr.dictfetchone()
                if inventory:
                    hand_quantity = inventory['ton_sl'] or 0
                    total_cost = inventory['total_cost'] or 0
                    avg_cost = hand_quantity and total_cost/hand_quantity or 0 
            return avg_cost
            
        def get_receipt_value(o, product_id):
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
                            where st.state='done' and st.location_dest_id != st.location_id
                            and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' 
                                    and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
                                        or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
                                              (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
                                    )foo
                            '''%(locat_ids[0],product_id,year,date_from,year,date_from)
            cr.execute(sql)
            inventory = cr.dictfetchone()
            if inventory:
                hand_quantity = inventory['ton_sl'] or 0
                total_cost = inventory['total_cost'] or 0
            sql = '''
                   select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= '%s' and state = 'done')
               '''%(product_id,date_from) 
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
        
        def get_qty_opening_chuaro(o, product_id):
            date_from = o.date_from
            parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
            sql = '''
                select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty_chuaro
                from stock_move where product_id = %s and state = 'done' and issue_id is null 
                and picking_id is null and inspec_id is null and location_id = %s 
                and to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and location_id != location_dest_id
            '''%(product_id, locat_ids[0], date_from)
            cr.execute(sql)
            product_qty_chuaro = cr.dictfetchone()['product_qty_chuaro']
            return product_qty_chuaro

        ## START       
        statement_obj = self.pool.get('tpt.raw.material.stock.statement')
        cr.execute('delete from tpt_raw_material_stock_statement')
        statement = self.browse(cr, uid, ids[0])
        statement_line = []
        for line in get_categ(statement):
            stock_in_out_line = []
            good = 0
            current = 0
            product = 0
            for seq, phuoc in enumerate(get_detail_lines(statement, line)):
                trans_qty = get_transaction_qty(statement,phuoc['id'], phuoc['material_issue_id'], phuoc['product_dec'], phuoc['doc_type'], line)
                if phuoc['doc_type']=='good':
                    qty = 0
                    value = 0
                    opening_stock = get_day_opening_stock_date_period(statement,line.id)
                    opening_stock_value = get_day_opening_stock_value(statement,line.id)
                    for l in stock_in_out_line:
                        qty += l[2]['transaction_quantity'] 
                        value += l[2]['stock_value']
                    if seq == 0:
                        st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
                    else:
                        st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
                    st_value = (st)*(trans_qty)
                    good += (-st_value)
                elif phuoc['doc_type']=='product':
                    qty = 0
                    value = 0
                    opening_stock = get_day_opening_stock_date_period(statement,line.id)
                    opening_stock_value = get_day_opening_stock_value(statement,line.id)
                    for l in stock_in_out_line:
                        qty += l[2]['transaction_quantity'] 
                        value += l[2]['stock_value']
                    if seq == 0:
                        st = (qty+opening_stock) and (value+opening_stock_value)/(qty+opening_stock) or 0
                    else:
                        st = (qty+opening_stock) and cur/(qty+opening_stock) or 0
                    st_value = (st)*(trans_qty)
                    product += (-st_value)
                else:
                    st_value = stock_value(line, phuoc['id'], phuoc['doc_type'])
                self.st_sum_value += st_value
                if seq == 0:
                    cur = get_day_opening_stock_value(statement,line.id)+st_value+current
                else:
                    cur = st_value+current
                current = cur
                stock_in_out_line.append((0,0,{
                    'transaction_quantity': trans_qty,
                    'stock_value': st_value,
                    'current_material_value':cur,
                }))
            statement_line.append((0,0,{
                'item_code': line.default_code,
                'item_name': line.name,
                'uom':line.uom_id and line.uom_id.name or 0,
                'day_open_stock': get_day_opening_stock(statement,line.id),
                'day_inward':get_day_inward(statement,line.id),
                'day_outward': get_day_outward(statement,line.id),
                'day_close_stock': get_closing_stock(statement,get_day_opening_stock(statement,line.id),get_day_inward(statement,line.id),get_day_outward(statement,line.id)),
                'day_close_value': get_day_opening_stock_value(statement,line.id)+get_receipt_value(statement,line.id)-(good)-product,
#                 'day_close_value': get_closing_stock(statement,get_day_opening_stock_value(statement,line.id),get_day_inward_value(statement,line.id),get_day_outward_value(statement,line.id)),   
                'month_open_stock': get_month_opening_stock(statement,line.id),
                'month_inward': get_month_inward(statement,line.id),
                'month_outward': get_month_outward(statement,line.id),
                'month_close_stock': get_closing_stock(statement,get_month_opening_stock(statement,line.id),get_month_inward(statement,line.id),get_month_outward(statement,line.id)),
                'month_close_value': get_day_opening_stock_value(statement,line.id)+get_receipt_value(statement,line.id)-(good)-product,
                'year_open_stock': get_year_opening_stock(statement,line.id),
                'year_inward': get_year_inward(statement,line.id),
                'year_outward': get_year_outward(statement,line.id),
                'year_close_stock': get_closing_stock(statement,get_year_opening_stock(statement,line.id),get_year_inward(statement,line.id),get_year_outward(statement,line.id)),
                'year_close_value': get_day_opening_stock_value(statement,line.id)+get_receipt_value(statement,line.id)-(good)-product, 
#                 'year_close_value': get_day_closing_stock_value(statement,line.id),
 
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
