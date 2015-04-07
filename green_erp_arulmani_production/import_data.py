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

class tpt_import_batch_anatase(osv.osv):
    _name = 'tpt.import.batch.anatase'
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
            super(tpt_import_batch_anatase, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_batch_anatase, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Batch', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_batch_anatase(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            batch_obj = self.pool.get('stock.production.lot')
            qty_ver_obj = self.pool.get('tpt.quality.verification')
            pro_obj = self.pool.get('product.product')
            locat_obj = self.pool.get('stock.location')
            inve_obj = self.pool.get('stock.inventory') 
            app_obj = self.pool.get('crm.application')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    product_id = False
                    product_ids = pro_obj.search(cr, uid, [('default_code','in',['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'])])
                    if not product_ids:
                        raise osv.except_osv(_('Warning!'),_('Do not have TITANIUM DIOXIDE-ANATASE product in stock, please check it!'))
                    else:
                        product_id = product_ids[0]
                    location_id = False
                    parent_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if not parent_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
                    locat_ids = locat_obj.search(cr, uid, [('name','in',['TiO2','TIO2']),('location_id','=',parent_ids[0])])
                    if not locat_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have TIO2 location in Store warehouse, please check it!'))
                    else:
                        location_id = locat_ids[0]
                        
                    app_id = False
                    app = sh.cell(row, 2).value
                    app_ids = app_obj.search(cr, uid, [('name','=',app.strip())])
                    if not app_ids:
                        app_id = app_obj.create(cr, uid, {'name':app.strip(),'code':app.strip()})
                    else:
                        app_id = app_ids[0]
                    batch = sh.cell(row, 0).value
                    batch_ids = batch_obj.search(cr, uid, [('name','=',batch.strip()),('product_id','=',product_id)])
                    if not batch_ids:
                        batch_id = batch_obj.create(cr, uid, {'name':batch.strip(),'product_id':product_id,'phy_batch_no':batch.strip(),'application_id':app_id,'location_id':location_id})
                    else:
                        batch_id = batch_ids[0]
                    location = sh.cell(row, 1).value.strip()
                    bags = sh.cell(row, 3).value.strip()
                    
                        ##############################################                         
                    dem += 1
                    qty_ver_obj.create(cr, uid, {
                        'prod_batch_id': batch_id or False,
                        'product_id': product_id,
                        'warehouse_id': location_id or False,
                        'phy_batch_no': batch.strip() or False,
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'applicable_id': app_id,
                        'location':location or '',
                        'weight': bags or '',
                        'state': 'done',
                    })
                    
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_batch_anatase()

class tpt_import_inventory_anatase(osv.osv):
    _name = 'tpt.import.inventory.anatase'
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
            super(tpt_import_inventory_anatase, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_inventory_anatase, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Material Data', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_inventory_anatase(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            pro_obj = self.pool.get('product.product')
            locat_obj = self.pool.get('stock.location')
            inve_obj = self.pool.get('stock.inventory')
            batch_obj = self.pool.get('stock.production.lot')
            inventory_line_id = []
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    location_id = False
                    parent_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if not parent_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
                    locat_ids = locat_obj.search(cr, uid, [('name','in',['TiO2','TIO2']),('location_id','=',parent_ids[0])])
                    if not locat_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have TIO2 location in Store warehouse, please check it!'))
                    else:
                        location_id = locat_ids[0]
                    
                    product_id = False
                    product_ids = pro_obj.search(cr, uid, [('default_code','in',['TITANIUM DIOXIDE-ANATASE','TiO2','M0501010001'])])
                    if not product_ids:
                        raise osv.except_osv(_('Warning!'),_('Do not have TITANIUM DIOXIDE-ANATASE product in stock, please check it!'))
                    else:
                        product_id = product_ids[0]
                        
                    batch = sh.cell(row, 0).value
                    batch_ids = batch_obj.search(cr, uid, [('name','=',batch.strip()),('product_id','=',product_id)])
                    if not batch_ids:
                        batch_id = batch_obj.create(cr, uid, {'name':batch.strip(),'product_id':product_id,'phy_batch_no':batch.strip(),'application_id':app_id,'location_id':location_id})
                    else:
                        batch_id = batch_ids[0]
                    qty = sh.cell(row, 4).value or 0
                    if qty > 0:
                        product = pro_obj.browse(cr, uid, product_id)
                        inventory_line_id.append((0,0,{
                                                        'location_id':location_id, 
                                                        'product_id': product.id,
                                                        'prod_lot_id':batch_id,
                                                        'product_qty':qty,
                                                        'product_uom':product.uom_po_id.id,
                                                       }))
                    dem += 1
                        
                        ##############################################                         
                if inventory_line_id:
                    inve_id = inve_obj.create(cr, uid, {
                        'name': 'Update',
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'inventory_line_id': inventory_line_id,
                    })
                    inve_obj.action_confirm(cr, uid, [inve_id],context=None)
                    inve_obj.action_done(cr, uid, [inve_id],context=None)
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_inventory_anatase()

class tpt_import_batch_rutile(osv.osv):
    _name = 'tpt.import.batch.rutile'
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
            super(tpt_import_batch_rutile, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_batch_rutile, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Data Batch', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_batch_rutile(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            batch_obj = self.pool.get('stock.production.lot')
            qty_ver_obj = self.pool.get('tpt.quality.verification')
            pro_obj = self.pool.get('product.product')
            locat_obj = self.pool.get('stock.location')
            inve_obj = self.pool.get('stock.inventory') 
            app_obj = self.pool.get('crm.application')
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    product_id = False
                    product_ids = pro_obj.search(cr, uid, [('default_code','in',['TITANIUM DIOXIDE-RUTILE','M0501010008'])])
                    if not product_ids:
                        raise osv.except_osv(_('Warning!'),_('Do not have TITANIUM DIOXIDE-RUTILE product in stock, please check it!'))
                    else:
                        product_id = product_ids[0]
                    location_id = False
                    parent_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if not parent_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
                    locat_ids = locat_obj.search(cr, uid, [('name','in',['TiO2','TIO2']),('location_id','=',parent_ids[0])])
                    if not locat_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have TIO2 location in Store warehouse, please check it!'))
                    else:
                        location_id = locat_ids[0]
                        
                    app_id = False
                    app = sh.cell(row, 2).value
                    app_ids = app_obj.search(cr, uid, [('name','=',app.strip())])
                    if not app_ids:
                        app_id = app_obj.create(cr, uid, {'name':app.strip(),'code':app.strip()})
                    else:
                        app_id = app_ids[0]
                    batch = sh.cell(row, 0).value
                    batch_ids = batch_obj.search(cr, uid, [('name','=',batch.strip()),('product_id','=',product_id)])
                    if not batch_ids:
                        batch_id = batch_obj.create(cr, uid, {'name':batch.strip(),'product_id':product_id,'phy_batch_no':batch.strip(),'application_id':app_id,'location_id':location_id})
                    else:
                        batch_id = batch_ids[0]
                    location = sh.cell(row, 1).value.strip()
                    bags = sh.cell(row, 3).value.strip()
                    
                        ##############################################                         
                    dem += 1
                    qty_ver_obj.create(cr, uid, {
                        'prod_batch_id': batch_id or False,
                        'product_id': product_id,
                        'warehouse_id': location_id or False,
                        'phy_batch_no': batch.strip() or False,
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'applicable_id': app_id,
                        'location':location or '',
                        'weight': bags or '',
                        'state': 'done',
                    })
                    
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_batch_rutile()

class tpt_import_inventory_rutile(osv.osv):
    _name = 'tpt.import.inventory.rutile'
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
            super(tpt_import_inventory_rutile, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_inventory_rutile, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True

    _columns = {
        'name': fields.date('Date Import', required=True,states={'done': [('readonly', True)]}),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Material Data', type="binary", nodrop=True,states={'done': [('readonly', True)]}),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'state':fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True)
    }
    
    _defaults = {
        'state':'draft',
        'name': time.strftime('%Y-%m-%d'),
        
    }
    
    def import_inventory_rutile(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            pro_obj = self.pool.get('product.product')
            locat_obj = self.pool.get('stock.location')
            inve_obj = self.pool.get('stock.inventory')
            batch_obj = self.pool.get('stock.production.lot')
            inventory_line_id = []
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    location_id = False
                    parent_ids = locat_obj.search(cr, uid, [('name','=','Store'),('usage','=','view')])
                    if not parent_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have Store warehouse, please check it!'))
                    locat_ids = locat_obj.search(cr, uid, [('name','in',['TiO2','TIO2']),('location_id','=',parent_ids[0])])
                    if not locat_ids:
                        raise osv.except_osv(_('Warning!'),_('System does not have TIO2 location in Store warehouse, please check it!'))
                    else:
                        location_id = locat_ids[0]
                    
                    product_id = False
                    product_ids = pro_obj.search(cr, uid, [('default_code','in',['TITANIUM DIOXIDE-RUTILE','M0501010008'])])
                    if not product_ids:
                        raise osv.except_osv(_('Warning!'),_('Do not have TITANIUM DIOXIDE-RUTILE product in stock, please check it!'))
                    else:
                        product_id = product_ids[0]
                        
                    batch = sh.cell(row, 0).value
                    batch_ids = batch_obj.search(cr, uid, [('name','=',batch.strip()),('product_id','=',product_id)])
                    if not batch_ids:
                        batch_id = batch_obj.create(cr, uid, {'name':batch.strip(),'product_id':product_id,'phy_batch_no':batch.strip(),'application_id':app_id,'location_id':location_id})
                    else:
                        batch_id = batch_ids[0]
                    qty = sh.cell(row, 4).value or 0
                    if qty > 0:
                        product = pro_obj.browse(cr, uid, product_id)
                        inventory_line_id.append((0,0,{
                                                        'location_id':location_id, 
                                                        'product_id': product.id,
                                                        'prod_lot_id':batch_id,
                                                        'product_qty':qty,
                                                        'product_uom':product.uom_po_id.id,
                                                       }))
                    dem += 1
                        
                        ##############################################                         
                if inventory_line_id:
                    inve_id = inve_obj.create(cr, uid, {
                        'name': 'Update',
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'inventory_line_id': inventory_line_id,
                    })
                    inve_obj.action_confirm(cr, uid, [inve_id],context=None)
                    inve_obj.action_done(cr, uid, [inve_id],context=None)
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_inventory_rutile()