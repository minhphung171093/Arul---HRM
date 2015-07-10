# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class daily_sale_form(osv.osv_memory):
    _name = "daily.sale.form"
    _columns = {    
                'product_id': fields.many2one('product.product', 'Material', required=False),
                'application_id':fields.many2one('crm.application','Application', required=False),
                'state_id':fields.many2one("res.country.state", 'Region', required=False),
                'customer_id':fields.many2one("res.partner", 'Customer', required=False),
                'name_consignee_id':fields.many2one("res.partner", 'Consignee', required=False),
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'city': fields.char('City', size=128),
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
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'daily.sale.form'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'daily_sale_report', 'datas': datas}
        
daily_sale_form()