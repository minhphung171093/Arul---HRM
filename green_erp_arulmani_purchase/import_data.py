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

class tpt_import_supplier(osv.osv):
    _name = 'tpt.import.supplier'
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
            super(tpt_import_supplier, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_supplier, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
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
    
    def import_supplier(self, cr, uid, ids, context=None):
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
            title_obj = self.pool.get('res.partner.title')
            zip = ''
            try:
                dem = 1
                for row in range(1,sh.nrows):
                    country = sh.cell(row, 3).value
                    country_ids = country_obj.search(cr, uid, [('code','=',country)])
                    if not country_ids:
                        country_id = country_obj.create(cr, uid, {'name':country,'code':country})
                    else:
                        country_id = country_ids[0]
                    state = sh.cell(row, 6).value
                    state_ids = state_obj.search(cr, uid, [('code','=',state),('country_id','=',country_id)])
                    if not state_ids:
                        state_id = state_obj.create(cr, uid, {'name':state,'code':state,'country_id':country_id})
                    else:
                        state_id = state_ids[0]
                    
                    title = sh.cell(row, 9).value
                    title_ids = title_obj.search(cr, uid, [('name','=',title)])
                    if not title_ids:
                        title_id = title_obj.create(cr, uid, {'name':title})
                    else:
                        title_id = title_ids[0]
                    
                    name = str(sh.cell(row, 1).value)
                    street = str(sh.cell(row, 7).value)
#                     vendor = sh.cell(row, 0).value or False
#                     if vendor:
#                         vendor_code = str(vendor)
#                     else:
#                         vendor_code = False
                    if sh.cell(row, 5).value:
                        zip = str(sh.cell(row, 5).value).replace(" ","")
                        ##############################################                         
                    dem += 1
                    partner_obj.create(cr, uid, {
                        'vendor_code': sh.cell(row, 0).value or False,
                        'country_id': country_id,
                        'name': name.replace('"','') or False,
                        'last_name': sh.cell(row, 2).value or False,
                        'city': sh.cell(row, 8).value or False,
                        'zip': zip,
                        'state_id':state_id or False,
                        'street': street.replace('"','') or False,
                        'street2': sh.cell(row, 4).value or False,
                        'phone': sh.cell(row, 12).value or False,
                        'mobile': sh.cell(row, 13).value or False,
                        'fax': sh.cell(row, 14).value or False,
                        'title': title_id or False,
                        'tin':sh.cell(row, 11).value or False,
                        'cst':sh.cell(row, 10).value or False,
                        'supplier': True,
                    })
                    
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_supplier()

class tpt_import_material(osv.osv):
    _name = 'tpt.import.material'
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
            super(tpt_import_material, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_material, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
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
    
    def import_material(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            pro_pro_obj = self.pool.get('product.product')
            pro_tem_obj = self.pool.get('product.template')
            uom_obj = self.pool.get('product.uom')
            cate_obj = self.pool.get('product.category')
            uom_cate_obj = self.pool.get('product.uom.categ')
            try:
                dem = 1
                for row in range(2,sh.nrows):
                    code = sh.cell(row, 0).value or False
                    if code:
                        cla = sh.cell(row, 2).value or False
                        classif = False
                        if cla:
                            if cla.strip()=='Mechanical':
                                classif = 'mechan'
                            if cla.strip()=='Civil':
                                classif = 'civil'
                            if cla.strip()=='Electrical':
                                classif = 'elect'
                            if cla.strip()=='Instrumentation':
                                classif = 'inst'
                            if cla.strip()=='Raw. Mat. & Prod':
                                classif = 'raw_mat'
                            if cla.strip()=='QC and R&D':
                                classif = 'qc'
                            if cla.strip()=='Safety & Personnel':
                                classif = 'safe'
                            if cla.strip()=='Projects':
                                classif = 'proj'
                        
                        cate = sh.cell(row, 4).value or False
                        cate_name = False
                        if cate:
                            if cate.strip() in ['Raw Materials','Raw Material']:
                                cate_name = 'raw'
                            if cate.strip() == 'Finished Product':
                                cate_name = 'finish'
                            if cate.strip() == 'Spares':
                                cate_name = 'spares'
                            if cate.strip() == 'Consumables':
                                cate_name = 'consum'
                        cate_ids = cate_obj.search(cr, uid, [('cate_name','=',cate_name)])
                        if not cate_ids:
                            cate_id = cate_obj.create(cr, uid, {'name':cate,'cate_name':cate_name})
                        else:
                            cate_id = cate_ids[0]
                        
                        unit_ids = uom_cate_obj.search(cr, uid, [('name','=','Unit')])
                        if not unit_ids:
                            unit_id = uom_cate_obj.create(cr, uid, {'name':'Unit'})
                        else:
                            unit_id = unit_ids[0]
                        
                        weight_ids = uom_cate_obj.search(cr, uid, [('name','=','Weight')])
                        if not weight_ids:
                            weight_id = uom_cate_obj.create(cr, uid, {'name':'Weight'})
                        else:
                            weight_id = weight_ids[0]
                        
                        length_ids = uom_cate_obj.search(cr, uid, [('name','=','Length / Distance')])
                        if not length_ids:
                            length_id = uom_cate_obj.create(cr, uid, {'name':'Length / Distance'})
                        else:
                            length_id = length_ids[0]
                        
                        volume_ids = uom_cate_obj.search(cr, uid, [('name','=','Volume')])
                        if not volume_ids:
                            volume_id = uom_cate_obj.create(cr, uid, {'name':'Volume'})
                        else:
                            volume_id = volume_ids[0]
                            
                        uom = sh.cell(row, 5).value or False
                        uom_name = False
                        uom_cate = False
                        if uom:
                            if uom.strip()=='KG':
                                uom_name = 'kg'
                                uom_cate = weight_id
                            if uom.strip()=='GRM':
                                uom_name = 'GRM'
                                uom_cate = weight_id
                            if uom.strip()=='MT':
                                uom_name = 'Tonne'
                                uom_cate = weight_id
                            if uom.strip()=='M2':
                                uom_name = 'M2'
                                uom_cate = weight_id
                            if uom.strip()=='M3':
                                uom_name = 'M3'
                                uom_cate = weight_id
                            if uom.strip()=='BAG':
                                uom_name = 'BAG'
                                uom_cate = unit_id
                            if uom.strip()=='BOX':
                                uom_name = 'BOX'
                                uom_cate = unit_id
                            if uom.strip()=='SET':
                                uom_name = 'SET'
                                uom_cate = unit_id
                            if uom.strip()=='PKT':
                                uom_name = 'PKT'
                                uom_cate = unit_id
                            if uom.strip()=='LOT':
                                uom_name = 'LOT'
                                uom_cate = unit_id
                            if uom.strip()=='PAIR':
                                uom_name = 'PAIR'
                                uom_cate = unit_id
                            if uom.strip()=='COIL':
                                uom_name = 'COIL'
                                uom_cate = unit_id
                            if uom.strip()=='No':
                                uom_name = 'No'
                                uom_cate = unit_id
                            if uom.strip()=='FT':
                                uom_name = 'FT'
                                uom_cate = length_id
                            if uom.strip()=='FT2':
                                uom_name = 'FT2'
                                uom_cate = length_id
                            if uom.strip()=='M':
                                uom_name = 'M'
                                uom_cate = length_id
                            if uom.strip()=='ROL':
                                uom_name = 'ROL'
                                uom_cate = length_id
                            if uom.strip()=='L':
                                uom_name = 'L'
                                uom_cate = volume_id
                            if uom.strip()=='KL':
                                uom_name = 'KL'
                                uom_cate = volume_id
                            if uom.strip()=='ML':
                                uom_name = 'ML'
                                uom_cate = volume_id
                        uom_ids = []
                        if uom_name:
                            uom_ids = uom_obj.search(cr, uid, [('name','=',uom_name)])
                        if not uom_ids:
                            uom_id = uom_obj.create(cr, uid, {'name':uom_name,'category_id':uom_cate,'factor':1})
                        else:
                            uom_id = uom_ids[0]
                            
                        mrp = False
                        min = sh.cell(row, 7).value or 0
                        max = sh.cell(row, 8).value or 0
                        reod = sh.cell(row, 6).value or 0
                        if max > 0:
                            mrp = True
                            
                        ##############################################                         
                        dem += 1
                        pro_pro_obj.create(cr, uid, {
                            'name': sh.cell(row, 1).value.strip() or False,
                            'categ_id': cate_id,
                            'purchase_ok': True,
                            'cate_name': cate_name,
                            'default_code': sh.cell(row, 0).value.strip() or False,
                            'uom_id': uom_id,
                            'uom_po_id': uom_id,
                            'mrp_control': mrp,
                            'min_stock': min,
                            'max_stock': max,
                            're_stock': reod,
                            'bin_location': str(sh.cell(row, 14).value).strip() or False,
                            'tpt_mater_type': classif,
                            'old_no': sh.cell(row, 3).value.strip() or False,
                        })
                    
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem+1))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_material()

class tpt_import_inventory(osv.osv):
    _name = 'tpt.import.inventory'
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
            super(tpt_import_inventory, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(tpt_import_inventory, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
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
    
    def import_inventory(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0])
        try:
            recordlist = base64.decodestring(this.datas)
            excel = xlrd.open_workbook(file_contents = recordlist)
            sh = excel.sheet_by_index(0)
        except Exception, e:
            raise osv.except_osv(_('Warning!'), str(e))
        if sh:
            pro_pro_obj = self.pool.get('product.product')
            locat_obj = self.pool.get('stock.location')
            inve_obj = self.pool.get('stock.inventory')
            inventory_line_id = []
            try:
                dem = 1
                for row in range(2,sh.nrows):
                    locat = sh.cell(row, 9).value.strip() or ''
                    qty = sh.cell(row, 10).value or 0
                    mate = sh.cell(row, 0).value.strip() or False
                    locat_id = False
                    if qty > 0:
                        if locat != '':
                            locat = locat.strip()
                            locat_ids = locat_obj.search(cr, uid, [('name','=',locat)])
                            if locat_ids:
                                locat_id = locat_ids[0]
                        if mate:
                            product_ids = pro_pro_obj.search(cr, uid, [('default_code','=',mate)])
                            for product in pro_pro_obj.browse(cr, uid, product_ids):
                                inventory_line_id.append((0,0,{
                                                                'location_id':locat_id, 
                                                                'product_id': product.id,
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
    
tpt_import_inventory()