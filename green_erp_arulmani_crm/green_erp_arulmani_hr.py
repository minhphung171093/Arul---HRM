# -*- coding: utf-8 -*-
import openerp
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from datetime import datetime, date, timedelta #TPT
import parser #TPT



class hr_employee(osv.osv):
    _inherit = "hr.employee"
    
    def create(self, cr, user, vals, context=None):
        if 'employee_id' not in vals:
            vals['employee_id']= self.pool.get('ir.sequence').get(cr, user, 'hr.employee.id')
        new_id = super(hr_employee, self).create(cr, user, vals, context)
        return new_id
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['employee_id','name','last_name'], context=context)
        res = []
        for record in reads:
            if record['employee_id']:
                name = '['+record['employee_id']+']'+record['name']+ ' ' + (record['last_name'] and record['last_name'] or'')
            else:
                name = record['name']+ ' ' + (record['last_name'] and record['last_name'] or'') 
            res.append((record['id'], name))
        return res
  
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:] 
        ids = []
        
        if name:
            ids = self.search(cr, user, ['|',('last_name', operator, name),('name', operator, name)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)     
        return self.name_get(cr, user, ids, context=context)
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}
    def onchange_permanent_state_id(self, cr, uid, ids, permanent_state_id, context=None):
        if permanent_state_id:
            permanent_country_id = self.pool.get('res.country.state').browse(cr, uid, permanent_state_id, context).country_id.id
            return {'value':{'permanent_country_id':permanent_country_id}}
        return {}
    #===========================================================================
    # #TPT Starts
    # def _age_yrs(self, cr, uid, ids, date_of_birth, args=None, context=None):                
    #     
    #     current_date=datetime.now()
    #     current_year=current_date.year
    #     #birth_date = parser.parse(age_in_years)
    #     date = datetime(year=int(age_in_years[0:4]), month=int(age_in_years[4:6]), day=int(age_in_years[6:8]))        
    #     current_age=current_year-age_in_years.year
    #     age_in_yrs = {
    #         'age_in_yrs':current_age
    #     }
    #     return {'value':{'age_in_yrs':age_in_yrs}}
    # #TPT End
    #===========================================================================

        
        
        
   #TPT     
        
    def _age(self, cr, uid, ids, field_name, arg, context=None):
        res = {}        
        
        for emp in self.browse(cr, uid, ids, context=context):
            res[emp.id] = {
                'age_in_yrs': 0,
            }  
      
            if emp.birthday:
                dob = emp.birthday    
                b_date = datetime.strptime(dob, '%Y-%m-%d')
                datenew = str(datetime.today())            
                current_date = datetime.strptime(str(datetime.today()), '%Y-%m-%d %H:%M:%S.%f')            
                difference_in_days = ((current_date - b_date).days/365)
                
                res[emp.id]['age_in_yrs'] = difference_in_days 
           
        return res              
      #TPT          
                
                
    
    _columns = {
                'employee_id': fields.char('Employee ID',size=128,readonly=True,store=True),
                'plant_id' : fields.many2one('hr.plant', 'Plant',ondelete='restrict'),
                'date_of_joining' : fields.date('Date Of Joining'),  
                'age_in_years': fields.integer('Age In Years'),
                'age_in_yrs': fields.function(_age, string='Age in Yrs', multi='sums', help="Age."),
                'place_of_birth': fields.many2one('res.country.state','State Of Birth',ondelete='restrict'),
                'caste' : fields.char('Caste', size=128), 
                'religion_id': fields.many2one('hr.religion', 'Religion',ondelete='restrict'),
                'blood_group': fields.selection([('O+','O+'),
                                                 ('O-','O-'),
                                                 ('A+','A+'),
                                                 ('A-','A-'),
                                                 ('B+','B+'),
                                                 ('B-','B-'),
                                                 ('AB+','AB+'),
                                                 ('AB-','AB-'),
                                                 ('A1+','A1+'),
                                                 ('A1-','A1-'),
                                                 ('A1B+','A1B+'),
                                                 ('A1B-','A1B-'),
                                                 ('A2+','A2+'),
                                                 ('A2-','A2-'),
                                                 ('A2B+','A2B+'),
                                                 ('A2B-','A2B-'),
                                                 ('B1+','B1+'),
                                                  ],'Blood Group'),
                'physically_challenged' : fields.boolean('Physically Challenged'),
                'physically_challenged_note' : fields.text('Note'),
                'identities_ids': fields.one2many('hr.identities.attachment','employee_id','Identities Line'),
                'qualification_ids': fields.one2many('hr.qualification.attachment','employee_id','Qualification Line'),
                'experience_ids': fields.one2many('hr.experience','employee_id','Experience Summary'),
                'family_ids': fields.one2many('hr.family','employee_id','Family Details'),
                'last_name' : fields.char('Last Name', size=32),
                'date_of_resignation' : fields.date('Date Of Leaving'), 
                'employee_category_id' : fields.many2one('vsis.hr.employee.category', 'Employee Category', ondelete='restrict'),
                'employee_sub_category_id' : fields.many2one('hr.employee.sub.category', 'Employee Sub Category(Grade)',ondelete='restrict'),
                'employee_grade_id' : fields.many2one('hr.employee.grade', 'Employee Grade'),
                'street': fields.char('Street', size=128),
                'street2': fields.char('Street2', size=128),
                'zip': fields.char('Zip', change_default=True, size=24),
                'city': fields.char('City', size=128),
                'state_id': fields.many2one("res.country.state", 'State',ondelete='restrict'),
                'country_id': fields.many2one('res.country', 'Country',ondelete='restrict'),
                'is_different_permanent_address' : fields.boolean('Is Different Permanent Address?'),
                'permanent_street': fields.char('Street', size=128),
                'permanent_street2': fields.char('Street2', size=128),
                'permanent_zip': fields.char('Zip', change_default=True, size=24),
                'permanent_city': fields.char('City', size=128),
                'permanent_state_id': fields.many2one("res.country.state", 'State',ondelete='restrict'),
                'permanent_country_id': fields.many2one('res.country', 'Country',ondelete='restrict'),
                'date_of_wedding' : fields.date('Date Of Wedding'),
                'statutory_ids': fields.one2many('hr.statutory','employee_id','Statutory Details'),
                'basic' : fields.float('Basic'), 
                'conveyance' : fields.float('Conveyance'),
                'lunch_allowance' : fields.float('Lunch Allowance'),
                'special_allowance' : fields.float('Special Allowance'),
                'gross' : fields.float('Gross'),
                'mra' : fields.float('MRA'),
                'ctc' : fields.float('CTC'),
                'hra' : fields.float('HRA'),
                'education_allowance' : fields.float('Education Allowance'),
                'admin_allowance' : fields.float('Admin Allowance'),
                'other_allowance' : fields.float('Other Allowance'),
                'lta' : fields.float('LTA'),
                'bonus' : fields.float('Bonus'),
#                 'employee_active' : fields.boolean('Active'),
                'marital': fields.selection([('single', 'Single'), 
                                             ('married', 'Married'), 
                                             ('widower', 'Widower'),
                                             ('widow', 'Widow'),
                                             ('divorced', 'Divorced')
                                              ], 'Marital Status'),
                'write_date': fields.datetime('Updated Date',readonly = True),
                }
    _defaults = {
                 'active': True,
#         'employee_active': True,
    }
