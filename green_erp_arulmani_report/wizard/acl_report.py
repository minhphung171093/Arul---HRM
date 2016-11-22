# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
import locale
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
DATE_FORMAT = "%Y-%m-%d"

class tpt_acl(osv.osv_memory):
    _name = "tpt.acl"
    _columns = {
        'tpt_group_ids': fields.many2many('res.groups', 'groups_acl_ref', 'group_id', 'acl_id', 'Groups'),
        'tpt_model_ids': fields.many2many('ir.model', 'model_acl_ref', 'model_id', 'acl_id', 'Models'),
    }
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': ids}
        datas['model'] = 'tpt.acl'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':ids[0]})
        return {'type': 'ir.actions.report.xml', 'report_name': 'acl_report', 'datas': datas}

tpt_acl()
