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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
