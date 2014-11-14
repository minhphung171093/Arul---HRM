# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

class arul_hr_holiday_special(osv.osv):
    _name = "arul.hr.holiday.special"
    _columns = {
        'name' : fields.char('Holiday Name', size = 1024),
        'date' : fields.date('Date'),
    }
arul_hr_holiday_special()

class arul_hr_leave_master(osv.osv):
    _name = "arul.hr.leave.master"
    _columns = {
        'leave_type_id' : fields.many2one('arul.hr.leave.types', 'Leave Type'),
        'employee_category_id' : fields.many2one('vsis.hr.employee.category', 'Employee Category'),
        'employee_sub_category_id' : fields.many2one('hr.employee.sub.category', 'Employee Sub Category'),
        'maximum_limit': fields.integer('Maximum Limit Applicable'),
        'carryforward_nextyear': fields.boolean('Is Carry Forward for Next Year'),
        'condition': fields.selection([('yes', 'Yes'),('no', 'No')], 'Eligible per Annum'),
    }
arul_hr_leave_master()

