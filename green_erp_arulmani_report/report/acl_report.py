# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import osv
from openerp.tools.translate import _
import random
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        pool = pooler.get_pool(self.cr.dbname)
        self.data_dict = {}
        self.group_ids = []
        self.model_ids = []
        self.check_group_ids = []
        self.group_checking_id = False
        self.localcontext.update({
            'convert_date': self.convert_date,
            'khoi_tao': self.khoi_tao,
            'get_groups': self.get_groups,
            'get_models': self.get_models,
            'get_acl': self.get_acl,
            'get_group_name': self.get_group_name,
            'get_model_name': self.get_model_name,
        })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
    
    def get_groups(self):
        return self.group_ids
    
    def get_models(self):
        return self.model_ids
    
    def get_group_name(self, group_id):
        group = self.pool.get('res.groups').browse(self.cr, self.uid, group_id)
        return group.name
    
    def get_model_name(self, model_id):
        model = self.pool.get('ir.model').browse(self.cr, self.uid, model_id)
        return model.name
    
    def check_full_access(self, group_id, model_id):
        if self.data_dict.get(group_id, False):
            if self.data_dict[group_id].get(model_id, False):
                if self.data_dict[group_id][model_id]['read'] and self.data_dict[group_id][model_id]['write'] and self.data_dict[group_id][model_id]['create'] and self.data_dict[group_id][model_id]['unlink']:
                    return True
                else:
                    return False
        return False
    
    def get_all_object(self, group):
        if self.group_checking_id:
            self.check_group_ids.append(group.id)
            for access in group.model_access:
                if self.check_full_access(self.group_checking_id, access.model_id.id):
                    continue
                if self.data_dict.get(self.group_checking_id, False):
                    if self.data_dict[self.group_checking_id].get(access.model_id.id, False):
                        if access.perm_read:
                            self.data_dict[self.group_checking_id][access.model_id.id]['read'] = True
                        if access.perm_write:
                            self.data_dict[self.group_checking_id][access.model_id.id]['write'] = True
                        if access.perm_create:
                            self.data_dict[self.group_checking_id][access.model_id.id]['create'] = True
                        if access.perm_unlink:
                            self.data_dict[self.group_checking_id][access.model_id.id]['unlink'] = True
            
            for implied in group.implied_ids:
                if implied.id not in self.check_group_ids:
                    self.get_all_object(implied)
                else:
                    continue
        return True
    
    def khoi_tao(self):
        wizard_data = self.localcontext['data']['form']
        group_ids = wizard_data['tpt_group_ids']
        if not group_ids:
            group_ids = self.pool.get('res.groups').search(self.cr, self.uid, [])
        self.group_ids = group_ids
        wizard_data = self.localcontext['data']['form']
        model_ids = wizard_data['tpt_model_ids']
        if not model_ids:
            model_ids = self.pool.get('ir.model').search(self.cr, self.uid, [])
        self.model_ids = model_ids
        for group in self.pool.get('res.groups').browse(self.cr, self.uid, group_ids):
            self.data_dict[group.id] = {}
            for model_id in model_ids:
                self.data_dict[group.id].update({
                    model_id: {'read': False, 'write': False, 'create': False, 'unlink': False}
                })
            self.group_checking_id = group.id
            self.check_group_ids = []
            self.get_all_object(group)
        return True
    
    def get_acl(self, group_id, model_id, access):
        if self.data_dict.get(group_id, False):
            if self.data_dict[group_id].get(model_id, False):
                if self.data_dict[group_id][model_id][access]:
                    return True
        return False
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
