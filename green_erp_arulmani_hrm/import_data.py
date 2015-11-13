# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import base64
import calendar
import xlrd
from xlrd import open_workbook,xldate_as_tuple

class tpt_import_employee(osv.osv):
    _name = 'tpt.import.employee'
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
            super(tpt_import_employee, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_employee, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_employee(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            category_obj = self.pool.get('vsis.hr.employee.category')
            sub_category_obj = self.pool.get('hr.employee.sub.category')
            payroll_area_obj = self.pool.get('arul.hr.payroll.area')
            country_obj = self.pool.get('res.country')
            state_obj = self.pool.get('res.country.state')
            job_obj = self.pool.get('hr.job')
            lang_obj = self.pool.get('res.lang')
            religion_obj = self.pool.get('hr.religion')
            employee_obj = self.pool.get('hr.employee')
            department_obj = self.pool.get('hr.department')
            section_obj = self.pool.get('arul.hr.section')
            statutory_obj = self.pool.get('hr.statutory')
            bank_acc_obj = self.pool.get('res.partner.bank')
            bank_obj = self.pool.get('res.bank')
            partner_obj = self.pool.get('res.partner')
            plant_obj = self.pool.get('hr.plant')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    emp_category = sh.cell(row, 3).value
                    category_ids = category_obj.search(cr, uid, [('code','=',emp_category)])
                    if not category_ids:
                        category_id = category_obj.create(cr, uid, {'name':emp_category,'code':emp_category})
                    else:
                        category_id = category_ids[0]
                         
                    sub_category = sh.cell(row, 4).value
                    sub_category_ids = sub_category_obj.search(cr, uid, [('code','=',sub_category),('category_id','=',category_id)])
                    if not sub_category_ids:
                        sub_category_id = sub_category_obj.create(cr, uid, {'name':sub_category,'code':sub_category,'category_id':category_id})
                    else:
                        sub_category_id = sub_category_ids[0]
                         
                    active = sh.cell(row, 7).value
                    if active=='N':
                        is_active = False
                    else:
                        is_active = True
                         
                    payroll_area = sh.cell(row, 8).value
                    payroll_area_ids = payroll_area_obj.search(cr, uid, [('code','=',payroll_area)])
                    if not payroll_area_ids:
                        payroll_area_id = payroll_area_obj.create(cr, uid, {'name':payroll_area,'code':payroll_area})
                    else:
                        payroll_area_id = payroll_area_ids[0]
                         
                    job = sh.cell(row, 11).value
                    job_ids = job_obj.search(cr, uid, [('name','=',job)])
                    if not job_ids:
                        job_id = job_obj.create(cr, uid, {'name':job})
                    else:
                        job_id = job_ids[0]
                     
                    birth_date = sh.cell(row, 12).value
                    if birth_date:
                        birth = birth_date[6:10] + '-' + birth_date[3:5] + '-'+ birth_date[:2]
                    else:
                        birth = False
                         
                    country = sh.cell(row, 13).value
                    country_ids = country_obj.search(cr, uid, [('code','=',country)])
                    if not country_ids:
                        country_id = country_obj.create(cr, uid, {'name':country,'code':country})
                    else:
                        country_id = country_ids[0]
                         
                    state = sh.cell(row, 14).value
                    state_ids = state_obj.search(cr, uid, [('code','=',state),('country_id','=',country_id)])
                    if not state_ids:
                        state_id = state_obj.create(cr, uid, {'name':state,'code':state,'country_id':country_id})
                    else:
                        state_id = state_ids[0]
                     
                    lang = sh.cell(row, 16).value
                    lang_ids = lang_obj.search(cr, uid, [('iso_code','=',lang)])
                    if lang_ids:
                        lang_id = lang_ids[0]
                    else:
                        lang_id = False
                     
                    religion = sh.cell(row, 17).value
                    religion_ids = religion_obj.search(cr, uid, [('name','=',religion)])
                    if not religion_ids:
                        religion_id = religion_obj.create(cr, uid, {'name':religion,'code':religion})
                    else:
                        religion_id = religion_ids[0]
                     
                    marital_status = sh.cell(row, 18).value
                    if marital_status == 'Single':
                        marital = 'single'
                    elif marital_status == 'Married':
                        marital = 'married'
                    elif marital_status == 'Widower':
                        marital = 'widower'
                    elif marital_status == 'Divorced':
                        marital = 'divorced'
                    else:
                        marital = False
                     
                    wedding_date = sh.cell(row, 19).value
                    if wedding_date:
                        wedding = wedding_date[6:10] + '-' + wedding_date[3:5] + '-'+ wedding_date[:2]
                    else:
                        wedding = False
                     
                    department = sh.cell(row, 20).value
                    department_ids = department_obj.search(cr, uid, [('name','=',department)])
                    if not department_ids:
                        department_id = department_obj.create(cr, uid, {'name':department,'code':self.pool.get('ir.sequence').get(cr, uid, 'hr.department.import')})
                    else:
                        department_id = department_ids[0]
                         
                    section = sh.cell(row, 21).value
                    section_ids = section_obj.search(cr, uid, [('name','=',section)])
                    if not section_ids:
                        section_id = section_obj.create(cr, uid, {'name':section,'code':section,'department_id':department_id})
                    else:
                        section_id = section_ids[0]
                    
                    epf_no = sh.cell(row, 22).value
                    esi_no = sh.cell(row, 23).value
                    esi_dis = sh.cell(row, 24).value
                    pen_no = sh.cell(row, 25).value
                    statutory_arr = [(0,0,{'name':epf_no,'esi_no':esi_no,'esi_dispensary':esi_dis,'pension_no':pen_no})]
                    
#                     bank_country = sh.cell(row, 27).value
#                     bank_country_ids = country_obj.search(cr, uid, [('code','=',bank_country)])
#                     if not bank_country_ids:
#                         bank_country_id = country_obj.create(cr, uid, {'name':bank_country,'code':bank_country})
#                     else:
#                         bank_country_id = bank_country_ids[0]
#                     
#                     bank_name = sh.cell(row, 26).value
#                     bank_ids = bank_obj.search(cr, uid, [('name','=',bank_name),('country','=',bank_country_id)])
#                     if not bank_ids:
#                         bank_id = bank_obj.create(cr, uid, {'name':bank_name,'country':bank_country_id})
#                     else:
#                         bank_id = bank_ids[0]
                    
                    bank_acc = sh.cell(row, 28).value
#                     bank_acc_ids = bank_acc_obj.search(cr, uid, [('acc_number','=',bank_acc),('bank','=',bank_id)])
#                     if not bank_acc_ids:
#                         partner_id = partner_obj.create(cr, uid, {'name':sh.cell(row, 1).value})
#                         bank_acc_id = bank_acc_obj.create(cr, uid, {'acc_number':bank_acc,'bank':bank_id,'partner_id':partner_id,'state': "bank"})
#                     else:
#                         bank_acc_id = bank_acc_ids[0]
                    
                    plant = sh.cell(row, 29).value
                    plant_ids = plant_obj.search(cr, uid, [('code','=',plant)])
                    if not plant_ids:
                        plant_id = plant_obj.create(cr, uid, {'name':plant,'code':plant})
                    else:
                        plant_id = plant_ids[0]
                         
                    employee_code = sh.cell(row, 0).value
                    dem += 1
                    employee_obj.create(cr, uid, {
                        'employee_id': employee_code,
                        'name': sh.cell(row, 1).value,
                        'last_name': sh.cell(row, 2).value,
                        'employee_category_id': category_id,
                        'employee_sub_category_id': sub_category_id,
                        'city': sh.cell(row, 5).value,
                        'zip': sh.cell(row, 6).value,
                        'active': is_active,
                        'payroll_area_id': payroll_area_id,
                        'time_record': employee_code,
                        'job_id': job_id,
                        'birthday': birth,
                        'time_record': str(sh.cell(row, 10).value),
                        'country_stateofbirth_id': country_id,
                        'place_of_birth': state_id,
                        'birth_place': sh.cell(row, 15).value,
                        'religion_id': religion_id,
                        'marital': marital,
                        'date_of_wedding': wedding,
                        'department_id': department_id,
                        'section_id': section_id,
                        'statutory_ids': statutory_arr,
#                         'bank_account_id':bank_acc_id,
                        'bank_account':bank_acc,
                        'plant_id':plant_id,
                    })
                    
#                     epf_no = sh.cell(row, 22).value
#                     esi_no = sh.cell(row, 23).value
#                     esi_dis = sh.cell(row, 24).value
#                     pen_no = sh.cell(row, 25).value
#                     statutory_ids = statutory_obj.search(cr, uid, [('name','=',epf_no),('employee_id','=',emp_new_id)])
#                     if not statutory_ids:
#                         statutory_id = statutory_obj.create(cr, uid, {'name':epf_no,'esi_no':esi_no,'esi_dispensary':esi_dis,'pension_no':pen_no,'employee_id':emp_new_id})
#                     else:
#                         statutory_id = statutory_ids[0]
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_employee()
    
class tpt_import_employee_family(osv.osv):
    _name = 'tpt.import.employee.family'
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
            super(tpt_import_employee_family, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_employee_family, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_employee_family(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            employee_obj = self.pool.get('hr.employee')
            emp_family_obj = self.pool.get('hr.family')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    emp_code = sh.cell(row, 0).value
                    employee_ids = employee_obj.search(cr, uid, [('employee_id','=',str(emp_code))])
                    if not employee_ids:
                        raise osv.except_osv(_('Warning!'), ' Line: '+str(dem+1))
                    else:
                        emp_id = employee_ids[0]
                         
                    member_name = sh.cell(row, 1).value
                    
                    relation = sh.cell(row, 2).value
                    if relation == 'Father':
                        relation_type = 'father'
                    elif relation == 'Mother':
                        relation_type = 'mother'
                    elif relation == 'Spouse':
                        relation_type = 'spouse'
                    elif relation == 'Sibling':
                        relation_type = 'sibling'
                    elif relation == 'Child':
                        relation_type = 'child'
                    elif relation == 'Other':
                        relation_type = 'other'
                    else:
                        relation_type = False
                    
                    birth = sh.cell(row, 3).value
                    if birth:
                        birthdate = birth[6:10] + '-' + birth[3:5] + '-'+ birth[:2]
                    else:
                        birthdate = False
                    
                    gen = sh.cell(row, 5).value
                    if gen:
                       if gen == 'Female':
                        gender = 'female'
                    elif gen == 'Male':
                        gender = 'male' 
                    else:
                        gender = False
                        
                    employee_code = sh.cell(row, 0).value
                    dem += 1
                    emp_family_obj.create(cr, uid, {
                        'name': member_name,
                        'employee_id': emp_id,
                        'relation_type': relation_type,
                        'date_of_birth': birthdate,
                        'gender': gender,
                    })
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_employee_family()

class tpt_import_payroll(osv.osv):
    _name = 'tpt.import.payroll'
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
            super(tpt_import_payroll, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_payroll, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_payroll(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            employee_obj = self.pool.get('hr.employee')
            pay_emp_stru_obj = self.pool.get('arul.hr.payroll.employee.structure')
            pay_earn_obj = self.pool.get('arul.hr.payroll.earning.parameters')
            try:
                dem = 1
                for row in range(1,sh.nrows):
    #                     earning_arr = []
                    emp_code = sh.cell(row, 0).value
                    emp_code_char = str(int(emp_code))
                    sql = '''
                        select id, employee_category_id, employee_sub_category_id from hr_employee where employee_id = '%s'
                    '''%(emp_code_char)
                    cr.execute(sql)
                    employee_ids = cr.dictfetchone()
                    if not employee_ids:
                        raise osv.except_osv(_('Warning!'), ' Line: '+str(dem+1))
                    else:
                        emp_id = employee_ids['id']
                        emp_cate = employee_ids['employee_category_id'] or False
                        emp_sub = employee_ids['employee_sub_category_id'] or False
                    earning_arr = []
                    join = sh.cell(row, 1).value
                    if join:
                        join_day = join[6:10] + '-' + join[3:5] + '-'+ join[:2]
                    else:
                        join_day = False
                    employee_obj.write(cr, uid, [emp_id], {'date_of_joining':join_day})
                    basic = sh.cell(row, 2).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"BASIC")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':basic}))
                        
                    da = sh.cell(row, 3).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"DA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':da}))
                    
                    hra = sh.cell(row, 4).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"HRA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':hra}))
                    
                    convey = sh.cell(row, 5).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"C")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':convey}))
                    
                    lunch_all = sh.cell(row, 6).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"LA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':lunch_all}))
                    
                    edu_all = sh.cell(row, 7).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"EA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':edu_all}))
                        
                    admin_all = sh.cell(row, 8).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"AA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':admin_all}))
                        
                    other_all = sh.cell(row, 9).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"OA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':other_all}))
                        
                    special_all = sh.cell(row, 10).value
                    pay_earn_ids = pay_earn_obj.search(cr, uid, [('code','=',"SpA")])
                    if pay_earn_ids:
                        pay_earn_id = pay_earn_ids[0]
                        earning_arr.append((0,0,{'earning_parameters_id':pay_earn_id,'float':special_all}))
                    
                    dem += 1
                    pay_emp_stru_obj.create(cr, uid, {
                        'employee_id': emp_id,
                        'employee_category_id': emp_cate,
                        'sub_category_id': emp_sub,
                        'payroll_earning_structure_line': earning_arr,
                    })
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_payroll()

class tpt_import_employee_history(osv.osv):
    _name = 'tpt.import.employee.history'
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
            super(tpt_import_employee_history, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_employee_history, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_employee_history(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            
            action_obj = self.pool.get('arul.employee.actions')
            action_type_obj = self.pool.get('arul.employee.action.type')
            employee_obj = self.pool.get('hr.employee')
            season_obj = self.pool.get('arul.season')
            user_obj = self.pool.get('res.users')
            department_obj = self.pool.get('hr.department')
            designation_obj = self.pool.get('hr.job')
            employee_category_obj = self.pool.get('vsis.hr.employee.category')
            sub_category_obj = self.pool.get('hr.employee.sub.category')
            payroll_area_obj = self.pool.get('arul.hr.payroll.area')
            payroll_sub_area_obj = self.pool.get('arul.hr.payroll.sub.area')
            employee_history_obj = self.pool.get('arul.hr.employee.action.history')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    action = sh.cell(row, 0).value
                    action_ids = action_obj.search(cr, uid, [('name','=',action)])
                    if not action_ids:
                        raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Action '+action+' does not exist!')
                    else:
                        action_id = action_ids[0]
                        
                    action_type = sh.cell(row, 1).value
                    action_type_ids = action_type_obj.search(cr, uid, [('name','=',action_type)])
                    if not action_type_ids:
                        raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Action Type '+action_type+' does not exist!')
                    else:
                        action_type_id = action_type_ids[0]
                        
                    employee = sh.cell(row, 2).value
                    if employee:
                        employee_ids = employee_obj.search(cr, uid, [('employee_id','=',employee)])
                        if not employee_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Employee '+employee+' does not exist!')
                        else:
                            employee_id = employee_ids[0]
                    else:
                        employee_id = False
                    
                    firstname = sh.cell(row, 3).value
                    if firstname:
                        first_name = firstname
                    else:
                        first_name = False
                        
                    lastname = sh.cell(row, 4).value
                    if lastname:
                        last_name = lastname
                    else:
                        last_name = False
                        
                    actiondate = sh.cell(row, 5).value
                    if actiondate:
                        action_date = actiondate[6:10] + '-' + actiondate[3:5] + '-'+ actiondate[:2]
                    else:
                        action_date = False
                        
                    createdate = sh.cell(row, 6).value
                    if createdate:
                        create_date = createdate[6:10] + '-' + createdate[3:5] + '-'+ createdate[:2]+createdate[10:]
                    else:
                        create_date = False
                        
                    create_by = sh.cell(row, 7).value
                    user_ids = user_obj.search(cr, uid, [('name','=',create_by)])
                    if not user_ids:
                        raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' User '+user+' does not exist!')
                    else:
                        user_id = user_ids[0]
                        
                    periodfrom = sh.cell(row, 8).value
                    if periodfrom:
                        period_from = periodfrom[6:10] + '-' + periodfrom[3:5] + '-'+ periodfrom[:2]
                    else:
                        period_from = False
                        
                    periodto = sh.cell(row, 9).value
                    if periodto:
                        period_to = periodto[6:10] + '-' + periodto[3:5] + '-'+ periodto[:2]
                    else:
                        period_to = False
                        
                    reason = sh.cell(row, 10).value
                    if reason:
                        season_ids = season_obj.search(cr, uid, [('season_id','=',season)])
                        if not season_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Season '+season+' does not exist!')
                        else:
                            season_id = season_ids[0]
                    else:
                        reason_id = False
                        
                    note = sh.cell(row, 11).value
                    
                    department_from = sh.cell(row, 12).value
                    if department_from:
                        department_from_ids = department_obj.search(cr, uid, [('name','=',department_from)])
                        if not department_from_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Department '+department_from+' does not exist!')
                        else:
                            department_from_id = department_from_ids[0]
                    else:
                        department_from_id = False
                        
                    department_to = sh.cell(row, 13).value
                    if department_to:
                        department_to_ids = department_obj.search(cr, uid, [('name','=',department_to)])
                        if not department_to_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Department '+department_to+' does not exist!')
                        else:
                            department_to_id = department_to_ids[0]
                    else:
                        department_to_id = False
                    
                    designation_from = sh.cell(row, 14).value
                    if designation_from:
                        designation_from_ids = designation_obj.search(cr, uid, [('name','=',designation_from)])
                        if not designation_from_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Designation '+designation_from+' does not exist!')
                        else:
                            designation_from_id = designation_from_ids[0]
                    else:
                        designation_from_id = False
                        
                    designation_to = sh.cell(row, 15).value
                    if designation_to:
                        designation_to_ids = designation_obj.search(cr, uid, [('name','=',designation_to)])
                        if not designation_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Designation '+designation_to+' does not exist!')
                        else:
                            designation_to_id = designation_to_ids[0]
                    else:
                        designation_to_id = False
                        
                    employee_category = sh.cell(row, 16).value
                    if employee_category:
                        employee_category_ids = employee_category_obj.search(cr, uid, [('code','=',employee_category)])
                        if not employee_category_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Employee Category '+employee_category+' does not exist!')
                        else:
                            employee_category_id = employee_category_ids[0]
                    else:
                        employee_category_id = False
                        
                    sub_category = sh.cell(row, 17).value
                    if sub_category:
                        sub_category_ids = sub_category_obj.search(cr, uid, [('code','=',sub_category)])
                        if not sub_category_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Employee Sub Category '+sub_category+' does not exist!')
                        else:
                            sub_category_id = sub_category_ids[0]
                    else:
                        sub_category_id = False
                        
                    payroll_area = sh.cell(row, 18).value
                    if payroll_area:
                        payroll_area_ids = payroll_area_obj.search(cr, uid, [('code','=',payroll_area)])
                        if not payroll_area_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Payroll Area '+payroll_area+' does not exist!')
                        else:
                            payroll_area_id = payroll_area_ids[0]
                    else:
                        payroll_area_id = False
                        
                    payroll_sub_area = sh.cell(row, 19).value
                    if payroll_sub_area:
                        payroll_sub_area_ids = payroll_sub_area_obj.search(cr, uid, [('code','=',payroll_sub_area)])
                        if not payroll_sub_area_ids:
                            raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Payroll Sub Area '+payroll_sub_area+' does not exist!')
                        else:
                            payroll_sub_area_id = payroll_sub_area_ids[0]
                    else:
                        payroll_sub_area_id = False
                        
                    current_monthsalary = sh.cell(row, 20).value
                    if current_monthsalary:
                        if current_monthsalary=='Y':
                            current_month_salary = True
                        else:
                            current_month_salary = False
                    else:
                        current_month_salary = False
                        
                    plencashment = sh.cell(row, 21).value
                    if plencashment:
                        if plencashment=='Y':
                            pl_encashment = True
                        else:
                            pl_encashment = False
                    else:
                        pl_encashment = False
                        
                    coff = sh.cell(row, 22).value
                    if coff:
                        if coff=='Y':
                            c_off = True
                        else:
                            c_off = False
                    else:
                        c_off = False
                        
                    bonus_val = sh.cell(row, 23).value
                    if bonus_val:
                        if bonus_val=='Y':
                            bonus = True
                        else:
                            bonus = False
                    else:
                        bonus = False
                        
                    medicalreimbursement = sh.cell(row, 24).value
                    if medicalreimbursement:
                        if medicalreimbursement=='Y':
                            medical_reimbursement = True
                        else:
                            medical_reimbursement = False
                    else:
                        medical_reimbursement = False
                        
                    gratuity_val = sh.cell(row, 25).value
                    if gratuity_val:
                        if gratuity_val=='Y':
                            gratuity = True
                        else:
                            gratuity = False
                    else:
                        gratuity = False
                        
                    pfsettlement = sh.cell(row, 26).value
                    if pfsettlement:
                        if pfsettlement=='Y':
                            pf_settlement = True
                        else:
                            pf_settlement = False
                    else:
                        pf_settlement = False
                    
                    dem += 1
                    if employee_id:
                        employee_history_obj.create(cr, uid, {
                            'employee_id': employee_id,
                            'first_name': first_name,
                            'last_name': last_name,
                            'action_id': action_id,
                            'action_type_id': action_type_id,
                            'action_date': action_date,
                            'create_date': create_date,
                            'create_uid': create_uid,
                            'period_from': period_from,
                            'period_to': period_to,
                            'reason_id': reason_id,
                            'note': note,
                            'department_from_id': department_from_id,
                            'department_to_id': department_to_id,
                            'designation_from_id': designation_from_id,
                            'designation_to_id': designation_to_id,
                            'employee_category_id': employee_category_id,
                            'sub_category_id': sub_category_id,
                            'employee_category_id': employee_category_id,
                            'payroll_area_id': payroll_area_id,
                            'payroll_sub_area_id': payroll_sub_area_id,
                            'current_month_salary': current_month_salary,
                            'pl_encashment': pl_encashment,
                            'c_off': c_off,
                            'bonus': bonus,
                            'medical_reimbursement': medical_reimbursement,
                            'gratuity': gratuity,
                            'pf_settlement': pf_settlement,
                        })
                    else:
                        raise osv.except_osv(_('Warning!'),'Line: '+str(dem+1)+' Employee '+employee+' does not exist!')
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_employee_history()

class tpt_import_leave_balance(osv.osv):
    _name = 'tpt.import.leave.balance'
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
            super(tpt_import_leave_balance, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_leave_balance, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'year': fields.char('Import for Year',size=128, required=True),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        'year': time.strftime('%Y'),
    }
    
    def import_leave_balance(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            employee_obj = self.pool.get('hr.employee')
            employee_leave_obj = self.pool.get('employee.leave')
            leave_type_obj = self.pool.get('arul.hr.leave.types')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    emp_code = sh.cell(row, 1).value
                    emp_code_char = str(int(emp_code))
                    sql = '''
                        select id from hr_employee where employee_id = '%s'
                    '''%(emp_code_char)
                    cr.execute(sql)
                    employee_ids = [r[0] for r in cr.fetchall()]
                    if not employee_ids:
                        raise osv.except_osv(_('Warning!'), ' Line: '+str(dem+1))
                    emp_id = employee_ids[0]
                    year = this.year
                    cl = sh.cell(row, 4).value
                    sl = sh.cell(row, 5).value
                    pl = sh.cell(row, 6).value
                    coff = sh.cell(row, 7).value
                    
                    employee_leave_ids = employee_leave_obj.search(cr, uid, [('employee_id','=',emp_id),('year','=',year)])
                    if employee_leave_ids:
                        employee_leave_obj.unlink(cr, uid, employee_leave_ids)
                        
                    leave_type_cl_ids = leave_type_obj.search(cr, uid, [('code','=','CL')])
                    leave_type_sl_ids = leave_type_obj.search(cr, uid, [('code','=','SL')])
                    leave_type_pl_ids = leave_type_obj.search(cr, uid, [('code','=','PL')])
                    leave_type_coff_ids = leave_type_obj.search(cr, uid, [('code','=','C.Off')])
                    if not leave_type_cl_ids or not leave_type_sl_ids or not leave_type_pl_ids or not leave_type_coff_ids:
                        raise osv.except_osv(_('Warning!'), ' Line: '+str(dem+1))
                    dem += 1
                    employee_leave_obj.create(cr, uid, {
                        'employee_id': emp_id,
                        'year': year,
                        'emp_leave_details_ids': [
                              (0,0,{'leave_type_id':leave_type_cl_ids[0],'total_day':cl}),
                              (0,0,{'leave_type_id':leave_type_sl_ids[0],'total_day':sl}),
                              (0,0,{'leave_type_id':leave_type_pl_ids[0],'total_day':pl}),
                              (0,0,{'leave_type_id':leave_type_coff_ids[0],'total_day':coff}),
                         ],
                    })
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_leave_balance()

class tpt_import_customer(osv.osv):
    _name = 'tpt.import.customer'
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
            super(tpt_import_customer, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_customer, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Customer', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_customer(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            partner_obj = self.pool.get('res.partner')
            country_obj = self.pool.get('res.country')
            state_obj = self.pool.get('res.country.state')
            country_obj = self.pool.get('res.country')
            state_obj = self.pool.get('res.country.state')
            account_obj = self.pool.get('customer.account.group')
#             tax_number_1_obj = self.pool.get('tax.number.1')
            payment_obj = self.pool.get('account.payment.term')
            tax_category_obj = self.pool.get('tax.category')
            tax_classification_obj = self.pool.get('tax.classification')
            title_obj = self.pool.get('res.partner.title')
            currency_obj = self.pool.get('res.currency')
            incoterms_obj = self.pool.get('stock.incoterms')
            dischannel_obj = self.pool.get('crm.case.channel')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    country = sh.cell(row, 1).value
                    country_ids = country_obj.search(cr, uid, [('code','=',country)])
                    if not country_ids:
                        country_id = country_obj.create(cr, uid, {'name':country,'code':country})
                    else:
                        country_id = country_ids[0]
                    
                    state = sh.cell(row, 5).value # Region
                    state_ids = state_obj.search(cr, uid, [('code','=',state),('country_id','=',country_id)])
                    if not state_ids:
                        state_id = state_obj.create(cr, uid, {'name':state,'code':state,'country_id':country_id})
                    else:
                        state_id = state_ids[0]
                    
                    title = sh.cell(row, 10).value
                    title_ids = title_obj.search(cr, uid, [('name','=',title)])
                    if not title_ids:
                        title_id = title_obj.create(cr, uid, {'name':title})
                    else:
                        title_id = title_ids[0]
                    
                    account = sh.cell(row, 22).value #Customer Account Group
                    account_ids = account_obj.search(cr, uid, [('code','=',account)])
                    if not account_ids:
                        account_id = account_obj.create(cr, uid, {'name':account,'code':account})
                    else:
                        account_id = account_ids[0]
                        
#                     tax_number_1 = sh.cell(row, 12).value
#                     tax_number_1_ids = tax_number_1_obj.search(cr, uid, [('code','=',tax_number_1)])
#                     if not tax_number_1_ids:
#                         tax_number_1_id = tax_number_1_obj.create(cr, uid, {'code':tax_number_1,'name':tax_number_1})
#                     else:
#                         tax_number_1_id = tax_number_1_ids[0]
                        
                    payment = sh.cell(row, 23).value
                    payment_ids = payment_obj.search(cr, uid, [('name','=',payment)])
                    if not payment_ids:
                        payment_id = payment_obj.create(cr, uid, {'name':payment})
                    else:
                        payment_id = payment_ids[0]
                        
                    tax_category = sh.cell(row, 25).value
                    tax_category_ids = tax_category_obj.search(cr, uid, [('code','=',tax_category)])
                    if not tax_category_ids:
                        tax_category_id = tax_category_obj.create(cr, uid, {'code':tax_category,'name':tax_category})
                    else:
                        tax_category_id = tax_category_ids[0]
                    
                    tcs_id = 0
                    tcs = sh.cell(row, 26).value
                    if tcs:
                        tcs_ids = tax_category_obj.search(cr, uid, [('code','=',tcs)])
                        if not tcs_ids:
                            tcs_id = tax_category_obj.create(cr, uid, {'code':tcs,'name':tcs})
                        else:
                            tcs_id = tcs_ids[0]
                    
                    curr = sh.cell(row, 30).value
                    curr_ids = currency_obj.search(cr, uid, [('name','=',curr)])
                    if not curr_ids:
                        curr_id = currency_obj.create(cr, uid, {'name':curr})
                    else:
                        curr_id = curr_ids[0]
                    
                    cus_type1 = 0    
                    cus_type = sh.cell(row, 28).value
                    if cus_type=='Export':
                          cus_type1 = 'export'
                    if cus_type=='Indirect Export':
                          cus_type1 = 'indirect_export'
                    if cus_type=='Domestic':
                          cus_type1 = 'domestic'
                    
                    inco_id = 0      
                    inco = sh.cell(row, 29).value
                    inco_ids = incoterms_obj.search(cr, uid, [('code','=',inco)])
                    if  inco_ids:                   
                        inco_id = inco_ids[0]
                    
                    channel_name = sh.cell(row, 27).value
                    channel_ids = dischannel_obj.search(cr, uid, [('name','=',channel_name)])
                    if not channel_ids:
                        channel_id = dischannel_obj.create(cr, uid, {'name':channel_name})
                    else:
                        channel_id = channel_ids[0]
                            
#                     tax_classification = sh.cell(row, 16).value
#                     tax_classification_ids = tax_classification_obj.search(cr, uid, [('code','=',tax_classification)])
#                     if not tax_classification_ids:
#                         tax_classification_id = tax_classification_obj.create(cr, uid, {'code':tax_classification,'name':tax_classification})
#                     else:
#                         tax_classification_id = tax_classification_ids[0]
                        
                        ##############################################    
                    #TPT
                    sql = '''
                    select count(*) from res_partner where customer_code = '%s'                   
                    '''%(sh.cell(row, 0).value)
                    cr.execute(sql)
                    q_fetch = cr.fetchone()
                    exist_custo_count = q_fetch[0]
                    
                    if exist_custo_count > 0:                         
                        dem += 1                        
                        sql = '''
                        select id from res_partner where customer_code = '%s'                   
                        '''%(sh.cell(row, 0).value)
                        cr.execute(sql)
                        id = cr.fetchone()
                        exist_custo_id = id[0]
                    
                        partner_obj.write(cr, uid,exist_custo_id, {
                        #'customer_code': sh.cell(row, 0).value or False,
                        'country_id': country_id,
                        #'name': sh.cell(row, 2).value,
                        #'last_name': sh.cell(row, 3).value or False,
                        'city': sh.cell(row, 3).value or False,
                        'zip': sh.cell(row, 4).value or False,
                        'state_id':state_id or False,
                        'street': sh.cell(row, 7).value or False,
                        'phone': sh.cell(row, 8).value or False,
                        'fax': sh.cell(row, 9).value or False,
                        'title': title_id or False,                                            
                                        
                        'tin': sh.cell(row, 11).value or False,
                        'contact_per':sh.cell(row, 12).value or False,
                        'ecc':sh.cell(row, 13).value or False,
                        'excise_reg_no':sh.cell(row, 14).value or False,
                        'range':sh.cell(row, 15).value or False,
                        'division':sh.cell(row, 16).value or False,
                        'commissionerate':sh.cell(row, 17).value or False,                                             
                        'cst': sh.cell(row, 18).value or False,
                        'lst': sh.cell(row, 19).value or False,
                        'pan_tin':sh.cell(row, 20).value or False,                       
                        'service_reg_no': sh.cell(row, 21).value or False,
                        'customer_account_group_id': account_id or False,    # 22
                        'property_payment_term':payment_id or False,  #23
                        'credit_limit_used':sh.cell(row, 24).value or False,                        
                        'tax_category_id': tax_category_id or False, #25 
                        'tcs': tcs_id or False, #26
                        'distribution_channel': channel_id or False, #27                   
                        'arulmani_type': cus_type1 or False, #28 CGroup
                        'inco_terms_id': inco_id or False, #29 
                        'currency_id': curr_id or False, #29 
#                         'tax_classification_id': tax_classification_id or False,
                        
                        },context)
                        
                    #TPT                     
                    else :
                        dem += 1
                        partner_obj.create(cr, uid, {
                        'customer_code': sh.cell(row, 0).value or False,                  
                        'name': sh.cell(row, 2).value,
                        'last_name': sh.cell(row, 3).value or False,
                        'country_id': country_id,
                        #'name': sh.cell(row, 2).value,
                        #'last_name': sh.cell(row, 3).value or False,
                        'city': sh.cell(row, 3).value or False,
                        'zip': sh.cell(row, 4).value or False,
                        'state_id':state_id or False,
                        'street': sh.cell(row, 7).value or False,
                        'phone': sh.cell(row, 8).value or False,
                        'fax': sh.cell(row, 9).value or False,
                        'title': title_id or False,                                            
                        'tin': sh.cell(row, 11).value or False,
                        'contact_per':sh.cell(row, 12).value or False,
                        'ecc':sh.cell(row, 13).value or False,
                        'excise_reg_no':sh.cell(row, 14).value or False,
                        'range':sh.cell(row, 15).value or False,
                        'division':sh.cell(row, 16).value or False,
                        'commissionerate':sh.cell(row, 17).value or False,                                             
                        'cst': sh.cell(row, 18).value or False,
                        'lst': sh.cell(row, 19).value or False,
                        'pan_tin':sh.cell(row, 20).value or False,                       
                        'service_reg_no': sh.cell(row, 21).value or False,
                        'customer_account_group_id': account_id or False,    # 22
                        'property_payment_term':payment_id or False,  #23
                        'credit_limit_used':sh.cell(row, 24).value or False,                        
                        'tax_category_id': tax_category_id or False, #25 
                        'tcs': tcs_id or False, #26
                        'distribution_channel': channel_id or False, #27                   
                        'arulmani_type': cus_type1 or False, #28 CGroup
                        'inco_terms_id': inco_id or False, #29 
                        'currency_id': curr_id or False, #29 
#                         'tax_classification_id': tax_classification_id or False,
                        'is_company': True,
                        'customer': True,
                    })
                    
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_customer()


#Start:TPT
class tpt_import_meals_deduction(osv.osv):
    _name = 'tpt.import.meals.deduction'    
    
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
            super(tpt_import_meals_deduction, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_meals_deduction, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True    


    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }

    def import_meals_deduction(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            #employee_obj = self.pool.get('hr.employee')
            #details_obj = self.pool.get('meals.details')
            deduction_obj = self.pool.get('meals.deduction')
            details_obj = self.pool.get('meals.details')
            #food_subsidy_obj = self.pool.get('food.subsidy')            
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    meals_date = sh.cell(row, 0).value
                    if meals_date:
                        mealsdate = meals_date[6:10] + '-' + meals_date[3:5] + '-'+ meals_date[:2]                          
                    else:
                        mealsdate = False
                   
                    #getting meals-for from xls 
                    mealsfor = sh.cell(row, 1).value 
                    if mealsfor:
                        if mealsfor=='Employees':
                            mealsfor = 'employees'
                        else:
                            mealsfor = 'others'
                    else:
                        mealsfor = 'employees'    
               
                    #Create Meals Dedution            
                    deduction_obj.create(cr, uid, {
                        'meals_date': mealsdate,
                        'meals_for': mealsfor
            #'meals_details_order_ids': [
                        #      (0,0,{'break_fast':m_bfast,'lunch':m_lunch,'dinner':m_dinner,'midnight_tiffin':m_midtiffen,'emp_id':emp_id}),
                              
                       #  ],
                        
                    }) 

                      
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})


tpt_import_meals_deduction()


class tpt_import_meals_details(osv.osv):
    _name = 'tpt.import.meals.details'    
    
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
            super(tpt_import_meals_details, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_meals_details, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True    


    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }

    def import_meals_details(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            #employee_obj = self.pool.get('hr.employee')
            #details_obj = self.pool.get('meals.details')
            deduction_obj = self.pool.get('meals.deduction')
            details_obj = self.pool.get('meals.details')
            #food_subsidy_obj = self.pool.get('food.subsidy')            
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    meals_date = sh.cell(row, 1).value
                    if meals_date:
                        mealsdate = meals_date[6:10] + '-' + meals_date[3:5] + '-'+ meals_date[:2]                          
                    else:
                        mealsdate = False
                   
        
                        #getting meals-for from xls
                    emp_code = sh.cell(row, 0).value
                    emp_code_char = str(int(emp_code))
                    sql = '''
                        select id from hr_employee where employee_id = '%s'
                    '''%(emp_code_char)
                    cr.execute(sql)
                    employee_ids = [r[0] for r in cr.fetchall()]
                    if not employee_ids:
                        raise osv.except_osv(_('Warning!'), ' Line: '+str(dem+1))
                    emp_id = employee_ids[0]

                    bfast = sh.cell(row, 2).value
                    if bfast:
                        if bfast=='Y':
                            m_bfast = True
                        else:
                            m_bfast = False
                    else:
                        m_bfast = False
                    lunch = sh.cell(row, 3).value
                    if lunch:
                        if lunch=='Y':
                            m_lunch = True
                        else:
                            m_lunch = False
                    else:
                        m_lunch = False
                    dinner = sh.cell(row, 4).value
                    if dinner:
                        if dinner=='Y':
                            m_dinner = True
                        else:
                            m_dinner = False
                    else:
                        m_dinner = False
                    midtiffen = sh.cell(row, 5).value
                    if midtiffen:
                        if midtiffen=='Y':
                            m_midtiffen = True
                        else:
                            m_midtiffen = False
                    else:
                        m_midtiffen = False
                    
                    sql1 = '''select id from meals_deduction where meals_date ='%s' '''%mealsdate
                    sql2 = '''select meals_date from meals_deduction where meals_date ='%s' '''%mealsdate
                    cr.execute(sql1)
                    melasid= cr.fetchone()
                    cr.execute(sql2)
                    melas_date= cr.fetchone()
                    if melas_date != mealsdate:    
                    #Create Meals Dedution            
                        details_obj.create(cr, uid, {
                        'break_fast':m_bfast,
                        'lunch':m_lunch,
                        'dinner':m_dinner,
                        'midnight_tiffin':m_midtiffen,
                        'emp_id':emp_id,
                        'meals_id':melasid
                  
                        }) 

                      
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})


tpt_import_meals_details()



#End:TPT

###TPT-CANTEEN

class tpt_import_canteen_details(osv.osv):
    _name = 'tpt.import.canteen.details'    
    
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
            super(tpt_import_canteen_details, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_canteen_details, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True    


    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Employee', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }

    def import_canteen_details(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            details_obj = self.pool.get('tpt.canteen.deduction')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    emp_code = sh.cell(row, 0).value
                    emp_code_char = str(int(emp_code))
                    sql = '''
                        select id from hr_employee where employee_id = '%s'
                    '''%(emp_code_char)
                    cr.execute(sql)
                    employee_ids = [r[0] for r in cr.fetchall()]
                    if not employee_ids:
                        raise osv.except_osv(_('Warning!'), ' Line: '+str(dem+1))
                    emp_id = employee_ids[0]
                    
                    bfast_count = 0
                    lunch_count = 0
                    dinner_count = 0
                    night_tiffin_count = 0
                    non_veg_count = 0
                    omlette_count = 0
                    
                    book_obj = self.pool.get('tpt.canteen.book.type')
                      
            
                    bfast = sh.cell(row, 1).value 
                    if len(str(bfast))>=1:                       
                        no_of_book = 1
                        type_id = book_obj.search(cr, uid, [('name','=','Breakfast')])
                        breakfast_id = book_obj.browse(cr,uid,type_id[0])
                        book_type_id = breakfast_id.id 
                        
                        details_obj.create(cr, uid, {
                        'employee_id':emp_id,
                        'book_type_id':book_type_id,
                        'no_of_book':no_of_book,

                        }) 
                   
                    lunch = sh.cell(row, 2).value
                    if len(str(lunch))>=1:
                        #print "TEST:",len(str(lunch))
                        no_of_book = 1
                        type_id = book_obj.search(cr, uid, [('name','=','Lunch')])
                        breakfast_id = book_obj.browse(cr,uid,type_id[0])
                        book_type_id = breakfast_id.id 
                        details_obj.create(cr, uid, {
                        'employee_id':emp_id,
                        'book_type_id':book_type_id,
                        'no_of_book':no_of_book,

                        }) 

                    night_tiffin = sh.cell(row, 3).value
                    if len(str(night_tiffin))>=1:
                        no_of_book = 1
                        type_id = book_obj.search(cr, uid, [('name','=','Night tiffin')])
                        breakfast_id = book_obj.browse(cr,uid,type_id[0])
                        book_type_id = breakfast_id.id 
                        details_obj.create(cr, uid, {
                        'employee_id':emp_id,
                        'book_type_id':book_type_id,
                        'no_of_book':no_of_book,

                        }) 
                      
                    nonveg = sh.cell(row, 4).value
                    if len(str(nonveg))>=1:
                        non_veg_count = 1
                        type_id = book_obj.search(cr, uid, [('name','=','Non Veg')])
                        breakfast_id = book_obj.browse(cr,uid,type_id[0])
                        book_type_id = breakfast_id.id 
                        details_obj.create(cr, uid, {
                        'employee_id':emp_id,
                        'book_type_id':book_type_id,
                        'no_of_book':no_of_book,

                        }) 
                        
                    omlette = sh.cell(row, 5).value
                    if len(str(omlette))>=1:
                        no_of_book = 1
                        type_id = book_obj.search(cr, uid, [('name','=','Omlette')])
                        breakfast_id = book_obj.browse(cr,uid,type_id[0])
                        book_type_id = breakfast_id.id 
                        details_obj.create(cr, uid, {
                        'employee_id':emp_id,
                        'book_type_id':book_type_id,
                        'no_of_book':no_of_book,

                        }) 
                    ###
                       
   
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})


tpt_import_canteen_details()


###TPT-CANTEEN

