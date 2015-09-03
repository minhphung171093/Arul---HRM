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
             'name':fields.char(''),  
             'date_from':fields.date('Date From'),
             'date_to':fields.date('Date To'),
             'po_no': fields.many2one('purchase.order' ,string='Po Number'),          
             'grn_no': fields.many2one('stock.picking','GRN No', size = 1024),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'project_id': fields.many2one('tpt.project','Project Title'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),
            
             'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Receive'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status', 
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, simply waiting for confirmation.\n
                 * Received: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
                             
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
        'grn_no': fields.many2one('stock.picking.in','GRN No', size = 1024), #TPT-Y on 03Sept15, navigation line
        'grn_date': fields.date('GRN date'),
        'supplier': fields.char('Supplier'),
        'doc_type': fields.char('Po Document Type'),
        'po_no': fields.many2one('purchase.order',string='Po Number'), #TPT-Y on 03Sept15, navigation line
        'po_indent_id': fields.many2one('tpt.purchase.indent',string='Po Indent No',size = 1024), #TPT-Y on 03Sept15, navigation line
        'description':fields.char('Description', size = 50, readonly = True),
        'item_text':fields.text('Item Text'),
        'product_id': fields.char('Product'),
        'req': fields.char('PR Requisitioner'),
        'qty': fields.float('Quantity'),
        'uom': fields.char('Uom', size = 1024),
        'bin': fields.char('Bin Location', size = 1024),
        'action_taken':fields.selection([('direct','Direct Stock Update'),('move','Move To Consumption'),('need','Need Inspection')],'Action To Be Taken'),
        'state': fields.char('State', size = 1024),
                 
            
 }
grn_line_details_report()


class grn_detail_line_report(osv.osv_memory):
     _name = "grn.detail.line.report"
     
     _columns = {
             'name':fields.char(''),    
             'date_from':fields.date('Date From'),
             'date_to':fields.date('Date To'),
             'po_no': fields.many2one('purchase.order','Purchase Order No', size = 1024),             
             'grn_no': fields.many2one('stock.picking','GRN No', size = 1024 ),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'project_id': fields.many2one('tpt.project','Project Title'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),
             'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Receive'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status',
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, simply waiting for confirmation.\n
                 * Received: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""), 
     }
 
     def _check_date(self, cr, uid, ids, context=None):
         for date in self.browse(cr, uid, ids, context=context):
             if date.date_to < date.date_from:
                 raise osv.except_osv(_('warning!'),_('date to is not less than date from'))
                 return False
         return True
     _constraints = [
      #   (_check_date, 'identical data', []),
     ]
     
     
     def print_report(self, cr, uid, ids, context=None):         
         
        
            
        def get_req_name_code(name):
                req_name = name
         
                return '['+req_name+']'
                
                
        #------------------------------------ def get_pending_qty(po_no,pol_id):
            #-------------------------------------------------------- po_qty = 0
            #------------------------------------------------------- grn_qty = 0
            #--------------------------------------------------------- if po_no:
                #----------------------------------------------------- sql = '''
                           # select case when sum(sm.product_qty)>0 then sum(sm.product_qty) else 0 end product_qty
                           #--------------------------------- from stock_move sm
                           #- inner join stock_picking sp on sm.picking_id=sp.id
                           # inner join purchase_order po on sp.purchase_id=po.id
                           # inner join purchase_order_line pol on po.id=pol.order_id
                           # where sm.state in  ('assigned','cancel') and po.id=%s
                        #------------------------------------------- '''%(po_no)
                #----------------------------------------------- cr.execute(sql)
                #--------------------------------------- grn_qty = cr.fetchone()
                #------------------------------------------ grn_qty = grn_qty[0]
