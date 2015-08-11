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
           
            
            
        })
        
    def get_date_from(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_from'], DATE_FORMAT)        
        return date.strftime('%d/%m/%Y')
    
    def get_date_to(self):
        wizard_data = self.localcontext['data']['form']
        date = datetime.strptime(wizard_data['date_to'], DATE_FORMAT)
        return date.strftime('%d/%m/%Y')
    
    def get_pending_qty(po_no):
            po_qty = 0
            grn_qty = 0
            if po_no:
                sql = '''
                           select case when sum(sm.product_qty)>0 then sum(sm.product_qty) else 0 end product_qty from stock_move sm
                            inner join stock_picking sp on sm.picking_id=sp.id
                            inner join purchase_order po on sp.purchase_id=po.id
                            inner join purchase_order_line pol on po.id=pol.order_id
                            where po.id=%s
                        '''%(po_no.id)
                cr.execute(sql)
                grn_qty = cr.fetchone()
                grn_qty = grn_qty[0]
                        
                sql = '''
                           select pol.product_qty po_qty from purchase_order_line pol
                        where pol.order_id=(select id from purchase_order where id=%s)
                        '''%(po_no.id)
                cr.execute(sql)
                po_qty = cr.fetchone()
                po_qty = po_qty[0]
      
                return po_qty-grn_qty or 0.000
    
    
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
        project_sec_id=wizard_data['project_section_id'] 
       
                
        sql = '''
                   select sp.name grn_no,sp.date as grn_date,po.name po_no, rp.name supplier,
                      po.po_document_type as doc_type,pi.name as po_indent_no,pp.default_code||'-'||pt.name as product,
                      sm.item_text, sm.description, sm.product_qty as prod_qty,pu.name as product_uom,
                      sm.action_taken as act_take,sm.bin_location,sm.state as state, emp.name_related requisitioner
                      from stock_move sm
                      inner join stock_picking sp on sm.picking_id=sp.id
                      inner join purchase_order po on sp.purchase_id=po.id
                      inner join res_partner rp on (sp.partner_id = rp.id)
                      inner join purchase_order_line pol on po.id=pol.order_id--pi.id = pol.po_indent_no
                      inner join tpt_purchase_indent pi on pol.po_indent_no=pi.id
                      inner join product_uom pu on sm.product_uom=pu.id 
                      inner join product_product pp on sm.product_id=pp.id 
                      inner join product_template pt on sm.product_id=pt.id 
                      inner join hr_employee emp on pi.requisitioner=emp.id
                      where sp.date between '%s' and '%s' 
                    '''%(date_from, date_to)
              

        self.cr.execute(sql)
        return self.cr.dictfetchall()
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

