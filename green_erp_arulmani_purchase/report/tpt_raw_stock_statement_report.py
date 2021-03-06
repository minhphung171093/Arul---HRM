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
#                 'get_date_to':self.get_date_to,
#                 'get_category':self.get_category,
#                 'get_product':self.get_product,
#                 'get_name_product':self.get_name_product,
#                 'get_categ':self.get_categ,
#                 'get_opening_stock':self.get_opening_stock,
#                 'get_qty':self.get_qty,
#                 'get_qty_out':self.get_qty_out,
#                 'get_opening_stock_value': self.get_opening_stock_value,
#                 'get_receipt_value':self.get_receipt_value,
#                 'get_consumption_value':self.get_consumption_value,
                'get_closing_stock':self.get_closing_stock,
                'convert_date': self.convert_date,
#               'get_categ_product':self.get_categ_product
              
              
              
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
#     def get_date(self):
#         date = time.strftime('%Y-%m-%d'),
#         date = datetime.strptime(date[0], DATE_FORMAT)
#         return date.strftime('%d/%m/%Y')
#     
#     
#     def get_category(self):
#         wizard_data = self.localcontext['data']['form']
#         cat = wizard_data['categ_id']
#         if cat:
#             cat_obj = self.pool.get('product.category').browse(self.cr,self.uid,cat[0])
#             return cat_obj
#         return False
#     
#     def get_product(self):
#         wizard_data = self.localcontext['data']['form']
#         pro = wizard_data['product_id']
#         if pro:
#             pro_obj = self.pool.get('product.product').browse(self.cr,self.uid,pro[0])
#             return pro_obj
#         return False
# 
#     def get_categ(self):
#         wizard_data = self.localcontext['data']['form']
#         categ = wizard_data['categ_id']
#         product = wizard_data['product_id']
#         pro_obj = self.pool.get('product.product')
#         categ_ids = []
# 
#         if categ and product:
#             sql='''
#                         select product_product.id 
#                         from product_product,product_template 
#                         where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
#                         and product_product.product_tmpl_id = product_template.id and product_product.id = %s ;
#             '''%(categ[0],product[0])
#             self.cr.execute(sql)
#             categ_ids += [r[0] for r in self.cr.fetchall()]
#             return self.pool.get('product.product').browse(self.cr,self.uid,categ_ids)
#         if categ:
#             sql='''
#                         select product_product.id 
#                         from product_product,product_template 
#                         where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
#                         and product_product.product_tmpl_id = product_template.id;
#             '''%(categ[0])
#             self.cr.execute(sql)
#             categ_ids += [r[0] for r in self.cr.fetchall()]
#             return pro_obj.browse(self.cr,self.uid,categ_ids)
#         
#     def get_opening_stock(self,product_id):
# #         wizard_data = self.localcontext['data']['form']
# #         date_from = wizard_data['date_from']
# #         date_to = wizard_data['date_to']
# # #         product_id = wizard_data['product_id']
# #         sql = '''
# #             select case when sum(product_qty)!=0 then sum(product_qty) else 0 end product_qty from stock_move  
# #             where product_id = %s and picking_id in (select id from stock_picking where date < '%s' and state = 'done' and type = 'in')
# #         '''%(product, date_from)
# #         self.cr.execute(sql)
# #         product_qty = self.cr.dictfetchone()['product_qty']
# #          
# #         sql = '''
# #             select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
# #             where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and state = 'done')
# #         '''%(product, date_from)
# #         self.cr.execute(sql)
# #         product_isu_qty = self.cr.dictfetchone()['product_isu_qty']
# # 
# #         opening_stock = product_qty-product_isu_qty
# # 
# #         return opening_stock
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         categ = wizard_data['categ_id']
#         if categ[1]=='Raw Materials':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#             sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id=%s and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_from,date_from)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#             if inventory:
#                 sql = '''
#                             select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
#                             where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
#                         '''%(product_id, date_from,locat_ids[0])
#                 self.cr.execute(sql)
#                 product_isu_qty = self.cr.fetchone()[0]
#                 open_qty = (inventory and inventory['ton_sl'] or 0) - product_isu_qty
#         if categ[1] =='Spares':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
#             sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id=%s and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_from,date_from)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#             if inventory:
#                 sql = '''
#                             select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
#                             where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec < '%s' and warehouse = %s and state = 'done')
#                         '''%(product_id, date_from,locat_ids[0])
#                 self.cr.execute(sql)
#                 product_isu_qty = self.cr.fetchone()[0]
#                 open_qty = (inventory and inventory['ton_sl'] or 0) - product_isu_qty
#         return open_qty
#         
#     
#     def get_qty(self, line):
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         categ = wizard_data['categ_id']
#         ton = 0
#         inspec = 0
# #         categ_ids = self.pool.get('product.category').search(self.cr, self.uid, [('id','=',categ[0])])
#         if categ[1]=='Raw Materials':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#             sql = '''
#                             select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
#                                 (select st.product_qty
#                                     from stock_move st 
#                                     where st.state='done' and st.product_id = %s and st.location_dest_id = %s 
#                                         and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                                              or (id in (select move_id from stock_inventory_move_rel where inventory_id in 
#                                               (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
#                                     )foo
#                             '''%(line,locat_ids[0],date_from,date_to,date_from,date_to)
#             self.cr.execute(sql)
#             ton_arr = self.cr.fetchone()
#             if ton_arr:
#                 ton = ton_arr[0] or 0
#             else:
#                 ton = 0
#             sql = '''
#                    select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                '''%(line,date_from,date_to) 
#             self.cr.execute(sql)
#             for move in self.cr.dictfetchall():
#                if move['action_taken'] == 'need':
#                    sql = '''
#                        select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
#                    '''%(move['id'])
#                    self.cr.execute(sql)
#                    inspec_arr = self.cr.fetchone()
#                    if inspec_arr:
#                        inspec = inspec_arr[0] or 0
#                    else:
#                        inspec = 0
#                    ton = ton  + inspec
#             return ton
#         if categ[1] =='Spares':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
#             sql = '''
#                             select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton from 
#                                 (select st.product_qty
#                                     from stock_move st 
#                                     where st.state='done' and st.product_id = %s and st.location_dest_id = %s 
#                                     
#                                         and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                                              or (id in (select move_id from stock_inventory_move_rel where inventory_id in 
#                                               (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
#                                     )foo
#                             '''%(line,locat_ids[0],date_from,date_to,date_from,date_to)
#             self.cr.execute(sql)
#             ton_arr = self.cr.fetchone()
#             if ton_arr:
#                 ton = ton_arr[0] or 0
#             else:
#                 ton = 0
#             sql = '''
#                    select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                '''%(line,date_from,date_to) 
#             self.cr.execute(sql)
#             for move in self.cr.dictfetchall():
#                if move['action_taken'] == 'need':
#                    sql = '''
#                        select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
#                    '''%(move['id'])
#                    self.cr.execute(sql)
#                    inspec_arr = self.cr.fetchone()
#                    if inspec_arr:
#                        inspec = inspec_arr[0] or 0
#                    else:
#                        inspec = 0
#                    ton = ton  + inspec
#             return ton
#     
#     def get_qty_out(self, line):
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         categ = wizard_data['categ_id']
# #         categ_ids = self.pool.get('product.category').search(self.cr, self.uid, [('id','=',categ[0])])
#         if categ[1]=='Raw Materials':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#             sql = '''
#                     select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
#                     where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
#                 '''%(line, date_from,date_to,locat_ids[0])
#             self.cr.execute(sql)
#             product_isu_qty = self.cr.dictfetchone()
#         if categ[1] =='Spares':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
#             sql = '''
#                     select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
#                     where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
#                 '''%(line, date_from,date_to,locat_ids[0])
#             self.cr.execute(sql)
#             product_isu_qty = self.cr.dictfetchone()
#         return product_isu_qty and product_isu_qty['product_isu_qty'] or 0
#     
#     def get_opening_stock_value(self, product_id):
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         opening_stock_value = 0
#         categ = wizard_data['categ_id']
#         if categ[1]=='Raw Materials':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
# #             sql = '''
# #                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
# #                         (select st.product_qty,st.price_unit*st.product_qty as price_unit
# #                             from stock_move st
# #                                 join stock_location loc1 on st.location_id=loc1.id
# #                                 join stock_location loc2 on st.location_dest_id=loc2.id
# #                             where st.state='done' and st.location_dest_id = %s  and st.product_id=%s
# #                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
# #                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
# #                                     )
# #                         union all
# #                             select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
# #                             from stock_move st
# #                                 join stock_location loc1 on st.location_id=loc1.id
# #                                 join stock_location loc2 on st.location_dest_id=loc2.id
# #                             where st.state='done' and st.location_id=%s and st.product_id=%s
# #                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
# #                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
# #                                     )
# #                         )foo
# #                     '''%(locat_ids[0],product_id,date_from,date_from,locat_ids[0],product_id,date_from,date_from)
#             sql = '''
#                       select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                         from stock_move st
#                             join stock_location loc1 on st.location_id=loc1.id
#                             join stock_location loc2 on st.location_dest_id=loc2.id
#                         where st.state='done' and st.location_dest_id=%s and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_from,date_from)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#             if inventory:
#                     hand_quantity = inventory['ton_sl'] or 0
#                     total_cost = inventory['total_cost'] or 0
#                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
#                     sql = '''
#                         select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
#                             from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
#                     '''%(date_from,locat_ids[0],product_id)
#                     self.cr.execute(sql)
#                     product_isu_qty = self.cr.fetchone()[0]
#                     opening_stock_value = total_cost-(product_isu_qty*avg_cost)
#         if categ[1] =='Spares':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
# #             sql = '''
# #                     select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
# #                         (select st.product_qty,st.price_unit*st.product_qty as price_unit
# #                             from stock_move st
# #                                 join stock_location loc1 on st.location_id=loc1.id
# #                                 join stock_location loc2 on st.location_dest_id=loc2.id
# #                             where st.state='done' and st.location_dest_id = %s  and st.product_id=%s
# #                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
# #                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
# #                                     )
# #                         union all
# #                             select -1*st.product_qty,st.price_unit*st.product_qty as price_unit
# #                             from stock_move st
# #                                 join stock_location loc1 on st.location_id=loc1.id
# #                                 join stock_location loc2 on st.location_dest_id=loc2.id
# #                             where st.state='done' and st.location_id=%s and st.product_id=%s
# #                                 and ( (picking_id in (select id from stock_picking where date < '%s' and state = 'done')) 
# #                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
# #                                     )
# #                         )foo
# #                     '''%(locat_ids[0],product_id,date_from,date_from,locat_ids[0],product_id,date_from,date_from)
#             sql = '''
#                   select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                     from stock_move st
#                         join stock_location loc1 on st.location_id=loc1.id
#                         join stock_location loc2 on st.location_dest_id=loc2.id
#                     where st.state='done' and st.location_dest_id=%s and st.product_id=%s
#                                 and ( (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') < '%s' and state = 'done')) 
#                                 or  (inspec_id in (select id from tpt_quanlity_inspection where date < '%s' and state in ('done','remaining')))
#                                 or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') <'%s' and state = 'done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_from,date_from)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#             if inventory:
#                     hand_quantity = inventory['ton_sl'] or 0
#                     total_cost = inventory['total_cost'] or 0
#                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
#                     sql = '''
#                         select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
#                             from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec<'%s' and warehouse = %s and state='done') and product_id=%s
#                     '''%(date_from,locat_ids[0],product_id)
#                     self.cr.execute(sql)
#                     product_isu_qty = self.cr.fetchone()[0]
#                     opening_stock_value = total_cost-(product_isu_qty*avg_cost)
#         return opening_stock_value
#         
#     def get_receipt_value(self, product_id):
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         categ = wizard_data['categ_id']
#         opening_stock_value = 0
#         hand_quantity = 0
#         if categ[1]=='Raw Materials':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#             sql = '''
#                 select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                     (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
#                         from stock_move st
#                             join stock_location loc1 on st.location_id=loc1.id
#                             join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' 
#                                     and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                                         or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
#                                               (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
#                                     )foo
#                             '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#         if categ[1] =='Spares':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
#             sql = '''
#                 select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
#                     (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
#                         from stock_move st
#                             join stock_location loc1 on st.location_id=loc1.id
#                             join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_dest_id = %s and st.product_id=%s and loc1.usage != 'internal' and loc2.usage = 'internal' 
#                                     and (picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                                         or (st.id in (select move_id from stock_inventory_move_rel where inventory_id in 
#                                               (select id from stock_inventory where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done'))))
#                                     )foo
#                             '''%(locat_ids[0],product_id,date_from,date_to,date_from,date_to)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#         if inventory:
#             hand_quantity = inventory['ton_sl'] or 0
#             total_cost = inventory['total_cost'] or 0
#         sql = '''
#                    select * from stock_move where product_id = %s and picking_id in (select id from stock_picking where to_date(to_char(date, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s' and state = 'done')
#                '''%(product_id,date_from,date_to) 
#         self.cr.execute(sql)
#         for line in self.cr.dictfetchall():
#             if line['action_taken'] == 'need':
#                 sql = '''
#                        select qty_approve from tpt_quanlity_inspection where need_inspec_id = %s and state in ('done','remaining')
#                    '''%(line['id'])
#                 self.cr.execute(sql)
#                 inspec = self.cr.dictfetchone()
#                 if inspec:
#                        hand_quantity += inspec['qty_approve'] or 0
#                        total_cost += line['price_unit'] * (inspec['qty_approve'] or 0)
#         return total_cost  
# #             avg_cost = hand_quantity and total_cost/hand_quantity or 0
# #             sql = '''
# #                 select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
# #                     from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and state='done') and product_id=%s
# #             '''%(date_from,date_to,product_id)
# #             self.cr.execute(sql)
# #             product_isu_qty = self.cr.fetchone()[0]
# #             opening_stock_value = total_cost-(product_isu_qty*avg_cost)
#             
#     def get_consumption_value(self, product_id):
#         wizard_data = self.localcontext['data']['form']
#         date_from = wizard_data['date_from']
#         date_to = wizard_data['date_to']
#         categ = wizard_data['categ_id']
# #         opening_stock_value = 0
# #         sql = '''
# #             select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl,case when sum(foo.price_unit)!=0 then sum(foo.price_unit) else 0 end total_cost from 
# #                 (select st.product_qty as product_qty,st.price_unit*st.product_qty as price_unit
# #                     from stock_move st
# #                         join stock_location loc1 on st.location_id=loc1.id
# #                         join stock_location loc2 on st.location_dest_id=loc2.id
# #                     where st.state='done' and st.product_id=%s and loc1.usage = 'internal' and loc2.usage != 'internal' and date between '%s' and '%s'
# #                 )foo
# #         '''%(product_id,date_from,date_to)
# #         self.cr.execute(sql)
# #         inventory = self.cr.dictfetchone()
# #         if inventory:
# #             hand_quantity = float(inventory['ton_sl'])
# #             total_cost = float(inventory['total_cost'])
# # #             avg_cost = hand_quantity and total_cost/hand_quantity or 0
# # #             sql = '''
# # #                 select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
# # #                     from tpt_material_issue_line where material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and state='done') and product_id=%s
# # #             '''%(date_from,date_to,product_id)
# # #             self.cr.execute(sql)
# # #             product_isu_qty = self.cr.fetchone()[0]
# # #             opening_stock_value = total_cost-(product_isu_qty*avg_cost)
# #         return total_cost      
#         consum_value = 0
#         if categ[1]=='Raw Materials':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw Material','Raw Materials','Raw material']),('location_id','=',parent_ids[0])])
#             sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s
#                                 and ( (issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and state in ('done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_to)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#             if inventory:
#                 hand_quantity = inventory['ton_sl'] or 0
#                 total_cost = inventory['total_cost'] or 0
#                 avg_cost = hand_quantity and total_cost/hand_quantity or 0
#                 sql = '''
#                     select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
#                     where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
#                 '''%(product_id, date_from,date_to,locat_ids[0])
#                 self.cr.execute(sql)
#                 product_isu_qty = self.cr.fetchone()[0]
#                 consum_value = (product_isu_qty*avg_cost)
#         if categ[1] =='Spares':
#             parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
#             locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spares','Spare','spares']),('location_id','=',parent_ids[0])])
#             sql = '''
#                           select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
#                             from stock_move st
#                                 join stock_location loc1 on st.location_id=loc1.id
#                                 join stock_location loc2 on st.location_dest_id=loc2.id
#                             where st.state='done' and st.location_id=%s and st.product_id=%s
#                                 and ( (issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and state in ('done')))
#                                     )
#                     '''%(locat_ids[0],product_id,date_from,date_to)
#             self.cr.execute(sql)
#             inventory = self.cr.dictfetchone()
#             if inventory:
#                 hand_quantity = inventory['ton_sl'] or 0
#                 total_cost = inventory['total_cost'] or 0
#                 avg_cost = hand_quantity and total_cost/hand_quantity or 0
#                 sql = '''
#                     select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty from tpt_material_issue_line  
#                     where product_id = %s and material_issue_id in (select id from tpt_material_issue where date_expec between '%s' and '%s' and warehouse = %s and state = 'done')
#                 '''%(product_id, date_from,date_to,locat_ids[0])
#                 self.cr.execute(sql)
#                 product_isu_qty = self.cr.fetchone()[0]
#                 consum_value = (product_isu_qty*avg_cost)
#         return consum_value     
#     
    def get_closing_stock(self, receipt,consum,opening):
        total_cost = 0
        total_cost = receipt - consum + opening
        return total_cost           
            
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

