# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class alert_warning_form(osv.osv_memory):
    _name = "alert.warning.form"
    _columns = {    
                'name': fields.char(string="Title", size=100, readonly=True),
                }

    
alert_warning_form()