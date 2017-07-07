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
    _order = "create_date desc"  
    _columns = {
        'name': fields.char('Form No', size = 1024, readonly = True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'date': fields.date('Date',  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'commisionarate_id': fields.many2one('tpt.commisionarate', 'Commisionarate', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'consignment_to': fields.many2one('res.country', 'Consigment To', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'invoice_no_id': fields.many2one('account.invoice','Invoice No', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'manufacturer_id': fields.many2one('tpt.organisation','Manufacturer', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'ce_reg_no': fields.char('CE Reg no', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'package_description':fields.char('No. & Package Description',size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'marks_package': fields.char('Marks & No on Packages', size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'gross_weight':fields.float('Gross Weight', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'net_weight':fields.float('Net Weight', states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'quantity':fields.float('Quantity', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'description_goods': fields.char('Description of Goods',size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'value':fields.float('Value', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'invoiced_date': fields.date('Invoiced Date',  states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'rebate_claimed_amt': fields.float('Rebate Claimed Amt', digits=(16,2), states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'remarks': fields.char('Remarks',size = 1024, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        'duty_rate_line':fields.one2many('tpt.form.are.1.duty.rate','form_are_1_id','Duty Rate'),   
        'state':fields.selection([('draft', 'Draft'),('cancel', 'Cancelled'),('done', 'Approved')],'Status', readonly=True, states={'cancel': [('readonly', True)], 'done':[('readonly', True)]}),
        
        'excise_duty_id': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]", ),
        'tax_id': fields.many2one('account.tax', 'GST', domain="[('type_tax_use','=','sale')]", ),
        'ed_amount': fields.float('ED Amt', ),
        'amount_usd': fields.float('Amt in USD', ),
        'amount_inr': fields.float('Amt in INR', ),
 
        'is_original': fields.boolean('Original Copy'),
        'is_duplicate': fields.boolean('Duplicate Copy'),
        'is_triplicate': fields.boolean('Triplicate Copy'),
        'is_quadruplicate': fields.boolean('Quadruplicate Copy'),
        'is_extra': fields.boolean('Extra Copy'),
        
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),       
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True),
        #TPT START - By SSR - ON 16/02/2017 - Ticket - 3808
        'bond_no': fields.char('Bond No', size=128),
        'bond_date' : fields.date('Date'),
        ##
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
#         if vals.get('name','/')=='/':
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.form.area.1.import') or '/'
         #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
        if 'excise_duty_id' in vals:
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            if vals.get('name','/')=='/':
                sequence = self.pool.get('ir.sequence').get(cr, uid,'tpt.form.area.1.import') or '/'
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
          #TPT END
        return super(tpt_form_are_1, self).create(cr, uid, vals, context=context)
    def print_are1(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        
        are1_ids = self.browse(cr, uid, ids[0])
        if are1_ids.is_original is False and are1_ids.is_duplicate is False and are1_ids.is_triplicate is False and are1_ids.is_quadruplicate is False and are1_ids.is_extra is False:
            raise osv.except_osv(_('Warning!'),
                _('Please Select any one of the following: -Original Copy\n -Duplicate Copy\n -Triplicate Copy\n -Quadruplicate Copy\n -Extra Copy'))
        
        datas = {
             'ids': ids,
             'model': 'tpt.form.are.1',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'form_are_1_report',
            }
    def print_are1_gst(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        
        are1_ids = self.browse(cr, uid, ids[0])
        if are1_ids.is_original is False and are1_ids.is_duplicate is False and are1_ids.is_triplicate is False and are1_ids.is_quadruplicate is False and are1_ids.is_extra is False:
            raise osv.except_osv(_('Warning!'),
                _('Please Select any one of the following: -Original Copy\n -Duplicate Copy\n -Triplicate Copy\n -Quadruplicate Copy\n -Extra Copy'))
        
        datas = {
             'ids': ids,
             'model': 'tpt.form.are.1',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'form_are_1_report_gst',
            }
    #TPT START - By SSR - ON 16/02/2017 - Ticket - 3808        
    def print_are1_back(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        
        are1_ids = self.browse(cr, uid, ids[0])
        if are1_ids.is_original is False and are1_ids.is_duplicate is False and are1_ids.is_triplicate is False and are1_ids.is_quadruplicate is False and are1_ids.is_extra is False:
            raise osv.except_osv(_('Warning!'),
                _('Please Select any one of the following: -Original Copy\n -Duplicate Copy\n -Triplicate Copy\n -Quadruplicate Copy\n -Extra Copy'))
        
        datas = {
             'ids': ids,
             'model': 'tpt.form.are.1',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'form_are_1_report_back',
            }          
    #End#
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
    _order = "create_date desc"   
    _columns = {
        'name': fields.char('SI.No',size = 32, required = True, readonly =True),
        'range_from': fields.char('From Range',size =1024),
        'range_to': fields.char('To Range',size = 1024),
        'reg_no_from': fields.char('From CE Reg No',size =1024),
        'reg_no_to': fields.char('To CE Reg No',size = 1024),
        'division_from': fields.char('From Division',size =1024, ),
        'division_to': fields.char('To Division',size = 1024,  ),
        'warehouse_from_id': fields.many2one('stock.location','From Warehouse',  ),
        'warehouse_to_id': fields.many2one('stock.location','To Warehouse',  ),
        'to_mr_mess': fields.char('To Mr./Messrs.',size = 1024),
        'invoice_no_id': fields.many2one('account.invoice','Invoice No'),
        'date': fields.date('Date',),
        'warehouse_register':fields.char('No. in Warehouse Register',size = 1024),
        'good_description':fields.char('Good Description',size = 1024),
        'remarks':fields.char('Remarks',size = 1024),
        'package_description':fields.char('No. & Package Description',size = 1024),
        'tranport':fields.char('Transport Manner',size = 1024),
        'gross_weight':fields.float('Package gross weight'),
        'good_qty':fields.float('Good Qty'),
        'value':fields.float('Value'),
        'marks_package':fields.float('Marks & No on Packages'),
        'warehouse_date': fields.date('Warehouse Date of Entry', ),
        'invoiced_date': fields.date('Invoiced Date', ),
        'warehousing_date': fields.date('1st Warehousing Date', ),
        'duty_rate_line':fields.one2many('tpt.form.are.3.duty.rate','form_are_3_id','Duty Rate'),   
        
        'excise_duty_id': fields.many2one('account.tax', 'Ex.Duty', domain="[('type_tax_use','=','excise_duty')]", ),
        'is_original': fields.boolean('Original Copy'),
        'is_duplicate': fields.boolean('Duplicate Copy'),
        'is_triplicate': fields.boolean('Triplicate Copy'),
        'is_quadruplicate': fields.boolean('Quadruplicate Copy'), 
        
        'create_date': fields.datetime('Created Date',readonly = True),
        'create_uid': fields.many2one('res.users','Created By',ondelete='restrict',readonly = True),       
        'write_date': fields.datetime('Updated Date',readonly = True),
        'write_uid': fields.many2one('res.users','Updated By',ondelete='restrict',readonly = True),   
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
#         if vals.get('name','/')=='/':
#             vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tpt.form.area.3.import') or '/'
        #TPT START - By P.Vinothkumar - ON 29/03/2016 - FOR (Modify Document Sequence change)
          if 'excise_duty_id' in vals:
            sql = '''
                select code from account_fiscalyear where '%s' between date_start and date_stop
            '''%(time.strftime('%Y-%m-%d'))
            cr.execute(sql)
            fiscalyear = cr.dictfetchone()
            if not fiscalyear:
                raise osv.except_osv(_('Warning!'),_('Financial year has not been configured. !'))
            if vals.get('name','/')=='/':
                sequence = self.pool.get('ir.sequence').get(cr, uid, 'tpt.form.area.3.import') or '/'
                vals['name'] =  sequence and sequence+'/'+fiscalyear['code'] or '/'
          #TPT END  
            return super(tpt_form_are_3, self).create(cr, uid, vals, context=context)
    
    def print_are3(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'tpt.form.are.3',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        are3_ids = self.browse(cr, uid, ids[0])  
        if are3_ids.is_original is False and are3_ids.is_duplicate is False and are3_ids.is_triplicate is False and are3_ids.is_quadruplicate is False:
            raise osv.except_osv(_('Warning!'),
                _('Please Select any one of the following: -Original Copy\n -Duplicate Copy\n -Triplicate Copy\n -Quadruplicate Copy'))
        if are3_ids.is_original is True:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_are_3_report_original',
                } 
        elif are3_ids.is_duplicate is True:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_are_3_report_duplicate',
                } 
        elif are3_ids.is_triplicate is True:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_are_3_report_triplicate',
                } 
        elif are3_ids.is_quadruplicate is True:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_are_3_report_quadruplicate',
                } 
        else:
            return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'form_are_3_report',
                }
            
    def print_are3_back(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'tpt.form.are.3',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'form_are_3_back_report',
            }
    
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
