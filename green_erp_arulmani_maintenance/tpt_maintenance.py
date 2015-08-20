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
                select id from tpt_equip_category where id != %s and code = '%s'
            '''%(equip_cat.id,equip_cat.code)
            cr.execute(sql)
            equip_code_ids = [row[0] for row in cr.fetchall()]
            if equip_code_ids or equip_name_ids:  
                raise osv.except_osv(_('Warning!'),_('This code or name can not be duplicated!'))
        return True
    _constraints = [
        (_check_name_code, 'Identical Data', ['name','code']),
    ]
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
                select id from tpt_equipment where id != %s and code = '%s'
            '''%(equip.id,equip.code)
            cr.execute(sql)
            equip_code_ids = [row[0] for row in cr.fetchall()]
            if equip_code_ids or equip_name_ids:  
                raise osv.except_osv(_('Warning!'),_('This code or name can not be duplicated!'))
        return True
    _constraints = [
        (_check_name_code, 'Identical Data', ['name','code']),
    ]
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
                select id from tpt_machineries where id != %s and lower(name) = lower('%s')
            '''%(equip.id,equip.name)
            cr.execute(sql)
            equip_name_ids = [row[0] for row in cr.fetchall()]
            sql = '''
                select id from tpt_machineries where id != %s and code = '%s'
            '''%(equip.id,equip.code)
            cr.execute(sql)
            equip_code_ids = [row[0] for row in cr.fetchall()]
            if equip_code_ids or equip_name_ids:  
                raise osv.except_osv(_('Warning!'),_('This code or name can not be duplicated!'))
        return True
    _constraints = [
        (_check_name_code, 'Identical Data', ['name','code']),
    ]
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
        'department_id': fields.many2one('hr.department', 'Department',required=True,states={'close': [('readonly', True)]}),
        'section_id': fields.many2one('arul.hr.section', 'Section',required=True,states={'close': [('readonly', True)]}),
        'employee_id': fields.many2one('hr.employee', 'Assigned to',required=True,states={'close': [('readonly', True)]},ondelete='restrict'),
        'priority':fields.selection([('high', 'High'),('medium', 'Medium'),('low', 'Low')],'Priority',states={'close': [('readonly', True)]}),
        'equip_id': fields.many2one('tpt.equipment', 'Equipment',required=True,states={'close': [('readonly', True)]}),
        'machine_id': fields.many2one('tpt.machineries', 'Machineries',required=True,states={'close': [('readonly', True)]}),
        'start_date': fields.date('Work Start Date',required=True,states={'close': [('readonly', True)]}),
        'completion_date': fields.date('Target Date of Completion',required=True,states={'close': [('readonly', True)]}),
        'create_uid':fields.many2one('res.users','Raised By', readonly = True),
        'issue_reported':fields.text('Issue Reported',states={'close': [('readonly', True)]}),
        'issue_finding':fields.text('Issue Finding',states={'close': [('readonly', True)]}),
        'service_entry_line':fields.one2many('tpt.service.entry','maintenance_id','Staff Service Entry',states={'close': [('readonly', True)]}),
        'third_service_line':fields.one2many('tpt.third.service.entry','maintenance_id','Third Party Service Entry',states={'close': [('readonly', True)]}),
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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
