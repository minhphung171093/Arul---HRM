# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_cash_book(osv.osv_memory):
    _name = "tpt.cash.book"
    _columns = {
        'name': fields.char('SI.No', readonly=True),
        'cb_line': fields.one2many('tpt.cash.book.line', 'cb_id', 'Cash Book Line'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type')
    }
    
    def print_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.cash.book'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_cash_book_xls', 'datas': datas}
    
    def print_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'tpt.cash.book'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'report_cash_book', 'datas': datas}
    
tpt_cash_book()

class tpt_cash_book_line(osv.osv_memory):
    _name = "tpt.cash.book.line"
    _columns = {
        'cb_id': fields.many2one('tpt.cash.book', 'Cash Book', ondelete='cascade'),
        'voucher_id': fields.many2one('account.voucher', 'Voucher No.'),
        'opening_balance': fields.char(''),
        'debit': fields.float('Debit (Rs.)'),
    }

tpt_cash_book_line()

class cash_book_report(osv.osv_memory):
    _name = "cash.book.report"
    _columns = {    
                'date_from': fields.date('Date From', required=True),
                'date_to': fields.date('Date To', required=True),
                'type_trans':fields.selection([('payment', 'Payment'),('receipt', 'Receipt')],'Transaction type')
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
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'cash.book.report'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'report_cash_book', 'datas': datas}
        cr.execute('delete from tpt_cash_book')
        cb_obj = self.pool.get('tpt.cash.book')
        line = self.browse(cr, uid, ids[0])
        cb_line = []
        cb_line.append((0,0,{
            'voucher_id': False,
            'opening_balance': 'Opening Balance:',
            'debit': 1234,
        }))
        cb_line.append((0,0,{
            'voucher_id': False,
            'opening_balance': False,
            'debit': 123,
        }))
        vals = {
            'name': 'Cash Book for the Period: ',
            'cb_line': cb_line,
            'date_from': line.date_from,
            'date_to': line.date_to,
            'type_trans': line.type_trans,
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_accounting', 'view_tpt_cash_book_form')
        return {
                    'name': 'Cash Book Report',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tpt.cash.book',
                    'domain': [],
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': cb_id,
                }
        
cash_book_report()