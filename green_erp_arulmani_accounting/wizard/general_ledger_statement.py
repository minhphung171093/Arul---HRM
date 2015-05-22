# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class general_ledger_statement(osv.osv_memory):
    _name = "general.ledger.statement"
    _columns = {    
                'date_from': fields.date('Posting ate From', required=True),
                'date_to': fields.date('To', required=True),
                'account_id':fields.many2one('account.account','GL Account',required=True),
                'doc_type': fields.selection([('cus_inv', 'Customer Invoice'),('cus_pay', 'Customer Payment'),
                                  ('sup_inv_po', 'Supplier Invoice(With PO)'),('sup_inv', 'Supplier Invoice(Without PO)'),('sup_pay', 'Supplier Payment'),
                                  ('payroll', 'Executives Payroll'),
                                  ('grn', 'GRN'),
                                  ('good', 'Good Issue'),
                                  ('do', 'DO'),
                                  ('inventory', 'Inventory Transfer'),
                                  ('manual', 'Manual Journal'),
                                  ('cash_pay', 'Cash Payment'),
                                  ('cash_rec', 'Cash Receipt'),
                                  ('bank_pay', 'Bank Payment'),
                                  ('bank_rec', 'Bank Receipt'),
                                  ('ser_inv', 'Service Invoice'),
                                  ('product', 'Production'),
                                  ('staff_payroll', 'Staff Payroll'),
                                  ('worker_payroll', 'Workers Payroll')],'Document Type'),   
#                 'doc_type':fields.selection([('cas_pay','Cash Payment'), ('cas_rec','Cash Receipts'), 
#                                             ('bak_pay','Bank Payments'), ('bak_rec','Bank Receipts'), 
#                                             ('sup_pay','Supplier Payments'),('cus_pay', 'Customer Payments'), 
#                                             ('cus_inv','Customer Invoice'),('deliver','DO'), 
#                                             ('sup_inv','Supplier Invoice'),('grn','GRN'), 
#                                             ('issue','Material Issue'), ('pro','Production'), 
#                                             ('pay','Payroll'),('jour','Journal Vouchers' )],'Document Type'),
                'doc_no':fields.char('Document No',size=1024),
                'narration':fields.char('Narration',size=1024),
                
                
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
    
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.ledger.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_ledger_statement_report_pdf', 'datas': datas}
        
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'general.ledger.statement'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'general_ledger_statement_report_xls', 'datas': datas}
general_ledger_statement()