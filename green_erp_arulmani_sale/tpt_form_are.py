# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import datetime
import calendar
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class tpt_form_are_1(osv.osv):
    _name = "tpt.form.are.1"
      
    _columns = {
        'name': fields.char('Form No', size = 1024, readonly = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date': fields.date('Date', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'commisionarate_id': fields.many2one('tpt.commisionarate', 'Commisionarate', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'consignment_to': fields.many2one('res.country', 'Consigment To', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'invoice_no_id': fields.many2one('account.invoice','Invoice No', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'manufacturer_id': fields.many2one('tpt.organisation','Manufacturer', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'ce_reg_no': fields.char('CE Reg no', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'package_description':fields.char('No. & Package Description',size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'marks_package': fields.char('Marks & No on Packages', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'gross_weight':fields.float('Gross Weight', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'net_weight':fields.float('Net Weight', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'quantity':fields.float('Quantity', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'description_goods': fields.char('Description of Goods',size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'value':fields.float('Value', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'invoiced_date': fields.date('Invoiced Date', required = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'rebate_claimed_amt': fields.float('Rebate Claimed Amt', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'remarks': fields.char('Remarks',size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'duty_rate_line':fields.one2many('tpt.form.are.1.duty.rate','form_are_1_id','Duty Rate'),   
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancel'),('done', 'Approve')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        
        'excise_duty_id': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]", ),
        'ed_amount': fields.float('ED Amt', ),
        'amount_usd': fields.float('Amt in USD', ),
        'amount_inr': fields.float('Amt in INR', ),
 
        'is_original': fields.boolean('Original Copy'),
        'is_duplicate': fields.boolean('Duplicate Copy'),
        'is_triplicate': fields.boolean('Triplicate Copy'),
        'is_quadruplicate': fields.boolean('Quadruplicate Copy'),
        'is_extra': fields.boolean('Extra Copy'),
                }
    _defaults={
               'name':'/',
               'state':'draft',
    }
    
    def bt_approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'done'})
    
    def bt_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids,{'state':'cancel'})
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.form.area.1.import') or '/'
        return super(tpt_form_are_1, self).create(cr, uid, vals, context=context)
    
tpt_form_are_1()

class tpt_commisionarate(osv.osv):
    _name = "tpt.commisionarate"
      
    _columns = {
        'name': fields.char('Name Of Commisionarate ', size = 1024, required = True),
        'nature': fields.char('Nature Of Commisionarate ', size = 1024),
        'code1': fields.char('Commisionarate Code 1', size = 1024),
        'code2': fields.char('Commisionarate Code 2', size = 1024),
        'code3': fields.char('Commisionarate Code 3', size = 1024),
                }
tpt_commisionarate()

class tpt_organisation(osv.osv):
    _name = "tpt.organisation"
      
    _columns = {
        'name': fields.char('Name Of Manufacturer ', size = 1024, required = True),
                }
tpt_organisation()

class tpt_form_are_1_duty_rate(osv.osv):
    _name = "tpt.form.are.1.duty.rate"
      
    _columns = {
        'duty_rate': fields.float('Duty Rate in %', digits=(16,2), required = True),
        'amount_usd': fields.float('Amount(in USD)', digits=(16,2), required = True),
        'amount_inr': fields.float('Amount(in INR)', digits=(16,2), required = True),
        'form_are_1_id': fields.many2one('tpt.form.are.1', 'Duty Rate'),
                }
tpt_form_are_1_duty_rate()

class tpt_form_are_3(osv.osv):
    _name = "tpt.form.are.3"
      
    _columns = {
        'name': fields.char('SI.No',size = 32, required = True, readonly =True),
        'range_from': fields.char('From Range',size =1024),
        'range_to': fields.char('To Range',size = 1024),
        'reg_no_from': fields.char('From CE Reg No',size =1024),
        'reg_no_to': fields.char('To CE Reg No',size = 1024),
        'division_from': fields.char('From Division',size =1024, required = True),
        'division_to': fields.char('To Division',size = 1024,  required = True),
        'warehouse_from_id': fields.many2one('stock.location','From Warehouse',  required = True),
        'warehouse_to_id': fields.many2one('stock.location','To Warehouse',  required = True),
        'to_mr_mess': fields.char('To Mr./Messrs.',size = 1024),
        'invoice_no_id': fields.many2one('account.invoice','Invoice No'),
        'date': fields.date('Date', required = True),
        'warehouse_register':fields.char('No. in Warehouse Register',size = 1024),
        'good_description':fields.char('Good Description',size = 1024),
        'remarks':fields.char('Remarks',size = 1024),
        'package_description':fields.char('No. & Package Description',size = 1024),
        'tranport':fields.char('Transport Manner',size = 1024),
        'gross_weight':fields.float('Package gross weight'),
        'good_qty':fields.float('Good Qty'),
        'value':fields.float('Value'),
        'marks_package':fields.float('Marks & No on Packages'),
        'warehouse_date': fields.date('Warehouse Date of Entry', required = True),
        'invoiced_date': fields.date('Invoiced Date', required = True),
        'warehousing_date': fields.date('1st Warehousing Date', required = True),
        'duty_rate_line':fields.one2many('tpt.form.are.3.duty.rate','form_are_3_id','Duty Rate'),   
        
        'is_original': fields.boolean('Original Copy'),
        'is_duplicate': fields.boolean('Duplicate Copy'),
        'is_triplicate': fields.boolean('Triplicate Copy'),
        'is_quadruplicate': fields.boolean('Quadruplicate Copy'),    
                }
    _defaults={
               'name':'/',
    }
    
    def onchange_so_date(self, cr, uid, ids, invoice_no_id=False, context=None):
        vals = {}
        if invoice_no_id:
            invoice = self.pool.get('account.invoice').browse(cr,uid,invoice_no_id)
            vals={'invoiced_date':invoice.date_invoice,                  
                  }
        return {'value':vals}    

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.form.area.3.import') or '/'
        return super(tpt_form_are_3, self).create(cr, uid, vals, context=context)
tpt_form_are_3()

class tpt_form_are_3_duty_rate(osv.osv):
    _name = "tpt.form.are.3.duty.rate"
      
    _columns = {
        'duty_rate': fields.float('Duty Rate in %', digits=(16,2), required = True),
        'amount_usd': fields.float('Amount(in USD)', digits=(16,2), required = True),
        'amount_inr': fields.float('Amount(in INR)', digits=(16,2), required = True),
        'form_are_3_id': fields.many2one('tpt.form.are.3', 'Duty Rate'),
                }
    
tpt_form_are_3_duty_rate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
