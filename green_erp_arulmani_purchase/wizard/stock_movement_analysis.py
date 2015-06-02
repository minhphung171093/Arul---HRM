# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class stock_movement_analysis(osv.osv_memory):
    _name = "stock.movement.analysis"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Product Category',required = True),
                'product_id': fields.many2one('product.product', 'Product'),
                'date_from':fields.date('Date From',required = True),
                'date_to':fields.date('To',required = True),
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
    
    def onchange_categ_id(self, cr, uid, ids,categ_id=False, context=None):
        if categ_id:
            return {'value': {
                              'location_id': False,
                              'product_id': False,
                              } }
    def onchange_product_id(self, cr, uid, ids, categ_id=False, product_id=False, context=None):
        if categ_id and not product_id:
            return {'value': {
                                  'location_id': False,
                                  'product_id': False,
                                  } }
        elif categ_id and product_id:
            return {'value': {
                              'location_id': False,
                              } }
        elif product_id and not categ_id:
            return {'value': {
                              'location_id': False,
                              } }
    
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'stock.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_xls', 'datas': datas}
#             stock_obj = self.pool.get('tpt.form.movement.analysis')
#             cr.execute('delete from tpt_form_movement_analysis')
#             stock = self.browse(cr, uid, ids[0])
#             vals = {
#                 'name': 'Stock Movement Analysis ',
#                 'product_id': stock.product_id.id,
#                 'product_name': stock.product_id and stock.product_id.name or 'All' ,
#                 'product_name_title': 'Product',
#                 'date_from': stock.date_from,
#                 'date_to': stock.date_to,
#                 'date_from_title':'Date From: ',
#                 'date_to_title':'To: ',
#                 'categ_id': stock.categ_id.id,
#                 'categ_name': stock_obj.get_categ_name(cr, uid, ids,stock.categ_id.cate_name),
#                 'categ_name_title': 'Product Category',
#             }
#             stock_id = stock_obj.create(cr, uid, vals)
#             res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
#                                             'green_erp_arulmani_purchase', 'view_tpt_form_movement_analysis')
#             return {
#                         'name': 'Stock Movement Analysis',
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'res_model': 'tpt.form.movement.analysis',
#                         'domain': [],
#                         'type': 'ir.actions.act_window',
#                         'target': 'current',
#                         'res_id': stock_id,
#                     }
        
stock_movement_analysis()

class product_product(osv.osv):
    _inherit = "product.product"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('search_product_id'):
            if context.get('categ_id'):
                sql = '''
                     select product_product.id 
                        from product_product,product_template 
                        where product_template.categ_id in(select product_category.id from product_category where product_category.id = %s) 
                        and product_product.product_tmpl_id = product_template.id;
                '''%(context.get('categ_id'))
                cr.execute(sql)
                product_ids = [row[0] for row in cr.fetchall()]
                args += [('id','in',product_ids)]
        return super(product_product, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
       ids = self.search(cr, user, args, context=context, limit=limit)
       return self.name_get(cr, user, ids, context=context)
product_product()

class tpt_form_movement_analysis(osv.osv):
    _name = "tpt.form.movement.analysis"
    _columns = {    
                'categ_id': fields.many2one('product.category', 'Product Category'),
                'product_id': fields.many2one('product.product', 'Product'),
                'date_from':fields.date('Date From'),
                'date_from_title':fields.char('Date From'),
                'date_to':fields.date('To'),
                'date_to_title':fields.char('To'),
                'name':fields.char('Stock Movement Analysis',size=1024,readonly=True),
                'movement_line':fields.one2many('movement_analysis_line','movement_id','Stock Movement'),
                'categ_name':fields.char('Product Category',size=1024),
                'product_name':fields.char('Product',size=1024),
                'categ_name_title':fields.char('Product Category',size=1024),
                'product_name_title':fields.char('Product Category',size=1024),
                }



    def get_categ_name(self, cr, uid, ids,categ_name = False, context=None):
        if categ_name and categ_name == 'raw':
            cate_name = 'Raw Materials'
        if categ_name and categ_name == 'spares':
            cate_name = 'Spares'
        return cate_name
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.form.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_xls', 'datas': datas}
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.form.movement.analysis'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_stock_movement_analysis_pdf', 'datas': datas}
tpt_form_movement_analysis()


class tpt_movement_analysis_line(osv.osv):
    _name = "tpt.movement.analysis.line"
    _columns = {    
        'movement_id': fields.many2one('tpt.form.movement.analysis', 'Stock Movement', ondelete='cascade'),
        'item_code': fields.char('Item Code', size = 1024),
        'item_name': fields.char('Item Name', size = 1024),
        'uom': fields.char('UOM', size = 1024),
        'open_stock': fields.float('Opening Stock'),
        'open_value': fields.float('Opening Stock Value'),
        'receipt_qty': fields.float('Qty (Receipts)'),
        'receipt_value':fields.float('Stock Value (Receipts)'),
        'consum_qty': fields.float('Qty (Consumption)'),
        'consum_value':fields.float('Stock Value (Consumption)'),     
        'close_stock': fields.float('Closing Stock'),
        'close_value': fields.float('Closing Stock Value'),   
                }
    

tpt_movement_analysis_line()





