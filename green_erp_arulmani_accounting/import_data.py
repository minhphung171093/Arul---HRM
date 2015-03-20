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

class tpt_import_account(osv.osv):
    _name = 'tpt.import.account'
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
            super(tpt_import_account, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_account, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='GL Account', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_account(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            account_obj = self.pool.get('account.account')
            type_obj = self.pool.get('account.account.type')
            pa = False
            recon = False
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    account = str(sh.cell(row, 0).value) or False
                    if not account:
                        raise osv.except_osv(_('Warning!'),_('Do not have Account code in line %s!'%dem))
                    else:
                        account_code = account.replace(" ","")
                    inter_type = sh.cell(row, 2).value
                    if inter_type in ('Regular','regular'):
                        inter_type = 'other'
                    if inter_type in ('receivable','Receivable','payable','Payable'):
                        recon = True
                    acc_type = sh.cell(row, 3).value or False
                    if acc_type:
                        type_ids = type_obj.search(cr, uid, [('name','=',acc_type)])
                        if type_ids:
                            account_type = type_ids[0]
                        else:
                            raise osv.except_osv(_('Warning!'),_('Account Type %s is not exist!'%acc_type))
                    else:
                        raise osv.except_osv(_('Warning!'),_('Do not have Account Type for %s!'%account))
                    parent = sh.cell(row, 4).value
                    if parent:
                        parent_code = parent.replace(" ","")
                        parent_ids = account_obj.search(cr, uid, [('code','=',parent_code)])
                        if not parent_ids:
                            raise osv.except_osv(_('Warning!'),_('Parent Account of %s is not exist!'%account))
                        else:
                            pa = parent_ids[0]
                    
                    dem += 1
                    account_obj.create(cr, uid, {
                        'code': account_code,
                        'name': sh.cell(row, 1).value,
                        'type': inter_type.lower(),
                        'user_type': account_type,
                        'parent_id': pa,
                        'reconcile': recon,
                    })
                    
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_account()

class tpt_map_account(osv.osv):
    _name = 'tpt.map.account'

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'state':fields.selection([('draft', 'Draft'),('map_cus', 'Mapped Customer'),('map_sup', 'Mapped Supplier')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def map_customer_account(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        cus_obj = self.pool.get('res.partner')
        
        account_ids = account_obj.search(cr, uid, [('type','=','receivable')])
        for account in account_obj.browse(cr, uid, account_ids):
            cus_code = account.code[4:]
            cus_ids = cus_obj.search(cr, uid, [('customer_code','=',cus_code),('customer','=',True),('is_company','=',True)])
            if cus_ids:
                cus_obj.write(cr, uid, cus_ids,{'property_account_receivable':account.id})
        return self.write(cr, uid, ids, {'state':'map_cus'})
    
    def map_supplier_account(self, cr, uid, ids, context=None):
        account_obj = self.pool.get('account.account')
        cus_obj = self.pool.get('res.partner')
        
        account_ids = account_obj.search(cr, uid, [('type','=','payable')])
        for account in account_obj.browse(cr, uid, account_ids):
            sup_code = account.code
            sup_ids = cus_obj.search(cr, uid, [('vendor_code','=',sup_code),('supplier','=',True)])
            if sup_ids:
                cus_obj.write(cr, uid, sup_ids,{'property_account_payable':account.id})
        return self.write(cr, uid, ids, {'state':'map_sup'})
    
tpt_map_account()

