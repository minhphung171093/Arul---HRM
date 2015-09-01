# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_purchase_indent_report(osv.osv_memory):
    _name = "tpt.purchase.indent.report"
    _columns = {
             'name': fields.char('', readonly=True),                               
             'date_from':fields.date('Date From'),
             'date_to':fields.date('Date To'),
             'pur_product_id':fields.many2one('tpt.purchase.indent','Purchase Indent No',ondelete='cascade' ),
             'department_id':fields.many2one('hr.department','Department'),
             'section_id': fields.many2one('arul.hr.section','Section'),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'project_id': fields.many2one('tpt.project','Project'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),
             'state':fields.selection([('draft', 'Draft'),('confirm', 'Confirmed'),('close', 'Closed'),
                                          ('+', 'Store Approved'),('++', 'Store & HOD Approved'),
                                          ('x', 'Store Rejected'),('xx', 'Store & HOD Rejected'),
                                          ('rfq_raised','RFQ Raised'),
                                          ('cancel','PO Cancelled'),
                                          ('quotation_raised','Quotation Raised'),
                                          ('po_raised','PO Raised'),
                                          ('quotation_cancel','Quotation Cancelled'),
                                          ],'Status'),    
             'purchase_indent_line_id': fields.one2many('tpt.purchase.indent.line.report', 'purchase_indent_id', 'Purchase Indent Line'),
    }
      
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'material.request.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_purchase_indent_report_pdf', 'datas': datas}
      
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'material.request.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_purchase_indent_report_xls', 'datas': datas}   
      
tpt_purchase_indent_report()
 
class tpt_purchase_indent_line_report(osv.osv_memory):
    _name = "tpt.purchase.indent.line.report"
      
    _columns = {
        'purchase_indent_id': fields.many2one('tpt.purchase.indent.report','Purchase Indent', ondelete='cascade'),
        'ind_no' : fields.char('Indent No', size = 1024),
        'ind_date': fields.date('Indent Date'),
        'doc_type': fields.char('Document Type', size = 1024),
        'dep': fields.char('Department', size = 1024),
        'sec': fields.char('Section', size = 1024),        
        'requi': fields.char('Requisitioner', size = 1024),        
        'mat_code': fields.char('Material Code', size = 1024),
        'mat_desc': fields.char('Material Desc', size = 1024),
        'uom': fields.char('UOM', size = 1024),
        'unit_price': fields.float('Unit Price'),
        'ind_qty': fields.float('Indent Qty'),
        'res_qty': fields.float('Reserved Qty'),
        'on_hand_qty': fields.float('On-hand Qty'),
        'pend_qty': fields.float('Pending Qty'),
        'proj': fields.char('Project', size = 1024),
        'proj_sec': fields.char('Project Section', size = 1024),
        'tot': fields.char('Total Value', size = 1024),
        'state': fields.char('State', size = 1024),
                  
             
 }
tpt_purchase_indent_line_report()


