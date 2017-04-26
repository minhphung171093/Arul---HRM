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
                        
                    uom_ids = uom_obj.search(cr, uid, [('name','=','No')],limit=1)
                    if not uom_ids:
                        raise osv.except_osv(_('Warning!'),_('Please config Unit of Measure "No"!'))
                    else:
                        uom_id = uom_ids[0]
                    
                    product_vals = product_obj.onchange_category_product_id(cr, uid, [], category_id)['value']
                    
                    product_vals.update({
                        'name': name,
                        'categ_id': category_id,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        'default_code': code,
                    })
                    product_obj.create(cr, uid, product_vals)
#                         
            except Exception, e:
                raise osv.except_osv(_('Warning!'), str(e)+ ' Line: '+str(dem))
        return self.write(cr, uid, ids, {'state':'done'})
    
tpt_import_asset_product()

