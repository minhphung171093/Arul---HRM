import hashlib
import itertools
import logging
import os
import re
import time

from openerp import tools
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class direct_work(osv.osv):
    _name = 'direct.work'
    _order = "create_date desc"
    _columns = {
        'name': fields.char('Work No.', size=16, readonly=True),
        'complaint_number': fields.many2one('complaint.register', 'Complaint No'),
        'complaint_date': fields.date('Complaint Date', readonly=True),
        'department_id': fields.many2one('hr.department', 'Department', readonly=True),
        'section_id': fields.many2one('arul.hr.section', 'Section', readonly=True),
        'work_date': fields.date('Work Date'),
        'action_against': fields.selection([('employee', 'Employee'), ('others', 'Others')],'Action Against'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'user_id': fields.many2one('res.users', 'Raised By', readonly=True),
        'action_taken': fields.text('Action Taken'),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
                                   ('approved', 'Approved')], 'Status', readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'user_id': lambda self, cr, uid, c: uid,
        'name': '/',
    }

    def confirm_work(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'})
        self.update_complaint_state(cr, uid, ids, 'dw_created', context=None)
        return True

    def approve_work(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})
        self.update_complaint_state(cr, uid, ids, 'closed', context=None)
        return True

    def set_dw_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        self.update_complaint_state(cr, uid, ids, 'hod_approved', context=None)
        return True

    def update_complaint_state(self, cr, uid, ids, updated_state, context=None):
        dw_obj_id = self.browse(cr, uid, ids[0])
        if dw_obj_id.complaint_number:
            req_obj = self.pool.get('complaint.register')
            complaint_id = req_obj.browse(cr, uid, dw_obj_id.complaint_number.id)
            complaint_id.write({'state': updated_state})
        return True

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'safety.direct.work.number') or '/'
        if vals.get('complaint_number',False):
            req_obj = self.pool.get('complaint.register')
            data = req_obj.browse(cr, uid, vals.get('complaint_number',False))
            vals['complaint_date'] = data.complaint_date or False
            vals['department_id'] = data.department_id and data.department_id.id or False
            vals['section_id'] = data.section_id and data.section_id.id or False
        new_id = super(direct_work, self).create(cr, uid, vals, context)
        return new_id

    def write(self, cr, uid, ids, vals, context=None):
        if 'complaint_number' in vals:
            if vals['complaint_number']:
                req_obj = self.pool.get('complaint.register')
                data = req_obj.browse(cr, uid, vals['complaint_number'])
                vals['complaint_date'] = data.complaint_date or False
                vals['department_id'] = data.department_id and data.department_id.id or False
                vals['section_id'] = data.section_id and data.section_id.id or False
        return super(direct_work, self).write(cr, uid, ids, vals, context)

    def on_change_complaint_number(self, cr, uid, ids, complaint_number, context=None):
        result = {'value': {}}
        req_obj = self.pool.get('complaint.register')
        data = req_obj.browse(cr, uid, complaint_number)

        result['value']['complaint_date'] = data.complaint_date or False
        result['value']['department_id'] = data.department_id and data.department_id.id or False
        result['value']['section_id'] = data.section_id and data.section_id.id or False

        return result

direct_work()