# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class tpt_stock_inward_outward(osv.osv_memory):
    _name = "tpt.stock.inward.outward"
    _columns = {
        'name': fields.char('', readonly=True),
        'product_id': fields.many2one('product.product', 'Material'),
        'product_name': fields.char('Product Name: '),
        'product_code': fields.char('Product Code: '),
        'date_from':fields.date('Date From'),
        'date_to':fields.date('Date To'),
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.stock.inward.outward'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_inward_outward_xls', 'datas': datas}
#     
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.stock.inward.outward'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_inward_outward_pdf', 'datas': datas}
    
tpt_stock_inward_outward()

class stock_inward_outward_report(osv.osv_memory):
    _name = "stock.inward.outward.report"
    _columns = {    
                'product_id': fields.many2one('product.product', 'Material', required=True),
                'date_from':fields.date('Date From', required=True),
                'date_to':fields.date('Date To', required=True),
                }
    
    def _check_date(self, cr, uid, ids, context=None):
        for date in self.browse(cr, uid, ids, context=context):
            if date.date_to < date.date_from:
                raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                return False
        return True
    _constraints = [
        (_check_date, 'Identical Data', []),
    ]
    
    def print_report(self, cr, uid, ids, context=None):
        stock_obj = self.pool.get('tpt.stock.inward.outward')
        cr.execute('delete from tpt_stock_inward_outward')
        stock = self.browse(cr, uid, ids[0])
        vals = {
            'name': 'Stock Inward and Outward Details',
            'product_id': stock.product_id.id,
            'date_from': stock.date_from,
            'date_to': stock.date_to,
            'product_name': stock.product_id.name,
            'product_code': stock.product_id.code,
        }
        stock_id = stock_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_purchase', 'view_tpt_stock_inward_outward_form')
        return {
                    'name': 'Stock Inward and Outward Details',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.stock.inward.outward',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': stock_id,
                }
    
stock_inward_outward_report()

class product_product(osv.osv):
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_inward_outward'):
            sql = '''
                 select product_product.id 
                    from product_product,product_template 
                    where product_template.categ_id in(select id from product_category where cate_name in ('raw','spares'))
                    and product_product.product_tmpl_id = product_template.id
            '''
            cr.execute(sql)
            product_ids = [row[0] for row in cr.fetchall()]
            args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
product_product()

