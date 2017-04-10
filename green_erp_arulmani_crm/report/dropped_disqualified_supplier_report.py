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
from report import report_sxw
import pooler
from osv import osv
from tools.translate import _
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml.html.builder import INS
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'convert_date': self.convert_date,
            'get_lines': self.get_lines,
        })
        
    def convert_date(self,date):
        if date:
            new_date = datetime.strptime(date, DATE_FORMAT)
            return new_date.strftime('%d/%m/%Y')
        return ''
    
    def get_lines(self):
        wizard_data = self.localcontext['data']['form']
        partner_id = wizard_data['partner_id']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        sql = '''
            select id, name, date_of_action, remarks
            
                from res_partner
                where date_of_action between '%s' and '%s' 
        '''%(date_from,date_to)
        if partner_id:
            sql += '''
                and id=%s
            '''%(partner_id[0])
        self.cr.execute(sql)
        res=[]
        for line in self.cr.dictfetchall():
            sql = '''
                select pt.name
                    from purchase_order_line pol
                    left join purchase_order po on pol.order_id=po.id
                    left join product_product pp on pol.product_id=pp.id
                    left join product_template pt on pp.product_tmpl_id=pt.id
                    
                    where po.partner_id=%s and po.state not in ('draft','cancel')
                    order by po.date_order desc, pol.id desc
                    limit 1
            '''%(line['id'])
            self.cr.execute(sql)
            product_name = self.cr.fetchone()
            res.append({
                'name': line['name'],
                'date_of_action': line['date_of_action'],
                'remarks': line['remarks'],
                'product_name': product_name and product_name[0] or '',
            })
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

