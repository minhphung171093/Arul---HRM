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
            'get_invoice':self.get_invoice,
            'get_status':self.get_status,
            'get_doc_type':self.get_doc_type,
            'get_req_name_code':self.get_req_name_code,
            'get_on_hand_qty':self.get_on_hand_qty,
            'get_pending_qty':self.get_pending_qty,
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['date_from']:
            date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['date_to']:
            date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        return ''
    
    def get_req_name_code(self,name,code,lname):
        req_name = name
        req_code = code
        req_lname = lname 
        if req_name and req_code:
            if lname:   
                return '['+req_code+']' +req_name+' ' +lname or ''
            else:
                return '['+req_code+']' +req_name+' '
        else:
            return ' '  
  
   
    def get_status(self,type):
        if type == 'draft':
            return 'Draft'
        if type == 'confirm':
            return 'Confirmed'
        if type == 'close':
            return 'Closed'
        if type == '+':
            return 'Store Approved'            
        if type == '++':
            return 'Store & HOD Approved'
        if type == 'x':
            return 'Store Rejected'            
        if type == 'xx':
            return 'Store & HOD Rejected'
        if type == 'rfq_raised':
            return 'RFQ Raised'        
        if type == 'cancel':
            return 'PO Cancelled'
        if type == 'quotation_raised':
            return 'Quotation Raised'        
        if type == 'po_raised':
            return 'PO Raised'
        if type == 'quotation_cancel':
            return 'Quotation Cancelled'
        #return res or ''
   
    def get_doc_type(self,type):
        if type == 'draft':
            return 'VV Level Based PR'
        if type == 'capital':
            return 'VV Capital PR'
        if type == 'local':
            return 'VV Local Purchase PR'
        if type == 'maintenance':
            return 'VV Maintenance PR'
        if type == 'consumable':
            return 'VV Consumable PR'
        if type == 'outside':
            return 'VV Outside Service PR'            
        if type == 'spare':
            return 'VV Spare (Project) PR'
        if type == 'service':
            return 'VV Service PR'
        if type == 'normal':
            return 'VV Normal PR'
        if type == 'raw':
            return 'VV Raw Material PR'
       # return res or ''
    
    def get_pending_qty(self,line_id,stock_id,ind_qty):            
            if stock_id > 0:          
                sql = '''
                        select pp.rfq_qty as rfq_qty
                        from tpt_purchase_indent pi
                        inner join tpt_purchase_product pp on (pp.pur_product_id = pi.id)
                        left join stock_move sm on (sm.po_indent_id = pi.id and sm.product_id = pp.product_id)
                        left join stock_picking sp on (sp.id = sm.picking_id)
                        where sp.state in ('done') and pp.id = %s and sm.id = %s
                      '''%(line_id,stock_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                      if move['rfq_qty']:
                            rfq_qty = move['rfq_qty']
                            pen_qty = ind_qty - rfq_qty
                            return pen_qty or 0.000
            else:
                return ind_qty or 0.000
                
    def get_issue_qty_count(self,move_line_id):
                
                sql = '''
                    select count(*) from tpt_material_issue_line msl 
                    inner join tpt_material_issue ms on (ms.id = msl.material_issue_id)
                    where state = 'done' and msl.request_line_id = %s
                '''%(move_line_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    count = move['count']
                    return count or 0.000
   
    
    def get_on_hand_qty(self,product_id):
                res = {}
                sql = '''
                            select case when sum(foo.product_qty)>0 then sum(foo.product_qty) else 0 end ton_sl from 
                                    (select st.product_qty
                                        from stock_move st 
                                        where st.state='done' and st.product_id=%s and st.location_dest_id in (select id from stock_location
                                                                                                where usage = 'internal')
                                    union all
                                    select st.product_qty*-1
                                        from stock_move st 
                                        where st.state='done' and st.product_id=%s and st.location_id in (select id from stock_location
                                                                                                where usage = 'internal')
                                    )foo
                        '''%(product_id,product_id)
                self.cr.execute(sql)
                ton_sl = self.cr.dictfetchone()['ton_sl']
                    
                res[product_id] = {
                        'on_hand_qty': ton_sl,
                    }
                return ton_sl
    

    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']
        indent_no = wizard_data['pur_product_id']
        dept = wizard_data['department_id']
        section = wizard_data['section_id']
        requ = wizard_data['requisitioner']
        project = wizard_data['project_id']
        proj_sec = wizard_data['project_section_id']
        status = wizard_data['state']

                
        sql = '''
                select pi.name as indent_no,pp.pur_product_id,pp.date_indent_relate as ind_date,pp.doc_type_relate as doc_type,
                pp.department_id_relate,d.name as dept,pp.section_id_relate,s.name as sec,(pp.product_uom_qty*pp.price_unit) as total_val,
                pp.requisitioner_relate,pp.product_id,pr.name_template as mat_desc,pr.default_code as mat_code,pp.price_unit as unit_price,
                pp.description,pp.uom_po_id,u.name as uom,pp.id as line_id,pp.mrs_qty as res_qty,pp.state as status,
                e.name_related as requisitioner,e.employee_id as requisitioner_code,e.last_name as lname,pp.product_uom_qty as ind_qty,
                pp.product_id as prod_id,prr.name as project,prs.name as proj_sec,COALESCE(sm.id,0) as stock_id
                from tpt_purchase_product pp
                inner join tpt_purchase_indent pi on (pi.id = pp.pur_product_id)
                inner join hr_department d on (d.id = pp.department_id_relate)
                inner join arul_hr_section s on (s.id = pp.section_id_relate)
                left join product_product pr on (pr.id = pp.product_id)
                left join product_uom u on (u.id = pp.uom_po_id)
                left join hr_employee e on (e.id = pp.requisitioner_relate)
                left join stock_move sm on (sm.po_indent_id = pi.id and sm.product_id = pp.product_id)
                left join tpt_project prr on (pr.id = pi.project_id)
                left join tpt_project_section prs on (prs.id = pi.project_section_id)
            '''
            
        if date_from or date_to or indent_no or dept or section or requ or project or proj_sec or status:
                    str = " where "
                    sql = sql+str
        if date_from and not date_to:
                    str = " pp.date_indent_relate <= '%s'"%(date_from)
                    sql = sql+str               
        if date_to and not date_from:
                    str = " pp.date_indent_relate <= '%s'"%(date_to)
                    sql = sql+str
        if date_to and date_from:
                    str = " pp.date_indent_relate between '%s' and '%s'"%(date_from,date_to)
                    sql = sql+str
        if indent_no and not date_to and not date_from:
                    str = " pp.pur_product_id = %s"%(indent_no[0])
                    sql = sql+str
        if indent_no and (date_to or date_from):
                    str = " and pp.pur_product_id = %s"%(indent_no[0])
                    sql = sql+str
        if dept and not date_to and not date_from and not indent_no:
                    str = " pp.department_id_relate = %s "%(dept[0])
                    sql = sql+str
        if dept and (date_to or date_from or indent_no):
                    str = " and pp.department_id_relate = %s "%(dept[0])
                    sql = sql+str
        if section and not dept and not indent_no and not date_to and not date_from:
                    str = " pp.section_id_relate = %s "%(section[0])
                    sql = sql+str
        if section and (date_to or date_from or indent_no or dept):
                    str = " and pp.section_id_relate = %s "%(section[0])
                    sql = sql+str
        if requ and not section and not dept and not indent_no and not date_to and not date_from: 
                    str = " pp.requisitioner_relate = %s "%(requ[0])
                    sql = sql+str
        if requ and (date_to or date_from or indent_no or dept or section):
                    str = " and pp.requisitioner_relate = %s "%(requ[0])
                    sql = sql+str
        if project and not requ and not section and not dept and not indent_no and not date_to and not date_from:
                    str = " pi.project_id = %s "%(project[0])
                    sql = sql+str
        if project and (date_to or date_from or indent_no or dept or section or requ):
                    str = " and pi.project_id = %s "%(project[0])
                    sql = sql+str
        if proj_sec and not project and not requ and not section and not dept and not indent_no and not date_to and not date_from:
                    str = " pi.project_section_id = %s"%(proj_sec[0])
                    sql = sql+str
        if proj_sec and (date_to or date_from or indent_no or dept or section or requ or project):
                    str = " and pi.project_section_id = %s "%(proj_sec[0])
                    sql = sql+str
        if status and not proj_sec and not project and not requ and not section and not dept and not indent_no and not date_to and not date_from:
                    str = " pp.state = '%s' "%(status)
                    sql = sql+str
        if status and (date_to or date_from or indent_no or dept or section or requ or project or proj_sec):
                    str = " and pp.state = '%s' "%(status)
                    sql = sql+str                           
                     
        sql=sql+" order by pp.date_indent_relate,pi.name"  
        self.cr.execute(sql)
        return self.cr.dictfetchall()
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

