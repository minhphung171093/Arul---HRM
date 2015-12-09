# -*- coding: utf-8 -*-
##############################################################################
#
#    Tenth Planet Technologies
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
from green_erp_arulmani_purchase.report.amount_to_text_indian import Number2Words
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
from green_erp_arulmani_purchase.report import amount_to_text_en

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
        
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
                                  
        'get_date': self.get_date,
        'get_onhand_qty': self.get_onhand_qty,
        
        })
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')  

    def get_onhand_qty(self, product_id):
          location_id = False
          locat_ids = []
          parent_ids = []
          cate_name = product_id.categ_id and product_id.categ_id.cate_name or False
          if cate_name == 'finish':
              parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
              if parent_ids:
                  locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
              if locat_ids:
                  location_id = locat_ids[0]
                  sql = '''
                      select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
                          (select st.product_qty as product_qty
                              from stock_move st 
                              where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                           union all
                           select st.product_qty*-1 as product_qty
                              from stock_move st 
                              where st.state='done'
                              and st.product_id=%s
                                          and location_id=%s
                                          and location_dest_id != location_id
                          )foo
                  '''%(product_id.id,location_id,product_id.id,location_id)
                  cr.execute(sql)
                  onhand_qty = cr.dictfetchone()['onhand_qty']
          if cate_name == 'raw':
              parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
              if parent_ids:
                  locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
              if locat_ids:
                  location_id = locat_ids[0]
          if cate_name == 'spares':
              parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
              if parent_ids:
                  locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
              if locat_ids:
                  location_id = locat_ids[0]
          if location_id and cate_name != 'finish':
              sql = '''
                  select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
                      (select st.product_qty as product_qty
                          from stock_move st 
                          where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                       union all
                       select st.product_qty*-1 as product_qty
                          from stock_move st 
                          where st.state='done'
                                  and st.product_id=%s
                                      and location_id=%s
                                      and location_dest_id != location_id
                      )foo
              '''%(product_id.id,location_id,product_id.id,location_id)
              self.cr.execute(sql)
              onhand_qty = self.cr.dictfetchone()['onhand_qty']
              
              return onhand_qty