#------------------------------------------------------------------------------ 
                #----------------------------------------------------- sql = '''
                           #---------------------- select pol.product_qty po_qty
                           #----------------------- from purchase_order_line pol
                           # where pol.order_id=(select id from purchase_order where id=%s)
                        #------------------------------------------ '''%(pol_id)
                #----------------------------------------------- cr.execute(sql)
                #---------------------------------------- po_qty = cr.fetchone()
                #-------------------------------------------- po_qty = po_qty[0]
                #------------------------------ return po_qty - grn_qty or 0.000
               
        def get_status(type):
                
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
                
                
                
        def get_doc_type(type):
            if type == 'raw':
                return 'VV Raw Material Po'
            if type == 'asset':
                return 'VV Asset Po'
            if type == 'standard':
                return 'VV Standard Po'
            if type == 'local':
                return 'VV Local Po'
            if type == 'return':
                return 'VV Return Po'
            if type == 'service':
                return 'VV Service Po'            
            if type == 'out':
                return 'VV Out Service Po'
           
                
         
        def get_invoice(cb):
                res = {}                
                date_from = cb.date_from
                date_to = cb.date_to      
                po_no= cb.po_no 
                grn_no= cb.grn_no                
                requisitioner= cb.requisitioner.id
                state= cb.state
                project_id= cb.project_id
                project_section_id = cb.project_section_id
               
                         
                sql = '''
                    select sp.name as grn_no_1,sp.id as grn_no,sp.date as grn_date,po.name as po_no_1,po.id as po_no,rp.name supplier,
                    pr.name as proj_name,prs.name as proj_sec_name,
                      po.po_document_type as doc_type,pi.name as po_indent_no_1,pi.id as po_indent_no,pp.default_code||'-'||pt.name as product,
                      sm.item_text, sm.description, sm.product_qty as prod_qty,pu.name as product_uom,
                      sm.action_taken as act_take,sm.bin_location,
                      sp.state  as state,  
                      emp.name_related as requisitioner,
                      po.id as po_id,pol.order_id as order_line_id
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
                    str = " sp.id = %s"%(grn_no.id)
                    sql = sql+str
                if grn_no and (date_to or date_from or po_no) and (date_to or date_from or po_no or requisitioner or project_id or project_section_id or state):
                    str = " and sp.id = %s "%(grn_no.id)
                    sql = sql+str         
                
                if po_no and not date_to and not date_from and not grn_no and not requisitioner and not project_id and not project_section_id and not state :
                    str = " po.id = %s"%(po_no.id)
                    sql = sql+str 
                if po_no and (date_to or date_from) and (date_to or date_from or grn_no or requisitioner or project_id or project_section_id or state):
                    str = " and po.id = %s"%(po_no.id)
                    sql = sql+str
                    
                if state and not po_no and not date_to and not date_from and not grn_no and not requisitioner and not project_id and not project_section_id :
                    str = " sp.state = '%s'"%(state)
                    sql = sql+str
                if state and (date_to or date_from or po_no or grn_no or requisitioner or project_id or project_section_id) and (date_to or date_from or po_no or grn_no or requisitioner or project_id or project_section_id ):
                    str = " and sp.state = '%s' "%(state)
                    sql = sql+str
                    
                if requisitioner and not po_no and not date_to and not date_from and not grn_no and not project_id and not project_section_id and not state :
                    str = " pi.requisitioner = '%s'"%(requisitioner)
                    sql = sql+str
                if requisitioner and (date_to or date_from or po_no or grn_no) and (date_to or date_from or po_no or grn_no or project_id or project_section_id or state):
                    str = " and pi.requisitioner = %s "%(requisitioner)
                    sql = sql+str 
                if project_id and not po_no and not date_to and not date_from and not grn_no and not requisitioner and not state and not project_section_id: # or (project_sec_id):
                    str = " pr.id = %s"%(project_id.id)
                    sql = sql+str
                if project_id and (date_to or date_from or po_no or grn_no or requisitioner  or state or project_section_id): # and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_sec_id):
                    str = " and prs.id = %s "%(project_id.id)
                    sql = sql+str    
                if project_section_id and not po_no and not date_to and not date_from and not grn_no and not requisitioner and not state and  not project_id:
                    str = " prs.id = %s"%(project_section_id.id)
                    sql = sql+str
                if project_section_id and (date_to or date_from or po_no or grn_no or requisitioner or state or project_id):
                    str = " and prs.id = %s "%(project_section_id.id)
                    sql = sql+str     
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
                            'doc_type': get_doc_type(line['doc_type']) or '',
                            'po_no': line['po_no'] or '',
                            'req': line['requisitioner'],
                            'po_indent_id': line['po_indent_no'],
                            'description': line['description'],
                            'item_text': line['item_text'],
                            'action_taken':line['act_take'],
                            'uom':line['product_uom'],
                            'product_id':line['product'],
                            'qty': line['prod_qty'] or 0.000,
                            'bin': line['bin_location'],
                            'state': get_status(line['state']) or '',
                            # 'pend_qty':get_pending_qty(line['po_id'],line['order_line_id']),
                                             
                }))
             
        vals = {
                    'name': 'GRN Line Details Report',
                    'date_from': cb.date_from,
                    'date_to': cb.date_to, 
                    'project_id':cb.project_id.id,
                    'project_section_id':cb.project_section_id.id,               
                    'requisitioner': cb.requisitioner.id,
                    'grn_no': cb.grn_no.id,       
                    'state': cb.state,
                    'po_no': cb.po_no.id,
                    
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
