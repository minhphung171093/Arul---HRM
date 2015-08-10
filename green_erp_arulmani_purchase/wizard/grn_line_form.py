# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare


class grn_details_report(osv.osv_memory):
    _name = "grn.details.report"
    _columns = {
             'date_from':fields.date('Date From', required=True),
             'date_to':fields.date('Date To', required=True),
             'po_no': fields.many2one('purchase.order' ,string='Po Number'),          
             'grn_no': fields.many2one('stock.picking','GRN No', size = 1024),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'project_id': fields.many2one('tpt.project','Project Title'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),
             'pend_qty': fields.float('Pending Qty'), 
             'state':fields.selection([('waiting', 'Draft'),('cancel', 'Cancelled'),('confirmed', 'Waiting Availability'),('assigned', 'Ready to Receive'),('done', 'Received')], string='State'),
                             
             'grn_line_id': fields.one2many('grn.line.details.report', 'grn_lines_id', 'GRN Line Details'),
    }
     
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'grn.detail.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'grn_line_report_pdf', 'datas': datas}
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'grn.detail.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'grn_line_report_xls', 'datas': datas}   
     

grn_details_report()

class grn_line_details_report(osv.osv_memory):
    _name = "grn.line.details.report"
     
    _columns = {
        'grn_lines_id': fields.many2one('grn.details.report','GRN Line Details', ondelete='cascade'),
        'grn_no': fields.char('GRN no',size = 1024),
        'grn_date': fields.date('GRN date'),
        'supplier': fields.char('Supplier'),
        'doc_type': fields.selection([
            ('raw','VV Raw Material Po'),('asset','VV Asset Po'),('standard','VV Standard Po'),('local','VV Local Po'),('return','VV Return Po'),('service','VV Service Po'),('out','VV Out Service Po')], string='Po Document Type'),
        'po_no': fields.char(string='Po Number',size = 1024, ),
        'po_indent_id': fields.char('Po Indent No'),
        'description':fields.char('Description', size = 50, readonly = True),
        'item_text':fields.text('Item Text'),
        'product_id': fields.char('Product'),
        'qty': fields.float('Quantity'),
        'pend_qty': fields.float('Pending Qty'),
        'uom': fields.char('Uom', size = 1024),
        'bin': fields.char('Bin Location', size = 1024),
        'action_taken':fields.selection([('direct','Direct Stock Update'),('move','Move To Consumption'),('need','Need Inspection')],'Action To Be Taken'),
        'state': fields.char('State', size = 1024),
                 
            
 }
grn_line_details_report()


class grn_detail_line_report(osv.osv_memory):
     _name = "grn.detail.line.report"
     
     _columns = {
             'date_from':fields.date('Date From', required=True),
             'date_to':fields.date('Date To', required=True),
             'po_no': fields.many2one('purchase.order','Purchase Order No', size = 1024),             
             'grn_no': fields.many2one('stock.picking','GRN No', size = 1024),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'project_id': fields.many2one('tpt.project','Project Title'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),
             'pend_qty': fields.float('Pending Qty'), 
             'state':fields.selection([('waiting', 'Draft'),('cancel', 'Cancelled'),('confirmed', 'Waiting Availability'),('assigned', 'Ready to Receive'),('done', 'Received')], string='State'),                      
     }
 
     def _check_date(self, cr, uid, ids, context=None):
         for date in self.browse(cr, uid, ids, context=context):
             if date.date_to < date.date_from:
                 raise osv.except_osv(_('warning!'),_('date to is not less than date from'))
                 return False
         return True
     _constraints = [
         (_check_date, 'identical data', []),
     ]
     
     
     def print_report(self, cr, uid, ids, context=None):         
         
        
            
        def get_req_name_code(name):
                req_name = name
         
                return '['+req_name+']'
                
                
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
               
        def get_status(type):
                if type == 'cancel':
                    res = 'cancelled'
                if type == 'done':
                    res = 'received'
                if type == 'assigned':
                    res = 'ready to receive'
                if type == 'confirmed':
                    res = 'waiting availability'
                if type == 'waiting':
                    res = 'draft'    
                return res or ''
         
        def get_invoice(cb):
                res = {}                
                date_from = cb.date_from
                date_to = cb.date_to      
                po_no= cb.po_no 
                     
                #===============================================================
                grn_no= cb.grn_no                
                #===============================================================
                requisitioner= cb.requisitioner.id
                state= cb.state
                
                #mat_desc=wizard_data['dec_material']
                         
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
                       
                if po_no:
                    str = " and sp.purchase_id = %s"%(po_no.id)
                    sql = sql+str
                if grn_no:
                    str = " and sp.purchase_id = %s"%(grn_no.purchase_id.id)
                    sql = sql+str
                #===============================================================
                # if grn_no:
                #     str = " and sm.picking_id = %s "%(cost_cent)
                #     sql = sql+str
                # if requisitioner:
                #     str = " and mr.requisitioner = %s "%(requisitioner)
                #     sql = sql+str
                # if state:
                #     str = " and mr.state = '%s' "%(state)
                #     sql = sql+str 
                #===============================================================
                     
                sql=sql+" order by sp.date"                    
                cr.execute(sql)
                print sql
                return cr.dictfetchall()
             
        cr.execute('delete from grn_details_report')
        cb_obj = self.pool.get('grn.details.report')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        for line in get_invoice(cb):
            cb_line.append((0,0,{                                     
                             
                            
                            'grn_no' : line['grn_no'] or False,
                            'grn_date': line['grn_date'] or False,
                            'supplier': line['supplier'] ,
                            'doc_type': line['doc_type'] or '',
                            'po_no': line['po_no'] or '',
                            'requisitioner': line['requisitioner'],
                            'po_indent_id': line['po_indent_no'],
                            'description': line['description'],
                            'item_text': line['item_text'],
                            'action_taken':line['act_take'],
                            'uom':line['product_uom'],
                            'product_id':line['product'],
                            'qty': line['prod_qty'] or 0.000,
                            'bin': line['bin_location'],
                            'state': get_status(line['state']) or '',
                            'pend_qty':get_pending_qty(cb.grn_no.purchase_id),     
                                             
                }))
             
        vals = {
                    'name': 'grn line details report',
                    'date_from': cb.date_from,
                    'date_to': cb.date_to, 
                    'project_id':cb.project_id.id,
                    'project_section_id':cb.project_section_id.id,               
                    'requisitioner': cb.requisitioner.id,
                            
                    'state': cb.state,
                    'grn_line_id': cb_line,
                }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_purchase', 'view_grn_line_detail_report')
        return {
                        'name': 'grn line details report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'grn.details.report',
                        'domain': [],
                        'type': 'ir.actions.act_window',
                        'target': 'current',
                        'res_id': cb_id,
                    }
         
         
         #======================================================================
         # if context is None:
         #     context = {}
         # datas = {'ids': context.get('active_ids', [])}
         # datas['model'] = 'material.request.line.report'
         # datas['form'] = self.read(cr, uid, ids)[0]
         # datas['form'].update({'active_id':context.get('active_ids',False)})
         # return {'type': 'ir.actions.report.xml', 'report_name': 'material_request_line_report', 'datas': datas}
         #======================================================================
        

grn_detail_line_report() 
