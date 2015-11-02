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
            'get_req_name_code':self.get_req_name_code,
            'get_status':self.get_status,
            #'get_on_hand_qty':self.get_on_hand_qty,
            'get_pending_qty' : self.get_pending_qty,
            'get_issue_qty_count':self.get_issue_qty_count,
            
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = ''
        if wizard_data['date_from']:
            date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)      
            date = date.strftime('%d/%m/%Y')
        return date
        
          
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = ''
        if wizard_data['date_to']:
            date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
            date = date.strftime('%d/%m/%Y')
        return date
    
    def get_req_name_code(self,name,code,lname):
        req_name = name
        req_code = code
        req_lname = lname 
        if req_name and req_code:        
            return '['+req_code+']' +req_name+' ' +lname
        else:
            return ' '
    
    def get_status(self,type):
        if type == 'draft':
            return 'Draft'
        if type == 'done':
            return 'Approve'
        if type == 'partially':
            return 'Partially Issued'
        if type == 'closed':
            return 'Closed'
        
    
    def get_pending_qty(self,move_line_id,req_qty,check_count):
        
        if check_count > 0:                
            sql = '''
                    select sum(product_isu_qty) as issue_qty                   
                    from tpt_material_issue_line isl
                    inner join tpt_material_issue ss on (ss.id = isl.material_issue_id)
                    where state = 'done' and request_line_id = %s
                  '''%(move_line_id)
            self.cr.execute(sql)
            for move in self.cr.dictfetchall():
                  if move['issue_qty']:
                        isu_qty = move['issue_qty']
                        pen_qty = req_qty - isu_qty
                        return pen_qty or 0.00                    
        else:
            return req_qty or 0.000
                
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
    
    
    def get_on_hand_qty(self,line_id):                
        res = {}
        req_line_obj = self.pool.get('tpt.material.request.line')
        line = req_line_obj.browse(self.cr,self.uid,line_id)        
        #for line in request_line:
            
        onhand_qty = 0
        location_id = False
        locat_ids = []
        parent_ids = []
