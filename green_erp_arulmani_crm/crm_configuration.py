# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import hashlib
import itertools
import logging
import os
import re

from openerp import tools
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
                'company_code': fields.char('Company Code', size=1000),  
                'factory_street': fields.char('Street', size=128),
                'factory_street2': fields.char('Street2', size=128),
                'factory_zip': fields.char('Zip', change_default=True, size=24),
                'factory_city': fields.char('City', size=128),
                'factory_state_id': fields.many2one("res.country.state", 'State'),
                'factory_country_id': fields.many2one('res.country', 'Country'),              
                }
res_company()    

class res_partner(osv.osv):
    _inherit = "res.partner"   
    
    def _get_is_company(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.crm_lead_id:
                result[obj.id] = False
            else:
                result[obj.id] = True
        return result
    
#     def name_get(self, cr, uid, ids, context=None):
#         """Overrides orm name_get method"""
#         res = []
#         if not ids:
#             return res
#         reads = self.read(cr, uid, ids, ['name','last_name'], context)
#  
#         for record in reads:
#             name = record['name']
#             if record['last_name']:
#                 name += ' '+ record['last_name']
#             res.append((record['id'], name))
#         return res
    
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#         ids = self.search(cr, user, args, context=context, limit=limit)
#         return self.name_get(cr, user, ids, context=context)
    
    def onchange_employee_id(self, cr, uid, ids,employee_id=False, context=None):
        print 'employee=',employee_id
        vals = {}
        if employee_id:
            emp = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            vals = {'user_id':emp.user_id.id}
        return {'value': vals}
    def get_sychronized(self, cursor, user, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for partner in self.browse(cursor, user, ids, context=context):
            res[partner.id] = False
        return res
    
    _columns = {
        'arulmani_type': fields.selection([('export','Export'),('domestic','Domestic'),('indirect_export','Indirect Export')],'Customer Group'),
        'zone': fields.selection([('north','North'),('east','East'),('west','West'),('south','South')],'Zone'),
        'credit_limit_used': fields.float('Credit Limit',degits=(16,2)),
        'credit_exposure': fields.float('Credit Exposure',degits=(16,2)),
        'vat': fields.float('VAT',degits=(16,2)),
        #'pan_tin': fields.char('PAN/TIN',size=128),
        #'pan': fields.char('PAN',size=128),
        'pan_tin': fields.char('PAN',size=128),
        
        'ce_rc': fields.char('Ex. C.E.RC.',size=128),
        'ecc': fields.char('Ex. E.C.C',size=128),
        'sin': fields.char('SIN',size=128),
        'cst': fields.char('CST',size=128),
        'range': fields.char('Ex. Range',size=128),
        'division': fields.char('Ex. Division',size=128),
        'commissionerate': fields.char('Ex. Commissionerate',size=128),
        'excise_duty': fields.char('Excise Duty',size=128),
#         'distribution_channel': fields.selection([('corporate','Corporate'),('distributor','Distributor'),('consignee','Consignee'),('indenting','Indenting'),('direct','Direct')],'Distribution Channel'),
        'distribution_channel': fields.many2one('crm.case.channel','Distribution Channel'),
        'crm_lead_id': fields.many2one('crm.lead','CRM Lead'),
        'employee_id': fields.many2one('hr.employee', 'Salesperson', select=True, track_visibility='onchange'),
        'gender': fields.selection([('male', 'Male'),('female', 'Female')], 'Gender'),
        'last_name' : fields.char('Last Name', size=32),
        'customer_code': fields.char('Customer Code', size=64, select=1, readonly=1),
#         'is_company': fields.function(_get_is_company, type='boolean', size=5, string='Is a company',store=True, invisible=True),
        'currency_id': fields.many2one('res.currency','Currency'),
        'create_uid': fields.many2one('res.users','Create by'),
        'create_date': fields.datetime('Create on'),
        'language_id': fields.many2one('res.lang','Language'),
        'sales_organization_code_id': fields.many2one('sales.organization.code','Sales Organization Code'),
        'customer_account_group_id': fields.many2one('customer.account.group','Customer Account Group'),
        'sort_key_id': fields.many2one('sort.key','Sort Key'),
        'tax_classification_id': fields.many2one('tax.classification','Tax Classification'),
        'tax_number_2_id': fields.many2one('tax.number.2','Tax Number 2'),    
        'account_assign_group_id': fields.many2one('account.assign.group','Account Assign Group'), 
        'customer_statistics_group_id': fields.many2one('customer.statistics.group','Customer Statistics Group'),       
        'price_group_id': fields.many2one('price.group','Price Group'),
        'inco_terms_id': fields.many2one('stock.incoterms', 'Incoterm'),
        'division_code_id': fields.many2one('division.code','Division Code'),
        'tax_category_id': fields.many2one('tax.category','VAT/CST in %'), 
        'tax_number_1_id': fields.many2one('tax.number.1','Tax Number 1'),
        'credit_control_area_id': fields.many2one('credit.control.area','Credit Control Area'),    
        'shipping_conditions_id': fields.many2one('shipping.conditions','Shipping Conditions'), 
        'cust_pric_procedure_id': fields.many2one('cust.pric.procedure','Cust Pric Procedure'), 
        'customer_group_id': fields.many2one('customer.group','Customer Type'), 
        'order_probability_id': fields.many2one('order.probability','Order Probability'), 
        'reconciliation_acct_id': fields.many2one('reconciliation.acct','Reconciliation Acct'), 
        'sychronized': fields.function(get_sychronized, string='Is Sychronized', type='boolean'),
        
        #TPT'
        'excise_reg_no': fields.char('Ex.RegNo.',size=128),
        'tin': fields.char('TIN',size=128),
        'street3': fields.char('Street3',size=128),       
        'lst': fields.char('LST',size=128),
        'service_reg_no': fields.char('Service RegNo.',size=128),
        'tcs': fields.many2one('tax.category','TCS %'), 
        #'is_approved': fields.boolean('Is Approved'),
    }
    _defaults = {
        'is_company': True,
        'sychronized':False,
    }
    
    def init(self, cr):
        sql ='''
            delete from ir_ui_menu where name = 'Partner Ledger';
            delete from ir_act_window where name = 'Partner Ledger';
            delete from ir_values where name = 'Print Partner Ledger';
        '''
        cr.execute(sql)
        return True
    #TPT START - By BalamuruganPurushothaman ON 28/03/2015 - TO SET DIFF SEQ NO FOR CUSTOMERS & CONSIGNEES
    def create(self, cr, uid, vals, context=None):  
        if vals['customer_account_group_id']:     
            sql = '''
            select id from customer_account_group where name = 'VVTI Ship to Party'
         '''
            cr.execute(sql)
            temp = cr.fetchone()
            consignee_id = temp[0]
        
            sql = '''
        select id from customer_account_group where name = 'VVTI Sold to Party'
         '''
            cr.execute(sql)
            temp = cr.fetchone()
            customer_id = temp[0]
        
            sql = '''
        select id from customer_account_group where name = 'VVTI Indent Comm.'
         '''
            cr.execute(sql)
            temp = cr.fetchone()
            indend_comm_id = temp[0]
                
            if vals['customer_account_group_id']==consignee_id:
                sql = '''
            select max(customer_code) from res_partner where customer_account_group_id = 
            (select id from customer_account_group where code = 'VVTI Ship to Party')
         '''
                cr.execute(sql)
                temp = cr.fetchone()
                consignee_seq = temp[0]
                vals['customer_code'] = int(float(consignee_seq)) + 1
        
            if vals['customer_account_group_id']==customer_id:
                sql = '''
            select max(customer_code) from res_partner where customer_account_group_id = 
            (select id from customer_account_group where code = 'VVTI Sold to Party')
         '''
                cr.execute(sql)
                temp = cr.fetchone()
                customer_seq = temp[0]
                vals['customer_code'] = int(float(customer_seq)) + 1
        
            if vals['customer_account_group_id']==indend_comm_id:
                sql = '''
            select max(customer_code) from res_partner where customer_account_group_id = 
            (select id from customer_account_group where code = 'VVTI Indent Comm.')
         '''
                cr.execute(sql)
                temp = cr.fetchone()
                indend_comm_seq = temp[0]
                vals['customer_code'] = int(float(indend_comm_seq)) + 1
                               
        return super(res_partner, self).create(cr, uid, vals, context)
    
res_partner()

class res_language(osv.osv):
    _name = "res.language"
    _description = 'Language'
    _columns = {
        'code': fields.char('Language Code', size=128,required=True),
        'name': fields.char('Language Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Language Code must be unique !', ['code']),
    ]
res_language()

class sales_organization_code(osv.osv):
    _name = "sales.organization.code"
    _description = 'Sales Organization Code'
    _columns = {
        'name': fields.char('Sales Organization Code', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            if name and len(name) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Sales Organization Code must be unique !', ['name']),
    ]
sales_organization_code()
class customer_account_group(osv.osv):
    _name = "customer.account.group"
    _description = 'Customer Account Group'
    _columns = {
        'code': fields.char('Customer Account Group Code', size=128,required=True),
        'name': fields.char('Customer Account Group Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Customer Account Group Code must be unique !', ['code']),
    ]
customer_account_group()
class sort_key(osv.osv):
    _name = "sort.key"
    _description = 'Sort Key'
    _columns = {
        'code': fields.char('Sort Key Code', size=128,required=True),
        'name': fields.char('Sort Key Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Sort Key Code must be unique !', ['code']),
    ]
sort_key()
class tax_classification(osv.osv):
    _name = "tax.classification"
    _description = 'Tax Classification'
    _columns = {
        'code': fields.char('Tax Classification Code', size=128,required=True),
        'name': fields.char('Tax Classification Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Tax Classification Code must be unique !', ['code']),
    ]
tax_classification()
class tax_number_2(osv.osv):
    _name = "tax.number.2"
    _description = 'Tax Number 2'
    _columns = {
        'code': fields.char('Tax Number 2 Code', size=128,required=True),
        'name': fields.char('Tax Number 2  Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Tax Number 2 Code must be unique !', ['code']),
    ]
tax_number_2()
class account_assign_group(osv.osv):
    _name = "account.assign.group"
    _description = 'Account Assign Group'
    _columns = {
        'description': fields.char('Description', size=128,required=True),
        'name': fields.char('Account Assign Group', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            if name and len(name) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Account Assign Group must be unique !', ['name']),
    ]
account_assign_group()
class customer_statistics_group(osv.osv):
    _name = "customer.statistics.group"
    _description = 'Customer Statistics Group'
    _columns = {
        'description': fields.char('Description', size=128,required=True),
        'name': fields.char('Customer Statistics Group Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            if name and len(name) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Customer Statistics Group must be unique !', ['name']),
    ]
customer_statistics_group() 
class price_group(osv.osv):
    _name = "price.group"
    _description = 'Price Group'
    _columns = {
        'code': fields.char('Price Group', size=128,required=True),
        'name': fields.char('Description', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Price Group Code must be unique !', ['code']),
    ]
price_group() 
# class inco_terms(osv.osv):
#     _name = "inco.terms"
#     _description = 'Inco Terms'
#     _columns = {
#         'code': fields.char('Inco Terms Code', size=128,required=True),
#         'name': fields.char('Inco Terms Name', size=128,required=True),
#     }
#     def _check_name(self,cr,uid,ids):
#         obj = self.browse(cr,uid,ids[0])
#         if obj and obj.code:
#             code = self.search(cr, uid, [('code','=',obj.code)])
#             if code and len(code) > 1:
#                 return False
#         return True
#     _constraints = [
#         (_check_name, 'The Inco Terms Code must be unique !', ['code']),
#     ]
# inco_terms()
class division_code(osv.osv):
    _name = "division.code"
    _description = 'Division Code'
    _columns = {
        'name': fields.char('Division Code', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            code = self.search(cr, uid, [('name','=',obj.name)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Division Code must be unique !', ['code']),
    ]
division_code() 
class tax_category(osv.osv):
    _name = "tax.category"
    _description = 'Division Code'
    _columns = {
        'code': fields.char('Tax Category Code', size=128,required=True),
        'name': fields.char('Tax Category Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Tax Category Code must be unique !', ['code']),
    ]
tax_category()
class tax_number_1(osv.osv):
    _name = "tax.number.1"
    _description = 'Tax Number 1'
    _columns = {
        'code': fields.char('Tax Number 1 Code', size=128,required=True),
        'name': fields.char('Tax Number 1 Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Tax Number 1 Code must be unique !', ['code']),
    ]
tax_number_1() 
class credit_control_area(osv.osv):
    _name = "credit.control.area"
    _description = 'Credit Control Area'
    _columns = {
        'code': fields.char('Credit Control Area Code', size=128,required=True),
        'name': fields.char('Credit Control Area Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Credit Control Area Code must be unique !', ['code']),
    ]
credit_control_area()
class shipping_conditions(osv.osv):
    _name = "shipping.conditions"
    _description = 'Shipping Conditions'
    _columns = {
        'description': fields.text('Description', size=128,required=True),
        'name': fields.char('Shipping Conditions', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            if name and len(name) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Shipping Conditions must be unique !', ['name']),
    ]
shipping_conditions() 
class cust_pric_procedure(osv.osv):
    _name = "cust.pric.procedure"
    _description = 'Cust Pric Procedure'
    _columns = {
        'code': fields.char('Cust Pric Procedure Code', size=128,required=True),
        'name': fields.char('Cust Pric Procedure Name', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Cust Pric Procedure Code must be unique !', ['code']),
    ]
cust_pric_procedure() 
class customer_group(osv.osv):
    _name = "customer.group"
    _description = 'Customer Group'
    _columns = {
        'code': fields.char('Customer Group', size=128,required=True),
        'name': fields.char('Description', size=128,required=True),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.code:
            code = self.search(cr, uid, [('code','=',obj.code)])
            if code and len(code) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Customer Group must be unique !', ['code']),
    ]
customer_group() 
class order_probability(osv.osv):
    _name = "order.probability"
    _description = 'Order Probability'
    _columns = {
        'from': fields.datetime('From',required=True),
        'to': fields.datetime('to',required=True),        
        'name': fields.text('Short Description', required=True),
    }
order_probability() 
class reconciliation_acct(osv.osv):
    _name = "reconciliation.acct"
    _description = 'Reconciliation Acct'
    _columns = {
        'code': fields.char('Ch.Account Code', size=128),
        'name': fields.char('Account Name', size=128,required=True),
        'description': fields.char('G/L Ac', size=128),
    }
    def _check_name(self,cr,uid,ids):
        obj = self.browse(cr,uid,ids[0])
        if obj and obj.name:
            name = self.search(cr, uid, [('name','=',obj.name)])
            if name and len(name) > 1:
                return False
        return True
    _constraints = [
        (_check_name, 'The Account Name must be unique !', ['name']),
    ]
reconciliation_acct() 
class customer_address(osv.osv):
    _name = "customer.address"
    _columns = {
        'crm_lead_id': fields.many2one('crm.lead','CRM Lead'),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'street3': fields.char('Street3', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'country': fields.related('country_id', type='many2one', relation='res.country', string='Country',
                                  deprecated="This field will be removed as of OpenERP 7.1, use country_id instead"),
    }
customer_address()

class crm_leadsource(osv.osv):
    _name = "crm.leadsource"
    _columns = {
        'name': fields.char('Name', size=128,required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique !'),
    ]
crm_leadsource()

class crm_application(osv.osv):
    _name = "crm.application"
    _columns = {
        'code': fields.char('Code', size=128,required=True),
        'name': fields.char('Name', size=128,required=True),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique !'),
        ('name_uniq', 'unique (name)', 'The name must be unique !'),
    ]
crm_application()

class res_partner_bank(osv.osv):
    _inherit = 'res.partner.bank'
    
    _columns = {
        'factory_street': fields.char('Street', size=128),
        'factory_zip': fields.char('Zip', change_default=True, size=24),
        'factory_city': fields.char('City', size=128),
        'factory_state_id': fields.many2one("res.country.state", 'State'),
        'factory_country_id': fields.many2one('res.country', 'Country'),
    }
res_partner_bank()

class account_tax(osv.osv):
    _inherit = 'account.tax'
    _columns= {
               'type_tax_use': fields.selection([('excise_duty','Excise Duty'),('sale','Sale'),('purchase','Purchase'),('all','All')], 'Tax Application', required=True),
               
               }
    
account_tax()


class account_payment_term(osv.osv):
    _inherit = 'account.payment.term'
    _columns = {
                'code': fields.char('Payment Term Code', size=64),
                }
    
account_payment_term()    
    
class product_product(osv.osv):
    _inherit = "product.product"
     
#     _columns = {
#         'product_code': fields.char('Product Code', size=128),
#     }
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        res = []
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return res
#         reads = self.read(cr, uid, ids, ['default_code'], context)
        reads = self.read(cr, uid, ids, ['name','default_code'], context=context)
        for record in reads:
            name = record['default_code']+ ' ' + (record['name'] or'')
            res.append((record['id'], name))
  
#         for record in reads:
#             name = record['default_code']
#             res.append((record['id'], name))
        return res
     
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
     
     
product_product()

class crm_case_channel(osv.osv):
    _inherit = "crm.case.channel"
    _columns = {
        'code': fields.char('Channel Code', size=64, required=True),
    }
crm_case_channel()    


