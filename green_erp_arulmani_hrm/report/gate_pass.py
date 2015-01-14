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
            'get_date': self.get_date,
            'get_shift': self.get_shift,
            'float_to_time': self.float_to_time,
        })
        
    def get_date(self, date=False):
        if not date:
            date = time.strftime(DATE_FORMAT)
        date = datetime.strptime(date, DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_shift(self,obj):
        shift = ''
        month = int(obj.date[5:7])
        month_char = str(month)
        year = int(obj.date[0:4])
        day = int(obj.date[8:10])
        dep = obj.employee_id.department_id and obj.employee_id.department_id.id or False
        sec = obj.employee_id.section_id and obj.employee_id.section_id.id or False
        if dep and sec:
            work_ids = self.pool.get('arul.hr.monthly.work.schedule').search(self.cr, self.uid, [('department_id','=',dep),('section_id','=',sec),('year','=',year),('month','=',month_char)])
            if work_ids:
                shift_ids = self.pool.get('arul.hr.monthly.shift.schedule').search(self.cr, self.uid, [('monthly_work_id','=',work_ids[0]),('employee_id','=',obj.employee_id.id)])
                if shift_ids:
                    for line in self.pool.get('arul.hr.monthly.shift.schedule').browse(self.cr, self.uid, shift_ids):
                        if day == 1 :
                            shift = line.day_1 and line.day_1.name or ''
                        if day == 2 :
                            shift = line.day_2 and line.day_2.name or ''
                        if day == 3 :
                            shift = line.day_3 and line.day_3.name or ''
                        if day == 4 :
                            shift = line.day_4 and line.day_4.name or ''
                        if day == 5 :
                            shift = line.day_5 and line.day_5.name or ''
                        if day == 6 :
                            shift = line.day_6 and line.day_6.name or ''
                        if day == 7 :
                            shift = line.day_7 and line.day_7.name or ''
                        if day == 8 :
                            shift = line.day_8 and line.day_8.name or ''
                        if day == 9 :
                            shift = line.day_9 and line.day_9.name or ''
                        if day == 10 :
                            shift = line.day_10 and line.day_10.name or ''
                        if day == 11 :
                            shift = line.day_11 and line.day_11.name or ''
                        if day == 12 :
                            shift = line.day_12 and line.day_12.name or ''
                        if day == 13 :
                            shift = line.day_13 and line.day_13.name or ''
                        if day == 14 :
                            shift = line.day_14 and line.day_14.name or ''
                        if day == 15 :
                            shift = line.day_15 and line.day_15.name or ''
                        if day == 16 :
                            shift = line.day_16 and line.day_16.name or ''
                        if day == 17 :
                            shift = line.day_17 and line.day_17.name or ''
                        if day == 18 :
                            shift = line.day_18 and line.day_18.name or ''
                        if day == 19 :
                            shift = line.day_19 and line.day_19.name or ''
                        if day == 20 :
                            shift = line.day_20 and line.day_20.name or ''
                        if day == 21 :
                            shift = line.day_21 and line.day_21.name or ''
                        if day == 22 :
                            shift = line.day_22 and line.day_22.name or ''
                        if day == 23 :
                            shift = line.day_23 and line.day_23.name or ''
                        if day == 24 :
                            shift = line.day_24 and line.day_24.name or ''
                        if day == 25 :
                            shift = line.day_25 and line.day_25.name or ''
                        if day == 26 :
                            shift = line.day_26 and line.day_26.name or ''
                        if day == 27 :
                            shift = line.day_27 and line.day_27.name or ''
                        if day == 28 :
                            shift = line.day_28 and line.day_28.name or ''
                        if day == 29 :
                            shift = line.day_29 and line.day_29.name or ''
                        if day == 30 :
                            shift = line.day_30 and line.day_30.name or ''
                        if day == 31 :
                            shift = line.day_31 and line.day_31.name or ''
        return shift
    
    def float_to_time(self,time_f):
        if not time_f:
            return ''
        return time.strftime('%H:%M', time.gmtime(time_f*3600))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

