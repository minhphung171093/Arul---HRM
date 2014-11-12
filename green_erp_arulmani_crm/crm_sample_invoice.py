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
import openerp.addons.decimal_precision as dp
from openerp import tools
from openerp.osv import fields,osv
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class crm_sample_invoice(osv.osv):
    _name = 'crm.sample.invoice'
    
    _order = "create_date desc"
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name')=='/'):
            seq_obj_name =  self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
            sample_sending_id = self.pool.get('crm.sample.sending').browse(cr, user, vals['sample_sending_id'])
            vals['invoice_type'] = sample_sending_id.lead_id.lead_group
        new_id = super(crm_sample_invoice, self).create(cr, user, vals, context)
        sample_invoice_id = self.browse(cr, user, new_id)
        self.pool.get('crm.lead').write(cr, user, [sample_invoice_id.lead_id.id], {'status':sample_invoice_id.acceptance_status}, context=context)
        self.pool.get('crm.lead.history').create(cr, user,{'lead_id':sample_invoice_id.lead_id.id,'status':sample_invoice_id.acceptance_status}, context=context)
        return new_id
    def write(self, cr, uid, ids, vals, context=None):
        res = super(crm_sample_invoice, self).write(cr, uid, ids, vals, context=context)
        for sample_invoice_id in self.browse(cr, uid, ids):
            self.pool.get('crm.lead').write(cr, uid, [sample_invoice_id.lead_id.id], {'status':sample_invoice_id.acceptance_status}, context=context)
            self.pool.get('crm.lead.history').create(cr, uid,{'lead_id':sample_invoice_id.lead_id.id,'status':sample_invoice_id.acceptance_status}, context=context)
        return res
    
    def onchange_sample_sending_id(self, cr, uid, ids,sample_sending_id=False, context=None):
        res = {'value':{
                        'lead_id':False,
                        'sample_invoice_line':[],
                      }
               }
        if sample_sending_id:
            sample_sending = self.pool.get('crm.sample.sending').browse(cr, uid, sample_sending_id)
            res['value'].update({
                    'lead_id': sample_sending.lead_id.id,})
            sample_invoice_line = []
            for line in sample_sending.sample_sending_line:
                sample_invoice_line.append({
                          'product_id': line.product_id.id,
                          'description': line.product_id.name,
                          'quantity':line.quantity,
                          'uom_id': line.uom_id.id,
                    })
            res['value'].update({
                        'sample_invoice_line': sample_invoice_line,
            })
        return res
    
    def onchange_lead_id(self, cr, uid, ids,lead_id=False, context=None):
        res = {'value':{
                        'invoice_type':False,
                        'currency_id':False,
                        'consignee':False,
                        'street':False,
                        'street2':False,
                        'city':False,
                        'zip':False,
                        'state_id':False,
                        'country_id':False,
                        'sample_invoice_line':[],
                      }
               }
        if lead_id:
            lead = self.pool.get('crm.lead').browse(cr, uid, lead_id)
            res['value'].update({
                                'invoice_type':lead.lead_group,
                                'currency_id':lead.currency_id.id,
                                'consignee':lead.partner_name,
                                'street':lead.street,
                                'street2':lead.street2,
                                'city':lead.city,
                                'zip':lead.zip,
                                'state_id':lead.state_id.id,
                                'country_id':lead.country_id.id,
                                })
            sample_invoice_line = []
            for line in lead.lead_line:
                sample_invoice_line.append({
                          'product_id': line.product_id.id,
                          'description': line.product_id.name,
                          'quantity':1,
                          'uom_id': line.uom_id.id,
                    })
            res['value'].update({
                        'sample_invoice_line': sample_invoice_line,
            })
        return res
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for sample_invoice in self.browse(cr, uid, ids, context=context):
            res[sample_invoice.id] = {
                'amount_total': 0.0,
            }
            total = 0
            for line in sample_invoice.sample_invoice_line:
                total += line.amount
            res[sample_invoice.id]['amount_total'] = total
        return res
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('crm.sample.invoice.line').browse(cr, uid, ids, context=context):
            result[line.sample_invoice_id.id] = True
        return result.keys()

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}
    
    _columns = {
        'name': fields.char('Document No',size=256, required=True,readonly=True),
        'sample_sending_id': fields.many2one('crm.sample.sending','Sample Sending Ref. No.'),
        'lead_id': fields.related('sample_sending_id','lead_id',type='many2one',relation='crm.lead',string='Lead',store=True,readonly=True),
#         'consignee': fields.related('lead_id','partner_name',type='char',relation='crm.lead',string='Consignee',store=True,readonly=True,),
        'consignee':fields.char('Consignee',size=256),
        'acceptance_status':fields.selection([('awaiting_for_sample_acceptance','Awaiting for Sample Acceptance'),('sample_matched','Sample Matched'),('sample_mismatched','Sample Mismatched')],'Acceptance Status'),
        'contact_id': fields.many2one('res.partner', 'Contact',),
        'invoice_date':fields.date('Invoice Date',required=True),
        'invoice_type':fields.selection([ ('domestic','Domestic'), ('export','Export'), ],'Invoice Type',readonly=True),
        'currency_id': fields.related('lead_id','currency_id',type='many2one',relation='res.currency',string='Currency',store=True,readonly=True),
#         'street': fields.related('lead_id','street',type='char',relation='crm.lead',string='Street',store=True,readonly=True,),
#         'street2': fields.related('lead_id','street2',type='char',relation='crm.lead',string='Street2',store=True,readonly=True,),
#         'zip': fields.related('lead_id','zip',type='char',relation='crm.lead',string='Zip',store=True,readonly=True,),
#         'city': fields.related('lead_id','city',type='char',relation='crm.lead',string='City',store=True,readonly=True,),
#         'state_id': fields.related('lead_id','state_id',type='many2one',relation='res.country.state',string='State',store=True,readonly=True,),
#         'country_id': fields.related('lead_id','country_id',type='many2one',relation='res.country',string='Country',store=True,readonly=True,),
        'street':fields.char('Street', size=128),
        'street2':fields.char('Street2', size=128),
        'zip':fields.char('Zip', change_default=True, size=24),
        'city':fields.char('City', size=128),
        'state_id':fields.many2one("res.country.state", 'State'),
        'country_id':fields.many2one('res.country', 'Country'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'crm.sample.invoice': (lambda self, cr, uid, ids, c={}: ids, ['sample_invoice_line'], 10),
                'crm.sample.invoice.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The total amount."),

        'sample_invoice_line': fields.one2many('crm.sample.invoice.line','sample_invoice_id','Product Line'),
    }
    

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'acceptance_status':'awaiting_for_sample_acceptance',
    }
    _sql_constraints = [
        ('sample_sending_id_uniq', 'unique (sample_sending_id)', 'The Sample Sending Ref. No. must be unique !'),
    ]
    
crm_sample_invoice()

class crm_sample_invoice_line(osv.osv):
    _name = "crm.sample.invoice.line"
    _columns = {
        'sample_invoice_id': fields.many2one('crm.sample.invoice','Sample Invoice', ondelete='cascade'),
        'product_id': fields.many2one('product.product','Product',required=True),
        'description': fields.char('Description'),
        'quantity': fields.integer('Quantity'),
        'rate_per_kg': fields.float('Rate Per Kg'),
        'uom_id': fields.many2one('product.uom','UOM'),
        'amount': fields.float('Amount', required=True),
            }
    _defaults = {
        'quantity':1,
    }
    
    def onchange_product_id(self, cr, uid, ids,product_id=False, context=None):
        vals = {}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            vals = {'uom_id':product.uom_id.id,'description':product.name}
        return {'value': vals}
    def onchange_show_amount(self, cr, uid, ids,quantity=False,rate_per_kg=False, context=None):
        vals = {}
        if quantity and rate_per_kg:
            amount = quantity*rate_per_kg
            vals = {'amount':amount}
        return {'value': vals}
crm_sample_invoice_line()
