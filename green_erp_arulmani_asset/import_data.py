# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
from datetime import datetime
import base64
import calendar
import xlrd
from xlrd import open_workbook,xldate_as_tuple

class tpt_import_asset_product(osv.osv):
    _name = 'tpt.import.asset.product'
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
            super(tpt_import_asset_product, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_asset_product, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
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
    
    def import_asset_product(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            product_obj = self.pool.get('product.product')
            category_obj = self.pool.get('product.category')
            uom_obj = self.pool.get('product.uom')
            account_obj = self.pool.get('account.account')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    dem += 1
                    code = str(sh.cell(row, 0).value) or False
                    name = str(sh.cell(row, 1).value) or False
                    if not code:
                        raise osv.except_osv(_('Warning!'),_('Do not have MATERIAL CODE in line %s!'%dem))
                    if not name:
                        raise osv.except_osv(_('Warning!'),_('Do not have MATERIAL NAME in line %s!'%dem))

                    category_ids = category_obj.search(cr, uid, [('name','=','Assets')])
                    if not category_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Category "Assets"!'))
                    else:
                        category_id = category_ids[0]
                        
                    uom = str(sh.cell(row, 2).value) or False
                    uom_ids = uom_obj.search(cr, uid, [('name','=',uom)],limit=1)
                    if not uom_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Unit of Measure "%s"!'%(uom)))
                    else:
                        uom_id = uom_ids[0]
                        
                    account = str(sh.cell(row, 3).value) or False
                    account_ids = account_obj.search(cr, uid, [('code','=',account)],limit=1)
                    if not account_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Account "%s"!'%(account)))
                    else:
                        account_id = account_ids[0]
                        
                    purchase_account_ids = account_obj.search(cr, uid, [('code','=','0000119503')],limit=1)
                    if not purchase_account_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Account "0000119503"!'))
                    else:
                        purchase_account_id = purchase_account_ids[0]
                    
                    product_vals = product_obj.onchange_category_product_id(cr, uid, [], category_id)['value']
                    
                    product_vals.update({
                        'name': name,
                        'categ_id': category_id,
                        'product_asset_acc_id': account_id,
                        'purchase_acc_id': purchase_account_id,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        'default_code': code,
                    })
                    sql = '''
                        select pp.id
                            from product_product pp
                            left join product_template pt on pp.product_tmpl_id=pt.id
                            where (lower(regexp_replace((pp.name_template),'[^a-zA-Z0-9]', '', 'g')) = lower(regexp_replace(('%s'),'[^a-zA-Z0-9]', '', 'g'))
                            or lower(regexp_replace((pp.default_code),'[^a-zA-Z0-9]', '', 'g')) = lower(regexp_replace(('%s'),'[^a-zA-Z0-9]', '', 'g'))) and pt.categ_id=%s
                    '''%(name,code,category_id)
                    cr.execute(sql)
                    product_ids = [row[0] for row in cr.fetchall()]
                    if product_ids:
                        if len(product_ids)>1:
                            raise osv.except_osv(_('Warning!'),_('We have %s product with name is "%s" or code is "%s"!'%(len(product_ids),name,code)))
                        product_obj.write(cr, uid, product_ids, product_vals)
                    else:
                        product_obj.create(cr, uid, product_vals)
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_asset_product()

class tpt_import_asset_master(osv.osv):
    _name = 'tpt.import.asset.master'
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
            super(tpt_import_asset_master, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_asset_master, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
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
    
    def import_asset_master(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            product_obj = self.pool.get('product.product')
            category_obj = self.pool.get('account.asset.category')
            asset_obj = self.pool.get('asset.asset')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    dem += 1
                    name = str(sh.cell(row, 0).value) or False
                    category = str(sh.cell(row, 1).value) or False

                    category_ids = category_obj.search(cr, uid, [('name','=',category)])
                    if not category_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Asset Category "%s"!'%(category)))
                    else:
                        category_id = category_ids[0]
                        
                    product = str(sh.cell(row, 2).value) or False
                    sql = '''
                        select id from product_product where lower(regexp_replace((name_template),'[^a-zA-Z0-9]', '', 'g')) = lower(regexp_replace(('%s'),'[^a-zA-Z0-9]', '', 'g'))
                    '''%(name)
                    cr.execute(sql)
                    product_ids = [row[0] for row in cr.fetchall()]
                    if not product_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Product "%s"!'%(product)))
                    else:
                        product_id = product_ids[0]
                    asset_vals = {
                        'name': name,
                        'category_id': category_id,
                        'product_id': product_id,
                    }
                    asset_obj.create(cr, uid, asset_vals)
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_asset_master()

class tpt_import_asset_register(osv.osv):
    _name = 'tpt.import.asset.register'
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
            super(tpt_import_asset_register, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_asset_register, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
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
    
    def convert_float2date(self, date):
        if date:
            seconds = (date - 25569) * 86400.0
            converted_date = datetime.utcfromtimestamp(seconds)
            converted_date = converted_date.strftime('%Y-%m-%d')   
        else:
            converted_date = False
        return converted_date
    
    def import_asset_register(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            product_obj = self.pool.get('product.product')
            category_obj = self.pool.get('account.asset.category')
            asset_obj = self.pool.get('asset.asset')
            account_asset_obj = self.pool.get('account.asset.asset')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    dem += 1
                    code = str(sh.cell(row, 0).value) or False
                    category = str(sh.cell(row, 1).value) or False

                    category_ids = category_obj.search(cr, uid, [('name','=',category)])
                    if not category_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Asset Category "%s"!'%(category)))
                    else:
                        category_id = category_ids[0]
                    
                    capitalization_date = sh.cell(row, 2).value
                    capitalization_date = self.convert_float2date(capitalization_date)
                    
                    name = str(sh.cell(row, 3).value) or False
                    asset_ids = asset_obj.search(cr, uid, [('name','=',name)])
                    if not asset_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Asset Master "%s"!'%(name)))
                    else:
                        asset_id = asset_ids[0]
                    gross_value = sh.cell(row, 4).value
                    
                    asset_vals = {
                        'register_code': code,
                        'category_id': category_id,
                        'caps_date': capitalization_date,
                        'purchase_value': gross_value,
                        'name': name,
                        'asset_id': asset_id,
                    }
                    account_asset_obj.create(cr, uid, asset_vals)
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_asset_register()