#             product_id = product_obj.browse(cr,uid,order_line['product_id'])
        cate_name = line.product_id.categ_id and line.product_id.categ_id.cate_name or False
        if cate_name == 'finish':
                lot = line.prodlot_id and line.prodlot_id.id or False
                parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
                if locat_ids:
                    location_id = locat_ids[0]
                    if lot:
                        sql = '''
                            select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
                                (select st.product_qty as product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                                        and prodlot_id = %s
                                 union all
                                 select st.product_qty*-1 as product_qty
                                    from stock_move st 
                                    where st.state='done'
                                    and st.product_id=%s
                                                and location_id=%s
                                                and location_dest_id != location_id
                                                and prodlot_id = %s
                                )foo
                        '''%(line.product_id.id,location_id,lot,line.product_id.id,location_id,lot)
                    else:
                        sql = '''
                            select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end onhand_qty from 
                                (select st.product_qty as product_qty
                                    from stock_move st 
                                    where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                                 union all
                                 select st.product_qty*-1 as product_qty
                                    from stock_move st 
                                    where st.state='done'
                                    and st.product_id=%s
                                                and location_id=%s
                                                and location_dest_id != location_id
                                )foo
                        '''%(line.product_id.id,location_id,line.product_id.id,location_id)
                    self.cr.execute(sql)
                    onhand_qty = self.cr.dictfetchone()['onhand_qty']
        if cate_name == 'raw':
                parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                if locat_ids:
                    location_id = locat_ids[0]
        if cate_name == 'spares':
                parent_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','=','Store'),('usage','=','view')])
                if parent_ids:
                    locat_ids = self.pool.get('stock.location').search(self.cr, self.uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
                if locat_ids:
                    location_id = locat_ids[0]
        if location_id and cate_name != 'finish':
                sql = '''
                    select case when sum(foo.product_qty)!=0 then sum(foo.product_qty) else 0 end as onhand_qty from 
                        (select st.product_qty as product_qty
                            from stock_move st 
                            where st.state='done' and st.product_id=%s and st.location_dest_id=%s and st.location_dest_id != st.location_id
                         union all
                         select st.product_qty*-1 as product_qty
                            from stock_move st 
                            where st.state='done'
                                    and st.product_id=%s
                                        and location_id=%s
                                        and location_dest_id != location_id
                        )foo
                '''%(line.product_id.id,location_id,line.product_id.id,location_id)
                self.cr.execute(sql)
                onhand_qty = self.cr.dictfetchone()['onhand_qty']
                
        res[line.id] = {
                            'on_hand_qty': onhand_qty,
                        }
        return onhand_qty or 0.000
    

    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']        
        mat_req_no=wizard_data['material_request_id']
        cost_cent=wizard_data['cost_center_id']
        requisitioner=wizard_data['requisitioner']
        #pend_qty=wizard_data['pend_qty']
        department=wizard_data['department_id']
        section=wizard_data['section_id']
        state=wizard_data['state']
        mat_code=wizard_data['product_id']
        project_id=wizard_data['project_id']
        project_sec_id=wizard_data['project_section_id']       
        #mat_desc=wizard_data['dec_material']
                
        sql = '''
            select mr.name as mat_req_no,mr.date_request as mat_req_date,mr.date_expec as exp_date,d.name as department,
            s.name as section,p.bin_location as bin_loc,e.name_related as requisitioner,e.employee_id as requisitioner_code,
            e.last_name as lname,res.login as req_raise_by,p.default_code as mat_code,p.name_template as mat_desc,
            pr.name as proj_name,cc.name as cost_center,u.name as uom,mrl.product_uom_qty as req_qty,            
            mr.state as state,prs.name as proj_sec_name,mrl.id as lineid
            from tpt_material_request_line mrl
            join tpt_material_request mr on (mr.id = mrl.material_request_id)
            join hr_department d on (d.id = mr.department_id)
            join arul_hr_section s on (s.id = mr.section_id)
            left join hr_employee e on (e.id = mr.requisitioner)
            join res_users res on (res.id = mr.create_uid) 
            join product_product p on (p.id = mrl.product_id)
            join product_uom u on (u.id = mrl.uom_po_id)            
            left join tpt_cost_center cc on (cc.id = mr.cost_center_id)
            left join tpt_project pr on (pr.id = mr.project_id)
            left join tpt_project_section prs on (prs.id = mr.project_section_id)            
            '''
        
        if date_from or date_to or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_id or project_sec_id:
                    str = " where "
                    sql = sql+str
        if (date_from and not date_to and not mat_req_no and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_id and not project_sec_id) or (date_from and not date_to and (mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_id or project_sec_id)):
                    str = " mr.date_request <= '%s'"%(date_from)
                    sql = sql+str               
        if (date_to and not date_from and not mat_req_no and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_id and not project_sec_id) or (date_to and not date_from and (mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_id or project_sec_id)):
                    str = " mr.date_request <= '%s'"%(date_to)
                    sql = sql+str
        if (date_to and date_from and not mat_req_no and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_id and not project_sec_id) or ((date_to and date_from) and (mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_id or project_sec_id)):
                    str = " mr.date_request between '%s' and '%s'"%(date_from,date_to)
                    sql = sql+str                    
        if mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mrl.material_request_id = %s"%(mat_req_no[0])
                    sql = sql+str
        if mat_req_no and (date_to or date_from) and (date_to or date_from or cost_cent or requisitioner or department or section or state or mat_code or project_id or project_sec_id):
                    str = " and mrl.material_request_id = %s"%(mat_req_no[0])
                    sql = sql+str
        if cost_cent and not mat_req_no and not date_to and not date_from and not requisitioner and not department and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.cost_center_id = %s "%(cost_cent[0])
                    sql = sql+str
        if cost_cent and (date_to or date_from or mat_req_no) and (date_to or date_from or mat_req_no or requisitioner or department or section or state or mat_code or project_id or project_sec_id):
                    str = " and mr.cost_center_id = %s "%(cost_cent[0])
                    sql = sql+str                    
        if requisitioner and not mat_req_no and not date_to and not date_from and not cost_cent and not department and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.requisitioner = %s "%(requisitioner[0])
                    sql = sql+str
        if requisitioner and (date_to or date_from or mat_req_no or cost_cent) and (date_to or date_from or mat_req_no or cost_cent or department or section or state or mat_code or project_id or project_sec_id):
                    str = " and mr.requisitioner = %s "%(requisitioner[0])
                    sql = sql+str                
        if department and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.department_id = %s "%(department[0])
                    sql = sql+str
        if department and (date_to or date_from or mat_req_no or cost_cent or requisitioner) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or section or state or mat_code or project_id or project_sec_id):
                    str = " and mr.department_id = %s "%(department[0])
                    sql = sql+str
        if section and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.section_id = %s "%(section[0])
                    sql = sql+str
        if section and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or state or mat_code or project_id or project_sec_id):
                    str = " and mr.section_id = %s "%(section[0])
                    sql = sql+str
        if state and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not mat_code and not project_id and not project_sec_id:
                    str = " mr.state = '%s'"%(state)
                    sql = sql+str
        if state and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or mat_code or project_id or project_sec_id):
                    str = " and mr.state = '%s' "%(state)
                    sql = sql+str
        if mat_code and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not project_id and not project_sec_id:
                    str = " mrl.product_id = %s"%(mat_code[0])
                    sql = sql+str
        if mat_code and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or project_id or project_sec_id):
                    str = " and mrl.product_id = %s "%(mat_code[0])
                    sql = sql+str
        if project_id and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_sec_id:
                    str = " pr.id = %s"%(project_id[0])
                    sql = sql+str
        if project_id and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_sec_id):
                    str = " and prs.id = %s "%(project_id[0])
                    sql = sql+str
        if project_sec_id and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_id:
                    str = " prs.id = %s"%(project_sec_id[0])
                    sql = sql+str
        if project_sec_id and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_id):
                    str = " and prs.id = %s "%(project_sec_id[0])
                    sql = sql+str  
        #=======================================================================
        # if mat_req_no:
        #     str = " and mrl.material_request_id = %s"%(mat_req_no[0])
        #     sql = sql+str
        # if cost_cent:
        #     str = " and mr.cost_center_id = %s "%(cost_cent[0])
        #     sql = sql+str
        # if requisitioner:
        #     str = " and mr.requisitioner = %s "%(requisitioner[0])
        #     sql = sql+str
        # #=======================================================================
        # # if pend_qty:
        # #     str = " and (msl.product_uom_qty-msl.product_isu_qty) = %s "%(pend_qty)
        # #     sql = sql+str
        # #=======================================================================
        # if department:
        #     str = " and mr.department_id = %s "%(department[0])
        #     sql = sql+str 
        # if section:
        #     str = " and mr.section_id = %s "%(section[0])
        #     sql = sql+str 
        # if state:
        #     str = " and mr.state = '%s' "%(state)
        #     sql = sql+str 
        # if mat_code:
        #     str = " and mrl.product_id = %s "%(mat_code[0])
        #     sql = sql+str
        # if project_id:
        #     str = " and pr.id = %s "%(project_id[0])
        #     sql = sql+str
        # if project_sec_id:
        #     str = " and prs.id = %s "%(project_sec_id[0])
        #     sql = sql+str        
        # sql=sql+" order by mr.date_request"
        #=======================================================================
       
            
        self.cr.execute(sql)
        return self.cr.dictfetchall()
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

