# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
class hr_department(osv.osv):
    _description = "Department"
    _inherit = 'hr.department'
    _columns = {
        'code': fields.char('Department Code', size=1024, required = True),
        'primary_auditor_id': fields.many2one('res.users', 'Primary Time Auditor',ondelete='restrict'),
        'secondary_auditor_id':  fields.many2one('res.users', 'Sec. Time Auditor',ondelete='restrict'),
        'section_ids': fields.one2many('arul.hr.section', 'department_id','Sections'),
        'designation_line': fields.one2many('arul.hr.designation', 'department_id', 'Designation Line'),
        'payroll_sub_area_id': fields.many2one('arul.hr.payroll.sub.area', 'Area',ondelete='restrict'),
    }
    
#     def _check_code(self, cr, uid, ids, context=None):
#         for department in self.browse(cr, uid, ids, context=context):
#             department_ids = self.search(cr, uid, [('id','!=',department.id),('code','=',department.code)])
#             if department_ids:  
#                 return False
#         return True
    def _check_code(self, cr, uid, ids, context=None):
        for department in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from hr_department where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(department.id,department.code,department.name)
            cr.execute(sql)
            department_ids = [row[0] for row in cr.fetchall()]
            if department_ids:  
                return False
        return True
    _constraints = [
        (_check_code, 'Identical Data', ['code']),
    ] 
    

    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(hr_department, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(hr_department, self).write(cr, uid,ids, vals, context)
    
hr_department()

class arul_hr_section(osv.osv):
    _name = 'arul.hr.section'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
         'department_id': fields.many2one('hr.department', 'Department',ondelete='cascade'),
        
    }
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_hr_section, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            code = vals['code'].replace(" ","")
            vals['code'] = code
        return super(arul_hr_section, self).write(cr, uid,ids, vals, context)
    
    def _check_code_id(self, cr, uid, ids, context=None):
        for section in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from arul_hr_section where id != %s and (lower(code) = lower('%s') or lower(name) = lower('%s'))
            '''%(section.id,section.code,section.name)
            cr.execute(sql)
            section_ids = [row[0] for row in cr.fetchall()]
            if section_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code','name']),
    ]    
arul_hr_section()



class arul_hr_designation(osv.osv):
    _name = 'arul.hr.designation'
    _columns = {
        'designation_id': fields.many2one('hr.job', 'Designation',required=True),
        'number': fields.integer('No.of Persons'),
        'resource_budget': fields.integer('Resource Budget'),
        'department_id': fields.many2one('hr.department', 'Department',ondelete="cascade"),
    }
    
#     def _check_designation_id(self, cr, uid, ids, context=None):
#         for designation in self.browse(cr, uid, ids, context=context):
#             designation_ids = self.search(cr, uid, [('id','!=',designation.id),('department_id','=',designation.department_id.id),('designation_id','!=',False),('designation_id','=',designation.designation_id.id)])
#             if designation_ids:  
#                 return False
#         return True
# #     
#     _constraints = [
#         (_check_designation_id, 'Identical Data', ['designation_id']),
#     ]    
    
arul_hr_designation()
