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
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.user_obj = pooler.get_pool(self.cr.dbname).get('res.users')
        self.cr = cr
        self.uid = uid
        self.localcontext.update({
            'get_sale_order':self.get_sale_order, 
            'length_month':self.length_month,
            'get_month_name':self.get_month_name,   
        })
    def get_sale_order(self,quotation_id):
        sale_order_obj = self.pool.get('sale.order')
        sale_order_ids = sale_order_obj.search(self.cr, self.uid, [('id','=',quotation_id)])
        if sale_order_ids:
            return sale_order_obj.browse(self.cr, self.uid, sale_order_ids[0])
        else:
            return False            
    def length_month(self,year, month):
        if month == 2 and (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
            return 29 
        return [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month]
    def get_month_name(self, month):
        _months = {1:_("January"), 2:_("February"), 3:_("March"), 4:_("April"), 5:_("May"), 6:_("June"), 7:_("July"), 8:_("August"), 9:_("September"), 10:_("October"), 11:_("November"), 12:_("December")}
        d = _months[month]
        print d,month
        return d
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
