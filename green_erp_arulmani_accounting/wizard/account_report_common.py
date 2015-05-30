# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class tpt_account_balance_report(osv.osv_memory):
    _name = "tpt.account.balance.report"
    
    _columns = {    
        'balance_report_line':fields.one2many('tpt.account.balance.report.line','batch_wise_id','Balance Report Line'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'account_id':fields.many2one('account.account','Chart of Account'),
        'fiscal_id':fields.many2one('account.fiscalyear','Fiscal Year'),
        'display_account': fields.selection([('all','All'), ('movement','With movements'),
                                            ('not_zero','With balance is not equal to 0'),
                                            ],'Display Accounts'),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves'),
    }
    
#     def print_xls(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'tpt.batch.wise.stock'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'batch_wise_stock_report', 'datas': datas}
    
#     def print_pdf(self, cr, uid, ids, context=None):
#         if context is None:
#             context = {}
#         datas = {'ids': context.get('active_ids', [])}
#         datas['model'] = 'tpt.batch.wise.stock'
#         datas['form'] = self.read(cr, uid, ids)[0]
#         datas['form'].update({'active_id':context.get('active_ids',False)})
#         return {'type': 'ir.actions.report.xml', 'report_name': 'batch_wise_stock_report_pdf', 'datas': datas}
    
tpt_batch_wise_stock()

class tpt_account_balance_report_line(osv.osv_memory):
    _name = "tpt.account.balance.report.line"
    
    _columns = {    
        'batch_wise_id':fields.many2one('tpt.batch.wise.stock','Batch Wise',ondelete='cascade'),
        'col_1': fields.char('',size=1024),
        'col_2': fields.char('',size=1024),
        'col_3': fields.char('',size=1024),
        'col_4': fields.char('',size=1024),
    }
    
tpt_account_balance_report_line()

class account_balance_report(osv.osv_memory):
    _inherit = "account.balance.report"
    
    _columns = {
        'filter': fields.selection([('filter_date', 'Date')], "Filter by", required=True),
    }
    
    def print_aeroo_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.common.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'trial_balance_report', 'datas': datas}
    
    
account_balance_report()