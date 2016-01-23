# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class po_above10lacs(osv.osv_memory):
    _name = "po.above10lacs"
    _columns = {
        'year': fields.selection([(num, str(num)) for num in range(2000, 2026)], 'Year', required = True),
        'month': fields.selection([('1', 'January'),('2', 'February'), ('3', 'March'), ('4','April'), ('5','May'), ('6','June'), ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',required = True),
        'categ_id': fields.many2one('product.category', 'Material Category'),
       
    }
    _defaults = {       
        'year':int(time.strftime('%Y')),
        'month':int(time.strftime('%d')),
        }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'po.above10lacs'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        invoice_ids = self.browse(cr, uid, ids[0])
        if invoice_ids.categ_id:
            return {'type': 'ir.actions.report.xml', 'report_name': 'po_above10lacs', 'datas': datas}
        else:
            return {'type': 'ir.actions.report.xml', 'report_name': 'po_above10lacs_multiple', 'datas': datas}
    
    def print_report_multiple(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'po.above10lacs'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        
        invoice_ids = self.browse(cr, uid, ids[0])
        if invoice_ids.categ_id:
            return {'type': 'ir.actions.report.xml', 'report_name': 'po_above10lacs', 'datas': datas}
        else:
            return {'type': 'ir.actions.report.xml', 'report_name': 'po_above10lacs_multiple', 'datas': datas}
       
po_above10lacs()    
