# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class alert_warning_form_purchase(osv.osv_memory):
    _name = "alert.warning.form.purchase"
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(alert_warning_form_purchase, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            po_line = self.pool.get('purchase.order.line').browse(cr, uid, context['active_id'], context=context)
            ton_sl = 0
            mess = ''
            if po_line.product_id:
                if po_line.product_id.categ_id.cate_name != 'consum':
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
                    '''%(po_line.product_id.id,po_line.product_id.id)
                    cr.execute(sql)
                    ton_sl = cr.dictfetchone()['ton_sl']
                    mess = 'Current Stock Position of product %s (%s) is %s %s'%(po_line.product_id.name,po_line.product_id.default_code,ton_sl,po_line.product_uom.name)
                else:
                    mess = 'The system does not manage quantity on stock for Consumable Product!'
            res.update({'name': mess})
        return res
    
    _columns = {    
                'name': fields.char(string="Title", size=1024, readonly=True),
                }
alert_warning_form_purchase()