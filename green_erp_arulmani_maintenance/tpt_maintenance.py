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

class tpt_equip_category(osv.osv):
    _name = "tpt.equip.category"
    _columns = {
        'name':fields.char('Name', size = 1024,required=True),
        'code':fields.char('Code', size = 1024,required=True),
    }
    def _check_name_code(self, cr, uid, ids, context=None):
        for equip_cat in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_equip_category where id != %s and lower(name) = lower('%s')
            '''%(equip_cat.id,equip_cat.name)
            cr.execute(sql)
            equip_name_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select id from tpt_equip_category where id != %s and lower(code) = lower('%s')
            '''%(equip_cat.id,equip_cat.code)
            cr.execute(sql)
            equip_code_ids = [row[0] for row in cr.fetchall()]
            if equip_code_ids or equip_name_ids:  
                raise osv.except_osv(_('Warning!'),_('This code or name can not be duplicated!'))
        return True
    _constraints = [
        (_check_name_code, 'Identical Data', ['name','code']),
    ]
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(tpt_equip_category, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(tpt_equip_category, self).write(cr, uid,ids, vals, context)
tpt_equip_category()

class tpt_equipment(osv.osv):
    _name = "tpt.equipment"
    _columns = {
        'name':fields.char('Name', size = 1024,required=True),
        'code':fields.char('Code', size = 1024,required=True),
        'equip_cate_id': fields.many2one('tpt.equip.category', 'Equipment Category',required=True),
        'cost_id': fields.many2one('tpt.cost.center', 'Cost Center',required=True),
        'department_id': fields.many2one('hr.department', 'Department',required=True),
        'section_id': fields.many2one('arul.hr.section', 'Section',required=True),
        'start_date': fields.date('Installation Start Date',required=True),
        'end_date': fields.date('Installation End Date',required=True),
        'men_power_line':fields.one2many('tpt.men.power','equipment_id','Men Power Consumption'),
        'document_attach_line':fields.one2many('tpt.document.attach','equipment_id','Document Attachments'),
        'maintenance_oder_line':fields.one2many('tpt.maintenance.oder','equipment_id','Equipment Master History',readonly=True),
        'status':fields.selection([('active', 'Active'),('idle', 'Idle'),('scrap', 'Scrap')],'Status',required = True),
        'justification':fields.text('Justification'),
    }
    def _check_name_code(self, cr, uid, ids, context=None):
        for equip in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_equipment where id != %s and lower(name) = lower('%s')
            '''%(equip.id,equip.name)
            cr.execute(sql)
            equip_name_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select id from tpt_equipment where id != %s and lower(code) = lower('%s')
            '''%(equip.id,equip.code)
            cr.execute(sql)
            equip_code_ids = [row[0] for row in cr.fetchall()]
            if equip_code_ids or equip_name_ids:  
                raise osv.except_osv(_('Warning!'),_('This code or name can not be duplicated!'))
        return True
    _constraints = [
        (_check_name_code, 'Identical Data', ['name','code']),
    ]
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(tpt_equipment, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(tpt_equipment, self).write(cr, uid,ids, vals, context)
    
    def onchange_department_id(self, cr, uid, ids,department_id=False):
        res = {'value':{'section_id':False}}
        if department_id:
            return res
tpt_equipment()

class tpt_men_power(osv.osv):
    _name = "tpt.men.power"
    _columns = {
        'equipment_id': fields.many2one('tpt.equipment', 'Equipment',ondelete='cascade'),
        'machineries_id': fields.many2one('tpt.machineries', 'Machineries',ondelete='cascade'),
        'employee_id': fields.many2one('hr.employee', 'Employee ID',required=True,ondelete='restrict'),
        'work_hour': fields.float('Working hours (Hrs)'),
    }
    
tpt_men_power()

class tpt_document_attach(osv.osv):
    _name = "tpt.document.attach"
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'hr_identities_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(tpt_document_attach, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_document_attach, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'equipment_id': fields.many2one('tpt.equipment', 'Equipment',ondelete='cascade'),
        'machineries_id': fields.many2one('tpt.machineries', 'Machineries',ondelete='cascade'),
        'description':fields.char('Attachment Description', size = 1024),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='File', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
    }
    
tpt_document_attach()

class tpt_machineries(osv.osv):
    _name = "tpt.machineries"
    _columns = {
        'name':fields.char('Sub Equipment Name', size = 1024,required=True),
        'code':fields.char('Sub Equipment Code', size = 1024,required=True),
        'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True),
        'cost_id': fields.many2one('tpt.cost.center', 'Cost Center',required=True),
#         'department_id': fields.many2one('hr.department', 'Department',required=True),
#         'section_id': fields.many2one('arul.hr.section', 'Section',required=True),
        'start_date': fields.date('Installation Start Date',required=True),
        'end_date': fields.date('Installation End Date',required=True),
        'men_power_line':fields.one2many('tpt.men.power','machineries_id','Men Power Consumption'),
        'document_attach_line':fields.one2many('tpt.document.attach','machineries_id','Document Attachments'),
        'department_id': fields.related('equip_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
        'section_id': fields.related('equip_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
    }
    def _check_name_code(self, cr, uid, ids, context=None):
        for equip in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from tpt_machineries where id != %s and lower(name) = lower('%s')
            '''%(equip.id,equip.name)
            cr.execute(sql)
            equip_name_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select id from tpt_machineries where id != %s and lower(code) = lower('%s')
            '''%(equip.id,equip.code)
            cr.execute(sql)
            equip_code_ids = [row[0] for row in cr.fetchall()]
            if equip_code_ids or equip_name_ids:  
                raise osv.except_osv(_('Warning!'),_('This code or name can not be duplicated!'))
        return True
    _constraints = [
        (_check_name_code, 'Identical Data', ['name','code']),
    ]
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(tpt_machineries, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(tpt_machineries, self).write(cr, uid,ids, vals, context)
    
    def onchange_equip_id(self, cr, uid, ids,equip_id=False):
        res = {'value':{
                        'department_id':False,
                        'section_id':False,
                      }
               }
        if equip_id:
            no_id = self.pool.get('tpt.equipment').browse(cr,uid,equip_id)
            res['value'].update({
                        'department_id':no_id.department_id and no_id.department_id.id or False,
                        'section_id':no_id.section_id and no_id.section_id.id or False,
            })
        return res
tpt_machineries()

class tpt_notification(osv.osv):
    _name = "tpt.notification"
    _columns = {
        'name':fields.char('Notification No', size = 1024,readonly=True),
        'notif_type':fields.selection([
                                ('prevent','Preventive Maintenance'),
                                ('break','Breakdown')],'Notification Type',required = True,readonly = True,states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department',required=True,readonly = True,states={'draft': [('readonly', False)]}),
        'section_id': fields.many2one('arul.hr.section', 'Section',required=True,readonly = True,states={'draft': [('readonly', False)]}),
#         'department_id': fields.related('equip_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
#         'section_id': fields.related('equip_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
        'equip_id': fields.many2one('tpt.equipment', 'Equipment',required = True,readonly = True,states={'draft': [('readonly', False)]}),
        'machine_id': fields.many2one('tpt.machineries', 'Sub Equipment',required = True,readonly = True,states={'draft': [('readonly', False)]}),
        'issue_date': fields.date('Notification Date',required=True,readonly = True,states={'draft': [('readonly', False)]}),
        'issue_type':fields.selection([('major', 'Major'),('minor', 'Minor'),('critical', 'Critical')],'Complexity',required = True,readonly = True,states={'draft': [('readonly', False)]}),
        'priority':fields.selection([('high', 'High'),('medium', 'Medium'),('low', 'Low')],'Priority',required = True,readonly = True,states={'draft': [('readonly', False)]}),
        'issue_reported':fields.text('Issue Reported',required = True,readonly = True,states={'draft': [('readonly', False)]}),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'create_date': fields.datetime('Created Date',readonly = True),
        'schedule_line':fields.one2many('tpt.schedule','notification_id','Schedule',readonly = True,states={'draft': [('readonly', False)]}),
        'state':fields.selection([('draft', 'Drafted'),('waiting', 'Waiting For Approval'),
                                  ('in', 'In Progress'),('close','Closed'),('cancel','Cancelled')],'Status', readonly=True),
    }
    _defaults = {
        'state':'draft',
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.notification.seq')
            vals['name'] =  sequence
        new_id = super(tpt_notification, self).create(cr, uid, vals, context=context)
        if vals.get('notif_type',False)=='break':
            sql = '''
                delete from tpt_schedule where notification_id = %s
            '''%(new_id)
            cr.execute(sql)    
        return new_id
    
    def onchange_notif_type(self, cr, uid, ids,notif_type=False, context=None):
        vals = {'value':{
                        'schedule_line':[],
                      }
                
                }
        for notif in self.browse(cr, uid, ids):
            if notif.notif_type == 'break' and notif_type:
                vals['schedule_line']=False
                sql = '''
                    delete from tpt_schedule where notification_id = %s
                '''%(notif.id)
                cr.execute(sql)
                return {'value': {
                        'schedule_line':False,
                      }}
        return True
    
    def onchange_department_id(self, cr, uid, ids,department_id=False):
        res = {'value':{'section_id':False}}
#         if department_id:
        return res
    
    def onchange_equip_id(self, cr, uid, ids,equip_id=False):
        res = {'value':{'machine_id':False,
#                         'department_id':False,
#                         'section_id':False,
                        }}
#         if equip_id:
#             no_id = self.pool.get('tpt.equipment').browse(cr,uid,equip_id)
#             res['value'].update({
#                         'department_id':no_id.department_id and no_id.department_id.id or False,
#                         'section_id':no_id.section_id and no_id.section_id.id or False,
#             })
        return res
        
    def bt_generate(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'waiting'})
    
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            sql = '''
                select %s in (select primary_auditor_id from hr_department
                where id =%s)
            '''%(uid,line.department_id.id)
            cr.execute(sql)
            notif = cr.fetchone()
            if not notif[0]:
                raise osv.except_osv(_('Warning!'),_('HOD of The Department can only approve!'))
        return self.write(cr, uid, ids,{'state':'in'})
    
    def bt_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'close'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        step = 0
        for line in self.browse(cr,uid,ids,context=context):
            maintenance_ids = self.pool.get('tpt.maintenance.oder').search(cr, uid,[('notification_id','=',line.id)])
            if maintenance_ids:
                for main in maintenance_ids:
                    main_id = self.pool.get('tpt.maintenance.oder').browse(cr,uid,main)
                    if main_id.state == 'close':
                        step = 1
                    else:
                        raise osv.except_osv(_('Warning!'),_('Can not cancel this notification!'))
            else:
                step = 1
            if line.state == 'in':
                sql = '''
                    select %s in (select primary_auditor_id from hr_department
                    where id =%s)
                '''%(uid,line.department_id.id)
                cr.execute(sql)
                notif = cr.fetchone()
                if not notif[0]:
                    raise osv.except_osv(_('Warning!'),_('Do not have permission to cancel this notification!'))
        return self.write(cr, uid, ids,{'state':'cancel'})
    
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_tpt_notification'):
#             sql = '''
#                 select id from tpt_notification
#                 where department_id in (select id from hr_department where primary_auditor_id =%s)
#             '''%(uid)
#             cr.execute(sql)
#             notification_ids = [row[0] for row in cr.fetchall()]
#             sql='''
#                 select %s in (select uid from res_groups_users_rel where gid in (select id from res_groups 
#                     where name in ('Purchase Store Mgr','Production GM','Production Admin')
#                     and category_id in (select id from ir_module_category where name='VVTI - PRODUCTION')))
#             '''%(uid)
#             cr.execute(sql)
#             notif = cr.fetchone()
#             if notif and notif[0] != False:
#                 sql = '''
#                 select id from tpt_notification
#                 '''
#                 cr.execute(sql)
#                 notif_ids = [row[0] for row in cr.fetchall()]
#                 for noti in notif_ids:
#                     notification_ids.append(noti)
#             args = [('id','in',notification_ids)]
#             
#         return super(tpt_notification, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
#     
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#        ids = self.search(cr, user, args, context=context, limit=limit)
#        return self.name_get(cr, user, ids, context=context)
tpt_notification()

class tpt_schedule(osv.osv):
    _name = "tpt.schedule"
    _columns = {
        'notification_id': fields.many2one('tpt.notification','Notification',ondelete='cascade'),
        'schedule_date': fields.date('schedule Date',required=True),
        'activities':fields.char('Activities', size = 1024),
        'employee_id': fields.many2one('hr.employee', 'Responsible Person',required=True,ondelete='restrict'),
    }
tpt_schedule()

class tpt_maintenance_oder(osv.osv):
    _name = "tpt.maintenance.oder"
    
    def check_approve_uid(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            depart_pri = line.department_id and line.department_id.primary_auditor_id and line.department_id.primary_auditor_id.id or False
            if uid == depart_pri:
                res[line.id] = True
            else:
                res[line.id] = False
            if uid == 1:
                res[line.id] = True
        return res
    
    def get_net_value(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        entry_obj = self.pool.get('tpt.service.entry')
        third_obj = self.pool.get('tpt.third.service.entry')
        mater_obj = self.pool.get('tpt.material.request')
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'net_value': 0.0,
            }
            net_value = 0.0
            
            entry_ids = entry_obj.search(cr, uid,[('maintenance_id','=',line.id)])
            for entry in entry_ids:
                entry_id = entry_obj.browse(cr,uid,entry)
                net_value += entry_id.grand_total or 0
                
            third_ids = third_obj.search(cr, uid,[('maintenance_id','=',line.id)])
            for third in third_ids:
                third_id = third_obj.browse(cr,uid,third)
                net_value += third_id.grand_total or 0
            
            mater_ids = mater_obj.search(cr, uid,[('maintenance_id','=',line.id)])
            for mater in mater_ids:
                mater_id = mater_obj.browse(cr,uid,mater)
                net_value += mater_id.total or 0
                
            chargeable_ids = mater_obj.search(cr, uid,[('chargeable_maintenance_id','=',line.id)])
            for chargeable in chargeable_ids:
                chargeable_id = mater_obj.browse(cr,uid,chargeable)
                net_value += chargeable_id.total or 0
            res[line.id]['net_value'] = net_value
        return res
    
    _columns = {
        'name':fields.char('Order No', size = 1024,readonly=True),
        'issue_type':fields.selection([('major', 'Major'),('minor', 'Minor'),('critical', 'Critical')],'Issue Type',states={'close': [('readonly', True)]}),
        'notification_id':fields.many2one('tpt.notification','Notification No',required = True,states={'close': [('readonly', True)]}),
        'create_date': fields.datetime('Created Date',readonly = True),
        'notif_type':fields.selection([
                                ('prevent','Preventive Maintenance'),
                                ('break','Breakdown')],'Notification Type',required = True,states={'close': [('readonly', True)]}),
        'department_id': fields.many2one('hr.department', 'Department',required=True,states={'close': [('readonly', True)]}),
        'section_id': fields.many2one('arul.hr.section', 'Section',required=True,states={'close': [('readonly', True)]}),
#         'department_id': fields.related('notification_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
#         'section_id': fields.related('notification_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
        'equip_id': fields.related('notification_id','equip_id',type='many2one', relation='tpt.equipment',string='Equipment', readonly = True),
        'machine_id': fields.related('notification_id','machine_id',type='many2one', relation='tpt.machineries',string='Sub Equipment', readonly = True),
        
        'employee_id': fields.many2one('hr.employee', 'Assigned to',required=True,states={'close': [('readonly', True)]},ondelete='restrict'),
        'priority':fields.selection([('high', 'High'),('medium', 'Medium'),('low', 'Low')],'Priority',states={'close': [('readonly', True)]}),
        'equipment_id': fields.many2one('tpt.equipment', 'Equipment'),
#         'machine_id': fields.many2one('tpt.machineries', 'Machineries',required=True,states={'close': [('readonly', True)]}),
        'start_date': fields.date('Work Start Date',required=True,states={'close': [('readonly', True)]}),
        'completion_date': fields.date('Target Date of Completion',required=True,states={'close': [('readonly', True)]}),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'issue_reported':fields.text('Issue Reported',states={'close': [('readonly', True)]}),
        'issue_finding':fields.text('Issue Finding',states={'close': [('readonly', True)]}),
        'service_entry_line':fields.one2many('tpt.service.entry','maintenance_id','Staff Service Entry',states={'close': [('readonly', True)]}),
        'third_service_line':fields.one2many('tpt.third.service.entry','maintenance_id','Third Party Service Entry',states={'close': [('readonly', True)]}),
        'consumption_line':fields.one2many('tpt.material.request','maintenance_id','Material Consumption',states={'close': [('readonly', True)]}),
        'chargeable_line':fields.one2many('tpt.material.request','chargeable_maintenance_id','Chargeable MRS',states={'close': [('readonly', True)]}),
        'check_approve': fields.function(check_approve_uid, string='Approve?', type='boolean'),
        'net_value': fields.function(get_net_value, multi='sums',string='Net Value',digits=(16,2)),
        'state':fields.selection([('draft', 'Drafted'),
                                  ('confirm', 'Confirmed'),
                                  ('in', 'In Progress'),
                                  ('completed', 'Completed'),
                                  ('put', 'Put On Hold'),
                                  ('close','Closed'),
                                  ('cancel','Cancelled')],'Status', readonly=True),
    }
    _defaults = {
        'state':'draft',
    }
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.maintenance.oder.seq')
            vals['name'] =  sequence
        new_id = super(tpt_maintenance_oder, self).create(cr, uid, vals, context=context)
        return new_id
    
    def onchange_notification_id(self, cr, uid, ids,notification_id=False):
        res = {'value':{
                        'department_id':False,
                        'section_id':False,
                        'equip_id':False,
                        'machine_id':False,
                        'issue_reported':False,
                        'issue_type':False,
                        'priority':False,
                        'notif_type':False,
                        'employee_id':False,
                        'equipment_id':False,
                      }
               }
        if notification_id:
            no_id = self.pool.get('tpt.notification').browse(cr,uid,notification_id)
            res['value'].update({
                        'department_id':no_id.department_id and no_id.department_id.id or False,
                        'section_id':no_id.section_id and no_id.section_id.id or False,
                        'equip_id':no_id.equip_id and no_id.equip_id.id or False,
                        'machine_id':no_id.machine_id and no_id.machine_id.id or False,
                        'issue_reported':no_id.issue_reported or False,
                        'issue_type':no_id.issue_type or False,
                        'priority':no_id.priority or False,
                        'notif_type':no_id.notif_type or False,
                        'equipment_id':no_id.equip_id and no_id.equip_id.id or False,
            })
        return res
    
    def onchange_department_id(self, cr, uid, ids,department_id=False,section_id=False,employee_id=False):
        res = {'value':{}}
        if department_id:
            if section_id:
                cr.execute('select id from arul_hr_section where department_id = %s and id = %s',(department_id,section_id,))
                section = cr.fetchall()
                if not section:
                    res['value'].update({'section_id':False})
            if employee_id:
                cr.execute('select id from hr_employee where department_id = %s and id = %s',(department_id,employee_id,))
                employee = cr.fetchall()
                if not employee:
                    res['value'].update({'employee_id':False})
        return res
    
    def onchange_start_date(self, cr, uid, ids, no_id=False,sys_date=False, context=None):
        vals = {}
        warning = {}
        if no_id:
            noti_id = self.pool.get('tpt.notification').browse(cr,uid,no_id)
            no_date = noti_id.create_date
            if sys_date and sys_date < no_date[:10]:
                vals = {'start_date':False}
                warning = {
                    'title': _('Warning!'),
                    'message': _('Do not accept back date before the notification date!')
                }
        return {'value':vals,'warning':warning}
    
    def onchange_completion_date(self, cr, uid, ids, no_id=False,sys_date=False, context=None):
        vals = {}
        warning = {}
        if no_id:
            noti_id = self.pool.get('tpt.notification').browse(cr,uid,no_id)
            no_date = noti_id.create_date
            if sys_date and sys_date < no_date[:10] :
                vals = {'completion_date':False}
                warning = {
                    'title': _('Warning!'),
                    'message': _('Do not accept back date before the notification date!')
                }
        return {'value':vals,'warning':warning}
    
    def bt_create_order(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'confirm'})
    
    def bt_approve_order(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'in'})
    
    def bt_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'close'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def bt_set_to(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'draft'})
    
    def bt_return_rq(self, cr, uid, ids, context=None):
        return True
    
    def bt_service_entry(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_maintenance', 'view_tpt_service_entry_form')
        order_id = self.pool.get('tpt.maintenance.oder').browse(cr,uid,ids[0])
        return {
                    'name': 'Staff Service Entry',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.service.entry',
                    'domain': [],
                    'context': {
                                'default_maintenance_id':order_id.id or False,
                                'default_service_type':'employee',
                                'default_section_id':order_id.section_id and order_id.section_id.id or False,
                                'default_department_id':order_id.department_id and order_id.department_id.id or False,
                                'default_equip_id':order_id.equip_id and order_id.equip_id.id or False,
                                'default_machine_id':order_id.machine_id and order_id.machine_id.id or False},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        
    def bt_third_service_entry(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_maintenance', 'view_tpt_third_service_entry_form')
        order_id = self.pool.get('tpt.maintenance.oder').browse(cr,uid,ids[0])
        return {
                    'name': 'Third Party Service Entry',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.third.service.entry',
                    'domain': [],
                    'context': {
                                'default_maintenance_id':order_id.id or False,
                                'default_section_id':order_id.section_id and order_id.section_id.id or False,
                                'default_department_id':order_id.department_id and order_id.department_id.id or False,
                                'default_equip_id':order_id.equip_id and order_id.equip_id.id or False,
                                'default_machine_id':order_id.machine_id and order_id.machine_id.id or False},
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
    
    def bt_create_mrs(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_maintenance', 'view_tpt_material_request_form_for_mainten')
        order_id = self.pool.get('tpt.maintenance.oder').browse(cr,uid,ids[0])
        return {
                    'name': 'Material Request',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.material.request',
                    'domain': [],
                    'context': {
                                'default_maintenance_id':order_id.id or False,
                                'default_section_id':order_id.section_id and order_id.section_id.id or False,
                                'default_department_id':order_id.department_id and order_id.department_id.id or False,
                                'default_mrs_type':'normal',
                                },
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        
    def bt_chargeable_mrs(self, cr, uid, ids, context=None):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                        'green_erp_arulmani_maintenance', 'view_tpt_material_request_form_for_mainten')
        order_id = self.pool.get('tpt.maintenance.oder').browse(cr,uid,ids[0])
        return {
                    'name': 'Material Request',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': res[1],
                    'res_model': 'tpt.material.request',
                    'domain': [],
                    'context': {
                                'default_chargeable_maintenance_id':order_id.id or False,
                                'default_section_id':order_id.section_id and order_id.section_id.id or False,
                                'default_department_id':order_id.department_id and order_id.department_id.id or False,
                                'default_mrs_type':'chargeable',
                                },
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
        
    
tpt_maintenance_oder()

class tpt_service_entry(osv.osv):
    _name = "tpt.service.entry"
    def amount_all_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'grand_total': 0.0,
            }
            grand_total = 0.0
            amount_line = 0.0 
            for service in line.service_entry_line:
                amount_line = service.product_uom_qty * service.price_unit
                grand_total += round(amount_line,2)
            res[line.id]['grand_total'] = grand_total
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.service.entry.line').browse(cr, uid, ids, context=context):
            result[line.service_entry_id.id] = True
        return result.keys()
    
    _columns = {
        'name':fields.char('Document No', size = 1024,readonly=True),
        'create_date': fields.datetime('Created on',readonly = True),
        'maintenance_id':fields.many2one('tpt.maintenance.oder','Maintenance Order No',readonly = True),
        'service_type':fields.selection([('internal','Third Party Internal'),('employee', 'Employee'),('external','Third Party External')],'Service Type'),
        'work_taken': fields.date('Work Taken on',required=True),
#         'department_id': fields.many2one('hr.department', 'Department',required=True),
#         'section_id': fields.many2one('arul.hr.section', 'Section',required=True),
#         'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True),
#         'machine_id': fields.many2one('tpt.machineries', 'Machineries',required=True),
        'department_id': fields.related('maintenance_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
        'section_id': fields.related('maintenance_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
        'equip_id': fields.related('maintenance_id','equip_id',type='many2one', relation='tpt.equipment',string='Equipment', readonly = True),
        'machine_id': fields.related('maintenance_id','machine_id',type='many2one', relation='tpt.machineries',string='Machineries', readonly = True),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'service_entry_line':fields.one2many('tpt.service.entry.line','service_entry_id','Service Entry Lines'),
        'grand_total': fields.function(amount_all_line, multi='sums',string='Grand Total',digits=(16,2),
                                         store={
                'tpt.service.entry': (lambda self, cr, uid, ids, c={}: ids, ['service_entry_line'], 10),
                'tpt.service.entry.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit'], 10),})
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.service.entry.seq')
            vals['name'] =  sequence
        new_id = super(tpt_service_entry, self).create(cr, uid, vals, context=context)
        return new_id
    
    def bt_service_invoice(self, cr, uid, ids, context=None):
        return True
    
    def bt_save(self, cr, uid, ids,vals,context=None):
#         service_obj = self.pool.get('tpt.maintenance.oder')
#         vals = {}
#         service = self.browse(cr, uid, ids[0])
#         vals.update({   'maintenance_id': context.get('default_maintenance_id', False),
#                         'section_id': context.get('default_section_id', False),
#                         'department_id': context.get('default_department_id', False),
#                         'equip_id': context.get('default_equip_id', False),
#                         'machine_id': context.get('default_machine_id', False),
#                         'service_type': service.service_type or False,
#                         'work_taken': service.work_taken or False,
#                         })
                     
#                         'default_department_id':order_id.department_id and order_id.department_id.id or False,
#                         'default_equip_id':order_id.equip_id and order_id.equip_id.id or False,
#                         'default_machine_id':order_id.machine_id and order_id.machine_id.id or False,})
#         return self.write(cr,uid,ids[0],vals,context)
        return True
    
tpt_service_entry()

class tpt_service_entry_line(osv.osv):
    _name = "tpt.service.entry.line"
    def line_net_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            line_net = 0.0
            res[line.id] = {
                    'line_net': 0.0,
                }  
            line_net = line.product_uom_qty * line.price_unit
            res[line.id]['line_net'] = round(line_net,2)
        return res
    _columns = {
        'service_entry_id': fields.many2one('tpt.service.entry','Service Entry',ondelete='cascade'),
        'line_no': fields.integer('S.No', readonly = True),
#         'po_id':fields.many2one('purchase.order','Purchase Order', ondelete = 'restrict'),
        'employee_ids':fields.many2many('hr.employee','service_entry_employee_ref','service_entry_id','employee_id','Employee'),
        'work_day': fields.date('Work Day',required=True),
        'parti':fields.char('Particulars', size = 1024),
        'po_line_id':fields.many2one('purchase.order.line','Particulars', ondelete = 'restrict'),
        'uom_id': fields.many2one('product.uom', 'UOM'),
        'product_uom_qty': fields.float('Quantity',digits=(16,3)),   
        'price_unit': fields.float('Unit Price',digits=(16,3)),
#         'price_unit': fields.related('po_line_id','price_unit',type='float', relation='purchase.order.line',string='Unit Price', readonly = True),
        'line_net': fields.function(line_net_line, multi='deltas' ,digits=(16,2),string='Line Net'),
        'work_hour': fields.float('Working hours (Hrs)'),
    }
    _defaults = {
        'price_unit':0.0,
        'product_uom_qty':1,
    }
    
#     def _check_qty_line(self, cr, uid, ids, context=None):
#         for line in self.browse(cr,uid,ids,context=context):
#             qty = line.product_uom_qty or 0
#             po_qty = line.po_line_id and line.po_line_id.product_qty or 0
#             if qty > po_qty:
#                 raise osv.except_osv(_('Warning!'),_('Quantity can not be greater than PO Quantity!'))
#         return True
#     _constraints = [
#         (_check_qty_line, 'Identical Data', ['product_uom_qty']),
#     ]
    
    def unlink(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            update_ids = self.search(cr, uid,[('service_entry_id','=',line.service_entry_id.id),('line_no','>',line.line_no)])
            if update_ids:
                cr.execute("UPDATE tpt_service_entry_line SET line_no=line_no-1 WHERE id in %s",(tuple(update_ids),))
        return super(tpt_service_entry_line, self).unlink(cr, uid, ids, context)  
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('service_entry_id',False):
            vals['line_no'] = len(self.search(cr, uid,[('service_entry_id', '=', vals['service_entry_id'])])) + 1
        return super(tpt_service_entry_line, self).create(cr, uid, vals, context)
    
#     def onchange_po_line_id(self, cr, uid, ids,po_line_id=False):
#         res = {'value':{
#                         'uom_id':False,
#                         'product_uom_qty':False,
#                         'price_unit':False,
#                       }
#                }
#         if po_line_id:
#             no_id = self.pool.get('purchase.order.line').browse(cr,uid,po_line_id)
#             res['value'].update({
#                         'uom_id':no_id.product_uom and no_id.product_uom.id or False,
#                         'product_uom_qty':no_id.product_qty or False,
#                         'price_unit':no_id.price_unit or False,
#             })
#         return res
    
#     def onchange_po_id(self, cr, uid, ids,po_id=False,po_line_id=False):
#         res = {'value':{}}
#         if po_id and po_line_id:
#             cr.execute('select id from purchase_order_line where order_id = %s and id = %s',(po_id,po_line_id,))
#             line = cr.fetchall()
#             if not line:
#                 res['value'].update({'uom_id':False,
#                                     'product_uom_qty':False,
#                                     'price_unit':False,
#                                     'po_line_id':False,})
#         return res
    
tpt_service_entry_line()

class tpt_third_service_entry(osv.osv):
    _name = "tpt.third.service.entry"
    def amount_all_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'grand_total': 0.0,
            }
            grand_total = 0.0
            amount_line = 0.0 
            for service in line.third_service_line:
                amount_line = service.product_uom_qty * service.price_unit
                grand_total += round(amount_line,2)
            res[line.id]['grand_total'] = grand_total
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tpt.third.service.entry.line').browse(cr, uid, ids, context=context):
            result[line.third_service_id.id] = True
        return result.keys()
    
    _columns = {
        'name':fields.char('Document No', size = 1024,readonly=True),
        'create_date': fields.datetime('Created on',readonly = True),
        'maintenance_id':fields.many2one('tpt.maintenance.oder','Maintenance Order No',readonly = True),
        'service_type':fields.selection([('internal','Third Party Internal'),('external','Third Party External')],'Service Type'),
        'work_taken': fields.date('Work Taken on',required=True),
#         'department_id': fields.many2one('hr.department', 'Department',required=True),
#         'section_id': fields.many2one('arul.hr.section', 'Section',required=True),
#         'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True),
#         'machine_id': fields.many2one('tpt.machineries', 'Machineries',required=True),
        'department_id': fields.related('maintenance_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
        'section_id': fields.related('maintenance_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
        'equip_id': fields.related('maintenance_id','equip_id',type='many2one', relation='tpt.equipment',string='Equipment', readonly = True),
        'machine_id': fields.related('maintenance_id','machine_id',type='many2one', relation='tpt.machineries',string='Machineries', readonly = True),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'third_service_line':fields.one2many('tpt.third.service.entry.line','third_service_id','Service Entry Lines'),
        'grand_total': fields.function(amount_all_line, multi='sums',string='Grand Total',digits=(16,2),
                                         store={
                'tpt.third.service.entry': (lambda self, cr, uid, ids, c={}: ids, ['third_service_line'], 10),
                'tpt.third.service.entry.line': (_get_order, ['product_uom_qty', 'uom_id', 'price_unit'], 10),})
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.third.service.entry.seq')
            vals['name'] =  sequence
        new_id = super(tpt_third_service_entry, self).create(cr, uid, vals, context=context)
        return new_id
    
    def bt_service_invoice(self, cr, uid, ids, context=None):
        return True
    
    def bt_save(self, cr, uid, ids,vals,context=None):
        return True
    
tpt_third_service_entry()

class tpt_third_service_entry_line(osv.osv):
    _name = "tpt.third.service.entry.line"
    def line_net_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            line_net = 0.0
            res[line.id] = {
                    'line_net': 0.0,
                }  
            line_net = line.product_uom_qty * line.price_unit
            res[line.id]['line_net'] = round(line_net,2)
        return res
    _columns = {
        'third_service_id': fields.many2one('tpt.third.service.entry','Third Party Service Entry',ondelete='cascade'),
        'create_date': fields.datetime('Created Date',readonly = True),
        'work_taken': fields.date('Work Taken Date',required=True),
        'po_id':fields.many2one('purchase.order','Service PO',required=True,ondelete = 'restrict'),
        'po_line_id':fields.many2one('purchase.order.line','Particulars',required=True, ondelete = 'restrict'),
        'gl_account': fields.many2one('account.account', 'GL Account',required=True),
        'uom_id': fields.many2one('product.uom', 'UOM'),
        'product_uom_qty': fields.float('Quantity',digits=(16,3)),   
#         'price_unit': fields.float('Unit Price',digits=(16,3)),
        'price_unit': fields.related('po_line_id','price_unit',type='float', relation='purchase.order.line',string='Unit Price', readonly = True),
        'line_net': fields.function(line_net_line, multi='deltas' ,digits=(16,2),string='Total Amount'),
    }
    
    def _check_qty_line(self, cr, uid, ids, context=None):
        for line in self.browse(cr,uid,ids,context=context):
            qty = line.product_uom_qty or 0
            po_qty = line.po_line_id and line.po_line_id.product_qty or 0
            if qty > po_qty:
                raise osv.except_osv(_('Warning!'),_('Quantity can not be greater than PO Quantity!'))
        return True
    _constraints = [
        (_check_qty_line, 'Identical Data', ['product_uom_qty']),
    ]
    
    def onchange_po_line_id(self, cr, uid, ids,po_line_id=False):
        res = {'value':{
                        'uom_id':False,
                        'product_uom_qty':False,
                        'price_unit':False,
                      }
               }
        if po_line_id:
            no_id = self.pool.get('purchase.order.line').browse(cr,uid,po_line_id)
            res['value'].update({
                        'uom_id':no_id.product_uom and no_id.product_uom.id or False,
                        'product_uom_qty':no_id.product_qty or False,
                        'price_unit':no_id.price_unit or False,
            })
        return res
    
    def onchange_po_id(self, cr, uid, ids,po_id=False,po_line_id=False):
        res = {'value':{}}
        if po_id and po_line_id:
            cr.execute('select id from purchase_order_line where order_id = %s and id = %s',(po_id,po_line_id,))
            line = cr.fetchall()
            if not line:
                res['value'].update({'uom_id':False,
                                    'product_uom_qty':False,
                                    'price_unit':False,
                                    'po_line_id':False,})
        return res
tpt_third_service_entry_line()

class tpt_material_request(osv.osv):
    _inherit = "tpt.material.request"
    
    def amount_issue_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        issue_line_obj = self.pool.get('tpt.material.issue.line')
        for line in self.browse(cr,uid,ids,context=context):
            res[line.id] = {
                'total': 0.0,
            }
            amount = 0.0 
            for req in line.material_request_line:
                issue_line_ids = issue_line_obj.search(cr, uid, [('request_line_id','=',req.id)])
#                 if issue_line_ids:
                for price in issue_line_obj.browse(cr,uid,issue_line_ids):
                    price_unit = 0
#                     for price in [issue_line_obj.browse(cr,uid,x) for x in issue_line_ids]:
                    sql='''
                        select price_unit from stock_move where issue_id=%s and product_id=%s 
                            and issue_id in (select id from tpt_material_issue where state = 'done')
                    '''%(price.material_issue_id.id,price.product_id.id)
                    cr.execute(sql)
                    price_sql = cr.fetchone()
                    price_unit = price_sql and price_sql[0] or 0
                    amount += round(price_unit,2)*price.product_isu_qty
                        
            res[line.id]['total'] = amount
        return res
    
    _columns = {
                'maintenance_id':fields.many2one('tpt.maintenance.oder','Maintenance Order No',readonly = True),
                'chargeable_maintenance_id':fields.many2one('tpt.maintenance.oder','Maintenance Order No',readonly = True),
                'mrs_type':fields.selection([('normal','Normal MRS'),('chargeable', 'Chargeable MRS')],'MRS Type',readonly = True),
                'total': fields.function(amount_issue_line, multi='sums',string='Total',digits=(16,2)),
                'vendor_id':fields.many2one('res.partner', 'Vendor'), 
                }
    def bt_main_save(self, cr, uid, ids,vals,context=None):
        return True
    

tpt_material_request()

class tpt_material_request_line(osv.osv):
    _inherit = "tpt.material.request.line"
    
    def line_net_line(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr,uid,ids,context=context):
            total_value = 0.0
            res[line.id] = {
                    'total_value': 0.0,
                }  
            total_value = line.issue_qty *( line.price_unit and round(line.price_unit,2) or 0)
            res[line.id]['total_value'] = total_value
        return res
    
    _columns = {
                'issue_qty': fields.float('Issued Qty',digits=(16,3),readonly=True),  
                'price_unit': fields.float('Unit Value', readonly=True ),  
#                 'total_value': fields.float('Total Value',readonly=True ), 
                'total_value': fields.function(line_net_line, multi='deltas' ,digits=(16,2),string='Total Value'),
                }
tpt_material_request_line()

class tpt_material_issue(osv.osv):
    _inherit = "tpt.material.issue"
    
    def bt_approve(self, cr, uid, ids, context=None):
        price = 0.0
        product_price = 0.0
        tpt_cost = 0
        account_move_obj = self.pool.get('account.move')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        avg_cost_obj = self.pool.get('tpt.product.avg.cost')
        journal_line = []
        dest_id = False
        move_obj = self.pool.get('stock.move')
                 
         
        for line in self.browse(cr, uid, ids):
            if line.request_type == 'production':
                dest_id = line.dest_warehouse_id and line.dest_warehouse_id.id or False
            else:
                location_ids=self.pool.get('stock.location').search(cr, uid,[('name','=','Scrapped')])
                if location_ids:
                    dest_id = location_ids[0]
             
            for p in line.material_issue_line:
                onhand_qty = 0.0
                location_id = False
                locat_ids = []
                parent_ids = []
                cate_name = p.product_id.categ_id and p.product_id.categ_id.cate_name or False
                sql = '''
                    select case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty, product_id 
                    from tpt_material_issue_line where product_id = %s and material_issue_id in (select id from tpt_material_issue where name = %s) group by product_id
                '''%(p.product_id.id, line.name.id)
                cr.execute(sql)
                for sum in cr.dictfetchall():
                    product_id = self.pool.get('product.product').browse(cr,uid,sum['product_id'])
                    sql = '''
                        select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                            (select st.product_qty
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_dest_id = %s 
                            union all
                            select st.product_qty*-1
                                from stock_move st 
                                where st.state='done' and st.product_id=%s and st.location_id = %s
                            )foo
                    '''%(sum['product_id'],line.warehouse.id,sum['product_id'],line.warehouse.id)
                    cr.execute(sql)
                    ton_sl = cr.dictfetchone()['ton_sl']
                    if sum['product_isu_qty'] > ton_sl:
                        raise osv.except_osv(_('Warning!'),_("You are confirm %s but only %s available for this product '%s' " %(sum['product_isu_qty'], ton_sl,product_id.default_code)))
                if cate_name == 'raw':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                    location_id = locat_ids[0]
                if cate_name == 'spares':
                    parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if parent_ids:
                        locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
                    if locat_ids:
                        location_id = locat_ids[0]
                if location_id and cate_name != 'finish':
                    sql = '''
                          select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl,case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where st.state='done' and st.location_dest_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                                and st.location_dest_id != st.location_id
                                and ( picking_id is not null 
                                or inspec_id is not null 
                                or (st.id in (select move_id from stock_inventory_move_rel))
                        )
                    '''%(location_id,p.product_id.id,line.date_expec)
                    cr.execute(sql)
                    inventory = cr.dictfetchone()
                    if inventory:
                        hand_quantity = inventory['ton_sl'] or 0
                        total_cost = inventory['total_cost'] or 0
    #                     avg_cost = hand_quantity and total_cost/hand_quantity or 0
                    sql = '''
                       select case when sum(st.product_qty)!=0 then sum(st.product_qty) else 0 end ton_sl, case when sum(st.price_unit*st.product_qty)!=0 then sum(st.price_unit*st.product_qty) else 0 end total_cost
                            from stock_move st
                            where st.state='done' and st.location_id=%s and st.product_id=%s and to_char(date, 'YYYY-MM-DD')<'%s'
                            and issue_id is not null
                             
                    '''%(location_id,p.product_id.id,line.date_expec)
                    cr.execute(sql)
                    for issue in cr.dictfetchall():
                        hand_quantity_issue = issue['ton_sl'] or 0
                        total_cost_issue = issue['total_cost'] or 0
                    #TPT By BalamuruganPurushothaman on 14/10/2015 - To avoid throwing Warning - Physical Inventpries to Material Issue
                    opening_stock_value = 0
                    if (hand_quantity-hand_quantity_issue)!=0:
                        opening_stock_value = (total_cost-total_cost_issue)/(hand_quantity-hand_quantity_issue)
                     
                rs = {
                      'name': '/',
                      'product_id':p.product_id and p.product_id.id or False,
                      'product_qty':p.product_isu_qty or False,
                      'product_uom':p.uom_po_id and p.uom_po_id.id or False,
                      'location_id':line.warehouse and line.warehouse.id or False,
                      'location_dest_id':dest_id,
                      'issue_id':line.id,
                      'date':line.date_expec or False,
                      'price_unit': opening_stock_value or 0,
                      }
                 
                move_id = move_obj.create(cr,uid,rs)
                # boi vi field price unit tu dong lam tron 2 so thap phan nen phai dung sql de update lai
                sql = '''
                        update stock_move set price_unit = %s where id = %s
                '''%(opening_stock_value, move_id)
                cr.execute(sql)
                move_obj.action_done(cr, uid, [move_id])
                cr.execute(''' update stock_move set date=%s,date_expected=%s where id=%s ''',(line.date_expec,line.date_expec,move_id,))
            date_period = line.date_expec
            sql = '''
                select id from account_journal
            '''
            cr.execute(sql)
            journal_ids = [r[0] for r in cr.fetchall()]
            sql = '''
                select id from account_period where '%s' between date_start and date_stop and special is False
            '''%(date_period)
            cr.execute(sql)
            period_ids = [r[0] for r in cr.fetchall()]
              
            if not period_ids:
                raise osv.except_osv(_('Warning!'),_('Period is not null, please configure it in Period master !'))
                 
            for mater in line.material_issue_line:
#                 price += mater.product_id.standard_price * mater.product_isu_qty
                acc_expense = mater.product_id and mater.product_id.property_account_expense and mater.product_id.property_account_expense.id or False
                acc_asset = mater.product_id and mater.product_id.product_asset_acc_id and mater.product_id.product_asset_acc_id.id or False
                if not acc_expense or not acc_asset:
                    raise osv.except_osv(_('Warning!'),_('Please configure Expense Account and Product Asset Account for all materials!'))
                avg_cost_ids = avg_cost_obj.search(cr, uid, [('product_id','=',mater.product_id.id),('warehouse_id','=',line.warehouse.id)])
                unit = 1
                if avg_cost_ids:
                    avg_cost_id = avg_cost_obj.browse(cr, uid, avg_cost_ids[0])
                    unit = avg_cost_id.avg_cost or 0
                sql = '''
                    select price_unit from stock_move where product_id=%s and product_qty=%s and issue_id=%s
                '''%(mater.product_id.id,mater.product_isu_qty,mater.material_issue_id.id)
                cr.execute(sql)
                move_price = cr.fetchone()
                if move_price and move_price[0] and move_price[0]>0:
                    unit=move_price[0]
                if not unit or unit<0:
                    unit=1
                price += unit * mater.product_isu_qty
                product_price = unit * mater.product_isu_qty
                ### update request
#                 cr.execute(''' update tpt_material_request_line set issue_qty = %s, price_unit = %s, total_value = %s where id = %s ''',(mater.product_isu_qty,unit,product_price,mater.request_line_id.id,))
                cr.execute(''' update tpt_material_request_line set issue_qty = %s, price_unit = %s where id = %s ''',(mater.product_isu_qty,unit,mater.request_line_id.id,))
                ###
                journal_line.append((0,0,{
                                        'name':line.doc_no + ' - ' + mater.product_id.name, 
                                        'account_id': acc_asset,
                                        'debit':0,
                                        'credit':product_price,
                                        'product_id':mater.product_id.id,
                                          
                                       }))
                journal_line.append((0,0,{
                            'name':line.doc_no + ' - ' + mater.product_id.name, 
                            'account_id': acc_expense,
                            'credit':0,
                            'debit':product_price,
                            'product_id':mater.product_id.id,
                        }))
            value={
                'journal_id':journal_ids[0],
                'period_id':period_ids[0] ,
                'ref': line.doc_no,
                'date': date_period,
                'material_issue_id': line.id,
                'line_id': journal_line,
                'doc_type':'good'
                }
            new_jour_id = account_move_obj.create(cr,uid,value)
            auto_ids = self.pool.get('tpt.auto.posting').search(cr, uid, [])
            if auto_ids:
                auto_id = self.pool.get('tpt.auto.posting').browse(cr, uid, auto_ids[0], context=context)
                if auto_id.material_issue:
                    try:
                        account_move_obj.button_validate(cr,uid, [new_jour_id], context)
                    except:
                        pass
            self.write(cr, uid, ids,{'state':'done'})
        return True
tpt_material_issue()

### TPT-Start
class tpt_service_gpass_req(osv.osv):
    _name = "tpt.service.gpass.req"
    
    _columns = {               
            'name': fields.char('Document No', size = 1024, readonly=True), 
            'maintenance_id': fields.many2one('tpt.maintenance.oder', 'Maintenance Order', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'vendor_id': fields.many2one('res.partner', '3rd Party Service Vendor', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'equipment_id': fields.many2one('tpt.equipment', 'Equipement', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'sub_equipment_id': fields.many2one('tpt.machineries', 'Sub Equipement', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'service_date': fields.date('Date', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'carrier_name': fields.char('Carrier Name', size = 1024, states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'truck_no': fields.char('Truck No.', size = 1024, states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'purpose': fields.text('Purpose', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'service_gpass_req_line': fields.one2many('tpt.service.gpass.req.line', 'gpass_req_id', 'Service GPass', states={'cancel': [('readonly', True)], 'approve':[('readonly', True)], 'done':[('readonly', True)]}),
            'state':fields.selection([('draft', 'Draft'), 
                                      ('waiting', 'Waiting for Approval'), 
                                      ('approve', 'Approved'), 
                                      ('cancel', 'Cancelled'), 
                                      ('done', 'Service Gate Pass Raised')], 'Status', readonly=True),
            'create_date': fields.datetime('Created Date', readonly = True),
            'create_uid': fields.many2one('res.users', 'Created By', ondelete='restrict', readonly = True),    
                }
    _defaults = {
        'state': 'draft',
        'name': '/',
        'service_date': time.strftime('%Y-%m-%d'),
    }
    
    def onchange_maintenance_id(self, cr, uid, ids,maintenance_id=False, context=None):
        vals = {}    
        if maintenance_id:
            maintenance_obj = self.pool.get('tpt.maintenance.oder').browse(cr, uid, maintenance_id)
            vals.update( {
                    'equipment_id':maintenance_obj.equip_id and maintenance_obj.equip_id.id or False,
                    'sub_equipment_id':maintenance_obj.machine_id and maintenance_obj.machine_id.id or False,
                    })
        return {'value': vals} 
    def bt_generate(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if not line.service_gpass_req_line:
                raise osv.except_osv(_('Warning!'),_('You can not approve without lines!'))
            self.write(cr, uid, ids,{'state':'waiting'})
        return True 
    def bt_approve(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'approve'})
        return True 
    def bt_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'cancel'})
        return True 
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.service.gpass.req.import') or '/'
            
        new_id = super(tpt_service_gpass_req, self).create(cr, uid, vals, context=context)
        return new_id
    def bt_print(self, cr, uid, ids, context=None):
        '''
        This function prints the Service Gate Pass Print and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        
        datas = {
             'ids': ids,
             'model': 'tpt.service.gpass.req',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'service_gpass_req_report',
            } 
        
tpt_service_gpass_req()

class tpt_service_gpass_req_line(osv.osv):
    _name = "tpt.service.gpass.req.line"
       
    _columns = {               
            'gpass_req_id': fields.many2one('tpt.service.gpass.req', 'Service GPass Requisition', ondelete = 'cascade'),
            'item_desc': fields.char('Item Description', size = 1024, ),
            'service_qty': fields.float('Quatity'),
            'approx_qty': fields.float('Approximate Value'),
            'uom_po_id': fields.many2one('product.uom', 'UOM'),
                }
    
tpt_service_gpass_req_line()

class tpt_service_gpass(osv.osv):
    _name = "tpt.service.gpass"
    
    _columns = {                
            'gpass_req_id': fields.many2one('tpt.service.gpass.req', 'Service Gate Pass Requisition', states={'close': [('readonly', True)], 'approve':[('readonly', True)]}),
            'maintenance_id': fields.many2one('tpt.maintenance.oder', 'Maintenance Order'),
            'vendor_id': fields.many2one('res.partner', '3rd Party Service Vendor'),
            'service_date': fields.date('Date', states={'close': [('readonly', True)], 'approve':[('readonly', True)]}),
            'equipment_id': fields.many2one('tpt.equipment', 'Equipement'),
            'sub_equipment_id': fields.many2one('tpt.machineries', 'Sub Equipement'),
            'carrier_name': fields.char('Carrier Name', size = 1024, ),
            'truck_no': fields.char('Truck No.', size = 1024, ),
            'purpose': fields.text('Purpose'),
            'exp_return_date': fields.date('Expected Return Date', states={'close': [('readonly', True)], 'approve':[('readonly', True)]}),
            'act_return_date': fields.date('Actual Return Date', states={'close': [('readonly', True)]}),
            'service_gpass_line': fields.one2many('tpt.service.gpass.line', 'gpass_id', 'Service GPass', states={'close': [('readonly', True)], 'approve':[('readonly', True)]}),
            'state':fields.selection([('draft', 'Draft'),
                                      ('close', 'Closed'),
                                       ('approve', 'Gate Pass Generated')], 'Status', readonly=True),
            'create_date': fields.datetime('Created Date', readonly = True),
            'create_uid': fields.many2one('res.users', 'Created By', ondelete='restrict', readonly = True),    
                }
    _defaults = {
        'state': 'draft',
        'service_date': time.strftime('%Y-%m-%d'),
    }
    def onchange_service_gpass_id(self, cr, uid, ids,service_gpass_id=False, context=None):
        vals = {}    
        if service_gpass_id:
            gpass_req_obj = self.pool.get('tpt.service.gpass.req').browse(cr, uid, service_gpass_id)
            for line in self.browse(cr, uid, ids):
                sql = '''
                    delete from tpt_service_gpass_line where gpass_id = %s
                '''%(line.id)
                cr.execute(sql)
            service_gpass_line = []
            for gpass_req_line in gpass_req_obj.service_gpass_req_line:
                rs_service = {
                                  'item_desc': gpass_req_line.item_desc or '',
                                  'service_qty': gpass_req_line.service_qty or 0,
                                  'approx_qty': gpass_req_line.approx_qty or 0,
                                  'uom_po_id': gpass_req_line.uom_po_id and gpass_req_line.uom_po_id.id or False,
                                  
                                  }
                service_gpass_line.append((0,0,rs_service))
                
                         
            
            vals = {
                    'maintenance_id':gpass_req_obj.maintenance_id and gpass_req_obj.maintenance_id.id or False,
                    'vendor_id':gpass_req_obj.vendor_id and gpass_req_obj.vendor_id.id or False,
                    'equipment_id':gpass_req_obj.equipment_id and gpass_req_obj.equipment_id.id or False,
                    'sub_equipment_id':gpass_req_obj.sub_equipment_id and gpass_req_obj.sub_equipment_id.id or False,
                    'carrier_name':gpass_req_obj.carrier_name or '',
                    'truck_no':gpass_req_obj.truck_no or '',
                    'purpose':gpass_req_obj.purpose or '',
                    'service_gpass_line':service_gpass_line,
                    }
        return {'value': vals}  
    def create(self, cr, uid, vals, context=None):
        if 'gpass_req_id' in vals:
            gpass_req_obj = self.pool.get('tpt.service.gpass.req').browse(cr, uid, vals['gpass_req_id']) 
            service_gpass_line = []
            for gpass_req_line in gpass_req_obj.service_gpass_req_line:
                rs_service = {
                                  'item_desc': gpass_req_line.item_desc or '',
                                  'service_qty': gpass_req_line.service_qty or 0,
                                  'approx_qty': gpass_req_line.approx_qty or 0,
                                  'uom_po_id': gpass_req_line.uom_po_id and gpass_req_line.uom_po_id.id or False,
                                  
                                  }
                service_gpass_line.append((0,0,rs_service))
                 
            vals.update( {
                    'maintenance_id':gpass_req_obj.maintenance_id and gpass_req_obj.maintenance_id.id or False,
                    'vendor_id':gpass_req_obj.vendor_id and gpass_req_obj.vendor_id.id or False,
                    'equipment_id':gpass_req_obj.equipment_id and gpass_req_obj.equipment_id.id or False,
                    'sub_equipment_id':gpass_req_obj.sub_equipment_id and gpass_req_obj.sub_equipment_id.id or False,
                    'carrier_name':gpass_req_obj.carrier_name or '',
                    'truck_no':gpass_req_obj.truck_no or '',
                    'purpose':gpass_req_obj.purpose or '',
                    'service_gpass_line':service_gpass_line,
                    })
                   
        new_id = super(tpt_service_gpass, self).create(cr, uid, vals, context=context)
        if 'gpass_req_id' in vals:
            gpass_obj = self.pool.get('tpt.service.gpass.req')
            gpass_req_obj = gpass_obj.browse(cr, uid, vals['gpass_req_id']) 
            gpass_obj.write(cr, uid, [gpass_req_obj.id], {'state':'done'})        
        return new_id
    def write(self, cr, uid, ids, vals, context=None):
        if 'gpass_req_id' in vals:
            gpass_req_obj = self.pool.get('tpt.service.gpass.req').browse(cr, uid, vals['gpass_req_id']) 
            service_gpass_line = []
            for gpass_req_line in gpass_req_obj.service_gpass_req_line:
                rs_service = {
                                  'item_desc': gpass_req_line.item_desc or '',
                                  'service_qty': gpass_req_line.service_qty or 0,
                                  'approx_qty': gpass_req_line.approx_qty or 0,
                                  'uom_po_id': gpass_req_line.uom_po_id and gpass_req_line.uom_po_id.id or False,
                                  
                                  }
                service_gpass_line.append((0,0,rs_service))
                 
            vals.update( {
                    'maintenance_id':gpass_req_obj.maintenance_id and gpass_req_obj.maintenance_id.id or False,
                    'vendor_id':gpass_req_obj.vendor_id and gpass_req_obj.vendor_id.id or False,
                    'equipment_id':gpass_req_obj.equipment_id and gpass_req_obj.equipment_id.id or False,
                    'sub_equipment_id':gpass_req_obj.sub_equipment_id and gpass_req_obj.sub_equipment_id.id or False,
                    'carrier_name':gpass_req_obj.carrier_name or '',
                    'truck_no':gpass_req_obj.truck_no or '',
                    'purpose':gpass_req_obj.purpose or '',
                    'service_gpass_line':service_gpass_line,
                    })
        new_write = super(tpt_service_gpass, self).write(cr, uid,ids, vals, context)
        if 'gpass_req_id' in vals:
            gpass_obj = self.pool.get('tpt.service.gpass.req')
            gpass_req_obj = gpass_obj.browse(cr, uid, vals['gpass_req_id']) 
            gpass_obj.write(cr, uid, [gpass_req_obj.id], {'state':'done'})                  
        return new_write
    def bt_generate(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            self.write(cr, uid, ids,{'state':'approve'})
        return True 
    def bt_close(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids):
            if not line.act_return_date:
                raise osv.except_osv(_('Warning!'),_('Please fill the Actual Retutrn Date!'))
            self.write(cr, uid, ids,{'state':'close'})
        return True 
    def bt_print(self, cr, uid, ids, context=None):
        '''
        This function prints the Service Gate Pass Print and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        
        datas = {
             'ids': ids,
             'model': 'tpt.service.gpass',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'service_gate_out_pass_report',
            } 
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['gpass_req_id', 'maintenance_id'], context)
  
        for record in reads:
            name = record['gpass_req_id']
            res.append((record['id'], name))
        return res 
    def _check_date(self, cr, uid, ids, context=None): 
        for line in self.browse(cr, uid, ids, context = context):
            if line.act_return_date:
                if line.act_return_date < line.service_date:
                    raise osv.except_osv(_('Warning!'),_('Actual Return Date is less than Gate Pass Date'))
                    return False
        return True    
    _constraints = [
       
        (_check_date, _(''), ['service_date', 'act_return_date']),
        ]
tpt_service_gpass()

class tpt_service_gpass_line(osv.osv):
    _name = "tpt.service.gpass.line"
       
    _columns = {               
            'gpass_id': fields.many2one('tpt.service.gpass', 'Service GPass', ondelete = 'cascade'),
            'item_desc': fields.char('Item Description', size = 1024, ),
            'service_qty': fields.float('Quatity'),          
            'approx_qty': fields.float('Approximate Value'),
            'uom_po_id': fields.many2one('product.uom', 'UOM'),
                }
    
tpt_service_gpass_line()

### TPT-Start
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
