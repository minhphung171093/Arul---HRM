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
        })
    
    def convert_date(self, date):
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
        sql = '''
            select foo.prodlot_id,case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                (select st.prodlot_id,st.product_qty
                    from stock_move st 
                    where st.state='done' and st.product_id = %s and st.location_dest_id = %s
                union all
                select st.prodlot_id,st.product_qty*-1
                    from stock_move st 
                    where st.state='done' and st.product_id = %s and st.location_id = %s
                )foo
                group by st.prodlot_id
        '''%(product.id,location_data[0],product.id,location_data[0])
        self.cr.execute(sql)
        return True
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

