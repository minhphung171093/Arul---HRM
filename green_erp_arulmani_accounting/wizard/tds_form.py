# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tds_form_report(osv.osv_memory):
    _name = "tds.form.report"
    
    _columns = {
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'employee': fields.many2one('res.partner', 'Vendor',ondelete='restrict'),                
                'taxes_id':fields.many2one('account.tax','TDS %'),                 
                'code':fields.many2one('account.account', 'GL Account'),
                'invoice_type':fields.selection([('ser_inv','Service Invoice'),('sup_inv','Supplier Invoice (Without PO)'),('freight','Freight Invoice')],'Invoice Type'),
                 #'invoice_type':fields.selection([('ServiceInvoice','Service Invoice'),('SupplierInvoice(Without PO)','Supplier Invoice (Without PO)'),('Freight Invoice','Freight Invoice')],'Invoice Type'),            
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
        datas['model'] = 'tds.form.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tds_form_report', 'datas': datas}
        
tds_form_report()

