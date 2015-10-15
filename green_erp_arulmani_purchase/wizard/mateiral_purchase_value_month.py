# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class mateiral_purchase_value_month(osv.osv_memory):
    _name = "mateiral.purchase.value.month"
    _columns = {
             'year': fields.many2one('account.fiscalyear','Year', required=True),
             'material_cate':fields.many2one('product.category','Material Category', required=True),
             'material_ids': fields.many2many('product.product', 'material_ref_report', 'mate_pur_month_id', 'product_id', 'Material'),  
             'avg_value': fields.selection(
            [('0', '0'),            
            ('1', '1 to 5000'),
            ('5001', '5001 to 10000'),
            ('all', 'All'),],
            'Average Value'),
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'mateiral.purchase.value.month'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_mateiral_purchase_value_month', 'datas': datas}   
     

mateiral_purchase_value_month()

class mateiral_purchase_value_day(osv.osv_memory):
    _name = "mateiral.purchase.value.day"
    _columns = {
             'year': fields.many2one('account.fiscalyear','Year'),
             'month_year': fields.many2one('account.period','Year and Month', required=True),
             'material_cate':fields.many2one('product.category','Material Category', required=True),
             'material_ids': fields.many2many('product.product', 'day_wise_material_ref_report', 'mate_pur_day_id', 'product_id', 'Material'),  
             'avg_value': fields.selection(
            [('0', '0'),            
            ('1', '1 to 5000'),
            ('5001', '5001 to 10000'),
            ('all', 'All'),],
            'Average Value'),
    }
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'mateiral.purchase.value.day'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'day_wise_report_material_purchase_value', 'datas': datas}   
     

mateiral_purchase_value_day()
