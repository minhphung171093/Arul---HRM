# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
from xlwt import Row
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_lines': self.get_lines,
        })
    
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        journal = wizard_data['journal_id']
        account = wizard_data['account_id']
        sql = '''
            select am.date as date, am.ref as doc_no, aa.code as acc_code, aa.name as acc_name, am.narration as narration,
                coalesce(aml.debit, 0) as debit, coalesce(aml.credit, 0) as credit,
                coalesce(aml.debit, 0) + coalesce(aml.credit, 0) as total, coalesce(ai.name, ai.vvt_number) as invoice_no,
                ai.date_invoice as invoice_date, po.name as po_no, po.date_order as po_date
            
                from account_move_line aml
                left join account_move am on aml.move_id=am.id
                left join account_account aa on aml.account_id=aa.id
                left join account_invoice ai on ai.move_id=am.id
                left join purchase_order po on ai.purchase_id=po.id
                
                where am.date between '%s' and '%s'
                
        '''%(date_from, date_to)
        if journal:
            sql += '''
                and am.journal_id=%s
            '''%(journal[0])
        if account:
            sql += '''
                and aml.account_id=%s
            '''%(account[0])
        sql += '''
            order by am.date
        '''
        self.cr.execute(sql)
        return self.cr.dictfetchall()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

