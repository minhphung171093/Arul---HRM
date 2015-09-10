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
            #--------------------------- 'get_pending_qty':self.get_pending_qty,
           
            
            
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['date_from']:
            date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
            return date.strftime('%d/%m/%Y')
        else:
            return ''
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        if wizard_data['date_to']:
            date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
            return date.strftime('%d/%m/%Y')
        else:
            return ''
    #===========================================================================
    # def get_pending_qty(self,po_no,pol_id):
    #      
    #         po_qty = 0
    #         grn_qty = 0
    #         if po_no:                
    #            sql = '''
    #                   select case when sum(sm.product_qty)>0 then sum(sm.product_qty) else 0 end product_qty 
    #                        from stock_move sm
    #                        inner join stock_picking sp on sm.picking_id=sp.id
    #                        inner join purchase_order po on sp.purchase_id=po.id
    #                        inner join purchase_order_line pol on po.id=pol.order_id
    #                        where sm.state in ('assigned','cancel') and po.id=%s
    #                     '''%(po_no)
    #         self.cr.execute(sql)
    #         for move in self.cr.dictfetchall():
    #               if move['product_qty ']:
    #                     po_qty = move['product_qty']
    #                     pen_qty = po_qty - grn_qty
    #                     return pen_qty or 0.00                    
    #         else:
    #           return grn_qty or 0.000
    #===========================================================================
    #===========================================================================
    # def get_pending_qty(self,po_no,pol_id):
    #         po_qty = 0
    #         grn_qty = 0
    #         if po_no:
    #             sql = '''
    #                        select case when sum(sm.product_qty)>0 then sum(sm.product_qty) else 0 end product_qty 
    #                        from stock_move sm
    #                        inner join stock_picking sp on sm.picking_id=sp.id
    #                        inner join purchase_order po on sp.purchase_id=po.id
    #                        inner join purchase_order_line pol on po.id=pol.order_id
    #                        where sm.state in  ('assigned','cancel') and po.id=%s                       
    #                     '''%(po_no)
    #             self.cr.execute(sql)
    #             grn_qty = self.cr.fetchone()
    #             grn_qty = grn_qty[0]
    #                       
    #             sql = '''
    #                        select pol.product_qty po_qty 
    #                        from purchase_order_line pol
    #                        where pol.order_id=(select id from purchase_order where id=%s)
    #                     '''%(pol_id)
    #             self.cr.execute(sql)
    #             po_qty = self.cr.fetchone()
    #             po_qty = po_qty[0]      
    #             return  po_qty - grn_qty or 0.000
    #===========================================================================
                
                
                         
    
    
    def get_status(self,type):
        if type == 'draft':
            res = 'Draft'
        if type == 'done':
            res = 'Approve'
        if type == 'partially':
            res = 'Partially Issued'
        if type == 'closed':
            res = 'Closed'
        return res or ''

    def get_invoice(self):
        res = {}
        wizard_data = self.localcontext['data']['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to'] 
        po_no=wizard_data['po_no']
        grn_no=wizard_data['grn_no']
        requisitioner=wizard_data['requisitioner']
        state=wizard_data['state']
        project_id=wizard_data['project_id']
        project_section_id=wizard_data['project_section_id'] 
       
        #raise osv.except_osv(_('Warning!'),_(grn_no))
  
        sql = '''
                   select sp.id as grn_id, po.id as po_id,sp.name grn_no,sp.date as grn_date,po.name as po_no, rp.name supplier,
                   pr.name as proj_name,prs.name as proj_sec_name,
                      (case when po.po_document_type='raw' then 'VV Raw material PO' 
                       when po.po_document_type='asset' then 'VV Capital PO' 
                       when po.po_document_type='standard' then 'VV Standard PO'
                       when po.po_document_type='local' then 'VV Local PO'
                       when po.po_document_type='return' then 'VV Return PO'
                       when po.po_document_type='service' then 'VV Service PO'
                       when po.po_document_type='out' then 'VV Out Service PO'
                       else '' end) as doc_type,
                       pi.name as po_indent_no,pp.default_code||'-'||pt.name as product,
                       sm.item_text, sm.description, sm.product_qty as prod_qty,pu.name as product_uom,
                      (case when sm.action_taken = 'direct' then 'Direct Stock Update' 
                       when sm.action_taken ='need' then 'Need Inspection'    
                       when sm.action_taken ='move' then 'Move To Consumption' else '' end) as  act_take,
                       sm.bin_location,
                       (case when sm.state = 'waiting' then 'Draft' 
                                   when sm.state ='cancel' then 'Cancelled'
                                   when sm.state ='confirmed' then 'Waiting Availability'
                                   when sm.state ='assigned' then 'Ready to Receive'    
                                   when sm.state ='done' then 'Received' else '' end)  as state, 
                       emp.name_related as requisitioner,po.id as po_id,pol.order_id as order_line_id
                       
                      from stock_move sm
                      inner join stock_picking sp on sm.picking_id=sp.id
                      inner join purchase_order po on sp.purchase_id=po.id 
                      inner join res_partner rp on (sp.partner_id = rp.id)
                      inner join purchase_order_line pol on po.id=pol.order_id and sm.description=pol.description
                      inner join tpt_purchase_indent pi on pol.po_indent_no=pi.id
                      inner join product_uom pu on sm.product_uom=pu.id 
                      inner join product_product pp on sm.product_id=pp.id 
                      inner join product_template pt on sm.product_id=pt.id 
                      inner join hr_employee emp on pi.requisitioner=emp.id 
                      left join tpt_project pr on  pi.project_id = pr.id
                      left join tpt_project_section prs on pi.project_section_id = prs.id  
                    '''
        
        
        if date_from or date_to or po_no or grn_no or requisitioner or project_id or project_section_id or state:
                    str = "where "
                    sql = sql+str
                    
        if (date_from and not date_to and not po_no and not grn_no and not requisitioner and not project_id and not project_section_id and not state ) or (date_from and not date_to and (po_no or grn_no or requisitioner or project_id or project_section_id or state )):
                    str = " sp.date <= '%s'"%(date_from)
                    sql = sql+str                  
                
        if (date_to and not date_from and not po_no and not grn_no and not requisitioner and not project_id and not project_section_id and not state ) or (date_to and not date_from and (po_no or grn_no or requisitioner or project_id or project_section_id or state )):
                    str = " sp.date <= '%s'"%(date_to)
                    sql = sql+str
                
                
        if (date_to and date_from and not po_no and not grn_no and not requisitioner and not project_id and not project_section_id and not state) or ((date_to and date_from) and (po_no or grn_no or requisitioner or project_id or project_section_id or state )):
                    if date_to==date_from:
                        str = "extract(day from sp.date)=%s and extract(month from sp.date)=%s and extract(year from sp.date)=%s "%(int(date_from[8:10]), int(date_from[5:7]), date_from[:4])
                    else:
                        str = "sp.date between '%s' and '%s' "%(date_from, date_to) 
                    sql = sql+str
                    
                    
        if grn_no and not po_no and not date_to and not date_from and not requisitioner and not project_id and not project_section_id and not state :
                    str = " sp.id = %s"%grn_no[0]#(grn_no.purchase_id.id)
                    sql = sql+str
        if grn_no and (date_to or date_from or po_no) and (date_to or date_from or po_no or requisitioner or project_id or project_section_id or state):
                    str = " and sp.id = %s "%(grn_no[0])
                    sql = sql+str         
                
        if po_no and not date_to and not date_from and not grn_no and not requisitioner and not project_id and not project_section_id and not state :
                    str = " po.id = %s"%(po_no[0])
                    sql = sql+str 
        if po_no and (date_to or date_from) and (date_to or date_from or grn_no or requisitioner or project_id or project_section_id or state):
                    str = " and po.id = %s"%(po_no[0])
                    sql = sql+str
                    
        if state and not po_no and not date_to and not date_from and not grn_no and not requisitioner and not project_id and not project_section_id :
                    str = " sm.state = '%s'"%(state)
                    sql = sql+str
        if state and (date_to or date_from or po_no or grn_no or requisitioner or project_id or project_section_id) and (date_to or date_from or po_no or grn_no or requisitioner or project_id or project_section_id ):
                    str = " and sm.state = '%s' "%(state)
                    sql = sql+str
                    
        if requisitioner and not po_no and not date_to and not date_from and not grn_no and not project_id and not project_section_id and not state :
                    str = " pi.requisitioner = %s"%(requisitioner[0])
                    sql = sql+str
        if requisitioner and (date_to or date_from or po_no or grn_no) and (date_to or date_from or po_no or grn_no or project_id or project_section_id or state):
                    str = " and pi.requisitioner = %s "%(requisitioner[0])
                    sql = sql+str 
        if project_id and not po_no and not date_to and not date_from and not grn_no and not requisitioner and not state and not project_section_id: # or (project_sec_id):
                    str = " pr.id = %s"%(project_id[0])
                    sql = sql+str
        if project_id and (date_to or date_from or po_no or grn_no or requisitioner  or state or project_section_id): # and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_sec_id):
                    str = " and pr.id = %s "%(project_id[0])
                    sql = sql+str    
        if project_section_id and not po_no and not date_to and not date_from and not grn_no and not requisitioner and not state and  not project_id:
                    str = " prs.id = %s"%(project_section_id)
                    sql = sql+str
        if project_section_id and (date_to or date_from or po_no or grn_no or requisitioner or state or project_id):
                    str = " and prs.id = %s "%(project_section_id)
                    sql = sql+str               
        sql=sql+" order by sp.date asc" 
                        
        self.cr.execute(sql)
        return self.cr.dictfetchall()
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