class purchase_indent_line_report(osv.osv_memory):
     _name = "purchase.indent.line.report"
     
     _columns = {
             'date_from':fields.date('Date From'),
             'date_to':fields.date('Date To'),
             'pur_product_id':fields.many2one('tpt.purchase.indent','Purchase Indent No',ondelete='cascade' ),
             'department_id':fields.many2one('hr.department','Department'),
             'section_id': fields.many2one('arul.hr.section','Section'),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'project_id': fields.many2one('tpt.project','Project'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),
             'state':fields.selection([('draft', 'Draft'),('confirm', 'Confirmed'),('close', 'Closed'),
                                          ('+', 'Store Approved'),('++', 'Store & HOD Approved'),
                                          ('x', 'Store Rejected'),('xx', 'Store & HOD Rejected'),
                                          ('rfq_raised','RFQ Raised'),
                                          ('cancel','PO Cancelled'),
                                          ('quotation_raised','Quotation Raised'),
                                          ('po_raised','PO Raised'),
                                          ('quotation_cancel','Quotation Cancelled'),
                                          ],'Status'),
     }
    
     def _check_date(self, cr, uid, ids, context=None):
         for date in self.browse(cr, uid, ids, context=context):
             
             if date.date_to and date.date_from:
                 if date.date_to < date.date_from:
                     raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
                     return False
                 return True
         return True
     _constraints = [
         (_check_date, 'Identical Data', []),
     ]
     
     
     def print_report(self, cr, uid, ids, context=None):
         
        def get_req_name_code(name,code,lname):
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
  
   
        def get_status(type):
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
       
        def get_doc_type(type):
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
            #return res or ''
        
        
        #=======================================================================
        # def get_pending_qty(count,indent_id,prod_id,ind_qty):
        #              
        #     if count > 0:
        #         sql = '''
        #                 select pol.product_qty as rfq_qty
        #                 from purchase_order_line pol
        #                 join purchase_order po on (po.id = pol.order_id)
        #                 join tpt_purchase_indent pi on (pi.id = pol.po_indent_no)
        #                 where pol.po_indent_no = %s and pol.product_id = %s
        #               '''%(indent_id,prod_id)
        #         cr.execute(sql)
        #         for move in cr.dictfetchall():                      
        #             rfq_qty = move['rfq_qty']
        #             pen_qty = ind_qty - rfq_qty
        #             return pen_qty or 0.000
        #     else:
        #         return ind_qty or 0.000        
        #=======================================================================
        
        def get_pending_qty(count,indent_id,prod_id,ind_qty,item_text,desc):                   
            if count > 0:
                sql = '''
                        select pol.product_qty as rfq_qty
                        from purchase_order_line pol
                        join purchase_order po on (po.id = pol.order_id)
                        join tpt_purchase_indent pi on (pi.id = pol.po_indent_no)
                        where pol.po_indent_no = %s and pol.product_id = %s
                      '''%(indent_id,prod_id)
                if item_text:
                    item_text = item_text.replace("'", "'||''''||'")
                    str = " and pol.item_text = '%s'"%(item_text)
                    sql = sql+str
                if desc:
                    desc = desc.replace("'", "'||''''||'")
                    str = " and pol.description = '%s'"%(desc)
                    sql = sql+str
                cr.execute(sql)
                for move in cr.dictfetchall():                      
                        rfq_qty = move['rfq_qty']
                        pen_qty = ind_qty - rfq_qty
                        return pen_qty or 0.000
            else:
                return ind_qty or 0.000
            
            
        def get_issue_qty_count(indent_id,prod_id,item_text,desc):             
                
                sql = '''
                        select count(*)
                        from purchase_order_line pol
                        join purchase_order po on (po.id = pol.order_id)
                        join tpt_purchase_indent pi on (pi.id = pol.po_indent_no)
                        where pol.po_indent_no = %s and pol.product_id = %s
                    '''%(indent_id,prod_id)
                if item_text:
                    item_text = item_text.replace("'", "'||''''||'")
                    str = " and pol.item_text = '%s'"%(item_text)
                    sql = sql+str
                if desc:
                    desc = desc.replace("'", "'||''''||'")
                    str = " and pol.description = '%s'"%(desc)
                    sql = sql+str
                cr.execute(sql)
                for move in cr.dictfetchall():
                    count = move['count']
                    return count or 0.000                 
            
                    
        #=======================================================================
        # def get_issue_qty_count(indent_id,prod_id):                   
        #     sql = '''
        #                 select count(*)
        #                 from purchase_order_line pol
        #                 join purchase_order po on (po.id = pol.order_id)
        #                 join tpt_purchase_indent pi on (pi.id = pol.po_indent_no)
        #                 where pol.po_indent_no = %s and pol.product_id = %s
        #             '''%(indent_id,prod_id)
        #     cr.execute(sql)
        #     for move in cr.dictfetchall():
        #         count = move['count']
        #         return count or 0.000
        #=======================================================================
        
        def get_on_hand_qty(product_id):
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
            cr.execute(sql)
            ton_sl = cr.dictfetchone()['ton_sl']
                        
            res[product_id] = {
                        'on_hand_qty': ton_sl,
                     }
            return ton_sl


        def get_invoice(cb):
            res = {}
            date_from = cb.date_from
            date_to = cb.date_to
            indent_no = cb.pur_product_id.id
            dept = cb.department_id.id
            section = cb.section_id.id
            requ = cb.requisitioner.id
            project = cb.project_id.id
            proj_sec = cb.project_section_id.id
            status = cb.state            
            
            sql = '''
                select pi.name as indent_no,pp.pur_product_id,pp.date_indent_relate as ind_date,pp.doc_type_relate as doc_type,
                pp.department_id_relate,d.name as dept,pp.section_id_relate,s.name as sec,(pp.product_uom_qty*pp.price_unit) as total_val,
                pp.requisitioner_relate,pp.product_id,pp.description as mat_desc,pr.default_code as mat_code,pp.price_unit as unit_price,
                pp.description,pp.uom_po_id,u.name as uom,pp.id as line_id,pp.mrs_qty as res_qty,pp.state as status,
                e.name_related as requisitioner,e.employee_id as requisitioner_code,e.last_name as lname,pp.product_uom_qty as ind_qty,
                pp.product_id as prod_id,prr.name as project,prs.name as proj_sec,COALESCE(pp.pur_product_id,0) as stock_id,
                COALESCE(pi.id,0) as line_id,pp.item_text as item_text,pp.description as desc
                from tpt_purchase_product pp
                inner join tpt_purchase_indent pi on (pi.id = pp.pur_product_id)
                left join hr_department d on (d.id = pp.department_id_relate)
                left join arul_hr_section s on (s.id = pp.section_id_relate)
                left join product_product pr on (pr.id = pp.product_id)
                left join product_uom u on (u.id = pp.uom_po_id)
                left join hr_employee e on (e.id = pp.requisitioner_relate)
                left join tpt_project prr on (prr.id = pi.project_id)
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
                    str = " pp.pur_product_id = %s"%(indent_no)
                    sql = sql+str
            if indent_no and (date_to or date_from):
                    str = " and pp.pur_product_id = %s"%(indent_no)
                    sql = sql+str
            if dept and not date_to and not date_from and not indent_no:
                    str = " pp.department_id_relate = %s "%(dept)
                    sql = sql+str
            if dept and (date_to or date_from or indent_no):
                    str = " and pp.department_id_relate = %s "%(dept)
                    sql = sql+str
            if section and not dept and not indent_no and not date_to and not date_from:
                    str = " pp.section_id_relate = %s "%(section)
                    sql = sql+str
            if section and (date_to or date_from or indent_no or dept):
                    str = " and pp.section_id_relate = %s "%(section)
                    sql = sql+str
            if requ and not section and not dept and not indent_no and not date_to and not date_from: 
                    str = " pp.requisitioner_relate = %s "%(requ)
                    sql = sql+str
            if requ and (date_to or date_from or indent_no or dept or section):
                    str = " and pp.requisitioner_relate = %s "%(requ)
                    sql = sql+str
            if project and not requ and not section and not dept and not indent_no and not date_to and not date_from:
                    str = " pi.project_id = %s "%(project)
                    sql = sql+str
            if project and (date_to or date_from or indent_no or dept or section or requ):
                    str = " and pi.project_id = %s "%(project)
                    sql = sql+str
            if proj_sec and not project and not requ and not section and not dept and not indent_no and not date_to and not date_from:
                    str = " pi.project_section_id = %s"%(proj_sec)
                    sql = sql+str
            if proj_sec and (date_to or date_from or indent_no or dept or section or requ or project):
                    str = " and pi.project_section_id = %s "%(proj_sec)
                    sql = sql+str
            if status and not proj_sec and not project and not requ and not section and not dept and not indent_no and not date_to and not date_from:
                    str = " pp.state = '%s' "%(status)
                    sql = sql+str
            if status and (date_to or date_from or indent_no or dept or section or requ or project or proj_sec):
                    str = " and pp.state = '%s' "%(status)
                    sql = sql+str                           
                     
            sql=sql+" order by pp.date_indent_relate,pi.name"
            cr.execute(sql)
            return cr.dictfetchall()
        
        
        cr.execute('delete from tpt_purchase_indent_report')
        cb_obj = self.pool.get('tpt.purchase.indent.report')
        cb = self.browse(cr, uid, ids[0])
        cb_line = []
        for line in get_invoice(cb):
            cb_line.append((0,0,{
                        'ind_no' :line['indent_no'] or '',
                        'ind_date':line['ind_date'] or False,
                        'doc_type':get_doc_type(line['doc_type']) or '',
                        'dep':line['dept'],
                        'sec':line['sec'],        
                        'requi':get_req_name_code(line['requisitioner'],line['requisitioner_code'],line['lname']) or '',        
                        'mat_code':line['mat_code'] or '',
                        'mat_desc':line['mat_desc'] or '',
                        'proj':line['project'],
                        'proj_sec':line['proj_sec'],
                        'uom':line['uom'] or '',
                        'unit_price':line['unit_price'] or 0.000,
                        'ind_qty':line['ind_qty'] or 0.000,
                        'res_qty':line['res_qty'] or 0.000,
                        'on_hand_qty':get_on_hand_qty(line['prod_id']),
                        #'pend_qty':get_pending_qty(line['line_id'],line['stock_id'],line['ind_qty']),
                        'pend_qty':get_pending_qty(get_issue_qty_count(line['line_id'],line['prod_id'],line['item_text'],line['desc']),line['line_id'],line['prod_id'],line['ind_qty'],line['item_text'],line['desc']),
                        'tot':line['total_val'] or 0.000,
                        'state':get_status(line['status']) or '',
                                              
                }))
              
        vals = {
                    'name': 'Purchase Indent Line Report',
                    'date_from': cb.date_from,
                    'date_to': cb.date_to,
                    'pur_product_id': cb.pur_product_id.id,
                    'department_id' : cb.department_id.id,
                    'section_id' : cb.section_id.id,
                    'requisitioner' : cb.requisitioner.id,
                    'project_id' : cb.project_id.id,
                    'project_section_id' : cb.project_section_id.id,
                    'state' : cb.state,
                    'purchase_indent_line_id': cb_line,
        }
        cb_id = cb_obj.create(cr, uid, vals)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_purchase', 'view_tpt_purchase_indent_report')
        return {
                            'name': 'Purchase Indent Line Report',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'tpt.purchase.indent.report',
                            'domain': [],
                            'type': 'ir.actions.act_window',
                            'target': 'current',
                            'res_id': cb_id,
                   }
         
            #===================================================================
            # def get_invoice(cb):
            #     res = {}                
            #     date_from = cb.date_from
            #     date_to = cb.date_to      
            #     mat_req_no= cb.material_request_id.id                
            #     cost_cent= cb.cost_center_id.id                
            #     requisitioner= cb.requisitioner.id
            #     pend_qty=cb.pend_qty                
            #     department= cb.department_id.id
            #     section= cb.section_id.id
            #     state= cb.state
            #     mat_code= cb.product_id.id
            #     project_id = cb.project_id.id
            #     project_sec_id = cb.project_section_id.id            
            #     
            #              
            #     sql = '''
            #         select mr.name as mat_req_no,mr.date_request as mat_req_date,mr.date_expec as exp_date,d.name as department,
            #         s.name as section,p.bin_location as bin_loc,e.name_related as requisitioner,e.employee_id as requisitioner_code,
            #         e.last_name as lname,res.login as req_raise_by,p.default_code as mat_code,p.name_template as mat_desc,
            #         pr.name as proj_name,cc.name as cost_center,u.name as uom,mrl.product_uom_qty as req_qty,                    
            #         mr.state as state,prs.name as proj_sec_name,mrl.id as lineid
            #         from tpt_material_request_line mrl
            #         join tpt_material_request mr on (mr.id = mrl.material_request_id)
            #         join hr_department d on (d.id = mr.department_id)
            #         join arul_hr_section s on (s.id = mr.section_id)
            #         left join hr_employee e on (e.id = mr.requisitioner)
            #         join res_users res on (res.id = mr.create_uid) 
            #         join product_product p on (p.id = mrl.product_id)
            #         join product_uom u on (u.id = mrl.uom_po_id)                    
            #         left join tpt_cost_center cc on (cc.id = mr.cost_center_id)
            #         left join tpt_project pr on (pr.id = mr.project_id)
            #         left join tpt_project_section prs on (prs.id = mr.project_section_id)
            #         where mr.date_request between '%s' and '%s'
            #         '''%(date_from, date_to)
            #            
            #     if mat_req_no:
            #         str = " and mrl.material_request_id = %s"%(mat_req_no)
            #         sql = sql+str
            #     if cost_cent:
            #         str = " and mr.cost_center_id = %s "%(cost_cent)
            #         sql = sql+str
            #     if requisitioner:
            #         str = " and mr.requisitioner = %s "%(requisitioner)
            #         sql = sql+str
            #     if pend_qty:
            #         str = " and (msl.product_uom_qty-msl.product_isu_qty) = %s "%(pend_qty)
            #         sql = sql+str
            #     if department:
            #         str = " and mr.department_id = %s "%(department)
            #         sql = sql+str 
            #     if section:
            #         str = " and mr.section_id = %s "%(section)
            #         sql = sql+str
            #     if state:
            #         str = " and mr.state = '%s' "%(state)
            #         sql = sql+str 
            #     if mat_code:
            #         str = " and mrl.product_id = %s "%(mat_code)
            #         sql = sql+str
            #     if project_id:
            #         str = " and pr.id = %s "%(project_id)
            #         sql = sql+str
            #     if project_sec_id:
            #         str = " and prs.id = %s "%(project_sec_id)
            #         sql = sql+str        
            #     sql=sql+" order by mr.date_request"
            #                          
            #     cr.execute(sql)
            #     return cr.dictfetchall()
            #  
            # cr.execute('delete from tpt_material_request_report')
            # cb_obj = self.pool.get('tpt.purchase.indent.report')
            # cb = self.browse(cr, uid, ids[0])
            # cb_line = []
            # for line in get_invoice(cb):
            #     cb_line.append((0,0,{                                     
            #                  
            #                 'mat_req_no' : line['mat_req_no'] or False,
            #                 'mat_req_date': line['mat_req_date'] or False,
            #                 'exp_date': line['exp_date'] or False,
            #                 'dept': line['department'] or '',
            #                 'sec': line['section'] or '',
            #                 'requisitioner': get_req_name_code(line['requisitioner'],line['requisitioner_code'],line['lname']) or '',
            #                 'req_raised': line['req_raise_by'],
            #                 'mat_code': line['mat_code'],
            #                 'mat_desc': line['mat_desc'],
            #                 'cost_cent': line['cost_center'],
            #                 'uom':line['uom'],
            #                 'req_qty':round(line['req_qty'],3) or 0.000,
            #                 'on_hand_qty': get_on_hand_qty(line['lineid']) or 0.000,
            #                 #'pen_qty': line['pen_qty'] or 0.000, YuVi 
            #                 'pen_qty': get_pending_qty(line['lineid'],line['req_qty'],get_issue_qty_count(line['lineid'])) or 0.000,
            #                 'bin': line['bin_loc'],
            #                 'project' : line['proj_name'] or '',
            #                 'project_sec' : line['proj_sec_name'] or '',
            #                 'state': get_status(line['state']) or '',
            #                                  
            #     }))
            #  
            # vals = {
            #     'name': 'Goods Request Line Report',
            #     'date_from_title': 'Date From: ',
            #     'date_to_title': 'Date To: ',
            #     'mat_req_no_title': 'Material Request No',
            #     'cost_cent_title': 'Cost Center',
            #     'requisition_title': 'Requisitioner',
            #     'dept_title': 'Department',
            #     'sec_title': 'Section',
            #     'state_title': 'State',
            #     'prod_title': 'Material Code',                
            #     'date_from': cb.date_from,
            #     'date_to': cb.date_to,                
            #     'material_request_id': cb.material_request_id.id,
            #     'cost_center_id': cb.cost_center_id.id,
            #     'requisitioner': cb.requisitioner.id,                
            #     'department_id': cb.department_id.id,
            #     'section_id': cb.section_id.id,
            #     'state': cb.state,
            #     'product_id': cb.product_id.id,
            #     'project_id':cb.project_id.id,
            #     'project_section_id':cb.project_section_id.id,
            #     'pend_qty':cb.pend_qty,
            #     'material_req_line_id': cb_line,
            # }
            # cb_id = cb_obj.create(cr, uid, vals)
            # res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
            #                                 'green_erp_arulmani_purchase', 'view_tpt_material_request_report')
            # return {
            #             'name': 'Goods Request Line Report',
            #             'view_type': 'form',
            #             'view_mode': 'form',
            #             'res_model': 'tpt.purchase.indent.report',
            #             'domain': [],
            #             'type': 'ir.actions.act_window',
            #             'target': 'current',
            #             'res_id': cb_id,
            #         }
            #===================================================================
         
         
        #=======================================================================
        # if context is None:
        #     context = {}
        # datas = {'ids': context.get('active_ids', [])}
        # datas['model'] = 'purchase.indent.line.report'
        # datas['form'] = self.read(cr, uid, ids)[0]
        # datas['form'].update({'active_id':context.get('active_ids',False)})
        # return {'type': 'ir.actions.report.xml', 'report_name': 'purchase_indent_line_report', 'datas': datas}
        #=======================================================================

purchase_indent_line_report() 