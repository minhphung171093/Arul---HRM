# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class journal_book_wizard(osv.osv_memory):
    _name = "journal.book.wizard"
    
    _columns = {
        'date_from': fields.date('From Date'),
        'date_to': fields.date('To Date'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'account_id': fields.many2one('account.journal', 'GL Acc'),
    }
    
    _defaults = {
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'journal.book.wizard'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0], 'active_ids':ids})
        return {'type': 'ir.actions.report.xml', 'report_name': 'journal_book_report', 'datas': datas}
        
journal_book_wizard()
