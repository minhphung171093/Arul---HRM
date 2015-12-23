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
            'get_date_from':self.get_date_from,
            'convert_date': self.convert_date,
            'get_customer': self.get_customer,
            'get_customer_group': self.get_customer_group,
            #'get_balance': self.get_balance,
            
        
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    def get_customer_group(self):
    	customer_group = ''
        wizard_data = self.localcontext['data']['form']
        customer_group = wizard_data['customer_group'] 
        if customer_group == 'export':
        	customer_group = 'Export'
        if customer_group == 'domestic':
        	customer_group = 'Domestic'
        if customer_group == 'indirect_export':
        	customer_group = 'Indirect Export'
        return  customer_group
    def get_customer(self):
        wizard_data = self.localcontext['data']['form']
        customer_group = wizard_data['customer_group']
        customer_id = wizard_data['customer_id']
        date = wizard_data['date_from']
        bp_obj = self.pool.get('res.partner')
        if customer_id:
            bp_ids = bp_obj.search(self.cr, self.uid, [('id','=',customer_id[0])                                                   
                                        ])
        if customer_group:
            bp_ids = bp_obj.search(self.cr, self.uid, [('customer','=',True),
                                                   ('customer_account_group_id','=','VVTI Sold to Party'),
                                                   ('arulmani_type','=',customer_group)
                                        ])
        if not customer_id and not customer_group:
            bp_ids = bp_obj.search(self.cr, self.uid, [('customer','=',True),
                                                   ('customer_account_group_id','=','VVTI Sold to Party')                   
                                        ])
        res = []
        for line in bp_obj.browse(self.cr, self.uid, bp_ids):
            res.append({ 
                'code': line['customer_code'] or '',
                'name': line['name'] or '',  
                'balance': self.get_balance(line['customer_code'], date) or 0.00,
            })
        return res
    
    def get_balance (self, code, date):
    	credit = 0
        sql  = '''
                select case when SUM(debit-credit)=0 then 0 else SUM(debit-credit) end credit from account_move_line where 
                account_id=(select id from account_account where code = '0000'||'%s') and date <= '%s'
            '''%(code, date)
        self.cr.execute(sql)
        credit = self.cr.fetchone()
        if credit:
           credit = credit[0]            
        return credit  
     
           
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

