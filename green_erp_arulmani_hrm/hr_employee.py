# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class arul_employee_category(osv.osv):
    _name="arul.employee.category"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
        'active':fields.boolean('Active'),
        'sub_category_ids':fields.many2many('arul.employee.sub.category','catagory_subcategory_ref','category_id','sub_category_id','Sub Category'),
              }
    _defaults={
            'active':True,
               }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_category()

class arul_employee_sub_category(osv.osv):
    _name="arul.employee.sub.category"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
              }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_sub_category()

class arul_employee_actions(osv.osv):
    _name="arul.employee.actions"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
        'active':fields.boolean('Active'),
#         'action_type_ids':fields.many2many('arul.employee.sub.category','catagory_subcategory_ref','category_id','sub_category_id','Sub Category'),
              }
    _defaults={
            'active':True,
               }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_actions()

class arul_employee_sub_category(osv.osv):
    _name="arul.employee.sub.category"
    _columns={
        'name':fields.char('Name', size=64, required = True),
        'code':fields.char('Code',size=64,required = True),
              }
    def _check_code(self, cr, uid, ids, context=None):
        for employee in self.browse(cr, uid, ids, context=context):
            employee_ids = self.search(cr, uid, [('id','!=',employee.id),('name','=',employee.code)])
            if employee_ids:  
                return False
        return True

    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ]
arul_employee_sub_category()