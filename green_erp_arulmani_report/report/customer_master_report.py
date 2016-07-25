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
            'get_lines': self.get_lines,
            'get_cus_group': self.get_cus_group,
        })
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        customer_account_group = wizard_data['customer_account_group_id']
        sql = '''
            select rp.id as id
            
            from 
                res_partner rp
                left join customer_account_group cag on rp.customer_account_group_id=cag.id
            where rp.is_company=True and rp.customer=True
        '''
        if customer_account_group:
            sql += '''
                and rp.customer_account_group_id=%s
            '''%(customer_account_group[0])
        self.cr.execute(sql)
        partner_ids = [r[0] for r in self.cr.fetchall()]
        return self.pool.get('res.partner').browse(self.cr, self.uid, partner_ids)
    
    def get_cus_group(self, group):
        if group=='export':
            return 'Export'
        if group=='domestic':
            return 'Domestic'
        if group=='indirect_export':
            return 'Indirect Export'
        return ''
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

