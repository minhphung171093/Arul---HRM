# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime



class arul_hr_payroll_area(osv.osv):
    _name = 'arul.hr.payroll.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_code_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            payroll_name_ids = self.search(cr, uid, [('id','!=',payroll.id),('name','=',payroll.name)])
            if payroll_code_ids or payroll_name_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
    
arul_hr_payroll_area()

class arul_hr_payroll_sub_area(osv.osv):
    _name = 'arul.hr.payroll.sub.area'
    _columns = {
        'name': fields.char('Name', size=1024, required = True),
         'code': fields.char('Code', size=1024, required = True),
        
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for payroll in self.browse(cr, uid, ids, context=context):
            payroll_ids = self.search(cr, uid, [('id','!=',payroll.id),('code','=',payroll.code)])
            if payroll_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
    
arul_hr_payroll_sub_area()
