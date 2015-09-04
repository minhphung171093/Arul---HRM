# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tpt_material_request_report(osv.osv_memory):
    _name = "tpt.material.request.report"
    _columns = {
             'name': fields.char('', readonly=True),
             'date_from_title': fields.char('', size = 1024),
             'date_to_title': fields.char('', size = 1024),
             'mat_req_no_title': fields.char('', size = 1024), 
             'cost_cent_title': fields.char('', size = 1024), 
             'requisition_title': fields.char('', size = 1024),
             'dept_title': fields.char('', size = 1024),
             'sec_title': fields.char('', size = 1024),
             'state_title': fields.char('', size = 1024),
             'prod_title': fields.char('', size = 1024),          
             'date_from':fields.date('Date From'),
             'date_to':fields.date('Date To'),
             'material_request_id': fields.many2one('tpt.material.request', 'Material Request No',ondelete='cascade'),             
             'cost_center_id': fields.many2one('tpt.cost.center','Cost center'),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'department_id':fields.many2one('hr.department','Department'),
             'section_id': fields.many2one('arul.hr.section','Section'),             
             'state':fields.selection([('draft', 'Draft'),('done', 'Approve'),('partially', 'Partially Issued'),('closed', 'Closed')],'Status'),                 
             'product_id': fields.many2one('product.product', 'Material Code'),
             #'pend_qty': fields.float('Pending Qty'),
             'project_id': fields.many2one('tpt.project','Project'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),    
             'material_req_line_id': fields.one2many('tpt.material.request.line.report', 'material_req_id', 'Material Request Line'),
    }
     
    def print_report_pdf(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'material.request.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_material_request_report_pdf', 'datas': datas}
     
    def print_report_xls(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'material.request.line.report'
        datas['form'] = self.read(cr, uid, ids)[0]
        datas['form'].update({'active_id':context.get('active_ids',False)})
        return {'type': 'ir.actions.report.xml', 'report_name': 'tpt_material_request_report_xls', 'datas': datas}   
     
tpt_material_request_report()

class tpt_material_request_line_report(osv.osv_memory):
    _name = "tpt.material.request.line.report"
     
    _columns = {
        'material_req_id': fields.many2one('tpt.material.request.report','Material Request', ondelete='cascade'),
        'mat_req_no' : fields.many2one('tpt.material.request', 'Material Req.No'), #TPT-Y on 03Sept15, navigation line
        'mat_req_date': fields.date('Material Req Date'),
        'exp_date': fields.date('Expected Date'),
        'dept': fields.char('Department', size = 1024),
        'sec': fields.char('Section', size = 1024),
        'requisitioner': fields.char('Requisitioner', size = 1024),
        'req_raised': fields.char('Req Raised By', size = 1024),
        'mat_code': fields.char('Material Code', size = 1024),
        'mat_desc': fields.char('Material Desc', size = 1024),
        'cost_cent': fields.char('Cost Center', size = 1024),
        'uom': fields.char('UOM', size = 1024),
        'req_qty': fields.float('Req Qty'),
        #'on_hand_qty': fields.float('On-hand Qty'), TPT-Y, fix - 3033
        'pen_qty': fields.float('Pending Qty'),
        'bin': fields.char('Bin Location', size = 1024),
        'project': fields.char('Project', size = 1024),         
        'project_sec': fields.char('Project Sub Category', size = 1024),
        'state': fields.char('State', size = 1024),
                 
            
 }
tpt_material_request_line_report()


class material_request_line_report(osv.osv_memory):
     _name = "material.request.line.report"
     
     _columns = {
             'date_from':fields.date('Date From'),
             'date_to':fields.date('Date To'),
             'material_request_id': fields.many2one('tpt.material.request', 'Material Request No',ondelete='cascade'),             
             'cost_center_id': fields.many2one('tpt.cost.center','Cost center'),
             'requisitioner':fields.many2one('hr.employee','Requisitioner'),
             'department_id':fields.many2one('hr.department','Department'),
             'section_id': fields.many2one('arul.hr.section','Section'),             
             'state':fields.selection([('draft', 'Draft'),('done', 'Approve'),('partially', 'Partially Issued'),('closed', 'Closed')],'Status'),                 
             'product_id': fields.many2one('product.product', 'Material Code'),  
             #'pend_qty': fields.float('Pending Qty'),
             'project_id': fields.many2one('tpt.project','Project'),
             'project_section_id': fields.many2one('tpt.project.section','Project Sub Category'),       
     }
 
    
     #==========================================================================
     # def _check_date(self, cr, uid, ids, context=None):
     #     for date in self.browse(cr, uid, ids, context=context):
     #         if date.date_to < date.date_from:
     #             raise osv.except_osv(_('Warning!'),_('Date To is not less than Date From'))
     #             return False
     #     return True
     # _constraints = [
     #     (_check_date, 'Identical Data', []),
     # ]
     #==========================================================================
     
     
     def print_report(self, cr, uid, ids, context=None):
         
         
            #YuVi
            def get_on_hand_qty(line_id):
                res = {}
                req_line_obj = self.pool.get('tpt.material.request.line')
                line = req_line_obj.browse(cr,uid,line_id)
                onhand_qty = 0
                location_id = False
                locat_ids = []
                parent_ids = []
        #             product_id = product_obj.browse(cr,uid,order_line['product_id'])
                cate_name = line.product_id.categ_id and line.product_id.categ_id.cate_name or False
                if cate_name == 'finish':
                        lot = line.prodlot_id and line.prodlot_id.id or False
                        parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                        if parent_ids:
                            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','FSH'),('location_id','=',parent_ids[0])])
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
                            cr.execute(sql)
                            onhand_qty = cr.dictfetchone()['onhand_qty']
                if cate_name == 'raw':
                        parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                        if parent_ids:
                            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Raw material','Raw Material']),('location_id','=',parent_ids[0])])
                        if locat_ids:
                            location_id = locat_ids[0]
                if cate_name == 'spares':
                        parent_ids = self.pool.get('stock.location').search(cr, uid, [('name','=','Store'),('usage','=','view')])
                        if parent_ids:
                            locat_ids = self.pool.get('stock.location').search(cr, uid, [('name','in',['Spare','Spares']),('location_id','=',parent_ids[0])])
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
                        cr.execute(sql)                       
                        onhand_qty = cr.dictfetchone()['onhand_qty']
                        
                res[line.id] = {
                                    'on_hand_qty': onhand_qty,
                                }
                return onhand_qty or 0.000
         
            def get_req_name_code(name,code,lname):
                req_name = name
                req_code = code
                req_lname = lname
                if req_name and req_code:        
                    return '['+req_code+']' +req_name+' ' +lname
                else:
                    return ' '
                
            def get_pending_qty(move_line_id,req_qty,check_count):
                
               if check_count > 0:
                    
                    sql = '''
                        select sum(product_isu_qty) as issue_qty               
                        from tpt_material_issue_line isl
                        inner join tpt_material_issue ss on (ss.id = isl.material_issue_id)
                        where state = 'done' and request_line_id = %s
                    '''%(move_line_id)
                    cr.execute(sql)
                    for move in cr.dictfetchall():
                        if move['issue_qty']:
                            isu_qty = move['issue_qty']
                            pen_qty = req_qty - isu_qty
                            return pen_qty or 0.000
               else:
                   return req_qty or 0.000
                    
            def get_issue_qty_count(move_line_id):
                
                sql = '''
                    select count(*) from tpt_material_issue_line msl 
                    inner join tpt_material_issue ms on (ms.id = msl.material_issue_id)
                    where state = 'done' and msl.request_line_id = %s
                '''%(move_line_id)
                cr.execute(sql)
                for move in cr.dictfetchall():
                    count = move['count']
                    return count or 0.000
                
                
             
            def get_status(type):
                if type == 'draft':
                    res = 'Draft'
                if type == 'done':
                    res = 'Approve'
                if type == 'partially':
                    res = 'Partially Issued'
                if type == 'closed':
                    res = 'Closed'
                return res or ''
         
            def get_invoice(cb):
                res = {}                
                date_from = cb.date_from
                date_to = cb.date_to      
                mat_req_no= cb.material_request_id.id                
                cost_cent= cb.cost_center_id.id                
                requisitioner= cb.requisitioner.id
                #pend_qty=cb.pend_qty                
                department= cb.department_id.id
                section= cb.section_id.id
                state= cb.state
                mat_code= cb.product_id.id
                project_id = cb.project_id.id
                project_sec_id = cb.project_section_id.id            
                
                         
                sql = '''
                    select mr.name as mat_req_no_1,mr.id as mat_req_no,mr.date_request as mat_req_date,mr.date_expec as exp_date,d.name as department,
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
                    str = " mrl.material_request_id = %s"%(mat_req_no)
                    sql = sql+str
                if mat_req_no and (date_to or date_from) and (date_to or date_from or cost_cent or requisitioner or department or section or state or mat_code or project_id or project_sec_id):
                    str = " and mrl.material_request_id = %s"%(mat_req_no)
                    sql = sql+str
                if cost_cent and not mat_req_no and not date_to and not date_from and not requisitioner and not department and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.cost_center_id = %s "%(cost_cent)
                    sql = sql+str
                if cost_cent and (date_to or date_from or mat_req_no) and (date_to or date_from or mat_req_no or requisitioner or department or section or state or mat_code or project_id or project_sec_id):
                    str = " and mr.cost_center_id = %s "%(cost_cent)
                    sql = sql+str                    
                if requisitioner and not mat_req_no and not date_to and not date_from and not cost_cent and not department and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.requisitioner = %s "%(requisitioner)
                    sql = sql+str
                if requisitioner and (date_to or date_from or mat_req_no or cost_cent) and (date_to or date_from or mat_req_no or cost_cent or department or section or state or mat_code or project_id or project_sec_id):
                    str = " and mr.requisitioner = %s "%(requisitioner)
                    sql = sql+str                
                if department and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not section and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.department_id = %s "%(department)
                    sql = sql+str
                if department and (date_to or date_from or mat_req_no or cost_cent or requisitioner) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or section or state or mat_code or project_id or project_sec_id):
                    str = " and mr.department_id = %s "%(department)
                    sql = sql+str
                if section and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not state and not mat_code and not project_id and not project_sec_id:
                    str = " mr.section_id = %s "%(section)
                    sql = sql+str
                if section and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or state or mat_code or project_id or project_sec_id):
                    str = " and mr.section_id = %s "%(section)
                    sql = sql+str
                if state and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not mat_code and not project_id and not project_sec_id:
                    str = " mr.state = '%s'"%(state)
                    sql = sql+str
                if state and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or mat_code or project_id or project_sec_id):
                    str = " and mr.state = '%s' "%(state)
                    sql = sql+str
                if mat_code and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not project_id and not project_sec_id:
                    str = " mrl.product_id = %s"%(mat_code)
                    sql = sql+str
                if mat_code and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or project_id or project_sec_id):
                    str = " and mrl.product_id = %s "%(mat_code)
                    sql = sql+str
                if project_id and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_sec_id:
                    str = " pr.id = %s"%(project_id)
                    sql = sql+str
                if project_id and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code) and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_sec_id):
                    str = " and prs.id = %s "%(project_id)
                    sql = sql+str
                if project_sec_id and not mat_req_no and not date_to and not date_from and not cost_cent and not requisitioner and not department and not section and not state and not mat_code and not project_id:
                    str = " prs.id = %s"%(project_sec_id)
                    sql = sql+str
                if project_sec_id and (date_to or date_from or mat_req_no or cost_cent or requisitioner or department or section or state or mat_code or project_id):
                    str = " and prs.id = %s "%(project_sec_id)
                    sql = sql+str      
                #===============================================================
                # if mat_req_no:
                #     str = " and mrl.material_request_id = %s"%(mat_req_no)
                #     sql = sql+str
                # if cost_cent:
                #     str = " and mr.cost_center_id = %s "%(cost_cent)
                #     sql = sql+str
                # if requisitioner:
                #     str = " and mr.requisitioner = %s "%(requisitioner)
                #     sql = sql+str
                # #===============================================================
                # # if pend_qty:
                # #     str = " and (msl.product_uom_qty-msl.product_isu_qty) = %s "%(pend_qty)
                # #     sql = sql+str
                # #===============================================================
                # if department:
                #     str = " and mr.department_id = %s "%(department)
                #     sql = sql+str 
                # if section:
                #     str = " and mr.section_id = %s "%(section)
                #     sql = sql+str
                # if state:
                #     str = " and mr.state = '%s' "%(state)
                #     sql = sql+str 
                # if mat_code:
                #     str = " and mrl.product_id = %s "%(mat_code)
                #     sql = sql+str
                # if project_id:
                #     str = " and pr.id = %s "%(project_id)
                #     sql = sql+str
                # if project_sec_id:
                #     str = " and prs.id = %s "%(project_sec_id)
                #     sql = sql+str        
                #===============================================================
                sql=sql+" order by mr.date_request"
                                     
                cr.execute(sql)
                return cr.dictfetchall()
             
            cr.execute('delete from tpt_material_request_report')
            cb_obj = self.pool.get('tpt.material.request.report')
            cb = self.browse(cr, uid, ids[0])
            cb_line = []
            for line in get_invoice(cb):
                cb_line.append((0,0,{                                     
                             
                            'mat_req_no' : line['mat_req_no'] or False,
                            'mat_req_date': line['mat_req_date'] or False,
                            'exp_date': line['exp_date'] or False,
                            'dept': line['department'] or '',
                            'sec': line['section'] or '',
                            'requisitioner': get_req_name_code(line['requisitioner'],line['requisitioner_code'],line['lname']) or '',
                            'req_raised': line['req_raise_by'],
                            'mat_code': line['mat_code'],
                            'mat_desc': line['mat_desc'],
                            'cost_cent': line['cost_center'],
                            'uom':line['uom'],
                            'req_qty':round(line['req_qty'],3) or 0.000,
                            #'on_hand_qty': get_on_hand_qty(line['lineid']) or 0.000, TPT-Y, fix - 3033
                            #'pen_qty': line['pen_qty'] or 0.000, YuVi 
                            'pen_qty': get_pending_qty(line['lineid'],line['req_qty'],get_issue_qty_count(line['lineid'])) or 0.000,
                            'bin': line['bin_loc'],
                            'project' : line['proj_name'] or '',
                            'project_sec' : line['proj_sec_name'] or '',
                            'state': get_status(line['state']) or '',
                                             
                }))
             
            vals = {
                'name': 'Material Request Line Report',
                'date_from_title': 'Date From: ',
                'date_to_title': 'Date To: ',
                'mat_req_no_title': 'Material Request No',
                'cost_cent_title': 'Cost Center',
                'requisition_title': 'Requisitioner',
                'dept_title': 'Department',
                'sec_title': 'Section',
                'state_title': 'State',
                'prod_title': 'Material Code',                
                'date_from': cb.date_from,
                'date_to': cb.date_to,                
                'material_request_id': cb.material_request_id.id,
                'cost_center_id': cb.cost_center_id.id,
                'requisitioner': cb.requisitioner.id,                
                'department_id': cb.department_id.id,
                'section_id': cb.section_id.id,
                'state': cb.state,
                'product_id': cb.product_id.id,
                'project_id':cb.project_id.id,
                'project_section_id':cb.project_section_id.id,
                #'pend_qty':cb.pend_qty,
                'material_req_line_id': cb_line,
            }
            cb_id = cb_obj.create(cr, uid, vals)
            res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 
                                            'green_erp_arulmani_purchase', 'view_tpt_material_request_report')
            return {
                        'name': 'Material Request Line Report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'tpt.material.request.report',
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
        

material_request_line_report() 