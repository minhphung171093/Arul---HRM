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
    _columns = {
        'equipment_id': fields.many2one('tpt.equipment', 'Equipment',ondelete='cascade'),
        'machineries_id': fields.many2one('tpt.machineries', 'Machineries',ondelete='cascade'),
        'description':fields.char('Attachment Description', size = 1024),
    }
    
tpt_document_attach()

class tpt_machineries(osv.osv):
    _name = "tpt.machineries"
    _columns = {
        'name':fields.char('Machineries Name', size = 1024,required=True),
        'code':fields.char('Machineries Code', size = 1024,required=True),
        'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True),
        'cost_id': fields.many2one('tpt.cost.center', 'Cost Center',required=True),
#         'department_id': fields.many2one('hr.department', 'Department',required=True),
#         'section_id': fields.many2one('arul.hr.section', 'Section',required=True),
        'start_date': fields.date('Installation Start Date',required=True),
        'end_date': fields.date('Installation End Date',required=True),
        'men_power_line':fields.one2many('tpt.men.power','equipment_id','Men Power Consumption'),
        'document_attach_line':fields.one2many('tpt.document.attach','equipment_id','Document Attachments'),
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
#         'department_id': fields.many2one('hr.department', 'Department',required=True,readonly = True,states={'draft': [('readonly', False)]}),
#         'section_id': fields.many2one('arul.hr.section', 'Section',required=True,readonly = True,states={'draft': [('readonly', False)]}),
        'department_id': fields.related('equip_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
        'section_id': fields.related('equip_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
        'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True,readonly = True,states={'draft': [('readonly', False)]}),
        'machine_id': fields.many2one('tpt.machineries', 'Machineries',required=True,readonly = True,states={'draft': [('readonly', False)]}),
        'issue_date': fields.date('Issue Dated on',required=True,readonly = True,states={'draft': [('readonly', False)]}),
        'issue_type':fields.selection([('major', 'Major'),('minor', 'Minor'),('critical', 'Critical')],'Issue Type',readonly = True,states={'draft': [('readonly', False)]}),
        'priority':fields.selection([('high', 'High'),('medium', 'Medium'),('low', 'Low')],'Priority',readonly = True,states={'draft': [('readonly', False)]}),
        'issue_reported':fields.text('Issue Reported',readonly = True,states={'draft': [('readonly', False)]}),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'create_date': fields.datetime('Created Date',readonly = True),
        'schedule_line':fields.one2many('tpt.schedule','notification_id','Schedule',readonly = True,states={'draft': [('readonly', False)]}),
        'state':fields.selection([('draft', 'Drafted'),('waiting', 'Waiting For Approval'),
                                  ('in', 'In Progress'),('close','Closed')],'Status', readonly=True),
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
        if department_id:
            return res
    
    def onchange_equip_id(self, cr, uid, ids,equip_id=False):
        res = {'value':{'machine_id':False,
                        'department_id':False,
                        'section_id':False,}}
        if equip_id:
            no_id = self.pool.get('tpt.equipment').browse(cr,uid,equip_id)
            res['value'].update({
                        'department_id':no_id.department_id and no_id.department_id.id or False,
                        'section_id':no_id.section_id and no_id.section_id.id or False,
            })
            return res
        
    def bt_generate(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'waiting'})
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'in'})
    
    def bt_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'close'})
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
    _columns = {
        'name':fields.char('Order No', size = 1024,readonly=True),
        'issue_type':fields.selection([('major', 'Major'),('minor', 'Minor'),('critical', 'Critical')],'Issue Type',states={'close': [('readonly', True)]}),
        'notification_id':fields.many2one('tpt.notification','Notification No',required = True,states={'close': [('readonly', True)]}),
        'create_date': fields.datetime('Created Date',readonly = True),
        'notif_type':fields.selection([
                                ('prevent','Preventive Maintenance'),
                                ('break','Breakdown')],'Notification Type',required = True,states={'close': [('readonly', True)]}),
#         'department_id': fields.many2one('hr.department', 'Department',required=True,states={'close': [('readonly', True)]}),
#         'section_id': fields.many2one('arul.hr.section', 'Section',required=True,states={'close': [('readonly', True)]}),
        'department_id': fields.related('notification_id','department_id',type='many2one', relation='hr.department',string='Department', readonly = True),
        'section_id': fields.related('notification_id','section_id',type='many2one', relation='arul.hr.section',string='Section', readonly = True),
        'equip_id': fields.related('notification_id','equip_id',type='many2one', relation='tpt.equipment',string='Equipment', readonly = True),
        'machine_id': fields.related('notification_id','machine_id',type='many2one', relation='tpt.machineries',string='Machineries', readonly = True),
        
        'employee_id': fields.many2one('hr.employee', 'Assigned to',required=True,states={'close': [('readonly', True)]},ondelete='restrict'),
        'priority':fields.selection([('high', 'High'),('medium', 'Medium'),('low', 'Low')],'Priority',states={'close': [('readonly', True)]}),
#         'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True,states={'close': [('readonly', True)]}),
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
        'state':fields.selection([('draft', 'Drafted'),
                                  ('in', 'In Progress'),
                                  ('completed', 'Completed'),
                                  ('put', 'Put On Hold'),
                                  ('close','Closed')],'Status', readonly=True),
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
    
    def bt_process(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'completed'})
    
    def bt_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'close'})
    
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
        'grand_total': fields.function(amount_all_line, multi='sums',string='Grand Total',digits=(16,3),
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
        'po_id':fields.many2one('purchase.order','Purchase Order', ondelete = 'restrict'),
        'po_line_id':fields.many2one('purchase.order.line','Particulars', ondelete = 'restrict'),
        'uom_id': fields.many2one('product.uom', 'UOM'),
        'product_uom_qty': fields.float('Quantity',digits=(16,3)),   
        'price_unit': fields.float('Unit Price',digits=(16,3)),
        'line_net': fields.function(line_net_line, multi='deltas' ,digits=(16,3),string='Line Net'),
    }
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
        'third_service_line':fields.one2many('tpt.third.service.entry.line','third_service_id','Service Entry Lines'),
        'grand_total': fields.function(amount_all_line, multi='sums',string='Grand Total',digits=(16,3),
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
        'price_unit': fields.float('Unit Price',digits=(16,3)),
        'line_net': fields.function(line_net_line, multi='deltas' ,digits=(16,3),string='Total Amount'),
    }
    
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
    _columns = {
                'maintenance_id':fields.many2one('tpt.maintenance.oder','Maintenance Order No',readonly = True),
                'chargeable_maintenance_id':fields.many2one('tpt.maintenance.oder','Maintenance Order No',readonly = True),
                'mrs_type':fields.selection([('normal','Normal MRS'),('chargeable', 'Chargeable MRS')],'MRS Type'),
                }
    
