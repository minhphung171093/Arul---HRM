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
    