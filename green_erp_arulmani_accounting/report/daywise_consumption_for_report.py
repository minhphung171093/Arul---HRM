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
        self.localcontext.update({
            'get_date_from':self.get_date_from,
            'get_date_to':self.get_date_to,
            'get_norms':self.get_norms,
            'get_raw_mat':self.get_raw_mat,
             #'get_move_ids':self.get_move_ids,
             #'get_date':self.get_date,
            #'get_leave_balance':self.get_leave_balance,
            'get_invoice':self.get_invoice,
            #'processing_rows':self.processing_rows,
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_norms(self):
        wizard_data = self.localcontext['data']['form']
        norms=wizard_data['name']
        sql = '''
               Select name as norm_name from mrp_bom where id = %s
              '''%(norms[0])
        self.cr.execute(sql)
        for move in self.cr.dictfetchall():
             norm_name1 = move['norm_name']             
        return norm_name1 or ''
    
    def get_raw_mat(self):
        wizard_data = self.localcontext['data']['form']
        raw = wizard_data['product_id']
        if raw:
            sql = '''
                   select default_code as code,name_template as name from product_product where cate_name = 'raw' and id = '%s'
                  '''%(raw[0])
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                 code = move['code']
                 name = move['name']           
            return code +" " +name or ''
        else:
            return ' '
  
	def processing_rows(self, val):
		lst_val = []
		final_data = []
		count = 0
		for i in val:	
			if i['mat_code'] in lst_val:
				count += 1
				val_str = 'applied_qty' + str(count)
				data[val_str] = i['applied_qty']		
			else:
				data = {}
				data.update(i)
				lst_val.append(i['mat_code'])
				count = 0
			if not final_data:
				final_data.append(data)
			else:
				l_data = len(final_data)
				for pos, val in enumerate(final_data):
					if val['mat_code'] == i['mat_code']:
						del final_data[pos]
						final_data.append(data)
					else:
						if pos == (l_data - 1):
							final_data.append(data)
						else:
							continue
		for pos, val in enumerate(final_data):
			for r in range(1,15):
				m_str = 'applied_qty' + str(r)
				if m_str not in val:
					final_data[pos][m_str] = 0.0
		return final_data
    
    #def get_leave_balance(self):
    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        raw_mat=wizard_data['product_id']
        norms=wizard_data['name']
        #res = []
        #date_from += datetime.timedelta(1)
        #datenext = wizard_data['date_from'] + 1
        
        if raw_mat:
            sql = '''
                           select a.material_code as mat_code,a.material_name as mat_name,a.uom as uom,
                           a.sch_date as scheduled_date,a.app_qty as applied_qty
                           from (select p.default_code as material_code,p.name_template as material_name,
                           mp.date_planned as sch_date,u.name as uom,mpp.product_qty as app_qty
                           from mrp_production_product_line mpp
                           join mrp_production mp on (mp.id = mpp.production_id)
                           join product_product p on (p.id = mpp.product_id) 
                           join mrp_bom bm on (bm.id = mp.bom_id)
                           join product_uom u on (u.id = mpp.product_uom)
                           where mp.date_planned between '%s' and '%s' and mp.state = 'done'
                           and mp.bom_id = '%s' and p.id = '%s'
                           group by p.default_code,p.name_template,mp.date_planned,
                           u.name,mpp.product_qty
                           )a
                           order by a.material_code,a.sch_date
                        '''%(date_from,date_to,norms[0],raw_mat[0])
            self.cr.execute(sql)                    
            lst_val = []
            final_data = []
            count = 0
            for i in self.cr.dictfetchall():    
                if i['mat_code'] in lst_val:
                    count += 1
                    val_str = 'applied_qty' + str(count)
                    data[val_str] = i['applied_qty']        
                else:
                    data = {}
                    data.update(i)
                    lst_val.append(i['mat_code'])
                    count = 0
                if not final_data:
                    final_data.append(data)
                else:
                    l_data = len(final_data)
                    for pos, val in enumerate(final_data):
                        if val['mat_code'] == i['mat_code']:
                            del final_data[pos]
                            final_data.append(data)
                        else:
                            if pos == (l_data - 1):
                                final_data.append(data)
                            else:
                                continue
            for pos, val in enumerate(final_data):
                for r in range(1,15):
                    m_str = 'applied_qty' + str(r)
                    if m_str not in val:
                        final_data[pos][m_str] = 0.0           
            return final_data
        
        else:
            sql = '''
                           select a.material_code as mat_code,a.material_name as mat_name,a.uom as uom,
                           a.sch_date as scheduled_date,a.app_qty as applied_qty
                           from (select p.default_code as material_code,p.name_template as material_name,
                           mp.date_planned as sch_date,u.name as uom,mpp.product_qty as app_qty
                           from mrp_production_product_line mpp
                           join mrp_production mp on (mp.id = mpp.production_id)
                           join product_product p on (p.id = mpp.product_id) 
                           join mrp_bom bm on (bm.id = mp.bom_id)
                           join product_uom u on (u.id = mpp.product_uom)
                           where mp.date_planned between '%s' and '%s' and mp.bom_id = '%s' and mp.state = 'done'
                           group by p.default_code,p.name_template,mp.date_planned,
                           u.name,mpp.product_qty
                           )a
                           order by a.material_code,a.sch_date
                        '''%(date_from,date_to,norms[0])
            self.cr.execute(sql)         
            lst_val = []
            final_data = []
            count = 0
            for i in self.cr.dictfetchall():    
                if i['mat_code'] in lst_val:
                    count += 1
                    val_str = 'applied_qty' + str(count)
                    data[val_str] = i['applied_qty']        
                else:
                    data = {}
                    data.update(i)
                    lst_val.append(i['mat_code'])
                    count = 0
                if not final_data:
                    final_data.append(data)
                else:
                    l_data = len(final_data)
                    for pos, val in enumerate(final_data):
                        if val['mat_code'] == i['mat_code']:
                            del final_data[pos]
                            final_data.append(data)
                        else:
                            if pos == (l_data - 1):
                                final_data.append(data)
                            else:
                                continue
            for pos, val in enumerate(final_data):
                for r in range(1,15):
                    m_str = 'applied_qty' + str(r)
                    if m_str not in val:
                        final_data[pos][m_str] = 0.0           
            return final_data
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

