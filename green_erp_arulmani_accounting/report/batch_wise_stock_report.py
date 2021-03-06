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
            'convert_date': self.convert_date,
            'get_line_product':self.get_line_product,
            'get_date': self.get_date,
            'get_location': self.get_location,
            'get_line_batch': self.get_line_batch,
            'get_batch_name': self.get_batch_name,
            'get_application': self.get_application,
            'get_total_qty': self.get_total_qty,
            'get_total': self.get_total_qty,
            'get_filter': self.get_filter,
        })
    def get_filter(self, o):
        print o#.batch_wise_line
        res = [] 
        for prd in o.batch_wise_line:
            if prd.col_1 not in ('S.No'):
                res.append( {
                       'col_1':prd.col_1,
                       'col_2':prd.col_2,
                       'col_3':prd.col_3,
                       'col_4':prd.col_4,
                       })
        return res
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_date(self):
        return self.convert_date(time.strftime('%Y-%m-%d'))
    
    def get_location(self):
        wizard_data = self.localcontext['data']['form']
        return wizard_data['location_id'][1]
    
    def get_line_product(self):
        wizard_data = self.localcontext['data']['form']
        product_data = wizard_data['product_id']
        location_data = wizard_data['location_id']
        if product_data:
            product_ids = [product_data[0]]
        else:
            application_data = wizard_data['application_id']
            if application_data:
                sql = '''
                    select foo.product_id,case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                        (select st.product_id,st.product_qty
                            from stock_move st 
                            where st.state='done' and st.location_dest_id = %s
                                and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s and history_id is null)
                        union all
                        select st.product_id,st.product_qty*-1
                            from stock_move st 
                            where st.state='done' and st.location_id = %s
                                and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s and history_id is null)
                        )foo
                        group by foo.product_id
                '''%(location_data[0],application_data[0],location_data[0],application_data[0])
                self.cr.execute(sql)
                product_ids = []
                for r in self.cr.fetchall():
                    if r[1]>0:
                        product_ids.append(r[0])
            else:
                sql = '''
                    select foo.product_id,case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                        (select st.product_id,st.product_qty
                            from stock_move st 
                            where st.state='done' and st.location_dest_id = %s
                        union all
                        select st.product_id,st.product_qty*-1
                            from stock_move st 
                            where st.state='done' and st.location_id = %s
                        )foo
                        group by foo.product_id
                '''%(location_data[0],location_data[0])
                self.cr.execute(sql)
                product_ids = []
                for r in self.cr.fetchall():
                    if r[1]>0:
                        product_ids.append(r[0])
        return self.pool.get('product.product').browse(self.cr, self.uid, product_ids)
    
    def get_line_batch(self,product):
        wizard_data = self.localcontext['data']['form']
        location_data = wizard_data['location_id']
        application_data = wizard_data['application_id']
        if application_data:
            sql = '''
                select foo.prodlot_id,case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                    (select st.prodlot_id,st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                    union all
                    select st.prodlot_id,st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_id = %s
                    )foo
                    where foo.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s and history_id is null)
                    group by foo.prodlot_id
            '''%(product.id,location_data[0],product.id,location_data[0],application_data[0])
            self.cr.execute(sql)
            tons = []
            for r in self.cr.fetchall():
                if r[1]!=0:
                    tons.append(r)
        else: 
            sql = '''
                select foo.prodlot_id,case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                    (select st.prodlot_id,st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                    union all
                    select st.prodlot_id,st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_id = %s
                    )foo
                    group by foo.prodlot_id
            '''%(product.id,location_data[0],product.id,location_data[0])
            self.cr.execute(sql)
            tons = []
            for r in self.cr.fetchall():
                if r[1]!=0:
                    tons.append(r)
        return tons
    
    def get_application(self,product,batch_id):
        def get_name_application(application_id=False):
            if application_id:
                return self.pool.get('crm.application').browse(self.cr, self.uid, application_id).name
            else:
                return ''
        wizard_data = self.localcontext['data']['form']
        application_data = wizard_data['application_id']
        if application_data:
            return application_data[1]
        else:
            if product and batch_id:
                sql = 'select applicable_id from tpt_quality_verification where history_id is null and product_id = %s and prod_batch_id=%s'%(product.id,batch_id)
                self.cr.execute(sql)
                kq = self.cr.fetchone()
                
                return kq and get_name_application(kq[0]) or ''
            else:
                return ''
    
    def get_batch_name(self,batch_id=False):
        if batch_id:
            return self.pool.get('stock.production.lot').browse(self.cr,self.uid,batch_id).name
        else:
            return 'Undefined'
        
    def get_total_qty(self, product):
        wizard_data = self.localcontext['data']['form']
        location_data = wizard_data['location_id']
        application_data = wizard_data['application_id']
        if application_data:
            sql = '''
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                    (select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                            and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s and history_id is null)
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_id = %s
                            and st.prodlot_id in (select prod_batch_id from tpt_quality_verification where applicable_id = %s and history_id is null)
                    )foo
            '''%(product.id,location_data[0],application_data[0],product.id,location_data[0],application_data[0])
            self.cr.execute(sql)
            tons = self.cr.fetchone()[0]
        else: 
            sql = '''
                select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end ton_sl from 
                    (select st.product_qty
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                    union all
                    select st.product_qty*-1
                        from stock_move st 
                        where st.state='done' and st.product_id = %s and st.location_id = %s
                    )foo
            '''%(product.id,location_data[0],product.id,location_data[0])
            self.cr.execute(sql)
            tons = self.cr.fetchone()[0]
        return float(tons)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