#     def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
#         if context is None:
#             context = {}
#         if context.get('search_ma_request'): 
#             request_id = context.get('request_id')
#             request_master_full_ids = []
#             sql = '''
#                 select request_line_id,case when sum(product_isu_qty)!=0 then sum(product_isu_qty) else 0 end product_isu_qty
#                     from tpt_material_issue_line group by request_line_id
#             '''
#             cr.execute(sql)
#             request_line_ids = []
#             temp = 0
#             lines = cr.fetchall()
#             for request_line in lines:
#                 if request_line[0]:
#                     sql = '''
#                         select case when sum(product_uom_qty)!=0 then sum(product_uom_qty) else 0 end product_uom_qty
#                             from tpt_material_request_line where id = %s
#                     '''%(request_line[0])
#                     cr.execute(sql)
#                     product_uom_qty = cr.fetchone()[0]
#                     if product_uom_qty <= request_line[1]:
#                         temp+=1
#             if temp==len(lines):
#                 request_line_ids.append(request_line[0])
#             if request_line_ids:
#                 cr.execute('''
#                     select material_request_id from tpt_material_request_line where id in %s
#                 ''',(tuple(request_line_ids),))
#                 request_master_full_ids = [r[0] for r in cr.fetchall()]
#             request_master_ids = self.pool.get('tpt.material.request').search(cr, uid, [('id','not in',request_master_full_ids)])
#             args += [('id','in',request_master_ids)]
#         if context.get('normal_material'):
#             sql = '''
#                 select id from tpt_material_request where mrs_type = 'normal'
#             '''
#             cr.execute(sql)
#             request_ids = [r[0] for r in cr.fetchall()]
#             args += [('id','in',request_ids)]
#         return super(tpt_material_request, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
#      
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#        ids = self.search(cr, user, args, context=context, limit=limit)
#        return self.name_get(cr, user, ids, context=context)

tpt_material_request()

class tpt_material_request_line(osv.osv):
    _inherit = "tpt.material.request.line"
    _columns = {
                'issue_qty': fields.float('Issued Qty',digits=(16,3),readonly=True),  
                'price_unit': fields.float('Unit Value', readonly=True ),  
                'total_value': fields.float('Total Value',readonly=True ), 
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
                cr.execute(''' update tpt_material_request_line set issue_qty = %s, price_unit = %s, total_value = %s where id = %s ''',(mater.product_isu_qty,unit,product_price,mater.request_line_id.id,))
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
