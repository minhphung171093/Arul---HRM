# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
from datetime import date
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc

from array import array
import xmlrpclib

class notification_manual(osv.osv):
    _inherit = 'tpt.notification'

    _columns = {
        'complaint_number': fields.many2one('complaint.register', 'Complaint No'),
        'notif_type':fields.selection([
                                ('prevent','Preventive Maintenance'),
                                ('break','Breakdown'),
                                ('safety', 'Safety')],'Notification Type',required = False,readonly = True,states={'draft': [('readonly', False)]}),
        'equip_id': fields.many2one('tpt.equipment', 'Equipment', required=False, readonly=True,
                                    states={'draft': [('readonly', False)]}),
        'machine_id': fields.many2one('tpt.machineries', 'Sub Equipment', required=False, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department', required=False, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'section_id': fields.many2one('arul.hr.section', 'Section', required=False, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'issue_date': fields.date('Notification Date', required=False, readonly=True,
                                  states={'draft': [('readonly', False)]}),
        'issue_type': fields.selection([('major', 'Major'), ('minor', 'Minor'), ('critical', 'Critical')], 'Complexity',
                                       required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'priority': fields.selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], 'Priority',
                                     required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'issue_reported': fields.text('Issue Reported', required=False, readonly=True,
                                      states={'draft': [('readonly', False)]}),
    }

    _defaults = {
        'priority': 'medium',

    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('complaint_number', False):
            req_obj = self.pool.get('complaint.register')
            complaint_id = req_obj.browse(cr, uid, vals.get('complaint_number', False))
            complaint_id.write({'state': 'notif_created'})

        return super(notification_manual, self).create(cr, uid, vals, context)

    def on_change_complaint_number(self, cr, uid, ids, complaint_number, context=None):
        result = {'value': {}}
        req_obj = self.pool.get('complaint.register')
        data = req_obj.browse(cr, uid, complaint_number)

        # result['value']['issue_type'] = data.issue_severity or False
        # result['value']['department_id'] = data.department_id.id or False
        # result['value']['section_id'] = data.section_id.id or False
        result['value'] = {
            'issue_type': data.issue_severity or False,
            'department_id':data.department_id and data.department_id.id or False,
            'section_id':data.section_id and data.section_id.id or False,
        }
        return result


notification_manual()