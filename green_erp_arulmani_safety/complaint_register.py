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


class complaint_register(osv.osv):
    _name = 'complaint.register'
    _order = "create_date desc"
    _columns = {
        'name': fields.char('Compliance No.', size=16, readonly=True),
        'complaint_date': fields.date('Compliance Date'),
        'complaint_type': fields.selection([('condition', 'Unsafe Condition'), ('act', 'Unsafe Act')],'Compliance Type'),
        'issue_severity': fields.selection([('major', 'Major'), ('minor', 'Minor'), ('critical', 'Critical')], 'Issue Severity'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'section_id': fields.many2one('arul.hr.section', 'Section'),
        'user_id': fields.many2one('res.users', 'Raised By', readonly=True),
        'issue_reported': fields.text('Issue Reported'),
        'hod_reject_reason': fields.text(string="Reason For Rejection"),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), 
                                   ('sm_approved', 'SM Approved'), ('sm_rejected', 'SM Rejected'),
                                   ('hod_approved', 'SM & HOD Approved'), ('hod_rejected', 'HOD Rejected'),
                                   ('notif_created', 'Notification created'), ('dw_created', 'Direct Work Created'),
                                   ('closed', 'Closed')],'Status', readonly=True),
        'tpt_location': fields.text('Location'),
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True),
    }

    _defaults = {
        'state': 'draft',
        'user_id': lambda self, cr, uid, c: uid,
        'name': '/',
        'issue_severity':'critical',
    }

    def confirm_complaint(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'confirmed'})

    def cancel_complaint(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'})

    def set_complaint_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})

    def create(self, cr, uid, vals, context=None):
        sql = '''
                        select code from account_fiscalyear where '%s' between date_start and date_stop
                    ''' % (time.strftime('%Y-%m-%d'))
        cr.execute(sql)
        fiscalyear = cr.dictfetchone()
        if not fiscalyear:
            raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
        if vals.get('name', '/') == '/':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'safety.complaint.number') or '/'
            vals['name'] = sequence and sequence + '/' + fiscalyear['code'] or '/'
        new_id = super(complaint_register, self).create(cr, uid, vals, context)
        return new_id

    def onchange_department_id(self, cr, uid, ids,department_id=False,):
        value = {}
        if department_id:
            value['section_id']= False
            return {'value': value}
        
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            if line.state == 'confirmed':
                self.write(cr, uid, ids,{'state':'sm_approved'})
        return True
    
    def bt_reject(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids):
            if line.state == 'confirmed':
                self.write(cr, uid, ids,{'state':'sm_rejected'})
        return True
    
    def bt_hod_approve(self, cr, uid, ids,notif, context=None):
        sql = '''
            select %s in (select uid from res_groups_users_rel where gid in (select id from res_groups where name='Dept HOD Approval' 
            and category_id in (select id from ir_module_category where name='VVTI - Safety')))
                    '''%(uid)
        cr.execute(sql)
        hod = cr.fetchone()
        if hod[0]:
            for line in self.browse(cr,uid,ids):
                if line.state == 'sm_approved':
                    self.write(cr, uid, line.id,{'state':'hod_approved'})   
                if notif:
                    self.pool.get('tpt.notification').create(cr,uid,{ 
                                                                     'complaint_number': line.id,
                                                                     'notif_type': 'safety',
                                                                    'issue_type': line.issue_severity or False,
                                                                    'priority': 'medium',
                                                                     'state': 'draft',
                                                                    'department_id': line.department_id and line.department_id.id or False,
                                                                    'section_id': line.section_id and line.section_id.id or False,
                                                                    'issue_reported': line.issue_reported or False,
                                                                     })
                    self.write(cr, uid, ids,{'state':'notif_created'})
        else:
            raise osv.except_osv(_('Warning!'),_('User does not have permission to approve!'))
        return True
    
    def bt_hod_reject(self, cr, uid, ids, hod_reject_reason, context=None):
        sql = '''
            select %s in (select uid from res_groups_users_rel where gid in (select id from res_groups where name='Dept HOD Approval' 
            and category_id in (select id from ir_module_category where name='VVTI - Safety')))
                    '''%(uid)
        cr.execute(sql)
        hod = cr.fetchone()
        if hod[0]:
            for line in self.browse(cr,uid,ids):
                if line.state == 'sm_approved':
                    self.write(cr, uid, ids,{'state':'hod_rejected','hod_reject_reason':hod_reject_reason})
        else:
            raise osv.except_osv(_('Warning!'),_('User does not have permission to approve!'))
        return True

complaint_register()


