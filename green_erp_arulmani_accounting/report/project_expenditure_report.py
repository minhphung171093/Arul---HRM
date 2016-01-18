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
          
        sql = '''
        select a.default_code as m_code, a.project,a.section, a.name_template as material_name, sum(a.product_isu_qty) as IssueQty,
        a.UOM, sum(a.amount) as IssueAmt
        from (select p.default_code,p.name_template,mil.product_isu_qty, uom.name as UOM,
        (select sum(credit) from account_move_line where move_id=am.id and credit>0) as Amount,
        mi.doc_no, hs.name as section, tp.name as Project
        from tpt_material_issue_line mil
        inner join tpt_material_issue mi on (mil.material_issue_id=mi.id)
        inner join tpt_material_request mr on (mr.id=mi.name)
        inner join account_move am on (am.material_issue_id=mi.id)
        inner join product_product p on (p.id=mil.product_id)
        inner join arul_hr_section hs on (hs.id=mr.section_id)
        inner join tpt_project tp on (tp.id=mr.project_id)
        inner join product_uom uom on (uom.id=mil.uom_po_id)
        where mi.date_expec>='%s' and mi.date_expec<='%s')a
        '''%((date_from),(date_to))
        if project_id:
            proj_ids = proj_obj.browse(self.cr,self.uid,project_id[0])
            proj_name = proj_ids.name
            sql += " where a.project='%s'"%proj_name
        sql += " group by a.default_code, a.name_template, a.section, a.project, a.uom order by a.project, a.section, a.default_code"
                     
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

