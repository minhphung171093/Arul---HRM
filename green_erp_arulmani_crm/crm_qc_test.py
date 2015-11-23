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

class crm_qc_test(osv.osv):
    _name = 'crm.qc.test'
    
    _order = "create_date desc"
    def create(self, cr, user, vals, context=None):
        new_id = super(crm_qc_test, self).create(cr, user, vals, context)
        qc_test_id = self.browse(cr, user, new_id)
        self.pool.get('crm.lead').write(cr, user, [qc_test_id.name.lead_id.id], {'status':'qc_test_completed'}, context=context)
        self.pool.get('crm.lead.history').create(cr, user,{'lead_id':qc_test_id.name.lead_id.id,'status':'qc_test_completed'}, context=context)
        return new_id
    
    def onchange_name(self, cr, uid, ids,name=False, context=None):
        res = {'value':{
                      'qc_test_line':[],
                      }
               }
        if name:
            specification = self.pool.get('crm.specification').browse(cr, uid, name)
            qc_test_line = []
            for line in specification.specification_line:
                qc_test_line.append({
                          'product_id': line.product_id.id,
                          'quantity':line.quantity,
                          'product_type':line.product_type,
                          'uom_id': line.uom_id.id,
                          'application_id':line.application_id.id,
                    })
        res['value'].update({
                    'qc_test_line': qc_test_line,
        })
        return res
    
    
    _columns = {
        'name':fields.many2one('crm.specification','QC Test Request Document No',required=True),
        'test_result':fields.selection([('matched','Matched'),('not_matched','Not Matched')],'Test Result',required=True),
        'remarks': fields.text('Remarks'),
        'qc_test_line': fields.one2many('crm.qc.test.line','qc_test_id','Product Line'),
        'test_detail': fields.one2many('crm.qc.test.detail','qc_test_id','Test Detail',required=True),
    }
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The QC Test Request Document No must be unique !'),
    ]
    
crm_qc_test()

class crm_qc_test_line(osv.osv):
    _name = "crm.qc.test.line"
    _columns = {
        'qc_test_id': fields.many2one('crm.qc.test','QC Test', ondelete='cascade'),
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
crm_qc_test_line()

class crm_qc_test_detail(osv.osv):
    _name = "crm.qc.test.detail"
    
    _columns = {
        'qc_test_id': fields.many2one('crm.qc.test','QC Test', ondelete='cascade'),
        'name': fields.char('Parameters',size=256),
        'required_spec': fields.char('Required Spec',size=256),
        'available_spec': fields.char('Available Spec',size=256),
        'uom_id': fields.many2one('product.uom','UOM'),
            }
    
    
crm_qc_test_detail()
