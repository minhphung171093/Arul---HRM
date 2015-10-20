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
            'get_store_qty':self.get_store_qty,
            'get_insp_qty':self.get_insp_qty,
            'get_block_qty':self.get_block_qty,
            'get_action_taken':self.get_action_taken,
            'get_doc_type':self.get_doc_type,
            'get_po_no':self.get_po_no,
            
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
                
    
    def get_store_qty(self,action_taken,grn,picking_id):
            
            if action_taken == 'direct':
                           
                sql = '''
                          select case when sm.product_qty>0 then sm.product_qty else 0 end as prod_qty 
                          from stock_move sm
                          join stock_picking sp on (sp.id = sm.picking_id)
                          where sp.name = '%s' and sm.action_taken = 'direct' and sp.state = 'done' and 
                          sm.picking_id = %s                           
                       '''%(grn,picking_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    if move['prod_qty']:
                        str_qty = move['prod_qty']                    
                        return str_qty
                    else:
                        return 0.000
                    
            elif action_taken == 'need':
                           
                sql = '''
                      select case when tqi.qty_approve>0 then tqi.qty_approve else 0 end as prod_qty              
                      from stock_move sm
                      join stock_picking sp on (sp.id = sm.picking_id)
                      join tpt_quanlity_inspection tqi on (tqi.need_inspec_id = sm.id and tqi.name = sm.picking_id)
                      where sp.name = '%s' and sm.action_taken = 'need' and sm.picking_id = %s
                      and sp.state = 'done'                     
                       '''%(grn,picking_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    if move['prod_qty']:
                        str_qty = move['prod_qty']                    
                        return str_qty
                    else:
                        return 0.000
            else:
                return 0.000
                    
    def get_insp_qty(self,action_taken,grn,picking_id):            
                                
            if action_taken == 'need':
                           
                sql = '''
                      select case when tqi.remaining_qty>0 then tqi.remaining_qty else 0 end as rem_qty              
                      from stock_move sm
                      join stock_picking sp on (sp.id = sm.picking_id)
                      join tpt_quanlity_inspection tqi on (tqi.need_inspec_id = sm.id and tqi.name = sm.picking_id)
                      where sp.name = '%s' and sm.action_taken = 'need' and sm.picking_id = %s 
                      and sp.state = 'done'                     
                       '''%(grn,picking_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    if move['rem_qty']:
                        rem_qty = move['rem_qty']              
                        return rem_qty
                    else:
                        return 0.000
            else:
                return 0.000
        
    def get_block_qty(self,action_taken,grn,picking_id):            
                                
            if action_taken == 'need':
                           
                sql = '''
                      select COALESCE(qty,0)-(COALESCE(qty_approve,0)+COALESCE(remaining_qty,0)) as block_qty            
                      from stock_move sm
                      join stock_picking sp on (sp.id = sm.picking_id)
                      join tpt_quanlity_inspection tqi on (tqi.need_inspec_id = sm.id and tqi.name = sm.picking_id)
                      where sp.name = '%s' and sm.action_taken = 'need' and sm.picking_id = %s 
                      and sp.state = 'done'                     
                       '''%(grn,picking_id)
                self.cr.execute(sql)
                for move in self.cr.dictfetchall():
                    if move['block_qty']:
                        rem_qty = move['block_qty']              
                        return rem_qty
                    else:
                        return 0.000
            else:
                return 0.000
            
    def get_action_taken(self,type):            
            if type == 'direct':
                return 'Direct Stock Update' 
            if type == 'move':
                return 'Move To Consumption'
            if type == 'need':
                return 'Need Inspection'
        
    def get_status(self,type):                
        if type == 'draft':
            return 'Draft' 
        if type == 'auto':
            return 'Waiting Another Operation'
        if type == 'confirmed':
            return 'Waiting Availability'
        if type == 'assigned':
            return 'Ready to Receive'
        if type == 'done':
            return 'Received'
        if type == 'cancel':
            return 'Cancelled'          
    
    def get_doc_type(self,type):
        if type == 'raw':
            return 'VV Raw Material PO'
        if type == 'asset':
            return 'VV Asset PO'
        if type == 'standard':
            return 'VV Standard PO'
        if type == 'local':
            return 'VV Local PO'
        if type == 'return':
            return 'VV Return PO'
        if type == 'service':
            return 'VV Service PO'            
        if type == 'out':
            return 'VV Out Service PO'
    
    def get_po_no(self,po_id):        
        acc_obj = self.pool.get('purchase.order')
        acc = acc_obj.browse(self.cr,self.uid,po_id)
        po_no = acc.name
        return po_no

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
                      select sp.name as grn_no,sp.id as grn_no_1,sp.date as grn_date,sp.purchase_id as po_no,rp.name supplier, rp.vendor_code supplier_code,
                      pr.name as proj_name,prs.name as proj_sec_name,sp.document_type as doc_type,pi.name as po_indent_no_1,
                      pi.id as po_indent_no,pp.default_code||'-'||pt.name as product,sm.item_text,sm.description,
                      sm.product_qty as prod_qty,pu.name as product_uom,sm.action_taken as act_take,sm.bin_location,                  
                      sp.state as state,emp.name_related as requisitioner,sm.picking_id as pick_id,sm.action_taken as actn_taken
                      from stock_move sm
                      inner join stock_picking sp on sm.picking_id=sp.id
                      inner join res_partner rp on (sp.partner_id = rp.id)                     
                      inner join tpt_purchase_indent pi on (pi.id = sm.po_indent_id)
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
        if date_from and not date_to:
                    str = " sp.date <= '%s'"%(date_from)
                    sql = sql+str               
        if date_to and not date_from:
                    str = " sp.date <= '%s'"%(date_to)
                    sql = sql+str               
        if date_to and date_from:
                    if date_to == date_from:
                        str = "extract(day from sp.date)=%s and extract(month from sp.date)=%s and extract(year from sp.date)=%s "%(int(date_from[8:10]), int(date_from[5:7]), date_from[:4])
                    else:
                        str = "sp.date between '%s' and '%s' "%(date_from, date_to) 
                    sql = sql+str        
        if grn_no and not date_to and not date_from:
                    str = " sp.id = %s"%(grn_no[0])
                    sql = sql+str
        if grn_no and (date_to or date_from):
                    str = " and sp.id = %s"%(grn_no[0])
                    sql = sql+str        
        if po_no and not date_to and not date_from and not grn_no:
                    str = " sp.purchase_id = %s "%(po_no[0])
                    sql = sql+str
        if po_no and (date_to or date_from or grn_no):
                    str = " and sp.purchase_id = %s "%(po_no[0])
                    sql = sql+str
        if state and not po_no and not grn_no and not date_to and not date_from:
                    str = " sm.state = '%s' "%(state)
                    sql = sql+str
        if state and (date_to or date_from or po_no or grn_no):
                    str = " and sm.state = '%s' "%(state)
                    sql = sql+str
        if requisitioner and not state and not po_no and not grn_no and not date_to and not date_from: 
                    str = " pi.requisitioner = %s "%(requisitioner[0])
                    sql = sql+str
        if requisitioner and (date_to or date_from or state or po_no or grn_no):
                    str = " and pi.requisitioner = %s "%(requisitioner[0])
                    sql = sql+str
        if project_id and not requisitioner and not state and not po_no and not grn_no and not date_to and not date_from:
                    str = " pr.id = %s "%(project_id[0])
                    sql = sql+str
        if project_id and (date_to or date_from or requisitioner or state or po_no or grn_no):
                    str = " and pr.id = %s "%(project_id[0])
                    sql = sql+str
        if project_section_id and not project_id and not requisitioner and not state and not po_no and not grn_no and not date_to and not date_from:
                    str = " prs.id = %s"%(project_section_id[0])
                    sql = sql+str
        if project_section_id and (date_to or date_from or project_id or requisitioner or state or po_no or grn_no):
                    str = " and prs.id = %s "%(project_section_id[0])
                    sql = sql+str
        sql=sql+" order by sp.date asc" 
                        
        self.cr.execute(sql)
        return self.cr.dictfetchall()
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

