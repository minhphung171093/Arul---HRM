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
            
            'get_qc_date': self.get_qc_date,
        })
    def get_qc_date(self,lead_id):
        result = []
        sql = ''' 
                select date(qc.create_date) as qc_date
                from crm_specification cs
                left join crm_qc_test qc on qc.name = cs.id
                where cs.lead_id = %s
              '''%(lead_id)
        self.cr.execute(sql)
        for line in self.cr.dictfetchall():
            print line,datetime.strptime(line['qc_date'], DATE_FORMAT).strftime('%d-%m-%Y')
            dic = {
                   'qc_date': datetime.strptime(line['qc_date'], DATE_FORMAT).strftime('%d-%m-%Y'),
            }
            result.append(dic)
        return result
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

