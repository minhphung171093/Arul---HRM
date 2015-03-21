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
                    vendor = int(sh.cell(row, 0).value) or False
                    if vendor:
                        vendor_code = str(vendor)
                    else:
                        vendor_code = False
                    if sh.cell(row, 5).value:
                        zip = str(sh.cell(row, 5).value).replace(" ","")
                        ##############################################                         
                    dem += 1
                    partner_obj.create(cr, uid, {
                        'vendor_code': vendor_code,
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

