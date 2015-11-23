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
from lxml import etree

from openerp import tools
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class crm_specification(osv.osv):
    _name = 'crm.specification'
    _order = "create_date desc"
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(crm_specification, self).create(cr, user, vals, context)
        specification_id = self.browse(cr, user, new_id)
        self.pool.get('crm.lead').write(cr, user, [specification_id.lead_id.id], {'status':'awaiting_qc_results'}, context=context)
        self.pool.get('crm.lead.history').create(cr, user,{'lead_id':specification_id.lead_id.id,'status':'awaiting_qc_results'}, context=context)
        return new_id
    
    def onchange_lead_id(self, cr, uid, ids,lead_id=False, context=None):
        res = {'value':{
                      'specification_line':[],
                      }
               }
        if lead_id:
            lead = self.pool.get('crm.lead').browse(cr, uid, lead_id)
            specification_line = []
            for line in lead.lead_line:
                specification_line.append({
                          'product_id': line.product_id.id,
                          'product_type':line.product_type,
                          'application_id':line.application_id.id,
                          'quantity':line.quantity,
                          'uom_id': line.uom_id.id,
                    })
        res['value'].update({
                    'specification_line': specification_line,
        })
        return res
    
    def _full_path(self, cr, uid, location, path):
        assert location.startswith('file:'), "Unhandled filestore location %s" % location
        location = location[5:]

        # sanitize location name and path
        location = re.sub('[.]','',location)
        location = location.strip('/\\')

        path = re.sub('[.]','',path)
        path = path.strip('/\\')
        return os.path.join(tools.config['root_path'], location, cr.dbname, path)

    def _file_read(self, cr, uid, location, fname, bin_size=False):
        full_path = self._full_path(cr, uid, location, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path,'rb').read().encode('base64')
        except IOError:
            _logger.error("_read_file reading %s",full_path)
        return r

    def _file_write(self, cr, uid, location, value):
        bin_value = value.decode('base64')
        fname = hashlib.sha1(bin_value).hexdigest()
        # scatter files across 1024 dirs
        # we use '/' in the db (even on windows)
        fname = fname[:3] + '/' + fname
        full_path = self._full_path(cr, uid, location, fname)
        try:
            dirname = os.path.dirname(full_path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            open(full_path,'wb').write(bin_value)
        except IOError:
            _logger.error("_file_write writing %s",full_path)
        return fname

    def _file_delete(self, cr, uid, location, fname):
        count = self.search(cr, 1, [('store_fname','=',fname)], count=True)
        if count <= 1:
            full_path = self._full_path(cr, uid, location, fname)
            try:
                os.unlink(full_path)
            except OSError:
                _logger.error("_file_delete could not unlink %s",full_path)
            except IOError:
                # Harmless and needed for race conditions
                _logger.error("_file_delete could not unlink %s",full_path)

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
            super(crm_specification, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(crm_specification, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
    
    _columns = {
        'name': fields.char('Document No',size=256, required=True,readonly=True),
        'lead_id': fields.many2one('crm.lead','Lead',),
        'subject': fields.char('Subject',size=256,),
        'description': fields.text('Description'),
        'specification_line': fields.one2many('crm.specification.line','specification_id','Product Line'),
        'datas_fname': fields.char('File Name',size=256),
        'datas': fields.function(_data_get, fnct_inv=_data_set, string='Upload/View Specification', type="binary", nodrop=True),
        'store_fname': fields.char('Stored Filename', size=256),
        'db_datas': fields.binary('Database Data'),
        'file_size': fields.integer('File Size'),
        'states': fields.related('lead_id', 'status', string='States', size=128, type='char'),
        'test_based_on':fields.selection([('specification','Specification'),('samples','Samples')],'Test Based on',required=True),
    }
    

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
    }
    # TPT-By BalamuruganPurushothaman - ON 04/11/2015 - Ticket No:2416
#     _sql_constraints = [
#         ('lead_id_uniq', 'unique (lead_id)', 'The Lead must be unique !'),
#     ]
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name'], context)
 
        for record in reads:
            name = record['name']
            res.append((record['id'], name))
        return res
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('qc_test_request'):
            sql = '''
                SELECT name FROM crm_qc_test where name is not null
            '''
            cr.execute(sql)
            qc_test_request_ids = [row[0] for row in cr.fetchall()]
            request_ids = self.search(cr, uid, [('id','not in',qc_test_request_ids)])
            if context.get('name'):
                request_ids.append(context.get('name'))
            args += [('id','in',request_ids)]
        return super(crm_specification, self).search(cr, uid, args, offset, limit, order, context, count)
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
crm_specification()

class crm_specification_line(osv.osv):
    _name = "crm.specification.line"
    _columns = {
        'specification_id': fields.many2one('crm.specification','QC Test Request', ondelete='cascade'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'quantity': fields.integer('Quantity'),
        'product_type':fields.selection([('rutile','Rutile'),('anatase','Anatase')],'Product Type'),
        'uom_id': fields.many2one('product.uom','UOM'),
        'application_id': fields.many2one('crm.application','Application', ondelete='restrict'),
            }
    _defaults = {
        'quantity':1,
    }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'uom_id':product.uom_id.id}
        return {'value': vals}
crm_specification_line()
