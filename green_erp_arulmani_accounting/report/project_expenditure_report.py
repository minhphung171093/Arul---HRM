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
        'get_project':self.get_project,
        'get_tpt_project':self.get_tpt_project,
        
                                })
        
    def convert_date(self, date):
        if date:
            date = datetime.strptime(date, DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')     
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')    
    
    def get_tpt_project(self):
        wizard_data = self.localcontext['data']['form']
        tpt_project=wizard_data['project_id']
        proj_obj=self.pool.get('tpt.project') 
        tpt_project = ''
        if tpt_project:
          proj_ids = proj_obj.browse(self.cr,self.uid,project_id[0])  
          proj_name = proj_ids.name
        return proj_name
    
    def get_project(self):
        wizard_data = self.localcontext['data']['form']
        date_from=wizard_data['date_from']
        date_to=wizard_data['date_to'] 
        project_id=wizard_data['project_id']
        proj_obj=self.pool.get('tpt.project')
        # Script modified by P.vinothkumar on 10/08/2016 for issue_amount issue-  "and product_id=mil.product_id " is added
        
        # Sql script modified by P.vinothkumar on 22/09/2016 for report matching between GL VS project exp report.  
        sql = '''
        select (sm.product_qty*sm.price_unit) as issueamt,pp.default_code as m_code, pp.name_template as material_name, 
        tp.name as project, tps.name as section,sm.product_qty as issueqty,pu.name as uom
        from tpt_material_issue mi
        inner join stock_move sm on mi.id=sm.issue_id
        inner join tpt_material_request mr on mi.name=mr.id
        inner join product_product pp on sm.product_id=pp.id
        inner join product_template pt on pp.product_tmpl_id=pt.id
        inner join product_uom pu on pt.uom_id=pu.id
        left join tpt_project tp on mr.project_id=tp.id
        left join tpt_project_section tps on mr.project_section_id=tps.id
        where sm.date between '%s' and '%s' and sm.state='done' and mi.state='done' and mi.cost_center_id=20
        and mr.project_id is not null
    '''%((date_from),(date_to))
        if project_id:
            proj_ids = proj_obj.browse(self.cr,self.uid,project_id[0])
            proj_name = proj_ids.name
            sql += " and  tp.name='%s'"%proj_name
        sql += " order by project,section,default_code"          
        self.cr.execute(sql);
        res = []
        s_no = 1
        for line in self.cr.dictfetchall():    
            res.append({
                        's_no':s_no,
                        'material_code': line['m_code'] or '',
                        'material_name': line['material_name'] or '',
                        'project': line['project'] or '',
                        'project_section': line['section'] or '',
                        'issue_qty': line['issueqty'] or '',  
                        'uom': line['uom'] or '', 
                        'issue_amt': line['issueamt'] or '',         
                                 
                        })
            s_no += 1
        return res