hr_employee()

class hr_religion(osv.osv):
    _name = "hr.religion"
    _order = "code"
    _description = "Religion"
    _columns = {
        'name' : fields.char('Name', 64, required=True),
        'code' : fields.char('Code', 64, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
    ]
    def copy(self, cr, uid, id, default={}, context=None, done_list=[], local=False):
        record = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default = default.copy()
        default['code'] = (record['code'] or '') + '(copy)'
        default['name'] = (record['name'] or '') + '(copy)'
        return super(hr_religion, self).copy(cr, uid, id, default, context=context)
hr_religion()

class hr_qualification_master(osv.osv):
    _name = "hr.qualification.master"
    _order = "code"
    _description = "Qualification Master"
    _columns = {
        'name' : fields.char('Name', 64, required=True),
        'code' : fields.char('Code', 9, required=True),
        'description' : fields.text('Description'),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
    ]
hr_qualification_master()
class hr_experience(osv.osv):
    _name = "hr.experience"
    _description = "Experience"
    _columns = {
        'company_ornganization' : fields.char('Company/Organization', size=128),
        'last_held_designation' : fields.char('Last Held Designation', size=128),
        'joining_date' : fields.date('Joining Date'),
        'relieving_date' : fields.date('Relieving Date'), 
        'last_drawn_salary': fields.float('Last Drawn Salary'),
        'employee_id': fields.many2one('hr.employee','Employee'),
    }
hr_experience()
class hr_family (osv.osv):
    _name = "hr.family"
    _description = "Family"
    _columns = {
        'name' : fields.char('Name', size=128   ),
        'relation_type': fields.selection([('father','Father'),('mother','Mother'),('spouse','Spouse'),('sibling','Sibling'),('child','Child'),('daughter','Daughter'),('son','Son'),('brother','Brother'),('sister','Sister'),('other','Other')],'Relation Type'),
        'date_of_birth' : fields.date('Date Of Birth'),
        'qualification' : fields.char('Qualification', size=128),
        'phone' : fields.char('Phone', size=128),
        'mobile' : fields.char('Mobile', size=128),
        'email' : fields.char('Email', size=128),
        'emergency_contact':fields.selection([('yes','Yes'),('no','No')],'Emergency Contact'),
        'employee_id': fields.many2one('hr.employee','Employee'),
        'gender': fields.selection([('female','Female'),('male','Male')],'Gender'),
    }
hr_family()

class hr_plant(osv.osv):
    _name = "hr.plant"
    _order = "code"
    _description = "Plant"
    _columns = {
        'name' : fields.char('Name', 64, required=True),
        'code' : fields.char('Code', 9, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
    ]
hr_plant()

class hr_employee_category(osv.osv):
    _name = "vsis.hr.employee.category"
    _order = "code"
    _description = "Employee Category"
    _columns = {
        'name' : fields.char('Name', 64, required=True),
        'code' : fields.char('Code', 9, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    def _check_code_id(self, cr, uid, ids, context=None):
        for category in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from vsis_hr_employee_category where id != %s and ( lower(code) = lower('%s') or lower(name) = lower('%s') )
            '''%(category.id,category.code,category.name)
            cr.execute(sql)
            category_ids = [row[0] for row in cr.fetchall()]
            if category_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
    
    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(hr_employee_category, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(hr_employee_category, self).write(cr, uid,ids, vals, context)
hr_employee_category()
class hr_employee_sub_category(osv.osv):
    _name = "hr.employee.sub.category"
    _order = "code"
    _description = "Employee Sub Category"
    _columns = {
        'name' : fields.char('Name', 64, required=True),
        'code' : fields.char('Code', 9, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }

    def create(self, cr, uid, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(hr_employee_sub_category, self).create(cr, uid, vals, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'code' in vals:
            name = vals['code'].replace(" ","")
            vals['code'] = name
        return super(hr_employee_sub_category, self).write(cr, uid,ids, vals, context)
    
    def _check_code_id(self, cr, uid, ids, context=None):
        for sub_category in self.browse(cr, uid, ids, context=context):
            sql = '''
                select id from hr_employee_sub_category where id != %s and ( lower(code) = lower('%s') or lower(name) = lower('%s') )
            '''%(sub_category.id,sub_category.code,sub_category.name)
            cr.execute(sql)
            sub_category_ids = [row[0] for row in cr.fetchall()]
            if sub_category_ids:  
                return False
        return True
    _constraints = [
        (_check_code_id, 'Identical Data', ['code']),
    ]
hr_employee_sub_category()
class hr_employee_grade(osv.osv):
    _name = "hr.employee.grade"
    _order = "code"
    _description = "Employee Grade"
    _columns = {
        'name' : fields.char('Name', 64, required=True),
        'code' : fields.char('Code', 9, required=True),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the record without removing it."),
    }
    _defaults = {
        'active': True,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
    ]
    
 
hr_employee_grade()
class hr_statutory (osv.osv):
    _name = "hr.statutory"
    _description = "Statutory"
    _columns = {
        'name' : fields.char('EPF No.', size=128),
        'epf_nominee' : fields.char('EPF/EPS Nominee', size=128),
        'esi_no' : fields.char('ESI No', size=128),
        'eis_nominee' : fields.char('ESI Nominee', size=128),
        'esi_dispensary' : fields.char(' ESI Dispensary ', size=128),
        'gratuity_no' : fields.char('Gratuity No', size=128),
        'gratuity_nominee' : fields.char('Gratuity Nominee', size=128),
        'pan_no' : fields.char('PAN No.', size=128),
        'pension_no' : fields.char('Pension No', size=128),
        'employee_id': fields.many2one('hr.employee','Employee',ondelete='cascade'),
        'uan' : fields.char('UAN', size=128),
        #TPT-SSR-ON 08/02/2017 - Aadhar No addition 
        'aadhar_no' : fields.char('Aadhar No', size=128),
    }

    def _check_epf(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record_ids = self.search(cr, uid, [('id','!=',record.id),('name','=',record.name)])
            if record_ids:
                raise osv.except_osv(_('Warning!'),_('EPF No. has already existed !'))
                return False
            if record.pension_no:
                pension_ids = self.search(cr, uid, [('id','!=',record.id),('pension_no','=',record.pension_no)])
                if pension_ids:
                    raise osv.except_osv(_('Warning!'),_('Pension No. has already existed !'))
                    return False
        return True
    _constraints = [
        (_check_epf, 'Identical Data', ['name']),
    ]
hr_statutory()


